#!/usr/bin/env python3
"""Record and verify the R10-v1/C20-v2 scope-mismatch correction.

R10 was designed against C20 v1, where the four current-rule references were
deliberately URL-only.  C20 v2 retained the rule text to close that gap.  A
legacy R10 execution against v2 therefore fails only its obsolete URL-only
assertion.  This script preserves that execution as a trace and prevents it
from being misread as a current C20 regression.

It is a provenance correction, not a replacement independent audit, strategy
test, product selection, eligibility conclusion, or external action.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
C20_PATH = CASE_DIR / "analysis" / "c20_domestic_public_reit_strategy_feasibility_20260815.json"
LEGACY_R10_PATH = CASE_DIR / "analysis" / "r10_independent_c20_public_reit_feasibility_audit_20260815.json"
RULE_MANIFEST_PATH = CASE_DIR / "sources" / "c20-current-sse-rule-text-20260815" / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r13_r10_v1_scope_mismatch_correction_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r13_r10_v1_scope_mismatch_correction_20260815.md"

EXPECTED_LEGACY_R10_SHA256 = "3d3d7b897981269d96b64bf447911a07e32e9c65f9be43734433db6fb4026f8c"
EXPECTED_C20_HASH_EMBEDDED_IN_LEGACY_R10 = "81d6c9fae8cc7f8c6069f0e84e2a5b3a2c6ae6dcf1068bd31dc85d682b9d5fad"
EXPECTED_RULE_MANIFEST_SHA256 = "f0e710ef25872489d4ee697c58fb0bf73abd8c180f0d4115ce10aaf69e278829"
EXPECTED_RETAINED_STATE = "retained_in_c20_current_rule_source_batch"


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

    c20 = load(C20_PATH)
    legacy_r10 = load(LEGACY_R10_PATH)

    check(
        "legacy R10 re-execution retained unchanged",
        sha256(LEGACY_R10_PATH) == EXPECTED_LEGACY_R10_SHA256,
        sha256(LEGACY_R10_PATH),
    )
    check(
        "legacy R10 identifies the then-current C20 v2 input",
        legacy_r10.get("c20_artifacts", {}).get("json_sha256") == EXPECTED_C20_HASH_EMBEDDED_IN_LEGACY_R10,
        str(legacy_r10.get("c20_artifacts", {}).get("json_sha256")),
    )
    legacy_failures = legacy_r10.get("failures", [])
    check(
        "legacy R10 failure is exclusively the obsolete URL-only assertion",
        legacy_r10.get("result") == "FAIL"
        and legacy_r10.get("failure_count") == 1
        and legacy_failures == ["R10-S03: C20 transparently labels all current-rule rechecks as URL-only"],
        str(legacy_failures),
    )
    check(
        "legacy R10 retained-source and no-action checks still passed",
        legacy_r10.get("inherited_source_manifest", {}).get("integrity_status") == "PASS"
        and legacy_r10.get("c20_scope_boundary", {}).get("status") == "PASS",
        "inherited-source/scope status",
    )
    check(
        "C20 remains the remediated v2 artifact",
        c20.get("artifact_id") == "D5PT-C20-FEASIBILITY-v2",
        str(c20.get("artifact_id")),
    )
    amendment = c20.get("source_control_amendment", {})
    check(
        "C20 records the R10-SC-01 remediation rationale",
        "R10-SC-01" in str(amendment.get("reason") or "")
        and amendment.get("previous_feasibility_sha256") == "21f4ce8c90c68ed1acca106ea7261e109dd184736a2f7b4a8f19a81eec649f4a",
        str(amendment),
    )
    live_checks = c20.get("source_control", {}).get("live_primary_rule_recheck", [])
    states = [item.get("retention_state") for item in live_checks if isinstance(item, dict)]
    check(
        "C20 v2 deliberately uses retained rather than URL-only rule states",
        len(states) == 4 and states == [EXPECTED_RETAINED_STATE] * 4,
        str(states),
    )
    check(
        "current-rule source batch remains immutable",
        RULE_MANIFEST_PATH.is_file() and sha256(RULE_MANIFEST_PATH) == EXPECTED_RULE_MANIFEST_SHA256,
        sha256(RULE_MANIFEST_PATH) if RULE_MANIFEST_PATH.is_file() else "missing",
    )
    scope = c20.get("scope_control", {})
    disposition = c20.get("current_disposition", {})
    no_action = (
        c20.get("research_only") is True
        and c20.get("formal_decision_eligible") is False
        and c20.get("external_orders") is False
        and c20.get("portfolio_q") == 0
        and scope.get("product_selected") is False
        and scope.get("universe_selected") is False
        and scope.get("historical_strategy_selected") is False
        and scope.get("return_test_run") is False
        and scope.get("return_result") is None
        and scope.get("eligibility_inference") is False
        and disposition.get("state") == "NO_STRATEGY_TEST_ADMISSION_NO_PRODUCT_SELECTION_NO_ACTION"
    )
    check("C20 v2 retains no-selection/no-test/no-action controls", no_action, "scope/disposition fields")

    result = "PASS_SCOPE_MISMATCH_DOCUMENTED" if not failures else "FAIL"
    report = {
        "schema_version": "r13_r10_v1_scope_mismatch_correction.v1",
        "artifact_id": "D5PT-R13-R10-V1-SCOPE-CORRECTION-v1",
        "as_of": "2026-08-15",
        "result": result,
        "correction_type": "audit-provenance correction for a legacy v1 verifier run against remediated C20 v2",
        "legacy_artifact": {
            "path": str(LEGACY_R10_PATH.relative_to(REPO_ROOT)),
            "sha256": EXPECTED_LEGACY_R10_SHA256,
            "interpretation": "The retained FAIL is a post-remediation scope mismatch. Its sole failed assertion expects v1 URL-only states that C20 v2 intentionally changed to retained-source states.",
        },
        "historical_boundary": {
            "reported_pre_amendment_result": "PASS_WITH_OPEN_SOURCE_CONTROL_GAP",
            "historical_gap_id": "R10-SC-01",
            "reproducibility_limit": "The immutable C20 v1 input/output pair was superseded before this correction. The reported v1 result is not reconstructed or asserted as a current independent audit; C20 v2's amendment and the retained legacy re-execution preserve the scope transition instead.",
        },
        "current_interpretation": "Do not interpret the legacy R10 FAIL as an open C20 v2 source-control defect. R12 separately verifies the retained-rule-text remediation; neither R12 nor this correction makes C20 strategy-testable or admitted.",
        "checks": checks,
        "failures": failures,
        "boundary": "This correction preserves audit provenance only. It does not select a product, define a universe, calculate a return, infer eligibility, authorize an action, or change C20's unadmitted status.",
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# R13 R10 v1 审计范围错配更正记录",
        "",
        f"- 结果：`{result}`。",
        "- R10 的历史断言针对 C20 v1：四个现行规则引用应为 URL-only。C20 v2 正是通过留存这些规则正文修复该缺口。",
        "- 因而，遗留 R10 在 C20 v2 上的 `FAIL` 仅来自已失效的 URL-only 断言，不可被解释为 C20 v2 的来源控制倒退。该原始重跑输出被保留以便审计追溯。",
        "- 本记录不重建或冒充 v1 的独立审计；R12 单独核验 v2 的规则正文留存。两者都不构成策略测试、选品、资格判断或外部动作。",
        "",
        "| 检查 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['name']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    if failures:
        lines.extend(["", "## 失败项", "", *[f"- {failure}" for failure in failures]])
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "这是一条审计来源沿革更正：它只说明为什么不能把遗留 R10 的机械失败当作当前缺口。C20 仍缺逐时点总体、可审计总回报、成本、执行和资格材料，因此仍未测试、未准入且无动作。",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"R13 R10 V1 SCOPE-MISMATCH CORRECTION: {result}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
