#!/usr/bin/env python3
"""Bridge the strict open-universe review to the current paper candidate.

The script does not calculate a new performance series.  It carries forward
only verified negative diagnostics and data-readiness states from the sealed
predecessor case, then places the current R01 paper procedure beside them.
Its purpose is to prevent an open research universe from being mistaken for a
permission to promote an unadmitted route.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
STRICT_CASE = CASE_DIR.parent / "domestic-personal-securities-futures-strategy-20260814"
R11_PATH = STRICT_CASE / "analysis" / "r11_open_universe_candidate_disposition_20260815.json"
R12_PATH = STRICT_CASE / "analysis" / "r12_independent_r11_disposition_audit_20260815.json"
M01_PATH = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.json"
R01_PATH = CASE_DIR / "analysis" / "r01_monthly_dynamic_etf_paper_rulebook_20260815.json"
R02_PATH = CASE_DIR / "analysis" / "r02_independent_m01_r01_audit_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r03_open_universe_bridge_disposition_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r03_open_universe_bridge_disposition_20260815.md"

EXPECTED_SHA256 = {
    R11_PATH: "219cb4a2862111fac1920f8d84d4094e4770472a454657031530d41737f76660",
    R12_PATH: "2f4cd06b789f251b336ab0b1e4f53ab0817a7c259ec3992bdd7b0753aeb296b2",
}
EXPECTED_CANDIDATES = tuple(f"C{number}" for number in range(7, 15))
NEGATIVE_DIAGNOSTIC = {"C7", "C8", "C10", "C11", "C14"}
DATA_BLOCKED = {"C9", "C12", "C13"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _build() -> dict[str, Any]:
    for path, expected in EXPECTED_SHA256.items():
        _require(path.is_file(), f"missing sealed predecessor artifact: {path}")
        _require(_sha256(path) == expected, f"sealed predecessor hash mismatch: {path.name}")

    r11 = _read(R11_PATH)
    r12 = _read(R12_PATH)
    m01 = _read(M01_PATH)
    r01 = _read(R01_PATH)
    r02 = _read(R02_PATH)
    rows = r11.get("rows")
    _require(isinstance(rows, list), "R11 rows are missing")
    by_id = {str(row.get("candidate_id")): row for row in rows if isinstance(row, dict)}
    _require(set(by_id) == set(EXPECTED_CANDIDATES), "R11 candidate coverage changed")
    _require(r12.get("audit_status") == "PASS", "R12 is not passing")
    _require(r12.get("portfolio_q") == 0, "R12 portfolio state changed")
    for candidate in EXPECTED_CANDIDATES:
        row = by_id[candidate]
        _require(row.get("admission_decision") == "不准入", f"R11 promoted {candidate}")
        _require(row.get("portfolio_q") == 0, f"R11 portfolio state changed: {candidate}")

    diagnostic = m01.get("five_percent_research_diagnostic", {})
    complete_years = [row for row in m01.get("complete_calendar_years", []) if row.get("complete")]
    annual_failures = [
        int(row["year"])
        for row in complete_years
        if float(row["market_price_proxy_change_after_illustrative_cost"]) < 0.05
    ]
    rolling = m01.get("rolling_five_year_endpoints", [])
    rolling_pass = sum(
        float(row["annualized_market_price_proxy_change_after_illustrative_cost"]) >= 0.05
        for row in rolling
    )
    _require(diagnostic.get("state") == "HURDLE_NOT_MET_IN_EXPLORATORY_PRICE_PROXY", "M01 hurdle state changed")
    _require(annual_failures == [2016, 2018, 2021, 2022], "M01 annual failure set changed")
    _require(len(rolling) == 81 and rolling_pass == 37, "M01 rolling population changed")
    _require(r02.get("result") == "PASS", "R02 is not passing")
    _require(r01.get("status") == "paper_benchmark_only_not_stable_return_admission", "R01 was promoted")
    _require(r01.get("external_orders") is False, "R01 external-order boundary changed")
    _require(r01.get("annual_or_rolling_floor") == "not asserted", "R01 return boundary changed")

    inherited_rows = []
    for candidate in EXPECTED_CANDIDATES:
        row = by_id[candidate]
        state = "negative_proxy_or_diagnostic" if candidate in NEGATIVE_DIAGNOSTIC else "not_testable_with_current_actual_contract_or_execution_evidence"
        inherited_rows.append(
            {
                "candidate_id": candidate,
                "route": row["route"],
                "research_state": state,
                "strict_gate_disposition": row["admission_decision"],
                "verified_summary": r12["verified_negative_or_blocked_states"][candidate],
                "reopen_or_completion_gate": row["reopen_or_completion_gate"],
                "source_artifacts": row["source_artifacts"],
                "portfolio_q": 0,
            }
        )

    current = {
        "candidate_id": "R01",
        "route": "五代码月度动态 ETF 纸面程序",
        "research_state": "paper_benchmark_with_negative_price_proxy_screen",
        "fixed_codes": r01["universe"]["equity"]["codes"] + [
            r01["universe"]["bond"]["code"],
            r01["universe"]["gold"]["code"],
            r01["universe"]["fallback"]["code"],
        ],
        "strict_gate_disposition": "不准入",
        "observed_proxy": {
            "annual_failure_years": annual_failures,
            "rolling_five_year_endpoints_at_or_above_5pct": rolling_pass,
            "rolling_five_year_endpoint_count": len(rolling),
            "annualized_market_price_proxy_change_after_illustrative_cost": m01["full_period_metrics"]["annualized_market_price_proxy_change_after_illustrative_cost"],
            "maximum_drawdown": m01["full_period_metrics"]["max_drawdown"],
        },
        "paper_rule_boundary": {
            "status": r01["status"],
            "external_orders": r01["external_orders"],
            "annual_or_rolling_floor": r01["annual_or_rolling_floor"],
            "forward_paper_months_required": r01["forward_validation"]["minimum_months"],
        },
        "reopen_or_completion_gate": [
            "Complete the fixed six-month forward paper log without changing the rule midstream.",
            "Retain dated product, account-route, quote, IOPV, fee, lot and settlement checks for every paper decision.",
            "Use an independently verified total-return and execution evidence package before any higher claim is considered.",
        ],
        "source_artifacts": [
            _relative(M01_PATH),
            _relative(R01_PATH),
            _relative(R02_PATH),
        ],
        "portfolio_q": 0,
    }

    return {
        "schema_version": "open_universe_bridge_disposition.v1",
        "artifact_id": "D5PT-R03-v1",
        "as_of": "2026-08-15",
        "research_scope": "A bounded disposition of the previously researched representative routes plus the current fixed ETF paper benchmark. It does not prove that every future domestic strategy or asset category fails.",
        "strict_research_gate": r11["strict_research_hurdle"],
        "source_control": {
            "predecessor_r11": {"path": _relative(R11_PATH), "sha256": _sha256(R11_PATH)},
            "predecessor_r12": {"path": _relative(R12_PATH), "sha256": _sha256(R12_PATH)},
            "current_m01": _relative(M01_PATH),
            "current_r01": _relative(R01_PATH),
            "current_r02": _relative(R02_PATH),
        },
        "inherited_representative_routes": inherited_rows,
        "current_paper_candidate": current,
        "current_decision": {
            "status": "NO_ADMITTED_USABLE_STRATEGY",
            "portfolio_q": 0,
            "formal_decision_eligible": False,
            "external_orders": False,
            "reason": "Every inherited representative route remains either negatively diagnosed or not testable with the required actual-contract/execution evidence. The only new fixed paper procedure also misses the strict annual and rolling diagnostic screen and has not completed forward paper validation.",
        },
        "next_research_priority": {
            "route": "actual-contract domestic futures trend research",
            "why": "It remains a distinct, open route rather than a relabeling of any failed ETF or fund proxy.",
            "preconditions": [
                "Lawful, retainable actual-contract daily data with source timing and hashes.",
                "Contract lifecycle, calendar, delivery-state, effective margin/limit/fee and broker-route evidence.",
                "A frozen no-fill, cost, roll, settlement and risk-event rulebook before a result is calculated.",
                "Independent reconstruction of every complete calendar year and rolling five-calendar-year endpoint.",
            ],
            "boundary": "This is a research queue, not a recommended futures action or a prediction of a five-percent outcome.",
        },
        "interpretation_boundary": [
            "A negative market-price, cash-distribution or NAV proxy is not an investor net-total-return result.",
            "A route with incomplete actual-contract or execution evidence is not rejected for economic reasons; it is simply not testable or usable at this evidence level.",
            "An open research funnel may add a newly evidenced route, but a fixed rulebook cannot silently add a product after its rule is frozen.",
        ],
    }


def _format_summary(summary: Any) -> str:
    if isinstance(summary, str):
        return "实际合约或执行证据尚不能形成完整回放"
    if not isinstance(summary, dict):
        return "已核验限制状态"
    if "complete_year_below_5pct" in summary:
        return f"{summary['complete_year_below_5pct']} 个完整年度、{summary['rolling_below_5pct']} 个滚动端点低于 5%"
    if "complete_year_failures" in summary:
        years = "、".join(str(row["year"]) for row in summary["complete_year_failures"])
        return f"{years} 年低于 5%；{summary['rolling_below_5pct']} 个滚动端点低于 5%"
    if "below_5pct_years" in summary:
        return "、".join(str(year) for year in summary["below_5pct_years"]) + " 年低于 5%"
    return "已核验限制状态"


def _markdown(result: dict[str, Any]) -> str:
    inherited = "\n".join(
        f"| {row['candidate_id']} | {row['route']} | {'诊断未过严格门槛' if row['research_state'] == 'negative_proxy_or_diagnostic' else '实际合约/执行证据未闭合'} | {_format_summary(row['verified_summary'])} | 不准入 |"
        for row in result["inherited_representative_routes"]
    )
    candidate = result["current_paper_candidate"]
    proxy = candidate["observed_proxy"]
    years = "、".join(str(year) for year in proxy["annual_failure_years"])
    return f"""# R03 开放资产池衔接处置：当前不能放行为可使用策略

