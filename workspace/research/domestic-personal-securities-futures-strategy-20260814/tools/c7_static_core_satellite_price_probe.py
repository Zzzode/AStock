#!/usr/bin/env python3
"""Freeze and diagnose the fixed C7 static ETF core--satellite candidate.

This is deliberately a market-price-only research diagnostic.  It retains the
official SSE public daily-bar responses used by the calculation, but neither
the endpoint nor the calculation establishes adjusted total return, historic
availability, investor costs, product status or a fill.  It must not approve a
strategy or an external transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c7-static-etf-price-observation-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
OUTPUT_JSON = CASE_DIR / "analysis" / f"c7_static_core_satellite_price_diagnostic_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"c7_static_core_satellite_price_diagnostic_{DATE_TAG}.md"
DATA_CUTOFF = pd.Timestamp("2026-08-14")
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
SOURCE_QUALITY = "primary_official_public_retrospective_market_price_observation"
PROTOCOL_STATUS = "exploratory_post_observation_not_clean_preregistration"
ILLUSTRATIVE_ONE_WAY_COST_BPS = 20.0
REBALANCE_MONTHS = {3, 9}

# The six fixed sleeves are structural inputs, not the output of a price
# ranking.  C7 uses strategic bands; it does not inherit R5's absolute-
# momentum, positive-sleeve, fallback, or survivor-selection logic.
SLEEVES: tuple[dict[str, Any], ...] = (
    {
        "code": "510300",
        "name": "华泰柏瑞沪深300ETF",
        "role": "core_broad_equity",
        "target_weight": 0.30,
        "band_absolute_weight": 0.05,
        "exposure": "沪深300股票指数；完全复制",
        "dated_product_fact": "2025-11-24 product summary; management 0.15%/year, custody 0.05%/year, composite operating cost 0.20%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/510300_product_summary_20251124.pdf",
    },
    {
        "code": "510500",
        "name": "南方中证500ETF",
        "role": "satellite_size_equity",
        "target_weight": 0.10,
        "band_absolute_weight": 0.03,
        "exposure": "中证500股票指数；完全复制",
        "dated_product_fact": "2026-07-29 product summary; management 0.15%/year, custody 0.05%/year, composite operating cost 0.23%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/510500_product_summary_20260729.pdf",
    },
    {
        "code": "510880",
        "name": "华泰柏瑞上证红利ETF",
        "role": "satellite_dividend_equity",
        "target_weight": 0.10,
        "band_absolute_weight": 0.03,
        "exposure": "上证红利指数；完全复制",
        "dated_product_fact": "2026-06-19 product summary; management 0.50%/year, custody 0.10%/year, composite operating cost 0.60%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/510880_product_summary_20260619.pdf",
    },
    {
        "code": "511010",
        "name": "国泰上证5年期国债ETF",
        "role": "core_government_bond",
        "target_weight": 0.30,
        "band_absolute_weight": 0.05,
        "exposure": "上证5年期国债指数；优化抽样复制",
        "dated_product_fact": "2026-03-19 product summary; management 0.15%/year, custody 0.05%/year, composite operating cost 0.21%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/511010_product_summary_20260319.pdf",
    },
    {
        "code": "511990",
        "name": "华宝现金添益ETF（A类）",
        "role": "core_liquidity_sleeve",
        "target_weight": 0.10,
        "band_absolute_weight": 0.05,
        "exposure": "货币市场工具组合",
        "dated_product_fact": "2025-06-21 A-class product summary; management 0.35%/year, custody 0.09%/year, service fee 0.25%/year, composite operating cost 0.69%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/511990_product_summary_20250621.pdf",
    },
    {
        "code": "518880",
        "name": "华安黄金ETF",
        "role": "satellite_gold",
        "target_weight": 0.10,
        "band_absolute_weight": 0.03,
        "exposure": "境内黄金现货合约为主，目标紧密跟踪国内黄金现货价格",
        "dated_product_fact": "2026-03-17 product summary; management 0.50%/year, custody 0.10%/year, composite operating cost 0.67%/year",
        "fact_source": "sources/official-r4-candidate-etf-diligence-20260815/518880_product_summary_20260317.pdf",
    },
)
CODES = tuple(item["code"] for item in SLEEVES)
TARGET = pd.Series({item["code"]: item["target_weight"] for item in SLEEVES}, dtype=float)
BANDS = pd.Series({item["code"]: item["band_absolute_weight"] for item in SLEEVES}, dtype=float)
R4_DILIGENCE = CASE_DIR / "analysis" / "r4_candidate_etf_diligence_20260815.md"
R4_MANIFEST = CASE_DIR / "sources" / "official-r4-candidate-etf-diligence-20260815" / "manifest.json"
SSE_ETF_FAQ = CASE_DIR / "sources" / "official-r4-candidate-etf-diligence-20260815" / "sse_etf_faq_20260815.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (C7 research evidence capture)",
    "Referer": "https://www.sse.com.cn/assortment/fund/etf/price/",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
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


def _runtime_provenance() -> dict[str, str]:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
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
        "numpy_version": np.__version__,
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _url(code: str) -> str:
    return (
        f"https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{code}?callback=c7probe"
        "&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000"
    )


def _raw_path(code: str) -> Path:
    return RAW_DIR / f"sse_etf_dayk_{code}_begin0_end5000.jsonp"


def _parse_jsonp(raw: bytes, code: str) -> dict[str, Any]:
    decoded = raw.decode("utf-8")
    match = re.fullmatch(r"c7probe\((.*)\)", decoded, flags=re.DOTALL)
    if not match:
        raise ValueError(f"SSE response for {code} is not expected JSONP")
    payload = json.loads(match.group(1))
    if str(payload.get("code")) != code:
        raise ValueError(f"SSE response code mismatch for {code}")
    if int(payload.get("begin", -1)) != 0:
        raise ValueError(f"SSE response begin mismatch for {code}")
    rows = payload.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SSE response has no kline rows for {code}")
    if len(rows) != int(payload.get("total", -1)):
        raise ValueError(f"SSE response is incomplete for {code}: {len(rows)} != {payload.get('total')}")
    if int(payload.get("end", -1)) != len(rows):
        raise ValueError(f"SSE response effective end mismatch for {code}")
    return payload


def _load_responses() -> dict[str, dict[str, Any]]:
    responses: dict[str, dict[str, Any]] = {}
    for code in CODES:
        path = _raw_path(code)
        if not path.is_file():
            raise FileNotFoundError(f"retained C7 source is absent: {path}")
        responses[code] = _parse_jsonp(path.read_bytes(), code)
    return responses


def _capture_responses() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    if MANIFEST_JSON.exists() or any(_raw_path(code).exists() for code in CODES):
        raise FileExistsError("C7 source batch already exists; use --refresh-derived or --verify-only")
    raw: dict[str, bytes] = {}
    retrieval: dict[str, str] = {}
    for code in CODES:
        response = requests.get(_url(code), headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"SSE request failed for {code}: HTTP {response.status_code}")
        _parse_jsonp(response.content, code)
        raw[code] = response.content
        retrieval[code] = datetime.now(timezone.utc).isoformat()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for code in CODES:
        _raw_path(code).write_bytes(raw[code])
    return _load_responses(), retrieval


def _dependency_record(path: Path, role: str, purpose: str, limitations: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required C7 evidence dependency is absent: {path}")
    return {
        **_file_record(path),
        "dependency_role": role,
        "source_quality": "case_local_primary_or_derived_reference",
        "purpose": purpose,
        "limitations": limitations,
    }


def _make_manifest(
    responses: dict[str, dict[str, Any]], retrieval: dict[str, str]
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for code in CODES:
        payload = responses[code]
        rows.append(
            {
                **_file_record(_raw_path(code)),
                "code": code,
                "publisher": "Shanghai Stock Exchange",
                "title": f"SSE ETF daily market-price response for {code}",
                "url": _url(code),
                "referer": HEADERS["Referer"],
                "document_date": "retrospective response captured 2026-08-15",
                "retrieved_at": retrieval[code],
                "format": "jsonp",
                "response_total": int(payload["total"]),
                "response_rows": len(payload["kline"]),
                "first_trade_date": str(payload["kline"][0][0]),
                "last_trade_date": str(payload["kline"][-1][0]),
                "capture_note": "Official retrospective daily market-price response. It does not disclose adjustment basis, historic available_at, NAV/IOPV, distributions, corporate actions, market status, depth, cost, entitlement or execution.",
            }
        )
    dependencies = [
        _dependency_record(
            R4_DILIGENCE,
            "dated_product_fact_reference",
            "Provides first-party product-structure, fee and risk references for C7's fixed sleeves.",
            "It is a dated representative diligence pack, not current product admission, trading availability, allocation approval or performance evidence.",
        ),
        _dependency_record(
            R4_MANIFEST,
            "primary_document_provenance_reference",
            "Provides hashes and first-party URLs for the six dated product-summary documents.",
            "It does not make product terms current after their document dates or establish personal access and execution.",
        ),
        _dependency_record(
            SSE_ETF_FAQ,
            "category_mechanics_reference",
            "Provides category-level secondary-market lot/tick and round-trip context used only as a pre-action recheck prompt.",
            "It is not product-specific or broker-specific execution confirmation.",
        ),
    ]
    captured_at = min(retrieval.values())
    manifest = {
        "schema_version": "c7_static_etf_price_observation_manifest.v1",
        "case_id": CASE_DIR.name,
        "capture_batch": RAW_DIR.name,
        "captured_at": captured_at,
        "purpose": "Frozen official SSE public daily market-price observation for a fixed, static C7 core--satellite ETF candidate. This is a research-only price diagnostic; it cannot establish investor total return, strategy feasibility, product admission, allocation, holding or action.",
        "source_quality": SOURCE_QUALITY,
        "protocol_status": PROTOCOL_STATUS,
        "files": rows,
        "dependencies": dependencies,
        "limitations": [
            "Historical records were retrieved retrospectively and do not prove original-date availability or revisions.",
            "The endpoint does not state adjustment basis and has no distribution, corporate-action, NAV/IOPV, trading-status, tax, cost, spread, depth, no-fill, settlement or account-permission ledger.",
            "A public endpoint does not establish data-use entitlement or an independently reviewable formal replay dataset.",
            "C7's fixed static allocation was documented after related public ETF observations existed elsewhere in the case; this is not a clean preregistration and cannot turn a positive diagnostic into independent strategy evidence.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "case_local_hash_control_only",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": [{key: row[key] for key in ("path", "bytes", "sha256")} for row in rows],
            "runtime_provenance": _runtime_provenance(),
            "boundary": "This detects a local raw-file mismatch only. It is not external notarization, data entitlement, PIT evidence, total-return evidence or execution evidence.",
        },
    }
    _write_json(MANIFEST_JSON, manifest)
    table = "\n".join(
        f"| {row['code']} | {row['response_rows']} / {row['response_total']} | {row['first_trade_date']} | {row['last_trade_date']} | `{row['sha256']}` |"
        for row in rows
    )
    _write_text(
        MANIFEST_MD,
        f"""# C7 Static ETF Price-Observation Manifest

