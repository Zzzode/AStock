#!/usr/bin/env python3
"""Build the 2026-07-15 sector stage from refreshed public flow packets."""

from __future__ import annotations

import concurrent.futures
import json
import math
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from build_market_scan import classify_sector, parse_float, parse_legulegu_valuation


CASE_DIR = Path(__file__).resolve().parents[1]
BASE_DATA_DIR = CASE_DIR / "data"
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
MARKET_DIR = DATA_DIR / "market"
DAILY_PATH = DATA_DIR / "raw_daily_tables_20260714.json"
WEEKLY_PATH = DATA_DIR / "raw_weekly_tables_20260710_refresh.json"
DATA_CUTOFF = "2026-07-15"
OBSERVATION_DATE = "2026-07-14"
SWS_URL = "https://www.swsresearch.com/institute-sw/api/index_publish/trend/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def paired_rows(packet: dict[str, Any]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for row in packet["rows"]:
        if isinstance(row, dict):
            result[str(row["industry"]).replace(" ", "")] = {
                "return_pct": float(row["return_pct"]),
                "flow_100mn": float(row["flow_100mn"]),
            }
            continue
        for offset in (0, 3):
            if len(row) < offset + 3:
                continue
            industry = str(row[offset]).replace(" ", "")
            change = parse_float(row[offset + 1])
            flow = parse_float(row[offset + 2])
            if industry and industry != "-" and change is not None and flow is not None:
                result[industry] = {"return_pct": change, "flow_100mn": flow}
    return result


def return_over_period(closes: pd.Series, days: int) -> float | None:
    if len(closes) <= days:
        return None
    return float((closes.iloc[-1] / closes.iloc[-days - 1] - 1) * 100)


def percentile_rank(values: pd.Series, current: float) -> float:
    clean = values.dropna()
    return float((clean <= current).mean() * 100) if not clean.empty else math.nan


def fetch_history(code: str) -> tuple[str, list[dict[str, Any]] | None, str | None]:
    for attempt in range(3):
        try:
            response = requests.get(
                SWS_URL,
                params={"swindexcode": code, "period": "DAY"},
                headers=HEADERS,
                verify=False,
                timeout=(5, 30),
            )
            response.raise_for_status()
            rows = (response.json().get("data") or [])
            if not rows:
                raise RuntimeError("empty SWS history")
            return code, rows, None
        except Exception as exc:
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
            error = repr(exc)
    return code, None, error


def load_histories(codes: list[str], daily: dict[str, dict[str, float]]) -> dict[str, dict[str, Any]]:
    histories: dict[str, dict[str, Any]] = {}
    pending: list[str] = []
    for code in codes:
        path = MARKET_DIR / f"raw_sw_index_{code}_20260714.json"
        if path.exists():
            rows = load_json(path)
            if rows:
                histories[code] = {
                    "rows": rows,
                    "history_source": "Shenwan official index history API",
                    "history_status": "official_through_2026-07-14"
                    if str(rows[-1].get("bargaindate", rows[-1].get("日期", "")))[:10]
                    == OBSERVATION_DATE
                    else "synthetic_current_close",
                    "fetch_error": None,
                }
                continue
        pending.append(code)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_history, code) for code in pending]
        for future in concurrent.futures.as_completed(futures):
            code, rows, error = future.result()
            path = MARKET_DIR / f"raw_sw_index_{code}_20260714.json"
            if rows:
                write_json(path, rows)
                histories[code] = {
                    "rows": rows,
                    "history_source": "Shenwan official index history API",
                    "history_status": "official_through_2026-07-14"
                    if str(rows[-1].get("bargaindate", ""))[:10] == OBSERVATION_DATE
                    else "official_stale",
                    "fetch_error": None,
                }
                continue
            old_path = BASE_DATA_DIR / f"raw_sw_index_{code}_20260710.json"
            old_rows = load_json(old_path) if old_path.exists() else []
            if not old_rows:
                raise RuntimeError(f"{code}: no official or archived index history")
            latest = dict(old_rows[-1])
            latest["日期"] = OBSERVATION_DATE
            latest["收盘"] = round(
                float(latest["收盘"]) * (1 + daily[code]["return_pct"] / 100), 6
            )
            rows = old_rows + [latest]
            write_json(path, rows)
            histories[code] = {
                "rows": rows,
                "history_source": "archived SWS history + current public daily return",
                "history_status": "synthetic_current_close",
                "fetch_error": error,
            }
    return histories


