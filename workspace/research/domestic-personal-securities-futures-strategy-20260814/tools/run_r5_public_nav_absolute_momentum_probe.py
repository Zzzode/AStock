#!/usr/bin/env python3
"""Run the single, fixed R5 public accumulated-NAV proxy test.

This is deliberately a case-local research probe, not a portfolio backtest.
It freezes every public API response used by the calculation and reports only
whether a narrow, explicit proxy arithmetic is falsified by its own historical
screen.  Public accumulated NAV is neither a point-in-time, entitled total
return record nor an executable exchange-market price.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "probe-r5-public-etf-nav-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
MANIFEST_MD_PATH = SOURCE_DIR / "manifest.md"
OUTPUT_PATH = CASE_DIR / "analysis" / "r5_public_nav_absolute_momentum_probe_20260815.json"
OUTPUT_MD_PATH = CASE_DIR / "analysis" / "r5_public_nav_absolute_momentum_probe_20260815.md"
PROTOCOL_PATH = CASE_DIR / "analysis" / "r5_predeclared_public_nav_feasibility_protocol_20260815.json"

ENDPOINT = "https://api.fund.eastmoney.com/f10/lsjz"
REFERER_TEMPLATE = "https://fundf10.eastmoney.com/jjjz_{code}.html"
START_DATE = "2010-01-01"
END_DATE = "2026-08-14"
PAGE_SIZE = 20
LOOKBACK = 252
ROLLING_INTERVALS = 1_260
COST_BPS = 20.0
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
RAW_BUNDLE_SCHEMA = "r5_public_fund_nav_raw_page_bundle.v1"
OUTPUT_SCHEMA = "r5_public_nav_absolute_momentum_probe.v1"

CODES = ("510300", "510880", "511010", "511990", "518880")
RISK_CODES = ("510300", "510880", "511010", "518880")
FALLBACK_CODE = "511990"
EQUITY_SIGNAL_SLEEVE_CONVENTION = (
    "fixed_base_buy_and_hold_equal_weighted_level; "
    "selected-equity targets reset to 50/50 only at strategy rebalances"
)


# This is intentionally duplicated from the protocol and then checked before
# every derivation.  It turns the human-readable protocol into a machine-bound
# contract for the fixed exploratory arithmetic; any substantive mismatch
# fails closed instead of silently producing a new variant.
IMPLEMENTATION_BINDING = {
    "equity_sleeve": {"codes": ["510300", "510880"], "within_sleeve_weights": [0.5, 0.5]},
    "bond_sleeve": {"codes": ["511010"], "within_sleeve_weights": [1.0]},
    "gold_sleeve": {"codes": ["518880"], "within_sleeve_weights": [1.0]},
    "fallback_money_market": {"codes": ["511990"], "within_sleeve_weights": [1.0]},
    "rule": {
        "lookback_common_observations": LOOKBACK,
        "signal_timing": "last common observation of calendar month",
        "effective_timing": "next common observation after signal",
        "equity_signal_sleeve_convention": EQUITY_SIGNAL_SLEEVE_CONVENTION,
        "eligible_rule": "absolute_momentum > 0",
        "target_weight_rule": "equal weight across all eligible sleeves; if none is eligible, 100% fallback_money_market",
        "relative_ranking": "prohibited",
        "top_n_selection": "prohibited",
        "parameter_variants": "prohibited",
        "leverage_or_derivatives": "prohibited",
    },
    "accounting": {
        "unit_nav_start": 1.0,
        "pre_trade_drift": True,
        "one_way_turnover": "0.5 * sum(abs(drifted_weight - target_weight))",
        "fixed_cost_bps_one_way": COST_BPS,
        "same_day_signal_and_return": "prohibited",
    },
    "evaluation": {
        "rolling_five_year_observation_intervals": ROLLING_INTERVALS,
        "strict_hurdle": 0.05,
        "terminal_calendar_year_rule": "terminal calendar year is eligible only when the final common observation is on calendar December 31",
        "terminal_rolling_month_rule": "terminal month is eligible only when the final common observation is on its calendar month end",
    },
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _write_text(path, _canonical_json(payload))


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_path(path),
    }


def _bundle_path(code: str) -> Path:
    return SOURCE_DIR / f"eastmoney_fund_nav_{code}_pages.json"


def _runtime_provenance() -> dict[str, str]:
    return {
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256_path(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "pandas_version": pd.__version__,
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
        "adapter": "direct anonymous HTTPS requests to Eastmoney public fund history endpoint",
    }


def _request_params(code: str, page_index: int) -> dict[str, str]:
    # The nonce is a cache-control hint only.  It is retained with the raw
    # response, so the frozen source remains auditable even though it changes.
    return {
        "fundCode": code,
        "pageIndex": str(page_index),
        "pageSize": str(PAGE_SIZE),
        "startDate": START_DATE,
        "endDate": END_DATE,
        "_": str(round(time.time() * 1000)),
    }


def _validate_response(raw_text: str, code: str, page_index: int) -> dict[str, Any]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"{code} page {page_index}: response is not JSON") from error
    data = payload.get("Data")
    total = payload.get("TotalCount")
    if not isinstance(data, dict) or not isinstance(data.get("LSJZList"), list):
        raise ValueError(f"{code} page {page_index}: response has no LSJZList")
    if not isinstance(total, int) or total <= 0:
        raise ValueError(f"{code} page {page_index}: invalid TotalCount {total!r}")
    return payload


def _fetch_bundle(code: str) -> dict[str, Any]:
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (research-only public source capture)",
        "Referer": REFERER_TEMPLATE.format(code=code),
        "Accept": "application/json, text/plain, */*",
    }
    pages: list[dict[str, Any]] = []
    expected_pages: int | None = None
    expected_total: int | None = None
    for page_index in range(1, 10_000):
        params = _request_params(code, page_index)
        response = session.get(ENDPOINT, params=params, headers=headers, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(f"{code} page {page_index}: HTTP {response.status_code}")
        raw_text = response.text
        payload = _validate_response(raw_text, code, page_index)
        total = int(payload["TotalCount"])
        if expected_total is None:
            expected_total = total
            expected_pages = math.ceil(total / PAGE_SIZE)
        elif total != expected_total:
            raise ValueError(f"{code}: TotalCount changed during capture ({expected_total} -> {total})")
        assert expected_pages is not None
        pages.append(
            {
                "page_index": page_index,
                "request_params": params,
                "response_url": response.url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "http_status": response.status_code,
                "raw_response_utf8": raw_text,
                "raw_response_sha256": _sha256_bytes(raw_text.encode("utf-8")),
            }
        )
        if page_index >= expected_pages:
            break
        time.sleep(0.03)
    if expected_pages is None or len(pages) != expected_pages:
        raise ValueError(f"{code}: incomplete page capture")
    bundle = {
        "schema_version": RAW_BUNDLE_SCHEMA,
        "fund_code": code,
        "endpoint": ENDPOINT,
        "referer": REFERER_TEMPLATE.format(code=code),
        "capture_window": {"start_date": START_DATE, "end_date": END_DATE},
        "page_size_requested": PAGE_SIZE,
        "page_count": expected_pages,
        "total_rows_reported": expected_total,
        "pages": pages,
    }
    _validate_bundle(bundle)
    return bundle


def _validate_bundle(bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    if bundle.get("schema_version") != RAW_BUNDLE_SCHEMA:
        raise ValueError("unexpected raw bundle schema")
    code = str(bundle.get("fund_code") or "")
    if code not in CODES:
        raise ValueError(f"unexpected code in raw bundle: {code!r}")
    pages = bundle.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError(f"{code}: pages missing")
    expected_pages = int(bundle.get("page_count") or 0)
    expected_total = int(bundle.get("total_rows_reported") or 0)
    if expected_pages != len(pages) or expected_total <= 0:
        raise ValueError(f"{code}: raw bundle count mismatch")
    rows: list[dict[str, Any]] = []
    for expected_index, page in enumerate(pages, start=1):
        if not isinstance(page, Mapping) or int(page.get("page_index") or 0) != expected_index:
            raise ValueError(f"{code}: page ordering mismatch")
        raw_text = page.get("raw_response_utf8")
        if not isinstance(raw_text, str):
            raise ValueError(f"{code} page {expected_index}: raw response absent")
        if _sha256_bytes(raw_text.encode("utf-8")) != page.get("raw_response_sha256"):
            raise ValueError(f"{code} page {expected_index}: raw response digest mismatch")
        payload = _validate_response(raw_text, code, expected_index)
        if int(payload["TotalCount"]) != expected_total:
            raise ValueError(f"{code} page {expected_index}: TotalCount mismatch")
        page_rows = payload["Data"]["LSJZList"]
        if not isinstance(page_rows, list):
            raise ValueError(f"{code} page {expected_index}: row list absent")
        rows.extend(page_rows)
    if len(rows) != expected_total:
        raise ValueError(f"{code}: captured rows {len(rows)} != reported {expected_total}")
    dates = [str(item.get("FSRQ") or "") for item in rows if isinstance(item, Mapping)]
    if len(dates) != len(rows) or len(set(dates)) != len(dates) or any(not value for value in dates):
        raise ValueError(f"{code}: date keys are missing or duplicated")
    return [dict(item) for item in rows]


def _read_bundle(code: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path = _bundle_path(code)
    if not path.is_file():
        raise FileNotFoundError(f"raw bundle not found: {path}")
    bundle = json.loads(path.read_text(encoding="utf-8"))
    rows = _validate_bundle(bundle)
    return bundle, rows


def _source_entry(code: str, bundle: Mapping[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    path = _bundle_path(code)
    date_values = sorted(str(row["FSRQ"]) for row in rows)
    return {
        **_file_record(path),
        "publisher": "Eastmoney public fund-history endpoint",
        "title": f"Public historical accumulated-NAV responses for {code}",
        "url": ENDPOINT,
        "referer": REFERER_TEMPLATE.format(code=code),
        "retrieved_at": min(str(page["retrieved_at"]) for page in bundle["pages"]),
        "source_displayed_date_range": {"first": date_values[0], "last": date_values[-1]},
        "response_page_count": int(bundle["page_count"]),
        "response_rows": len(rows),
        "capture_note": "Retrospectively captured public aggregate responses. The archive preserves exact response strings and request metadata but does not establish original-date availability, revisions, field semantics, data rights, complete total return or executable prices.",
    }


def _make_manifest(entries: list[dict[str, Any]]) -> dict[str, Any]:
    captured_at = min(str(entry["retrieved_at"]) for entry in entries)
    frozen_files = [
        {key: entry[key] for key in ("path", "bytes", "sha256")}
        for entry in entries
    ]
    return {
        "capture_batch": SOURCE_DIR.name,
        "captured_at": captured_at,
        "purpose": "Single-run R5 public accumulated-NAV proxy input. It is retained solely for a fixed exploratory research arithmetic and cannot establish total return, investor performance, product admission, allocation, holding, execution or action.",
        "source_quality": "tier_3_public_aggregated_retrospective_nav_proxy",
        "files": entries,
        "limitations": [
            "Rows were retrieved retrospectively. They do not prove original-date availability, revisions, field semantics, user rights, or complete historical coverage.",
            "Displayed accumulated NAV is not an exchange-market fill. The source does not establish price/NAV/IOPV, distributions and other events, halts, limits, lot size, bid/ask, capacity, fees, taxes, settlement or suitability.",
            "The archive is a case-local hash control. It is not external notarization, a data licence or a point-in-time total-return ledger.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "captured_and_sealed_once",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": frozen_files,
            "runtime_provenance": _runtime_provenance(),
            "boundary": "Case-local hash control only; it detects mismatched retained files and does not establish entitlement, PIT availability, total return or execution quality.",
        },
    }


def _manifest_markdown(manifest: Mapping[str, Any]) -> str:
    rows = "\n".join(
        "| {code} | {pages} | {rows} | {first} | {last} | `{sha}` |".format(
            code=Path(str(entry["path"])).stem.split("_")[3],
            pages=entry["response_page_count"],
            rows=entry["response_rows"],
            first=entry["source_displayed_date_range"]["first"],
            last=entry["source_displayed_date_range"]["last"],
            sha=entry["sha256"],
        )
        for entry in manifest["files"]
    )
    return f"""# R5 Public Accumulated-NAV Source Manifest

