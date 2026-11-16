#!/usr/bin/env python3
"""Archive reproducible public market snapshots for the 2026-08-11 update.

This collector deliberately treats 2026-08-10 as the last completed session.
It records a separate 2026-08-11 pre-open quote snapshot, whose current-price
field may be an auction indication and must not be used as a closing price.

Sources:
* Tencent batch quote: name/code validation, pre-open state, market caps.
* Tencent qfq daily K-line: adjusted one-year price-position series.
* Sohu daily history: one-year unadjusted OHLCV, turnover amount and rate.

All responses are retained unchanged beneath this directory.  The normalized
packet is intentionally written only to the assigned case data directory.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CASE = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent
DATA = CASE / "data"
COLLECTION_DATE = "2026-08-11"
HISTORY_START = "2025-08-11"
HISTORY_END = "2026-08-11"
LAST_COMPLETED_SESSION = "2026-08-10"
TARGETS = [
    "000703",
    "002379",
    "300014",
    "002497",
    "002432",
    "000623",
    "600739",
    "000685",
    "600150",
    "301308",
    "002812",
    "002240",
    "300390",
]
USER_AGENT = "Mozilla/5.0 (compatible; AStockResearch/1.0)"


def now_cst() -> str:
    """Return ISO-like collection time in the project reporting timezone."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def market_symbol(code: str) -> str:
    return f"sh{code}" if code.startswith("6") else f"sz{code}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, errors: list[dict[str, str]], label: str) -> tuple[bytes, str] | None:
    """Fetch with bounded retries and retain explicit failure provenance."""
    last_error = ""
    for attempt in range(1, 4):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    # Sina requires an origin-style Referer; other public
                    # endpoints tolerate it and retain their own raw payloads.
                    "Referer": "https://finance.sina.com.cn/",
                },
            )
            with urlopen(request, timeout=30) as response:
                return response.read(), now_cst()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < 3:
                time.sleep(0.4 * attempt)
    errors.append({"label": label, "url": url, "attempts": "3", "error": last_error})
    return None


def archive(path: Path, raw: bytes) -> dict[str, Any]:
    path.write_bytes(raw)
    return {"path": str(path.relative_to(CASE)), "bytes": len(raw), "sha256": sha256(raw)}


def as_float(value: str | float | int | None) -> float | None:
    if value in (None, "", "--"):
        return None
    try:
        return float(str(value).replace("%", ""))
    except (TypeError, ValueError):
        return None


def round_or_none(value: float | None, digits: int = 2) -> float | None:
    return round(value, digits) if value is not None else None


def percent_change(current: float, prior: float) -> float | None:
    return round((current / prior - 1.0) * 100.0, 2) if prior else None


def parse_tencent_quote(raw: bytes) -> dict[str, list[str]]:
    text = raw.decode("gbk", errors="replace")
    return {
        code: body.split("~")
        for code, body in re.findall(r'v_(?:sh|sz)(\d+)="([^"]*)"', text)
    }


def parse_sina_quote(raw: bytes) -> dict[str, list[str]]:
    text = raw.decode("gbk", errors="replace")
    return {
        code: body.split(",")
        for code, body in re.findall(r'var hq_str_(?:sh|sz)(\d+)="([^"]*)";', text)
    }


def parse_tencent_kline(payload: dict[str, Any], code: str) -> tuple[list[list[Any]], list[str] | None]:
    symbol = market_symbol(code)
    data = payload.get("data") or {}
    section = data.get(symbol) or {}
    rows = section.get("qfqday") or section.get("day") or []
    qt = (section.get("qt") or {}).get(symbol)
    return rows, qt


