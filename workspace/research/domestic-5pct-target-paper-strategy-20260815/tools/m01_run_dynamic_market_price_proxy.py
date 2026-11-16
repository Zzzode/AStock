#!/usr/bin/env python3
"""Derive one frozen, exploratory dynamic ETF market-price proxy.

The program intentionally reuses only the sealed SSE daily-close responses
from the prior strict-research case.  It is not a broker simulator, total-
return backtest, recommendation, or order generator.  Its purpose is to make
the proposed forward paper rule falsifiable before it is allowed into the
paper-observation register.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
STRICT_CASE = CASE_DIR.parent / "domestic-personal-securities-futures-strategy-20260814"
SOURCE_DIR = STRICT_CASE / "sources" / "c7-static-etf-price-observation-20260815"
SOURCE_MANIFEST = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.md"

DATE_CUTOFF = pd.Timestamp("2026-08-14")
LOOKBACK = 252
ROLLING_INTERVALS = 1260
ILLUSTRATIVE_ONE_WAY_COST_BPS = 20.0
CODES = ("510300", "510880", "511010", "511990", "518880")
FALLBACK = "511990"
SOURCE_PATHS = {code: SOURCE_DIR / f"sse_etf_dayk_{code}_begin0_end5000.jsonp" for code in CODES}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_source_manifest() -> dict[str, Any]:
    if not SOURCE_MANIFEST.is_file():
        raise FileNotFoundError(f"sealed SSE source manifest missing: {SOURCE_MANIFEST}")
    manifest = _load_json(SOURCE_MANIFEST)
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise ValueError("sealed SSE source manifest has no files list")
    expected = {_repo_relative(path) for path in SOURCE_PATHS.values()}
    by_path = {str(row.get("path")): row for row in rows if isinstance(row, dict)}
    frozen = {
        str(row.get("path")): row
        for row in manifest.get("source_freeze", {}).get("frozen_files", [])
        if isinstance(row, dict)
    }
    if not expected.issubset(by_path) or not expected.issubset(frozen):
        raise ValueError("sealed SSE source manifest does not cover the fixed five-code dependency")
    for code, path in SOURCE_PATHS.items():
        record = by_path[_repo_relative(path)]
        if not path.is_file():
            raise FileNotFoundError(f"sealed SSE source absent for {code}")
        if path.stat().st_size != int(record.get("bytes", -1)) or _sha256(path) != record.get("sha256"):
            raise ValueError(f"sealed SSE source digest mismatch for {code}")
        frozen_record = frozen[_repo_relative(path)]
        if any(frozen_record.get(key) != record.get(key) for key in ("path", "bytes", "sha256")):
            raise ValueError(f"sealed SSE freeze record differs for {code}")
    return manifest


def _parse_jsonp(path: Path, code: str) -> pd.Series:
    match = re.fullmatch(r"c7probe\((.*)\)", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    if not match:
        raise ValueError(f"{code}: source is not the expected JSONP response")
    payload = json.loads(match.group(1))
    if str(payload.get("code")) != code:
        raise ValueError(f"{code}: response code mismatch")
    rows = payload.get("kline")
    if not isinstance(rows, list) or len(rows) != int(payload.get("total", -1)):
        raise ValueError(f"{code}: incomplete daily-close response")
    frame = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    frame["date"] = pd.to_datetime(
        pd.to_numeric(frame["date"], errors="coerce").round().astype("Int64").astype(str),
        format="%Y%m%d",
        errors="coerce",
    )
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"]).sort_values("date", kind="stable")
    if frame.empty or frame["date"].duplicated().any() or (frame["close"] <= 0).any():
        raise ValueError(f"{code}: invalid date or close sequence")
    return frame.set_index("date")["close"].rename(code)


def _load_panel() -> tuple[pd.DataFrame, dict[str, int]]:
    series = {code: _parse_jsonp(path, code) for code, path in SOURCE_PATHS.items()}
    lengths = {code: len(values) for code, values in series.items()}
    panel = pd.concat(series.values(), axis=1, join="inner").sort_index(kind="stable")
    panel = panel.loc[:DATE_CUTOFF]
    if panel.empty or tuple(panel.columns) != CODES or panel.index.duplicated().any() or (panel <= 0).any().any():
        raise ValueError("fixed five-code common daily-close panel is invalid")
    return panel, lengths


def _equity_level(panel: pd.DataFrame) -> pd.Series:
    normalized = panel[["510300", "510880"]] / panel[["510300", "510880"]].iloc[0]
    return 0.5 * normalized["510300"] + 0.5 * normalized["510880"]


def _target(panel: pd.DataFrame, position: int) -> tuple[dict[str, float], dict[str, float], list[str]]:
    equity = _equity_level(panel)
    scores = {
        "equity": float(equity.iloc[position] / equity.iloc[position - LOOKBACK] - 1.0),
        "bond": float(panel["511010"].iloc[position] / panel["511010"].iloc[position - LOOKBACK] - 1.0),
        "gold": float(panel["518880"].iloc[position] / panel["518880"].iloc[position - LOOKBACK] - 1.0),
    }
    active = [name for name in ("equity", "bond", "gold") if scores[name] > 0.0]
    weights = {code: 0.0 for code in CODES}
    if not active:
        weights[FALLBACK] = 1.0
    else:
        sleeve_weight = 1.0 / len(active)
        if "equity" in active:
            weights["510300"] = 0.5 * sleeve_weight
            weights["510880"] = 0.5 * sleeve_weight
        if "bond" in active:
            weights["511010"] = sleeve_weight
        if "gold" in active:
            weights["518880"] = sleeve_weight
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-12):
        raise ValueError("target weights do not sum to one")
    return weights, scores, active


def _month_end_positions(panel: pd.DataFrame) -> set[int]:
    monthly_dates = pd.Series(panel.index, index=panel.index).groupby(panel.index.to_period("M")).tail(1).index
    return {int(panel.index.get_loc(value)) for value in monthly_dates}


def _simulate(panel: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    if len(panel) <= LOOKBACK + 1:
        raise ValueError("insufficient common observations for fixed warm-up")
    signal_positions = _month_end_positions(panel)
    first_signal = next((value for value in sorted(signal_positions) if value >= LOOKBACK and value + 1 < len(panel)), None)
    if first_signal is None:
        raise ValueError("no eligible monthly signal after warm-up")
    pending: dict[int, tuple[dict[str, float], dict[str, float], list[str], int]] = {}
    first_target, first_scores, first_active = _target(panel, first_signal)
    pending[first_signal + 1] = (first_target, first_scores, first_active, first_signal)
    weights = {code: 0.0 for code in CODES}
    weights[FALLBACK] = 1.0
    nav = 1.0
    rows: list[dict[str, Any]] = []
    rebalances: list[dict[str, Any]] = []
    cost_rate = ILLUSTRATIVE_ONE_WAY_COST_BPS / 10_000.0
    for position in range(first_signal + 1, len(panel)):
        date = panel.index[position]
        if position in pending:
            target, scores, active, signal_position = pending.pop(position)
            turnover = 0.5 * sum(abs(weights[code] - target[code]) for code in CODES)
            cost_fraction = turnover * cost_rate
            nav_before_cost = nav
            nav *= 1.0 - cost_fraction
            rebalances.append(
                {
                    "signal_date": panel.index[signal_position].date().isoformat(),
                    "effective_date": date.date().isoformat(),
                    "eligible_sleeves": active,
                    "trailing_252_observation_market_price_change": {key: round(value, 10) for key, value in scores.items()},
                    "drifted_weights_before_paper_trade": {key: round(value, 10) for key, value in weights.items()},
                    "target_weights": {key: round(value, 10) for key, value in target.items()},
                    "one_way_turnover": round(turnover, 10),
                    "illustrative_cost_fraction": round(cost_fraction, 10),
                    "unit_value_before_cost": round(nav_before_cost, 10),
                    "unit_value_after_cost": round(nav, 10),
                }
            )
            weights = target
        ratios = panel.iloc[position] / panel.iloc[position - 1]
        gross = sum(weights[code] * float(ratios[code]) for code in CODES)
        if not math.isfinite(gross) or gross <= 0.0:
            raise ValueError(f"non-positive market-price ratio at {date.date().isoformat()}")
        nav *= gross
        weights = {code: weights[code] * float(ratios[code]) / gross for code in CODES}
        rows.append({"date": date, "unit_value": nav, **{f"weight_{code}": weights[code] for code in CODES}})
        if position in signal_positions and position >= LOOKBACK and position + 1 < len(panel):
            target, scores, active = _target(panel, position)
            pending[position + 1] = (target, scores, active, position)
    if pending:
        raise ValueError("terminal target was not applied")
    curve = pd.DataFrame(rows).set_index("date")
    meta = {
        "first_signal_date": panel.index[first_signal].date().isoformat(),
        "first_effective_date": panel.index[first_signal + 1].date().isoformat(),
        "last_rebalance_effective_date": rebalances[-1]["effective_date"],
        "terminal_panel_observation_date": panel.index[-1].date().isoformat(),
        "common_panel_start": panel.index[0].date().isoformat(),
        "common_panel_end": panel.index[-1].date().isoformat(),
    }
    return curve, rebalances, meta


def _complete_years(curve: pd.DataFrame, panel: pd.DataFrame) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    terminal_complete = panel.index[-1].month == 12 and panel.index[-1].day == 31
    for year in sorted(set(int(item) for item in curve.index.year)):
        curve_dates = curve.index[curve.index.year == year]
        panel_dates = panel.index[panel.index.year == year]
        prior = curve.index[curve.index < panel_dates[0]] if len(panel_dates) else pd.DatetimeIndex([])
        complete = (
            len(panel_dates) > 0
            and panel_dates[0].month == 1
            and panel_dates[-1].month == 12
            and curve_dates[0] == panel_dates[0]
            and curve_dates[-1] == panel_dates[-1]
            and len(prior) > 0
            and (year < panel.index[-1].year or (year == panel.index[-1].year and terminal_complete))
        )
        change: float | None = None
        if complete:
            change = float(curve.loc[curve_dates[-1], "unit_value"] / curve.loc[prior[-1], "unit_value"] - 1.0)
        result.append(
            {
                "year": year,
                "complete": bool(complete),
                "market_price_proxy_change_after_illustrative_cost": None if change is None else round(change, 10),
                "at_or_above_5pct_diagnostic": None if change is None else bool(change >= 0.05),
            }
        )
    return result


def _rolling_five_years(curve: pd.DataFrame, panel: pd.DataFrame) -> list[dict[str, Any]]:
    month_end = pd.Series(curve.index, index=curve.index).groupby(curve.index.to_period("M")).tail(1).index
    terminal_month = panel.index[-1].to_period("M")
    terminal_complete = panel.index[-1] == panel.index[-1] + pd.offsets.MonthEnd(0)
    output: list[dict[str, Any]] = []
    for end_date in month_end:
        if end_date.to_period("M") == terminal_month and not terminal_complete:
            continue
        end_position = int(panel.index.get_loc(end_date))
        if end_position < ROLLING_INTERVALS:
            continue
        start_date = panel.index[end_position - ROLLING_INTERVALS]
        if start_date not in curve.index:
            continue
        annualized = float((curve.loc[end_date, "unit_value"] / curve.loc[start_date, "unit_value"]) ** (LOOKBACK / ROLLING_INTERVALS) - 1.0)
        output.append(
            {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "observation_intervals": ROLLING_INTERVALS,
                "annualized_market_price_proxy_change_after_illustrative_cost": round(annualized, 10),
                "at_or_above_5pct_diagnostic": bool(annualized >= 0.05),
            }
        )
    return output


def _metrics(curve: pd.DataFrame) -> dict[str, Any]:
    unit_value = curve["unit_value"]
    intervals = len(unit_value)
    annualized = float(unit_value.iloc[-1] ** (LOOKBACK / intervals) - 1.0)
    drawdown = unit_value / unit_value.cummax() - 1.0
    return {
        "start_date": unit_value.index[0].date().isoformat(),
        "end_date": unit_value.index[-1].date().isoformat(),
        "observation_intervals": intervals,
        "final_unit_value": round(float(unit_value.iloc[-1]), 10),
        "annualized_market_price_proxy_change_after_illustrative_cost": round(annualized, 10),
        "max_drawdown": round(float(drawdown.min()), 10),
    }


def _derive() -> dict[str, Any]:
    manifest = _validate_source_manifest()
    panel, source_lengths = _load_panel()
    curve, rebalances, simulation_meta = _simulate(panel)
    annual = _complete_years(curve, panel)
    rolling = _rolling_five_years(curve, panel)
    complete = [row for row in annual if row["complete"]]
    failures = []
    if any(row["at_or_above_5pct_diagnostic"] is False for row in complete):
        failures.append("At least one complete calendar-year market-price proxy is below 5%.")
    if any(row["at_or_above_5pct_diagnostic"] is False for row in rolling):
        failures.append("At least one rolling-five-year market-price proxy is below 5%.")
    status = "HURDLE_NOT_MET_IN_EXPLORATORY_PRICE_PROXY" if failures else "HURDLE_NOT_REJECTED_IN_EXPLORATORY_PRICE_PROXY"
    source_records = [
        {
            "code": code,
            "path": _repo_relative(path),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for code, path in SOURCE_PATHS.items()
    ]
    total_turnover = sum(float(row["one_way_turnover"]) for row in rebalances)
    total_cost_fraction = sum(float(row["illustrative_cost_fraction"]) for row in rebalances)
    return {
        "schema_version": "domestic_5pct_target_dynamic_market_price_proxy.v1",
        "artifact_id": "D5PT-M01-v1",
        "as_of": "2026-08-15",
        "artifact_class": "exploratory_retrospective_market_price_proxy",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "candidate_state": "research_only_not_paper_operable",
        "source_dependency": {
            "manifest_path": _repo_relative(SOURCE_MANIFEST),
            "manifest_sha256": _sha256(SOURCE_MANIFEST),
            "source_quality": manifest.get("source_quality"),
            "records": source_records,
        },
        "coverage": {
            "common_daily_close_observations": len(panel),
            "common_start": panel.index[0].date().isoformat(),
            "common_end": panel.index[-1].date().isoformat(),
            "source_rows_by_code": source_lengths,
            "excluded_rows_after_common_intersection": {code: source_lengths[code] - len(panel) for code in CODES},
        },
        "fixed_rule": {
            "signal": "On each calendar-month final common close, compare each sleeve value with the close 252 common observations earlier; positive means greater than zero.",
            "timing": "A signal formed after the month-end close applies no earlier than the next common trading session, before that session's proxy close-to-close movement.",
            "equity_sleeve": {"codes": ["510300", "510880"], "weights": [0.5, 0.5], "signal_level": "fixed-base buy-and-hold equal-weight level"},
            "other_risk_sleeves": {"bond": "511010", "gold": "518880"},
            "target": "Equal weight among positive equity, bond and gold sleeves; if none is positive, 100% 511990 fallback.",
            "leverage_derivatives_relative_ranking_parameter_search": "prohibited",
            "paper_trade_cost": {"one_way_bps": ILLUSTRATIVE_ONE_WAY_COST_BPS, "boundary": "Illustrative recurrence only; not an observed fee, tax, bid/ask, impact, fill, settlement or capacity measure."},
        },
        "simulation": simulation_meta,
        "full_period_metrics": _metrics(curve),
        "complete_calendar_years": annual,
        "rolling_five_year_endpoints": rolling,
        "rebalances": rebalances,
        "turnover_and_cost_summary": {
            "rebalance_events": len(rebalances),
            "zero_turnover_events": sum(float(row["one_way_turnover"]) == 0.0 for row in rebalances),
            "total_one_way_turnover": round(total_turnover, 10),
            "simple_sum_of_illustrative_cost_fractions": round(total_cost_fraction, 10),
            "boundary": "The simple sum is not a compounded result or an executable-cost estimate.",
        },
        "five_percent_research_diagnostic": {
            "threshold": 0.05,
            "state": status,
            "failures": failures,
            "allowed_interpretation": "This is a negative/positive screen only inside a retrospective close-price proxy. It cannot prove stable performance, investor return, personal access, implementation quality or a future result.",
        },
        "hard_limitations": [
            "The official SSE responses were captured retrospectively; they do not establish point-in-time availability, revisions, data rights or an adjusted total-return series.",
            "Daily close is not a tradable fill and omits distributions, fund events, NAV/IOPV, bid/ask, depth, price limits, suspensions, fees, taxes, settlement, account eligibility and no-fill outcomes.",
            "This rule was fixed after related public observations existed; it is not a clean preregistration and cannot support an out-of-sample performance claim.",
            "A five-percent screen does not turn a long-run target into a minimum return, and the result does not authorize an external action.",
        ],
    }


def _markdown(result: dict[str, Any]) -> str:
    metrics = result["full_period_metrics"]
    diagnostic = result["five_percent_research_diagnostic"]
    annual_rows = "\n".join(
        "| {year} | {complete} | {change} | {threshold} |".format(
            year=row["year"],
            complete="是" if row["complete"] else "否",
            change="—" if row["market_price_proxy_change_after_illustrative_cost"] is None else f"{row['market_price_proxy_change_after_illustrative_cost']:.2%}",
            threshold="—" if row["at_or_above_5pct_diagnostic"] is None else ("是" if row["at_or_above_5pct_diagnostic"] else "否"),
        )
        for row in result["complete_calendar_years"]
    )
    rolling_values = [float(row["annualized_market_price_proxy_change_after_illustrative_cost"]) for row in result["rolling_five_year_endpoints"]]
    rolling_summary = "没有可用的完整端点。"
    if rolling_values:
        rolling_summary = f"{len(rolling_values)} 个端点；最小值 {min(rolling_values):.2%}，最大值 {max(rolling_values):.2%}，不低于 5% 的端点 {sum(value >= 0.05 for value in rolling_values)}/{len(rolling_values)}。"
    failure_text = "无（仅代表该受限代理未被其自身阈值否决）。" if not diagnostic["failures"] else "\n".join(f"- {item}" for item in diagnostic["failures"])
    turnover = result["turnover_and_cost_summary"]
    return f"""# M01 月度动态 ETF 市场价代理诊断

