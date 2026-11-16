#!/usr/bin/env python3
"""Validate C33's binding to the C31/C34/C35/C36 research-only packet."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
ANALYSIS = CASE_DIR / "analysis"
DATA = CASE_DIR / "data"
EXPECTED_CODES = ["510300", "510880", "511010", "518880", "511990"]
BANNED_CAPITAL_TERMS = re.compile(
    r"本金|初始资金|初始金额|initial[ _-]?capital|principal|starting amount", re.IGNORECASE
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_artifact_path(path_text: str) -> Path:
    """Resolve case-relative artifacts and explicitly retained repository paths."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    if path_text.startswith("workspace/"):
        return REPO_ROOT / path
    return CASE_DIR / path


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    paths = {
        "c31": ANALYSIS / "c31_etf_product_diligence_refresh_20260815.json",
        "c34_protocol": ANALYSIS / "c34_dual_horizon_inverse_vol_etf_protocol_20260815.json",
        "c34": ANALYSIS / "c34_dual_horizon_inverse_vol_etf_candidate_20260815.json",
        "c35": ANALYSIS / "c35_c34_operational_action_card_20260815.json",
        "c36": ANALYSIS / "c36_c31_source_crosscheck_20260815.json",
        "c33": ANALYSIS / "c33_integrated_candidate_strategy_20260815.json",
        "ledger": DATA / "c33_forward_paper_ledger_template_20260815.json",
        "registry": DATA / "source_registry.json",
        "claims": DATA / "claim_audit.json",
        "gates": CASE_DIR / "gate_manifest.json",
    }
    failures: list[str] = []
    for label, path in paths.items():
        check(path.is_file(), f"missing {label}: {path}", failures)
    if failures:
        print("FAIL: C33 integration validator")
        print("\n".join(f"- {item}" for item in failures))
        return 1

    c31 = load(paths["c31"])
    c34_protocol = load(paths["c34_protocol"])
    c34 = load(paths["c34"])
    c35 = load(paths["c35"])
    c36 = load(paths["c36"])
    c33 = load(paths["c33"])
    ledger = load(paths["ledger"])
    registry = load(paths["registry"])
    claims = load(paths["claims"])
    gates = load(paths["gates"])

    c33_codes = [item["code"] for item in c33["actual_instruments"]]
    c31_codes = c31["scope"]["c30_actual_instruments"]
    c34_codes = c34_protocol["source"]["allowed_codes"]
    c35_codes = c35["product_map"]["closed_codes"]
    check(c33_codes == EXPECTED_CODES, "C33 exact code order differs", failures)
    check(c31_codes == EXPECTED_CODES, "C31 core code order differs", failures)
    check(c34_codes == EXPECTED_CODES, "C34 frozen universe differs", failures)
    check(c35_codes == EXPECTED_CODES, "C35 product map differs", failures)

    rule = c34_protocol["base_rule"]
    check(rule["score_horizons_common_observations"] == [126, 252], "C34 horizons differ", failures)
    check(rule["realized_volatility"]["return_observations"] == 60, "C34 volatility lookback differs", failures)
    check(rule["eligibility"] == "risk_sleeve_score > fallback_score, strictly", "C34 strict eligibility differs", failures)
    check(c33["dynamic_rule"]["equity_split"] == {"510300": 0.5, "510880": 0.5}, "C33 equity split differs", failures)
    check(c33["dynamic_rule"]["warmup_or_no_active_sleeve"] == {"511990": 1.0}, "C33 fallback differs", failures)
    check(c33["timing_and_actions"]["earliest_effective_session"].startswith("E: following common session"), "C33 D/E timing differs", failures)

    full = c34["hurdle_assessment"]["base_full_sample"]
    holdout = c34["hurdle_assessment"]["base_holdout"]
    c33_proxy = c33["historical_proxy_evidence"]
    check(
        c33_proxy["base_full_sample"]["annualized_market_price_proxy_change_after_illustrative_cost"]
        == full["annualized_market_price_proxy_change_after_illustrative_cost"],
        "C33 full-sample annualization differs from C34",
        failures,
    )
    check(c33_proxy["base_full_sample"]["rolling_five_year_endpoints_below_5pct"] == "43/98", "C33 rolling failure count differs", failures)
    check(
        c33_proxy["chronological_robustness_slice_2020_2025"]["annualized_market_price_proxy_change_after_illustrative_cost"]
        == holdout["annualized_market_price_proxy_change_after_illustrative_cost"],
        "C33 chronological slice differs from C34",
        failures,
    )
    check(c33["admission"]["strict_five_percent_proxy_hurdle"] == "FAIL", "C33 must retain strict proxy failure", failures)
    check(c33["admission"]["result"] == "NO_ADMITTED_USABLE_STRATEGY", "C33 admission result differs", failures)
    check(c33["status"] == "research_only_not_paper_operable_not_admitted", "C33 status differs", failures)
    check(c33["current_action"] == "NO_ACTION", "C33 current action differs", failures)
    check(c33["external_orders"] is False and c33["portfolio_q"] == 0, "C33 external-action boundary differs", failures)
    check(c35["status"] == "research_only_forward_ledger_incomplete", "C35 forward-ledger gate differs", failures)
    check(c36["source_integrity_status"] == "PASS", "C36 dated source integrity must pass", failures)
    check(c36["actionability_status"] == "VETO", "C36 actionability must remain VETO", failures)
    check(ledger["status"] == "template_only_no_observations", "forward ledger must remain empty template", failures)

    by_source = {item["source_id"]: item for item in registry["records"]}
    for evidence in c33["evidence_refs"]:
        path = resolve_artifact_path(evidence["artifact"])
        check(path.is_file(), f"C33 evidence path missing: {evidence['artifact']}", failures)
        if path.is_file():
            check(digest(path) == evidence["sha256"], f"C33 evidence hash mismatch: {evidence['artifact']}", failures)
    c31_evidence = next((item for item in c33["evidence_refs"] if item["artifact"] == "analysis/c31_etf_product_diligence_refresh_20260815.json"), None)
    check(c31_evidence is not None, "C33 misses C31 evidence reference", failures)
    if c31_evidence is not None:
        manifest = c31_evidence.get("upstream_venue_master_manifest")
        check(isinstance(manifest, dict), "C33 misses direct upstream venue-master manifest binding", failures)
        if isinstance(manifest, dict):
            manifest_path = resolve_artifact_path(manifest.get("path", ""))
            check(manifest_path.is_file(), "C33 upstream venue-master manifest path missing", failures)
            if manifest_path.is_file():
                check(digest(manifest_path) == manifest.get("sha256"), "C33 upstream venue-master manifest hash mismatch", failures)
            check(
                manifest.get("scope")
                == "Six R4 master-response codes: five actual-core codes 510300, 510880, 511010, 518880 and 511990, plus non-core 510500.",
                "C33 upstream venue-master manifest scope differs",
                failures,
            )
    for source_id in ("S38", "S39", "S40", "S41", "S42"):
        item = by_source.get(source_id)
        check(item is not None, f"source registry missing {source_id}", failures)
        if item:
            path = CASE_DIR / item["path"]
            check(path.is_file() and digest(path) == item["sha256"], f"source registry hash mismatch: {source_id}", failures)
    claim_ids = {item["claim_id"] for item in claims["claims"]}
    check({"CL18", "CL19", "CL20"}.issubset(claim_ids), "claim audit misses C34/C35 claims", failures)
    check("analysis/c33_integrated_candidate_strategy_20260815.json" in gates["required_artifacts"], "gate manifest misses C33", failures)

    reader_paths = [
        ANALYSIS / "c33_integrated_candidate_strategy_20260815.md",
        ANALYSIS / "c34_dual_horizon_inverse_vol_etf_candidate_20260815.md",
        ANALYSIS / "c35_c34_operational_action_card_20260815.md",
        CASE_DIR / "research_brief.md",
    ]
    for path in reader_paths:
        check(not BANNED_CAPITAL_TERMS.search(path.read_text(encoding="utf-8")), f"banned capital wording in {path.name}", failures)

    if failures:
        print("FAIL: C33 integration validator")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("PASS: C33 binds exactly to C31/C34/C35/C36 and remains research-only / NO_ACTION.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
