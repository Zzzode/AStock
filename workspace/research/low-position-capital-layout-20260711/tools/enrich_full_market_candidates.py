#!/usr/bin/env python3
"""Enrich full-market preview candidates with reproducible price-position data."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "full-market-preview-20260712" / "market"
KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def market_code(code: str) -> str:
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("8", "9", "4")):
        return f"bj{code}"
    return f"sz{code}"


def parse_quote_response(text: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for code, body in re.findall(r'v_(?:sh|sz|bj)(\d+)="([^"]*)"', text):
        fields = body.split("~")
        if len(fields) < 35:
            continue
        result[code] = {
            "ticker": code,
            "company": fields[1],
            "current_price": float(fields[3]) if fields[3] else None,
            "previous_close": float(fields[4]) if fields[4] else None,
            "daily_change_pct": float(fields[32]) if fields[32] else None,
            "daily_high": float(fields[33]) if fields[33] else None,
            "daily_low": float(fields[34]) if fields[34] else None,
            "quote_timestamp": fields[30] if len(fields) > 30 else None,
            "float_market_cap_100mn": (
                float(fields[44]) if len(fields) > 44 and fields[44] else None
            ),
            "total_market_cap_100mn": (
                float(fields[45]) if len(fields) > 45 and fields[45] else None
            ),
            "trading_value_100mn": (
                float(fields[57]) / 10000
                if len(fields) > 57 and fields[57]
                else None
            ),
        }
    return result


def fetch_quotes(codes: list[str]) -> dict[str, dict[str, Any]]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, Any]] = {}
    for offset in range(0, len(codes), 50):
        batch = codes[offset : offset + 50]
        query = ",".join(market_code(code) for code in batch)
        url = f"https://qt.gtimg.cn/q={query}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        raw_path = SOURCE_DIR / f"tencent_quotes_{offset // 50 + 1:02d}.txt"
        raw_path.write_bytes(response.content)
        result.update(parse_quote_response(response.content.decode("gbk", errors="ignore")))
    return result


def fetch_kline(code: str) -> dict[str, Any]:
    cache_path = DATA_DIR / f"raw_kline_{code}_20260710.json"
    if cache_path.exists() and cache_path.stat().st_size:
        return load_json(cache_path)
    symbol = market_code(code)
    response = requests.get(
        KLINE_URL,
        params={
            "param": f"{symbol},day,2025-07-01,2026-07-10,400,qfq",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    write_json(cache_path, payload)
    time.sleep(0.05)
    return payload


def kline_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data") or {}
    key = next((item for item in data if item not in {"qt", "market"}), None)
    if key is None:
        return {
            "return_20d_pct": None,
            "return_60d_pct": None,
            "position_1y_pct": None,
            "drawdown_from_1y_high_pct": None,
            "history_status": "missing",
        }
    rows = data[key].get("qfqday") or data[key].get("day") or []
    closes = [float(row[2]) for row in rows if len(row) >= 3]
    if not closes:
        return {
            "return_20d_pct": None,
            "return_60d_pct": None,
            "position_1y_pct": None,
            "drawdown_from_1y_high_pct": None,
            "history_status": "empty",
        }
    current = closes[-1]
    high = max(closes)
    low = min(closes)
    return {
        "return_20d_pct": (
            round((current / closes[-21] - 1) * 100, 2)
            if len(closes) > 20
            else None
        ),
        "return_60d_pct": (
            round((current / closes[-61] - 1) * 100, 2)
            if len(closes) > 60
            else None
        ),
        "position_1y_pct": (
            round((current - low) / (high - low) * 100, 2)
            if high > low
            else 50.0
        ),
        "drawdown_from_1y_high_pct": round((current / high - 1) * 100, 2),
        "history_status": (
            "full_year" if len(closes) >= 200 else f"partial_{len(closes)}_days"
        ),
    }


def final_disposition(row: dict[str, Any]) -> str:
    nonrecurring = row.get("nonrecurring_share_pct")
    position = row.get("position_1y_pct")
    stage = row.get("sector_stage")
    yoy = row.get("parent_np_yoy_midpoint_pct")
    return_20d = row.get("return_20d_pct")
    return_60d = row.get("return_60d_pct")
    history_status = row.get("history_status")
    if row.get("h1_deducted_np_midpoint_100mn") is not None and row[
        "h1_deducted_np_midpoint_100mn"
    ] <= 0:
        return "exclude_deducted_profit_nonpositive"
    if nonrecurring is not None and nonrecurring > 40:
        return "exclude_nonrecurring_dominated"
    if yoy is None or yoy <= 0:
        return "earnings_decline_watch"
    if position is None or history_status != "full_year":
        return "watch_insufficient_price_history"
    if stage == "silent_accumulation" and position <= 65:
        return "quiet_accumulation_priority"
    if (
        stage in {"launch_confirmation", "flow_watch"}
        and position <= 80
        and max(return_20d or -999, return_60d or -999) >= 5
    ):
        return "launched_with_runway_candidate"
    if position <= 35:
        return "low_position_earnings_priority"
    if position > 80:
        return "earnings_delivered_price_advanced"
    return "earnings_validation_watch"


def main() -> None:
    candidate_path = DATA_DIR / "full_market_preview_candidates_20260712.json"
    packet = load_json(candidate_path)
    rows = packet["rows"]
    codes = [row["ticker"] for row in rows]
    quotes = fetch_quotes(codes)
    failures: list[dict[str, str]] = []
    enriched: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        code = row["ticker"]
        try:
            metrics = kline_metrics(fetch_kline(code))
        except Exception as exc:
            failures.append({"ticker": code, "error": repr(exc)})
            metrics = {
                "return_20d_pct": None,
                "return_60d_pct": None,
                "position_1y_pct": None,
                "drawdown_from_1y_high_pct": None,
                "history_status": "fetch_failed",
            }
        enriched_row = {**row, **quotes.get(code, {}), **metrics}
        enriched_row["full_market_disposition"] = final_disposition(enriched_row)
        enriched.append(enriched_row)
        print(f"{index}/{len(rows)} {code} {enriched_row['full_market_disposition']}")
    disposition_order = {
        "quiet_accumulation_priority": 0,
        "low_position_earnings_priority": 1,
        "launched_with_runway_candidate": 2,
        "earnings_validation_watch": 3,
        "earnings_delivered_price_advanced": 4,
        "watch_insufficient_price_history": 5,
        "earnings_decline_watch": 6,
        "exclude_nonrecurring_dominated": 7,
        "exclude_deducted_profit_nonpositive": 8,
    }
    enriched.sort(
        key=lambda row: (
            disposition_order.get(row["full_market_disposition"], 99),
            -row["impact_score"],
        )
    )
    priority = [
        row
        for row in enriched
        if row["full_market_disposition"]
        in {
            "quiet_accumulation_priority",
            "low_position_earnings_priority",
            "launched_with_runway_candidate",
        }
    ]
    write_json(
        DATA_DIR / "full_market_preview_candidates_20260712.json",
        {
            "schema_version": "astock.full_market_preview_candidates.v2",
            "row_count": len(enriched),
            "priority_count": len(priority),
            "failures": failures,
            "rows": enriched,
        },
    )
    write_json(
        DATA_DIR / "full_market_priority_pool_20260712.json",
        {
            "schema_version": "astock.full_market_priority_pool.v1",
            "row_count": len(priority),
            "rows": priority,
        },
    )
    print(
        json.dumps(
            {
                "row_count": len(enriched),
                "priority_count": len(priority),
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