- Batch: `{RAW_DIR.name}`
- Capture time: `{captured_at}`
- Method: read-only anonymous HTTPS requests to SSE's public daily-price endpoint; no credentials, account access, data purchase, bypass or trading action.
- Protocol status: `{PROTOCOL_STATUS}`.
- Boundary: these are retrospectively retrieved official market-price bars. They do **not** prove historic availability, adjustment basis, total return, distributions, events, NAV/IOPV, current product state, data entitlement, costs, tradability, settlement, broker route, account permission or fills.

| Code | Rows / reported total | First date | Last date | SHA-256 |
|---|---:|---|---|---|
{table}

The request uses `begin=0&end=5000`; the returned response reports that every
retained code's full available response fits within that range. This proves
only response completeness as declared by the endpoint at capture, not a
complete historical investor-return or execution ledger.
""",
    )
    return manifest


def _validate_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.is_file():
        raise FileNotFoundError(f"C7 manifest absent: {MANIFEST_JSON}")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    by_path = {row.get("path"): row for row in manifest.get("files", [])}
    freeze_paths = {row.get("path"): row for row in manifest.get("source_freeze", {}).get("frozen_files", [])}
    expected_paths = {_repo_relative(_raw_path(code)) for code in CODES}
    if set(by_path) != expected_paths or set(freeze_paths) != expected_paths:
        raise ValueError("C7 manifest/freeze path set does not match fixed sleeve source set")
    for path_key in expected_paths:
        entry = by_path[path_key]
        path = REPO_ROOT / path_key
        if not path.is_file() or path.stat().st_size != int(entry["bytes"]) or _sha256(path) != entry["sha256"]:
            raise ValueError(f"C7 raw source mismatch: {path_key}")
        frozen = freeze_paths[path_key]
        if {key: frozen.get(key) for key in ("path", "bytes", "sha256")} != {key: entry.get(key) for key in ("path", "bytes", "sha256")}:
            raise ValueError(f"C7 freeze entry mismatch: {path_key}")
    for dependency in manifest.get("dependencies", []):
        path = REPO_ROOT / str(dependency.get("path", ""))
        if not path.is_file() or path.stat().st_size != int(dependency.get("bytes", -1)) or _sha256(path) != dependency.get("sha256"):
            raise ValueError(f"C7 evidence dependency mismatch: {path}")
    return manifest


def _load_prices() -> pd.DataFrame:
    responses = _load_responses()
    series: dict[str, pd.Series] = {}
    for code, payload in responses.items():
        frame = pd.DataFrame(payload["kline"], columns=["date", "open", "high", "low", "close", "volume"])
        # SSE encodes calendar dates as numeric-looking YYYYMMDD values.  A
        # direct pandas conversion treats those values as nanoseconds; convert
        # through an integer string and require the explicit calendar format.
        numeric_dates = pd.to_numeric(frame["date"], errors="coerce")
        frame["date"] = pd.to_datetime(
            numeric_dates.round().astype("Int64").astype(str),
            format="%Y%m%d",
            errors="coerce",
        )
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["date", "close"]).sort_values("date", kind="stable")
        if frame.empty or frame["date"].duplicated().any() or (frame["close"] <= 0).any():
            raise ValueError(f"invalid price rows for {code}")
        series[code] = frame.set_index("date")["close"]
    panel = pd.concat(series, axis=1, sort=True).dropna().sort_index()
    panel = panel.loc[:DATA_CUTOFF]
    if panel.empty or tuple(panel.columns) != CODES:
        raise ValueError("C7 common price panel is missing a fixed sleeve")
    if panel.index.duplicated().any() or (panel <= 0).any().any():
        raise ValueError("C7 common price panel is invalid")
    return panel


def _effective_rebalance_positions(index: pd.DatetimeIndex) -> set[int]:
    positions: set[int] = set()
    for position in range(1, len(index)):
        previous = index[position - 1]
        current = index[position]
        if previous.month in REBALANCE_MONTHS and current.month != previous.month:
            positions.add(position)
    return positions


def _simulate(prices: pd.DataFrame) -> tuple[pd.Series, list[dict[str, Any]], pd.DataFrame]:
    values = TARGET.copy()
    nav_rows = [(prices.index[0], float(values.sum()))]
    weights_rows = [(prices.index[0], *(float(values[code] / values.sum()) for code in CODES))]
    events: list[dict[str, Any]] = []
    positions = _effective_rebalance_positions(prices.index)
    cost_rate = ILLUSTRATIVE_ONE_WAY_COST_BPS / 10_000.0
    for position in range(1, len(prices)):
        session = prices.index[position]
        if position in positions:
            pre_trade_nav = float(values.sum())
            drifted = values / pre_trade_nav
            deviations = drifted - TARGET
            trigger_codes = [code for code in CODES if abs(float(deviations[code])) > float(BANDS[code])]
            event: dict[str, Any] = {
                "decision_session": prices.index[position - 1].date().isoformat(),
                "effective_session": session.date().isoformat(),
                "information_through": prices.index[position - 1].date().isoformat(),
                "target_weights": {code: float(TARGET[code]) for code in CODES},
                "pre_trade_weights": {code: float(drifted[code]) for code in CODES},
                "band_absolute_weight": {code: float(BANDS[code]) for code in CODES},
                "trigger_codes": trigger_codes,
                "rebalanced": bool(trigger_codes),
                "one_way_turnover": 0.0,
                "illustrative_cost_fraction_of_pre_trade_nav": 0.0,
            }
            if trigger_codes:
                turnover = float((drifted - TARGET).abs().sum() / 2.0)
                cost = pre_trade_nav * turnover * cost_rate
                values = TARGET * (pre_trade_nav - cost)
                event["one_way_turnover"] = turnover
                event["illustrative_cost_fraction_of_pre_trade_nav"] = cost / pre_trade_nav
            events.append(event)
        ratios = prices.iloc[position] / prices.iloc[position - 1]
        values = values * ratios
        nav_rows.append((session, float(values.sum())))
        weights = values / float(values.sum())
        weights_rows.append((session, *(float(weights[code]) for code in CODES)))
    nav = pd.Series({date: value for date, value in nav_rows}, dtype=float).sort_index()
    weight_frame = pd.DataFrame(weights_rows, columns=["date", *CODES]).set_index("date")
    return nav, events, weight_frame


def _complete_year_metrics(nav: pd.Series) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    terminal_year = int(nav.index[-1].year)
    for year in sorted(set(int(value) for value in nav.index.year)):
        group = nav.loc[nav.index.year == year]
        months = sorted(set(int(value) for value in group.index.month))
        complete = year < terminal_year and months == list(range(1, 13))
        # A complete calendar-year return starts from the last observation
        # immediately before that year.  Using the first in-year close would
        # silently omit the first trading-session return.
        prior = nav.loc[nav.index < group.index[0]]
        if complete and prior.empty:
            raise ValueError(f"complete calendar year lacks a prior observation: {year}")
        start_value = float(prior.iloc[-1]) if complete else float(group.iloc[0])
        change = float(group.iloc[-1] / start_value - 1.0)
        rows.append(
            {
                "year": year,
                "start": group.index[0].date().isoformat(),
                "end": group.index[-1].date().isoformat(),
                "months_present": months,
                "complete_calendar_year": complete,
                "market_price_unitized_change": change,
                "at_or_above_5pct_market_price_diagnostic": bool(change >= 0.05),
            }
        )
    return rows


def _assert_complete_year_return_includes_first_session() -> None:
    """Guard against dropping the first return of a complete calendar year."""

    nav = pd.Series(
        [1.0, *np.linspace(1.1, 1.32, 12), 1.4],
        index=pd.to_datetime(
            [
                "2024-12-31",
                "2025-01-02",
                *pd.date_range("2025-02-28", "2025-12-31", freq="ME").tolist(),
                "2026-01-02",
            ]
        ),
        dtype=float,
    )
    rows = _complete_year_metrics(nav)
    row_2025 = next(row for row in rows if row["year"] == 2025)
    expected = 1.32 / 1.0 - 1.0
    if not row_2025["complete_calendar_year"] or abs(float(row_2025["market_price_unitized_change"]) - expected) > 1e-12:
        raise AssertionError("complete-year metric omitted the first in-year session return")


def _rolling_five_year_metrics(nav: pd.Series) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for end_position, end_date in enumerate(nav.index):
        eligible = nav.index[: end_position + 1][nav.index[: end_position + 1] <= end_date - pd.DateOffset(years=5)]
        if len(eligible) == 0:
            continue
        start_date = eligible[-1]
        days = int((end_date - start_date).days)
        if days < 1820:
            continue
        value = float((nav.loc[end_date] / nav.loc[start_date]) ** (365.25 / days) - 1.0)
        rows.append(
            {
                "start": start_date.date().isoformat(),
                "end": end_date.date().isoformat(),
                "calendar_days": days,
                "annualized_market_price_unitized_change": value,
                "at_or_above_5pct_market_price_diagnostic": value >= 0.05,
            }
        )
    if not rows:
        return {"window_count": 0, "rows": [], "warning": "No 5-year common-panel windows."}
    values = [float(row["annualized_market_price_unitized_change"]) for row in rows]
    return {
        "window_count": len(rows),
        "at_or_above_5pct_count": sum(value >= 0.05 for value in values),
        "below_5pct_count": sum(value < 0.05 for value in values),
        "minimum_annualized_market_price_unitized_change": min(values),
        "maximum_annualized_market_price_unitized_change": max(values),
        "rows": rows,
        "warning": "Overlapping end points are descriptive and not independent observations. This is an unadjusted-or-undisclosed market-price diagnostic, not a total-return test.",
    }


def _results(prices: pd.DataFrame, manifest: dict[str, Any]) -> dict[str, Any]:
    nav, events, weights = _simulate(prices)
    elapsed_days = int((nav.index[-1] - nav.index[0]).days)
    daily_changes = nav.pct_change().fillna(0.0)
    complete_years = _complete_year_metrics(nav)
    complete_rows = [row for row in complete_years if row["complete_calendar_year"]]
    rolling = _rolling_five_year_metrics(nav)
    total_turnover = sum(float(event["one_way_turnover"]) for event in events)
    max_drawdown = float((nav / nav.cummax() - 1.0).min())
    final_weights = {code: float(weights.iloc[-1][code]) for code in CODES}
    return {
        "schema_version": "c7_static_core_satellite_price_diagnostic.v1",
        "case_id": CASE_DIR.name,
        "artifact_class": "derived_research_evidence",
        "artifact_id": "DPSFS-C7-STATIC-PRICE-v1",
        "as_of": DATA_CUTOFF.date().isoformat(),
        "status": "market_price_diagnostic_not_total_return_or_execution_evidence",
        "research_only": True,
        "formal_decision_eligible": False,
        "portfolio_q": 0,
        "protocol_status": PROTOCOL_STATUS,
        "candidate_definition": {
            "name": "C7 fixed strategic ETF core--satellite candidate",
            "distinct_from_r5": [
                "C7 is a constant strategic allocation with semiannual drift bands, not absolute momentum.",
                "C7 has no positive-sleeve gating, relative ranking, defensive fallback or parameter-survivor logic.",
                "C7 adds a fixed CSI 500 sleeve and retains all sleeves structurally; it does not select them from R5 results.",
            ],
            "long_run_research_target": "5% annualized is a research objective only, never a guarantee, floor, prediction or suitability result.",
            "fixed_sleeves": list(SLEEVES),
            "weight_sum": float(TARGET.sum()),
        },
        "source": {
            "manifest_path": _repo_relative(MANIFEST_JSON),
            "manifest_sha256": _sha256(MANIFEST_JSON),
            "quality": SOURCE_QUALITY,
            "price_basis": "SSE endpoint does not disclose an adjustment basis; market price is not independently established as investor total return.",
            "common_panel": {
                "observations": int(len(prices)),
                "first_session": prices.index[0].date().isoformat(),
                "last_session": prices.index[-1].date().isoformat(),
                "raw_response_total_rows": {code: int(json.loads(_raw_path(code).read_text(encoding="utf-8")[8:-1]).get("total")) for code in CODES},
            },
        },
        "derived_runtime_provenance": _runtime_provenance(),
        "fixed_diagnostic_rule": {
            "starting_unitized_value": 1.0,
            "signal_or_selection": "none; all six sleeves exist structurally from the initial common session",
            "review_frequency": "After the final common close in March and September; any action becomes effective on the following common session.",
            "trade_trigger": "Rebalance only when at least one sleeve exceeds its fixed absolute target-weight band.",
            "cost_load": {
                "one_way_turnover_bps": ILLUSTRATIVE_ONE_WAY_COST_BPS,
                "meaning": "A fixed arithmetic load only; it is not an observed broker fee, tax, spread, impact, settlement or fill model.",
            },
            "not_modelled": [
                "distributions", "fund events", "corporate actions", "market-price adjustment basis", "NAV/IOPV", "premium_discount", "halt", "price_limit", "lots", "bid_ask", "depth", "partial_fill", "no_fill", "broker_fee", "tax", "settlement", "account_permission",
            ],
        },
        "arithmetic_output": {
            "initial_common_session": nav.index[0].date().isoformat(),
            "terminal_common_session": nav.index[-1].date().isoformat(),
            "common_sessions": int(len(prices)),
            "final_unitized_market_price_value": float(nav.iloc[-1]),
            "annualized_market_price_unitized_change": float(nav.iloc[-1] ** (365.25 / elapsed_days) - 1.0),
            "annualized_market_price_unitized_volatility": float(daily_changes.std(ddof=1) * np.sqrt(252.0)),
            "maximum_drawdown": max_drawdown,
            "review_events": len(events),
            "triggered_rebalances": sum(bool(event["rebalanced"]) for event in events),
            "aggregate_one_way_turnover": total_turnover,
            "complete_calendar_years": complete_years,
            "complete_calendar_year_summary": {
                "count": len(complete_rows),
                "at_or_above_5pct_count": sum(bool(row["at_or_above_5pct_market_price_diagnostic"]) for row in complete_rows),
                "below_5pct_count": sum(not bool(row["at_or_above_5pct_market_price_diagnostic"]) for row in complete_rows),
            },
            "rolling_five_year": rolling,
            "terminal_weights_after_last_price_move": final_weights,
        },
        "interpretation": {
            "historical_5pct_verdict": "not_adjudicated",
            "why": [
                "The endpoint's price adjustment basis is not stated, and it has no synchronized distribution or fund-event ledger; the arithmetic cannot be called investor total return.",
                "Historical rows are retrospectively retrieved, not point-in-time available-at evidence.",
                "No market-status, bid/ask, depth, broker fee, tax, settlement, account-permission, partial-fill or no-fill record exists, so the arithmetic cannot establish personal operability.",
                "The protocol is exploratory after related ETF public observations existed, so a positive arithmetic result would not be independent strategy evidence.",
            ],
            "allowed_use": "Identify whether this fixed candidate deserves a separately frozen, entitled total-return-and-execution test; it cannot authorize a holding, a trade, a target-return claim or a final strategy.",
        },
    }


def _markdown(result: dict[str, Any]) -> str:
    output = result["arithmetic_output"]
    rolling = output["rolling_five_year"]
    sleeves = result["candidate_definition"]["fixed_sleeves"]
    sleeve_rows = "\n".join(
        f"| {item['code']} {item['name']} | {item['role']} | {item['target_weight']:.0%} | ±{item['band_absolute_weight']:.0%} | {item['exposure']} |"
        for item in sleeves
    )
    years = "\n".join(
        f"| {row['year']} | {row['start']} | {row['end']} | {'是' if row['complete_calendar_year'] else '否'} | {row['market_price_unitized_change']:.2%} | {'是' if row['at_or_above_5pct_market_price_diagnostic'] else '否'} |"
        for row in output["complete_calendar_years"]
    )
    trigger_events = [row for row in output["rolling_five_year"].get("rows", []) if not row["at_or_above_5pct_market_price_diagnostic"]]
    rolling_summary = (
        "无完整滚动五年窗口。"
        if rolling["window_count"] == 0
        else f"共有 {rolling['window_count']} 个重叠滚动五年终点；其中 {rolling['at_or_above_5pct_count']} 个价格代理年化不低于 5%，{rolling['below_5pct_count']} 个低于 5%，范围 {rolling['minimum_annualized_market_price_unitized_change']:.2%} 至 {rolling['maximum_annualized_market_price_unitized_change']:.2%}。"
    )
    lower_example = "无" if not trigger_events else f"例如 {trigger_events[0]['start']} 至 {trigger_events[0]['end']}。"
    return f"""# C7：静态核心—卫星 ETF 候选及官方市场价格诊断 — 2026-08-15