- Capture batch: `{manifest['capture_batch']}`
- First response time: `{manifest['captured_at']}`
- Method: anonymous, read-only HTTPS retrieval of the public Eastmoney
  fund-history endpoint. No credential, purchase, account, bypass or trading
  action was used.
- Boundary: every retained file embeds exact response strings plus query
  metadata. The archive is retrospective and does not establish historical
  availability, revision lineage, field semantics, total return, executable
  market price, data rights or a strategy result.

| Code | Pages | Rows | First displayed date | Last displayed date | Bundle SHA-256 |
|---|---:|---:|---|---|---|
{rows}

The source is permitted only for the one R5 public-NAV proxy arithmetic under
`DPSFS-R5-PNAV-v1`. It cannot approve a product, allocation, holding or action.
"""


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"source manifest not found: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    freeze = manifest.get("source_freeze")
    if not isinstance(freeze, Mapping) or freeze.get("schema_version") != SOURCE_FREEZE_SCHEMA:
        raise ValueError("source manifest has no valid freeze control")
    files = manifest.get("files")
    frozen_files = freeze.get("frozen_files")
    if not isinstance(files, list) or not isinstance(frozen_files, list) or len(files) != len(CODES):
        raise ValueError("source manifest has an invalid file count")
    manifest_by_path = {item.get("path"): item for item in files if isinstance(item, Mapping)}
    freeze_by_path = {item.get("path"): item for item in frozen_files if isinstance(item, Mapping)}
    expected = {_repo_relative(_bundle_path(code)) for code in CODES}
    if set(manifest_by_path) != expected or set(freeze_by_path) != expected:
        raise ValueError("source manifest has unexpected bundle paths")
    for code in CODES:
        path = _bundle_path(code)
        entry = manifest_by_path[_repo_relative(path)]
        frozen = freeze_by_path[_repo_relative(path)]
        actual = _file_record(path)
        if any(actual[key] != entry.get(key) for key in actual):
            raise ValueError(f"{code}: retained bundle differs from manifest")
        if any(actual[key] != frozen.get(key) for key in actual):
            raise ValueError(f"{code}: retained bundle differs from freeze control")
        _read_bundle(code)
    capture_provenance = manifest.get("capture_implementation_provenance")
    if not isinstance(capture_provenance, Mapping):
        raise ValueError("source manifest lacks capture-implementation provenance disclosure")
    if capture_provenance.get("status") != "capture_script_version_not_retained":
        raise ValueError("source manifest has an unexpected capture-implementation provenance status")
    return manifest


def _load_and_validate_protocol() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(f"R5 protocol not found: {PROTOCOL_PATH}")
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol.get("artifact_id") != "DPSFS-R5-PNAV-v1":
        raise ValueError("R5 protocol identity differs from required protocol")
    if protocol.get("status") != "exploratory_post_observation_not_a_clean_preregistration":
        raise ValueError("R5 protocol status is not the required exploratory status")
    if protocol.get("implementation_binding") != IMPLEMENTATION_BINDING:
        raise ValueError("R5 protocol does not carry the required implementation binding")
    universe = protocol.get("fixed_implementation_universe")
    rule = protocol.get("rule")
    accounting = protocol.get("accounting")
    evaluation = protocol.get("evaluation")
    if not all(isinstance(value, Mapping) for value in (universe, rule, accounting, evaluation)):
        raise ValueError("R5 protocol has no valid machine-binding sections")
    actual = {
        "equity_sleeve": universe.get("equity_sleeve"),
        "bond_sleeve": universe.get("bond_sleeve"),
        "gold_sleeve": universe.get("gold_sleeve"),
        "fallback_money_market": universe.get("fallback_money_market"),
        "rule": {key: rule.get(key) for key in IMPLEMENTATION_BINDING["rule"]},
        "accounting": {key: accounting.get(key) for key in IMPLEMENTATION_BINDING["accounting"]},
        "evaluation": {key: evaluation.get(key) for key in IMPLEMENTATION_BINDING["evaluation"]},
    }
    if actual != IMPLEMENTATION_BINDING:
        raise ValueError("R5 protocol parameters differ from the fixed implementation binding")
    return protocol


def _series_from_rows(code: str, rows: list[dict[str, Any]]) -> pd.Series:
    if not rows:
        raise ValueError(f"{code}: source response has no rows")
    frame = pd.DataFrame(rows)
    if "FSRQ" not in frame.columns or "LJJZ" not in frame.columns:
        raise ValueError(f"{code}: source response lacks FSRQ/LJJZ")
    frame["date"] = pd.to_datetime(frame["FSRQ"], errors="coerce")
    frame["accumulated_nav"] = pd.to_numeric(frame["LJJZ"], errors="coerce")
    if frame["date"].isna().any() or frame["accumulated_nav"].isna().any():
        raise ValueError(f"{code}: malformed FSRQ/LJJZ source row")
    frame = frame.loc[:, ["date", "accumulated_nav"]].sort_values("date", kind="stable")
    if frame["date"].duplicated().any() or (frame["accumulated_nav"] <= 0).any():
        raise ValueError(f"{code}: invalid displayed accumulated-NAV observations")
    series = frame.set_index("date")["accumulated_nav"].rename(code)
    return series


def _equity_signal_sleeve_level(panel: pd.DataFrame) -> pd.Series:
    """Return the fixed-base, equal-weighted buy-and-hold equity signal level.

    This function is deliberately distinct from the selected equity target,
    which resets constituent weights to 50/50 when the overall strategy
    rebalances.  The difference is part of the fixed R5 rule rather than an
    implicit implementation detail.
    """
    base = panel.iloc[0]
    return 0.5 * (panel["510300"] / base["510300"]) + 0.5 * (
        panel["510880"] / base["510880"]
    )


def _run_implementation_self_tests() -> dict[str, str]:
    """Fail closed if the documented fixed-base signal convention drifts."""
    fixture = pd.DataFrame(
        {
            "510300": [1.0, 2.0, 4.0],
            "510880": [1.0, 0.5, 0.25],
        },
        # Jan 31 -> Feb 1 crosses a monthly signal boundary.  A mistaken
        # monthly reset would produce 1.25 on Feb 2 instead of 2.125.
        index=pd.to_datetime(["2000-01-31", "2000-02-01", "2000-02-02"]),
    )
    levels = _equity_signal_sleeve_level(fixture)
    expected = (1.0, 1.25, 2.125)
    observed = tuple(float(value) for value in levels)
    if any(not math.isclose(value, target, rel_tol=0.0, abs_tol=1e-12) for value, target in zip(observed, expected)):
        raise AssertionError("fixed-base equity signal sleeve convention self-test failed")
    prohibited_periodic_levels = (1.5625, 1.25)
    if any(math.isclose(observed[-1], value, rel_tol=0.0, abs_tol=1e-12) for value in prohibited_periodic_levels):
        raise AssertionError("equity signal sleeve unexpectedly became a daily or monthly reset index")

    target_fixture = pd.DataFrame(
        {
            "510300": np.linspace(1.0, 2.0, LOOKBACK + 1),
            "510880": np.linspace(1.0, 1.2, LOOKBACK + 1),
            "511010": np.linspace(1.0, 0.9, LOOKBACK + 1),
            "511990": np.ones(LOOKBACK + 1),
            "518880": np.linspace(1.0, 0.9, LOOKBACK + 1),
        },
        index=pd.date_range("2000-01-03", periods=LOOKBACK + 1, freq="B"),
    )
    target, _, active = _target_weights(target_fixture, LOOKBACK)
    drifted_equity_weights = {"510300": 0.7, "510880": 0.3}
    if active != ["equity"]:
        raise AssertionError("equity target-reset fixture has unexpected eligible sleeves")
    if not (math.isclose(target["510300"], 0.5, abs_tol=1e-12) and math.isclose(target["510880"], 0.5, abs_tol=1e-12)):
        raise AssertionError("selected equity sleeve does not reset constituent targets to 50/50")
    if all(math.isclose(target[code], drifted_equity_weights[code], abs_tol=1e-12) for code in drifted_equity_weights):
        raise AssertionError("selected equity sleeve target unexpectedly preserves drifted constituent weights")

    integration_index = pd.date_range("2000-01-03", periods=310, freq="B")
    integration_steps = np.arange(len(integration_index), dtype=float)
    integration_panel = pd.DataFrame(
        {
            "510300": np.exp(0.010 * integration_steps),
            "510880": np.exp(0.001 * integration_steps),
            "511010": np.exp(-0.001 * integration_steps),
            "511990": np.ones(len(integration_index)),
            "518880": np.exp(-0.0015 * integration_steps),
        },
        index=integration_index,
    )
    integration_curve, integration_rebalances, _ = _simulate(integration_panel)
    equity_rebalances = [
        item for item in integration_rebalances if item["eligible_sleeves"] == ["equity"]
    ]
    if len(equity_rebalances) < 2:
        raise AssertionError("integration fixture did not produce two equity-only rebalances")
    reset_rebalance = equity_rebalances[1]
    pre_trade = reset_rebalance["drifted_weights_before_trade"]
    target_after_trade = reset_rebalance["target_weights"]
    if math.isclose(pre_trade["510300"], pre_trade["510880"], abs_tol=1e-8):
        raise AssertionError("integration fixture did not generate unequal pre-trade equity drift")
    if not (
        math.isclose(target_after_trade["510300"], 0.5, abs_tol=1e-12)
        and math.isclose(target_after_trade["510880"], 0.5, abs_tol=1e-12)
    ):
        raise AssertionError("integration fixture did not set a 50/50 equity target")
    effective_date = pd.Timestamp(reset_rebalance["effective_date"])
    effective_position = integration_panel.index.get_loc(effective_date)
    price_ratio = integration_panel.iloc[effective_position] / integration_panel.iloc[effective_position - 1]
    expected_gross = 0.5 * float(price_ratio["510300"]) + 0.5 * float(price_ratio["510880"])
    observed_weight_510300 = float(integration_curve.loc[effective_date, "weight_510300"])
    observed_weight_510880 = float(integration_curve.loc[effective_date, "weight_510880"])
    if not math.isclose(observed_weight_510300, 0.5 * float(price_ratio["510300"]) / expected_gross, abs_tol=1e-12):
        raise AssertionError("integration fixture did not apply the reset target before the effective-date return")
    if not math.isclose(observed_weight_510880, 0.5 * float(price_ratio["510880"]) / expected_gross, abs_tol=1e-12):
        raise AssertionError("integration fixture did not apply the 50/50 reset target before the effective-date return")
    return {
        "equity_signal_sleeve_fixed_base_across_month_end_fixture": "PASS",
        "equity_selected_target_reset_fixture": "PASS",
        "equity_selected_target_reset_integration_fixture": "PASS",
    }


def _target_weights(panel: pd.DataFrame, index: int) -> tuple[dict[str, float], dict[str, float], list[str]]:
    equity = _equity_signal_sleeve_level(panel)
    values = {
        "equity": float(equity.iloc[index] / equity.iloc[index - LOOKBACK] - 1.0),
        "bond": float(panel["511010"].iloc[index] / panel["511010"].iloc[index - LOOKBACK] - 1.0),
        "gold": float(panel["518880"].iloc[index] / panel["518880"].iloc[index - LOOKBACK] - 1.0),
    }
    active = [name for name in ("equity", "bond", "gold") if values[name] > 0.0]
    target = {code: 0.0 for code in CODES}
    if not active:
        target[FALLBACK_CODE] = 1.0
    else:
        sleeve_weight = 1.0 / len(active)
        if "equity" in active:
            target["510300"] = 0.5 * sleeve_weight
            target["510880"] = 0.5 * sleeve_weight
        if "bond" in active:
            target["511010"] = sleeve_weight
        if "gold" in active:
            target["518880"] = sleeve_weight
    if not np.isclose(sum(target.values()), 1.0, atol=1e-12):
        raise ValueError("target weights do not sum to one")
    return target, values, active


def _simulate(panel: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    if panel.shape[0] <= LOOKBACK + 1:
        raise ValueError("common panel is too short for the fixed lookback")
    month_end = pd.Series(panel.index, index=panel.index).groupby(panel.index.to_period("M")).tail(1).index
    month_end_positions = {panel.index.get_loc(date) for date in month_end}
    first_signal = next((pos for pos in sorted(month_end_positions) if pos >= LOOKBACK and pos + 1 < len(panel)), None)
    if first_signal is None:
        raise ValueError("no eligible month-end signal after fixed lookback")
    pending: dict[int, tuple[dict[str, float], dict[str, float], list[str], int]] = {}
    first_target, first_momentum, first_active = _target_weights(panel, first_signal)
    pending[first_signal + 1] = (first_target, first_momentum, first_active, first_signal)
    weights = {code: 0.0 for code in CODES}
    weights[FALLBACK_CODE] = 1.0
    nav = 1.0
    daily_rows: list[dict[str, Any]] = []
    rebalances: list[dict[str, Any]] = []
    for index in range(first_signal + 1, len(panel)):
        date = panel.index[index]
        if index in pending:
            target, momentum, active, signal_index = pending.pop(index)
            turnover = 0.5 * sum(abs(weights[code] - target[code]) for code in CODES)
            cost_fraction = turnover * COST_BPS / 10_000.0
            nav_before_cost = nav
            nav *= 1.0 - cost_fraction
            rebalances.append(
                {
                    "signal_date": panel.index[signal_index].date().isoformat(),
                    "effective_date": date.date().isoformat(),
                    "eligible_sleeves": active,
                    "sleeve_absolute_momentum": {key: round(value, 10) for key, value in momentum.items()},
                    "drifted_weights_before_trade": {key: round(value, 10) for key, value in weights.items()},
                    "target_weights": {key: round(value, 10) for key, value in target.items()},
                    "one_way_turnover": round(turnover, 10),
                    "cost_fraction": round(cost_fraction, 10),
                    "unit_nav_before_cost": round(nav_before_cost, 10),
                    "unit_nav_after_cost": round(nav, 10),
                }
            )
            weights = target
        ratio = panel.iloc[index] / panel.iloc[index - 1]
        if ratio.isna().any() or (ratio <= 0.0).any():
            raise ValueError(f"invalid common NAV ratio on {date.date().isoformat()}")
        gross = sum(weights[code] * float(ratio[code]) for code in CODES)
        if gross <= 0.0:
            raise ValueError(f"nonpositive portfolio gross return on {date.date().isoformat()}")
        nav *= gross
        weights = {code: weights[code] * float(ratio[code]) / gross for code in CODES}
        daily_rows.append(
            {
                "date": date.date().isoformat(),
                "unit_nav": nav,
                **{f"weight_{code}": weights[code] for code in CODES},
            }
        )
        if index in month_end_positions and index >= LOOKBACK and index + 1 < len(panel):
            target, momentum, active = _target_weights(panel, index)
            pending[index + 1] = (target, momentum, active, index)
    if pending:
        raise ValueError("unapplied target remains after simulation")
    result = pd.DataFrame(daily_rows)
    result["date"] = pd.to_datetime(result["date"])
    result = result.set_index("date")
    metadata = {
        "first_signal_date": panel.index[first_signal].date().isoformat(),
        "first_effective_date": panel.index[first_signal + 1].date().isoformat(),
        "last_rebalance_effective_date": rebalances[-1]["effective_date"],
        "terminal_panel_observation_date": panel.index[-1].date().isoformat(),
        "common_panel_start": panel.index[0].date().isoformat(),
        "common_panel_end": panel.index[-1].date().isoformat(),
    }
    return result, rebalances, metadata


def _complete_calendar_years(curve: pd.DataFrame, panel: pd.DataFrame) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    common_by_year = {year: group.index for year, group in panel.groupby(panel.index.year)}
    curve_by_year = {year: group.index for year, group in curve.groupby(curve.index.year)}
    terminal_year_is_calendar_complete = (
        panel.index[-1].month == 12 and panel.index[-1].day == 31
    )
    for year in sorted(set(common_by_year).intersection(curve_by_year)):
        common_dates = common_by_year[year]
        curve_dates = curve_by_year[year]
        prior_dates = curve.index[curve.index < common_dates[0]]
        complete = (
            (year < panel.index[-1].year or (year == panel.index[-1].year and terminal_year_is_calendar_complete))
            and common_dates[0].month == 1
            and common_dates[-1].month == 12
            and curve_dates[0] == common_dates[0]
            and curve_dates[-1] == common_dates[-1]
            and len(prior_dates) > 0
        )
        if complete:
            start_nav = float(curve.loc[prior_dates[-1], "unit_nav"])
            end_nav = float(curve.loc[curve_dates[-1], "unit_nav"])
            net_change: float | None = end_nav / start_nav - 1.0
        else:
            net_change = None
        output.append(
            {
                "year": int(year),
                "complete": bool(complete),
                "net_unitized_change": None if net_change is None else round(net_change, 10),
                "strict_hurdle_pass": None if net_change is None else bool(net_change >= 0.05),
            }
        )
    return output


def _rolling_five_years(curve: pd.DataFrame, panel: pd.DataFrame) -> list[dict[str, Any]]:
    curve_positions = {date: pos for pos, date in enumerate(panel.index)}
    month_end_dates = pd.Series(curve.index, index=curve.index).groupby(curve.index.to_period("M")).tail(1).index
    terminal_month = panel.index[-1].to_period("M")
    terminal_is_calendar_month_end = panel.index[-1] == (panel.index[-1] + pd.offsets.MonthEnd(0))
    output: list[dict[str, Any]] = []
    for end_date in month_end_dates:
        if end_date.to_period("M") == terminal_month and not terminal_is_calendar_month_end:
            # The archive ends during this calendar month.  Its last displayed
            # row is not a complete month-end assessment point.
            continue
        end_position = curve_positions.get(end_date)
        if end_position is None or end_position - ROLLING_INTERVALS < 0:
            continue
        start_date = panel.index[end_position - ROLLING_INTERVALS]
        if start_date not in curve.index:
            continue
        start_nav = float(curve.loc[start_date, "unit_nav"])
        end_nav = float(curve.loc[end_date, "unit_nav"])
        annualized = (end_nav / start_nav) ** (LOOKBACK / ROLLING_INTERVALS) - 1.0
        output.append(
            {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "observation_intervals": ROLLING_INTERVALS,
                "annualized_net_unitized_change": round(float(annualized), 10),
                "strict_hurdle_pass": bool(annualized >= 0.05),
            }
        )
    return output


def _metrics(curve: pd.DataFrame) -> dict[str, Any]:
    nav = curve["unit_nav"]
    periods = len(nav)
    annualized = float(nav.iloc[-1] ** (LOOKBACK / periods) - 1.0)
    drawdown = nav / nav.cummax() - 1.0
    return {
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "observation_intervals": int(periods),
        "final_unit_nav": round(float(nav.iloc[-1]), 10),
        "annualized_net_unitized_change": round(annualized, 10),
        "max_drawdown": round(float(drawdown.min()), 10),
    }


def _coverage(panel: pd.DataFrame, source_lengths: Mapping[str, int]) -> dict[str, Any]:
    return {
        "source_rows_by_code": {code: int(source_lengths[code]) for code in CODES},
        "common_positive_nav_observations": int(len(panel)),
        "common_start": panel.index[0].date().isoformat(),
        "common_end": panel.index[-1].date().isoformat(),
        "excluded_rows_by_code_after_common_intersection": {
            code: int(source_lengths[code] - len(panel)) for code in CODES
        },
        "exception_policy": "Any missing/nonpositive/duplicate source value causes a source failure; the calculation has no secondary-source replacement path.",
    }


def _derive() -> dict[str, Any]:
    manifest = _load_manifest()
    protocol = _load_and_validate_protocol()
    self_tests = _run_implementation_self_tests()
    series: dict[str, pd.Series] = {}
    lengths: dict[str, int] = {}
    for code in CODES:
        _, rows = _read_bundle(code)
        series[code] = _series_from_rows(code, rows)
        lengths[code] = len(series[code])
    panel = pd.concat(series, axis=1, join="inner").sort_index(kind="stable")
    if panel.index.duplicated().any() or panel.empty or (panel <= 0.0).any().any():
        raise ValueError("invalid common accumulated-NAV panel")
    curve, rebalances, simulation_metadata = _simulate(panel)
    annual_years = _complete_calendar_years(curve, panel)
    rolling = _rolling_five_years(curve, panel)
    complete_annual = [item for item in annual_years if item["complete"]]
    failures: list[str] = []
    if not complete_annual:
        failures.append("No complete calendar-year metric is available after the fixed signal warmup.")
    if not rolling:
        failures.append("No 1,260-observation rolling-five-year endpoint is available after the fixed signal warmup.")
    if any(item["strict_hurdle_pass"] is False for item in complete_annual):
        failures.append("At least one complete calendar-year proxy metric is below the fixed 5% hurdle.")
    if any(item["strict_hurdle_pass"] is False for item in rolling):
        failures.append("At least one rolling-five-year proxy endpoint is below the fixed 5% hurdle.")
    state = "PUBLIC_NAV_PROXY_HURDLE_NOT_FALSIFIED" if not failures else "PUBLIC_NAV_PROXY_HURDLE_FALSIFIED"
    return {
        "schema_version": OUTPUT_SCHEMA,
        "artifact_id": "DPSFS-R5-PNAV-RESULT-v1",
        "as_of": "2026-08-15",
        "artifact_class": "derived_public_nav_proxy_research_observation",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "derived_runtime_provenance": _runtime_provenance(),
        "protocol": {
            "path": _repo_relative(PROTOCOL_PATH),
            "sha256": _sha256_path(PROTOCOL_PATH),
            "artifact_id": protocol["artifact_id"],
            "status": protocol["status"],
            "pre_observation_disclosure": protocol.get("pre_observation_disclosure"),
        },
        "source": {
            "manifest_path": _repo_relative(MANIFEST_PATH),
            "manifest_sha256": _sha256_path(MANIFEST_PATH),
            "source_quality": manifest["source_quality"],
            "source_registry_id": "P08",
            "capture_implementation_provenance": manifest["capture_implementation_provenance"],
        },
        "data_quality": "retrospectively_captured_public_accumulated_nav_proxy_not_pit_not_executable",
        "coverage": _coverage(panel, lengths),
        "simulation": {
            **simulation_metadata,
            "unit_nav_start": 1.0,
            "lookback_common_observations": LOOKBACK,
            "rolling_five_year_observation_intervals": ROLLING_INTERVALS,
            "fixed_one_way_cost_bps": COST_BPS,
            "cost_boundary": "Illustrative load only; not an execution, fee, tax, spread, impact, fill, settlement or capacity assertion.",
            "strategy_rule": "Monthly absolute momentum across one locked equity sleeve, one government-bond sleeve and one gold sleeve; equal weight among positive sleeves; locked money-market ETF fallback only when none is positive.",
            "implementation_binding": IMPLEMENTATION_BINDING,
            "implementation_self_tests": self_tests,
            "terminal_observation_policy": {
                "calendar_year_terminal_complete": bool(panel.index[-1].month == 12 and panel.index[-1].day == 31),
                "calendar_month_terminal_complete": bool(panel.index[-1] == (panel.index[-1] + pd.offsets.MonthEnd(0))),
                "boundary": "A terminal period is assessed only when the final common observation reaches the relevant calendar end; otherwise it is excluded as incomplete.",
            },
        },
        "full_period_metrics": _metrics(curve),
        "complete_calendar_years": annual_years,
        "rolling_five_year_endpoints": rolling,
        "rebalances": rebalances,
        "turnover_and_cost_summary": {
            "rebalance_events": len(rebalances),
            "zero_turnover_events": sum(float(item["one_way_turnover"]) == 0.0 for item in rebalances),
            "total_one_way_turnover": round(sum(float(item["one_way_turnover"]) for item in rebalances), 10),
            "sum_simple_cost_fractions": round(sum(float(item["cost_fraction"]) for item in rebalances), 10),
            "interpretation": "The cost sum is the arithmetic sum of per-rebalance illustrative fractions; it is not a compounded-return drag or an execution-cost estimate.",
        },
        "strict_proxy_hurdle": {
            "threshold": 0.05,
            "state": state,
            "failures": failures,
            "boundary": "The state is only a result of the stated public-NAV proxy arithmetic. It is not an investor-return result, guarantee, forecast, recommendation or action decision.",
        },
        "hard_limitations": [
            "Public rows were retrospectively captured and do not establish original-date availability, revision lineage, field semantics, data rights or a complete total-return ledger.",
            "Displayed accumulated NAV is not an executable exchange-market price; market price/NAV/IOPV, fund events, halts, limits, lot size, bid/ask, fills, fees, taxes, settlement and suitability are not modeled.",
            "The five-code group is representative only, not U0, an historical population, a decision universe or an allocation recommendation.",
            "This cannot close UR01--UR05 or establish individual action feasibility, even if the proxy hurdle is not falsified.",
        ],
    }


def _markdown(result: Mapping[str, Any]) -> str:
    metrics = result["full_period_metrics"]
    strict = result["strict_proxy_hurdle"]
    years = result["complete_calendar_years"]
    rolling = result["rolling_five_year_endpoints"]
    complete_year_rows = "\n".join(
        "| {year} | {complete} | {value} | {passed} |".format(
            year=item["year"],
            complete="是" if item["complete"] else "否",
            value="—" if item["net_unitized_change"] is None else f"{item['net_unitized_change']:.2%}",
            passed="—" if item["strict_hurdle_pass"] is None else ("是" if item["strict_hurdle_pass"] else "否"),
        )
        for item in years
    ) or "| — | — | — | — |"
    rolling_values = [float(item["annualized_net_unitized_change"]) for item in rolling]
    rolling_summary = "无合格端点"
    if rolling_values:
        rolling_summary = (
            f"{len(rolling_values)} 个端点；最小值 {min(rolling_values):.2%}，"
            f"最大值 {max(rolling_values):.2%}，"
            f"通过数 {sum(value >= 0.05 for value in rolling_values)}/{len(rolling_values)}。"
        )
    failures = strict["failures"]
    turnover = result["turnover_and_cost_summary"]
    failure_text = "无（仅表示代理口径未被其自身否决）。" if not failures else "\n".join(f"- {item}" for item in failures)
    return f"""# R5 公开累计净值绝对动量代理检验 — 2026-08-15

