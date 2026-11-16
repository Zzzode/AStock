#!/usr/bin/env python3
"""Independently check C21-C24 open-universe feasibility memos.

The check is deliberately narrow: it verifies each memo's declared evidence
boundary and no-action controls.  It does not validate external webpages,
grant data rights, select a product, or calculate a return.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
ANALYSIS = CASE_DIR / "analysis"
OUTPUT_JSON = ANALYSIS / "r14_open_universe_feasibility_expansion_audit_20260815.json"
OUTPUT_MD = ANALYSIS / "r14_open_universe_feasibility_expansion_audit_20260815.md"
FORBIDDEN_READER_TERMS = re.compile(
    r"本金|初始资金|初始金额|initial capital|initial_capital|\\bprincipal\\b|starting amount",
    re.IGNORECASE,
)

CANDIDATES = (
    {
        "id": "C21",
        "json": ANALYSIS / "c21_public_reit_historical_data_route_research_20260815.json",
        "md": ANALYSIS / "c21_public_reit_historical_data_route_research_20260815.md",
        "status": "CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_C20_TEST_ADMITTED",
    },
    {
        "id": "C22",
        "json": ANALYSIS / "c22_company_bond_historical_data_route_research_20260815.json",
        "md": ANALYSIS / "c22_company_bond_historical_data_route_research_20260815.md",
        "status": "CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_TEST_ADMITTED",
    },
    {
        "id": "C23",
        "json": ANALYSIS / "c23_open_ended_public_fund_data_feasibility_20260815.json",
        "md": ANALYSIS / "c23_open_ended_public_fund_data_feasibility_20260815.md",
        "status": "CONDITIONAL_PRODUCT_LEVEL_DATA_PATHS_IDENTIFIED_NOT_YET_TESTABLE",
    },
    {
        "id": "C24",
        "json": ANALYSIS / "c24_direct_ashare_equity_data_feasibility_20260815.json",
        "md": ANALYSIS / "c24_direct_ashare_equity_data_feasibility_20260815.md",
        "status": "CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_TEST_ADMITTED",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    checks: list[dict[str, object]] = []
    failures: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    reports: dict[str, dict[str, Any]] = {}
    for candidate in CANDIDATES:
        candidate_id = str(candidate["id"])
        json_path = candidate["json"]
        md_path = candidate["md"]
        check(f"{candidate_id} artifacts exist", json_path.is_file() and md_path.is_file(), f"{json_path.name}, {md_path.name}")
        try:
            report = load(json_path)
            reports[candidate_id] = report
            check(f"{candidate_id} JSON object", isinstance(report, dict), json_path.name)
        except (OSError, json.JSONDecodeError) as error:
            reports[candidate_id] = {}
            check(f"{candidate_id} JSON object", False, str(error))
            continue
        markdown = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
        check(f"{candidate_id} declared conditional status", report.get("status") == candidate["status"], str(report.get("status")))
        check(f"{candidate_id} Markdown mirrors no-action boundary", bool(markdown.strip()) and "不" in markdown, md_path.name)
        check(f"{candidate_id} reader wording excludes restricted amount terms", not bool(FORBIDDEN_READER_TERMS.search(markdown)), md_path.name)
        urls = re.findall(r"https://[^\"\s<>]+", json.dumps(report, ensure_ascii=False))
        check(f"{candidate_id} records primary-source locators", len(urls) >= 3, f"url_count={len(urls)}")

    c21 = reports.get("C21", {})
    check(
        "C21 preserves no-selection/no-test/no-action fields",
        c21.get("research_only") is True
        and c21.get("formal_decision_eligible") is False
        and c21.get("portfolio_q") == 0
        and c21.get("product_selected") is False
        and c21.get("return_test_run") is False
        and c21.get("return_result") is None
        and c21.get("external_action") is False
        and c21.get("current_disposition", {}).get("state") == "NO_PRODUCT_SELECTION_NO_DATA_ACQUISITION_NO_BACKTEST_NO_ACTION",
        "C21 controls",
    )
    check(
        "C21 treats URLs as locators rather than a rights grant",
        "not a grant of data rights" in str(c21.get("source_retention_note", "")).lower()
        and "written" in " ".join(c21.get("minimum_contract_and_data_acceptance_gate", [])).lower(),
        "C21 rights boundary",
    )

    c22 = reports.get("C22", {})
    check(
        "C22 preserves no-selection/no-test/no-action fields",
        c22.get("research_only") is True
        and c22.get("product_selected") is False
        and c22.get("return_test_run") is False
        and c22.get("return_result") is None
        and c22.get("external_action") is False
        and c22.get("current_disposition", {}).get("state") == "NO_BOND_SELECTION_NO_BACKTEST_NO_ACTION",
        "C22 controls",
    )
    check(
        "C22 keeps universe, realized-event, and rights blockers",
        len(c22.get("field_coverage_matrix", [])) >= 5
        and any(item.get("status") == "BLOCKED" for item in c22.get("field_coverage_matrix", []) if isinstance(item, dict))
        and "does not retain source files" in str(c22.get("source_retention_note", "")).lower(),
        "C22 field and source boundary",
    )

    c23 = reports.get("C23", {})
    c23_scope = c23.get("scope", {})
    check(
        "C23 preserves no-selection/no-test/no-action fields",
        c23_scope.get("selected_products") == []
        and c23_scope.get("product_selection_performed") is False
        and c23_scope.get("return_test_run") is False
        and c23_scope.get("return_result") is None
        and c23_scope.get("action_authorized") is False
        and c23_scope.get("portfolio_q") == 0
        and c23.get("formal_decision_eligible") is False,
        "C23 controls",
    )
    check(
        "C23 confines the five-percent reference to a research hurdle",
        "not a guarantee" in str(c23.get("research_hurdle_policy", {}).get("five_percent", "")).lower(),
        str(c23.get("research_hurdle_policy", {}).get("five_percent")),
    )
    check(
        "C23 requires data-rights/sample gate before a rule design",
        c23.get("next_gate", {}).get("id") == "C23-GATE-1"
        and "internal research" in " ".join(c23.get("next_gate", {}).get("requirements", [])).lower()
        and "sample" in " ".join(c23.get("next_gate", {}).get("requirements", [])).lower(),
        str(c23.get("next_gate", {}).get("id")),
    )

    c24 = reports.get("C24", {})
    c24_scope = c24.get("scope", {})
    check(
        "C24 preserves no-selection/no-test/no-action fields",
        c24.get("research_only") is True
        and c24.get("formal_decision_eligible") is False
        and c24.get("portfolio_q") == 0
        and c24.get("product_selected") is False
        and c24.get("universe_frozen") is False
        and c24.get("return_test_run") is False
        and c24.get("return_result") is None
        and c24.get("external_action") is False
        and c24.get("current_disposition", {}).get("state") == "NO_STOCK_SELECTION_NO_UNIVERSE_FREEZE_NO_DATA_ACQUISITION_NO_BACKTEST_NO_ACTION",
        "C24 controls",
    )
    check(
        "C24 distinguishes Shanghai/Shenzhen A shares from the separate BSE gate",
        len(c24_scope.get("base_scope", [])) == 4
        and c24_scope.get("separately_explicit_domestic_stock_coverage_gate") == ["Beijing Stock Exchange"],
        str(c24_scope),
    )
    check(
        "C24 requires full per-stock institutional diligence",
        len(c24.get("product_level_diligence_gates", [])) >= 8
        and "full equity-research" in " ".join(c24.get("minimum_contract_and_data_acceptance_gate", [])).lower(),
        f"gate_count={len(c24.get('product_level_diligence_gates', []))}",
    )

    result = "PASS" if not failures else "FAIL"
    report = {
        "schema_version": "r14_open_universe_feasibility_expansion_audit.v1",
        "artifact_id": "D5PT-R14-OPEN-UNIVERSE-FEASIBILITY-EXPANSION-AUDIT-v1",
        "as_of": "2026-08-15",
        "result": result,
        "scope": "C21 public-REIT, C22 company-bond, C23 open-ended-fund, and C24 direct-mainland-equity feasibility-memo boundaries",
        "candidate_hashes": {
            str(candidate["id"]): sha256(candidate["json"]) if candidate["json"].is_file() else None
            for candidate in CANDIDATES
        },
        "checks": checks,
        "failures": failures,
        "boundary": "This audit checks declared readiness controls only. It does not validate external pages, obtain data rights, establish a historic universe, choose a product, calculate a return, or authorize an action.",
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# R14 开放研究池新增路线边界审计",
        "",
        f"- 结果：`{result}`。",
        "- 范围：C21 公募 REIT、C22 公司债、C23 开放式公募基金、C24 境内直接股票的数据与权利可行性备忘录。",
        "- 本审计只核查工件的边界与声明一致性；不验证外部网页、不授予数据权利、不建立总体、不选品、不计算收益，也不产生行动。",
        "",
        "| 检查 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['name']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    if failures:
        lines.extend(["", "## 失败项", "", *[f"- {failure}" for failure in failures]])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"R14 OPEN-UNIVERSE FEASIBILITY EXPANSION AUDIT: {result}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
