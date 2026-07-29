#!/usr/bin/env python3
"""Refresh the full-market H1-preview universe through 2026-07-15.

The prior 2026-07-11/13 artifacts remain immutable baselines. This script writes
the rolling refresh into the case-local refresh-20260715 data/source tree.
"""

from __future__ import annotations

import concurrent.futures
import json
import re
import time
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
BASELINE_DATA = CASE_DIR / "data"
REFRESH_DIR = CASE_DIR / "refresh-20260715"
REFRESH_DATA = REFRESH_DIR / "data"
REFRESH_SOURCES = REFRESH_DIR / "sources" / "official-preview-scan-20260715"
INDEX_URL = "https://np-anotice-stock.eastmoney.com/api/security/ann"
CONTENT_URL = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://data.eastmoney.com/notices/",
}
BEGIN_DATE = "2026-06-01"
END_DATE = "2026-07-15"
DATA_CUTOFF = "2026-07-15"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def fetch_latest_notice(ticker: str) -> dict[str, Any]:
    params = {
        "sr": "-1",
        "page_size": "100",
        "page_index": "1",
        "ann_type": "A",
        "client_source": "web",
        "f_node": "0",
        "s_node": "0",
        "begin_time": BEGIN_DATE,
        "end_time": END_DATE,
        "stock_list": ticker,
    }
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(
                INDEX_URL, params=params, headers=HEADERS, timeout=30
            )
            response.raise_for_status()
            rows = (response.json().get("data") or {}).get("list") or []
            matches = [
                row
                for row in rows
                if "半年度业绩预" in str(
                    row.get("title") or row.get("title_ch") or ""
                )
                and any(
                    str(code.get("stock_code") or "") == ticker
                    for code in row.get("codes") or []
                )
            ]
            if not matches:
                return {
                    "ticker": ticker,
                    "status": "not_found_in_window",
                    "matches": [],
                    "retrieved_at": DATA_CUTOFF,
                }
            matches.sort(
                key=lambda row: (
                    str(row.get("notice_date") or ""),
                    str(row.get("sort_date") or ""),
                ),
                reverse=True,
            )
            selected = matches[0]
            art_code = str(selected.get("art_code") or "")
            content_response = requests.get(
                CONTENT_URL,
                params={"art_code": art_code, "client_source": "web"},
                headers=HEADERS,
                timeout=30,
            )
            content_response.raise_for_status()
            content = content_response.json().get("data") or {}
            attach_url = str(
                content.get("attach_url") or content.get("attach_url_web") or ""
            )
            result = {
                "ticker": ticker,
                "status": "matched",
                "art_code": art_code,
                "announcement_date": str(selected.get("notice_date") or "")[:10],
                "title": str(
                    selected.get("title") or selected.get("title_ch") or ""
                ),
                "notice_url": (
                    f"https://data.eastmoney.com/notices/detail/"
                    f"{ticker}/{art_code}.html"
                ),
                "attach_url": attach_url,
                "content_char_count": len(
                    str(content.get("notice_content") or "")
                ),
                "index_notice": selected,
                "notice_content": str(content.get("notice_content") or ""),
                "retrieved_at": DATA_CUTOFF,
            }
            return result
        except Exception as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))
    return {
        "ticker": ticker,
        "status": "failed",
        "error": repr(last_error),
        "retrieved_at": DATA_CUTOFF,
    }


def parse_number(text: str) -> float:
    return float(text.replace(",", "").replace("，", ""))


def metric_from_overlay(
    ticker: str, baseline_row: dict[str, Any], overlay: dict[str, Any]
) -> dict[str, Any]:
    """Use the validated 9-name packet where the prior run already parsed it."""
    row = dict(baseline_row)
    metric = overlay.get(ticker)
    if metric is None:
        return row
    for source_key, target_key in (
        ("h1_parent_np_midpoint_100mn", "h1_parent_np_midpoint_100mn"),
        ("h1_deducted_np_midpoint_100mn", "h1_deducted_np_midpoint_100mn"),
        ("h1_eps_midpoint", "official_h1_eps_midpoint"),
        ("announcement_date", "announcement_date"),
        ("preview_type", "preview_type"),
        ("quality_class", "refresh_quality_class"),
        ("quality_reason", "refresh_quality_reason"),
        ("disposition", "refresh_disposition"),
    ):
        if source_key in metric:
            row[target_key] = metric[source_key]
    row["h1_parent_np_midpoint_100mn"] = metric[
        "h1_parent_np_midpoint_100mn"
    ]
    row["h1_deducted_np_midpoint_100mn"] = metric[
        "h1_deducted_np_midpoint_100mn"
    ]
    row["parent_np_yoy_midpoint_pct"] = (
        (row["h1_parent_np_midpoint_100mn"] * 100 / metric["prior_parent_np_100mn"] - 100)
        if metric.get("prior_parent_np_100mn")
        else row.get("parent_np_yoy_midpoint_pct")
    )
    parent = row["h1_parent_np_midpoint_100mn"]
    deducted = row["h1_deducted_np_midpoint_100mn"]
    row["deducted_profit_share_pct"] = round(deducted / parent * 100, 2) if parent else None
    row["nonrecurring_share_pct"] = (
        round((parent - deducted) / parent * 100, 2) if parent else None
    )
    row["refresh_source_quality"] = "official_company_preview_pdf"
    row["refresh_source_path"] = metric.get("local_pdf")
    row["refresh_updated"] = True
    return row