## 结论

**状态：`{strict['state']}`。** 该状态只回答固定的公开累计净值代理算术是否被其自身 `5%` 历史否决线否决；它不是投资者回报、收益承诺、预测、产品推荐或操作结论。

**预注册状态：不是干净预注册。** 在规则写定前已进行相关公开字段可用性/样例观察；因此本结果只能作探索性负面记录，不能把任何正面表现解释为独立样本外或策略证据。

本运行使用锁定的权益、国债、黄金和货币市场五代码分组，以初始值 1 的单位净值记录，并在每月信号后的下一共同观察日才生效。公开页面的累计净值不是场内成交价，故即使代理算术未被否决，也不能称为可个人执行的策略。

## 全期代理指标

| 项目 | 值 |
|---|---:|
| 有效区间 | {metrics['start_date']} 至 {metrics['end_date']} |
| 期末单位净值 | {metrics['final_unit_nav']:.4f} |
| 年化净单位化变化 | {metrics['annualized_net_unitized_change']:.2%} |
| 最大回撤 | {metrics['max_drawdown']:.2%} |
| 单边固定成本载荷 | {result['simulation']['fixed_one_way_cost_bps']:.0f}bp |
| 调仓次数 | {len(result['rebalances'])} |
| 总单边换手 | {turnover['total_one_way_turnover']:.4f} |
| 零换手调仓 | {turnover['zero_turnover_events']} |
| 单次成本分数的算术和 | {turnover['sum_simple_cost_fractions']:.2%} |