- 截止日：2026-08-15
- 当前状态：`NO_ADMITTED_USABLE_STRATEGY`；`portfolio_q=0`。
- 严格研究门槛：完整自然年经成本后净回报率与滚动五年年化净回报率均不低于 5%。这只是研究准入测试，不是收益承诺、预测或外部操作指令。

## 结论

截至本次复核，**没有任何已研究路线可以诚实地写成可个人直接采用、并稳定满足严格 5% 门槛的策略。** 先前八条代表路线仍保留原处置；新建的五代码月度 ETF 程序有明确纸面动作，但其市场价代理本身未通过严格筛选，也没有形成总回报、成交与前瞻纸面记录，因此同样不放行。

这不是对国内所有未来策略或资产类别的否定。开放研究池可以继续加入新路线；但任何固定规则在冻结后都不能为了改善结果而临时增添产品或改写历史动作。

## 已研究路线的处置

| 编号 | 路线 | 当前证据状态 | 已独立核验的关键信号 | 是否准入 |
|---|---|---|---|---|
{inherited}
| R01 | 五代码月度动态 ETF 纸面程序 | 固定规则已定义；市场价代理未过严格筛选 | {years} 年低于 5%；滚动五年端点 {proxy['rolling_five_year_endpoints_at_or_above_5pct']}/{proxy['rolling_five_year_endpoint_count']} 达到 5%；最大回撤 {proxy['maximum_drawdown']:.2%} | 不准入 |

