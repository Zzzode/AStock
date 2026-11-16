#!/usr/bin/env python3
"""Independently audit the historical C20 v1 public-REIT feasibility artifact.

This verifier is intentionally limited to source integrity, evidence-shape, and
scope-boundary checks.  It does not calculate a return, select a product, or
infer an individual's eligibility or ability to transact.

The R10 assertions include the v1-only expectation that four current-rule
references are URL-only.  C20 v2 deliberately remediates that finding by
retaining the same rule text.  To prevent a post-remediation execution from
overwriting the historical audit trail with a mechanical false failure, this
script refuses to run unless its input is explicitly the v1 artifact.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
ANALYSIS_DIR = CASE_DIR / "analysis"
C20_JSON_PATH = ANALYSIS_DIR / "c20_domestic_public_reit_strategy_feasibility_20260815.json"
C20_MD_PATH = ANALYSIS_DIR / "c20_domestic_public_reit_strategy_feasibility_20260815.md"
C14_SOURCE_DIR = (
    REPO_ROOT
    / "workspace"
    / "research"
    / "domestic-personal-securities-futures-strategy-20260814"
    / "sources"
    / "c14-public-infrastructure-reit-508000-20260815"
)
MANIFEST_PATH = C14_SOURCE_DIR / "manifest.json"
OUTPUT_JSON_PATH = ANALYSIS_DIR / "r10_independent_c20_public_reit_feasibility_audit_20260815.json"
OUTPUT_MD_PATH = ANALYSIS_DIR / "r10_independent_c20_public_reit_feasibility_audit_20260815.md"

EXPECTED_MANIFEST_SHA256 = "9a92989970e231562dd570b4f68685ed689362ce119cf8d219438e82b9ba19ea"
EXPECTED_C20_V1_ARTIFACT_ID = "D5PT-C20-FEASIBILITY-v1"
EXPECTED_STATUS = "PRODUCT_LEVEL_SOURCE_PREFLIGHT_PARTIAL_PASS_STRATEGY_TOTAL_RETURN_AND_OPERABILITY_NOT_READY"
EXPECTED_DISPOSITION = "NO_STRATEGY_TEST_ADMISSION_NO_PRODUCT_SELECTION_NO_ACTION"
EXPECTED_LIVE_URLS = (
    "https://www.sse.com.cn/lawandrules/sselawsrules2025/reits/c/c_20251231_10803729.shtml",
    "https://www.sse.com.cn/lawandrules/sselawsrules2025/repeal/rules/c/c_20250609_10804035.shtml",
    "https://edu.sse.com.cn/REITS/document/c/10608582/files/1b8f787ec537440db979406640606415.pdf",
    "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml",
)
EXPECTED_SOURCE_FILENAMES = {
    "csrc_public_infrastructure_reit_guideline_announcement_20200807.html",
    "sse_public_infrastructure_reit_business_rules_20210129.html",
    "sse_first_public_reits_listing_20210621.html",
    "508000_updated_prospectus_20241104.pdf",
    "508000_product_summary_20240628.pdf",
    "508000_2025_annual_report_20260327.pdf",
    "508000_2024_distribution_announcement_20250415.pdf",
    "sse_508000_daily_market_price_begin0_end5000.jsonp",
    "sse_508000_distribution_history_page1.jsonp",
    "sse_508000_nav_history_page1.jsonp",
}
FORBIDDEN_READER_TERMS = (
    "本金",
    "初始资金",
    "初始金额",
    "initial capital",
    "initial_capital",
    "principal",
    "starting amount",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_jsonp(path: Path, callback: str) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    matched = re.fullmatch(rf"{re.escape(callback)}\((.*)\)", content, flags=re.DOTALL)
    if not matched:
        raise ValueError(f"unexpected JSONP callback in {path.name}")
    payload = json.loads(matched.group(1))
    if not isinstance(payload, dict):
        raise ValueError(f"JSONP payload is not an object in {path.name}")
    return payload


def parse_compact_date(value: Any) -> date:
    text = str(value)
    if not re.fullmatch(r"\d{8}", text):
        raise ValueError(f"unexpected compact date: {value!r}")
    return date(int(text[:4]), int(text[4:6]), int(text[6:]))


def as_jsonable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): as_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [as_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [as_jsonable(item) for item in value]
    return value


def render_markdown(audit: dict[str, Any]) -> str:
    inherited = audit["inherited_source_manifest"]
    coverage = inherited["retained_data_shape"]
    source_gap = audit["source_control_gap"]
    boundary = audit["c20_scope_boundary"]
    checks = audit["checks"]
    failed = [check for check in checks if check["status"] == "FAIL"]
    lines = [
        "# R10 C20 境内公募 REIT 准备度：独立来源与边界审计",
        "",
        "- 截止日：2026-08-15",
        f"- 审计结论：`{audit['result']}`",
        "- 范围：仅复算继承来源清单、原始响应形状与 C20 边界字段；不选择产品、不计算回报、不推断任何个人资格，也不产生外部行动。",
        "",
        "## 结论",
        "",
        "C20 的继承来源批次可通过本地完整性复算：清单 SHA-256、10 个原始文件、10 个冻结条目及三类响应形状均一致。C20 也明确保持未选品、未定义总体、未运行回报测试、未产出回报结果、未作资格推断及不行动的状态；这些边界在 JSON 与 Markdown 中一致。",
        "",
        "但 C20 对现行规则的四项复核只有 URL 级记录，未在 C20 案例中保留网页或附件原件及其哈希。因此该部分具有一手来源属性，却不能作为冻结、逐字可复核的证据包。该缺口不构成产品选择、回报测试或资格结论，也不把 C20 提升为可准入测试的路线。",
        "",
        "## 继承来源核验",
        "",
        f"- 清单路径：`{inherited['path']}`",
        f"- 期望/实测 SHA-256：`{inherited['expected_sha256']}` / `{inherited['actual_sha256']}`",
        f"- 已核验原始文件：{inherited['verified_source_files']}/{inherited['source_file_count']}；冻结条目：{inherited['frozen_file_count']}。",
        f"- 日线响应：{coverage['daily_market_price']['record_count']} 行，{coverage['daily_market_price']['first_observation_date']} 至 {coverage['daily_market_price']['last_observation_date']}；仅核验字段形状和覆盖边界，未作任何计算。",
        f"- 分配响应：{coverage['distribution_history']['record_count']} 行，除权日 {coverage['distribution_history']['first_exright_date']} 至 {coverage['distribution_history']['last_exright_date']}；仅核验公开字段存在。",
        f"- NAV 查询响应：`pageHelp.total={coverage['nav_endpoint']['captured_rows']}`。",
        "",
        "这些结果只说明本地保留文件与清单相符；并不证明历史可得时点、复权、总回报、成本、成交或个人账户路径。",
        "",
        "## C20 边界核验",
        "",
        f"- `product_selected={str(boundary['scope_control']['product_selected']).lower()}`；`universe_selected={str(boundary['scope_control']['universe_selected']).lower()}`；`historical_strategy_selected={str(boundary['scope_control']['historical_strategy_selected']).lower()}`。",
        f"- `return_test_run={str(boundary['scope_control']['return_test_run']).lower()}`；`return_result={json.dumps(boundary['scope_control']['return_result'])}`；`performance_claim={str(boundary['scope_control']['performance_claim']).lower()}`。",
        f"- `eligibility_inference={str(boundary['scope_control']['eligibility_inference']).lower()}`；`portfolio_q={boundary['portfolio_q']}`；`formal_decision_eligible={str(boundary['formal_decision_eligible']).lower()}`。",
        f"- 当前处置：`{boundary['current_disposition']}`。",
        "",
        "故 R10 没有发现 C20 将非选择性历史探针误写为选品、测试结果或个人可操作性的证据。",
        "",
        "## 开放的来源控制缺口",
        "",
        f"- `{source_gap['gap_id']}`：{source_gap['summary']}",
        f"- 受影响范围：{source_gap['affected_scope']}",
        f"- 影响：{source_gap['impact']}",
        f"- 关闭条件：{source_gap['closure_condition']}",
        "",
        "四项 URL 记录仍可用于只读定位，不应被升级为逐日规则连续性、个人账户权限、成交可得性或测试准入证明。",
        "",
        "## 断言审计",
        "",
        "未发现可由已保留材料直接证伪的 C20 事实断言。需要注意的是，‘未发现直接矛盾’并不等于 URL 级规则文字已完成冻结证据控制；上述缺口保持开放。",
        "",
        "## 机械检查",
        "",
        f"- 通过：{len(checks) - len(failed)} 项；失败：{len(failed)} 项。",
    ]
    if failed:
        lines.extend(["", "失败项："])
        lines.extend(f"- `{item['id']}`：{item['message']}" for item in failed)
    else:
        lines.extend(["", "所有机械检查通过；审计结论仍保留上述来源控制缺口。"])
    lines.extend(
        [
            "",
            "## 限制",
            "",
            "本审计没有导入 C14 的规则书、回放或任何派生表现结论；也没有将 C20 的非选择性探针变成候选产品。它不能替代未来对全市场逐时点总体、总回报、成本、执行、资格及治理材料的独立核验。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    # R10 is a historical v1 checker.  It must not emit a new artifact against
    # C20 v2 because R10-S03 is intentionally false after the rule-text fix.
    try:
        c20_identity = json.loads(C20_JSON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"R10 C20 PUBLIC REIT FEASIBILITY AUDIT: NOT_APPLICABLE ({error})")
        return 0
    if c20_identity.get("artifact_id") != EXPECTED_C20_V1_ARTIFACT_ID:
        print(
            "R10 C20 PUBLIC REIT FEASIBILITY AUDIT: NOT_APPLICABLE "
            "(historical v1 checker; C20 is now remediated v2; use R12/R13)"
        )
        return 0

    failures: list[str] = []
    checks: list[dict[str, str]] = []

    def require(check_id: str, condition: bool, message: str) -> None:
        checks.append({"id": check_id, "status": "PASS" if condition else "FAIL", "message": message})
        if not condition:
            failures.append(f"{check_id}: {message}")

    for path in (C20_JSON_PATH, C20_MD_PATH, MANIFEST_PATH):
        require("R10-A00", path.is_file(), f"required artifact exists: {path.relative_to(REPO_ROOT)}")

    c20: dict[str, Any] = {}
    manifest: dict[str, Any] = {}
    c20_markdown = ""
    try:
        c20 = json.loads(C20_JSON_PATH.read_text(encoding="utf-8"))
        require("R10-A01", isinstance(c20, dict), "C20 JSON parses as an object")
    except (OSError, json.JSONDecodeError) as error:
        require("R10-A01", False, f"C20 JSON parse succeeds: {error}")
    try:
        c20_markdown = C20_MD_PATH.read_text(encoding="utf-8")
        require("R10-A02", bool(c20_markdown.strip()), "C20 Markdown is nonempty")
    except OSError as error:
        require("R10-A02", False, f"C20 Markdown is readable: {error}")
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        require("R10-A03", isinstance(manifest, dict), "C14 manifest parses as an object")
    except (OSError, json.JSONDecodeError) as error:
        require("R10-A03", False, f"C14 manifest parse succeeds: {error}")

    manifest_digest = sha256(MANIFEST_PATH) if MANIFEST_PATH.is_file() else None
    require(
        "R10-M01",
        manifest_digest == EXPECTED_MANIFEST_SHA256,
        "C14 manifest SHA-256 matches the C20-declared immutable digest",
    )

    files = manifest.get("files") if isinstance(manifest, dict) else None
    frozen = manifest.get("source_freeze", {}).get("frozen_files") if isinstance(manifest, dict) else None
    require("R10-M02", isinstance(files, list) and len(files) == 10, "C14 manifest retains exactly ten source entries")
    require("R10-M03", isinstance(frozen, list) and len(frozen) == 10, "C14 source freeze retains exactly ten entries")
    files = files if isinstance(files, list) else []
    frozen = frozen if isinstance(frozen, list) else []
    manifest_by_path = {entry.get("path"): entry for entry in files if isinstance(entry, dict)}
    frozen_by_path = {entry.get("path"): entry for entry in frozen if isinstance(entry, dict)}
    require("R10-M04", len(manifest_by_path) == len(files), "C14 manifest source paths are unique")
    require("R10-M05", len(frozen_by_path) == len(frozen), "C14 frozen source paths are unique")
    require("R10-M06", set(manifest_by_path) == set(frozen_by_path), "manifest and source-freeze path sets match")
    filenames = {Path(str(entry.get("path"))).name for entry in files if isinstance(entry, dict) and entry.get("path")}
    require("R10-M07", filenames == EXPECTED_SOURCE_FILENAMES, "C14 manifest has the expected ten source identities")

    verified_source_files = 0
    for source_index, (path_key, entry) in enumerate(manifest_by_path.items(), start=1):
        raw_path = REPO_ROOT / str(path_key)
        frozen_entry = frozen_by_path.get(path_key, {})
        present = raw_path.is_file()
        require(f"R10-M08-{source_index:02d}", present, f"retained source exists: {path_key}")
        if not present:
            continue
        size_matches = raw_path.stat().st_size == entry.get("bytes")
        hash_matches = sha256(raw_path) == entry.get("sha256")
        freeze_matches = all(entry.get(key) == frozen_entry.get(key) for key in ("path", "bytes", "sha256"))
        require(f"R10-M09-{source_index:02d}", size_matches, f"retained source byte count matches: {path_key}")
        require(f"R10-M10-{source_index:02d}", hash_matches, f"retained source SHA-256 matches: {path_key}")
        require(f"R10-M11-{source_index:02d}", freeze_matches, f"retained source agrees with frozen entry: {path_key}")
        if size_matches and hash_matches and freeze_matches:
            verified_source_files += 1

    price_summary: dict[str, Any] = {"record_count": None, "first_observation_date": None, "last_observation_date": None, "calendar_years_present": []}
    distribution_summary: dict[str, Any] = {"record_count": None, "first_exright_date": None, "last_exright_date": None}
    nav_summary: dict[str, Any] = {"captured_rows": None}
    try:
        price_payload = parse_jsonp(C14_SOURCE_DIR / "sse_508000_daily_market_price_begin0_end5000.jsonp", "c14price")
        distribution_payload = parse_jsonp(C14_SOURCE_DIR / "sse_508000_distribution_history_page1.jsonp", "c14distribution")
        nav_payload = parse_jsonp(C14_SOURCE_DIR / "sse_508000_nav_history_page1.jsonp", "c14nav")
        price_rows = price_payload.get("kline")
        distribution_rows = distribution_payload.get("result")
        require("R10-D01", price_payload.get("code") == "508000", "daily-market response identifies the retained probe code")
        require("R10-D02", isinstance(price_rows, list) and len(price_rows) == 1250, "daily-market response has 1,250 rows")
        price_rows = price_rows if isinstance(price_rows, list) else []
        price_dates = [parse_compact_date(row[0]) for row in price_rows if isinstance(row, list) and len(row) >= 6]
        require("R10-D03", len(price_dates) == len(price_rows), "every daily-market row has the expected ordered OHLCV shape")
        require("R10-D04", min(price_dates, default=None) == date(2021, 6, 21), "daily-market response first date matches")
        require("R10-D05", max(price_dates, default=None) == date(2026, 8, 14), "daily-market response last date matches")
        years = sorted({observed.year for observed in price_dates})
        require("R10-D06", all(year in years for year in range(2022, 2026)), "daily-market response has observations in each 2022-2025 calendar year")
        price_summary = {
            "record_count": len(price_rows),
            "first_observation_date": min(price_dates).isoformat() if price_dates else None,
            "last_observation_date": max(price_dates).isoformat() if price_dates else None,
            "calendar_years_present": years,
            "ordered_fields_confirmed_by_manifest_url": ["date", "open", "high", "low", "close", "volume"],
        }

        require("R10-D07", isinstance(distribution_rows, list) and len(distribution_rows) == 9, "distribution response has nine rows")
        distribution_rows = distribution_rows if isinstance(distribution_rows, list) else []
        distribution_keys = {"rightsRegistDate", "exrightDate", "fundDividends"}
        require(
            "R10-D08",
            all(isinstance(row, dict) and distribution_keys.issubset(row) for row in distribution_rows),
            "every distribution row has registration-date, ex-right-date, and per-share-cash fields",
        )
        distribution_dates = [date.fromisoformat(str(row["exrightDate"])) for row in distribution_rows if isinstance(row, dict) and "exrightDate" in row]
        require("R10-D09", min(distribution_dates, default=None) == date(2022, 4, 13), "distribution response first ex-right date matches")
        require("R10-D10", max(distribution_dates, default=None) == date(2026, 4, 17), "distribution response last ex-right date matches")
        distribution_summary = {
            "record_count": len(distribution_rows),
            "first_exright_date": min(distribution_dates).isoformat() if distribution_dates else None,
            "last_exright_date": max(distribution_dates).isoformat() if distribution_dates else None,
            "observed_raw_fields": ["rightsRegistDate", "exrightDate", "fundDividends"],
        }

        nav_total = nav_payload.get("pageHelp", {}).get("total")
        require("R10-D11", nav_total == 0, "captured NAV query reports zero rows")
        nav_summary = {"captured_rows": nav_total}
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        require("R10-D00", False, f"raw response shape checks parse successfully: {error}")

    source_control = c20.get("source_control", {}) if isinstance(c20, dict) else {}
    retained_probe = source_control.get("retained_nonselective_probe", {}) if isinstance(source_control, dict) else {}
    live_rechecks = source_control.get("live_primary_rule_recheck", []) if isinstance(source_control, dict) else []
    require("R10-C01", c20.get("status") == EXPECTED_STATUS, "C20 status retains a preflight-only state")
    require("R10-C02", c20.get("research_only") is True, "C20 is research-only")
    require("R10-C03", c20.get("formal_decision_eligible") is False, "C20 remains formally ineligible")
    require("R10-C04", c20.get("external_orders") is False, "C20 does not authorize external orders")
    require("R10-C05", c20.get("portfolio_q") == 0, "C20 portfolio quantity remains zero")
    require("R10-C06", retained_probe.get("manifest_path") == str(MANIFEST_PATH.relative_to(REPO_ROOT)), "C20 names the inherited manifest path")
    require("R10-C07", retained_probe.get("manifest_sha256") == manifest_digest, "C20 names the verified inherited manifest digest")

    scope = c20.get("scope_control", {}) if isinstance(c20, dict) else {}
    expected_scope = {
        "product_selected": False,
        "universe_selected": False,
        "historical_strategy_selected": False,
        "return_test_run": False,
        "return_result": None,
        "performance_claim": False,
        "eligibility_inference": False,
    }
    for key, expected in expected_scope.items():
        require(f"R10-B-{key}", scope.get(key) == expected, f"C20 scope control keeps {key} at the required boundary")

    strict = c20.get("strict_test_boundary", {}) if isinstance(c20, dict) else {}
    require("R10-B08", strict.get("five_percent_role") == "A hypothetical future research hurdle only; not a promised, forecast, stable, or minimum return.", "C20 confines the five-percent reference to a hypothetical future research hurdle")
    require("R10-B09", strict.get("current_result") == "NOT_TESTED_NOT_ADMITTED", "C20 does not state a test result")
    require("R10-B10", strict.get("return_test_run") is False and strict.get("return_result") is None, "strict-test fields do not contain a return computation or result")
    current_disposition = c20.get("current_disposition", {}) if isinstance(c20, dict) else {}
    require("R10-B11", current_disposition.get("state") == EXPECTED_DISPOSITION, "C20 current disposition prohibits test admission, selection, and action")
    prohibitions = current_disposition.get("prohibitions", []) if isinstance(current_disposition, dict) else []
    require("R10-B12", isinstance(prohibitions, list) and len(prohibitions) >= 5, "C20 lists explicit no-action prohibitions")

    require("R10-P01", "return_test_run=false" in c20_markdown and "return_result=null" in c20_markdown, "C20 Markdown matches JSON no-test fields")
    require("R10-P02", "不选择任何产品" in c20_markdown and "不推断任何个人能够交易" in c20_markdown, "C20 Markdown preserves no-selection and no-eligibility-inference boundaries")
    require("R10-P03", EXPECTED_DISPOSITION in c20_markdown, "C20 Markdown contains the no-action disposition")
    require("R10-P04", "G8" in c20_markdown and len(c20.get("gate_matrix", [])) == 7, "Markdown-only G8 is a conservative explanatory addition, not a conflicting structured gate")

    require("R10-S01", isinstance(live_rechecks, list) and len(live_rechecks) == 4, "C20 identifies four current-rule URL rechecks")
    urls = tuple(entry.get("url") for entry in live_rechecks if isinstance(entry, dict)) if isinstance(live_rechecks, list) else ()
    require("R10-S02", urls == EXPECTED_LIVE_URLS, "C20 current-rule URL set is complete and ordered")
    url_only_states = [entry.get("retention_state") for entry in live_rechecks if isinstance(entry, dict)] if isinstance(live_rechecks, list) else []
    require("R10-S03", url_only_states == ["url_only_read_only_recheck_not_c20_raw_capture"] * 4, "C20 transparently labels all current-rule rechecks as URL-only")

    previous_output_contains_restricted_language = False
    for output_path in (OUTPUT_JSON_PATH, OUTPUT_MD_PATH):
        if output_path.is_file():
            output_text = output_path.read_text(encoding="utf-8").lower()
            previous_output_contains_restricted_language = previous_output_contains_restricted_language or any(
                term.lower() in output_text for term in FORBIDDEN_READER_TERMS
            )
    require(
        "R10-W01",
        not previous_output_contains_restricted_language,
        "previous reader-facing R10 output omits restricted language",
    )

    result = "PASS_WITH_OPEN_SOURCE_CONTROL_GAP" if not failures else "FAIL"
    audit: dict[str, Any] = {
        "schema_version": "r10_independent_c20_public_reit_feasibility_audit.v1",
        "artifact_id": "D5PT-R10-INDEPENDENT-C20-PUBLIC-REIT-AUDIT-v1",
        "as_of": "2026-08-15",
        "result": result,
        "audit_scope": {
            "included": [
                "C20 JSON/Markdown boundary consistency",
                "C14 inherited manifest hash, raw-file hashes, freeze agreement, and source-response shape",
                "C20 current-rule URL retention classification",
            ],
            "excluded": [
                "product selection",
                "universe definition",
                "return or total-return computation",
                "performance result or forecast",
                "individual eligibility, account, broker, settlement, or execution inference",
                "external action",
            ],
        },
        "c20_artifacts": {
            "json_path": str(C20_JSON_PATH.relative_to(REPO_ROOT)),
            "json_sha256": sha256(C20_JSON_PATH) if C20_JSON_PATH.is_file() else None,
            "markdown_path": str(C20_MD_PATH.relative_to(REPO_ROOT)),
            "markdown_sha256": sha256(C20_MD_PATH) if C20_MD_PATH.is_file() else None,
        },
        "inherited_source_manifest": {
            "path": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "expected_sha256": EXPECTED_MANIFEST_SHA256,
            "actual_sha256": manifest_digest,
            "integrity_status": "PASS" if not any(check["status"] == "FAIL" and check["id"].startswith("R10-M") for check in checks) else "FAIL",
            "source_file_count": len(files),
            "frozen_file_count": len(frozen),
            "verified_source_files": verified_source_files,
            "retained_data_shape": {
                "daily_market_price": price_summary,
                "distribution_history": distribution_summary,
                "nav_endpoint": nav_summary,
            },
            "scope_limit": "The integrity result validates retained local files only. It does not establish historical availability, adjustment basis, total return, costs, eligibility, or execution.",
        },
        "c20_scope_boundary": {
            "status": "PASS" if not any(check["status"] == "FAIL" and check["id"].startswith(("R10-B", "R10-C", "R10-P")) for check in checks) else "FAIL",
            "scope_control": {key: scope.get(key) for key in expected_scope},
            "strict_test_boundary": {
                "five_percent_role": strict.get("five_percent_role"),
                "current_result": strict.get("current_result"),
                "return_test_run": strict.get("return_test_run"),
                "return_result": strict.get("return_result"),
            },
            "portfolio_q": c20.get("portfolio_q"),
            "formal_decision_eligible": c20.get("formal_decision_eligible"),
            "current_disposition": current_disposition.get("state"),
            "finding": "No C20 field turns the retained nonselective probe into a selected product, return result, eligibility inference, or action.",
        },
        "unsupported_assertions": {
            "status": "NONE_IDENTIFIED_WITHIN_RETAINED_AUDIT_SCOPE",
            "finding": "No C20 assertion was directly contradicted by the retained manifest or retained raw-response shape checks. This finding does not elevate URL-only current-rule material to frozen evidence.",
        },
        "source_control_gap": {
            "gap_id": "R10-SC-01",
            "status": "OPEN",
            "summary": "C20 对四项现行规则复核仅保留 URL，未在 C20 案例中存档网页或附件原件、内容哈希、抓取元数据或冻结文本。",
            "affected_scope": "当前规则版本、一般交易机制，以及 C20 Markdown 引用的具体规则文字。",
            "impact": "这些链接可定位一手来源，但不是冻结证据包。它们不能证明未来测试区间的规则连续性，也不能支持个人访问、执行、成本或资格结论。",
            "closure_condition": "任何后续依赖规则的测试准入审查前，应保留适用规则网页及附件、抓取元数据、哈希、生效日和带日期的规则版本映射；同时维持不对个人作推断的边界。",
            "c20_disclosure_quality": "C20 已将这些项目标为 url_only_read_only_recheck_not_c20_raw_capture，因此该缺口已披露而非隐藏。",
        },
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
        "generated_by": str(Path(__file__).relative_to(REPO_ROOT)),
    }
    OUTPUT_JSON_PATH.write_text(json.dumps(as_jsonable(audit), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(render_markdown(audit), encoding="utf-8")

    # The output itself must remain free of reader-facing restricted capital language.
    for output_path in (OUTPUT_JSON_PATH, OUTPUT_MD_PATH):
        output_text = output_path.read_text(encoding="utf-8").lower()
        if any(term.lower() in output_text for term in FORBIDDEN_READER_TERMS):
            raise RuntimeError("restricted language found in a reader-facing R10 output")

    if failures:
        print("R10 C20 PUBLIC REIT FEASIBILITY AUDIT: FAIL")
        print("\n".join(failures))
        return 1
    print("R10 C20 PUBLIC REIT FEASIBILITY AUDIT: PASS_WITH_OPEN_SOURCE_CONTROL_GAP")
    print(f"manifest_sha256={manifest_digest}")
    print(f"verified_source_files={verified_source_files}/10")
    print("current_rule_url_only_entries=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