- 工件 ID：`{result['artifact_id']}`
- 状态：`{result['status']}`；`portfolio_q=0`
- 研究目标：探索一套个人可理解、只用境内场内 ETF 的长期 **5% 年化目标** 候选。5% 不是承诺、下限、预测或适当性结论。
- 关键结论：本文件给出了明确的候选篮子、权重和条件化操作规则，但当前仍**不是可启用策略**。历史计算只有上交所回溯公开市场价，不能证明投资者总回报或成交结果；本轮不会把任何数字写成“稳定 5%”。

## 1. 与 R5 的分离

C7 不是 R5 的参数延伸或幸存者选择：它从一开始是六个固定袖套的战略配置，半年只在偏离带触发时恢复固定权重；没有绝对动量、横截面排名、正信号筛选、防守替代或参数搜索。新增中证500袖套也不是根据 R5 表现挑选。因在写定 C7 前本案例已存在相关公开 ETF 观察，C7 只能标为 `{result['protocol_status']}`；即使价格算术为正，也不能当作独立样本外证据。

## 2. 候选篮子与产品尽调边界

| 产品 | 功能 | 静态目标权重 | 偏离带 | 经核验的暴露描述（仅在资料日期有效） |
|---|---|---:|---:|---|
{sleeve_rows}

六只产品的管理人、结构、上市历史、复制方式、资料概要费用与风险已由同案一手资料固化在 [R4 产品尽调](r4_candidate_etf_diligence_20260815.md)。其中费用是基金披露费用，**不是**个人实际佣金、税费、点差或净结果；资料概要日期后也必须复核公告、完整法律文件和产品状态。

