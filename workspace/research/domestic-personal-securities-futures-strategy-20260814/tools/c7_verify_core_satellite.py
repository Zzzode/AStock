#!/usr/bin/env python3
"""Verify C7 rulebook, detailed product cards, and frozen price diagnostic.

This is a consistency control, not an investment, performance, suitability, or
execution approval.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RULEBOOK_JSON = CASE_DIR / "analysis" / f"c7_static_core_satellite_rulebook_{DATE_TAG}.json"
RULEBOOK_MD = CASE_DIR / "analysis" / f"c7_static_core_satellite_rulebook_{DATE_TAG}.md"
CARDS_JSON = CASE_DIR / "analysis" / f"c7_etf_product_cards_{DATE_TAG}.json"
CARDS_MD = CASE_DIR / "analysis" / f"c7_etf_product_cards_{DATE_TAG}.md"
DIAGNOSTIC_JSON = CASE_DIR / "analysis" / f"c7_static_core_satellite_price_diagnostic_{DATE_TAG}.json"
DIAGNOSTIC_MD = CASE_DIR / "analysis" / f"c7_static_core_satellite_price_diagnostic_{DATE_TAG}.md"
MANIFEST = CASE_DIR / "sources" / f"c7-static-etf-price-observation-{DATE_TAG}" / "manifest.json"
EXPECTED = {
    "510300": (0.30, 0.05),
    "510500": (0.10, 0.03),
    "510880": (0.10, 0.03),
    "511010": (0.30, 0.05),
    "511990": (0.10, 0.05),
    "518880": (0.10, 0.03),
}
FORBIDDEN = tuple(
    "".join(chr(codepoint) for codepoint in item)
    for item in (
        (26412, 37329),
        (21021, 22987, 36164, 37329),
        (21021, 22987, 37329, 39069),
        (105, 110, 105, 116, 105, 97, 108, 32, 99, 97, 112, 105, 116, 97, 108),
        (105, 110, 105, 116, 105, 97, 108, 95, 99, 97, 112, 105, 116, 97, 108),
        (112, 114, 105, 110, 99, 105, 112, 97, 108),
        (115, 116, 97, 114, 116, 105, 110, 103, 32, 97, 109, 111, 117, 110, 116),
    )
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key: {key}")
        result[key] = value
    return result


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    for path in (RULEBOOK_JSON, RULEBOOK_MD, CARDS_JSON, CARDS_MD, DIAGNOSTIC_JSON, DIAGNOSTIC_MD, MANIFEST):
        _require(path.is_file(), f"missing C7 artifact: {path.relative_to(CASE_DIR)}", failures)
    if failures:
        print("C7 CORE-SATELLITE: FAIL")
        print("\n".join(failures))
        return 1

    rulebook = _load(RULEBOOK_JSON)
    cards = _load(CARDS_JSON)
    diagnostic = _load(DIAGNOSTIC_JSON)
    manifest = _load(MANIFEST)

    _require(rulebook.get("artifact_id") == "DPSFS-C7-RULE-v1", "rulebook ID differs", failures)
    _require(rulebook.get("candidate_status") == "frozen_exploratory_candidate_not_action_ready", "rulebook status differs", failures)
    _require(rulebook.get("historical_protocol_status") == "exploratory_post_observation_not_clean_preregistration", "rulebook must disclose post-observation status", failures)
    _require(rulebook.get("constraints", {}).get("portfolio_q") == 0, "rulebook must retain q=0", failures)
    _require(rulebook.get("constraints", {}).get("no_external_orders") is True, "rulebook must prohibit external orders", failures)
    _require(
        rulebook.get("non_exclusion_boundary", {}).get("direct_a_shares", "").startswith("not excluded"),
        "rulebook must state direct A shares are not excluded",
        failures,
    )
    _require(
        rulebook.get("non_exclusion_boundary", {}).get("futures", "").startswith("not excluded"),
        "rulebook must state futures are not excluded",
        failures,
    )

    sleeves = rulebook.get("rule", {}).get("sleeves", [])
    weights = {row.get("code"): (row.get("target_weight"), row.get("weight_band_absolute")) for row in sleeves}
    _require(weights == EXPECTED, "rulebook code/weight/band matrix differs from C7 fixed definition", failures)
    _require(abs(sum(float(row.get("target_weight", 0.0)) for row in sleeves) - 1.0) < 1e-12, "rulebook weights do not sum to one", failures)
    calendar = rulebook.get("rule", {}).get("calendar", {})
    _require("March and September" in calendar.get("information_date", ""), "rulebook review calendar differs", failures)
    _require("next common trading session" in calendar.get("minimum_effective_date", ""), "rulebook next-session timing differs", failures)
    _require("exceeds" in calendar.get("rebalancing_trigger", ""), "rulebook band trigger differs", failures)
    order_controls = rulebook.get("rule", {}).get("order_controls", {})
    _require(order_controls.get("order_type") == "limit order only", "rulebook must retain limit-order control", failures)
    _require(order_controls.get("missing_quote_iopv_fee_or_status") == "no_action", "rulebook must retain no-action gate", failures)
    _require(rulebook.get("formal_test_and_disposition", {}).get("current_action") == "no_action", "rulebook current action differs", failures)

    _require(cards.get("artifact_id") == "DPSFS-C7-PRODUCT-CARDS-v1", "product-card ID differs", failures)
    card_codes = {row.get("code") for row in cards.get("products", [])}
    _require(card_codes == set(EXPECTED), "product cards do not cover all fixed sleeves", failures)
    for card in cards.get("products", []):
        source = REPO_ROOT / str(card.get("source", ""))
        _require(source.is_file(), f"product-card source absent: {card.get('code')}", failures)

    _require(diagnostic.get("portfolio_q") == 0, "diagnostic must retain q=0", failures)
    _require(diagnostic.get("formal_decision_eligible") is False, "diagnostic must retain formal-decision block", failures)
    _require(diagnostic.get("protocol_status") == "exploratory_post_observation_not_clean_preregistration", "diagnostic protocol status differs", failures)
    _require(diagnostic.get("interpretation", {}).get("historical_5pct_verdict") == "not_adjudicated", "diagnostic must not adjudicate 5%", failures)
    derived_sleeves = diagnostic.get("candidate_definition", {}).get("fixed_sleeves", [])
    derived_weights = {row.get("code"): (row.get("target_weight"), row.get("band_absolute_weight")) for row in derived_sleeves}
    _require(derived_weights == EXPECTED, "diagnostic code/weight/band matrix differs from rulebook", failures)
    arithmetic = diagnostic.get("arithmetic_output", {})
    _require(arithmetic.get("common_sessions") == 3171, "diagnostic common-session count differs", failures)
    _require(arithmetic.get("complete_calendar_year_summary", {}).get("below_5pct_count") == 5, "diagnostic complete-year count differs", failures)
    _require(arithmetic.get("rolling_five_year", {}).get("below_5pct_count") == 1428, "diagnostic rolling-window count differs", failures)

    files = manifest.get("files", [])
    file_codes = {row.get("code") for row in files}
    _require(file_codes == set(EXPECTED), "source manifest does not cover six sleeves", failures)
    _require(manifest.get("protocol_status") == "exploratory_post_observation_not_clean_preregistration", "source manifest protocol status differs", failures)
    frozen = {row.get("path"): row for row in manifest.get("source_freeze", {}).get("frozen_files", [])}
    for item in files:
        path = REPO_ROOT / str(item.get("path", ""))
        _require(path.is_file(), f"raw C7 price file absent: {item.get('code')}", failures)
        if path.is_file():
            _require(path.stat().st_size == item.get("bytes"), f"raw C7 price size mismatch: {item.get('code')}", failures)
            _require(_sha256(path) == item.get("sha256"), f"raw C7 price hash mismatch: {item.get('code')}", failures)
        freeze_entry = frozen.get(item.get("path"))
        _require(
            isinstance(freeze_entry, dict) and all(freeze_entry.get(key) == item.get(key) for key in ("path", "bytes", "sha256")),
            f"raw C7 price freeze mismatch: {item.get('code')}",
            failures,
        )

    for path in (RULEBOOK_JSON, RULEBOOK_MD, CARDS_JSON, CARDS_MD, DIAGNOSTIC_JSON, DIAGNOSTIC_MD):
        lowered = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN:
            _require(term.lower() not in lowered, f"forbidden monetary-scope term {term!r} in {path.name}", failures)

    if failures:
        print("C7 CORE-SATELLITE: FAIL")
        print("\n".join(failures))
        return 1
    print("C7 CORE-SATELLITE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