## 结论

**状态：`{diagnostic['state']}`。** 这是为未来纸面规则做的单一、事后、官方日收盘价代理诊断。它不证明持有人总回报、可成交净收益、稳定年度结果或未来收益，更不产生实盘指令。

该规则在每月最后一个共同交易日收盘后，只比较权益、国债与黄金三个袖套过去 252 个共同观察值的市场价变化；正值袖套等权，全部不为正时才转入货币市场 ETF。任何信号最早下一共同交易日生效。这里的市场价没有复权、分配、实际成本或成交账本，因此其作用是**否决不当表述**，不是验证收益承诺。

## 全期受限代理指标

| 项目 | 值 |
|---|---:|
| 代理区间 | {metrics['start_date']} 至 {metrics['end_date']} |
| 期末单位值 | {metrics['final_unit_value']:.4f} |
| 年化市场价代理变化 | {metrics['annualized_market_price_proxy_change_after_illustrative_cost']:.2%} |
| 最大回撤 | {metrics['max_drawdown']:.2%} |
| 调仓事件 | {turnover['rebalance_events']} |
| 总单边换手 | {turnover['total_one_way_turnover']:.4f} |
| 示例成本分数算术和 | {turnover['simple_sum_of_illustrative_cost_fractions']:.2%} |

最后一项只是每次按 20bp 机械计入后的简单加总，**不是**复合成本拖累，也不是对券商费率、税费、点差、冲击或成交结果的估计。

## 完整自然年代理结果

| 年份 | 完整 | 市场价代理变化 | 不低于 5% |
|---:|:---:|---:|:---:|
{annual_rows}

## 滚动五年代理结果

{rolling_summary}

## 5% 研究线

{failure_text}

即使没有上述失败，也只能说明这一个受限代理没有被自己的阈值否决，不能说明策略“稳定”、年度必达或个人可以按同一结果成交。当前本案状态仍为 `research_only_not_paper_operable`；要进入连续纸面运行，仍须完成产品复核、月度数据/报价/IOPV/费用/结算账本和独立审查。

## 不可省略的局限

- 原始日价虽来自交易所公开接口，但为事后抓取；没有证明历史可得性、修订链、数据权利或复权总回报。
- 日收盘价不是成交价，未包含分配、基金事件、NAV/IOPV、盘口、停复牌、涨跌幅限制、费用、税费、结算、账户权限和未成交。
- 规则写定时已经存在相关公开观察，不能作为样本外或独立历史策略证据。
- 本诊断不替代期货、期权、直接股票或 REIT 的独立研究，也不会因为核心规则当前未使用它们而把它们排除在开放研究池之外。
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    result = _derive()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"M01 dynamic market-price proxy: {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
