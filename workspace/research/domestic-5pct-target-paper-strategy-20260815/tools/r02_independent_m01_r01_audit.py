#!/usr/bin/env python3
"""Independently reconstruct M01 and check that R01 preserves its boundary.

This verifier deliberately does not import M01's derivation code.  It reads
the sealed raw SSE responses, reconstructs the fixed signals, trade timing,
illustrative turnover/cost recurrence, annual records and rolling endpoints,
then compares the outcome with the published M01 output.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
STRICT_CASE = CASE_DIR.parent / "domestic-personal-securities-futures-strategy-20260814"
SOURCE_DIR = STRICT_CASE / "sources" / "c7-static-etf-price-observation-20260815"
SOURCE_MANIFEST = SOURCE_DIR / "manifest.json"
M01 = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.json"
R01 = CASE_DIR / "analysis" / "r01_monthly_dynamic_etf_paper_rulebook_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r02_independent_m01_r01_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r02_independent_m01_r01_audit_20260815.md"
CODES = ("510300", "510880", "511010", "511990", "518880")
LOOKBACK = 252
ROLLING = 1260
COST = 20.0 / 10_000.0
TOLERANCE = 1e-9


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_panel() -> pd.DataFrame:
    manifest = _load_json(SOURCE_MANIFEST)
    records = {str(row.get("path")): row for row in manifest.get("files", []) if isinstance(row, dict)}
    columns: dict[str, pd.Series] = {}
    for code in CODES:
        path = SOURCE_DIR / f"sse_etf_dayk_{code}_begin0_end5000.jsonp"
        record = records.get(_relative(path))
        if record is None or not path.is_file() or _sha256(path) != record.get("sha256"):
            raise ValueError(f"sealed source mismatch: {code}")
        raw = path.read_text(encoding="utf-8")
        found = re.match(r"^[^(]+\((.*)\)$", raw, flags=re.DOTALL)
        if not found:
            raise ValueError(f"unparseable source response: {code}")
        payload = json.loads(found.group(1))
        rows = payload.get("kline")
        if str(payload.get("code")) != code or not isinstance(rows, list) or len(rows) != int(payload.get("total", -1)):
            raise ValueError(f"source payload validation failed: {code}")
        frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
        frame["date"] = pd.to_datetime(frame["date"].astype(str), format="%Y%m%d", errors="raise")
        frame["close"] = pd.to_numeric(frame["close"], errors="raise")
        if frame["date"].duplicated().any() or (frame["close"] <= 0).any():
            raise ValueError(f"invalid price sequence: {code}")
        columns[code] = frame.set_index("date")["close"]
    panel = pd.concat(columns, axis=1, join="inner").sort_index()
    panel = panel.loc[:pd.Timestamp("2026-08-14")]
    if tuple(panel.columns) != CODES or panel.empty or panel.index.duplicated().any():
        raise ValueError("invalid common source panel")
    return panel


def _signal_and_target(panel: pd.DataFrame, pos: int) -> tuple[dict[str, float], list[str]]:
    equity_base = 0.5 * panel["510300"] / panel["510300"].iloc[0] + 0.5 * panel["510880"] / panel["510880"].iloc[0]
    scores = {
        "equity": equity_base.iloc[pos] / equity_base.iloc[pos - LOOKBACK] - 1.0,
        "bond": panel["511010"].iloc[pos] / panel["511010"].iloc[pos - LOOKBACK] - 1.0,
        "gold": panel["518880"].iloc[pos] / panel["518880"].iloc[pos - LOOKBACK] - 1.0,
    }
    active = [name for name in ("equity", "bond", "gold") if float(scores[name]) > 0.0]
    weights = {code: 0.0 for code in CODES}
    if not active:
        weights["511990"] = 1.0
    else:
        scalar = 1.0 / len(active)
        if "equity" in active:
            weights["510300"] = 0.5 * scalar
            weights["510880"] = 0.5 * scalar
        if "bond" in active:
            weights["511010"] = scalar
        if "gold" in active:
            weights["518880"] = scalar
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-12):
        raise ValueError("independent target does not sum to one")
    return weights, active


def _replay(panel: pd.DataFrame) -> tuple[pd.Series, list[dict[str, Any]]]:
    month_ends = pd.Series(panel.index, index=panel.index).groupby(panel.index.to_period("M")).tail(1).index
    month_positions = {int(panel.index.get_loc(value)) for value in month_ends}
    first = next(pos for pos in sorted(month_positions) if pos >= LOOKBACK and pos + 1 < len(panel))
    pending: dict[int, tuple[dict[str, float], int, list[str]]] = {}
    target, active = _signal_and_target(panel, first)
    pending[first + 1] = (target, first, active)
    weights = {code: 0.0 for code in CODES}
    weights["511990"] = 1.0
    value = 1.0
    curve: dict[pd.Timestamp, float] = {}
    events: list[dict[str, Any]] = []
    for pos in range(first + 1, len(panel)):
        if pos in pending:
            target, signal_pos, active = pending.pop(pos)
            turnover = 0.5 * sum(abs(weights[code] - target[code]) for code in CODES)
            value *= 1.0 - turnover * COST
            events.append(
                {
                    "signal_date": panel.index[signal_pos].date().isoformat(),
                    "effective_date": panel.index[pos].date().isoformat(),
                    "one_way_turnover": turnover,
                    "active": active,
                }
            )
            weights = target
        ratios = panel.iloc[pos] / panel.iloc[pos - 1]
        gross = sum(weights[code] * float(ratios[code]) for code in CODES)
        value *= gross
        weights = {code: weights[code] * float(ratios[code]) / gross for code in CODES}
        curve[panel.index[pos]] = value
        if pos in month_positions and pos >= LOOKBACK and pos + 1 < len(panel):
            target, active = _signal_and_target(panel, pos)
            pending[pos + 1] = (target, pos, active)
    if pending:
        raise ValueError("unapplied independent target")
    return pd.Series(curve), events


def _annual(curve: pd.Series, panel: pd.DataFrame) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    terminal_is_complete = panel.index[-1].month == 12 and panel.index[-1].day == 31
    for year in sorted(set(curve.index.year)):
        current = curve[curve.index.year == year]
        panel_dates = panel.index[panel.index.year == year]
        prior = curve.index[curve.index < panel_dates[0]]
        complete = bool(
            len(panel_dates)
            and panel_dates[0].month == 1
            and panel_dates[-1].month == 12
            and current.index[0] == panel_dates[0]
            and current.index[-1] == panel_dates[-1]
            and len(prior)
            and (year < panel.index[-1].year or (year == panel.index[-1].year and terminal_is_complete))
        )
        output.append({"year": int(year), "value": None if not complete else float(curve.loc[current.index[-1]] / curve.loc[prior[-1]] - 1.0)})
    return output


def _rolling(curve: pd.Series, panel: pd.DataFrame) -> list[dict[str, Any]]:
    ends = pd.Series(curve.index, index=curve.index).groupby(curve.index.to_period("M")).tail(1).index
    terminal_period = panel.index[-1].to_period("M")
    terminal_month_complete = panel.index[-1] == panel.index[-1] + pd.offsets.MonthEnd(0)
    rows: list[dict[str, Any]] = []
    for end in ends:
        if end.to_period("M") == terminal_period and not terminal_month_complete:
            continue
        pos = int(panel.index.get_loc(end))
        if pos < ROLLING:
            continue
        start = panel.index[pos - ROLLING]
        if start not in curve.index:
            continue
        value = float((curve.loc[end] / curve.loc[start]) ** (LOOKBACK / ROLLING) - 1.0)
        rows.append({"start": start.date().isoformat(), "end": end.date().isoformat(), "value": value})
    return rows


def _close(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), abs_tol=TOLERANCE, rel_tol=0.0)


def _audit() -> dict[str, Any]:
    panel = _source_panel()
    curve, events = _replay(panel)
    annual = _annual(curve, panel)
    rolling = _rolling(curve, panel)
    m01 = _load_json(M01)
    r01 = _load_json(R01)
    failures: list[str] = []
    metrics = m01["full_period_metrics"]
    reconstructed_annualized = float(curve.iloc[-1] ** (LOOKBACK / len(curve)) - 1.0)
    reconstructed_dd = float((curve / curve.cummax() - 1.0).min())
    if not _close(curve.iloc[-1], metrics["final_unit_value"]):
        failures.append("final unit value differs")
    if not _close(reconstructed_annualized, metrics["annualized_market_price_proxy_change_after_illustrative_cost"]):
        failures.append("annualized proxy change differs")
    if not _close(reconstructed_dd, metrics["max_drawdown"]):
        failures.append("maximum drawdown differs")
    if len(events) != len(m01["rebalances"]):
        failures.append("rebalance-event count differs")
    if not _close(sum(item["one_way_turnover"] for item in events), m01["turnover_and_cost_summary"]["total_one_way_turnover"]):
        failures.append("aggregate turnover differs")
    published_annual = {int(row["year"]): row["market_price_proxy_change_after_illustrative_cost"] for row in m01["complete_calendar_years"]}
    for row in annual:
        if row["value"] is not None and not _close(row["value"], published_annual[row["year"]]):
            failures.append(f"annual result differs: {row['year']}")
    published_rolling = {(row["start_date"], row["end_date"]): row["annualized_market_price_proxy_change_after_illustrative_cost"] for row in m01["rolling_five_year_endpoints"]}
    if len(rolling) != len(published_rolling):
        failures.append("rolling endpoint count differs")
    for row in rolling:
        if (row["start"], row["end"]) not in published_rolling or not _close(row["value"], published_rolling[(row["start"], row["end"])]):
            failures.append(f"rolling endpoint differs: {row['end']}")
    if r01.get("status") != "paper_benchmark_only_not_stable_return_admission":
        failures.append("R01 status was promoted")
    if r01.get("m01_boundary", {}).get("diagnostic_state") != "HURDLE_NOT_MET_IN_EXPLORATORY_PRICE_PROXY":
        failures.append("R01 does not retain M01 non-admission boundary")
    if r01.get("external_orders") is not False or r01.get("annual_or_rolling_floor") != "not asserted":
        failures.append("R01 operational/return boundary changed")
    return {
        "schema_version": "independent_m01_r01_audit.v1",
        "artifact_id": "D5PT-R02-v1",
        "as_of": "2026-08-15",
        "audit_scope": "sealed-source reconstruction of M01 plus R01 boundary validation",
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_control": {"manifest": _relative(SOURCE_MANIFEST), "manifest_sha256": _sha256(SOURCE_MANIFEST), "codes": list(CODES), "common_observations": len(panel)},
        "independent_reconstruction": {
            "final_unit_value": round(float(curve.iloc[-1]), 10),
            "annualized_market_price_proxy_change_after_illustrative_cost": round(reconstructed_annualized, 10),
            "max_drawdown": round(reconstructed_dd, 10),
            "rebalance_events": len(events),
            "total_one_way_turnover": round(sum(item["one_way_turnover"] for item in events), 10),
            "complete_year_count": sum(row["value"] is not None for row in annual),
            "rolling_endpoint_count": len(rolling),
        },
        "r01_boundary": {"status": r01.get("status"), "external_orders": r01.get("external_orders"), "annual_or_rolling_floor": r01.get("annual_or_rolling_floor")},
        "conclusion": "The published proxy arithmetic is independently reproducible, but its stated limitations remain binding: no total-return, execution, personal-access or stable-return conclusion follows from this result."
    }


def _markdown(result: dict[str, Any]) -> str:
    facts = result["independent_reconstruction"]
    lines = "无。" if not result["failures"] else "\n".join(f"- {item}" for item in result["failures"])
    return f"""# R02 独立复算审计：M01 与 R01

