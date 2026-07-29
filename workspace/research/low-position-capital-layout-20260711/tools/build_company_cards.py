#!/usr/bin/env python3
"""Build full-universe company cards and valuation dispositions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"


CORE_MODEL_TICKERS = {
    "601077",
    "000425",
    "601825",
    "600276",
    "601138",
}

POST_PREVIEW_REPORT_OVERRIDES = {
    "601138": {
        "latest_report_date": "2026-07-10",
        "latest_report_title": "AI推动1H26净利润同比预增93%~101%",
        "latest_broker": "华泰证券",
        "latest_rating": "买入",
        "latest_2026e_eps": 2.82,
        "latest_2026e_pe": 23.5,
        "report_vs_preview": "post_preview",
    }
}

DISPOSITION_OVERRIDES = {
    "000063": (
        "conditional_watch_insufficient_segment_economics",
        "Upgrade only after H2 profit growth turns positive, operating cash flow improves, and compute-segment margin or order evidence becomes available.",
    ),
    "301308": (
        "conditional_watch_cycle_model_unresolved",
        "Upgrade only after H2 deducted profit and operating cash flow validate, inventory write-down stays contained, and contract-price or customer-order evidence supports cycle duration.",
    ),
    "000938": (
        "post_preview_model_refresh",
        "Deduct CNY0.25-0.35bn non-recurring gains and rebuild H3C ownership economics before target upgrade.",
    ),
    "000977": (
        "earnings_delivered_wait_pullback",
        "Post-preview reports exist; monitor margin and working capital after the sharp price response.",
    ),
    "002396": (
        "oneoff_discount_watch",
        "Remove CNY0.10-0.12bn non-recurring gains and verify data-center switch margin.",
    ),
    "301165": (
        "earnings_delivered_wait_pullback",
        "Post-preview report and target exist, but price already reflects much of the upgrade.",
    ),
    "001339": (
        "price_above_broker_anchor",
        "Preview is strong, but current price exceeds the public target range; wait for a new forecast.",
    ),
    "300475": (
        "post_preview_model_refresh",
        "H1 profit exceeds old full-year forecasts; rebuild full-year margin, supply and cash-flow assumptions.",
    ),
    "603986": (
        "post_preview_model_refresh",
        "Use deducted profit and separate fair-value gains before rebuilding the 2026E denominator.",
    ),
    "600685": (
        "post_preview_model_refresh",
        "Update the stale broker forecast for order mix, associates and investment income.",
    ),
    "002829": (
        "exclude_nonrecurring_dominated",
        "Deducted profit remains negative and investment income creates the reported turnaround.",
    ),
    "600601": (
        "post_preview_model_refresh",
        "Old EPS is obsolete; rebuild high-end PCB revenue, margin, capex and customer/order evidence.",
    ),
    "000636": (
        "cycle_watch_price_demanding",
        "Q2 accelerates, but valuation and price already require sustained MLCC price/mix improvement.",
    ),
    "001314": (
        "oneoff_discount_watch",
        "Investment income is material; value the operating AI-terminal business separately.",
    ),
    "002407": (
        "cycle_watch_q2_deceleration",
        "H1 improves but implied Q2 profit falls versus Q1; require LiPF6 price and cash-flow validation.",
    ),
    "002842": (
        "cycle_watch_working_capital",
        "Tungsten pass-through supports profit, but cash conversion and downstream elasticity remain hard gates.",
    ),
}

SECTOR_DEFAULTS = {
    "银行": (
        "no_preview_fundamental_watch",
        "Track NIM, asset quality, dividend and H1 actual disclosure.",
    ),
    "工程机械": (
        "no_preview_cycle_watch",
        "Track overseas/mining growth, margin and operating cash flow.",
    ),
    "创新药": (
        "no_preview_pipeline_watch",
        "Track innovative-drug sales, approvals, BD milestones and 2026E EPS.",
    ),
    "先进封装": (
        "price_advanced_wait_earnings",
        "Price has advanced; require H1 actual margin, capex utilization and cash-flow confirmation.",
    ),
    "传媒与AI应用": (
        "broker_supported_no_preview",
        "Track product pipeline, user/monetization evidence and AI contribution to EPS.",
    ),
    "国防军工与商业航天": (
        "no_preview_order_watch",
        "Track order recovery, revenue recognition and operating cash flow.",
    ),
    "AI网络与算力设备": (
        "no_preview_compute_watch",
        "Track compute revenue mix, margin, delivery and cash conversion.",
    ),
    "AI存储": (
        "no_preview_storage_watch",
        "Track storage contract prices, supply allocation, inventory and cash flow.",
    ),
    "业绩预告新雷达": (
        "preview_radar_watch",
        "Require a refreshed broker denominator and current-price valuation before upgrade.",
    ),
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


def q1_metrics(ticker: str) -> dict[str, Any]:
    path = financial_path(ticker)
    if path is None:
        return {}
    payload = load_json(path)
    for period in payload.get("periods") or payload.get("statements") or []:
        if str(period.get("period")) == "20260331":
            metrics = period.get("metrics") or {}
            return {
                "q1_revenue_100mn": (
                    round(float(metrics["total_revenue"]) / 1e8, 2)
                    if metrics.get("total_revenue") is not None
                    else None
                ),
                "q1_net_profit_100mn": (
                    round(float(metrics["net_profit_parent"]) / 1e8, 2)
                    if metrics.get("net_profit_parent") is not None
                    else None
                ),
                "q1_ocf_100mn": (
                    round(float(metrics["operating_cash_flow"]) / 1e8, 2)
                    if metrics.get("operating_cash_flow") is not None
                    else None
                ),
                "q1_revenue_growth_pct": metrics.get("revenue_growth"),
                "q1_profit_growth_pct": metrics.get("profit_growth"),
                "q1_gross_margin_pct": metrics.get("gross_margin"),
                "q1_net_margin_pct": metrics.get("net_margin"),
                "q1_eps": metrics.get("eps_basic"),
                "q1_bps": metrics.get("bps"),
                "financial_source_path": str(path.relative_to(CASE_DIR)),
            }
    return {}


def kline_metrics(ticker: str) -> dict[str, float | None]:
    path = DATA_DIR / f"raw_kline_{ticker}_20260710.json"
    if not path.exists() or not path.stat().st_size:
        return {"return_20d_pct": None, "return_60d_pct": None, "position_1y_pct": None}
    payload = load_json(path).get("data", {})
    key = next((key for key in payload if key not in {"qt", "market"}), None)
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


def main() -> None:
    census = load_json(DATA_DIR / "core_universe_preview_census_20260711.json")
    report_catalog = load_json(DATA_DIR / "core_broker_report_catalog_20260711.json")
    preview_quality = load_json(DATA_DIR / "earnings_preview_quality_20260711.json")
    quotes = {
        row["code"]: row
        for row in load_json(DATA_DIR / "raw_core_universe_quotes_20260710.json").get(
            "ticks", []
        )
    }
    report_map = {row["ticker"]: row for row in report_catalog["metadata_rows"]}
    preview_quality_map = {row["ticker"]: row for row in preview_quality["rows"]}

    rows: list[dict[str, Any]] = []
    for company in census["rows"]:
        ticker = company["ticker"]
        quote = quotes.get(ticker, {})
        report = {
            **report_map.get(ticker, {}),
            **POST_PREVIEW_REPORT_OVERRIDES.get(ticker, {}),
        }
        preview = preview_quality_map.get(ticker, {})
        if ticker in CORE_MODEL_TICKERS:
            disposition = "current_price_core_model"
            upgrade_trigger = "Maintain the current model only while its company-specific validation thresholds hold."
        elif ticker in DISPOSITION_OVERRIDES:
            disposition, upgrade_trigger = DISPOSITION_OVERRIDES[ticker]
        else:
            disposition, upgrade_trigger = SECTOR_DEFAULTS[company["sector"]]
        row = {
            **company,
            **q1_metrics(ticker),
            **kline_metrics(ticker),
            "current_price": quote.get("price"),
            "daily_change_pct": quote.get("change_pct"),
            "trading_value_100mn": (
                round(float(quote["amount"]) / 1e8, 2)
                if quote.get("amount") is not None
                else None
            ),
            "h1_preview_midpoint_100mn": preview.get(
                "h1_net_profit_midpoint_100mn"
            ),
            "h1_eps_midpoint": preview.get("h1_eps_midpoint"),
            "h1_eps_to_latest_2026e_eps_ratio": preview.get(
                "h1_eps_to_latest_2026e_eps_ratio"
            ),
            "q2_implied_net_profit_100mn": preview.get(
                "q2_implied_net_profit_100mn"
            ),
            "preview_quality_class": preview.get("quality_class", "not applicable"),
            "preview_quality_reason": preview.get(
                "quality_reason", "No 2026H1 preview found in the captured table."
            ),
            "nonrecurring_share_pct": preview.get("nonrecurring_share_pct"),
            "report_count": report.get("report_count", 0),
            "latest_report_date": report.get("latest_report_date", "not found"),
            "latest_report_title": report.get("latest_report_title", "not found"),
            "latest_broker": report.get("latest_broker", "not found"),
            "latest_rating": report.get("latest_rating", "not found"),
            "latest_2026e_eps": report.get("latest_2026e_eps"),
            "latest_2026e_pe": report.get("latest_2026e_pe"),
            "report_vs_preview": report.get("report_vs_preview", "not found"),
            "valuation_disposition": disposition,
            "upgrade_or_monitor_trigger": upgrade_trigger,
        }
        rows.append(row)

    sector_order = {
        "银行": 0,
        "工程机械": 1,
        "AI网络与算力设备": 2,
        "AI存储": 3,
        "创新药": 4,
        "国防军工与商业航天": 5,
        "先进封装": 6,
        "传媒与AI应用": 7,
        "业绩预告新雷达": 8,
    }
    tier_order = {
        "core": 0,
        "core_candidate": 1,
        "preview_candidate": 2,
        "satellite": 3,
        "demand_anchor": 4,
        "equipment_satellite": 5,
    }
    rows.sort(
        key=lambda row: (
            sector_order[row["sector"]],
            tier_order.get(row["tier"], 9),
            row["ticker"],
        )
    )
    write_json(
        DATA_DIR / "company_cards_20260711.json",
        {
            "schema_version": "astock.company_cards.v1",
            "data_cutoff": "2026-07-11 evidence; 2026-07-10 prices",
            "row_count": len(rows),
            "rows": rows,
        },
    )

    lines = [
        "# Full Core and Satellite Company Cards",
        "",
        "| Sector | Tier | Ticker | Company | Price | 1y pos | Q1 revenue | Q1 NP | Q1 OCF | H1 preview NP | H1 EPS | H1/full-year EPS | Implied Q2 | Preview quality | Latest broker/date | EPS/PE | Relation | Disposition |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|",
    ]
    for row in rows:
        def fmt(key: str, digits: int = 2) -> str:
            value = row.get(key)
            return f"{value:.{digits}f}" if value is not None else "-"

        eps_pe = (
            f"{fmt('latest_2026e_eps')}/{fmt('latest_2026e_pe', 1)}"
            if row.get("latest_2026e_eps") is not None
            or row.get("latest_2026e_pe") is not None
            else "-"
        )
        lines.append(
            f"| {row['sector']} | {row['tier']} | {row['ticker']} | {row['company']} | "
            f"{fmt('current_price')} | {fmt('position_1y_pct', 1)}% | "
            f"{fmt('q1_revenue_100mn')} | {fmt('q1_net_profit_100mn')} | "
            f"{fmt('q1_ocf_100mn')} | {fmt('h1_preview_midpoint_100mn')} | "
            f"{fmt('h1_eps_midpoint')} | "
            f"{fmt('h1_eps_to_latest_2026e_eps_ratio', 2)} | "
            f"{fmt('q2_implied_net_profit_100mn')} | {row['preview_quality_class']} | "
            f"{row['latest_broker']}/{row['latest_report_date']} | {eps_pe} | "
            f"{row['report_vs_preview']} | {row['valuation_disposition']} |"
        )
    lines += [
        "",
        "## Upgrade and Monitoring Rules",
        "",
    ]
    for row in rows:
        lines.append(
            f"- **{row['company']} ({row['ticker']})** — {row['valuation_disposition']}: "
            f"{row['upgrade_or_monitor_trigger']}"
        )
    write_text(DATA_DIR / "company_cards_20260711.md", "\n".join(lines))
    write_text(ANALYSIS_DIR / "company_cards.md", "\n".join(lines))

    disposition_counts: dict[str, int] = {}
    for row in rows:
        disposition_counts[row["valuation_disposition"]] = (
            disposition_counts.get(row["valuation_disposition"], 0) + 1
        )
    write_text(
        ANALYSIS_DIR / "valuation_disposition_matrix.md",
        "# Valuation Disposition Matrix\n\n"
        + "\n".join(
            f"- {key}: {value}" for key, value in sorted(disposition_counts.items())
        )
        + "\n\n"
        + "Only `current_price_core_model` names have published current targets. "
        + "`post_preview_model_refresh` names have material new evidence but require a "
        + "new forecast denominator and current-price model before an investable target. "
        + "Other dispositions remain watch, pullback or exclude decisions.\n",
    )
    print(
        json.dumps(
            {"row_count": len(rows), "disposition_counts": disposition_counts},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