def main() -> None:
    REFRESH_DATA.mkdir(parents=True, exist_ok=True)
    REFRESH_SOURCES.mkdir(parents=True, exist_ok=True)
    baseline_screen = load_json(
        BASELINE_DATA / "full_market_preview_screen_20260712.json"
    )
    baseline_rows = {row["ticker"]: row for row in baseline_screen["rows"]}
    overlay_packet = load_json(
        BASELINE_DATA / "earnings_preview_update_20260715.json"
    )
    overlay = {row["ticker"]: row for row in overlay_packet["rows"]}
    tickers = sorted(baseline_rows)

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(fetch_latest_notice, ticker): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["ticker"])
    matched = {row["ticker"]: row for row in results if row["status"] == "matched"}
    failures = [row for row in results if row["status"] == "failed"]

    refreshed_rows: list[dict[str, Any]] = []
    changed_rows: list[dict[str, Any]] = []
    for ticker in tickers:
        baseline = baseline_rows[ticker]
        latest = matched.get(ticker)
        row = dict(baseline)
        row["baseline_announcement_date"] = baseline.get("announcement_date")
        row["latest_notice_date"] = (
            latest.get("announcement_date") if latest else None
        )
        row["latest_notice_title"] = latest.get("title") if latest else None
        row["latest_notice_url"] = latest.get("notice_url") if latest else None
        row["latest_notice_art_code"] = latest.get("art_code") if latest else None
        row["latest_notice_status"] = (
            "updated_in_window"
            if latest
            and latest.get("announcement_date", "") > str(
                baseline.get("announcement_date") or ""
            )
            else "unchanged_or_no_new_notice"
        )
        row["refresh_data_quality"] = (
            "official_notice_overlay"
            if ticker in overlay
            else "baseline_structured_capture_with_full_window_notice_probe"
        )
        row = metric_from_overlay(ticker, row, overlay)
        if ticker in overlay:
            changed_rows.append(row)
        refreshed_rows.append(row)

    raw_packet = {
        "schema_version": "astock.full_market_h1_preview_refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "report_period": "2026H1",
        "source": "Eastmoney official announcement API full-window ticker probe",
        "window": [BEGIN_DATE, END_DATE],
        "baseline_source": "data/full_market_preview_screen_20260712.json",
        "ticker_count": len(tickers),
        "matched_notice_count": len(matched),
        "updated_notice_count": len(changed_rows),
        "failed_notice_count": len(failures),
        "fallback_path": (
            "AkShare stock_yjyg_em returned malformed data; the official announcement "
            "API was used for the full-window probe."
        ),
        "rows": refreshed_rows,
        "notice_results": results,
        "failures": failures,
    }
    write_json(REFRESH_DATA / "raw_full_market_h1_preview_20260715.json", raw_packet)
    write_json(REFRESH_DATA / "full_market_preview_screen_20260715.json", {
        **baseline_screen,
        "schema_version": "astock.full_market_preview_screen.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "source_preview_row_count": raw_packet["ticker_count"],
        "preview_company_count": len(refreshed_rows),
        "high_impact_candidate_count": sum(
            row.get("high_impact_candidate") for row in refreshed_rows
        ),
        "refresh_manifest": "data/full_market_refresh_manifest_20260715.json",
        "rows": refreshed_rows,
    })
    write_json(
        REFRESH_DATA / "full_market_refresh_manifest_20260715.json",
        {
            "schema_version": "astock.full_market_refresh_manifest.v1",
            "data_cutoff": DATA_CUTOFF,
            "ticker_count": len(tickers),
            "matched_notice_count": len(matched),
            "updated_notice_count": len(changed_rows),
            "failed_notice_count": len(failures),
            "updated_tickers": [row["ticker"] for row in changed_rows],
            "failed_tickers": [row["ticker"] for row in failures],
            "baseline_screen": "data/full_market_preview_screen_20260712.json",
            "raw_packet": "data/raw_full_market_h1_preview_20260715.json",
        },
    )
    lines = [
        "# Full-Market Refresh Manifest (2026-07-15)",
        "",
        f"- Ticker probes: {len(tickers)}",
        f"- Matched H1 preview notice in window: {len(matched)}",
        f"- Notice dates newer than baseline: {len(changed_rows)}",
        f"- Failed probes: {len(failures)}",
        "- Baseline retained: `data/full_market_preview_screen_20260712.json`",
        "- AkShare fallback: official Eastmoney announcement API",
        "",
        "## Updated Tickers",
        "",
        "| Ticker | Company | Baseline date | Latest date | Latest title | Source quality |",
        "|---|---|---|---|---|---|",
    ]
    for row in changed_rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | "
            f"{row.get('baseline_announcement_date')} | {row.get('latest_notice_date')} | "
            f"{row.get('latest_notice_title')} | {row.get('refresh_source_quality', 'official_notice_probe')} |"
        )
    if failures:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {row['ticker']}: {row.get('error')}" for row in failures)
    write_text(REFRESH_DATA / "full_market_refresh_manifest_20260715.md", "\n".join(lines))
    print(
        json.dumps(
            {
                "ticker_count": len(tickers),
                "matched_notice_count": len(matched),
                "updated_notice_count": len(changed_rows),
                "failed_notice_count": len(failures),
                "updated_tickers": [row["ticker"] for row in changed_rows],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