经济结构是：50% 中国股票（30% 沪深300、10% 中证500、10% 上证红利）、30% 五年期国债、10% 黄金、10% 货币市场工具。它意在避免只押单一权益风格，但没有证明这些袖套在压力期独立、会抵消损失或足以实现任何收益门槛。

## 3. 条件化、可复核的操作规则

这是一套**若且仅若前置门槛全部通过**才可进入纸面或个人执行准备的规则书；不是让读者现在下单。

1. 每年 3 月和 9 月最后一个共同交易收盘后，以经核验的持仓、当日可交易市场价和真实费用计算实际权重；计划最早在下一共同交易日生效。任何产品停牌、终止、重大条款变更、无有效报价、权限不明或数据缺失，均不假设可以交易。
2. 当任一核心袖套（510300、511010、511990）偏离目标超过 ±5 个百分点，或任一卫星袖套（510500、510880、518880）偏离超过 ±3 个百分点，才按目标权重回到上述六项配置；否则不交易。卖出超配，再买入低配，不能用未结算卖出款或同日买入的股票 ETF 份额假设可用。
3. 每只订单均须先通过：当日产品状态、账户权限、券商费率、100 份最小申报单位和 0.001 元最小价格变动单位的最新产品/券商核验。上交所 FAQ 只提供类别层面的提示，不等于个别产品或账户确认。
4. 仅使用限价单。若可取得官方/券商发布的 IOPV，买入时只有当显示最优卖价不高于 IOPV 的 100.3% 才能提交，卖出时只有当显示最优买价不低于 IOPV 的 99.7% 才能提交；IOPV、最优报价、费用或状态任一缺失则该腿跳过并记录为 `no_action`。这些 30bp 只是价格保护规则，不是已验证的点差或成交保证。
5. 股票 ETF 的类别性 T+1 提示意味着不得把当日新买份额计作当日可卖；债券、黄金、货币 ETF 的类别性 T+0 描述亦必须由当前产品和券商逐只核验。部分成交、未成交、撤单、价格限制、停牌及结算失败都必须记录，不能用更有利的收盘价补写。

