#!/usr/bin/env python3
"""Build a reproducible sector and continuous-inflow market scan."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "market-20260711"
DATA_CUTOFF = "2026-07-10"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text in {"-", "null", "None"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_legulegu_valuation() -> dict[str, dict[str, Any]]:
    html = (SOURCE_DIR / "legulegu_sw_industry_overview_20260711.html").read_text(
        errors="ignore"
    )
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, dict[str, Any]] = {}
    level_one = soup.select_one("#level1Items")
    if level_one is None:
        raise RuntimeError("Legulegu level-one valuation block is missing")
    for item in level_one.select(".lg-industries-item"):
        code = item.get("id", "")
        name_node = item.select_one(".lg-industries-item-number")
        values = item.select(".lg-sw-industries-value")
        if not code or name_node is None or len(values) < 4:
            continue
        name = re.sub(r"\(\d+\)$", "", name_node.get_text(strip=True))
        parsed_values: list[tuple[float | None, float | None]] = []
        for value in values[:4]:
            number = parse_float(
                value.select_one(".value").get_text(strip=True)
                if value.select_one(".value")
                else None
            )
            quantile = parse_float(
                value.select_one(".quantile").get_text(" ", strip=True).split()[0]
                if value.select_one(".quantile")
                else None
            )
            parsed_values.append((number, quantile))
        result[name] = {
            "industry_code": code,
            "pe_static": parsed_values[0][0],
            "pe_static_percentile": parsed_values[0][1],
            "pe_ttm": parsed_values[1][0],
            "pe_ttm_percentile": parsed_values[1][1],
            "pb": parsed_values[2][0],
            "pb_percentile": parsed_values[2][1],
            "dividend_yield": parsed_values[3][0],
            "dividend_yield_percentile": parsed_values[3][1],
        }
    if len(result) != 31:
        raise RuntimeError(f"Expected 31 first-level industries, found {len(result)}")
    return result


def paired_industry_rows(table: dict[str, Any]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for row in table["rows"]:
        for offset in (0, 3):
            if len(row) < offset + 3:
                continue
            industry = row[offset].strip()
            if not industry or industry == "-":
                continue
            change = parse_float(row[offset + 1])
            flow = parse_float(row[offset + 2])
            if change is None or flow is None:
                continue
            result[industry] = {"return_pct": change, "flow_100mn": flow}
    return result


def load_fund_flows() -> tuple[dict[str, Any], dict[str, Any]]:
    daily_tables = load_json(DATA_DIR / "raw_daily_tables_20260710.json")
    weekly_tables = load_json(DATA_DIR / "raw_weekly_tables_20260710.json")
    daily = paired_industry_rows(daily_tables[0])
    weekly = paired_industry_rows(weekly_tables[-1])
    if len(daily) != 31 or len(weekly) != 31:
        raise RuntimeError(
            f"Industry flow coverage mismatch: daily={len(daily)}, weekly={len(weekly)}"
        )
    return daily, weekly


def return_over_period(closes: pd.Series, days: int) -> float | None:
    if len(closes) <= days:
        return None
    return float((closes.iloc[-1] / closes.iloc[-days - 1] - 1) * 100)


def percentile_rank(values: pd.Series, current: float) -> float:
    clean = values.dropna()
    if clean.empty:
        return math.nan
    return float((clean <= current).mean() * 100)


def load_price_metrics(
    code: str, daily_change: float
) -> tuple[dict[str, Any], pd.DataFrame]:
    path = DATA_DIR / f"raw_sw_index_{code}_20260710.json"
    df = pd.DataFrame(load_json(path))
    df["日期"] = pd.to_datetime(df["日期"])
    for column in ("收盘", "开盘", "最高", "最低", "成交量", "成交额"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.sort_values("日期").dropna(subset=["收盘"])
    if df.empty:
        raise RuntimeError(f"No price history for {code}")
    latest_date = df.iloc[-1]["日期"].strftime("%Y-%m-%d")
    latest_close = float(df.iloc[-1]["收盘"])
    if latest_date < DATA_CUTOFF:
        synthetic_close = latest_close * (1 + daily_change / 100)
        synthetic = {
            "代码": code,
            "日期": pd.Timestamp(DATA_CUTOFF),
            "收盘": synthetic_close,
            "开盘": math.nan,
            "最高": math.nan,
            "最低": math.nan,
            "成交量": math.nan,
            "成交额": math.nan,
        }
        df = pd.concat([df, pd.DataFrame([synthetic])], ignore_index=True)
    closes = df["收盘"]
    one_year = df.tail(250)
    three_year = df.tail(750)
    current = float(closes.iloc[-1])
    high_52w = float(one_year["收盘"].max())
    low_52w = float(one_year["收盘"].min())
    price_position_52w = (
        (current - low_52w) / (high_52w - low_52w) * 100
        if high_52w > low_52w
        else 50.0
    )
    metrics = {
        "close": round(current, 4),
        "close_basis": (
            "official"
            if latest_date == DATA_CUTOFF
            else "2026-07-09 SWS close compounded by 2026-07-10 official daily return"
        ),
        "return_20d_pct": round(return_over_period(closes, 20) or 0.0, 2),
        "return_60d_pct": round(return_over_period(closes, 60) or 0.0, 2),
        "return_120d_pct": round(return_over_period(closes, 120) or 0.0, 2),
        "return_250d_pct": round(return_over_period(closes, 250) or 0.0, 2),
        "drawdown_from_52w_high_pct": round((current / high_52w - 1) * 100, 2),
        "price_position_52w_pct": round(price_position_52w, 2),
        "price_percentile_3y_pct": round(percentile_rank(three_year["收盘"], current), 2),
    }
    return metrics, df


def classify_sector(row: dict[str, Any]) -> tuple[str, str]:
    weekly_flow = row["weekly_flow_100mn"]
    weekly_return = row["weekly_return_pct"]
    daily_flow = row["daily_flow_100mn"]
    daily_return = row["daily_return_pct"]
    position = row["price_position_52w_pct"]
    valuation = min(
        row["pe_ttm_percentile"] if row["pe_ttm_percentile"] is not None else 100,
        row["pb_percentile"] if row["pb_percentile"] is not None else 100,
    )

    if (
        weekly_flow > 0
        and daily_flow > 0
        and daily_return >= 2.0
        and position <= 75
    ):
        return (
            "launch_confirmation",
            "Prior accumulation is now visible in price; no longer a purely quiet setup.",
        )
    if (
        weekly_flow > 0
        and daily_flow > 0
        and weekly_return <= 2.0
        and position <= 65
        and valuation <= 55
    ):
        return (
            "silent_accumulation",
            "Weekly and daily inflows coexist while price and valuation remain restrained.",
        )
    if weekly_flow > 0 and weekly_return <= 3.0:
        return (
            "flow_watch",
            "Weekly inflow exists, but price position or valuation does not meet the quiet-layout gate.",
        )
    if daily_flow > 0 and weekly_flow <= 0:
        return (
            "one_day_rebound",
            "Positive daily flow is not confirmed by the full week.",
        )
    if position <= 35 and weekly_flow <= 0:
        return (
            "low_price_no_flow",
            "Low price position without confirming capital accumulation.",
        )
    return ("no_signal", "No low-position accumulation signal under the defined gates.")


def build_sector_scan() -> list[dict[str, Any]]:
    valuation = parse_legulegu_valuation()
    daily, weekly = load_fund_flows()
    rows: list[dict[str, Any]] = []
    for industry, val in valuation.items():
        if industry not in daily or industry not in weekly:
            raise RuntimeError(f"Missing fund-flow row for {industry}")
        code = val["industry_code"].split(".")[0]
        price, _ = load_price_metrics(code, daily[industry]["return_pct"])
        row = {
            "industry": industry,
            **val,
            **price,
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
    rows.sort(
        key=lambda item: (
            stage_order[item["stage"]],
            -item["weekly_flow_100mn"],
            item["weekly_return_pct"],
        )
    )
    return rows


def build_continuous_inflow_scan() -> list[dict[str, Any]]:
    tables = load_json(DATA_DIR / "raw_continuous_tables_20260710.json")
    rows: list[dict[str, Any]] = []
    for row in tables[0]["rows"]:
        if len(row) < 6:
            continue
        gain = parse_float(row[5])
        inflow = parse_float(row[3])
        inflow_days = parse_float(row[2])
        inflow_ratio = parse_float(row[4])
        if None in {gain, inflow, inflow_days, inflow_ratio}:
            continue
        stage = (
            "quiet_stock_candidate"
            if gain <= 6 and inflow_days >= 5
            else "price_already_reacting"
        )
        rows.append(
            {
                "ticker": row[0],
                "company": row[1],
                "continuous_inflow_days": int(inflow_days),
                "cumulative_inflow_100mn": inflow,
                "inflow_to_turnover_pct": inflow_ratio,
                "cumulative_return_pct": gain,
                "stage": stage,
            }
        )
    rows.sort(
        key=lambda item: (
            item["stage"] != "quiet_stock_candidate",
            -item["continuous_inflow_days"],
            -item["cumulative_inflow_100mn"],
        )
    )
    return rows


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Full-Market Sector Scan",
        "",
        f"- Data cutoff: {DATA_CUTOFF}",
        "- Universe: all 31 Shenwan first-level industries",
        "- Price history: SWS Research; 2026-07-10 close is compounded from the "
        "2026-07-09 official close using the 2026-07-10 Wind/DataBao industry return.",
        "- Valuation: Legulegu Shenwan industry overview, updated 2026-07-10.",
        "- Fund flow: Securities Times/DataBao structured daily and weekly tables.",
        "",
        "| Industry | Stage | W flow (CNY100mn) | W ret | D flow | 52w pos | 52w DD | 3y pct | PE TTM pct | PB pct |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {industry} | {stage} | {weekly_flow_100mn:.2f} | "
            "{weekly_return_pct:.2f}% | {daily_flow_100mn:.2f} | "
            "{price_position_52w_pct:.1f}% | {drawdown_from_52w_high_pct:.1f}% | "
            "{price_percentile_3y_pct:.1f}% | {pe_ttm_percentile:.1f}% | "
            "{pb_percentile:.1f}% |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            "The scan detects price-flow configurations; it does not prove beneficial "
            "ownership, insider accumulation, undisclosed orders, or future returns. "
            "Daily main-flow data are transaction-size classifications rather than "
            "verified investor identities.",
            "",
        ]
    )
    return "\n".join(lines)


def continuous_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Continuous Main-Fund Inflow Candidates",
        "",
        f"- Data cutoff: {DATA_CUTOFF}",
        "- Source: Securities Times/DataBao continuous-inflow table.",
        "",
        "| Ticker | Company | Days | Inflow (CNY100mn) | Inflow/turnover | Return | Stage |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {ticker} | {company} | {continuous_inflow_days} | "
            "{cumulative_inflow_100mn:.2f} | {inflow_to_turnover_pct:.2f}% | "
            "{cumulative_return_pct:.2f}% | {stage} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            "Continuous main-fund inflow is a market-behavior screen, not proof of "
            "institutional ownership or a recommendation. Company-level price position, "
            "valuation, earnings quality, catalysts, and invalidation must be checked "
            "before an investable action is assigned.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    sector_rows = build_sector_scan()
    continuous_rows = build_continuous_inflow_scan()
    write_json(
        DATA_DIR / "sector_scan_20260710.json",
        {
            "schema_version": "astock.sector_scan.v1",
            "data_cutoff": DATA_CUTOFF,
            "universe_count": len(sector_rows),
            "rows": sector_rows,
        },
    )
    (DATA_DIR / "sector_scan_20260710.md").write_text(markdown_table(sector_rows))
    write_json(
        DATA_DIR / "continuous_inflow_candidates_20260710.json",
        {
            "schema_version": "astock.continuous_inflow.v1",
            "data_cutoff": DATA_CUTOFF,
            "row_count": len(continuous_rows),
            "rows": continuous_rows,
        },
    )
    (DATA_DIR / "continuous_inflow_candidates_20260710.md").write_text(
        continuous_markdown(continuous_rows)
    )
    print(
        json.dumps(
            {
                "sector_count": len(sector_rows),
                "stage_counts": pd.Series(
                    [row["stage"] for row in sector_rows]
                ).value_counts().to_dict(),
                "continuous_inflow_count": len(continuous_rows),
                "quiet_stock_count": sum(
                    row["stage"] == "quiet_stock_candidate"
                    for row in continuous_rows
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
