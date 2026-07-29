#!/usr/bin/env python3
"""Independently reconcile official FY2025 actuals and valuation arithmetic."""

from __future__ import annotations

import json
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
SRC = CASE / "sources" / "official-filings-20260718"


OFFICIAL = {
    "000034": ("神州数码", 1437.510445, 5.229438, "000034-digital-china-2025-annual-cninfo.pdf", "10-for-4 capital-reserve transfer disclosed; use current shares for forward EPS"),
    "000988": ("华工科技", 143.55, 14.707947, "000988-hgtech-2025-annual-cninfo.pdf", "no material forward-share-basis issue after reconciliation"),
    "600183": ("生益科技", 284.311385, 33.339544, "600183-shengyi-2025-annual-cninfo.pdf", "no material forward-share-basis issue after reconciliation"),
    "002916": ("深南电路", 236.469771, 32.757382, "002916-shennan-2025-annual-cninfo.pdf", "source EPS difference below 1%; current shares used"),
    "002463": ("沪电股份", 189.45, 38.223063, "002463-wus-2025-annual-cninfo.pdf", "source EPS reconciles to current shares"),
    "300476": ("胜宏科技", 192.923135, 43.119883, "300476-victory-2025-annual-cninfo.pdf", "no capital-reserve transfer; options/share changes create a 4% source EPS basis gap; current shares used"),
    "002837": ("英维克", 60.677591, 5.219148, "002837-envicool-2025-annual-cninfo.pdf", "10-for-3 capital-reserve transfer disclosed; use current shares for forward EPS"),
    "301018": ("申菱环境", 42.091988, 2.167772, "301018-shenling-2025-annual-cninfo.pdf", "10-for-4 capital-reserve transfer disclosed; use current shares for forward EPS"),
    "002335": ("科华数据", 81.602625, 4.179880, "002335-kehua-2025-annual-cninfo.pdf", "10-for-4.5 capital-reserve transfer disclosed; use current shares for forward EPS"),
    "002130": ("沃尔核材", 84.506606, 11.438684, "002130-woer-2025-annual-cninfo.pdf", "no capital-reserve transfer; current shares used to absorb other share-basis changes"),
    "002230": ("科大讯飞", 271.053905, 8.393909, "002230-iflytek-2025-annual-cninfo.pdf", "source EPS difference below 2%; current shares used"),
    "002025": ("航天电器", 58.198344, 1.828468, "002025-aerospace-electric-2025-annual-cninfo.pdf", "source EPS reconciles to current shares"),
}

BOOK_EQUITY = {
    "000034": 110.0644406737, "000988": 110.5718060923,
    "600183": 167.2350122633, "002916": 171.4943052985,
    "002463": 151.1270464200, "300476": 166.1760844357,
    "002837": 34.4564100879, "301018": 27.2683591797,
    "002335": 64.0655347915, "002130": 64.9711281378,
    "002230": 187.9446216869, "002025": 66.0377009246,
}


def close(a: float, b: float, tolerance: float) -> bool:
    return abs(a - b) <= tolerance