### 风险/失效规则

- 若单位化组合相对经核验高水位的回撤达到 12%，在下一次例行再平衡前形成独立复核记录；该审查不改变固定目标权重或偏离带，也不是经过历史验证的止损或择时信号。若所需核验未通过，则记为 `no_action`。
- 若任一基金发生终止、停牌、跟踪目标/复制方法/费用的重大变更，或个人账户/券商不再确认可交易，立即将该袖套降为 `not_actionable`，不得自动用相近产品替换。
- 若未来获权的 PIT 总回报与执行账本对 C7 固定规则显示完整自然年或滚动五年未达到研究门槛，C7 被否决，不能继续通过调权、调带或事后换产品寻找幸存者。

## 4. 官方市场价格诊断（受限、不可当作回报）

原始响应：[{RAW_DIR.name}/manifest.md](../sources/{RAW_DIR.name}/manifest.md)。上交所历史价格响应的共同面板从 {output['initial_common_session']} 至 {output['terminal_common_session']}，共 {output['common_sessions']} 个共同交易日。为避免零成本错觉，半年偏离带调仓按单边换手固定计入 {ILLUSTRATIVE_ONE_WAY_COST_BPS:.0f}bp 算术载荷；它不是实际费率、税费、点差、冲击、结算或成交模型。

