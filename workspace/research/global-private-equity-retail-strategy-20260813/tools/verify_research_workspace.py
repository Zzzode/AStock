#!/usr/bin/env python3
"""Read-only verifier for the global-private-equity retail translation memo."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PASS: list[str] = []
FAIL: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(f"{name}{': ' + detail if detail else ''}")


def load(rel: str) -> object:
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        check(f"JSON parses {rel}", False, str(exc))
        return {}


def text(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except Exception:
        return ""


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    required = [
        "research_brief.md", "gate_manifest.json", "gate_manifest.md",
        "artifact_contract.json", "artifact_contract.md", "main.tex", "main.pdf",
        "main_current_text.txt", "data/source_registry.json", "data/source_registry.md",
        "data/claim_audit.json", "data/claim_audit.md", "source_exhaustion_log.json",
        "source_exhaustion_log.md", "data/strategy_translation_packet_20260813.json",
        "data/portfolio_return_model_20260813.json", "analysis/house_view.md",
        "analysis/retail_underwriting_scorecard.md", "analysis/risk_framework.md",
        "analysis/variant_perception.md", "visual_review.md", "review_log.md",
        "final_signoff.json", "research_workflow_eval.json",
        "data/build_provenance_20260813.json",
    ]
    check("case root exists", ROOT.exists())
    check("required release artifacts exist", all((ROOT / rel).exists() for rel in required))
    sections = (
        "ch01_decision.tex", "ch02_global_methods.tex", "ch03_transferability.tex",
        "ch04_underwriting_playbook.tex", "ch05_china_constraints.tex",
        "ch06_monitoring.tex", "ch07_red_team.tex", "app_sources.tex",
    )
    check("all active section files exist", all((ROOT / "sections" / item).exists() for item in sections))

    manifest = load("gate_manifest.json")
    registry = load("data/source_registry.json")
    claims = load("data/claim_audit.json")
    packet = load("data/strategy_translation_packet_20260813.json")
    model = load("data/portfolio_return_model_20260813.json")
    signoff = load("final_signoff.json")
    workflow = load("research_workflow_eval.json")
    provenance = load("data/build_provenance_20260813.json")

    check("case profile is strategic allocation", isinstance(manifest, dict) and manifest.get("case_profile") == "strategic_allocation")
    controls = manifest.get("strategy_controls", {}) if isinstance(manifest, dict) else {}
    check("no named current direct equities", isinstance(controls, dict) and controls.get("named_t3_direct_equity_count") == 0 and controls.get("named_t3_direct_equity_tickers") == [])
    check("initial direct equity and REIT weights are zero", isinstance(controls, dict) and controls.get("initial_direct_stock_weight") == 0.0 and controls.get("reit_initial_weight") == 0.0)

    sources = registry.get("sources", []) if isinstance(registry, dict) else []
    source_ids = {row.get("source_id") for row in sources if isinstance(row, dict)}
    check("official source registry covers S01-S14", source_ids == {f"S{n:02d}" for n in range(1, 15)}, str(sorted(source_ids)))
    source_text = json.dumps(registry, ensure_ascii=False)
    for required_name in (
        "blackstone_2025_10k.pdf", "kkr_2025_10k.html", "apollo_2025_10k.html",
        "brookfield_2025_aif.pdf", "carlyle_2025_10k.html", "bain_2025_walker_review.pdf",
        "tpg_2025_10k.html", "sse_trading_rules_2026.docx",
        "sse_trading_rules_2026_deferred.docx", "sse_margin_rules_2023.docx",
        "szse_trading_rules_2026.pdf", "sse_public_reits_rules_2025.html",
        "sse_public_reits_measures_2025.docx", "sse_public_reits_listing_guide_2026.docx",
    ):
        check(f"archived source referenced {required_name}", required_name in source_text)
    check("S09 has operative and deferred-rule archive", "sse_trading_rules_2026.docx" in source_text and "sse_trading_rules_2026_deferred.docx" in source_text)
    check("S14 has operative margin-rule archive", "sse_margin_rules_2023.docx" in source_text)
    check("S10 and S11 have operative REIT-rule archives", "sse_public_reits_measures_2025.docx" in source_text and "sse_public_reits_listing_guide_2026.docx" in source_text)
    check("S11 has the correct issuance/listing guide title", "Issuance and Listing Administration" in source_text and "Publicly offered infrastructure REIT guide" not in source_text)
    for source in sources:
        if not isinstance(source, dict):
            continue
        paths = str(source.get("local_path", "")).split("; ")
        for item in paths:
            item = item.replace("release page: ", "")
            if item:
                check(f"registry local file exists {source.get('source_id')}", (ROOT / item).exists())

    rows = packet.get("manager_rows", []) if isinstance(packet, dict) else []
    check("seven-manager strategy matrix present", isinstance(rows, list) and len(rows) == 7)
    manager_names = {row.get("institution") for row in rows if isinstance(row, dict)}
    check("manager identity reconciles", manager_names == {"Blackstone", "KKR", "Apollo", "Brookfield", "Carlyle", "Bain Capital", "TPG"})
    row_audit_fields = ("documented_fact_locator", "documented_fact_class", "documented_structure_or_manager_described_feature", "analytical_inference")
    check("manager rows separate fact, locator and inference", all(all(str(row.get(field, "")).strip() for field in row_audit_fields) for row in rows if isinstance(row, dict)))
    packet_text = json.dumps(packet, ensure_ascii=False).lower()
    check("non-transferable institutional features explicit", all(term in packet_text for term in ("lbo", "control acquisition", "private direct origination", "non-public information")))
    check("strategy packet avoids causal outcome attribution", "outcomes are generated by" not in packet_text and "not a causal attribution" in packet_text)

    claim_rows = claims.get("claims", []) if isinstance(claims, dict) else []
    check("material claim audit has at least nine claims", isinstance(claim_rows, list) and len(claim_rows) >= 9)
    unresolved = []
    for row in claim_rows if isinstance(claim_rows, list) else []:
        if not isinstance(row, dict):
            unresolved.append("non-object")
            continue
        cited = row.get("source_ids", [])
        if not cited or any(source_id not in source_ids for source_id in cited):
            unresolved.append(str(row.get("claim_id")))
    check("every material claim resolves to registry sources", not unresolved, ", ".join(unresolved))

    base_core = model.get("active_base_core", []) if isinstance(model, dict) else []
    total = sum(float(row.get("weight", 0)) for row in base_core if isinstance(row, dict))
    check("inactive base-core weights sum to 100%", abs(total - 1.0) < 1e-9, str(total))
    check("return model makes no point forecast", isinstance(model, dict) and str(model.get("model_type", "")).lower().startswith("strategic allocation planning range"))
    activation = model.get("activation_controls", {}) if isinstance(model, dict) else {}
    direct_review = activation.get("direct_equities", {}).get("required_independent_review", []) if isinstance(activation, dict) and isinstance(activation.get("direct_equities"), dict) else []
    reit_review = activation.get("public_reits", {}).get("required_checks", []) if isinstance(activation, dict) and isinstance(activation.get("public_reits"), dict) else []
    check("future direct-equity dossier is sufficiently specified", isinstance(direct_review, list) and len(direct_review) >= 8)
    check("future REIT dossier is sufficiently specified", isinstance(reit_review, list) and len(reit_review) >= 7)

    reader = text("main_current_text.txt")
    for term in ("五票", "公开证据", "不构成", "q=0", "控制权", "LBO", "REIT", "红队"):
        check(f"reader-facing report contains {term}", term in reader)
    check("reader-facing report labels institutional claims as non-causal", "不是历史业绩的因果拆解" in reader and "不证明个人可以复制回报" in reader)
    check("reader-facing report defines core foreign abbreviations", all(term in reader for term in ("杠杆收购（LBO）", "关键经营指标（KPI）", "内部收益率（IRR）", "市盈率（PE）", "超额收益（alpha）")))
    check("reader-facing report states no return guarantee", "并不保证" in reader or "不承诺收益" in reader)
    check("reader-facing report does not promise current implementation", "实施批准" in reader and "没有" in reader)
    check("reader-facing report contains no absolute local path", "/home/" not in reader and "/workspace/" not in reader)
    check("reader-facing report avoids generic numeric allocation advice", all(token not in reader for token in ("1–2.5%", "0.25–0.50%", "20–25%", "单股上限5%")))
    check("reader-facing report distinguishes settlement from T+1 shorthand", "交收前不得卖出" in reader and "T+1" not in reader)
    check("reader-facing report treats ETF mechanics as category-specific", "不能将某类 ETF 的机制泛化" in reader)
    check("reader-facing report treats price-limit settings as heterogeneous", "价格限制不是全市场恒定数字" in reader)

    tex = text("main.tex")
    check("XeLaTeX engine is declared", "xelatex" in tex.lower())
    check("PDF is nonempty", (ROOT / "main.pdf").exists() and (ROOT / "main.pdf").stat().st_size > 100000)
    pdf_info = subprocess.run(["pdfinfo", "main.pdf"], cwd=ROOT, text=True, capture_output=True, check=False)
    check("PDF metadata reports at least 15 pages", "Pages:" in pdf_info.stdout and int(pdf_info.stdout.split("Pages:")[1].splitlines()[0].strip()) >= 15)
    check("build provenance is current", isinstance(provenance, dict) and provenance.get("pdf_sha256") == sha(ROOT / "main.pdf") and provenance.get("source_sha256") == sha(ROOT / "main.tex"))
    check("build provenance records XeLaTeX", isinstance(provenance, dict) and "xelatex" in json.dumps(provenance, ensure_ascii=False).lower())
    check("visual review sampled pages", all(f"release-page-{n:02d}.png" in text("visual_review.md") for n in (1, 5, 6, 11, 13, 16, 18)))

    cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("all five review finding files exist", all((ROOT / f"review_findings_{cycle}.json").exists() for cycle in cycles))
    check("R0-R3 repair-plan pairs exist", all((ROOT / f"repair_plan_{cycle}.json").exists() and (ROOT / f"repair_plan_{cycle}.md").exists() for cycle in cycles[:-1]))
    review_blob = "\n".join(text(f"review_findings_{cycle}.json") for cycle in cycles)
    unresolved_sa = []
    for cycle in cycles:
        finding_doc = load(f"review_findings_{cycle}.json")
        for finding in finding_doc.get("findings", []) if isinstance(finding_doc, dict) else []:
            if not isinstance(finding, dict):
                continue
            severity = str(finding.get("severity", ""))
            status = str(finding.get("status", "")).lower()
            if severity in {"S", "A"} and ("open" in status or "pending" in status or "reopened" in status):
                unresolved_sa.append(str(finding.get("id", cycle)))
    check("review findings have no unresolved S/A", not unresolved_sa, ", ".join(unresolved_sa))
    check("review log contains score", "Publishability Score:" in text("review_log.md"))

    check("final signoff is framework pass", isinstance(signoff, dict) and str(signoff.get("signoff_status", "")).lower() == "research_framework_pass")
    check("final signoff keeps implementation not approved", isinstance(signoff, dict) and str(signoff.get("implementation_status", "")).lower() == "not_approved")
    execution = signoff.get("execution_eligibility", {}) if isinstance(signoff, dict) else {}
    check("final signoff keeps q zero and execution off", isinstance(execution, dict) and execution.get("q") == 0.0 and execution.get("live_execution_authorized") is False)
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("workflow evaluator is publishable framework only", isinstance(quality, dict) and quality.get("publishable") is True and str(quality.get("implementation_status", "")).lower() == "not_approved")

    for item in PASS:
        print(f"PASS {item}")
    for item in FAIL:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(PASS)} PASS / {len(FAIL)} FAIL")
    print("RESULT PASS" if not FAIL else "RESULT FAIL")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
