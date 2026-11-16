#!/usr/bin/env python3
"""Read-only structural validator for the C35 action card.

The validator confirms that C35 mirrors the frozen C34 dual-horizon rule and
the C31 five-code product-card boundary. It deliberately cannot calculate an
outcome, elevate the candidate to paper_operable, or authorize an external
action.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


DATE_TAG = "20260815"
CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
ANALYSIS_DIR = CASE_DIR / "analysis"
C34_JSON = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_protocol_{DATE_TAG}.json"
C34_MD = ANALYSIS_DIR / f"c34_dual_horizon_inverse_vol_etf_protocol_{DATE_TAG}.md"
C31_JSON = ANALYSIS_DIR / f"c31_etf_product_diligence_refresh_{DATE_TAG}.json"
C31_MD = ANALYSIS_DIR / f"c31_etf_product_diligence_refresh_{DATE_TAG}.md"
C35_JSON = ANALYSIS_DIR / f"c35_c34_operational_action_card_{DATE_TAG}.json"
C35_MD = ANALYSIS_DIR / f"c35_c34_operational_action_card_{DATE_TAG}.md"
FORWARD_LEDGER = CASE_DIR / "data" / f"c33_forward_paper_ledger_template_{DATE_TAG}.json"
EXPECTED_CODES = ("510300", "510880", "511010", "518880", "511990")
EPSILON = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    return REPO_ROOT / path if path_text.startswith("workspace/") else CASE_DIR / path


def fail(message: str) -> None:
    raise ValueError(message)


def inverse_vol_target(scores: dict[str, float], fallback_score: float, volatilities: dict[str, float]) -> dict[str, float]:
    """Implement the frozen C34 target calculation for deterministic checks only."""

    active = [sleeve for sleeve in ("equity", "bond", "gold") if scores[sleeve] > fallback_score]
    if not active:
        return {"510300": 0.0, "510880": 0.0, "511010": 0.0, "518880": 0.0, "511990": 1.0}

    inverse: dict[str, float] = {}
    for sleeve in active:
        volatility = float(volatilities[sleeve])
        if not math.isfinite(volatility) or volatility <= 0.0:
            fail(f"invalid active-sleeve volatility for {sleeve}")
        inverse[sleeve] = 1.0 / volatility

    denominator = sum(inverse.values())
    if not math.isfinite(denominator) or denominator <= 0.0:
        fail("invalid inverse-volatility denominator")

    sleeve_weights = {sleeve: inverse[sleeve] / denominator for sleeve in active}
    target = {
        "510300": 0.5 * sleeve_weights.get("equity", 0.0),
        "510880": 0.5 * sleeve_weights.get("equity", 0.0),
        "511010": sleeve_weights.get("bond", 0.0),
        "518880": sleeve_weights.get("gold", 0.0),
        "511990": 0.0,
    }
    if any(not math.isfinite(weight) or weight < -EPSILON for weight in target.values()):
        fail("target has invalid weight")
    if abs(sum(target.values()) - 1.0) > EPSILON:
        fail("target weights do not sum to one")
    return target


def validate_target_math() -> str:
    if abs((0.5 * 0.10 + 0.5 * 0.02) - 0.06) > EPSILON:
        fail("dual-horizon score arithmetic is invalid")

    target = inverse_vol_target(
        {"equity": 0.07, "bond": 0.06, "gold": 0.05},
        0.04,
        {"equity": 0.10, "bond": 0.20, "gold": 0.40},
    )
    expected = {"510300": 2.0 / 7.0, "510880": 2.0 / 7.0, "511010": 2.0 / 7.0, "518880": 1.0 / 7.0, "511990": 0.0}
    for code, expected_weight in expected.items():
        if abs(target[code] - expected_weight) > EPSILON:
            fail(f"inverse-volatility target mismatch for {code}")

    equality_target = inverse_vol_target(
        {"equity": 0.04, "bond": 0.03, "gold": 0.02},
        0.04,
        {"equity": 0.10, "bond": 0.20, "gold": 0.40},
    )
    if equality_target != {"510300": 0.0, "510880": 0.0, "511010": 0.0, "518880": 0.0, "511990": 1.0}:
        fail("strict score equality does not fall back")

    try:
        inverse_vol_target(
            {"equity": 0.07, "bond": 0.03, "gold": 0.02},
            0.04,
            {"equity": 0.0, "bond": 0.20, "gold": 0.40},
        )
    except ValueError:
        return "base/equality/invalid-volatility target tests passed"
    fail("invalid active-sleeve volatility did not fail closed")


def validate_c34(c34: dict[str, Any]) -> None:
    if c34.get("artifact_id") != "D5PT-C34-PROTOCOL-v1":
        fail("C34 artifact identity differs")
    if c34.get("status") != "frozen_for_research_only_calculation" or c34.get("research_only") is not True:
        fail("C34 is not frozen research-only")
    if c34.get("external_orders") is not False:
        fail("C34 external-order boundary differs")
    if tuple(c34.get("source", {}).get("allowed_codes", [])) != EXPECTED_CODES:
        fail("C34 five-code universe differs")

    sleeves = c34.get("sleeves", {})
    if tuple(sleeves.get("equity", {}).get("codes", [])) != ("510300", "510880"):
        fail("C34 equity sleeve differs")
    if sleeves.get("equity", {}).get("component_weights") != [0.5, 0.5]:
        fail("C34 equity split differs")
    if sleeves.get("bond", {}).get("code") != "511010" or sleeves.get("gold", {}).get("code") != "518880" or sleeves.get("fallback", {}).get("code") != "511990":
        fail("C34 sleeve map differs")

    base = c34.get("base_rule", {})
    if base.get("score_horizons_common_observations") != [126, 252]:
        fail("C34 score horizons differ")
    if base.get("eligibility") != "risk_sleeve_score > fallback_score, strictly":
        fail("C34 eligibility differs")
    volatility = base.get("realized_volatility", {})
    if volatility.get("return_observations") != 60 or volatility.get("ddof") != 1 or volatility.get("weighting") != "active sleeve weights proportional to inverse realized volatility":
        fail("C34 volatility rule differs")
    if any(base.get(name) is not False for name in ("leverage", "shorting", "futures", "options", "borrowing")):
        fail("C34 prohibited exposure control differs")

    timing = c34.get("timing", {})
    if timing.get("decision") != "final common market-price close of each calendar month" or timing.get("execution") != "following common session at reported open only":
        fail("C34 decision/effective timing differs")
    if timing.get("same_session_close_execution") is not False or timing.get("same_bar_lookahead") is not False:
        fail("C34 timing safeguards differ")

    protection = c34.get("forward_paper_order_protection", {})
    if protection.get("buy") != "displayed ask <= IOPV * 1.003" or protection.get("sell") != "displayed bid >= IOPV * 0.997":
        fail("C34 price protection differs")


def validate_c31(c31: dict[str, Any], c34: dict[str, Any]) -> None:
    if c31.get("artifact_id") != "D5PT-C31-ETF-DIL-v1":
        fail("C31 artifact identity differs")
    if c31.get("research_only") is not True or c31.get("external_action_authorized") is not False:
        fail("C31 research/action boundary differs")
    if tuple(c31.get("lean_research_core", {}).get("codes", [])) != tuple(c34["source"]["allowed_codes"]):
        fail("C31 core differs from C34 universe")

    product_by_code = {str(product.get("code")): product for product in c31.get("products", [])}
    for code in EXPECTED_CODES:
        product = product_by_code.get(code)
        if not product:
            fail(f"C31 is missing core product {code}")
        refs = product.get("source_refs", [])
        if len(refs) < 2:
            fail(f"C31 lacks source links for {code}")
        for ref in refs:
            path = resolve_repo_path(str(ref.get("path", "")))
            if not path.is_file():
                fail(f"C31 source link missing for {code}: {path}")
            expected_hash = ref.get("sha256")
            if expected_hash and sha256_file(path) != expected_hash:
                fail(f"C31 source hash differs for {code}: {path}")


def validate_c34_market_source(c34: dict[str, Any]) -> None:
    manifest_path = resolve_repo_path(str(c34["source"]["manifest_path"]))
    manifest = load_json(manifest_path)
    by_code = {str(row.get("code")): row for row in manifest.get("files", [])}
    for code in EXPECTED_CODES:
        row = by_code.get(code)
        if not row:
            fail(f"C34 market-source manifest lacks {code}")
        raw_path = resolve_repo_path(str(row.get("path", "")))
        if not raw_path.is_file():
            fail(f"C34 market-source response missing for {code}")
        if sha256_file(raw_path) != row.get("sha256"):
            fail(f"C34 market-source hash differs for {code}")
        if raw_path.stat().st_size != int(row.get("bytes", -1)):
            fail(f"C34 market-source size differs for {code}")


def validate_c35(c35: dict[str, Any]) -> None:
    if c35.get("artifact_id") != "D5PT-C35-v1":
        fail("C35 artifact identity differs")
    if c35.get("status") != "research_only_forward_ledger_incomplete" or c35.get("research_only") is not True or c35.get("paper_operable") is not False:
        fail("C35 must remain research-only and not paper-operable")
    if c35.get("external_orders") is not False or c35.get("broker_or_account_mutation") is not False:
        fail("C35 external-action boundary differs")

    links = c35.get("source_links", {})
    expected_links = {
        "c34_protocol": C34_JSON,
        "c31_product_cards": C31_JSON,
        "forward_paper_ledger_template": FORWARD_LEDGER,
    }
    for key, path in expected_links.items():
        link = links.get(key, {})
        if link.get("path") != str(path.relative_to(REPO_ROOT)):
            fail(f"C35 source link path differs for {key}")
        if link.get("sha256") != sha256_file(path):
            fail(f"C35 source link hash differs for {key}")

    product_map = c35.get("product_map", {})
    if tuple(product_map.get("closed_codes", [])) != EXPECTED_CODES:
        fail("C35 code map differs")
    if product_map.get("equity", {}).get("component_weights_within_equity_sleeve") != [0.5, 0.5]:
        fail("C35 equity split differs")
    if any(product_map.get("excluded", {}).get(name) is not False for name in ("leverage", "shorting", "futures", "options", "borrowing", "automatic_substitution")):
        fail("C35 prohibited exposure control differs")

    math_rule = c35.get("dynamic_target_math", {})
    if math_rule.get("score_horizons_common_observations") != [126, 252] or math_rule.get("eligibility") != "risk sleeve score > fallback score, strictly; equality is inactive":
        fail("C35 score rule differs")
    if math_rule.get("realized_volatility", {}).get("return_observations") != 60 or math_rule.get("realized_volatility", {}).get("ddof") != 1:
        fail("C35 volatility rule differs")
    if math_rule.get("active_sleeve_weight") != "(1 / volatility_sleeve) / sum(1 / volatility_active_sleeves)":
        fail("C35 inverse-volatility rule differs")

    timing = c35.get("timing", {})
    if timing.get("decision") != "after the final common market-price close D of each calendar month" or timing.get("earliest_effective") != "following common session E at reported open only":
        fail("C35 timing differs")
    if timing.get("same_session_close_execution") is not False or timing.get("same_bar_lookahead") is not False:
        fail("C35 timing safeguards differ")

    protection = c35.get("price_protection", {})
    if protection.get("buy_cap") != "IOPV * 1.003 rounded to verified tick" or protection.get("sell_floor") != "IOPV * 0.997 rounded to verified tick":
        fail("C35 price protection differs")

    forward = c35.get("forward_paper_gate", {})
    if forward.get("minimum_uninterrupted_months") != 6 or forward.get("current_outcome") != "research_only" or forward.get("paper_operable_transition") != "not permitted by C35 or its validator":
        fail("C35 forward-paper boundary differs")


def validate_markdown() -> None:
    for path, markers in (
        (C34_MD, ("C34 Dual-Horizon", "126", "252", "60", "510300", "511990")),
        (C31_MD, ("C31", "510300", "510880", "511010", "518880", "511990")),
        (C35_MD, ("C35", "D5PT-C34-PROTOCOL-v1", "NO_ACTION", "paper_operable=false", "IOPV × 1.003", "IOPV × 0.997")),
    ):
        if not path.is_file():
            fail(f"Markdown mirror missing: {path}")
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                fail(f"Markdown mirror lacks required marker {marker}: {path}")


def validate_forward_ledger_boundary() -> None:
    ledger = load_json(FORWARD_LEDGER)
    if ledger.get("status") != "template_only_no_observations" or ledger.get("research_only") is not True or ledger.get("external_orders") is not False:
        fail("forward-paper ledger state differs from incomplete research-only boundary")
    if ledger.get("minimum_observation_months") != 6:
        fail("forward-paper ledger minimum period differs")


def main() -> int:
    checks: list[str] = []
    try:
        c34 = load_json(C34_JSON)
        c31 = load_json(C31_JSON)
        c35 = load_json(C35_JSON)
        validate_c34(c34)
        checks.append("C34 frozen rule, target inputs, timing, protection, and prohibited-exposure controls")
        validate_c31(c31, c34)
        checks.append("C31 five-code core and dated source-card links")
        validate_c34_market_source(c34)
        checks.append("C34 retained market-source manifest and response hashes")
        checks.append(validate_target_math())
        validate_c35(c35)
        checks.append("C35 source binding, action-card math, timing, protection, and research-only status")
        validate_markdown()
        checks.append("C34/C31/C35 Markdown mirrors")
        validate_forward_ledger_boundary()
        checks.append("six-month forward-paper gate remains incomplete and research-only")
    except (FileNotFoundError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"FAIL: C35 C34 operational action-card validation failed: {error}")
        return 1

    print("PASS: C35 C34 operational action card matches the frozen sources and remains research_only; no external action is authorized.")
    for check in checks:
        print(f"- {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
