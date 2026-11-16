#!/usr/bin/env python3
"""Freeze and screen a limited public ETF price observation.

This is deliberately a *research-only* falsification tool.  It preserves a
public Sina observation through AkShare, evaluates a small predeclared family
of momentum-rule hypotheses, and refuses to describe the resulting arithmetic
as investor total return, a licensed point-in-time replay, or a usable
strategy.  The raw source is immutable once first captured so later vendor
revisions cannot silently alter this case's observation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import akshare as ak
import numpy as np
import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "probe-public-etf-extended-r2-20260814"
RAW_PATH = SOURCE_DIR / "public_sina_etf_eod_observation.json"
MANIFEST_JSON = SOURCE_DIR / "manifest.json"
MANIFEST_MD = SOURCE_DIR / "manifest.md"
OUTPUT_JSON = CASE_DIR / "analysis" / "r2_public_series_extended_probe_20260814.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r2_public_series_extended_probe_20260814.md"
PRIOR_PUBLIC_INPUT = CASE_DIR / "sources" / "probe-public-etf-price-r0-20260814" / (
    "e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda"
    ".portfolio.replay.json"
)

DATA_CUTOFF = "2026-08-13"
ASSETS = ("510300", "510880", "518880", "511010")
RISK_ASSETS = ASSETS[:3]
DEFENSIVE_ASSET = "511010"
SOURCE_METHOD = "akshare.fund_etf_hist_sina(symbol='sh<code>')"
SOURCE_QUALITY = "tier_3_public_aggregation_observation"
PRICE_BASIS = "unverified_public_close_basis_not_total_return"
COST_BPS = (0.0, 10.0, 20.0, 50.0)
MODEL_VERSION = "monthly_self_financing_units_v2"
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"

# These are economic hypotheses and robustness variants fixed in this script
# before this screening run.  They were not independently pre-registered. The
# records are retained as a family so an apparent survivor cannot be mistaken
# for a unique, optimized rule.
HYPOTHESES = (
    {
        "hypothesis_id": "H01",
        "name": "12m-positive-momentum-top2-50pct-risk",
        "lookback_observations": 252,
        "top_n": 2,
        "risk_budget": 0.50,
        "economic_rationale": "Use medium-horizon relative strength only when the selected domestic risk sleeves have positive absolute momentum; retain the residual in the defensive comparison sleeve.",
    },
    {
        "hypothesis_id": "H02",
        "name": "12m-positive-momentum-top2-40pct-risk",
        "lookback_observations": 252,
        "top_n": 2,
        "risk_budget": 0.40,
        "economic_rationale": "Risk-budget robustness variant of H01.",
    },
    {
        "hypothesis_id": "H03",
        "name": "12m-positive-momentum-top2-60pct-risk",
        "lookback_observations": 252,
        "top_n": 2,
        "risk_budget": 0.60,
        "economic_rationale": "Risk-budget robustness variant of H01.",
    },
    {
        "hypothesis_id": "H04",
        "name": "9m-positive-momentum-top2-50pct-risk",
        "lookback_observations": 189,
        "top_n": 2,
        "risk_budget": 0.50,
        "economic_rationale": "Horizon robustness variant of H01.",
    },
    {
        "hypothesis_id": "H05",
        "name": "18m-positive-momentum-top2-50pct-risk",
        "lookback_observations": 378,
        "top_n": 2,
        "risk_budget": 0.50,
        "economic_rationale": "Horizon robustness variant of H01.",
    },
    {
        "hypothesis_id": "H06",
        "name": "12m-positive-momentum-top1-50pct-risk",
        "lookback_observations": 252,
        "top_n": 1,
        "risk_budget": 0.50,
        "economic_rationale": "Concentration robustness variant of H01.",
    },
    {
        "hypothesis_id": "H07",
        "name": "12m-positive-momentum-top3-50pct-risk",
        "lookback_observations": 252,
        "top_n": 3,
        "risk_budget": 0.50,
        "economic_rationale": "Breadth robustness variant of H01.",
    },
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(CASE_DIR.parents[2]))


def _runtime_provenance(*, adapter: str) -> dict[str, str]:
    """Record runtime facts without claiming an uncommitted script is versioned."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=CASE_DIR.parents[2],
            check=True,
            capture_output=True,
            text=True,
        )
        git_commit = completed.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "not_available"
    return {
        "git_commit_at_runtime": git_commit,
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "pandas_version": pd.__version__,
        "adapter": adapter,
        "adapter_version": str(getattr(ak, "__version__", "not_reported")),
    }


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _dependency_records() -> list[dict[str, Any]]:
    if not PRIOR_PUBLIC_INPUT.exists():
        return []
    return [
        {
            **_file_record(PRIOR_PUBLIC_INPUT),
            "dependency_role": "descriptive_overlap_only",
            "source_quality": "tier_3_frozen_public_observation",
            "purpose": "A prior public observation is read only to expose cross-capture close differences; it does not validate price basis, total return, availability or execution.",
            "limitations": "The dependency is a public, non-entitled observation and cannot enter a formal replay or strategy decision.",
        }
    ]


