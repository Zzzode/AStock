#!/usr/bin/env python3
"""Build the 2026-06-26 full valuation model for the AI-storage report."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
ANALYSIS = CASE / "analysis"
RUN_DATE = "2026-06-26"
CN_TZ = timezone(timedelta(hours=8))


VALUATION_ASSUMPTIONS = {
    "688008": {"bear": 60.0, "base": 65.0, "bull": 80.0, "method": "2027E PE", "quality": "B+", "rationale": "DDR5/RCD leader; CXL upside, but current valuation already discounts strong growth"},
    "002371": {"bear": 45.0, "base": 60.0, "bull": 75.0, "method": "2027E PE", "quality": "B+", "rationale": "Domestic equipment leader; order visibility higher than peers"},
    "688012": {"bear": 45.0, "base": 60.0, "bull": 75.0, "method": "2027E PE", "quality": "B", "rationale": "Etch platform scarce, but current price implies demanding execution"},
    "688072": {"bear": 50.0, "base": 70.0, "bull": 90.0, "method": "2027E PE", "quality": "B", "rationale": "ALD/CVD growth faster, but 2026 close embeds large premium"},
    "688126": {
        "bear": 14.0,
        "base": 18.0,
        "bull": 22.0,
        "valuation_type": "ps_pb",
        "method": "2026E PS/PB cross-check",
        "quality": "C",
        "revenue_2026_est_100mn": 45.5,
        "book_equity_100mn": 201.27,
        "rationale": "Consensus EPS remains negative, so PE is invalid; use discounted PS with PB sanity check for the 12-inch silicon wafer substrate option",
    },
    "000021": {"bear": 25.0, "base": 35.0, "bull": 45.0, "method": "2027E PE", "quality": "C+", "rationale": "Module and testing exposure, but low coverage and margin bridge uncertainty"},
    "600584": {"bear": 28.0, "base": 40.0, "bull": 50.0, "method": "2027E PE", "quality": "B-", "rationale": "Advanced packaging beta; profitability still below AI narrative"},
    "002156": {"bear": 30.0, "base": 45.0, "bull": 55.0, "method": "2027E PE", "quality": "B-", "rationale": "AMD/AI packaging optionality, but execution proof still needed"},
    "301308": {"bear": 14.0, "base": 20.0, "bull": 24.0, "method": "2026E peak-cycle PE", "quality": "C+", "rationale": "2027-2028E EPS path declines in THS consensus; use 2026E peak-cycle EPS"},
    "603986": {"bear": 40.0, "base": 60.0, "bull": 75.0, "method": "2027E PE", "quality": "B-", "rationale": "Niche DRAM/NOR recovery but current PE is already aggressive"},
    "300346": {"bear": 45.0, "base": 65.0, "bull": 85.0, "method": "2027E PE", "quality": "C+", "rationale": "Materials optionality, but HBM/ArF contribution remains partly thematic"},
}


def read_json(rel: str):
    return json.loads((CASE / rel).read_text(encoding="utf-8"))


def rating(upside: float | None, quality: str) -> tuple[str, str]:
    if upside is None:
        return "观察", "WATCHLIST"
    if upside >= 0.20 and quality not in {"C", "C+"}:
        return "买入", "BUY"
    if upside >= 0.08:
        return "增持", "ACCUMULATE"
    if upside > -0.15:
        return "中性", "NEUTRAL"
    return "减持", "REDUCE"


def pct(value: float | None) -> str:
    if value is None:
        return "n.a."
    return f"{value * 100:+.1f}%"


def money(value: float | None) -> str:
    if value is None:
        return "n.a."
    return f"{value:.2f}"


def main() -> int:
    reset = read_json("data/current_valuation_reset_20260626.json")
    ths = read_json("sources/market-data-20260626/ths_profit_forecast_20260626.json")
    rows = []
    weighted_upside = 0.0
    weighted_count = 0.0

    for item in reset["tickers"]:
        code = item["code"]
        forecasts = {str(row["年度"]): row for row in ths[code]}
        eps26 = float(forecasts["2026"]["均值"])
        eps26_min = float(forecasts["2026"]["最小值"])
        eps26_max = float(forecasts["2026"]["最大值"])
        eps27 = float(forecasts["2027"]["均值"])
        eps28 = float(forecasts["2028"]["均值"])
        inst = int(forecasts["2026"]["预测机构数"])
        assumption = VALUATION_ASSUMPTIONS[code]
        valuation_type = assumption.get("valuation_type", "pe")
        price = float(item["current_price_cny"])
        base_target = None
        bear_value = None
        bull_value = None
        final_range = "n.a."
        upside = None
        revenue_2026_est = assumption.get("revenue_2026_est_100mn")
        book_equity = assumption.get("book_equity_100mn")
        current_ps = None
        current_pb = None
        base_pb = None
        if valuation_type == "ps_pb":
            shares = float(item["total_shares_100mn"])
            revenue_2026_est = float(revenue_2026_est)
            book_equity = float(book_equity)
            bear_value = revenue_2026_est * float(assumption["bear"]) / shares
            base_target = revenue_2026_est * float(assumption["base"]) / shares
            bull_value = revenue_2026_est * float(assumption["bull"]) / shares
            final_range = f"{bear_value:.0f}--{bull_value:.0f}"
            upside = base_target / price - 1.0
            current_ps = float(item["total_market_cap_100mn_cny"]) / revenue_2026_est
            current_pb = float(item["total_market_cap_100mn_cny"]) / book_equity
            base_pb = base_target * shares / book_equity
            weighted_upside += upside * float(item["weight_pct"]) / 100.0
            weighted_count += float(item["weight_pct"]) / 100.0
        elif assumption["base"] is not None and eps26 > 0:
            if code == "301308":
                base_target = eps26 * assumption["base"]
                bear_value = eps26_min * assumption["bear"]
                bull_value = eps26_max * assumption["bull"]
            else:
                base_target = eps27 * assumption["base"]
                bear_value = max(0.0, eps26_min * assumption["bear"])
                bull_value = eps28 * assumption["bull"] / 1.15
            final_range = f"{bear_value:.0f}--{bull_value:.0f}"
            upside = base_target / price - 1.0
            weighted_upside += upside * float(item["weight_pct"]) / 100.0
            weighted_count += float(item["weight_pct"]) / 100.0
        action_cn, action_en = rating(upside, assumption["quality"])
        rows.append(
            {
                "code": code,
                "name": item["name"],
                "tier": item["tier"],
                "weight_pct": item["weight_pct"],
                "current_price_cny": price,
                "total_shares_100mn": item["total_shares_100mn"],
                "total_market_cap_100mn_cny": item["total_market_cap_100mn_cny"],
                "eps_2026_mean": eps26,
                "eps_2026_min": eps26_min,
                "eps_2026_max": eps26_max,
                "eps_2027_mean": eps27,
                "eps_2028_mean": eps28,
                "institution_count": inst,
                "valuation_type": valuation_type,
                "bear_pe": assumption["bear"] if valuation_type == "pe" else None,
                "base_pe": assumption["base"] if valuation_type == "pe" else None,
                "bull_pe": assumption["bull"] if valuation_type == "pe" else None,
                "bear_ps": assumption["bear"] if valuation_type == "ps_pb" else None,
                "base_ps": assumption["base"] if valuation_type == "ps_pb" else None,
                "bull_ps": assumption["bull"] if valuation_type == "ps_pb" else None,
                "revenue_2026_est_100mn": revenue_2026_est,
                "book_equity_100mn": book_equity,
                "current_ps_2026e": current_ps,
                "current_pb": current_pb,
                "base_target_pb": base_pb,
                "bear_value_cny": bear_value,
                "base_target_cny": base_target,
                "bull_value_cny": bull_value,
                "fair_value_range_cny": final_range,
                "implied_upside": upside,
                "rating_cn": action_cn,
                "rating_en": action_en,
                "method": assumption["method"],
                "evidence_quality": assumption["quality"],
                "rationale": assumption["rationale"],
                "catalyst": "HBM4/Vera Rubin、DDR5/CXL、国产设备订单、封测/材料验证的下一轮证据落地",
                "invalidation": "EPS 下修、订单或毛利率低于一致预期、海外可比估值继续压缩、政策/出口管制升级",
            }
        )

    payload = {
        "case_id": CASE.name,
        "run_date": RUN_DATE,
        "generated_at": datetime.now(CN_TZ).isoformat(timespec="seconds"),
        "decision": "publish_full_current_price_valuation",
        "method_note": "Base target uses 2027E consensus EPS times normalized PE except Jiangbolong, where declining 2027-2028E EPS requires 2026E peak-cycle PE. Bear uses 2026E EPS low times discounted PE. Bull uses 2028E EPS mean times bull PE discounted by 15%. Shanghai Silicon keeps PE blocked because consensus EPS stays negative, but receives a 2026E PS target with PB sanity check.",
        "weighted_base_upside": weighted_upside,
        "investable_weight_covered": weighted_count,
        "rows": rows,
    }
    (DATA / "current_valuation_model_20260626.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# AI Storage Full Valuation Model - 2026-06-26",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Weighted base upside: {pct(weighted_upside)}",
        "- Base target: 2027E EPS x normalized PE, except Jiangbolong uses 2026E peak-cycle EPS.",
        "- Shanghai Silicon: PE remains blocked because 2026-2028E EPS is negative; target price uses 2026E PS with PB sanity check.",
        "",
        "| Code | Name | Price | EPS26 | EPS27 | Bear | Base Target | Bull | Range | Upside | Rating | Quality |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['code']} | {row['name']} | {money(row['current_price_cny'])} | {money(row['eps_2026_mean'])} | {money(row['eps_2027_mean'])} | {money(row['bear_value_cny'])} | {money(row['base_target_cny'])} | {money(row['bull_value_cny'])} | {row['fair_value_range_cny']} | {pct(row['implied_upside'])} | {row['rating_cn']} | {row['evidence_quality']} |"
        )
    (DATA / "current_valuation_model_20260626.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    analysis_lines = [
        "# Valuation Model - AI Storage Current Valuation 2026-06-26",
        "",
        "## Executive Verdict",
        "",
        f"- Publishability: PASS FOR INTERNAL RESEARCH USE",
        f"- Weighted base upside: {pct(weighted_upside)}",
        "- The report should publish updated target prices and ratings instead of leaving all names suspended.",
        "- Most names screen expensive on current 2026-06-26 prices; the model therefore produces mostly Neutral/Reduce outcomes, not a bullish package.",
        "",
        "## Method",
        "",
        payload["method_note"],
        "",
        "## Final Valuation Table",
        "",
        "| Code | Name | Method | Price | Target | Range | Upside | Rating | Evidence | Invalidation |",
        "|---|---|---|---:|---:|---|---:|---|---|---|",
    ]
    for row in rows:
        analysis_lines.append(
            f"| {row['code']} | {row['name']} | {row['method']} | {money(row['current_price_cny'])} | {money(row['base_target_cny'])} | {row['fair_value_range_cny']} | {pct(row['implied_upside'])} | {row['rating_cn']} | {row['evidence_quality']} | {row['invalidation']} |"
        )
    (ANALYSIS / "valuation_model.md").write_text("\n".join(analysis_lines) + "\n", encoding="utf-8")
    print(f"wrote valuation model rows={len(rows)} weighted_base_upside={weighted_upside:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
