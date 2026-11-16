#!/usr/bin/env python3
"""Capture C8 first-party product/price evidence and replay the frozen price proxy.

This tool is intentionally case-local.  It does not place orders, access an
account, infer fund total return, or turn an exploratory proxy into an action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
RAW_DIR = CASE_DIR / "sources" / "c8-official-product-and-price-20260815"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
PROTOCOL_JSON = CASE_DIR / "analysis" / "c8_convertible_bond_etf_fixed_allocation_protocol_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.md"

ASSETS = OrderedDict(
    [
        ("511180", 0.50),
        ("511380", 0.25),
        ("511010", 0.25),
    ]
)
PRICE_REFERER = "https://www.sse.com.cn/assortment/fund/etf/price/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (C8 research evidence capture; read-only)",
    "Referer": PRICE_REFERER,
}
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
PRICE_SOURCE_QUALITY = "primary_official_public_retrospective_market_price_observation"
DATA_CUTOFF = "2026-08-15"

DOCUMENTS: tuple[dict[str, str], ...] = (
    {
        "filename": "511180_product_summary_20250324.pdf",
        "publisher": "Shanghai Stock Exchange / Haifutong Fund Management",
        "title": "Haifutong SSE Investment Grade Convertible Bond and Exchangeable Bond ETF product summary",
        "document_date": "2025-03-24",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2025-03-24/511180_20250324_Q0MJ.pdf",
        "format": "pdf",
    },
    {
        "filename": "511380_product_summary_20260626.pdf",
        "publisher": "Shanghai Stock Exchange / Bosera Fund Management",
        "title": "Bosera CSI Convertible Bond and Exchangeable Bond ETF product summary",
        "document_date": "2026-06-26",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2026-06-26/511380_20260626_CZVM.pdf",
        "format": "pdf",
    },
    {
        "filename": "511010_product_summary_20260319.pdf",
        "publisher": "Shanghai Stock Exchange / Guotai Fund Management",
        "title": "Guotai SSE 5-Year Treasury Bond ETF product summary",
        "document_date": "2026-03-19",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2026-03-19/511010_20260319_W8OE.pdf",
        "format": "pdf",
    },
    {
        "filename": "sse_950041_investment_grade_cb_methodology.pdf",
        "publisher": "Shanghai Stock Exchange / China Securities Index",
        "title": "SSE Investment Grade Convertible Bond and Exchangeable Bond Index Methodology",
        "document_date": "2026-04-30",
        "url": "https://www.sse.com.cn/market/sseindex/diclosure/c/10077961/files/32babf7875d24556aaf62d3c8d9eb015.pdf",
        "format": "pdf",
    },
    {
        "filename": "csi_931078_convertible_exchangeable_factsheet_20260130.pdf",
        "publisher": "China Securities Index",
        "title": "CSI Convertible Bond and Exchangeable Bond Index factsheet",
        "document_date": "2026-01-30",
        "url": "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/931078factsheet.pdf",
        "format": "pdf",
    },
    {
        "filename": "sse_bond_etf_guide_20200722.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "Shanghai Stock Exchange Bond ETF Business Guide",
        "document_date": "2020-07-22",
        "url": "https://www.sse.com.cn/lawandrules/guide/jjznlc/c/c_20200722_3986154.shtml",
        "format": "html",
    },
    {
        "filename": "sse_etf_faq_20260815.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "ETF Investor FAQ",
        "document_date": "2026-08-15",
        "url": "https://www.sse.com.cn/assortment/fund/etf/question/",
        "format": "html",
    },
    {
        "filename": "sse_convertible_redemption_index_rule_20190906.html",
        "publisher": "Shanghai Stock Exchange / China Securities Index",
        "title": "Temporary index adjustment rule for convertible and exchangeable bond redemption announcements",
        "document_date": "2019-09-06",
        "url": "https://www.sse.com.cn/market/sseindex/diclosure/c/c_20190906_4911303.shtml",
        "format": "html",
    },
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": _repo_relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write(path, (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_text(path: Path, text: str) -> None:
    _atomic_write(path, text.encode("utf-8"))


def _price_url(code: str) -> str:
    return (
        f"https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{code}?callback=c8probe"
        "&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000"
    )


def _price_filename(code: str) -> str:
    return f"sse_etf_dayk_{code}_begin0_end5000.jsonp"


def _parse_jsonp(content: bytes, code: str) -> dict[str, Any]:
    text = content.decode("utf-8")
    matched = re.fullmatch(r"c8probe\((.*)\)", text, flags=re.DOTALL)
    if not matched:
        raise ValueError(f"SSE response for {code} is not expected JSONP")
    payload = json.loads(matched.group(1))
    if str(payload.get("code")) != code:
        raise ValueError(f"SSE response code mismatch for {code}: {payload.get('code')}")
    rows = payload.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SSE response has no kline rows for {code}")
    if payload.get("begin") != 0:
        raise ValueError(f"SSE response begin mismatch for {code}")
    if len(rows) != int(payload.get("total", -1)):
        raise ValueError(f"SSE response is incomplete for {code}: {len(rows)} != {payload.get('total')}")
    if int(payload.get("end", -1)) != len(rows):
        raise ValueError(f"SSE response effective end mismatch for {code}")
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            raise ValueError(f"SSE response malformed kline row for {code}")
        if not isinstance(row[0], (str, int)) or len(str(row[0])) != 8 or float(row[4]) <= 0:
            raise ValueError(f"SSE response invalid date or close for {code}")
    return payload


def _validate_document(content: bytes, descriptor: dict[str, str]) -> None:
    if len(content) < 500:
        raise ValueError(f"Document unexpectedly short: {descriptor['filename']}")
    if descriptor["format"] == "pdf" and not content.startswith(b"%PDF"):
        raise ValueError(f"Document is not a PDF: {descriptor['filename']}")
    if descriptor["format"] == "html":
        prefix = content[:2000].decode("utf-8", errors="ignore").lower()
        if "safeline_bot_challenge" in prefix or "<title>web 应用防火墙" in prefix:
            raise ValueError(f"WAF response cannot be retained as official source: {descriptor['filename']}")


def _runtime_provenance() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
            text=True,
        )
        git_commit = result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "not_available"
    return {
        "git_commit_at_runtime": git_commit,
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _capture() -> None:
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C8 source batch already exists; use --rebuild-derived or --verify-only")
    staged: list[tuple[Path, bytes, dict[str, Any]]] = []
    now: list[str] = []
    for descriptor in DOCUMENTS:
        response = requests.get(descriptor["url"], headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Document download failed {response.status_code}: {descriptor['url']}")
        _validate_document(response.content, descriptor)
        path = RAW_DIR / descriptor["filename"]
        staged.append((path, response.content, {**descriptor, "retrieved_at": datetime.now(timezone.utc).isoformat()}))
        now.append(staged[-1][2]["retrieved_at"])
    for code in ASSETS:
        response = requests.get(_price_url(code), headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Price download failed {response.status_code}: {code}")
        payload = _parse_jsonp(response.content, code)
        path = RAW_DIR / _price_filename(code)
        retrieval = datetime.now(timezone.utc).isoformat()
        staged.append(
            (
                path,
                response.content,
                {
                    "publisher": "Shanghai Stock Exchange",
                    "title": f"SSE ETF daily market-price response for {code}",
                    "document_date": DATA_CUTOFF,
                    "url": _price_url(code),
                    "referer": PRICE_REFERER,
                    "format": "jsonp",
                    "retrieved_at": retrieval,
                    "response_total": int(payload["total"]),
                    "response_rows": len(payload["kline"]),
                    "first_trade_date": str(payload["kline"][0][0]),
                    "last_trade_date": str(payload["kline"][-1][0]),
                },
            )
        )
        now.append(retrieval)
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    for path, content, _ in staged:
        _atomic_write(path, content)
    rows: list[dict[str, Any]] = []
    for path, _, metadata in staged:
        rows.append(
            {
                **_file_record(path),
                **metadata,
                "capture_note": (
                    "Read-only retrospective public capture. It does not establish historical available_at, "
                    "revisions, data rights, total return, NAV/IOPV, corporate actions, market status, "
                    "costs, order-book depth, capacity, fills, allocation, holding, or action."
                ),
            }
        )
    manifest = {
        "capture_batch": RAW_DIR.name,
        "captured_at": min(now),
        "purpose": "C8 raw first-party product, index/mechanics documentation and retrospective market-price observations. It supports an exploratory source-bound price-proxy falsification only.",
        "source_quality": PRICE_SOURCE_QUALITY,
        "files": rows,
        "limitations": [
            "This is an anonymous read-only public capture, not entitled data delivery or evidence of permitted historical replay/derivation/review rights.",
            "The dayk records are exchange market-price observations, not verified investor total-return, NAV, IOPV, distribution, corporate-action, status, execution, or brokerage records.",
            "Product and index documents are dated disclosures. They must not be used as evidence of current account eligibility, current fund terms, liquidity, premiums, or an investment recommendation.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "case_local_hash_control",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": [_file_record(path) for path, _, _ in staged],
            "runtime_provenance": _runtime_provenance(),
            "boundary": "Case-local hashes detect raw-file mismatch only. They do not provide external notarization, point-in-time provenance, entitlement, total-return or execution validation.",
        },
    }
    _write_json(MANIFEST_JSON, manifest)
    lines = [
        "# C8 Official Product and Price Capture Manifest",
        "",
        f"- Batch: `{manifest['capture_batch']}`",
        f"- Capture time: `{manifest['captured_at']}`",
        "- Method: anonymous, read-only HTTPS requests to named official documents and the SSE ETF daily-price endpoint.",
        "- Boundary: documents support dated product/mechanics facts; prices are retrospective market-price observations only, not investor total return or execution proof.",
        "",
        "| File | Publisher | Date / price coverage | SHA-256 |",
        "|---|---|---|---|",
    ]
    for row in rows:
        period = row.get("document_date", "not_reported")
        if row.get("first_trade_date"):
            period = f"{row['first_trade_date']} to {row['last_trade_date']} ({row['response_rows']} rows)"
        lines.append(f"| {Path(row['path']).name} | {row['publisher']} | {period} | `{row['sha256']}` |")
    lines.extend(
        [
            "",
            "Every hash in this table is verified by `tools/verify_source_manifests.py`. The existence of an official public response does not establish point-in-time availability, price-adjustment basis, event completeness, licensed replay, or a tradable result.",
            "",
        ]
    )
    _write_text(MANIFEST_MD, "\n".join(lines))


def _verify_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.is_file():
        raise FileNotFoundError(f"Absent C8 source manifest: {MANIFEST_JSON}")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("C8 source manifest has no file records")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(frozen, list):
        raise ValueError("C8 source manifest has no frozen-file records")
    listed_paths = {entry.get("path") for entry in files}
    frozen_paths = {entry.get("path") for entry in frozen}
    if listed_paths != frozen_paths:
        raise ValueError("C8 source manifest and source freeze file sets differ")
    for entry in files:
        path = (REPO_ROOT / str(entry["path"])).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"C8 raw file absent: {path}")
        if path.stat().st_size != int(entry["bytes"]):
            raise ValueError(f"C8 raw file size mismatch: {path}")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"C8 raw file hash mismatch: {path}")
    return manifest


def _load_price_series(code: str) -> OrderedDict[str, float]:
    path = RAW_DIR / _price_filename(code)
    payload = _parse_jsonp(path.read_bytes(), code)
    series: OrderedDict[str, float] = OrderedDict()
    for row in payload["kline"]:
        raw_date = str(row[0])
        if len(raw_date) != 8 or not raw_date.isdigit():
            raise ValueError(f"Unexpected SSE date format in {code}: {raw_date}")
        date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        close = float(row[4])
        if date in series:
            raise ValueError(f"Duplicate date in {code}: {date}")
        if close <= 0:
            raise ValueError(f"Non-positive close in {code}: {date}")
        series[date] = close
    return series


def _last_common_observation_by_month(dates: list[str]) -> set[str]:
    last: dict[str, str] = {}
    for date in dates:
        last[date[:7]] = date
    return {date for month, date in last.items() if int(month[5:7]) in {3, 6, 9, 12}}


def _complete_calendar_years(dates: list[str], nav: list[float]) -> list[dict[str, Any]]:
    by_year: dict[int, list[int]] = {}
    for index, date in enumerate(dates):
        by_year.setdefault(int(date[:4]), []).append(index)
    first_year = min(by_year)
    last_year = max(by_year)
    rows: list[dict[str, Any]] = []
    for year, indexes in sorted(by_year.items()):
        first_date = dates[indexes[0]]
        last_date = dates[indexes[-1]]
        complete = year not in {first_year, last_year} and first_date[5:7] == "01" and last_date[5:7] == "12"
        if complete:
            prior_index = indexes[0] - 1
            if prior_index < 0:
                raise ValueError(f"Complete-year starting value unavailable: {year}")
            return_value = nav[indexes[-1]] / nav[prior_index] - 1.0
        else:
            return_value = None
        rows.append(
            {
                "year": year,
                "first_observation": first_date,
                "last_observation": last_date,
                "complete": complete,
                "net_unitized_change": return_value,
            }
        )
    return rows


def _simulate() -> dict[str, Any]:
    if not PROTOCOL_JSON.is_file():
        raise FileNotFoundError(f"Absent C8 protocol: {PROTOCOL_JSON}")
    protocol = json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))
    expected_targets = protocol["rules"]["targets"]
    targets = {code: float(expected_targets[code]) for code in ASSETS}
    if targets != dict(ASSETS) or abs(sum(targets.values()) - 1.0) > 1e-12:
        raise ValueError("C8 protocol target weights do not match frozen script targets")
    cost_rate = float(protocol["rules"]["cost_stress_rate"])
    if abs(cost_rate - 0.003) > 1e-12:
        raise ValueError("C8 protocol cost rate does not match frozen script")
    source = {code: _load_price_series(code) for code in ASSETS}
    common = sorted(set.intersection(*(set(series) for series in source.values())))
    if len(common) < 2:
        raise ValueError("C8 common price panel has insufficient observations")
    prices = [{code: source[code][date] for code in ASSETS} for date in common]
    last_quarterly = _last_common_observation_by_month(common)

    initial_nav_before_cost = 1.0
    initial_cost = cost_rate
    nav_value = initial_nav_before_cost * (1.0 - initial_cost)
    holdings = {code: nav_value * targets[code] / prices[0][code] for code in ASSETS}
    nav: list[float] = [nav_value]
    rebalance_rows: list[dict[str, Any]] = [
        {
            "formation_date": common[0],
            "effective_close_date": common[0],
            "kind": "initial_build_at_baseline_close",
            "one_way_turnover": 1.0,
            "cost_rate_on_nav": initial_cost,
            "nav_before_cost": initial_nav_before_cost,
            "nav_after_cost": nav_value,
        }
    ]
    pending_formation: str | None = None
    for position in range(1, len(common)):
        date = common[position]
        nav_before_rebalance = sum(holdings[code] * prices[position][code] for code in ASSETS)
        if pending_formation is not None:
            drift_weights = {
                code: holdings[code] * prices[position][code] / nav_before_rebalance
                for code in ASSETS
            }
            turnover = 0.5 * sum(abs(drift_weights[code] - targets[code]) for code in ASSETS)
            cost = cost_rate * turnover
            nav_after_rebalance = nav_before_rebalance * (1.0 - cost)
            holdings = {
                code: nav_after_rebalance * targets[code] / prices[position][code]
                for code in ASSETS
            }
            rebalance_rows.append(
                {
                    "formation_date": pending_formation,
                    "effective_close_date": date,
                    "kind": "quarterly_rebalance_at_effective_close",
                    "drift_weights_before_trade": drift_weights,
                    "one_way_turnover": turnover,
                    "cost_rate_on_nav": cost,
                    "nav_before_cost": nav_before_rebalance,
                    "nav_after_cost": nav_after_rebalance,
                }
            )
            nav_value = nav_after_rebalance
            pending_formation = None
        else:
            nav_value = nav_before_rebalance
        nav.append(nav_value)
        if date in last_quarterly and position < len(common) - 1:
            pending_formation = date
    if pending_formation is not None:
        # The protocol does not permit a same-close fictitious execution.
        unexecuted_rebalance = {"formation_date": pending_formation, "reason": "terminal_observation_has_no_next_common_close"}
    else:
        unexecuted_rebalance = None

    returns = [nav[i] / nav[i - 1] - 1.0 for i in range(1, len(nav))]
    peak = nav[0]
    max_drawdown = 0.0
    for value in nav:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1.0)
    intervals = len(nav) - 1
    # The protocol fixes the unit-NAV baseline at 1.0 before the initial
    # build.  The first recorded observation is already reduced by the
    # initial 30bp load, so dividing by nav[0] would incorrectly cancel it.
    annualized = nav[-1] ** (252.0 / intervals) - 1.0
    calendar_years = _complete_calendar_years(common, nav)
    complete_years = [row for row in calendar_years if row["complete"]]
    rolling: list[dict[str, Any]] = []
    lookback = 1260
    for index in range(lookback, len(nav)):
        change = (nav[index] / nav[index - lookback]) ** (252.0 / lookback) - 1.0
        rolling.append(
            {
                "start_date": common[index - lookback],
                "end_date": common[index],
                "annualized_net_unitized_change": change,
            }
        )
    hurdle = float(protocol["falsification"]["strict_hurdle"])
    annual_failures = [row for row in complete_years if float(row["net_unitized_change"]) < hurdle]
    rolling_failures = [row for row in rolling if float(row["annualized_net_unitized_change"]) < hurdle]
    input_failures: list[str] = []
    if not complete_years:
        input_failures.append("no_complete_calendar_year")
    if not rolling:
        input_failures.append("no_1260_observation_rolling_window")
    if input_failures or annual_failures or rolling_failures:
        label = protocol["falsification"]["fail_label"]
    else:
        label = protocol["falsification"]["pass_label"]
    total_turnover = sum(float(row["one_way_turnover"]) for row in rebalance_rows)
    total_cost_rate_contribution = sum(float(row["cost_rate_on_nav"]) for row in rebalance_rows)
    return {
        "protocol": {
            "document_id": protocol["document_id"],
            "status": protocol["status"],
            "portfolio_q": protocol["portfolio_q"],
            "path": _repo_relative(PROTOCOL_JSON),
            "sha256": _sha256(PROTOCOL_JSON),
        },
        "source_boundary": {
            "quality": PRICE_SOURCE_QUALITY,
            "basis": "SSE public dayk close, retrospective capture",
            "not_proven": [
                "point_in_time_availability", "adjustment_or_total_return_basis", "NAV_IOPV", "distributions", "corporate_actions", "market_status", "costs", "depth", "fills", "account_eligibility", "action"
            ],
        },
        "rule": {
            "target_weights": targets,
            "quarterly_formation_months": [3, 6, 9, 12],
            "effective_trade_timing": "next_common_observation_close_after_formation_close",
            "cost_stress_rate": cost_rate,
            "no_lookahead_note": "Each quarterly rebalance uses that effective close after the day under old holdings; new holdings affect subsequent observations only.",
        },
        "result": {
            "status": label,
            "portfolio_q": 0,
            "panel_observations": len(common),
            "panel_first_date": common[0],
            "panel_last_date": common[-1],
            "effective_return_start_date": common[1],
            "terminal_unit_nav": nav[-1],
            "net_unitized_change_from_baseline": nav[-1] - 1.0,
            "annualized_net_unitized_change": annualized,
            "max_drawdown": max_drawdown,
            "complete_calendar_years": calendar_years,
            "complete_year_failure_count": len(annual_failures),
            "complete_year_failures": annual_failures,
            "rolling_window_observations": lookback,
            "rolling_window_count": len(rolling),
            "rolling_pass_count": len(rolling) - len(rolling_failures),
            "rolling_failure_count": len(rolling_failures),
            "rolling_min_annualized_net_unitized_change": min((row["annualized_net_unitized_change"] for row in rolling), default=None),
            "rolling_max_annualized_net_unitized_change": max((row["annualized_net_unitized_change"] for row in rolling), default=None),
            "rolling_failures": rolling_failures,
            "rebalance_count_including_initial": len(rebalance_rows),
            "one_way_turnover_sum": total_turnover,
            "cost_rate_sum_not_compounded": total_cost_rate_contribution,
            "rebalance_rows": rebalance_rows,
            "unexecuted_terminal_rebalance": unexecuted_rebalance,
            "input_failures": input_failures,
        },
        "derived_runtime_provenance": _runtime_provenance(),
        "allowed_interpretation": "This frozen exploratory result is only a public official market-price arithmetic proxy. It cannot show total return, stable 5% performance, suitability, allocation, holding, order execution, or a personal action.",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    result = payload["result"]
    pct = lambda value: "n/a" if value is None else f"{100.0 * float(value):.2f}%"
    annual_rows = "\n".join(
        f"| {row['year']} | {row['first_observation']} | {row['last_observation']} | {'是' if row['complete'] else '否'} | {pct(row['net_unitized_change'])} |"
        for row in result["complete_calendar_years"]
    )
    failed_years = ", ".join(str(row["year"]) for row in result["complete_year_failures"]) or "无"
    rolling_fail_examples = "\n".join(
        f"| {row['start_date']} | {row['end_date']} | {pct(row['annualized_net_unitized_change'])} |"
        for row in result["rolling_failures"][:20]
    ) or "| 无 | 无 | 无 |"
    return f"""# C8 可转债 ETF 固定配置：官方公开市场价代理检验 — 2026-08-15