def _freeze_control(*, sealed_at: str, seal_status: str) -> dict[str, Any]:
    return {
        "schema_version": SOURCE_FREEZE_SCHEMA,
        "seal_status": seal_status,
        "sealed_at": sealed_at,
        "frozen_files": [_file_record(RAW_PATH)],
        "runtime_provenance": _runtime_provenance(adapter="AkShare fund_etf_hist_sina"),
        "boundary": "Case-local hash control only. It detects a raw-source mismatch during scripted verification, but does not establish external notarization, data rights, point-in-time availability, total return or execution quality.",
    }


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _normalise_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    required = ("date", "open", "high", "low", "close", "volume", "amount")
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"public response misses expected fields: {missing}")
    frame = frame.loc[:, required].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in required[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["date", "close"]).sort_values("date", kind="stable")
    frame = frame.loc[frame["date"] <= pd.Timestamp(DATA_CUTOFF)]
    if frame.empty or frame["date"].duplicated().any() or (frame["close"] <= 0).any():
        raise ValueError("public response has invalid date or close rows")
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        record: dict[str, Any] = {"date": pd.Timestamp(row["date"]).date().isoformat()}
        for column in required[1:]:
            value = row[column]
            record[column] = None if pd.isna(value) else float(value)
        records.append(record)
    return records


def _fetch_raw_observation() -> dict[str, Any]:
    observations: dict[str, Any] = {}
    for code in ASSETS:
        frame = ak.fund_etf_hist_sina(symbol=f"sh{code}")
        records = _normalise_records(frame)
        observations[code] = {
            "symbol_requested": f"sh{code}",
            "record_count": len(records),
            "first_date": records[0]["date"],
            "last_date": records[-1]["date"],
            "records": records,
        }
    return {
        "schema_version": "public_sina_etf_eod_observation.v1",
        "artifact_class": "primary_public_observation_not_entitled_data",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "data_cutoff": DATA_CUTOFF,
        "provider": "Sina public market-data endpoint via AkShare adapter",
        "method": SOURCE_METHOD,
        "source_quality": SOURCE_QUALITY,
        "price_basis": PRICE_BASIS,
        "limitations": [
            "The source is a public aggregation observation, not an official or licensed point-in-time archive.",
            "No source-provided available_at, revision chain, corporate-action ledger, NAV ledger, IOPV ledger, halt/limit ledger, trading calendar, fee/tax record, bid/ask record, or execution evidence is present.",
            "A public close cannot be interpreted here as investor total return, tradable fill, or proof that the observation was available on its historical date.",
        ],
        "series": observations,
    }


def _load_raw() -> dict[str, Any]:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"retained raw source is absent: {RAW_PATH}")
    payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "public_sina_etf_eod_observation.v1":
        raise ValueError("existing raw source has an unexpected schema")
    if payload.get("data_cutoff") != DATA_CUTOFF:
        raise ValueError("existing raw source has an unexpected cutoff")
    return payload


def _source_file_entry(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        **_file_record(RAW_PATH),
        "publisher": raw["provider"],
        "title": "Public ETF EOD observation through AkShare Sina adapter",
        "document_date": DATA_CUTOFF,
        "url": "upstream endpoint accessed through akshare.fund_etf_hist_sina",
        "format": "json",
        "capture_note": "Retained public-observation input with unverified adjustment and availability basis.",
    }


def _manifest_markdown(manifest: dict[str, Any]) -> str:
    raw_hash = manifest["files"][0]["sha256"]
    dependency_lines = "无。"
    if manifest.get("dependencies"):
        dependency_lines = "\n".join(
            f"- `{entry['path']}`（SHA-256 `{entry['sha256']}`）：仅作{entry['dependency_role']}。"
            for entry in manifest["dependencies"]
        )
    return f"""# Extended Public ETF Observation Manifest

One raw public-observation archive is retained in `manifest.json`: daily ETF
bars for 510300, 510880, 518880 and 511010 through {DATA_CUTOFF}, accessed
through the AkShare Sina adapter and originally captured at `{manifest['captured_at']}`.

The archive SHA-256 is `{raw_hash}`. It is a tier-3 public observation, not an
official or licensed point-in-time archive. It does not establish an adjustment
basis, investor total return, historical availability, corporate actions, NAV,
trading status, costs, market depth or executable fills. It is retained only
to falsify research hypotheses and cannot approve a strategy or action.

## Hash control

The source manifest is sealed through `{manifest['source_freeze']['schema_version']}`
at `{manifest['source_freeze']['sealed_at']}`. Scripted verify/derived-refresh
modes compare the retained raw bytes and declared dependencies against this
control and never rewrite it. This is a case-local tamper-evident control, not
external notarization or a data-rights assertion.

## Descriptive-only dependencies

{dependency_lines}
"""


def _make_source_manifest(raw: dict[str, Any], *, seal_status: str) -> dict[str, Any]:
    manifest = {
        "capture_batch": SOURCE_DIR.name,
        "captured_at": raw["retrieved_at"],
        "purpose": "Frozen extended public ETF daily-bar observation for research-only hypothesis falsification. It cannot establish total return, point-in-time availability, formal replay, product admission, allocation, holding or action.",
        "source_quality": SOURCE_QUALITY,
        "files": [_source_file_entry(raw)],
        "dependencies": _dependency_records(),
        "limitations": raw["limitations"],
        "source_freeze": _freeze_control(
            sealed_at=datetime.now(timezone.utc).isoformat(),
            seal_status=seal_status,
        ),
    }
    _write_json(MANIFEST_JSON, manifest)
    _write_text(MANIFEST_MD, _manifest_markdown(manifest))
    return manifest


def _verify_entry(entry: dict[str, Any], *, label: str) -> None:
    required = {"path", "bytes", "sha256"}
    missing = sorted(required.difference(entry))
    if missing:
        raise ValueError(f"{label} has no required fields: {missing}")
    path = (CASE_DIR.parents[2] / str(entry["path"])).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    if path.stat().st_size != int(entry["bytes"]):
        raise ValueError(f"{label} byte size differs: {path}")
    if _sha256(path) != entry["sha256"]:
        raise ValueError(f"{label} SHA-256 differs: {path}")


