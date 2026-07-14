#!/usr/bin/env python3
"""Case-local integrity verifier for the Tongding Interconnect report."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def close(a: float, b: float, tolerance: float = 0.02) -> bool:
    return abs(a - b) <= tolerance


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
        "analysis/template_brief.md",
        "analysis/house_view.md",
        "analysis/variant_perception.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/segment_valuation_model.md",
        "analysis/secondary_market_analysis.md",
        "analysis/growth_earnings_model.md",
        "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md",
        "analysis/risk_framework.md",
        "analysis/exhibit_plan.md",
        "data/current_valuation_model_20260714.json",
        "data/growth_driver_model.json",
        "data/broker_street_consensus_20260714.json",
        "data/source_registry.json",
        "data/claim_audit.json",
        "source_exhaustion_log.json",
        "source_exhaustion_log.md",
        "review_log.md",
        "final_signoff.json",
        "final_signoff.md",
    ]
    failures = [rel for rel in required if not (ROOT / rel).exists()]
    model = load("data/current_valuation_model_20260714.json")["rows"][0]
    expected_market_cap = model["current_price"] * model["shares_100mn"]
    if not close(expected_market_cap, model["market_cap_100mn_cny"]):
        failures.append("market_cap_reconciliation")
    expected_upside = model["final_target"] / model["current_price"] - 1
    if not close(expected_upside, model["upside"], 0.0001):
        failures.append("upside_reconciliation")
    base = model["base"]
    expected_base = (
        0.50 * base["pe_value"]
        + 0.25 * base["pb_value"]
        + 0.25 * base["ps_value"]
    )
    if not close(expected_base, base["target_price"]):
        failures.append("base_target_reconciliation")
    expected_final = 0.90 * model["base_target"] + 0.10 * model["market_implied_anchor"]
    if not close(expected_final, model["final_target"]):
        failures.append("final_target_reconciliation")
    audit = (ROOT / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    if "Model Reproducibility: PASS" not in audit:
        failures.append("valuation_reproducibility")
    text = (ROOT / "main_current_text.txt").read_text(encoding="utf-8")
    for anchor in ("20.86", "10.09", "9.16", "5.07", "14.96", "1.70", "2.30"):
        if anchor not in text:
            failures.append(f"pdf_anchor_{anchor}")
    if "TODO" in text or "待补" in text:
        failures.append("unfinished_marker")
    try:
        result = subprocess.run(
            ["pdfinfo", str(ROOT / "main.pdf")],
            text=True,
            capture_output=True,
            check=True,
        )
        match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
        if not match or int(match.group(1)) < 10:
            failures.append("pdf_pages")
    except subprocess.CalledProcessError:
        failures.append("pdfinfo")
    print(f"checked {len(required)} required artifacts")
    if failures:
        print("FAIL " + ", ".join(failures))
        return 1
    print("PASS tongding interconnect case verifier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