R01 的全期年化市场价代理变化为 {proxy['annualized_market_price_proxy_change_after_illustrative_cost']:.2%}，但这不能抵消年度和滚动端点的失败，也不是个人经成本后总回报。R02 已独立复算其算术；复算通过不改变数据和执行边界。

## 仍然开放、但尚未完成的下一条路线

下一优先级是**逐实际合约的国内期货趋势研究**。这条路线不能用连续主力曲线、通用 ETF 收益或假定成交来补全。开始任何结果计算前，必须取得并冻结：

1. 具有合法保留依据、来源时间和哈希的逐实际合约日度数据；
2. 合约生命周期、交易日历、交割状态、逐日有效的保证金/涨跌停/费用及期货公司通道证据；
3. 在看任何结果前确定的无成交、费用、换月、逐日结算和风险事件规则；
4. 对每个完整自然年和每个完整滚动五年端点的独立复算。

在这些条件完成前，它只是研究队列，不是期货操作建议，也不能预告会达到 5%。

## 推理边界

1. 市场价格、现金分配诊断或净值代理都不能替代个人净总回报。
2. 证据未闭合的实际合约路线不是“经济上被否定”，而是尚不可测、不可用。
3. 本文件不授权申购、赎回、买卖、期货或期权交易、开户、交割或任何外部动作。
"""


def main() -> int:
    result = _build()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print("R03 open-universe bridge disposition: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