def _verify_registry_manifest_seal() -> None:
    registry_path = CASE_DIR / "data" / "source_registry.json"
    if not registry_path.is_file():
        raise FileNotFoundError("source registry is required for sealed-source verification")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = next((item for item in registry if item.get("source_id") == "P02"), None)
    if not isinstance(source, dict):
        raise ValueError("source registry has no P02 sealed-source record")
    if source.get("sealed_manifest_path") != _repo_relative(MANIFEST_JSON):
        raise ValueError("source registry P02 manifest path differs from the required sealed manifest")
    if source.get("sealed_manifest_sha256") != _sha256(MANIFEST_JSON):
        raise ValueError("source registry P02 manifest SHA-256 differs from the sealed manifest")


def _load_frozen_source() -> tuple[dict[str, Any], dict[str, Any]]:
    raw = _load_raw()
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError("a retained raw observation requires a sealed manifest")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    freeze = manifest.get("source_freeze")
    if not isinstance(freeze, dict) or freeze.get("schema_version") != SOURCE_FREEZE_SCHEMA:
        raise ValueError("source manifest is not sealed; run --seal-existing-freeze explicitly")
    frozen_files = freeze.get("frozen_files")
    if not isinstance(frozen_files, list) or len(frozen_files) != 1:
        raise ValueError("source freeze must contain exactly one retained raw file")
    if not isinstance(manifest.get("files"), list) or len(manifest["files"]) != 1:
        raise ValueError("source manifest must contain exactly one retained raw file")
    _verify_entry(frozen_files[0], label="source-freeze raw file")
    _verify_entry(manifest["files"][0], label="source-manifest raw file")
    frozen_identity = {key: frozen_files[0][key] for key in ("path", "bytes", "sha256")}
    manifest_identity = {key: manifest["files"][0][key] for key in ("path", "bytes", "sha256")}
    if frozen_identity != manifest_identity:
        raise ValueError("source-freeze and source-manifest raw records differ")
    for number, dependency in enumerate(manifest.get("dependencies", []), start=1):
        _verify_entry(dependency, label=f"source dependency {number}")
    _verify_registry_manifest_seal()
    return raw, manifest


def _seal_existing_freeze() -> dict[str, Any]:
    raw = _load_raw()
    if not MANIFEST_JSON.exists():
        raise FileNotFoundError("cannot seal an existing raw observation without its original manifest")
    existing = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    if existing.get("source_freeze"):
        raise ValueError("source manifest is already sealed; do not reseal it")
    files = existing.get("files")
    if not isinstance(files, list) or len(files) != 1:
        raise ValueError("existing source manifest does not contain exactly one raw file")
    _verify_entry(files[0], label="existing source-manifest raw file")
    existing["dependencies"] = _dependency_records()
    existing["source_freeze"] = _freeze_control(
        sealed_at=datetime.now(timezone.utc).isoformat(),
        seal_status="explicit_post_capture_migration",
    )
    existing["freeze_migration_boundary"] = (
        "The original capture pre-dated the explicit hash-control migration. "
        "Original capture runtime provenance is unavailable; the migration provenance "
        "is retained in source_freeze.runtime_provenance."
    )
    _write_json(MANIFEST_JSON, existing)
    _write_text(MANIFEST_MD, _manifest_markdown(existing))
    return existing


