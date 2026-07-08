#!/usr/bin/env python3
"""Regenerate valuation_model.md analysis from updated 2026-07-03 JSON data.

Preserves qualitative methodology sections but regenerates all numeric tables
with fresh price data, targets, upside, and scenario positions.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
RUN_DATE = "2026-07-03"


def float_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    text = str(value).strip()
    if not text or text in {"not disclosed", "n/a", "none", "null", "未披露"}:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def fmt(value: object, decimals: int = 2) -> str:
    parsed = float_or_none(value)
    if parsed is None:
        return "N/A"
    return f"{parsed:.{decimals}f}"


def pct(value: object) -> str:
    parsed = float_or_none(value)
    if parsed is None:
        return "N/A"
    sign = "+" if parsed >= 0 else ""
    return f"{sign}{parsed * 100:.1f}%"


def street_anchor_display(row: dict) -> str:
    for key in ("street_broker_anchor", "broker_anchor", "broker_target"):
        val = row.get(key)
        if val is not None and str(val).strip() not in {"not disclosed", "n/a", "none", "null", "未披露"}:
            f = float_or_none(val)
            if f is not None:
                return f"{f:.3f}"
    return "未披露"


def load_combined() -> dict:
    path = DATA / f"combined_target_valuation_model_20260703.json"
    return json.loads(path.read_text(encoding="utf-8"))


def generate_final_valuation_table(rows: list[dict]) -> str:
    lines = []
    lines.append("## Final Valuation Table")
    lines.append("")
    lines.append("| Ticker | Company | Chain | Current | 2026E revenue | 2026E NP | 2026E EPS | Method | Bear | Base | Bull | Final target | Upside | Action | Evidence | Broker weight | Catalyst | Invalidation |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|---:|---|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        chain = r.get("chain_bucket", "")
        current = fmt(r.get("current_price"), 2)
        rev = fmt(r.get("revenue_2026e_100mn"), 1)
        np_ = fmt(r.get("np_2026e_100mn"), 1)
        eps = fmt(r.get("eps_2026e"), 2)
        method = str(r.get("method", ""))[:30]
        bear = fmt(r.get("bear"), 1)
        base = fmt(r.get("base"), 1)
        bull = fmt(r.get("bull"), 1)
        target = fmt(r.get("final_target"), 1)
        upside = pct(r.get("upside"))
        action = r.get("rating_or_action", "")
        evidence = str(r.get("evidence_quality", ""))[:15]
        bw = float_or_none(r.get("broker_weight")) or 0.0
        bw_str = f"{bw * 100:.0f}%"
        catalyst = str(r.get("catalyst", ""))[:50]
        invalidation = str(r.get("invalidation", ""))[:50]
        lines.append(
            f"| {ticker} | {company} | {chain} | {current} | {rev} | {np_} | {eps} | {method} | {bear} | {base} | {bull} | {target} | {upside} | {action} | {evidence} | {bw_str} | {catalyst} | {invalidation} |"
        )

    return "\n".join(lines)


def generate_price_reconciliation(rows: list[dict]) -> str:
    lines = []
    lines.append("## Current Price, Share Count and Market Cap Reconciliation")
    lines.append("")
    lines.append("| Ticker | Company | Current price | Shares (100mn) | Market cap (100mn CNY) | Price datetime |")
    lines.append("|---|---|---:|---:|---:|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        price = fmt(r.get("current_price"), 2)
        shares = fmt(r.get("shares_100mn"), 2)
        mcap = fmt(r.get("market_cap_100mn_cny"), 1)
        pdate = r.get("price_datetime", r.get("price_date", ""))
        lines.append(f"| {ticker} | {company} | {price} | {shares} | {mcap} | {pdate} |")

    return "\n".join(lines)


def generate_three_tier_targets(rows: list[dict]) -> str:
    lines = []
    lines.append("## Three-Tier Targets")
    lines.append("")
    lines.append("| Ticker | Company | Bear | Base | Bull | Final target | Scenario read |")
    lines.append("|---|---|---:|---:|---:|---:|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        bear = fmt(r.get("bear"), 1)
        base = fmt(r.get("base"), 1)
        bull = fmt(r.get("bull"), 1)
        target = fmt(r.get("final_target"), 1)
        scenario_pos = r.get("scenario_position", "")
        scenario_reason = r.get("scenario_exception_reason", "")
        scenario_read = f"{scenario_pos}: {scenario_reason}" if scenario_pos else ""
        lines.append(f"| {ticker} | {company} | {bear} | {base} | {bull} | {target} | {scenario_read} |")

    return "\n".join(lines)


def generate_target_formula_recalc(rows: list[dict]) -> str:
    lines = []
    lines.append("## Target Formula Recalculation")
    lines.append("")
    lines.append("Final target = Base fundamental anchor x Wf + market-implied anchor x Wm + Street/broker anchor x Ws. Rows with missing market anchors in upstream refresh are inferred back from the published formula and flagged through `market_anchor_source`; the final audit must still recalculate to the published target.")
    lines.append("")
    lines.append("| Ticker | Company | Base | Market anchor | Market anchor source | Street anchor | Wf | Wm | Ws | Final target | Recalc | Diff | Upside | Result |")
    lines.append("|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        base = fmt(r.get("base"), 3)
        mkt = fmt(r.get("market_anchor"), 3)
        mkt_src = r.get("market_anchor_source", "")
        street = street_anchor_display(r)
        fw = float_or_none(r.get("fundamental_weight")) or 0.0
        mw = float_or_none(r.get("market_weight")) or 0.0
        bw = float_or_none(r.get("broker_weight")) or 0.0
        target = fmt(r.get("final_target"), 3)
        recalc = fmt(r.get("recalculated_target"), 3)
        diff = fmt(r.get("target_recalc_diff"), 5)
        upside = pct(r.get("upside"))
        result = r.get("model_reproducibility", "CHECK")
        lines.append(
            f"| {ticker} | {company} | {base} | {mkt} | {mkt_src} | {street} | {fw * 100:.0f}% | {mw * 100:.0f}% | {bw * 100:.0f}% | {target} | {recalc} | {diff} | {upside} | {result} |"
        )

    return "\n".join(lines)


def generate_row_level_valuation(rows: list[dict]) -> str:
    """Generate per-company valuation formula text grouped by chain bucket."""
    # Group by chain bucket
    buckets = defaultdict(list)
    for r in rows:
        bucket = r.get("chain_bucket", "未分类")
        buckets[bucket].append(r)

    # Define display names for chain buckets
    bucket_names = {
        "AI PCB/CCL": "AI PCB/CCL",
        "AIDC/IDC 运营": "AIDC/IDC 运营",
        "供配电/能源": "供配电/能源",
        "光通信": "光模块/光器件",
        "服务器/网络设备/国产算力": "服务器/网络设备",
        "液冷/温控": "液冷/温控",
        "算力芯片/存储/网络 ASIC": "算力芯片/存储/网络 ASIC",
    }

    lines = []
    lines.append("## Row-Level Valuation Formula and Explanation")
    lines.append("")
    lines.append("本节是逐标的正文披露，不再用表格承载估值解释。每个目标价均按 Base 基本面锚 x Wf + 市场情绪锚 x Wm + Street/券商锚 x Ws 复算，并在同一段解释方法适配、锚点权重和下一季度验证条件。")
    lines.append("")

    for bucket, bucket_rows in buckets.items():
        display_name = bucket_names.get(bucket, bucket)
        lines.append(f"### {display_name}")
        lines.append("")

        for r in bucket_rows:
            ticker = r.get("ticker", "")
            company = r.get("company", "")
            rev = fmt(r.get("revenue_2026e_100mn"), 1)
            np_ = fmt(r.get("np_2026e_100mn"), 1)
            eps = fmt(r.get("eps_2026e"), 2)
            bear = fmt(r.get("bear"), 1)
            base = fmt(r.get("base"), 1)
            bull = fmt(r.get("bull"), 1)
            base_val = float_or_none(r.get("base")) or 0.0
            fw = float_or_none(r.get("fundamental_weight")) or 0.0
            mw = float_or_none(r.get("market_weight")) or 0.0
            bw = float_or_none(r.get("broker_weight")) or 0.0
            mkt_anchor = float_or_none(r.get("market_anchor"))
            street_anchor = float_or_none(r.get("street_broker_anchor")) or float_or_none(r.get("broker_target"))
            target = fmt(r.get("final_target"), 1)
            price = fmt(r.get("current_price"), 2)
            upside = pct(r.get("upside"))
            action = r.get("rating_or_action", "")
            evidence = r.get("evidence_quality", "")
            method = r.get("method", "")
            catalyst = r.get("catalyst", "")
            invalidation = r.get("invalidation", "")
            scenario_pos = r.get("scenario_position", "")
            scenario_reason = r.get("scenario_exception_reason", "")

            # Build formula text
            formula_parts = []
            formula_parts.append(f"{base_val:.1f}×{fw * 100:.0f}%")
            if mw > 0 and mkt_anchor is not None:
                formula_parts.append(f"{mkt_anchor:.1f}×{mw * 100:.0f}%")
            else:
                formula_parts.append(f"市场锚未用×{mw * 100:.0f}%")
            if bw > 0 and street_anchor is not None:
                formula_parts.append(f"{street_anchor:.1f}×{bw * 100:.0f}%")
            else:
                formula_parts.append(f"Street锚未用×{bw * 100:.0f}%")

            formula_str = " + ".join(formula_parts)

            # Compute PE ratios
            eps_val = float_or_none(r.get("eps_2026e"))
            price_val = float_or_none(r.get("current_price"))
            base_pe = ""
            current_pe = ""
            if eps_val and eps_val > 0:
                current_pe = f"{price_val / eps_val:.1f}" if price_val else "N/A"
                base_pe = f"{base_val / eps_val:.1f}"

            # Scenario text
            if scenario_pos == "inside_scenario":
                scenario_text = "最终目标落在 Bear/Bull 区间内。"
            elif scenario_pos == "above_bull_explained":
                scenario_text = "最终目标触及情景边界，已在质量审计中解释，不能自动上调基本面权重。"
            elif scenario_pos == "below_bear_explained":
                scenario_text = "最终目标低于 Bear，需复核分母和现金流。"
            else:
                scenario_text = scenario_reason

            # Market anchor source text
            mkt_src = r.get("market_anchor_source", "")
            if mkt_src == "source_model_disclosed":
                mkt_src_text = "原模型披露"
            elif "inferred" in str(mkt_src):
                mkt_src_text = "公式回推"
            else:
                mkt_src_text = str(mkt_src)

            # Street anchor text
            if bw > 0 and street_anchor is not None:
                street_text = f"Street锚为明示目标价，进入 {bw * 100:.0f}% 权重。"
            elif bw == 0:
                broker_bucket = r.get("broker_coverage_bucket", "")
                if "forecast_only" in str(broker_bucket):
                    street_text = "Street锚为预测-only，权重为 0，不替代 AStock 目标。"
                elif "official_disclosure" in str(broker_bucket):
                    street_text = "Street锚为公告替代，权重为 0，不替代 AStock 目标。"
                elif "milestone" in str(broker_bucket):
                    street_text = "Street锚为PS/SOTP里程碑，权重为 0，不替代 AStock 目标。"
                else:
                    street_text = "Street锚权重为 0，不替代 AStock 目标。"
            else:
                street_text = ""

            # PE read text
            pe_read = ""
            if current_pe and base_pe:
                pe_read = f"现价约 {current_pe}x 2026E PE，Base 约 {base_pe}x 2026E PE。"

            # Next quarter validation threshold
            threshold = r.get("next_quarter_validation_threshold", "")
            if threshold:
                # Truncate to first sentence or 80 chars
                threshold_short = threshold.split("。")[0] + "。" if "。" in threshold else threshold[:80]

            lines.append(
                f"**{ticker} {company}。** "
                f"2026E收入 {rev} 亿元，净利 {np_} 亿元，EPS {eps}；"
                f"Bear/Base/Bull {bear}/{base}/{bull}。"
                f"目标 = {formula_str} = {target}；"
                f"现价 {price}，空间 {upside}。 "
                f"{method}：核心看 {catalyst[:40]}。"
                f"市场锚按 {mkt_src_text} 进入 {mw * 100:.0f}% 权重。"
                f"{street_text}"
                f"{pe_read}"
                f"{scenario_text}"
                f"下一季度验证：{threshold_short if threshold else '需验证收入、毛利率和订单证据。'}"
            )

        lines.append("")

    return "\n".join(lines)


def generate_relative_peg_psg(rows: list[dict]) -> str:
    lines = []
    lines.append("## Relative / PEG / PSG Comparison")
    lines.append("")
    lines.append("| Ticker | Company | Current PE 2026E | Base PE proxy | Current PS 2026E | Read |")
    lines.append("|---|---|---:|---:|---:|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        eps = float_or_none(r.get("eps_2026e"))
        price = float_or_none(r.get("current_price"))
        base = float_or_none(r.get("base"))
        rev = float_or_none(r.get("revenue_2026e_100mn"))
        mcap = float_or_none(r.get("market_cap_100mn_cny"))

        current_pe = ""
        base_pe = ""
        current_ps = ""
        read = ""

        if eps and eps > 0 and price:
            current_pe = f"{price / eps:.1f}"
        if eps and eps > 0 and base:
            base_pe = f"{base / eps:.1f}"
        if rev and rev > 0 and mcap:
            current_ps = f"{mcap / rev:.2f}"

        if current_pe and base_pe:
            try:
                if float(current_pe) > float(base_pe) * 1.1:
                    read = "现价要求高于基础情景的增长久期或利润率。"
                elif float(current_pe) < float(base_pe) * 0.9:
                    read = "现价低于基础倍数，关键在分母兑现而非主题溢价。"
                else:
                    read = "现价大致贴近基础分母，后续看订单与现金流验证。"
            except (ValueError, TypeError):
                pass

        # Special case for negative EPS
        if eps is not None and eps <= 0:
            if rev and rev > 0 and mcap:
                read = "EPS 分母不足或为负，按 PS/PB/SOTP 或观察逻辑处理。"
            else:
                read = "EPS 分母不足，需 PS/SOTP 或里程碑证据。"

        lines.append(f"| {ticker} | {company} | {current_pe} | {base_pe} | {current_ps} | {read} |")

    return "\n".join(lines)


def generate_market_implied_sentiment(rows: list[dict]) -> str:
    lines = []
    lines.append("## Market-Implied Sentiment Anchor")
    lines.append("")
    lines.append("Current price is reverse-engineered by group: required EPS equals current price divided by the base-case multiple, and required revenue equals required net profit divided by the modeled net margin.")
    lines.append("")

    # Group by chain bucket
    buckets = defaultdict(list)
    for r in rows:
        bucket = r.get("chain_bucket", "未分类")
        buckets[bucket].append(r)

    # Group summary table
    lines.append("| Group | Rows | Avg current PE | Avg base PE | Required EPS vs 2026E | Required revenue vs 2026E | Interpretation |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")

    for bucket, bucket_rows in buckets.items():
        n = len(bucket_rows)
        current_pes = []
        base_pes = []
        for r in bucket_rows:
            eps = float_or_none(r.get("eps_2026e"))
            price = float_or_none(r.get("current_price"))
            base = float_or_none(r.get("base"))
            if eps and eps > 0 and price:
                current_pes.append(price / eps)
            if eps and eps > 0 and base:
                base_pes.append(base / eps)

        avg_cpe = sum(current_pes) / len(current_pes) if current_pes else 0
        avg_bpe = sum(base_pes) / len(base_pes) if base_pes else 0
        req_eps_vs = ""
        if avg_bpe > 0:
            req_ratio = avg_cpe / avg_bpe
            req_eps_vs = f"{(req_ratio - 1) * 100:.1f}%" if req_ratio > 1 else f"{(req_ratio - 1) * 100:.1f}%"
            req_eps_vs_display = f"+{req_eps_vs}" if not req_eps_vs.startswith("-") else req_eps_vs
        else:
            req_eps_vs_display = "N/A"

        interpretation = "现价基本要求基础情景外的 EPS 上修。" if avg_cpe > avg_bpe * 1.1 else "现价贴近或低于基础倍数，关键在分母兑现。"

        lines.append(
            f"| {bucket} | {n} | {avg_cpe:.1f} | {avg_bpe:.1f} | {req_eps_vs_display} | {req_eps_vs_display} | {interpretation} |"
        )

    lines.append("")

    # Row-level table
    lines.append("## Row-Level Market-Implied Anchor")
    lines.append("")
    lines.append("| Ticker | Company | Current price | Base | Market anchor | Market weight | Current/Base premium | Market anchor source | Read-through |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        price = fmt(r.get("current_price"), 2)
        base = fmt(r.get("base"), 2)
        mkt = fmt(r.get("market_anchor"), 2)
        mw = float_or_none(r.get("market_weight")) or 0.0
        mw_str = f"{mw * 100:.0f}%"
        mkt_src = r.get("market_anchor_source", "")

        # Current/Base premium
        price_val = float_or_none(r.get("current_price"))
        base_val = float_or_none(r.get("base"))
        premium = ""
        if price_val and base_val and base_val > 0:
            prem = (price_val / base_val - 1) * 100
            premium = f"+{prem:.1f}%" if prem >= 0 else f"{prem:.1f}%"

        # Read-through
        if price_val and base_val and price_val > base_val:
            read_through = "现价高于 Base，需要订单、毛利和现金流继续证明。"
        elif price_val and base_val and price_val < base_val:
            read_through = "现价低于 Base，重点验证分母质量。"
        else:
            read_through = "需要验证收入、毛利率和订单证据。"

        lines.append(
            f"| {ticker} | {company} | {price} | {base} | {mkt} | {mw_str} | {premium} | {mkt_src} | {read_through} |"
        )

    return "\n".join(lines)


def generate_next_quarter_threshold(rows: list[dict]) -> str:
    lines = []
    lines.append("## Next-Quarter Threshold")
    lines.append("")
    lines.append("| Ticker | Company | Chain bucket | Threshold | Invalidation |")
    lines.append("|---|---|---|---|---|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        bucket = r.get("chain_bucket", "")
        threshold = str(r.get("next_quarter_validation_threshold", ""))
        invalidation = str(r.get("invalidation", ""))

        # Clean up threshold (take first sentence)
        if "；" in threshold:
            threshold = threshold.split("；")[0]
        elif ";" in threshold:
            threshold = threshold.split(";")[0]
        if len(threshold) > 80:
            threshold = threshold[:77] + "..."

        if len(invalidation) > 60:
            invalidation = invalidation[:57] + "..."

        lines.append(f"| {ticker} | {company} | {bucket} | {threshold} | {invalidation} |")

    return "\n".join(lines)


def generate_broker_comparison(rows: list[dict]) -> str:
    lines = []
    lines.append("## Broker/Street Comparison")
    lines.append("")
    lines.append("The broker table distinguishes explicit target-price anchors from forecast-only PDFs, official-disclosure substitutes and zero-weight Street rows.")
    lines.append("")
    lines.append("| Ticker | Company | Bucket | Broker | Date | Target | Forecasts | Source quality | Broker weight |")
    lines.append("|---|---|---|---|---|---:|---|---|---:|")

    for r in rows:
        ticker = r.get("ticker", "")
        company = r.get("company", "")
        bucket = r.get("broker_coverage_bucket", "")
        broker = r.get("broker", "")
        broker_date = r.get("broker_date", "")
        broker_target = r.get("broker_target", "")
        broker_target_display = fmt(broker_target, 2) if float_or_none(broker_target) is not None else "未披露"

        # Build forecasts string
        rev = fmt(r.get("revenue_2026e_100mn"), 2)
        np_ = fmt(r.get("np_2026e_100mn"), 2)
        eps = fmt(r.get("eps_2026e"), 2)
        forecasts = f"收入{rev}；净利{np_}；EPS{eps}"

        source_quality = r.get("broker_source_quality", "")
        bw = float_or_none(r.get("broker_weight")) or 0.0
        bw_str = f"{bw * 100:.0f}%"

        lines.append(
            f"| {ticker} | {company} | {bucket} | {broker} | {broker_date} | {broker_target_display} | {forecasts} | {source_quality} | {bw_str} |"
        )

    return "\n".join(lines)


def main() -> int:
    print("Loading combined valuation model...")
    combined = load_combined()
    rows = combined.get("rows", [])
    meta = combined.get("metadata", {})
    print(f"  {len(rows)} rows loaded")

    # Generate all sections
    sections = []

    # Header
    price_benchmark = meta.get("price_benchmark", f"{RUN_DATE}统一收盘价基准")
    generated_at = meta.get("generated_at", datetime.now().isoformat(timespec="seconds"))

    sections.append("# Valuation Model")
    sections.append("")
    sections.append(f"价格基准: **{price_benchmark}** (Sina Finance {RUN_DATE} 15:00收盘价)。所有{len(rows)}只标的价格时间截面已统一。")
    sections.append("")

    # Final Valuation Table
    sections.append(generate_final_valuation_table(rows))
    sections.append("")

    # Price Reconciliation
    sections.append(generate_price_reconciliation(rows))
    sections.append("")

    # Three-Tier Targets
    sections.append(generate_three_tier_targets(rows))
    sections.append("")

    # Target Formula Recalculation
    sections.append(generate_target_formula_recalc(rows))
    sections.append("")

    # Row-Level Valuation Formula
    sections.append(generate_row_level_valuation(rows))
    sections.append("")

    # Relative / PEG / PSG Comparison
    sections.append(generate_relative_peg_psg(rows))
    sections.append("")

    # Seasonality Calibration (static text)
    sections.append("## Seasonality Calibration")
    sections.append("")
    sections.append("Original rows use the 2026Q1 / 2025A seasonality bridge in `data/current_valuation_model_20260630.json`. Extended rows use the 2026Q1 / 2025A denominator refresh in `data/core_candidate_extended_market_financials_20260702.json`; rejected broker forecast pairs are disclosed through `forecast_quality_flags`.")
    sections.append("")

    # Method and Assumption Bridge (static text)
    sections.append("## Method and Assumption Bridge")
    sections.append("")
    sections.append("Methods are assigned by business model, not by theme label: optical and AI PCB names use PE/PEG/PS cross-checks; server and network-equipment names use PE with inventory, receivable and gross-margin discipline; power, cooling and AIDC operators use normalized PE plus project acceptance, utilization, cash-flow and leverage checks; loss-making milestone names require explicit PS/SOTP evidence.")
    sections.append("")

    # Market-Expectation Valuation Bridge (static text)
    sections.append("## Market-Expectation Valuation Bridge")
    sections.append("")
    sections.append("The market-expectation bridge compares current price with the base-case multiple, required EPS and required revenue by group. A negative AStock upside does not mean the company is strategically weak; it means current price already requires longer growth duration, higher margin or stronger customer/order evidence than the base case currently supports.")
    sections.append("")

    # Next-Quarter Threshold
    sections.append(generate_next_quarter_threshold(rows))
    sections.append("")

    # Broker/Street Comparison
    sections.append(generate_broker_comparison(rows))
    sections.append("")

    # Market-Implied Sentiment Anchor
    sections.append(generate_market_implied_sentiment(rows))
    sections.append("")

    # Growth Earnings Dependency (static text)
    sections.append("## Growth Earnings Dependency")
    sections.append("")
    sections.append("Every target-price/fair-value row must remain tied to revenue exposure, unit/order proxy, ASP/proxy, gross margin, net profit, EPS and current-price-implied checks. Rows without valid positive EPS or explicit PS/SOTP evidence stay outside the 56-row publication universe.")
    sections.append("")

    # Full-Chain Classification Dependency (static text)
    sections.append("## Full-Chain Classification Dependency")
    sections.append("")
    sections.append("The 56-row valuation universe is the investable subset of the 173-name mapped AIDC pool and the 58-name core candidate pool. Full-chain position matters only after evidence and financial denominators pass.")
    sections.append("")

    # Write output
    output = "\n".join(sections)
    out_path = ANALYSIS / "valuation_model.md"
    out_path.write_text(output, encoding="utf-8")
    print(f"Written: {out_path}")
    print(f"  Lines: {len(output.splitlines())}")

    # Print summary stats
    upsides = [float_or_none(r.get("upside")) for r in rows]
    valid = [u for u in upsides if u is not None]
    if valid:
        print(f"  Average upside: {sum(valid) / len(valid) * 100:.1f}%")
        print(f"  Positive: {sum(1 for u in valid if u > 0)}/{len(valid)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