## 结论

**审计结果：`{result['result']}`。** 本审计不导入 M01 的推导程序；它直接读取冻结的上交所日收盘价响应，重新计算月度信号、下一交易日生效、换手和 20bp 示例成本，再与 M01 的全期、年度及滚动端点逐项核对。

| 项目 | 独立结果 |
|---|---:|
| 共同日价观察数 | {result['source_control']['common_observations']} |
| 期末单位值 | {facts['final_unit_value']:.4f} |
| 年化市场价代理变化 | {facts['annualized_market_price_proxy_change_after_illustrative_cost']:.2%} |
| 最大回撤 | {facts['max_drawdown']:.2%} |
| 调仓事件 | {facts['rebalance_events']} |
| 总单边换手 | {facts['total_one_way_turnover']:.4f} |
| 完整自然年 | {facts['complete_year_count']} |
| 滚动五年端点 | {facts['rolling_endpoint_count']} |

R01 状态仍为 `{result['r01_boundary']['status']}`，不发送外部订单，且未声明任何年度或滚动下限。

## 未通过项

{lines}

## 审计边界

复算通过只说明保留数据和公开的代理算术相互一致。它不消除 M01 的根本限制：日收盘价不是复权总回报或可成交价格；没有分配、基金事件、报价深度、实际费用、税费、未成交、结算和账户权限账本。因此审计不支持“稳定 5%”、个人适当性或未来回报结论。
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    result = _audit()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"R02 independent M01/R01 audit: {result['result']}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
