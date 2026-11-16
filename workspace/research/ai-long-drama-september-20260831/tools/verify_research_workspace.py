#!/usr/bin/env python3
"""Case-local acceptance checks for the observation-only tactical memo."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
checks = []
def check(name, ok):
    checks.append((name, bool(ok)))

for rel in [
    "research_brief.md", "gate_manifest.md", "gate_manifest.json", "artifact_contract.md",
    "artifact_contract.json", "data/source_registry.md", "data/source_registry.json",
    "data/claim_audit.md", "data/claim_audit.json", "source_exhaustion_log.md",
    "source_exhaustion_log.json", "data/raw_market_data.md", "analysis/evidence_ledger.md",
    "analysis/tactical_preplan.md", "analysis/theme_gate_scorecard.md",
    "analysis/theme_gate_scorecard.json", "analysis/daily_theme_evidence_packet_template.md",
    "analysis/non_chinext_candidate_audit.md", "analysis/risk_framework.md",
    "analysis/prose_style_audit.md", "analysis/prose_style_audit.json",
    "sources/official-catalyst-20260831/mgtv_programme_page_capture.md", "main.tex", "main.pdf",
    "main_current_text.txt", "review_log.md", "review_findings_R0_evidence.json",
    "review_findings_R2_draft.json", "review_findings_R3_render_compliance.json",
    "review_findings_R4_final_ic.json", "repair_plan_R0_evidence.md",
    "repair_plan_R0_evidence.json", "repair_plan_R2_draft.md", "repair_plan_R2_draft.json",
    "repair_plan_R3_render_compliance.md", "repair_plan_R3_render_compliance.json",
    "final_signoff.md", "final_signoff.json", "research_workflow_eval.md",
    "research_workflow_eval.json",
]: check(f"exists {rel}", (root / rel).exists())

registry = json.loads((root / "data/source_registry.json").read_text())
claim_audit = json.loads((root / "data/claim_audit.json").read_text())
scorecard = json.loads((root / "analysis/theme_gate_scorecard.json").read_text())
signoff = json.loads((root / "final_signoff.json").read_text())
style = json.loads((root / "analysis/prose_style_audit.json").read_text())
check("source registry carries S01-S13", {row["id"] for row in registry} == {f"S{i:02d}" for i in range(1, 14)})
check("source registry has URLs and boundaries", all(row.get("url") and row.get("boundary") for row in registry))
check("claim audit has adopted wording", all(row.get("adopted_wording") for row in claim_audit))
check("five simultaneous scorecard gates", len(scorecard.get("gates", [])) == 5)
check("project-direct tier required", "project_direct" in scorecard.get("as_of_rule", ""))
template_text = (root / "analysis/daily_theme_evidence_packet_template.md").read_text()
check("daily packet can express project-direct tier", "project_direct" in template_text)
check("style scan clean", style.get("prohibited_pattern_hits") == 0)
check("signoff blocks paper entry", signoff.get("paper_entry_status") == "blocked")
check("signoff has zero S/A", signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
check("PDF is non-empty", (root / "main.pdf").stat().st_size > 100000)
governance_text = "\n".join((root / rel).read_text() for rel in ["data/source_registry.md", "data/claim_audit.md", "analysis/evidence_ledger.md"])
check("S04 governance records have no stale broadcast claim", "30-episode" not in governance_text and "broadcast on Hunan TV" not in governance_text and "platform and TV broadcast" not in governance_text)

assert len(checks) == 51, len(checks)
failed = 0
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} | {name}")
    failed += not ok
print(f"SUMMARY | {len(checks)-failed} PASS / {failed} FAIL")
raise SystemExit(1 if failed else 0)