- 规则：`DPSFS-C8-CB-ETFR-v1`；规则状态：`{payload['protocol']['status']}`。
- 结论标签：**`{result['status']}`**；`portfolio_q=0`。
- 这不是基金净值或投资者总回报回放，而是上交所日线公开收盘价的回溯代理。即使来源为交易所，也没有复权/分配、NAV/IOPV、公司行动、停复牌、成本、深度或成交证据。

## 固定规则与覆盖

| 代码 | 固定权重 |
|---|---:|
| 511180（投资级可转债核心） | 50% |
| 511380（广义可转债卫星） | 25% |
| 511010（5 年期国债缓冲） | 25% |

- 面板：`{result['panel_observations']}` 个共同观察，`{result['panel_first_date']}` 至 `{result['panel_last_date']}`；收益从 `{result['effective_return_start_date']}` 起计算。
- 规则：初建仓与每个季度再平衡按漂移后单边换手施加 `30bp` 压力载荷；季度形成日后的下一共同观察日收盘才调整，避免用同日收盘价同时形成和生效。
- 全期价格代理年化单位化变化：`{pct(result['annualized_net_unitized_change'])}`；末端单位净值：`{result['terminal_unit_nav']:.6f}`；最大回撤：`{pct(result['max_drawdown'])}`。
- 共 `{result['rebalance_count_including_initial']}` 次含初建仓的调整；单边换手合计 `{result['one_way_turnover_sum']:.6f}`；非复利成本载荷和 `{pct(result['cost_rate_sum_not_compounded'])}`。

