#!/usr/bin/env python3
"""Verify the evidence and release identity of this strategy-translation case.

The verifier is deliberately case-specific: it tests that a research-framework
release remains q=0 and does not let crypto or institutional-manager labels
silently become execution authority.  It never judges a strategy's return.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]
PASS: list[str] = []
FAIL: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASS if condition else FAIL).append(f"{name}{': ' + detail if detail else ''}")


def load(rel: str) -> Any:
    path = CASE / rel
    if not path.exists():
        check(f"exists {rel}", False)
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        check(f"json parses {rel}", False, str(exc))
        return {}
    check(f"json parses {rel}", True)
    return value


def text(rel: str) -> str:
    path = CASE / rel
    check(f"exists {rel}", path.exists())
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_tree_sha256() -> str:
    """Hash the reader-facing TeX entrypoint and every included section.

    The build adapter exposes the entrypoint hash.  This extra manifest hash
    prevents a section-only edit from being invisible in release provenance.
    """

    paths = [CASE / "main.tex", *sorted((CASE / "sections").glob("*.tex"))]
    payload = "".join(
        f"{sha256(path)}  {path.relative_to(CASE)}\n" for path in paths
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def as_rows(value: Any, key: str) -> list[Mapping[str, Any]]:
    rows = value.get(key) if isinstance(value, Mapping) else None
    return [row for row in rows if isinstance(row, Mapping)] if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes)) else []


def source_and_claim_checks() -> set[str]:
    registry = load("data/source_registry.json")
    sources = as_rows(registry, "sources")
    source_ids = {str(row.get("source_id") or "") for row in sources}
    check("at least 15 primary source records", len(sources) >= 15, str(len(sources)))
    check("source IDs unique", len(source_ids) == len(sources) and "" not in source_ids)
    source_rows_ok = all(
        str(row.get("title") or "").strip()
        and str(row.get("authority") or "").strip()
        and str(row.get("url") or "").startswith("https://")
        and str(row.get("local_path") or "").strip()
        and str(row.get("claim_use") or "").strip()
        and str(row.get("limitation") or "").strip()
        for row in sources
    )
    check("source records have authority URL local-note claim-use limitation", source_rows_ok)
    notes = text("sources/official-source-notes-20260815/source_capture_notes.md")
    check("all registry IDs appear in local capture notes", all(source_id in notes for source_id in source_ids))
    check("current CSRC crypto notice is represented", "S14" in source_ids and "2026-02-06" in notes)

    audit = load("data/claim_audit.json")
    claims = as_rows(audit, "claims")
    check("at least 17 material claims audited", len(claims) >= 17, str(len(claims)))
    claim_ids = {str(row.get("claim_id") or "") for row in claims}
    check("claim IDs unique", len(claim_ids) == len(claims) and "" not in claim_ids)
    linked = True
    classified = True
    for row in claims:
        ids = row.get("source_ids")
        linked = linked and isinstance(ids, Sequence) and not isinstance(ids, (str, bytes)) and bool(ids) and set(map(str, ids)) <= source_ids
        classified = classified and str(row.get("type") or "").strip() and str(row.get("limitation") or "").strip() and str(row.get("status") or "").strip()
    check("every audited claim resolves to source IDs", linked)
    check("claims distinguish fact or translation and carry limitation", classified)
    return source_ids


def strategy_and_scope_checks(source_ids: set[str]) -> None:
    packet = load("data/strategy_translation_packet_20260815.json")
    rows = as_rows(packet, "strategies")
    expected = {f"F{i:02d}" for i in range(1, 14)}
    ids = {str(row.get("strategy_id") or "") for row in rows}
    check("exactly thirteen strategy families", ids == expected, f"ids={sorted(ids)}")
    required = ("family", "institutional_archetypes", "economic_engine", "china_securities_status", "domestic_futures_status", "crypto_status", "personal_operation", "non_replicable_components", "source_ids", "fact_vs_translation")
    complete = True
    linked = True
    for row in rows:
        complete = complete and all(bool(row.get(field)) for field in required)
        linked = linked and set(map(str, row.get("source_ids") or [])) <= source_ids
    check("every family has separate market fields and personal operation", complete)
    check("every family source-links to registry", linked)
    exclusion_terms = {"F09": "non_equivalent", "F10": "concept only", "F11": "analogue", "F12": "analogue"}
    check(
        "structural exclusions are explicit",
        all(
            expected in str(next(row for row in rows if row.get("strategy_id") == strategy_id).get("china_securities_status") or "").lower()
            for strategy_id, expected in exclusion_terms.items()
        ),
    )

    manifest = load("gate_manifest.json")
    controls = manifest.get("strategy_controls") if isinstance(manifest, Mapping) else {}
    check("strategic allocation profile", manifest.get("case_profile") == "strategic_allocation")
    check("current portfolio q zero", controls.get("current_portfolio_q") == 0)
    check("no named direct-equity admission", controls.get("named_t3_direct_equity_count") == 0 and controls.get("named_t3_direct_equity_tickers") == [])
    check("crypto named-asset/product counts remain zero", controls.get("named_crypto_asset_count") == 0 and controls.get("named_crypto_assets") == [] and controls.get("named_crypto_product_count") == 0 and controls.get("named_crypto_products") == [])
    check("crypto workaround explicitly prohibited", controls.get("crypto_circumvention_or_cross_border_workaround_prohibited") is True)

    crypto = load("data/crypto_applicability_packet_20260815.json")
    future = crypto.get("required_future_dossier") if isinstance(crypto, Mapping) else []
    prohibited = " ".join(map(str, crypto.get("prohibited_shortcuts") or [])) if isinstance(crypto, Mapping) else ""
    check("crypto packet is q=0 and not approved", crypto.get("current_weight") == 0.0 and str(crypto.get("implementation_status") or "").upper() == "NOT_APPROVED")
    check("crypto future dossier has ten controls", isinstance(future, Sequence) and len(future) >= 10)
    check("crypto packet bans circumvention and yield shortcut", "workaround" in prohibited.lower() and "yield" in prohibited.lower())

    model = load("data/portfolio_return_model_20260815.json")
    base = model.get("active_base_core") if isinstance(model, Mapping) else []
    weights = [float(row.get("weight") or 0) for row in base if isinstance(row, Mapping)]
    check("return-model weights sum to 100%", abs(sum(weights) - 1.0) < 1e-9, f"{sum(weights):.6f}")
    protected = [row for row in base if isinstance(row, Mapping) and row.get("asset") == "protected liquidity"]
    check("protected-liquidity fallback is 100%", len(protected) == 1 and protected[0].get("weight") == 1.0)
    check("all non-fallback sleeves are zero", all(float(row.get("weight") or 0) == 0.0 for row in base if isinstance(row, Mapping) and row.get("asset") != "protected liquidity"))
    check("no point-return forecast", str(model.get("model_type") or "").lower().startswith("strategic allocation planning range"))
    controls_model = model.get("activation_controls") if isinstance(model, Mapping) else {}
    direct = controls_model.get("direct_equities") if isinstance(controls_model, Mapping) else {}
    reits = controls_model.get("public_reits") if isinstance(controls_model, Mapping) else {}
    crypto_control = controls_model.get("crypto_assets_or_products") if isinstance(controls_model, Mapping) else {}
    check("direct-equity admission has eight independent controls", isinstance(direct, Mapping) and direct.get("initial_weight") == 0.0 and len(direct.get("required_independent_review") or []) >= 8)
    check("public-REIT admission has seven controls", isinstance(reits, Mapping) and reits.get("initial_weight") == 0.0 and len(reits.get("required_checks") or []) >= 7)
    check("crypto admission has ten controls and no workaround", isinstance(crypto_control, Mapping) and crypto_control.get("initial_weight") == 0.0 and len(crypto_control.get("required_independent_review") or []) >= 10 and crypto_control.get("circumvention_or_cross_border_workaround_prohibited") is True)
    cash = model.get("cash_ledger_and_accounting") if isinstance(model, Mapping) else {}
    total = model.get("total_return_measurement") if isinstance(model, Mapping) else {}
    check("cash ledger and once-only total-return rule", isinstance(cash, Mapping) and bool(cash.get("eligible_receipt_types")) and bool(cash.get("not_receipt_types")) and isinstance(total, Mapping) and "once" in str(total.get("cash_receipt_accounting_rule") or "").lower())


def release_checks() -> None:
    tex = text("main.tex")
    extracted = text("main_current_text.txt")
    required_term_groups = (("执行摘要", "决策摘要"), ("机构",), ("CTA",), ("因子",), ("事件",), ("加密", "虚拟货币"), ("个人",), ("红队",), ("来源",))
    all_text = tex + "\n" + extracted
    missing_groups = ["/".join(group) for group in required_term_groups if not any(term in all_text for term in group)]
    check("reader-facing report covers mandatory strategy sections", not missing_groups, ", ".join(missing_groups))
    check("reader-facing report makes q=0 visible", "q=0" in all_text or "q = 0" in all_text)
    mainland_named = "中国大陆" in all_text or "中国内地" in all_text
    route_blocked = any(phrase in all_text for phrase in ("不提供", "不构成", "不把任何虚拟货币", "不设计为本报告的实施路径"))
    check("reader-facing report blocks mainland crypto route", mainland_named and route_blocked)
    check("report does not contain unresolved LaTeX references", "??" not in extracted and "undefined" not in extracted.lower())

    pdf = CASE / "main.pdf"
    check("exists main.pdf", pdf.exists())
    page_count = 0
    if pdf.exists():
        result = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True, check=False)
        match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
        page_count = int(match.group(1)) if match else 0
    check("PDF has at least 15 pages", page_count >= 15, str(page_count))
    renders = sorted((CASE / "rendered" / "current-20260815").glob("*.png"))
    check("three or more rendered pages available for visual review", len(renders) >= 3, str(len(renders)))
    visual = text("visual_review.md")
    check("visual review records a pass and page inspection", "PASS" in visual and "page" in visual.lower())

    provenance = load("data/build_provenance_20260815.json")
    if (CASE / "main.tex").exists() and pdf.exists() and isinstance(provenance, Mapping):
        check("build provenance source hash reconciles", provenance.get("source_sha256") == sha256(CASE / "main.tex"))
        check("build provenance source-tree hash reconciles", provenance.get("source_tree_sha256") == source_tree_sha256())
        check("build provenance PDF hash reconciles", provenance.get("pdf_sha256") == sha256(pdf))
        source_notes = CASE / "sources" / "official-source-notes-20260815" / "source_capture_notes.md"
        check("build provenance source-note hash reconciles", provenance.get("source_capture_notes_sha256") == sha256(source_notes))
        check("build provenance records XeLaTeX", "xelatex" in str(provenance.get("engine") or "").lower())
        check("build provenance page count reconciles", provenance.get("page_count") == page_count)

    cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    allowed = {"closed", "verified", "resolved", "pass", "passed", "resolved_at_framework_scope"}
    for cycle in cycles:
        payload = load(f"review_findings_{cycle}.json")
        findings = as_rows(payload, "findings")
        check(f"review cycle {cycle} present and closed", isinstance(payload, Mapping) and all(str(row.get("status") or "").lower() in allowed for row in findings))
        if cycle != "R4_final_ic":
            check(f"repair plan pair {cycle}", (CASE / f"repair_plan_{cycle}.md").exists() and (CASE / f"repair_plan_{cycle}.json").exists())

    signoff = load("final_signoff.json")
    check("final signoff preserves research/implementation separation", isinstance(signoff, Mapping) and signoff.get("signoff_status") == "research_framework_pass" and signoff.get("implementation_status") == "not_approved" and signoff.get("live_execution_authorized") is False)
    check("final signoff has no open S/A findings", isinstance(signoff, Mapping) and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
    check("final signoff crypto boundary is explicit", isinstance(signoff, Mapping) and isinstance(signoff.get("crypto_controls"), Mapping) and signoff["crypto_controls"].get("implementation_status") == "not_approved")
    workflow = load("research_workflow_eval.json")
    quality = workflow.get("quality") if isinstance(workflow, Mapping) else {}
    try:
        blocking_count = int(quality.get("blocking_failure_count")) if isinstance(quality, Mapping) else -1
    except (TypeError, ValueError):
        blocking_count = -1
    check("workflow evaluation is a publishable research framework", isinstance(quality, Mapping) and quality.get("publishable") is True and quality.get("implementation_status") == "not_approved" and blocking_count == 0)


def main() -> int:
    source_ids = source_and_claim_checks()
    strategy_and_scope_checks(source_ids)
    release_checks()
    for item in PASS:
        print(f"PASS {item}")
    for item in FAIL:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(PASS)} PASS / {len(FAIL)} FAIL")
    print("RESULT PASS" if not FAIL else "RESULT FAIL")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
