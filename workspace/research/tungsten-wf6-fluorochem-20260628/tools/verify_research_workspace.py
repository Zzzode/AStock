#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

def ok_file(rel: str) -> tuple[bool, str]:
    p = BASE / rel
    return p.exists() and p.stat().st_size > 0, rel

def load_json(rel: str):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))

def pdf_pages() -> tuple[bool, str]:
    p = BASE / "main.pdf"
    if not p.exists():
        return False, "main.pdf missing"
    proc = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True)
    if proc.returncode != 0:
        return False, "pdfinfo failed"
    pages = 0
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
    return pages >= 15, f"pages={pages}"

def valuation_complete() -> tuple[bool, str]:
    rows = load_json("data/current_valuation_model_20260628.json").get("rows", [])
    missing = []
    for r in rows:
        for k in [
            "code",
            "name",
            "price",
            "shares",
            "market_cap",
            "revenue_2026e",
            "np_2026e",
            "eps_2026e",
            "bear_target",
            "base_target",
            "bull_target",
            "market_anchor",
            "weights_text",
            "final_target",
            "final_upside",
            "action",
            "next_quarter_threshold",
            "catalyst",
            "invalidation",
        ]:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('code')}:{k}")
    text = (BASE / "analysis/valuation_model.md").read_text(encoding="utf-8")
    required_sections = [
        "Final Valuation Table",
        "Three-Tier Targets",
        "Relative / PEG / PSG Comparison",
        "Seasonality Calibration",
        "Next-Quarter Threshold",
        "Method and Assumption Bridge",
        "Market-Expectation Valuation Bridge",
        "Broker/Street Comparison",
        "Market-Implied Sentiment Anchor",
    ]
    missing_sections = [s for s in required_sections if s not in text]
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    audit_ok = all(s in audit for s in ["Arithmetic Checks", "Forecast Availability", "Market-Implied Sentiment Anchor", "Required Fixes"])
    return len(rows) == 18 and not missing and not missing_sections and audit_ok, f"rows={len(rows)}, missing={missing[:3]}, sections={missing_sections}, audit={audit_ok}"

def source_registry() -> tuple[bool, str]:
    j = load_json("data/source_registry.json")
    return len(j.get("sources", [])) >= 8, f"sources={len(j.get('sources', []))}, captured={j.get('captured_count')}"

def mermaid_exists() -> tuple[bool, str]:
    text = (BASE / "analysis/wf6_chain_map.mmd").read_text(encoding="utf-8")
    return text.startswith("flowchart"), "Mermaid flowchart"

def json_valid() -> tuple[bool, str]:
    total = 0
    for p in list((BASE / "data").glob("*.json")) + list(BASE.glob("*.json")):
        total += 1
        json.loads(p.read_text(encoding="utf-8"))
    return total >= 5, f"json={total}"

def no_placeholders() -> tuple[bool, str]:
    text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    bad = ["<Report Title>", "TODO", "PLACEHOLDER"]
    hits = [b for b in bad if b in text]
    return not hits, f"hits={hits}"

def main() -> int:
    checks = []
    for rel in [
        "research_brief.md",
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
        "data/raw_market_data.md",
        "data/raw_financials.md",
        "data/verified_market_data.md",
        "data/verified_financials.md",
        "data/source_registry.md",
        "data/claim_audit.md",
        "analysis/industry_landscape.md",
        "analysis/house_view.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/risk_framework.md",
        "review_log.md",
        "completion_audit_manifest.json",
        "completion_audit_manifest.md",
        "source_exhaustion_log.json",
        "source_exhaustion_log.md",
        "data_room_index.md",
    ]:
        passed, detail = ok_file(rel)
        checks.append((f"file:{rel}", passed, detail))
    for name, fn in [
        ("pdf_pages", pdf_pages),
        ("valuation_complete", valuation_complete),
        ("source_registry", source_registry),
        ("mermaid_exists", mermaid_exists),
        ("json_valid", json_valid),
        ("no_placeholders", no_placeholders),
    ]:
        passed, detail = fn()
        checks.append((name, passed, detail))
    fail = 0
    for name, passed, detail in checks:
        print(("PASS" if passed else "FAIL") + f": {name} - {detail}")
        fail += 0 if passed else 1
    print(f"SUMMARY: PASS={len(checks)-fail} FAIL={fail}")
    return 1 if fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