def main() -> None:
    model = json.loads((DATA / "current_valuation_model_20260718.json").read_text(encoding="utf-8"))
    rows = model["rows"]
    checks: list[dict] = []
    reconciled: list[dict] = []

    checks.append({"check": "row_count", "status": "PASS" if len(rows) == 12 else "FAIL", "detail": f"rows={len(rows)}"})
    for row in rows:
        ticker = row["ticker"]
        company, revenue, profit, filename, corporate_action = OFFICIAL[ticker]
        source = SRC / filename
        historical_ok = close(row["revenue_2025a_100mn"], revenue, 0.02) and close(row["np_2025a_100mn"], profit, 0.02)
        book_ok = close(row["book_equity_2025a_100mn"], BOOK_EQUITY[ticker], 0.0001)
        eps_expected = row["np_2026e_100mn"] / row["shares_100mn"]
        eps_ok = close(row["eps_2026e"], eps_expected, 0.0002)
        primary_bear = row["bear_multiple"] * row["eps_2026e"] * row["bear_eps_factor"]
        primary_base = row["base_multiple"] * row["eps_2026e"] * row["base_eps_factor"]
        primary_bull = row["bull_multiple"] * row["eps_2026e"] * row["bull_eps_factor"]
        book_value_per_share = row["book_equity_2025a_100mn"] / row["shares_100mn"]
        low_pb, base_pb, high_pb = row["justified_pb_scenarios"]
        secondary_bear = low_pb * book_value_per_share
        secondary_base = base_pb * book_value_per_share
        secondary_bull = high_pb * book_value_per_share
        bear_expected = round(0.60 * primary_bear + 0.40 * secondary_bear, 2)
        base_expected = round(0.60 * primary_base + 0.40 * secondary_base, 2)
        bull_expected = round(0.60 * primary_bull + 0.40 * secondary_bull, 2)
        scenarios_ok = close(row["bear"], bear_expected, 0.02) and close(row["base"], base_expected, 0.02) and close(row["bull"], bull_expected, 0.02)
        weights_ok = close(row["fundamental_weight"] + row["market_weight"] + row["broker_weight"], 1.0, 1e-9)
        broker_anchor = row["broker_target_anchor"] if isinstance(row["broker_target_anchor"], (int, float)) else row["base"]
        final_expected = round(row["fundamental_weight"] * row["base"] + row["market_weight"] * row["current_price"] + row["broker_weight"] * broker_anchor, 2)
        target_ok = close(row["final_target"], final_expected, 0.01) and close(row["upside"], row["final_target"] / row["current_price"] - 1.0, 0.00001)
        source_ok = source.exists() and source.stat().st_size > 100_000
        atlas_ok = row["atlas_950_revenue_credit_2026e_100mn"] == 0
        status = "PASS" if all((historical_ok, book_ok, eps_ok, scenarios_ok, weights_ok, target_ok, source_ok, atlas_ok)) else "FAIL"
        checks.append({
            "check": f"ticker_{ticker}", "status": status,
            "detail": {"official_source": filename, "historical_actuals": historical_ok, "np_to_eps": eps_ok, "official_book_value_to_pb": book_ok, "scenarios": scenarios_ok, "weights": weights_ok, "target_and_upside": target_ok, "atlas_zero_credit": atlas_ok},
        })
        reconciled.append({
            "ticker": ticker, "company": company, "official_fy2025_revenue_100mn": revenue,
            "official_fy2025_parent_np_100mn": profit, "official_source_path": str(source.relative_to(CASE)),
            "official_source_url": {
                "000034": "https://static.cninfo.com.cn/finalpage/2026-06-13/1225367858.PDF",
                "000988": "https://static.cninfo.com.cn/finalpage/2026-03-26/1225031509.PDF",
                "600183": "https://static.cninfo.com.cn/finalpage/2026-04-25/1225195409.PDF",
                "002916": "https://static.cninfo.com.cn/finalpage/2026-03-13/1225006760.PDF",
                "002463": "https://static.cninfo.com.cn/finalpage/2026-03-25/1225027832.PDF",
                "300476": "https://static.cninfo.com.cn/finalpage/2026-03-13/1225007455.PDF",
                "002837": "https://static.cninfo.com.cn/finalpage/2026-04-21/1225131813.PDF",
                "301018": "https://static.cninfo.com.cn/finalpage/2026-04-27/1225181199.PDF",
                "002335": "https://static.cninfo.com.cn/finalpage/2026-04-27/1225194937.PDF",
                "002130": "https://static.cninfo.com.cn/finalpage/2026-04-01/1225067232.PDF",
                "002230": "https://static.cninfo.com.cn/finalpage/2026-04-29/1225233581.PDF",
                "002025": "https://static.cninfo.com.cn/finalpage/2026-03-31/1225054265.PDF",
            }[ticker],
            "corporate_action_reconciliation": corporate_action,
            "current_shares_100mn": row["shares_100mn"], "broker_eps_2026e_reported": row["broker_eps_2026e_reported"],
            "reconciled_eps_2026e": row["eps_2026e"], "share_basis_gap_pct": row["broker_eps_share_basis_gap_pct"],
            "q1_use_policy": "2026Q1 structured observation is not an input to target arithmetic; retain Medium confidence until issuer original is archived",
        })

    overall = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    (DATA / "official_financial_reconciliation_20260718.json").write_text(json.dumps({"status": overall, "rows": reconciled}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA / "valuation_reproducibility_checks_20260718.json").write_text(json.dumps({"status": overall, "checks": checks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Official Financial Reconciliation", "", f"Status: **{overall}**. FY2025 official originals cover 12/12 modeled issuers. 2026Q1 observations are not used in target arithmetic.", "", "| Ticker | Company | FY2025 revenue | FY2025 parent NP | Current shares | Source EPS | Reconciled EPS | Basis gap | Corporate-action treatment |", "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in reconciled:
        md.append(f"| {row['ticker']} | {row['company']} | {row['official_fy2025_revenue_100mn']:.2f} | {row['official_fy2025_parent_np_100mn']:.2f} | {row['current_shares_100mn']:.4f} | {row['broker_eps_2026e_reported']:.3f} | {row['reconciled_eps_2026e']:.3f} | {row['share_basis_gap_pct']:+.1f}% | {row['corporate_action_reconciliation']} |")
    (DATA / "official_financial_reconciliation_20260718.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    audit_md = ["# Valuation Reproducibility Checks", "", f"Model Reproducibility: {overall}", ""]
    audit_md += [f"- {item['check']}: {item['status']} — {item['detail']}" for item in checks]
    (DATA / "valuation_reproducibility_checks_20260718.md").write_text("\n".join(audit_md) + "\n", encoding="utf-8")
    print(json.dumps({"status": overall, "checks": len(checks), "rows": len(reconciled)}, ensure_ascii=False))
    raise SystemExit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