def parse_sohu_daily(payload: Any) -> tuple[list[list[Any]], str | None, int | None]:
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], dict):
        return [], None, None
    root = payload[0]
    return root.get("hq") or [], root.get("code"), root.get("status")


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def qfq_metrics(rows: list[list[Any]]) -> dict[str, Any]:
    parsed = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 6:
            continue
        close = as_float(row[2])
        if close is None:
            continue
        parsed.append({
            "date": str(row[0]),
            "open_cny": as_float(row[1]),
            "close_cny": close,
            "high_cny": as_float(row[3]),
            "low_cny": as_float(row[4]),
            "volume_lots": as_float(row[5]),
        })
    parsed.sort(key=lambda item: item["date"])
    closes = [item["close_cny"] for item in parsed]
    if not closes:
        return {"history_status": "empty_or_unparseable"}
    high = max(closes)
    low = min(closes)
    last = closes[-1]
    result: dict[str, Any] = {
        "history_status": "full_calendar_year" if len(parsed) >= 200 else f"partial_{len(parsed)}_sessions",
        "observation_count": len(parsed),
        "first_date": parsed[0]["date"],
        "last_date": parsed[-1]["date"],
        "last_close_cny": last,
        "one_year_high_close_cny": high,
        "one_year_low_close_cny": low,
        "position_in_one_year_close_range_pct": round_or_none(
            (last - low) / (high - low) * 100.0 if high > low else 50.0
        ),
        "drawdown_from_one_year_high_pct": round_or_none((last / high - 1.0) * 100.0),
    }
    for days in (5, 20, 60, 120):
        result[f"return_{days}d_pct"] = (
            percent_change(last, closes[-(days + 1)]) if len(closes) > days else None
        )
    return result


