#!/usr/bin/env python3
"""Refresh quotes, adjusted K-lines, and dispositions for the 2026-07-15 screen."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
SOURCE_DIR = REFRESH_DIR / "sources" / "market-20260715"
KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
DATA_CUTOFF = "2026-07-15"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def market_code(code: str) -> str:
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("8", "9", "4")):
        return f"bj{code}"
    return f"sz{code}"


def fetch_quotes(codes: list[str]) -> dict[str, dict[str, Any]]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, Any]] = {}
    for offset in range(0, len(codes), 50):
        batch = codes[offset : offset + 50]
        query = ",".join(market_code(code) for code in batch)
        response = requests.get(
            f"https://qt.gtimg.cn/q={query}",
            timeout=30,
        )
        response.raise_for_status()
        raw_path = SOURCE_DIR / f"tencent_quotes_{offset // 50 + 1:02d}.txt"
        raw_path.write_bytes(response.content)
        for code, body in re.findall(
            r'v_(?:sh|sz|bj)(\d+)="([^"]*)"',
            response.content.decode("gbk", errors="ignore"),
        ):
            fields = body.split("~")
            if len(fields) < 35:
                continue
            result[code] = {
                "ticker": code,
                "quote_company": fields[1],
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


def fetch_kline(code: str) -> dict[str, Any]:
    path = DATA_DIR / "market" / f"raw_kline_{code}_{DATA_CUTOFF.replace('-', '')}.json"
    if path.exists() and path.stat().st_size:
        return load_json(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(
                KLINE_URL,
                params={
                    "param": (
                        f"{market_code(code)},day,2025-07-01,"
                        f"{DATA_CUTOFF},400,qfq"
                    )
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            write_json(path, payload)
            time.sleep(0.03)
            return payload
        except Exception as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"{code}: K-line fetch failed: {last_error!r}")


def metrics(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data") or {}
    key = next((item for item in data if item not in {"qt", "market"}), None)
    if key is None:
        return {"history_status": "missing"}
    rows = data[key].get("qfqday") or data[key].get("day") or []
    closes = [float(row[2]) for row in rows if len(row) >= 3]
    if not closes:
        return {"history_status": "empty"}
    current = closes[-1]
    high = max(closes)
    low = min(closes)
    return {
        "return_20d_pct": round((current / closes[-21] - 1) * 100, 2)
        if len(closes) > 20
        else None,
        "return_60d_pct": round((current / closes[-61] - 1) * 100, 2)
        if len(closes) > 60
        else None,
        "return_120d_pct": round((current / closes[-121] - 1) * 100, 2)
        if len(closes) > 120
        else None,
        "position_1y_pct": round((current - low) / (high - low) * 100, 2)
        if high > low
        else 50.0,
        "drawdown_from_1y_high_pct": round((current / high - 1) * 100, 2),
        "history_status": "full_year" if len(closes) >= 200 else f"partial_{len(closes)}_days",
        "kline_observation_count": len(closes),
        "kline_cutoff": DATA_CUTOFF,
    }


def disposition(row: dict[str, Any]) -> str:
    nonrecurring = row.get("nonrecurring_share_pct")
    position = row.get("position_1y_pct")
    stage = row.get("sector_stage")
    yoy = row.get("parent_np_yoy_midpoint_pct")
    return_20d = row.get("return_20d_pct")
    return_60d = row.get("return_60d_pct")
    if row.get("h1_deducted_np_midpoint_100mn") is not None and row[
        "h1_deducted_np_midpoint_100mn"
    ] <= 0:
        return "exclude_deducted_profit_nonpositive"
    if nonrecurring is not None and nonrecurring > 40:
        return "exclude_nonrecurring_dominated"
    if yoy is None or yoy <= 0:
        return "earnings_decline_watch"
    if position is None or row.get("history_status") != "full_year":
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
    packet = load_json(DATA_DIR / "full_market_preview_screen_20260715.json")
    rows = packet["rows"]
    codes = [row["ticker"] for row in rows if row.get("high_impact_candidate")]
    quotes = fetch_quotes(codes)
    enriched: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        if not row.get("high_impact_candidate"):
            continue
        code = row["ticker"]
        try:
            kline = metrics(fetch_kline(code))
        except Exception as exc:
            failures.append({"ticker": code, "error": repr(exc)})
            kline = {"history_status": "fetch_failed"}
        item = {
            **row,
            **quotes.get(code, {}),
            **kline,
        }
        item["full_market_disposition"] = disposition(item)
        item["market_data_quality"] = (
            "Tencent quote + Tencent adjusted K-line through 2026-07-15"
            if item.get("current_price") is not None
            and item.get("history_status") == "full_year"
            else "partial_or_missing_market_data"
        )
        enriched.append(item)
        if index % 10 == 0 or index == len(codes):
            print(f"market {index}/{len(codes)}")
    order = {
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
    enriched.sort(key=lambda row: (order.get(row["full_market_disposition"], 99),
                                   -row["impact_score"]))
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
    payload = {
        "schema_version": "astock.full_market_candidates_refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "source_preview": "data/full_market_preview_screen_20260715.json",
        "candidate_count": len(enriched),
        "priority_count": len(priority),
        "failures": failures,
        "disposition_counts": {
            key: sum(row["full_market_disposition"] == key for row in enriched)
            for key in order
        },
        "rows": enriched,
    }
    write_json(DATA_DIR / "full_market_candidates_20260715.json", payload)
    write_json(DATA_DIR / "full_market_priority_pool_20260715.json", {
        "schema_version": "astock.full_market_priority_pool.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(priority),
        "rows": priority,
    })
    lines = [
        "# Full-Market Candidate Refresh Through 2026-07-15",
        "",
        f"- High-impact candidates: {len(enriched)}",
        f"- Priority candidates: {len(priority)}",
        f"- Market-data failures: {len(failures)}",
        "",
        "| Disposition | Count |",
        "|---|---:|",
    ]
    for key, count in payload["disposition_counts"].items():
        lines.append(f"| {key} | {count} |")
    lines += [
        "",
        "## Boundary",
        "",
        "Sector stages use complete 31/31 public daily and weekly industry-flow tables observed through 2026-07-14 and SWS index histories through 2026-07-14. Stock-level quotes and adjusted K-lines are refreshed through 2026-07-15. The separate continuous-inflow article is partial at 30/112 and is not treated as a complete universe.",
    ]
    write_text(DATA_DIR / "full_market_candidates_20260715.md", "\n".join(lines))
    print(json.dumps({
        "candidate_count": len(enriched),
        "priority_count": len(priority),
        "failures": failures,
        "disposition_counts": payload["disposition_counts"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