def price_metrics(code: str, history: dict[str, Any]) -> dict[str, Any]:
    frame = pd.DataFrame(history["rows"])
    if "bargaindate" in frame.columns:
        frame = frame.rename(
            columns={
                "bargaindate": "日期",
                "closeindex": "收盘",
                "openindex": "开盘",
                "maxindex": "最高",
                "minindex": "最低",
                "bargainamount": "成交量",
                "bargainsum": "成交额",
            }
        )
    frame["日期"] = pd.to_datetime(frame["日期"], errors="coerce")
    frame["收盘"] = pd.to_numeric(frame["收盘"], errors="coerce")
    frame = frame.sort_values("日期").dropna(subset=["收盘"])
    closes = frame["收盘"]
    current = float(closes.iloc[-1])
    one_year = frame.tail(250)
    three_year = frame.tail(750)
    high = float(one_year["收盘"].max())
    low = float(one_year["收盘"].min())
    return {
        "close": round(current, 4),
        "close_basis": history["history_status"],
        "price_observation_date": OBSERVATION_DATE,
        "return_20d_pct": round(return_over_period(closes, 20) or 0.0, 2),
        "return_60d_pct": round(return_over_period(closes, 60) or 0.0, 2),
        "return_120d_pct": round(return_over_period(closes, 120) or 0.0, 2),
        "return_250d_pct": round(return_over_period(closes, 250) or 0.0, 2),
        "drawdown_from_52w_high_pct": round((current / high - 1) * 100, 2),
        "price_position_52w_pct": round((current - low) / (high - low) * 100, 2)
        if high > low
        else 50.0,
        "price_percentile_3y_pct": round(percentile_rank(three_year["收盘"], current), 2),
        "price_history_status": history["history_status"],
        "price_fetch_error": history["fetch_error"],
    }


def main() -> None:
    daily_packet = load_json(DAILY_PATH)[0]
    weekly_packet = load_json(WEEKLY_PATH)[0]
    daily = paired_rows(daily_packet)
    weekly = paired_rows(weekly_packet)
    if len(daily) != 31 or len(weekly) != 31:
        raise AssertionError(f"flow coverage daily={len(daily)} weekly={len(weekly)}")
    valuation = parse_legulegu_valuation()
    codes = [value["industry_code"].split(".")[0] for value in valuation.values()]
    histories = load_histories(codes, daily)
    rows: list[dict[str, Any]] = []
    for industry, val in valuation.items():
        code = val["industry_code"].split(".")[0]
        row = {
            "industry": industry,
            **val,
            **price_metrics(code, histories[code]),
            "daily_return_pct": daily[industry]["return_pct"],
            "daily_flow_100mn": daily[industry]["flow_100mn"],
            "weekly_return_pct": weekly[industry]["return_pct"],
            "weekly_flow_100mn": weekly[industry]["flow_100mn"],
        }
        stage, rationale = classify_sector(row)
        row["stage"] = stage
        row["stage_rationale"] = rationale
        rows.append(row)
    stage_order = {
        "silent_accumulation": 0,
        "launch_confirmation": 1,
        "flow_watch": 2,
        "one_day_rebound": 3,
        "low_price_no_flow": 4,
        "no_signal": 5,
    }
    rows.sort(key=lambda row: (stage_order[row["stage"]], -row["weekly_flow_100mn"], row["weekly_return_pct"]))
    payload = {
        "schema_version": "astock.sector_scan.refresh.v2",
        "data_cutoff": DATA_CUTOFF,
        "flow_observation_date": OBSERVATION_DATE,
        "weekly_observation_end": weekly_packet["observation_end"],
        "universe_count": len(rows),
        "flow_source": {
            "daily": "data/raw_daily_tables_20260714.json",
            "weekly": "data/raw_weekly_tables_20260710_refresh.json",
            "daily_coverage": "31/31",
            "weekly_coverage": "31/31",
        },
        "price_source": "Shenwan official index history API with explicit synthetic fallback for failed codes",
        "price_history_status_counts": {
            status: sum(row["price_history_status"] == status for row in rows)
            for status in sorted({row["price_history_status"] for row in rows})
        },
        "rows": rows,
    }
    write_json(DATA_DIR / "sector_scan_20260715.json", payload)
    write_json(BASE_DATA_DIR / "sector_scan_20260715.json", payload)
    write_json(
        DATA_DIR / "continuous_inflow_candidates_20260714.json",
        load_json(DATA_DIR / "raw_continuous_tables_20260714.json")[0],
    )
    print(json.dumps({
        "sector_count": len(rows),
        "stage_counts": pd.Series([row["stage"] for row in rows]).value_counts().to_dict(),
        "price_history_status_counts": payload["price_history_status_counts"],
        "daily_coverage": "31/31",
        "weekly_coverage": "31/31",
        "continuous_coverage": "30/112 partial",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