## 严格 5% 否决检查

完整自然年中低于 5% 的年份：`{failed_years}`；滚动五年端点通过 `{result['rolling_pass_count']}/{result['rolling_window_count']}`，最低 `{pct(result['rolling_min_annualized_net_unitized_change'])}`，最高 `{pct(result['rolling_max_annualized_net_unitized_change'])}`。

| 年份 | 首观察日 | 末观察日 | 完整年度 | 净单位化变化 |
|---:|---|---|---|---:|
{annual_rows}

前 20 个不达标滚动端点（若有）：

| 起点 | 终点 | 年化净单位化变化 |
|---|---|---:|
{rolling_fail_examples}

## 正确解释

`{result['status']}` 只回答这条固定规则在受限价格代理口径下是否被用户目标导出的严格否决线否定。它不等于稳定收益，不应被用作任何买卖、持有、账户配置或基金优选动作。若标签为未否决，C8 仍因探索性规则冻结前的身份/文件发现、回溯抓取和缺失总回报/执行证据而保持 `portfolio_q=0`；若标签为否决，C8-T1 不得调权重、频率、样本期或成本寻找幸存者。

源文件、哈希和文档日期见 [C8 source manifest](../sources/c8-official-product-and-price-20260815/manifest.md)。机器副本：[c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json](c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json)。
"""


def _rebuild_derived() -> dict[str, Any]:
    manifest = _verify_manifest()
    payload = _simulate()
    payload["source_manifest"] = {
        "path": _repo_relative(MANIFEST_JSON),
        "sha256": _sha256(MANIFEST_JSON),
        "capture_batch": manifest["capture_batch"],
    }
    _write_json(OUTPUT_JSON, payload)
    _write_text(OUTPUT_MD, _render_markdown(payload))
    return payload


def _verify_output() -> None:
    _verify_manifest()
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        raise FileNotFoundError("C8 derived output is absent")
    saved = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    recalculated = _simulate()
    for key in ("protocol", "source_boundary", "rule", "result", "allowed_interpretation"):
        if saved.get(key) != recalculated.get(key):
            raise ValueError(f"C8 derived output differs on {key}; run --rebuild-derived")
    manifest_record = saved.get("source_manifest", {})
    if manifest_record.get("sha256") != _sha256(MANIFEST_JSON):
        raise ValueError("C8 derived output source-manifest hash differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--capture", action="store_true")
    modes.add_argument("--rebuild-derived", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
        payload = _rebuild_derived()
        print(f"C8 CAPTURE + REPLAY: {payload['result']['status']}")
    elif arguments.rebuild_derived:
        payload = _rebuild_derived()
        print(f"C8 REPLAY: {payload['result']['status']}")
    else:
        _verify_output()
        print("C8 CAPTURE/REPLAY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
