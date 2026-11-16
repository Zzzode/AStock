#!/usr/bin/env python3
"""Independently audit the R11 candidate-disposition synthesis.

The audit imports no R11 builder code.  It reads the frozen candidate artifacts
directly, verifies the R11 row-level disposition, and keeps the result at q=0.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = CASE_ROOT / "analysis"
R11_PATH = ANALYSIS / "r11_open_universe_candidate_disposition_20260815.json"
OUT_JSON = ANALYSIS / "r12_independent_r11_disposition_audit_20260815.json"
OUT_MD = ANALYSIS / "r12_independent_r11_disposition_audit_20260815.md"


def read_json(name: str) -> dict[str, Any]:
    with (ANALYSIS / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    r11 = json.loads(R11_PATH.read_text(encoding="utf-8"))
    rows = {row.get("candidate_id"): row for row in r11.get("rows", [])}

    check(r11.get("portfolio_q") == 0, "R11 portfolio_q must remain 0", failures)
    check(r11.get("formal_decision_eligible") is False, "R11 must remain formally ineligible", failures)
    check(r11.get("usable_candidate_count") == 0, "R11 usable-candidate count must remain 0", failures)
    check(
        r11.get("disposition") == "NO_CURRENT_CANDIDATE_CLEARS_THE_STRICT_RESEARCH_ADMISSION_GATE",
        "R11 disposition state differs",
        failures,
    )
    check(set(rows) == {"C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14"}, "R11 candidate set differs", failures)

    c7 = read_json("c7_static_core_satellite_price_diagnostic_20260815.json")
    c7_output = c7["arithmetic_output"]
    check(c7_output["complete_calendar_year_summary"]["below_5pct_count"] == 5, "C7 complete-year failure count differs", failures)
    check(c7_output["rolling_five_year"]["below_5pct_count"] == 1428, "C7 rolling failure count differs", failures)

    c8 = read_json("c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json")
    c8_result = c8["result"]
    check(c8_result["status"] == "PRICE_PROXY_HURDLE_FALSIFIED", "C8 status differs", failures)
    check(c8_result["complete_year_failure_count"] == 2, "C8 complete-year failure count differs", failures)
    check(c8_result["rolling_failure_count"] == 123, "C8 rolling failure count differs", failures)

    c9 = read_json("c9_commodity_actual_contract_feasibility_20260815.json")
    check(c9["status"] == "NOT_FEASIBLE_FOR_RETURN_CLAIM_OR_PERSONAL_ACTION_YET", "C9 status differs", failures)
    check(c9["return_result"] is None and c9["backtest_run"] is False, "C9 must remain untested", failures)

    c10_audit = read_json("r9_c10_independent_diagnostic_audit_20260815.json")
    check(c10_audit["audit_status"] == "PASS", "R9 status differs", failures)
    check(c10_audit["below_5pct_years"] == [2022, 2025], "C10 failure years differ", failures)

    c11 = read_json("c11_market_neutral_fund_nav_proxy_20260815.json")
    c11_audit = read_json("r8_c11_independent_audit_20260815.json")
    check(c11["result"]["status"] == "OFFICIAL_NAV_PROXY_HURDLE_FALSIFIED", "C11 status differs", failures)
    check(c11["result"]["complete_year_failure_count"] == 3, "C11 complete-year failure count differs", failures)
    check(c11["result"]["rolling_failure_count"] == 204, "C11 rolling failure count differs", failures)
    check(c11_audit["audit_status"] == "PASS", "R8 status differs", failures)

    c12 = read_json("c12_cash_futures_basis_feasibility_20260815.json")
    c12_audit = read_json("r10_c12_independent_route_audit_20260815.json")
    check(c12["status"] == "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION", "C12 status differs", failures)
    check(c12["return_result"] is None and c12["formal_decision_eligible"] is False, "C12 state differs", failures)
    check(c12_audit["audit_status"] == "PASS", "R10 status differs", failures)

    c13 = read_json("c13_etf_option_covered_call_feasibility_20260815.json")
    check(c13["strict_5pct_test"]["status"] == "NOT_FEASIBLE_FOR_RETURN_CLAIM", "C13 status differs", failures)
    check(c13["portfolio_q"] == 0, "C13 q differs", failures)

    c14 = read_json("c14_public_reit_feasibility_20260815.json")
    c14_gross = c14["strict_5pct_test"]["gross_cost_free_diagnostic"]
    check(c14["status"] == "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION", "C14 status differs", failures)
    check(c14["return_result"] is None and c14["formal_decision_eligible"] is False, "C14 state differs", failures)
    check(c14_gross["annual_failure_count"] == 3, "C14 annual failure count differs", failures)
    check(c14_gross["rolling_five_year_failure_count"] == 40, "C14 rolling failure count differs", failures)
    check(c14_gross["rolling_five_year_window_count"] == 40, "C14 rolling window count differs", failures)

    row_checks = {}
    for identifier, row in rows.items():
        decision = row.get("admission_decision")
        row_checks[identifier] = {
            "admission_decision": decision,
            "portfolio_q": row.get("portfolio_q"),
            "source_artifact_count": len(row.get("source_artifacts", [])),
        }
        check(decision == "不准入", f"{identifier} R11 admission decision differs", failures)
        check(row.get("portfolio_q") == 0, f"{identifier} R11 q differs", failures)
        check(bool(row.get("source_artifacts")), f"{identifier} R11 source-artifact link is absent", failures)

    payload = {
        "audit_id": "DPSFS-R12-INDEPENDENT-R11-DISPOSITION-v1",
        "as_of": "2026-08-15",
        "audit_status": "PASS" if not failures else "FAIL",
        "independence_boundary": "The audit parses R11 and source candidate artifacts directly; it does not import the R11 builder.",
        "comparison": {
            "failure_count": len(failures),
            "failures": failures,
            "checked_candidate_count": len(rows),
        },
        "row_checks": row_checks,
        "verified_negative_or_blocked_states": {
            "C7": {"complete_year_below_5pct": 5, "rolling_below_5pct": 1428},
            "C8": {"complete_year_below_5pct": 2, "rolling_below_5pct": 123},
            "C9": "NOT_TESTABLE_FOR_RETURN",
            "C10": {"below_5pct_years": [2022, 2025]},
            "C11": {"complete_year_below_5pct": 3, "rolling_below_5pct": 204},
            "C12": "NOT_TESTABLE_FOR_RETURN",
            "C13": "NOT_TESTABLE_FOR_RETURN",
            "C14": {"complete_year_below_5pct": 3, "rolling_below_5pct": "40/40"},
        },
        "allowed_interpretation": "The audit verifies only that the bounded R11 synthesis correctly retains each candidate's negative diagnostic or feasibility boundary. It does not establish investor total return, future performance, a universal market conclusion, allocation, holding, suitability or external action.",
        "portfolio_q": 0,
        "formal_decision_eligible": False,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# R12 独立审计：开放资产池候选处置表",
        "",
        f"- 状态：`{payload['audit_status']}`",
        "- 审计范围：直接读取 R11 及各候选工件，不调用 R11 汇总代码。",
        "- 结论：R11 正确维持八条代表性路线均为 `q=0`、不准入；审计不产生总回报、预测、配置或外部动作。",
        "",
        "| 路线 | 独立核验的状态 | R11 处置 |",
        "|---|---|---|",
        "| C7 | 5 个完整年度、1,428 个滚动五年端点低于 5% 的市场价格诊断 | 不准入 |",
        "| C8 | 2 个完整年度、123 个滚动五年端点低于 5% 的价格代理 | 不准入 |",
        "| C9 | 实际合约规则/样本已核验，但无完整回放 | 不准入 |",
        "| C10 | 2022、2025 年低于 5% 的事后四股票诊断 | 不准入 |",
        "| C11 | 3 个完整年度、204 个滚动端点低于 5% 的累计净值代理 | 不准入 |",
        "| C12 | 基差机制/样本已核验，但无匹配现券与双腿净账本 | 不准入 |",
        "| C13 | 期权机制已核验，但无实际合约与执行账本 | 不准入 |",
        "| C14 | 3 个完整年度、40/40 个滚动五年端点低于 5% 的零成本现金诊断 | 不准入 |",
        "",
        "此审计不将代理、公开价格或规则文件提升为个人净后成本回报，也不否定整个国内市场或任一完整资产类别。",
        "",
    ]
    if failures:
        lines.extend(["## 失败项", "", *[f"- {item}" for item in failures], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    if failures:
        print("R12 INDEPENDENT R11 DISPOSITION AUDIT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("R12 INDEPENDENT R11 DISPOSITION AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
