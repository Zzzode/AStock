#!/usr/bin/env python3
"""Build 2026H1 earnings-preview quality and implied-Q2 analytics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"


QUALITY_OVERRIDES = {
    "000938": (
        "operating_plus_structural_and_oneoff",
        "ICT/AI growth and higher H3C ownership are positive, but CNY0.25-0.35bn "
        "non-recurring gains and the completed ownership transaction inflate H1 growth.",
    ),
    "000977": (
        "operating_plus_material_nonrecurring",
        "AI-server volume, product mix and supply assurance drive the profit step-up, "
        "but the disclosed parent-to-deducted midpoint gap is about 19% of H1 profit.",
    ),
    "002396": (
        "operating_plus_oneoff",
        "Data-center switches drive growth, but CNY0.10-0.12bn non-recurring gains "
        "represent a material share of H1 net profit.",
    ),
    "301165": (
        "core_operating_delivery",
        "Internet-customer data-center switches are the primary driver and "
        "non-recurring gains are small.",
    ),
    "601138": (
        "core_operating_delivery",
        "AI-server revenue growth above 230% and 800G+ switch shipment growth provide "
        "direct operating evidence.",
    ),
    "001339": (
        "core_operating_delivery",
        "AI compute and ICT infrastructure shipment growth drive the preview.",
    ),
    "301308": (
        "core_operating_cycle_and_mix",
        "Storage prices, secured wafer supply, enterprise/AI mix and self-developed "
        "technology drive earnings; cycle and cash-flow risks remain.",
    ),
    "300475": (
        "core_operating_cycle_and_mix",
        "Distribution margin expansion and Hipu Storage commercialization drive earnings; "
        "non-recurring gains are minor relative to profit.",
    ),
    "603986": (
        "operating_plus_fair_value",
        "Storage and MCU volume/price growth are real, but securities fair-value gains "
        "inflate reported net profit; use deducted profit for valuation refresh.",
    ),
    "600685": (
        "core_operating_plus_investment_income",
        "Order mix and production efficiency improve gross profit, while associates and "
        "dividends also contribute.",
    ),
    "002829": (
        "nonrecurring_dominated",
        "Operating revenue declined and deducted profit remains negative; investment "
        "income of about CNY0.14bn creates the reported turnaround.",
    ),
    "600601": (
        "core_operating_delivery",
        "High-end PCB orders and product-mix improvement drive profit; deducted-profit "
        "growth is aligned with reported profit growth.",
    ),
    "000636": (
        "core_operating_cycle_and_mix",
        "MLCC/resistor/inductor volume and price growth plus cost reduction drive profit.",
    ),
    "001314": (
        "operating_plus_oneoff",
        "AI terminal sales and scale benefits improve operations, but CNY0.086bn "
        "investment income is material.",
    ),
    "002407": (
        "core_operating_cycle_and_mix",
        "LiPF6 volume/price recovery, integrated materials and battery volume drive profit.",
    ),
    "002842": (
        "core_operating_cycle_and_price",
        "Tungsten price pass-through drives revenue and profit; monitor working capital "
        "and downstream price elasticity.",
    ),
}

POST_PREVIEW_EPS_OVERRIDES = {
    "601138": 2.82,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def financial_path(ticker: str) -> Path | None:
    candidates = [
        DATA_DIR / "all_core_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "core_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "preview_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "launched_financials" / f"{ticker}_20260710.json",
        DATA_DIR / "financials" / f"{ticker}_20260710.json",
    ]
    return next((path for path in candidates if path.exists() and path.stat().st_size), None)


def first_quarter_metrics(ticker: str) -> dict[str, float | None]:
    path = financial_path(ticker)
    if path is None:
        return {
            "q1_net_profit_100mn": None,
            "q1_eps": None,
            "shares_100mn": None,
        }
    payload = load_json(path)
    periods = payload.get("periods") or payload.get("statements") or []
    for period in periods:
        if str(period.get("period")) == "20260331":
            metrics = period.get("metrics") or {}
            profit = metrics.get("net_profit_parent")
            deducted_profit = metrics.get("net_profit_deducted")
            eps = metrics.get("eps_basic")
            equity = metrics.get("equity")
            bps = metrics.get("bps")
            profit_100mn = float(profit) / 1e8 if profit is not None else None
            deducted_profit_100mn = (
                float(deducted_profit) / 1e8
                if deducted_profit is not None
                else None
            )
            shares_100mn = None
            shares_source = None
            if equity is not None and bps not in (None, 0):
                shares_100mn = float(equity) / 1e8 / float(bps)
                shares_source = "q1_equity_divided_by_bps"
            elif profit_100mn is not None and eps not in (None, 0):
                shares_100mn = profit_100mn / float(eps)
                shares_source = "q1_parent_profit_divided_by_eps_fallback"
            return {
                "q1_net_profit_100mn": profit_100mn,
                "q1_deducted_profit_100mn": deducted_profit_100mn,
                "q1_eps": float(eps) if eps is not None else None,
                "shares_100mn": shares_100mn,
                "shares_source": shares_source,
            }
    return {
        "q1_net_profit_100mn": None,
        "q1_deducted_profit_100mn": None,
        "q1_eps": None,
        "shares_100mn": None,
        "shares_source": None,
    }


def raw_preview_metric_map() -> dict[str, dict[str, dict[str, Any]]]:
    packet = load_json(DATA_DIR / "raw_a_share_h1_2026_preview_20260711.json")
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for row in packet["rows"]:
        ticker = str(row["股票代码"]).zfill(6)
        result.setdefault(ticker, {})[str(row["预测指标"])] = row
    return result


def kline_metrics(ticker: str) -> dict[str, float | None]:
    path = DATA_DIR / f"raw_kline_{ticker}_20260710.json"
    if not path.exists():
        return {"return_20d_pct": None, "return_60d_pct": None, "position_1y_pct": None}
    payload = load_json(path).get("data", {})
    key = next((item for item in payload if item not in {"qt", "market"}), None)
    if key is None:
        return {"return_20d_pct": None, "return_60d_pct": None, "position_1y_pct": None}
    rows = payload[key].get("qfqday") or payload[key].get("day") or []
    closes = [float(row[2]) for row in rows if len(row) >= 3]
    if not closes:
        return {"return_20d_pct": None, "return_60d_pct": None, "position_1y_pct": None}
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
        "position_1y_pct": round((current - low) / (high - low) * 100, 2)
        if high > low
        else 50.0,
    }


def quote_map() -> dict[str, dict[str, Any]]:
    payload = load_json(DATA_DIR / "raw_preview_quotes_20260710.json")
    return {row["code"]: row for row in payload.get("ticks", [])}


def main() -> None:
    census = load_json(DATA_DIR / "core_universe_preview_census_20260711.json")
    report_catalog = load_json(DATA_DIR / "core_broker_report_catalog_20260711.json")
    report_map = {row["ticker"]: row for row in report_catalog["metadata_rows"]}
    preview_metric_map = raw_preview_metric_map()
    quotes = quote_map()
    rows: list[dict[str, Any]] = []
    for preview in census["rows"]:
        if preview["preview_status"] != "disclosed":
            continue
        ticker = preview["ticker"]
        h1_mid = float(preview["forecast_midpoint_cny"]) / 1e8
        official_metrics = preview_metric_map.get(ticker, {})
        deducted_preview = official_metrics.get("扣除非经常性损益后的净利润")
        official_eps_preview = official_metrics.get("每股收益")
        h1_deducted_mid = (
            float(deducted_preview["预测数值"]) / 1e8
            if deducted_preview is not None
            and deducted_preview.get("预测数值") is not None
            else None
        )
        official_h1_eps = (
            float(official_eps_preview["预测数值"])
            if official_eps_preview is not None
            and official_eps_preview.get("预测数值") is not None
            else None
        )
        q1_metrics = first_quarter_metrics(ticker)
        q1 = q1_metrics["q1_net_profit_100mn"]
        shares_100mn = q1_metrics["shares_100mn"]
        q2_implied = round(h1_mid - q1, 2) if q1 is not None else None
        h1_eps_midpoint = official_h1_eps
        h1_eps_source = (
            "official_preview_eps"
            if official_h1_eps is not None
            else (
                "preview_parent_profit_divided_by_q1_equity_bps_shares"
                if shares_100mn not in (None, 0)
                else "not_available"
            )
        )
        if h1_eps_midpoint is None and shares_100mn not in (None, 0):
            h1_eps_midpoint = round(h1_mid / shares_100mn, 4)
        q1_deducted = q1_metrics.get("q1_deducted_profit_100mn")
        q2_implied_deducted = (
            round(h1_deducted_mid - q1_deducted, 2)
            if h1_deducted_mid is not None and q1_deducted is not None
            else None
        )
        latest_2026e_eps = POST_PREVIEW_EPS_OVERRIDES.get(
            ticker, report_map.get(ticker, {}).get("latest_2026e_eps")
        )
        h1_eps_to_latest_2026e_eps_ratio = (
            round(h1_eps_midpoint / float(latest_2026e_eps), 4)
            if h1_eps_midpoint is not None and latest_2026e_eps not in (None, 0)
            else None
        )
        nonrecurring = (
            round(h1_mid - h1_deducted_mid, 4)
            if h1_deducted_mid is not None
            else None
        )
        nonrecurring_share = (
            round(nonrecurring / h1_mid * 100, 2)
            if nonrecurring is not None and h1_mid
            else None
        )
        quality_class, quality_reason = QUALITY_OVERRIDES[ticker]
        quote = quotes.get(ticker, {})
        row = {
            **preview,
            "h1_net_profit_midpoint_100mn": round(h1_mid, 2),
            "q1_net_profit_100mn": round(q1, 2) if q1 is not None else None,
            "q1_deducted_profit_100mn": (
                round(q1_deducted, 2) if q1_deducted is not None else None
            ),
            "q1_eps": q1_metrics["q1_eps"],
            "shares_100mn": round(shares_100mn, 4)
            if shares_100mn is not None
            else None,
            "h1_eps_midpoint": h1_eps_midpoint,
            "h1_eps_source": h1_eps_source,
            "shares_source": q1_metrics.get("shares_source"),
            "h1_deducted_profit_midpoint_100mn": (
                round(h1_deducted_mid, 2)
                if h1_deducted_mid is not None
                else None
            ),
            "latest_2026e_eps": latest_2026e_eps,
            "h1_eps_to_latest_2026e_eps_ratio": h1_eps_to_latest_2026e_eps_ratio,
            "q2_implied_net_profit_100mn": q2_implied,
            "q2_implied_deducted_profit_100mn": q2_implied_deducted,
            "q2_vs_q1_pct": round((q2_implied / q1 - 1) * 100, 2)
            if q1 not in (None, 0) and q2_implied is not None
            else None,
            "nonrecurring_midpoint_100mn": nonrecurring,
            "nonrecurring_share_pct": nonrecurring_share,
            "quality_class": quality_class,
            "quality_reason": quality_reason,
            "current_price": quote.get("price"),
            "daily_change_pct": quote.get("change_pct"),
            "trading_value_100mn": round(float(quote.get("amount", 0)) / 1e8, 2)
            if quote
            else None,
            **kline_metrics(ticker),
        }
        rows.append(row)

    priority_order = {
        "core_operating_delivery": 0,
        "core_operating_cycle_and_mix": 1,
        "core_operating_plus_investment_income": 2,
        "core_operating_cycle_and_price": 3,
        "operating_plus_structural_and_oneoff": 4,
        "operating_plus_fair_value": 5,
        "operating_plus_oneoff": 6,
        "nonrecurring_dominated": 7,
    }
    rows.sort(
        key=lambda row: (
            priority_order.get(row["quality_class"], 99),
            -row["h1_net_profit_midpoint_100mn"],
        )
    )
    write_json(
        DATA_DIR / "earnings_preview_quality_20260711.json",
        {
            "schema_version": "astock.earnings_preview_quality.v1",
            "data_cutoff": "2026-07-11",
            "row_count": len(rows),
            "rows": rows,
        },
    )

    lines = [
        "# 2026H1 Earnings Preview Quality Review",
        "",
        "| Sector | Ticker | Company | H1 NP | H1 EPS | Latest 2026E EPS | H1/full-year EPS | Q1 NP | Implied Q2 NP | Q2 vs Q1 | Non-recurring share | Price | 20d | 1y position | Quality |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        values = {
            "q1": f"{row['q1_net_profit_100mn']:.2f}"
            if row["q1_net_profit_100mn"] is not None
            else "-",
            "h1eps": f"{row['h1_eps_midpoint']:.2f}"
            if row["h1_eps_midpoint"] is not None
            else "-",
            "fy_eps": f"{row['latest_2026e_eps']:.2f}"
            if row["latest_2026e_eps"] is not None
            else "-",
            "eps_ratio": f"{row['h1_eps_to_latest_2026e_eps_ratio']:.1%}"
            if row["h1_eps_to_latest_2026e_eps_ratio"] is not None
            else "-",
            "q2": f"{row['q2_implied_net_profit_100mn']:.2f}"
            if row["q2_implied_net_profit_100mn"] is not None
            else "-",
            "qoq": f"{row['q2_vs_q1_pct']:.1f}%"
            if row["q2_vs_q1_pct"] is not None
            else "-",
            "nonrec": f"{row['nonrecurring_share_pct']:.1f}%"
            if row["nonrecurring_share_pct"] is not None
            else "-",
            "price": f"{row['current_price']:.2f}"
            if row["current_price"] is not None
            else "-",
            "r20": f"{row['return_20d_pct']:.1f}%"
            if row["return_20d_pct"] is not None
            else "-",
            "pos": f"{row['position_1y_pct']:.1f}%"
            if row["position_1y_pct"] is not None
            else "-",
        }
        lines.append(
            f"| {row['sector']} | {row['ticker']} | {row['company']} | "
            f"{row['h1_net_profit_midpoint_100mn']:.2f} | {values['h1eps']} | "
            f"{values['fy_eps']} | {values['eps_ratio']} | {values['q1']} | "
            f"{values['q2']} | {values['qoq']} | {values['nonrec']} | "
            f"{values['price']} | {values['r20']} | {values['pos']} | "
            f"{row['quality_class']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
    ]
    for row in rows:
        lines.append(
            f"- **{row['company']} ({row['ticker']})** — {row['quality_class']}: "
            f"{row['quality_reason']}"
        )
    write_text(DATA_DIR / "earnings_preview_quality_20260711.md", "\n".join(lines))
    write_text(
        ANALYSIS_DIR / "earnings_preview_quality_review.md",
        "\n".join(lines)
        + "\n\n## Model Boundary\n\n"
        + "Preview growth is not automatically annualized. Core model upgrades require "
        + "deducted-profit quality, Q2 acceleration, cash conversion, a current-price "
        + "valuation denominator and an evidence-backed durability assessment.\n",
    )
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "quality_counts": {
                    quality: sum(row["quality_class"] == quality for row in rows)
                    for quality in sorted({row["quality_class"] for row in rows})
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