def _market_panels(raw: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    """Build observed open/close panels and retain source-presence states.

    A missing row is deliberately not treated as a market closure. The public
    observation has no authoritative calendar or market-status ledger.
    """
    frames: dict[str, pd.DataFrame] = {}
    all_dates = pd.DatetimeIndex([])
    for code in ASSETS:
        item = raw.get("series", {}).get(code, {})
        frame = pd.DataFrame(item.get("records", []))
        for column in ("date", "open", "close"):
            if column not in frame.columns:
                frame[column] = np.nan
        frame = frame.loc[:, ("date", "open", "close")].copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["open"] = pd.to_numeric(frame["open"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["date"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any():
            raise ValueError(f"invalid frozen series dates for {code}")
        frames[code] = frame.set_index("date")
        all_dates = all_dates.union(frames[code].index)
    all_dates = all_dates.sort_values()
    opens = pd.concat({code: frames[code]["open"] for code in ASSETS}, axis=1, sort=True)
    closes = pd.concat({code: frames[code]["close"] for code in ASSETS}, axis=1, sort=True)
    valid = (opens > 0.0) & (closes > 0.0)
    common = valid.all(axis=1)
    open_panel = opens.loc[common].sort_index()
    close_panel = closes.loc[common].sort_index()
    if open_panel.empty or close_panel.empty or not open_panel.index.equals(close_panel.index):
        raise ValueError("no common valid public-observation open/close sessions")
    presence_rows: list[dict[str, Any]] = []
    for session in all_dates:
        asset_status = {
            code: (
                "present_valid_open_and_close"
                if bool(valid.loc[session, code])
                else "not_observed_or_invalid_in_source_unknown_reason"
            )
            for code in ASSETS
        }
        presence_rows.append(
            {
                "date": session.date().isoformat(),
                "asset_status": asset_status,
                "common_valid_observation_session": bool(common.loc[session]),
            }
        )
    return open_panel, close_panel, presence_rows


def _price_panel(raw: dict[str, Any]) -> pd.DataFrame:
    """Compatibility helper for source-overlap diagnostics."""
    return _market_panels(raw)[1]


def _prior_public_overlap_observation(raw: dict[str, Any]) -> dict[str, Any]:
    """Describe, but never validate, overlap with the prior public capture."""
    if not PRIOR_PUBLIC_INPUT.exists():
        return {
            "status": "not_available",
            "reason": "The prior public observation was not present at evaluation time.",
        }
    prior = json.loads(PRIOR_PUBLIC_INPUT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for code in ASSETS:
        prior_frame = pd.DataFrame(prior.get("market_data", {}).get(code, []))
        current_frame = pd.DataFrame(raw.get("series", {}).get(code, {}).get("records", []))
        prior_frame["date"] = pd.to_datetime(prior_frame.get("date"), errors="coerce")
        current_frame["date"] = pd.to_datetime(current_frame.get("date"), errors="coerce")
        prior_frame["close"] = pd.to_numeric(prior_frame.get("close"), errors="coerce")
        current_frame["close"] = pd.to_numeric(current_frame.get("close"), errors="coerce")
        joint = pd.concat(
            [
                prior_frame.dropna(subset=["date", "close"]).set_index("date")["close"].rename("prior"),
                current_frame.dropna(subset=["date", "close"]).set_index("date")["close"].rename("extended"),
            ],
            axis=1,
            sort=True,
        ).dropna()
        if joint.empty:
            rows.append({"code": code, "overlap_sessions": 0, "status": "no_overlap"})
            continue
        difference = (joint["prior"] - joint["extended"]).abs()
        rows.append(
            {
                "code": code,
                "overlap_sessions": len(joint),
                "overlap_start": joint.index[0].date().isoformat(),
                "overlap_end": joint.index[-1].date().isoformat(),
                "max_absolute_close_difference": float(difference.max()),
                "rows_above_0_001_difference": int((difference > 0.001).sum()),
                "rows_above_0_01_difference": int((difference > 0.01).sum()),
            }
        )
    return {
        "status": "descriptive_only_not_basis_validation",
        "prior_path": str(PRIOR_PUBLIC_INPUT.relative_to(CASE_DIR)),
        "prior_sha256": _sha256(PRIOR_PUBLIC_INPUT),
        "interpretation": "Both inputs are public observations. Agreement cannot prove adjustment basis, source vintage, historical availability, total return, or execution quality; differences must remain visible.",
        "rows": rows,
    }


def _build_rebalance_schedule(
    prices: pd.DataFrame,
    hypothesis: dict[str, Any],
) -> tuple[pd.DataFrame, pd.Series, list[dict[str, Any]]]:
    """Freeze monthly signal and next-session execution timing.

    The warm-up rule intentionally waits for the next calendar-month boundary
    after enough observed closes exist. It does not introduce a mid-month
    decision merely because the lookback becomes available during that month.
    """
    lookback = int(hypothesis["lookback_observations"])
    top_n = int(hypothesis["top_n"])
    risk_budget = float(hypothesis["risk_budget"])
    targets = pd.DataFrame(0.0, index=prices.index, columns=ASSETS)
    rebalance_events = pd.Series(False, index=prices.index, dtype=bool)
    decision_ledger: list[dict[str, Any]] = []
    last_seen_month: tuple[int, int] | None = None
    for position, session in enumerate(prices.index):
        month = (int(session.year), int(session.month))
        if month == last_seen_month:
            continue
        last_seen_month = month
        if position < lookback + 1 or position + 1 >= len(prices.index):
            continue
        history = prices.iloc[:position]
        last_close = history.iloc[-1]
        momentum = last_close / history.iloc[-(lookback + 1)] - 1.0
        eligible = [code for code in RISK_ASSETS if momentum[code] > 0.0]
        selected = sorted(eligible, key=lambda code: float(momentum[code]), reverse=True)[:top_n]
        target = pd.Series(0.0, index=ASSETS)
        if selected:
            target.loc[selected] = risk_budget / len(selected)
            target.loc[DEFENSIVE_ASSET] = 1.0 - risk_budget
        else:
            target.loc[DEFENSIVE_ASSET] = 1.0
        execution_session = prices.index[position + 1]
        targets.loc[execution_session] = target
        rebalance_events.loc[execution_session] = True
        decision_ledger.append(
            {
                "signal_session": session.date().isoformat(),
                "execution_session": execution_session.date().isoformat(),
                "signal_uses_close_through": history.index[-1].date().isoformat(),
                "lookback_observations": lookback,
                "selected_risk_sleeves": selected,
                "target_security_weights": {code: float(target[code]) for code in ASSETS},
                "target_cash_weight": float(1.0 - target.sum()),
                "implementation_timing": "next_observed_session_open_then_same_session_close_mark",
            }
        )
    if not decision_ledger:
        raise ValueError("hypothesis produces no monthly rebalance decisions")
    return targets, rebalance_events, decision_ledger


def _rolling_five_year(nav: pd.Series) -> dict[str, Any]:
    annualized: list[float] = []
    for endpoint in nav.index:
        start_candidates = nav.index[nav.index <= endpoint - pd.DateOffset(years=5)]
        if start_candidates.empty:
            continue
        start = start_candidates[-1]
        elapsed_days = int((endpoint - start).days)
        if elapsed_days >= 1820:
            annualized.append(float((nav.loc[endpoint] / nav.loc[start]) ** (365.25 / elapsed_days) - 1.0))
    if not annualized:
        raise ValueError("no complete five-year windows")
    return {
        "window_count": len(annualized),
        "windows_below_5pct": sum(value < 0.05 for value in annualized),
        "windows_meeting_5pct": sum(value >= 0.05 for value in annualized),
        "minimum_annualized_public_series_change": min(annualized),
        "maximum_annualized_public_series_change": max(annualized),
        "all_complete_windows_meet_5pct": all(value >= 0.05 for value in annualized),
        "dependence_warning": "Daily-end five-year windows overlap and are not independent observations.",
    }


def _annual_rows(nav: pd.Series, *, initial_nav: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    first_year = int(nav.index[0].year)
    last_year = int(nav.index[-1].year)
    for year, values in nav.groupby(nav.index.year):
        first_session = values.index[0]
        prior = nav.loc[nav.index < first_session]
        carried_start_nav = float(prior.iloc[-1]) if not prior.empty else initial_nav
        complete_natural_year = int(year) not in {first_year, last_year}
        rows.append(
            {
                "year": int(year),
                "start_session": first_session.date().isoformat(),
                "end_session": values.index[-1].date().isoformat(),
                "carried_start_nav_from_prior_session": carried_start_nav,
                "end_nav": float(values.iloc[-1]),
                "public_series_change": float(values.iloc[-1] / carried_start_nav - 1.0),
                "complete_natural_year_within_observation": complete_natural_year,
                "included_in_any_annual_hurdle": False,
                "boundary_note": (
                    "Initial or cutoff calendar-year segment; displayed for reconciliation only."
                    if not complete_natural_year
                    else "Carry-forward prior-session NAV is used for the full calendar-year arithmetic."
                ),
            }
        )
    return rows


def _evaluate(
    opens: pd.DataFrame,
    prices: pd.DataFrame,
    targets: pd.DataFrame,
    rebalance_events: pd.Series,
    cost_bps: float,
    *,
    include_daily_state: bool,
) -> dict[str, Any]:
    """Simulate monthly self-financing units, cash and drifted close weights.

    Costs are paid once per scheduled monthly rebalance. One-way turnover is
    defined from drifted pre-trade component weights (securities plus cash) to
    target component weights. The calculation is a transparent public-price
    diagnostic, not a fill, lot, tax, settlement or total-return model.
    """
    if not opens.index.equals(prices.index):
        raise ValueError("open and close panels must share an identical index")
    if not prices.index.equals(targets.index) or not prices.index.equals(rebalance_events.index):
        raise ValueError("rebalance schedule index must match the price panel")
    event_sessions = rebalance_events[rebalance_events].index
    if event_sessions.empty:
        raise ValueError("hypothesis produces no active sessions")
    start = event_sessions[0]
    sessions = prices.loc[start:].index
    asset_codes = list(ASSETS)
    open_array = opens.loc[sessions, asset_codes].to_numpy(dtype=float)
    close_array = prices.loc[sessions, asset_codes].to_numpy(dtype=float)
    target_array = targets.loc[sessions, asset_codes].to_numpy(dtype=float)
    event_array = rebalance_events.loc[sessions].to_numpy(dtype=bool)
    units = np.zeros(len(asset_codes), dtype=float)
    cash = 1.0
    initial_nav = 1.0
    nav_values: list[float] = []
    nav_index: list[pd.Timestamp] = []
    rebalance_ledger: list[dict[str, Any]] = []
    daily_state: list[dict[str, Any]] = []
    max_self_financing_error = 0.0
    for position, session in enumerate(sessions):
        open_values = units * open_array[position]
        pre_trade_nav = float(cash + open_values.sum())
        rebalance_executed = bool(event_array[position])
        one_way_turnover = 0.0
        transaction_cost = 0.0
        if rebalance_executed:
            target_security = target_array[position]
            if (target_security < -1e-12).any() or target_security.sum() > 1.0 + 1e-12:
                raise ValueError(f"invalid target weights on {session.date().isoformat()}")
            target_cash = float(1.0 - target_security.sum())
            pre_security_weights = open_values / pre_trade_nav
            pre_cash_weight = float(cash / pre_trade_nav)
            one_way_turnover = float(
                (
                    np.abs(target_security - pre_security_weights).sum()
                    + abs(target_cash - pre_cash_weight)
                )
                / 2.0
            )
            transaction_cost = float(pre_trade_nav * cost_bps / 10000.0 * one_way_turnover)
            post_trade_nav = float(pre_trade_nav - transaction_cost)
            units = target_security * post_trade_nav / open_array[position]
            cash = target_cash * post_trade_nav
            post_trade_open_nav = float(cash + (units * open_array[position]).sum())
            self_financing_error = pre_trade_nav - transaction_cost - post_trade_open_nav
            max_self_financing_error = max(max_self_financing_error, abs(self_financing_error))
            rebalance_ledger.append(
                {
                    "execution_session": session.date().isoformat(),
                    "pre_trade_nav_at_observed_open": pre_trade_nav,
                    "post_trade_nav_at_observed_open": post_trade_open_nav,
                    "pre_trade_security_weights": {
                        code: float(pre_security_weights[number])
                        for number, code in enumerate(asset_codes)
                    },
                    "pre_trade_cash_weight": pre_cash_weight,
                    "target_security_weights": {
                        code: float(target_security[number])
                        for number, code in enumerate(asset_codes)
                    },
                    "target_cash_weight": target_cash,
                    "one_way_turnover": one_way_turnover,
                    "per_one_way_turnover_cost_bps": cost_bps,
                    "transaction_cost_paid": transaction_cost,
                    "self_financing_error": self_financing_error,
                    "execution_reference": "observed_public_session_open",
                    "lot_treatment": "not_modeled",
                    "no_fill_or_partial_fill_treatment": "not_modeled",
                    "settlement_treatment": "not_modeled",
                }
            )
        close_values = units * close_array[position]
        nav = float(cash + close_values.sum())
        if nav <= 0.0:
            raise ValueError(f"non-positive modeled NAV on {session.date().isoformat()}")
        close_security_weights = close_values / nav
        nav_values.append(nav)
        nav_index.append(session)
        if include_daily_state:
            daily_state.append(
                {
                    "session": session.date().isoformat(),
                    "close_nav": nav,
                    "cash_value": float(cash),
                    "units": {
                        code: float(units[number]) for number, code in enumerate(asset_codes)
                    },
                    "close_security_values": {
                        code: float(close_values[number]) for number, code in enumerate(asset_codes)
                    },
                    "drifted_close_security_weights": {
                        code: float(close_security_weights[number])
                        for number, code in enumerate(asset_codes)
                    },
                    "drifted_close_cash_weight": float(cash / nav),
                    "monthly_rebalance_executed_at_open": rebalance_executed,
                }
            )
    nav = pd.Series(nav_values, index=pd.DatetimeIndex(nav_index), name="modeled_nav")
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    if elapsed_days <= 0:
        raise ValueError("invalid evaluation duration")
    peak = initial_nav
    maximum_drawdown = 0.0
    for value in nav:
        peak = max(peak, float(value))
        maximum_drawdown = min(maximum_drawdown, float(value / peak - 1.0))
    annual_rows = _annual_rows(nav, initial_nav=initial_nav)
    result: dict[str, Any] = {
        "model_version": MODEL_VERSION,
        "evaluation_start": nav.index[0].date().isoformat(),
        "evaluation_end": nav.index[-1].date().isoformat(),
        "common_sessions": len(nav),
        "per_one_way_turnover_cost_bps": cost_bps,
        "annualized_public_series_change": float(
            (nav.iloc[-1] / initial_nav) ** (365.25 / elapsed_days) - 1.0
        ),
        "maximum_drawdown": maximum_drawdown,
        "cumulative_one_way_turnover": float(
            sum(row["one_way_turnover"] for row in rebalance_ledger)
        ),
        "initial_one_way_turnover": float(rebalance_ledger[0]["one_way_turnover"]),
        "total_transaction_cost_paid": float(
            sum(row["transaction_cost_paid"] for row in rebalance_ledger)
        ),
        "rebalance_event_count": len(rebalance_ledger),
        "max_abs_self_financing_error": max_self_financing_error,
        "rebalance_ledger": rebalance_ledger,
        "rolling_five_year_public_series_diagnostic": _rolling_five_year(nav),
        "annual_public_series_rows": annual_rows,
        "annual_row_method": "Each calendar year carries forward the prior observed-session NAV; initial and cutoff-year fragments are explicitly not complete years.",
    }
    if include_daily_state:
        result["daily_position_state"] = daily_state
    return result


def _result(raw: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    opens, prices, presence_rows = _market_panels(raw)
    prior_overlap = _prior_public_overlap_observation(raw)
    rows: list[dict[str, Any]] = []
    for hypothesis in HYPOTHESES:
        targets, rebalance_events, decision_ledger = _build_rebalance_schedule(prices, hypothesis)
        sensitivity = [
            _evaluate(
                opens,
                prices,
                targets,
                rebalance_events,
                cost,
                include_daily_state=cost == 20.0 and hypothesis["hypothesis_id"] == "H01",
            )
            for cost in COST_BPS
        ]
        primary = next(
            item for item in sensitivity if item["per_one_way_turnover_cost_bps"] == 20.0
        )
        primary_summary = {
            key: value for key, value in primary.items() if key != "daily_position_state"
        }
        rolling = primary["rolling_five_year_public_series_diagnostic"]
        rows.append(
            {
                **hypothesis,
                "decision_count": len(decision_ledger),
                "monthly_decision_ledger": decision_ledger,
                "daily_position_state_retention": (
                    "Retained only for H01 at the 20-bps sensitivity to make the"
                    " unit/cash drift convention inspectable without duplicating"
                    " full daily state ledgers for exploratory variants. The retained"
                    " state is located in cost_sensitivity, not duplicated in"
                    " primary_20bps."
                ),
                "cost_sensitivity": sensitivity,
                "primary_20bps": primary_summary,
                "screening_readout": {
                    "arithmetic_all_windows_meet_5pct_public_series_hurdle": rolling["all_complete_windows_meet_5pct"],
                    "not_a_total_return_or_strategy_pass": True,
                },
            }
        )
    primary_candidate = next(item for item in rows if item["hypothesis_id"] == "H01")
    candidates_with_arithmetic_hurdle = [
        item["hypothesis_id"]
        for item in rows
        if item["primary_20bps"]["rolling_five_year_public_series_diagnostic"]["all_complete_windows_meet_5pct"]
    ]
    return {
        "schema_version": "r2_extended_public_series_hypothesis_probe.v2",
        "as_of": "2026-08-14",
        "artifact_class": "derived_research_observation",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "derived_runtime_provenance": _runtime_provenance(
            adapter="AkShare source retained; self-financing calculation is case-local Python"
        ),
        "source": {
            "path": str(RAW_PATH.relative_to(CASE_DIR)),
            "sha256": _sha256(RAW_PATH),
            "manifest_path": str(MANIFEST_JSON.relative_to(CASE_DIR)),
            "sealed_manifest_sha256": _sha256(MANIFEST_JSON),
            "source_freeze": manifest["source_freeze"],
            "dependencies": manifest.get("dependencies", []),
            "quality": SOURCE_QUALITY,
            "source_declared_or_observed_basis": PRICE_BASIS,
        },
        "protocol": {
            "status": "retrospective_public_observation_exploratory_screen_not_independently_pre_registered_not_formal_replay",
            "decision_frequency": "first observed session of each calendar month after the full lookback exists; the warm-up waits for a month boundary rather than entering mid-month",
            "information_timing": "signal uses closes only through the previous observed session; target is executed at the next observed session open and marked to that same session close",
            "rebalance_frequency": "Every scheduled monthly execution rebalances drifted units to the target, even when the target sleeve set has not changed.",
            "asset_scope": {
                "risk_comparison_sleeves": list(RISK_ASSETS),
                "defensive_comparison_sleeve": DEFENSIVE_ASSET,
                "scope_warning": "A four-ETF observation is not the open domestic universe, a frozen U0 population, or a future decision universe.",
            },
            "selection_rule": "At each monthly decision, rank risk sleeves with positive lookback public-series price change, select the stated top N, equal-weight selected risk sleeves within the stated risk budget, and assign the residual to 511010; if none qualifies, assign 100% to 511010.",
            "accounting_model": "Monthly self-financing units-and-cash simulation. At each observed open, turnover equals one half of the absolute change from drifted pre-trade security-plus-cash weights to target component weights. Cost equals pre-trade observed-open NAV multiplied by that turnover and the stated sensitivity. Units then drift until the next scheduled monthly rebalance.",
            "cost_model": "Per-one-way-turnover cost sensitivity only. It excludes verified fees, taxes, bid/ask, market impact, T+1, lots, halts, limits, settlement, no-fill and capacity.",
            "return_basis": "Observed public open-to-close and close-to-next-open market-price arithmetic inside a self-financing accounting model; no investor total-return interpretation is permitted.",
            "annual_metric_boundary": "Annual rows carry forward prior-session NAV. Initial and cutoff-year fragments are explicitly marked incomplete and are not used for a separate annual hurdle.",
        },
        "evaluation": {
            "common_panel_start": prices.index[0].date().isoformat(),
            "common_panel_end": prices.index[-1].date().isoformat(),
            "common_panel_sessions": len(prices),
            "daily_source_presence_status": presence_rows,
            "hypotheses": rows,
        },
        "prior_public_overlap_observation": prior_overlap,
        "decision": {
            "formal_strategy_status": "not_usable_q0",
            "apparent_arithmetic_candidates_at_20bps": candidates_with_arithmetic_hurdle,
            "reason": [
                "Any apparent public-series hurdle survivor is only a hypothesis for an entitled, point-in-time replay; it is not total-return, product-admission, allocation or action evidence.",
                "The candidate family must be judged together. Sensitivity to horizon, risk budget or breadth is evidence against treating a single public-series survivor as a stable return process.",
                "The public panel is a coverage-restricted, retrospective four-ETF observation with overlapping windows; it does not establish an out-of-sample holdout or open-universe result.",
                "UR01--UR05, U0 freeze, accepted data modules, formal replay, route/cost evidence and prospective paper reconciliation remain open.",
            ],
            "next_research_gate": "If H01 or any other hypothesis remains of interest after this screen, translate it into a class-neutral, pre-frozen U0-to-T2 rule and test it only after accepted licensed/PIT data and execution ledgers are available.",
        },
        "reference_primary_hypothesis": primary_candidate["hypothesis_id"],
    }


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# R2 扩展公开序列假设筛查 — 2026-08-14",
        "",
        "- 状态：**研究性筛查，不可用；`q=0`。**",
        f"- 输入：`{result['source']['path']}`（SHA-256 `{result['source']['sha256']}`）。",
        f"- 计算口径：`{MODEL_VERSION}`；月度调仓之间按单位、现金和收盘价自然漂移，并在每个既定月度执行日按漂移后权重重新计算单向换手。",
        "- 数据性质：公开聚合日线，价格调整、历史可得时间、基金事件、NAV/IOPV、停复牌/涨跌停、费用税费、盘口和成交均未获验证。",
        "- 因此，下面的数值只能称为“公开序列算术变化”，不是投资者总回报、历史回放结果或可执行策略表现。",
        "",
        "## 本轮脚本固定的假设族（非独立预注册）",
        "",
        "在完整回看期出现后的下一个自然月首个观测日，用此前一观测日可见的公开收盘价计算动量；目标在下一观测日开盘建立，并按当日收盘价计入首日变化。此后每一个既定月度执行日都将漂移后的单位和现金重新调至目标，即使入选袖套没有变化。风险比较袖套为 510300、510880、518880，防守比较袖套为 511010。若风险袖套的回看期公开序列变化为正，按相对动量选择前 N 个，并在既定风险预算内等权；其余映射至 511010。若没有合格风险袖套，则映射至 511010。",
        "",
        "该四只 ETF 只是覆盖受限的观察样本，绝不是开放 U0 总体、未来决策资产池或产品清单。20 bps 是按漂移后证券加现金权重计算的单向换手成本敏感性，并不代表经核验的费用、税费、价差或成交成本。",
        "",
        "| 假设 | 回看观测数 | 前 N 个 | 风险预算 | 20 bps 年化公开序列变化 | 最大回撤 | 5 年窗口低于 5% | 5 年窗口最小值 | 筛查解释 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in result["evaluation"]["hypotheses"]:
        metric = item["primary_20bps"]
        rolling = metric["rolling_five_year_public_series_diagnostic"]
        readout = "未被该算术门槛否定" if rolling["all_complete_windows_meet_5pct"] else "被该算术门槛否定"
        lines.append(
            "| {id} | {lookback} | {top_n} | {budget:.0%} | {annual:.2%} | {drawdown:.2%} | {below}/{count} | {minimum:.2%} | {readout} |".format(
                id=item["hypothesis_id"],
                lookback=item["lookback_observations"],
                top_n=item["top_n"],
                budget=item["risk_budget"],
                annual=metric["annualized_public_series_change"],
                drawdown=metric["maximum_drawdown"],
                below=rolling["windows_below_5pct"],
                count=rolling["window_count"],
                minimum=rolling["minimum_annualized_public_series_change"],
                readout=readout,
            )
        )
    lines.extend(
        [
            "",
        "## 读法与结论",
            "",
            f"在 20 bps 单向换手成本敏感性下，未被本次公开序列算术门槛否定的假设为：`{', '.join(result['decision']['apparent_arithmetic_candidates_at_20bps']) or '无'}`。这不是通过策略准入，而是后续可在合格数据包中继续研究的候选假设。",
            "",
            "## 与既有公开样本的重叠观察",
            "",
        ]
    )
    overlap = result["prior_public_overlap_observation"]
    if overlap["status"] == "descriptive_only_not_basis_validation":
        lines.extend(
            [
                "本轮扩展样本与既有冻结公开样本在重叠区间作了描述性对照。两者同为公开观察，对照不能验证复权、历史可得性或总回报；反而应把差异保留下来。",
                "",
                "| 代码 | 重叠观测数 | 最大收盘价绝对差 | 差异大于 0.001 的行数 | 差异大于 0.01 的行数 |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in overlap["rows"]:
            if row.get("status") == "no_overlap":
                lines.append(f"| {row['code']} | 0 | — | — | — |")
            else:
                lines.append(
                    "| {code} | {sessions} | {max_difference:.6f} | {above_small} | {above_large} |".format(
                        code=row["code"],
                        sessions=row["overlap_sessions"],
                        max_difference=row["max_absolute_close_difference"],
                        above_small=row["rows_above_0_001_difference"],
                        above_large=row["rows_above_0_01_difference"],
                    )
                )
        lines.extend(
            [
                "",
                "个别历史收盘观察存在可见差异；在缺少来源修订链和价格口径说明时，不能把它们自行抹平或解释为可交易结果。这正是本文件不把筛查数值升级为回放结论的原因之一。",
                "",
            ]
        )
    else:
        lines.extend(["既有公开样本在本次运行中不可读取，因此未做重叠观察。", ""])
    lines.extend(
        [
            "不能从单一候选的表面结果得出“稳定 5%”结论：回看期限、风险预算和持仓广度的小幅改变会给出不同的五年窗口表现；所有五年窗口高度重叠；样本只有四个公共价格序列；且没有独立样本外持有期。JSON 中逐日列出了来源是否呈现有效开收盘观察；没有权威交易日历时，未呈现行的原因只能标为未知。更根本的是，公开日线没有回答基金分配、复权、NAV/市价、交易状态、税费、T+1、价格限制、盘口、无成交和结算问题。",
            "",
            "所以本轮的有效研究成果是缩小下一轮检验对象，而非形成配置动作。只有当候选被转为类别中立、预冻结的 U0→T2 规则，并在获授权的时点化数据、完整事件账本和执行账本上通过正式回放与前瞻纸面核对后，才可重新讨论其是否可用。",
            "",
            "机器可读副本：[r2_public_series_extended_probe_20260814.json](r2_public_series_extended_probe_20260814.json)。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--capture",
        action="store_true",
        help="Capture a new raw observation only when this source batch does not yet exist.",
    )
    modes.add_argument(
        "--seal-existing-freeze",
        action="store_true",
        help="One-time explicit migration that adds source hash control to a pre-existing capture.",
    )
    modes.add_argument(
        "--refresh-derived",
        action="store_true",
        help="Validate a sealed source and refresh derived research artifacts without touching the source manifest.",
    )
    modes.add_argument(
        "--verify-only",
        action="store_true",
        help="Read and validate the sealed source and calculation without writing any artifact.",
    )
    args = parser.parse_args()
    if args.capture:
        if RAW_PATH.exists() or MANIFEST_JSON.exists():
            raise FileExistsError(
                "source batch already exists; use --refresh-derived or --verify-only, not --capture"
            )
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        raw = _fetch_raw_observation()
        _write_json(RAW_PATH, raw)
        manifest = _make_source_manifest(raw, seal_status="captured_with_hash_control")
        result = _result(raw, manifest)
        _write_json(OUTPUT_JSON, result)
        _write_text(OUTPUT_MD, _markdown(result))
    elif args.seal_existing_freeze:
        _seal_existing_freeze()
        print("R2 EXTENDED PUBLIC SERIES SOURCE FREEZE: PASS (explicit migration only)")
        return 0
    else:
        raw, manifest = _load_frozen_source()
        result = _result(raw, manifest)
        if args.refresh_derived:
            _write_json(OUTPUT_JSON, result)
            _write_text(OUTPUT_MD, _markdown(result))
    print(
        "R2 EXTENDED PUBLIC SERIES PROBE: PASS "
        "(sealed research-only public observation; no strategy admission, allocation or action)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
