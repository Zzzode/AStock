#!/usr/bin/env python3
"""Case-local integrity checks for the Dongshan Precision report."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    required = [
        "research_brief.md",
        "gate_manifest.md",
        "gate_manifest.json",
        "artifact_contract.md",
        "artifact_contract.json",
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/segment_valuation_model.md",
        "analysis/secondary_market_analysis.md",
        "analysis/growth_earnings_model.md",
        "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md",
        "data/current_valuation_model_20260714.json",
        "data/growth_driver_model.json",
        "data/broker_street_consensus_20260714.json",
        "data/source_registry.json",
        "data/claim_audit.json",
        "source_exhaustion_log.json",
        "source_exhaustion_log.md",
        "review_log.md",
        "final_signoff.json",
    ]
    failures = [rel for rel in required if not (ROOT / rel).exists()]
    model = load("data/current_valuation_model_20260714.json")["rows"][0]
    expected_market_cap = model["current_price"] * model["shares_100mn"]
    if abs(expected_market_cap - model["market_cap_100mn_cny"]) > 0.02:
        failures.append("market_cap_reconciliation")
    expected_upside = model["final_target"] / model["current_price"] - 1
    if abs(expected_upside - model["upside"]) > 0.0001:
        failures.append("upside_reconciliation")
    if "Model Reproducibility: PASS" not in (ROOT / "analysis/valuation_audit.md").read_text(encoding="utf-8"):
        failures.append("valuation_reproducibility")
    if "CNY201.70" not in (ROOT / "main_current_text.txt").read_text(encoding="utf-8"):
        failures.append("target_missing_from_pdf_text")
    if "TODO" in (ROOT / "main_current_text.txt").read_text(encoding="utf-8"):
        failures.append("unfinished_marker")
    try:
        result = subprocess.run(
            ["pdfinfo", str(ROOT / "main.pdf")],
            text=True,
            capture_output=True,
            check=True,
        )
        if not re.search(r"^Pages:\s+\d+", result.stdout, re.MULTILINE):
            failures.append("pdf_pages")
    except subprocess.CalledProcessError:
        failures.append("pdfinfo")
    print(f"{len(required) - len([x for x in failures if x in required])} required artifacts checked")
    if failures:
        print("FAIL " + ", ".join(failures))
        return 1
    print("PASS dongshan precision case verifier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