市场价单位化算术的期末值为 {output['final_unitized_market_price_value']:.4f}，年化变化为 {output['annualized_market_price_unitized_change']:.2%}，最大回撤为 {output['maximum_drawdown']:.2%}；共 {output['review_events']} 次例行检查，{output['triggered_rebalances']} 次触发调仓，累计单边换手 {output['aggregate_one_way_turnover']:.2f}。这些是**未确认调整基准的价格算术**，不是总回报，也不是建议。

| 年度 | 起点 | 终点 | 完整自然年 | 市场价单位化变化 | 价格诊断 ≥5% |
|---:|---|---|---|---:|---|
{years}

{rolling_summary} {lower_example}

上述“≥5%”列仅描述这个未调整/口径未知价格代理与研究线的数值关系，绝不构成稳定 5% 的通过、失败或反证。分派、基金事件、复权口径、NAV/IOPV、税费、市场状态、深度、未成交、实际费率和个人账户权限均缺失；负值不能否定投资者总回报，正值也不能支持它。

## 5. 从候选到可使用策略的缺口

| 必经门槛 | 当前状态 | 允许的下一步 |
|---|---|---|
| 六只产品的一手结构/费用/风险资料 | 有日期的代表性资料已核验 | 每次行动前重核现行文件与公告 |
| 历史 PIT 总回报、分派/公司行动与版本链 | 缺失 | 取得有留存、派生、复核权的数据后，冻结再测固定 C7 |
| 当日市场状态、IOPV、报价、深度、费用、税费、结算、部分成交/未成交 | 缺失 | 由实际券商与可审计市场数据建立纸面订单账本 |
| 个人账户适当性、产品权限和订单路由 | 未验证 | 由经营机构和用户账户在行动前确认；本研究不推定 |
| 独立复算与前瞻纸面记录 | 未开始 | 规则冻结后先做不少于六个月的前瞻纸面核对 |