“总单边换手”是 144 次调仓的单边换手算术和；“单次成本分数的算术和”只是逐次 20bp 示例成本的算术求和，**不是**复合回报拖累，也不是可成交成本估计。

## 完整自然年代理结果

| 年份 | 完整 | 净单位化变化 | >=5% |
|---:|:---:|---:|:---:|
{complete_year_rows}

## 滚动五年代理结果

{rolling_summary}

## 否决原因

{failure_text}

## 必须保留的限制

- 原始行是事后取得的公开聚合页面，不能证明历史可得时间、修订、字段语义、数据权利或完整总回报。
- 累计净值不等于场内可成交市价；本运行没有市场价/NAV/IOPV、事件、停复牌、涨跌停、盘口、成交、费用、税费、结算或适当性账本。
- 五代码只是代表性研究输入，不是 U0、历史总体、决策总体或配置清单。
- 本结果不能关闭 `UR01--UR05`，也不能据此实施任何操作。
- 原始抓取时记录的脚本哈希与当前派生脚本不同，且抓取时版本未单独留存；原始响应哈希仍通过校验，但抓取实现的版本等价性不能被追溯验证。

机器可读结果：[r5_public_nav_absolute_momentum_probe_20260815.json](r5_public_nav_absolute_momentum_probe_20260815.json)。
"""


def _capture() -> None:
    if SOURCE_DIR.exists() or MANIFEST_PATH.exists():
        raise FileExistsError("R5 source directory already exists; use --verify-only to avoid modifying frozen source")
    bundles: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    for code in CODES:
        bundle = _fetch_bundle(code)
        bundles[code] = (bundle, _validate_bundle(bundle))
    SOURCE_DIR.mkdir(parents=True, exist_ok=False)
    for code, (bundle, _) in bundles.items():
        _write_json(_bundle_path(code), bundle)
    entries = [_source_entry(code, bundles[code][0], bundles[code][1]) for code in CODES]
    manifest = _make_manifest(entries)
    _write_json(MANIFEST_PATH, manifest)
    _write_text(MANIFEST_MD_PATH, _manifest_markdown(manifest))
    result = _derive()
    _write_json(OUTPUT_PATH, result)
    _write_text(OUTPUT_MD_PATH, _markdown(result))


def _verify_and_refresh() -> None:
    _load_manifest()
    result = _derive()
    _write_json(OUTPUT_PATH, result)
    _write_text(OUTPUT_MD_PATH, _markdown(result))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true", help="Capture and seal one new public source batch, then derive R5 output.")
    parser.add_argument("--verify-only", action="store_true", help="Verify sealed source bytes and refresh only derived R5 output.")
    arguments = parser.parse_args()
    if arguments.capture == arguments.verify_only:
        parser.error("choose exactly one of --capture or --verify-only")
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(f"predeclared R5 protocol not found: {PROTOCOL_PATH}")
    _run_implementation_self_tests()
    if arguments.capture:
        _capture()
    else:
        _verify_and_refresh()
    print(f"R5 public NAV proxy: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
