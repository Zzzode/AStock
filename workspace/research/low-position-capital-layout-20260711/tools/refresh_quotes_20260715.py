#!/usr/bin/env python3
"""Refresh same-day Tencent quotes for the 2026-07-15 candidate universe."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
SOURCE_DIR = REFRESH_DIR / "sources" / "market-20260715"
DATA_CUTOFF = "2026-07-15"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


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
        response = requests.get(
            "https://qt.gtimg.cn/q=" + ",".join(market_code(code) for code in batch),
            timeout=30,
        )
        response.raise_for_status()
        raw_path = SOURCE_DIR / f"tencent_quotes_intraday_{offset // 50 + 1:02d}.txt"
        raw_path.write_bytes(response.content)
        text = response.content.decode("gbk", errors="ignore")
        for code, body in re.findall(r'v_(?:sh|sz|bj)(\d+)="([^"]*)"', text):
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


def main() -> None:
    candidate_path = DATA_DIR / "full_market_candidates_20260715.json"
    packet = load_json(candidate_path)
    rows = packet["rows"]
    codes = [row["ticker"] for row in rows]
    quotes = fetch_quotes(codes)
    refreshed: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    changed: list[dict[str, Any]] = []
    for row in rows:
        code = row["ticker"]
        quote = quotes.get(code)
        if quote is None:
            failures.append({"ticker": code, "error": "quote not returned"})
            refreshed.append(row)
            continue
        updated = {**row, **quote}
        if row.get("current_price") != quote.get("current_price"):
            changed.append(
                {
                    "ticker": code,
                    "company": row["company"],
                    "old_price": row.get("current_price"),
                    "new_price": quote.get("current_price"),
                    "quote_timestamp": quote.get("quote_timestamp"),
                }
            )
        updated["intraday_refresh_at"] = datetime.now().astimezone().isoformat()
        updated["market_data_quality"] = (
            "Tencent intraday quote through 2026-07-15; adjusted K-line baseline retained"
        )
        refreshed.append(updated)
    refreshed.sort(
        key=lambda row: (
            row.get("full_market_disposition", ""),
            -(row.get("impact_score") or 0),
        )
    )
    output = {
        **packet,
        "schema_version": "astock.full_market_candidates_refresh_intraday.v1",
        "data_cutoff": DATA_CUTOFF,
        "intraday_refresh": True,
        "quote_count": len(quotes),
        "changed_price_count": len(changed),
        "quote_failures": failures,
        "rows": refreshed,
    }
    write_json(DATA_DIR / "full_market_candidates_20260715.json", output)
    write_json(
        DATA_DIR / "intraday_quote_refresh_20260715.json",
        {
            "schema_version": "astock.intraday_quote_refresh.v1",
            "data_cutoff": DATA_CUTOFF,
            "quote_count": len(quotes),
            "changed_price_count": len(changed),
            "failure_count": len(failures),
            "changed_rows": changed,
            "failures": failures,
            "source": "Tencent quote endpoint",
        },
    )
    lines = [
        "# Intraday Quote Refresh — 2026-07-15",
        "",
        f"- Candidate rows: {len(rows)}",
        f"- Quotes returned: {len(quotes)}",
        f"- Prices changed versus prior same-day snapshot: {len(changed)}",
        f"- Failures: {len(failures)}",
        "",
        "| Ticker | Company | Old price | New price | Quote timestamp |",
        "|---|---|---:|---:|---|",
    ]
    for row in changed:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['old_price']} | "
            f"{row['new_price']} | {row['quote_timestamp']} |"
        )
    (DATA_DIR / "intraday_quote_refresh_20260715.md").write_text(
        "\n".join(lines) + "\n"
    )
    print(
        json.dumps(
            {
                "candidate_count": len(rows),
                "quote_count": len(quotes),
                "changed_price_count": len(changed),
                "failure_count": len(failures),
                "changed_sample": changed[:10],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