因此，C7 已把“投资什么、按什么权重、何时检查、怎样处理价格保护和失效”具体化；但在这些门槛关闭前，它的准确定位仍是**待验证的个人 ETF 配置候选**，不是已经可用的稳定收益策略，更不包含外部交易动作。
"""


def _write_outputs(result: dict[str, Any]) -> None:
    _write_json(OUTPUT_JSON, result)
    _write_text(OUTPUT_MD, _markdown(result))


def _validate_result(result: dict[str, Any]) -> None:
    if result.get("status") != "market_price_diagnostic_not_total_return_or_execution_evidence":
        raise ValueError("C7 result status was weakened")
    if result.get("portfolio_q") != 0 or result.get("formal_decision_eligible") is not False:
        raise ValueError("C7 result must remain research-only and q=0")
    if abs(float(result["candidate_definition"]["weight_sum"]) - 1.0) > 1e-12:
        raise ValueError("C7 target weights must sum to 1")
    if result.get("protocol_status") != PROTOCOL_STATUS:
        raise ValueError("C7 protocol status differs")
    if result["interpretation"].get("historical_5pct_verdict") != "not_adjudicated":
        raise ValueError("C7 must not adjudicate the 5% objective from price data")


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--capture", action="store_true")
    modes.add_argument("--refresh-derived", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if args.capture:
        responses, retrieval = _capture_responses()
        _make_manifest(responses, retrieval)
    _assert_complete_year_return_includes_first_session()
    manifest = _validate_manifest()
    prices = _load_prices()
    result = _results(prices, manifest)
    _validate_result(result)
    if args.verify_only:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            raise FileNotFoundError("C7 derived outputs are absent")
        retained = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        _validate_result(retained)
        if retained != result:
            raise ValueError("C7 derived JSON differs from deterministic recomputation")
        expected_md = _markdown(result)
        if OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
            raise ValueError("C7 derived Markdown differs from deterministic recomputation")
        print("C7 STATIC PRICE DIAGNOSTIC: PASS")
        return 0
    _write_outputs(result)
    print(f"C7 STATIC PRICE DIAGNOSTIC: wrote {OUTPUT_JSON.name} and {OUTPUT_MD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