def sohu_metrics(rows: list[list[Any]]) -> dict[str, Any]:
    parsed = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 10:
            continue
        close = as_float(row[2])
        amount_wan = as_float(row[8])
        volume_lots = as_float(row[7])
        if close is None or amount_wan is None or volume_lots is None:
            continue
        parsed.append({
            "date": str(row[0]),
            "open_cny": as_float(row[1]),
            "close_cny": close,
            "daily_change_cny": as_float(row[3]),
            "daily_change_pct": as_float(row[4]),
            "low_cny": as_float(row[5]),
            "high_cny": as_float(row[6]),
            "volume_lots": volume_lots,
            "trading_value_wan_cny": amount_wan,
            "trading_value_cny": amount_wan * 10_000.0,
            "turnover_rate_pct": as_float(row[9]),
        })
    parsed.sort(key=lambda item: item["date"])
    if not parsed:
        return {"history_status": "empty_or_unparseable"}
    recent5 = parsed[-5:]
    recent20 = parsed[-20:]
    return {
        "history_status": "full_calendar_year" if len(parsed) >= 200 else f"partial_{len(parsed)}_sessions",
        "observation_count": len(parsed),
        "first_date": parsed[0]["date"],
        "last_date": parsed[-1]["date"],
        "last_completed_close_cny": parsed[-1]["close_cny"],
        "last_completed_volume_lots": parsed[-1]["volume_lots"],
        "last_completed_trading_value_cny": parsed[-1]["trading_value_cny"],
        "last_completed_turnover_rate_pct": parsed[-1]["turnover_rate_pct"],
        "average_5d_trading_value_cny": round_or_none(
            average([item["trading_value_cny"] for item in recent5]), 2
        ),
        "average_20d_trading_value_cny": round_or_none(
            average([item["trading_value_cny"] for item in recent20]), 2
        ),
        "average_5d_volume_lots": round_or_none(
            average([item["volume_lots"] for item in recent5]), 2
        ),
        "average_20d_volume_lots": round_or_none(
            average([item["volume_lots"] for item in recent20]), 2
        ),
        "average_5d_turnover_rate_pct": round_or_none(
            average([item["turnover_rate_pct"] for item in recent5 if item["turnover_rate_pct"] is not None]),
            3,
        ),
        "average_20d_turnover_rate_pct": round_or_none(
            average([item["turnover_rate_pct"] for item in recent20 if item["turnover_rate_pct"] is not None]),
            3,
        ),
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    errors: list[dict[str, str]] = []
    sources: list[dict[str, Any]] = []
    captured_at = now_cst()

    symbols = [market_symbol(code) for code in TARGETS]
    tencent_url = "https://qt.gtimg.cn/q=" + ",".join(symbols)
    tencent_result = fetch(tencent_url, errors, "tencent_batch_quote")
    tencent_fields: dict[str, list[str]] = {}
    if tencent_result:
        raw, retrieved_at = tencent_result
        record = archive(RAW / "tencent_quote_preopen_20260811_raw.txt", raw)
        record.update({"source": "Tencent batch quote", "url": tencent_url, "retrieved_at": retrieved_at, "encoding": "gbk"})
        sources.append(record)
        tencent_fields = parse_tencent_quote(raw)

    sina_url = "https://hq.sinajs.cn/list=" + ",".join(symbols)
    sina_result = fetch(sina_url, errors, "sina_batch_quote")
    sina_fields: dict[str, list[str]] = {}
    if sina_result:
        raw, retrieved_at = sina_result
        record = archive(RAW / "sina_quote_preopen_20260811_raw.txt", raw)
        record.update({"source": "Sina batch quote", "url": sina_url, "retrieved_at": retrieved_at, "encoding": "gbk"})
        sources.append(record)
        sina_fields = parse_sina_quote(raw)

    kline_payloads: dict[str, dict[str, Any]] = {}
    sohu_payloads: dict[str, Any] = {}
    for code in TARGETS:
        symbol = market_symbol(code)
        kline_url = (
            "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param="
            f"{symbol},day,{HISTORY_START},{HISTORY_END},400,qfq"
        )
        result = fetch(kline_url, errors, f"tencent_qfq_{code}")
        if result:
            raw, retrieved_at = result
            record = archive(RAW / f"tencent_qfq_{code}_20250811_20260811.json", raw)
            record.update({"source": "Tencent adjusted daily K-line", "url": kline_url, "retrieved_at": retrieved_at, "encoding": "utf-8"})
            sources.append(record)
            try:
                kline_payloads[code] = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append({"label": f"tencent_qfq_decode_{code}", "url": kline_url, "attempts": "1", "error": repr(exc)})

        sohu_url = (
            "https://q.stock.sohu.com/hisHq?"
            f"code=cn_{code}&start=20250811&end=20260811&stat=1&order=D&period=d"
        )
        result = fetch(sohu_url, errors, f"sohu_daily_{code}")
        if result:
            raw, retrieved_at = result
            record = archive(RAW / f"sohu_daily_{code}_20250811_20260811.json", raw)
            record.update({"source": "Sohu daily OHLCV / trading value history", "url": sohu_url, "retrieved_at": retrieved_at, "encoding": "gbk"})
            sources.append(record)
            try:
                # Sohu returns mostly ASCII numeric JSON but its ``stat`` label
                # is GBK-encoded; decoding bytes as UTF-8 rejects an otherwise
                # valid response. Preserve the original bytes in the archive
                # and decode GBK only for structured parsing.
                sohu_payloads[code] = json.loads(raw.decode("gbk", errors="replace"))
            except json.JSONDecodeError as exc:
                errors.append({"label": f"sohu_daily_decode_{code}", "url": sohu_url, "attempts": "1", "error": repr(exc)})

    rows: list[dict[str, Any]] = []
    for code in TARGETS:
        tf = tencent_fields.get(code, [])
        sf = sina_fields.get(code, [])
        kline_rows, kline_qt = parse_tencent_kline(kline_payloads.get(code, {}), code)
        sohu_rows, sohu_code, sohu_status = parse_sohu_daily(sohu_payloads.get(code, []))
        qfq = qfq_metrics(kline_rows)
        sohu = sohu_metrics(sohu_rows)
        quote_time = tf[30] if len(tf) > 30 else None
        qfq_name = kline_qt[1] if kline_qt and len(kline_qt) > 2 else None
        qfq_code = kline_qt[2] if kline_qt and len(kline_qt) > 2 else None
        tencent_name = tf[1] if len(tf) > 2 else None
        tencent_code = tf[2] if len(tf) > 2 else None
        sina_name = sf[0] if sf else None
        preopen_volume = as_float(tf[6]) if len(tf) > 6 else None
        preopen_amount_wan = as_float(tf[57]) if len(tf) > 57 else None
        preopen = {
            "quote_timestamp_source": quote_time,
            "current_price_or_auction_indication_cny": as_float(tf[3]) if len(tf) > 3 else None,
            "previous_close_cny": as_float(tf[4]) if len(tf) > 4 else None,
            "open_cny": as_float(tf[5]) if len(tf) > 5 else None,
            "intraday_volume_lots": preopen_volume,
            "intraday_trading_value_cny": preopen_amount_wan * 10_000.0 if preopen_amount_wan is not None else None,
            "intraday_change_pct": as_float(tf[32]) if len(tf) > 32 else None,
            "float_market_cap_100mn_cny": as_float(tf[44]) if len(tf) > 44 else None,
            "total_market_cap_100mn_cny": as_float(tf[45]) if len(tf) > 45 else None,
            "float_shares": as_float(tf[72]) if len(tf) > 72 else None,
            "total_shares": as_float(tf[73]) if len(tf) > 73 else None,
            "zero_trade": preopen_volume == 0 and preopen_amount_wan == 0,
            "interpretation": "Pre-open snapshot; do not use the current-price field as a completed-session close.",
        }
        last_sohu_close = sohu.get("last_completed_close_cny")
        last_qfq_close = qfq.get("last_close_cny")
        name_match = bool(
            tencent_name
            and tencent_name == qfq_name
            and tencent_name == sina_name
            and code == tencent_code == qfq_code
            and sohu_code == f"cn_{code}"
        )
        close_match = (
            abs(last_sohu_close - last_qfq_close) < 0.011
            if isinstance(last_sohu_close, float) and isinstance(last_qfq_close, float)
            else False
        )
        quality = "high" if name_match and close_match and qfq.get("history_status") == "full_calendar_year" and sohu.get("history_status") == "full_calendar_year" else "medium_or_degraded"
        rows.append({
            "ticker": code,
            "exchange_symbol": market_symbol(code),
            "company": tencent_name,
            "data_quality": quality,
            "ticker_name_validation": {
                "requested_ticker": code,
                "tencent_quote_code": tencent_code,
                "tencent_kline_code": qfq_code,
                "sohu_code": sohu_code,
                "tencent_quote_name": tencent_name,
                "tencent_kline_name": qfq_name,
                "sina_quote_name": sina_name,
                "all_code_and_name_checks_pass": name_match,
                "sohu_status": sohu_status,
            },
            "last_completed_session": LAST_COMPLETED_SESSION,
            "last_completed_session_close": {
                "close_cny": last_sohu_close,
                "source": "Sohu daily OHLCV",
                "cross_checked_with_tencent_qfq_close_cny": last_qfq_close,
                "cross_source_close_match": close_match,
            },
            "pre_open_snapshot_20260811": preopen,
            "adjusted_price_position_one_year": qfq,
            "daily_trading_value_one_year": sohu,
            "field_boundaries": {
                "price_position": "Tencent qfq adjusted daily close series; raw response archived.",
                "trading_value": "Sohu daily trading amount, directly reported in CNY after converting its stated 10,000-CNY unit; not a price-times-volume proxy.",
                "market_cap": "Tencent pre-open snapshot only; it can reflect auction-indicative price rather than the 2026-08-10 close.",
            },
        })

    completed = sum(row["data_quality"] == "high" for row in rows)
    packet = {
        "schema_version": "astock.raw_market_data.v1",
        "case": CASE.name,
        "collection_started_at": captured_at,
        "collection_finished_at": now_cst(),
        "collection_date": COLLECTION_DATE,
        "session_context": {
            "system_clock_context": "2026-08-11 pre-open / call-auction window",
            "last_completed_session": LAST_COMPLETED_SESSION,
            "completed_session_close_policy": "Use 2026-08-10 daily close for completed-session price. Keep 2026-08-11 snapshot separate.",
        },
        "universe": TARGETS,
        "row_count": len(rows),
        "high_quality_row_count": completed,
        "data_quality": "high" if completed == len(rows) and not errors else "partial_or_degraded",
        "warnings": [
            "The preferred astock CLI adapter was unavailable because .venv/bin/python was absent.",
            "2026-08-11 is pre-open: all quote current-price fields are auction indications or last values, not completed-session closes.",
            "Sohu daily series is unadjusted and is used only for directly reported daily turnover value/rate; adjusted Tencent daily closes drive one-year price-position metrics.",
            "Pre-open Tencent turnover can be zero by design and must not replace the 2026-08-10 completed-session turnover value.",
        ],
        "fallback_path": "astock CLI unavailable -> Tencent public batch quote + Tencent qfq K-line + Sohu daily OHLCV/trading value",
        "errors": errors,
        "sources": sources,
        "rows": rows,
    }
    json_path = DATA / "raw_market_data_20260811.json"
    json_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Raw Market Data — 2026-08-11 Pre-Open",
        "",
        f"- Collection window: {packet['collection_started_at']} to {packet['collection_finished_at']}",
        "- Completed-session close date: 2026-08-10 (the 2026-08-11 collection was pre-open).",
        "- Data path: Tencent public batch quote + Tencent adjusted daily K-line + Sohu daily OHLCV/trading value.",
        "- Degradation: the preferred local astock CLI was unavailable because `.venv/bin/python` was absent.",
        "",
        "| Ticker | Company | 8/10 close | 8/11 pre-open indication | 1Y position (adj.) | 1Y high / low (adj.) | 8/10 trading value | 5d avg trading value | Pre-open zero trade | Validation |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        q = row["adjusted_price_position_one_year"]
        s = row["daily_trading_value_one_year"]
        p = row["pre_open_snapshot_20260811"]
        v = row["ticker_name_validation"]
        value = s.get("last_completed_trading_value_cny")
        average5 = s.get("average_5d_trading_value_cny")
        lines.append(
            "| {ticker} | {company} | {close} | {indication} | {position} | {high} / {low} | {value} | {average5} | {zero} | {validation} |".format(
                ticker=row["ticker"],
                company=row["company"] or "n/a",
                close=f"{row['last_completed_session_close'].get('close_cny'):.2f}" if row["last_completed_session_close"].get("close_cny") is not None else "n/a",
                indication=f"{p.get('current_price_or_auction_indication_cny'):.2f}" if p.get("current_price_or_auction_indication_cny") is not None else "n/a",
                position=f"{q.get('position_in_one_year_close_range_pct'):.2f}%" if q.get("position_in_one_year_close_range_pct") is not None else "n/a",
                high=f"{q.get('one_year_high_close_cny'):.2f}" if q.get("one_year_high_close_cny") is not None else "n/a",
                low=f"{q.get('one_year_low_close_cny'):.2f}" if q.get("one_year_low_close_cny") is not None else "n/a",
                value=f"CNY {value / 1e9:.2f}bn" if value is not None else "n/a",
                average5=f"CNY {average5 / 1e9:.2f}bn" if average5 is not None else "n/a",
                zero="yes" if p.get("zero_trade") else "no / unavailable",
                validation="pass" if v.get("all_code_and_name_checks_pass") else "review",
            )
        )
    lines += [
        "",
        "## Use Boundary",
        "",
        "- Use `last_completed_session_close.close_cny` for 2026-08-10 close-based comparisons.",
        "- Do not use `pre_open_snapshot_20260811.current_price_or_auction_indication_cny` as a close or as a realized 2026-08-11 return.",
        "- Trading values are direct Sohu daily observations (CNY); no price-times-volume estimate was substituted.",
        "- Full source URLs, retrieval times, file hashes, raw responses, and any failures are in `raw_market_data_20260811.json`.",
    ]
    (DATA / "raw_market_data_20260811.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": "astock.market_collection_manifest.v1",
        "collection_date": COLLECTION_DATE,
        "created_at": now_cst(),
        "collector": str(Path(__file__).relative_to(CASE)),
        "raw_source_count": len(sources),
        "source_records": sources,
        "errors": errors,
        "normalized_outputs": [
            "data/raw_market_data_20260811.json",
            "data/raw_market_data_20260811.md",
        ],
    }
    (RAW / "collection_manifest_20260811.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "rows": len(rows),
        "high_quality_rows": completed,
        "raw_source_count": len(sources),
        "errors": errors,
        "packet": str(json_path.relative_to(CASE)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
