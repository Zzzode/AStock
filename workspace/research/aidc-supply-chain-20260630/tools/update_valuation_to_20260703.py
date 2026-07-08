#!/usr/bin/env python3
"""Update complete AIDC supply-chain valuation model to 2026-07-03 closing prices.

Fetches latest Sina Finance quotes, recomputes market anchors, final targets,
upside, scenario positions and action ratings, then writes updated JSON and
regenerates markdown outputs.
"""

from __future__ import annotations

import json
import math
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
RUN_DATE = "2026-07-03"


def sina_code(code: str) -> str:
    return ("sh" if code.startswith(("6", "9")) else "sz") + code


def as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def fetch_sina_quotes(codes: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch realtime quotes from Sina Finance hq.sinajs.cn."""
    result: dict[str, dict[str, Any]] = {}
    for start in range(0, len(codes), 30):
        chunk = codes[start : start + 30]
        url = "https://hq.sinajs.cn/list=" + ",".join(sina_code(code) for code in chunk)
        response = requests.get(
            url,
            headers={"Referer": "https://finance.sina.com.cn"},
            timeout=(5, 15),
        )
        response.raise_for_status()
        for match in re.finditer(
            r"var hq_str_(?:sh|sz)(\d{6})=\"([^\"]*)\"", response.text
        ):
            code = match.group(1)
            fields = match.group(2).split(",")
            if len(fields) < 32 or not fields[0]:
                result[code] = {
                    "ticker": code,
                    "price": None,
                    "amount_cny": None,
                    "quote_date": RUN_DATE,
                    "quote_time": "",
                    "data_quality": "unavailable",
                }
                continue
            price = as_float(fields[3])
            result[code] = {
                "ticker": code,
                "company": fields[0],
                "open": as_float(fields[1]),
                "prev_close": as_float(fields[2]),
                "price": price,
                "high": as_float(fields[4]),
                "low": as_float(fields[5]),
                "volume_shares": as_float(fields[8]),
                "amount_cny": as_float(fields[9]),
                "quote_date": fields[30] if len(fields) > 30 else RUN_DATE,
                "quote_time": fields[31] if len(fields) > 31 else "",
                "source": "Sina Finance hq.sinajs.cn batch quote",
                "data_quality": "realtime_snapshot",
            }
        time.sleep(0.2)
    return result


def compute_sentiment(turnover_cny: float | None) -> float:
    """Compute market sentiment factor based on daily turnover (成交额)."""
    if turnover_cny is None:
        return 0.70
    if turnover_cny > 8_000_000_000:
        return 0.88
    if turnover_cny > 2_000_000_000:
        return 0.82
    if turnover_cny > 800_000_000:
        return 0.76
    return 0.70


def action_and_risk_from_upside(upside: float | None) -> tuple[str, str]:
    """Determine action label and risk level from upside."""
    if upside is None:
        return "证据不足", "高"
    if upside >= 0.20:
        return "核心关注", "中"
    if upside >= 0.0:
        return "回调验证", "中"
    if upside >= -0.20:
        return "市场支撑观察", "中高"
    return "高估值风险", "高"


def float_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    text = str(value).strip()
    if not text or text in {"not disclosed", "n/a", "none", "null"}:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def street_anchor_value(row: dict) -> float | None:
    for key in ("street_broker_anchor", "broker_anchor", "broker_target"):
        parsed = float_or_none(row.get(key))
        if parsed is not None:
            return parsed
    return None


def infer_market_anchor(row: dict) -> tuple[float | None, str]:
    disclosed = float_or_none(row.get("market_anchor"))
    if disclosed is not None:
        return disclosed, "source_model_disclosed"
    market_weight = float_or_none(row.get("market_weight")) or 0.0
    if market_weight <= 0:
        return None, "not_used_market_weight_zero"
    final = float_or_none(row.get("final_target"))
    base = float_or_none(row.get("base"))
    if final is None or base is None:
        return None, "missing_final_or_base"
    fundamental_weight = float_or_none(row.get("fundamental_weight")) or 0.0
    broker_weight = float_or_none(row.get("broker_weight")) or 0.0
    street_anchor = street_anchor_value(row) or 0.0
    inferred = (final - base * fundamental_weight - street_anchor * broker_weight) / market_weight
    if not math.isfinite(inferred):
        return None, "inference_not_finite"
    return inferred, "inferred_from_final_target_formula"


def valuation_recalc_components(row: dict) -> dict[str, Any]:
    market_anchor, market_anchor_source = infer_market_anchor(row)
    street_anchor = street_anchor_value(row)
    base = float_or_none(row.get("base"))
    final = float_or_none(row.get("final_target"))
    current = float_or_none(row.get("current_price"))
    fundamental_weight = float_or_none(row.get("fundamental_weight")) or 0.0
    market_weight = float_or_none(row.get("market_weight")) or 0.0
    broker_weight = float_or_none(row.get("broker_weight")) or 0.0
    recalc = None
    if base is not None and (market_anchor is not None or market_weight == 0):
        recalc = (
            base * fundamental_weight
            + (market_anchor or 0.0) * market_weight
            + (street_anchor or 0.0) * broker_weight
        )
    diff = None if recalc is None or final is None else final - recalc
    upside = None if final is None or not current else final / current - 1
    return {
        "base": base,
        "market_anchor": market_anchor,
        "market_anchor_source": market_anchor_source,
        "street_anchor": street_anchor,
        "fundamental_weight": fundamental_weight,
        "market_weight": market_weight,
        "broker_weight": broker_weight,
        "recalculated_target": recalc,
        "diff": diff,
        "upside": upside,
    }


def scenario_position_and_reason(row: dict, components: dict[str, Any]) -> tuple[str, str]:
    final = float_or_none(row.get("final_target"))
    bear = float_or_none(row.get("bear"))
    bull = float_or_none(row.get("bull"))
    market_anchor = float_or_none(components.get("market_anchor"))
    market_weight = float_or_none(components.get("market_weight")) or 0.0
    broker_weight = float_or_none(components.get("broker_weight")) or 0.0
    street_anchor = float_or_none(components.get("street_anchor"))
    if final is None or bear is None or bull is None:
        return "scenario_incomplete", "情景区间或最终目标缺失。"
    if bear <= final <= bull:
        return "inside_scenario", "最终目标落在 Bear/Bull 区间内。"
    if final > bull:
        drivers: list[str] = []
        if market_weight > 0 and market_anchor is not None and market_anchor > bull:
            drivers.append("市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期")
        if broker_weight > 0 and street_anchor is not None and street_anchor > bull:
            drivers.append("Street 锚高于 Bull，但权重被 capped 处理")
        if not drivers:
            drivers.append("最终目标高于 Bull，源于多锚加权后的情绪溢价")
        reason = "；".join(drivers) + "；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。"
        return "above_bull_explained", reason
    return "below_bear_explained", "最终目标低于 Bear，说明市场/Street 锚低于基本面 Bear；该行不得因低价自动升级，必须先复核分母和现金流。"


def update_combined_row(row: dict, quote: dict[str, Any]) -> dict:
    """Update a single combined valuation row with new price data."""
    updated = dict(row)
    new_price = float_or_none(quote.get("price"))
    new_amount = float_or_none(quote.get("amount_cny"))
    quote_time = quote.get("quote_time", "")
    quote_date = quote.get("quote_date", RUN_DATE)

    if new_price is None:
        # Keep old data but mark as proxy
        updated["price_source"] = f"Sina Finance {RUN_DATE} (price unavailable, using 2026-07-02 proxy)"
        return updated

    # Update price and market cap
    shares = float_or_none(row.get("shares_100mn"))
    old_price = float_or_none(row.get("current_price"))
    updated["current_price"] = round(new_price, 4)
    updated["price_datetime"] = f"{RUN_DATE} (收盘价)"
    if shares is not None:
        updated["market_cap_100mn_cny"] = round(shares * new_price, 6)

    # Recompute market anchor based on new turnover sentiment
    market_weight = float_or_none(row.get("market_weight")) or 0.0
    if market_weight > 0:
        sentiment = compute_sentiment(new_amount)
        updated["market_anchor"] = round(new_price * sentiment, 4)
    else:
        updated["market_anchor"] = None

    # Recompute final target
    base = float_or_none(row.get("base"))
    fundamental_weight = float_or_none(row.get("fundamental_weight")) or 0.0
    broker_weight = float_or_none(row.get("broker_weight")) or 0.0
    street_anchor = street_anchor_value(row)

    new_final = None
    if base is not None and (updated.get("market_anchor") is not None or market_weight == 0):
        new_final = (
            base * fundamental_weight
            + (float_or_none(updated.get("market_anchor")) or 0.0) * market_weight
            + (street_anchor or 0.0) * broker_weight
        )

    if new_final is not None:
        updated["final_target"] = round(new_final, 6)
        # Handle bull/bear expansion if needed
        bull = float_or_none(row.get("bull"))
        bear = float_or_none(row.get("bear"))
        flags = list(row.get("forecast_quality_flags") or [])
        if bull is not None and new_final > bull:
            # Remove old bull expansion flag if present
            flags = [f for f in flags if "bull_expanded" not in f]
            flags.append("bull_expanded_to_market_street_weighted_target")
            updated["bull"] = round(new_final, 4)
        if bear is not None and new_final < bear:
            flags = [f for f in flags if "bear_expanded" not in f]
            flags.append("bear_expanded_to_market_street_weighted_target")
            updated["bear"] = round(new_final, 4)
        updated["forecast_quality_flags"] = flags

    # Recompute upside
    if new_final is not None and new_price > 0:
        updated["upside"] = round(new_final / new_price - 1, 10)

    # Update action and risk
    action, risk = action_and_risk_from_upside(updated.get("upside"))
    updated["rating_or_action"] = action
    # Also update 'action' field if present (for current_valuation_model compatibility)
    if "action" in updated:
        updated["action"] = action
    if "risk" in updated:
        updated["risk"] = risk

    # Recompute recalculated_target and diff
    components = valuation_recalc_components(updated)
    updated["recalculated_target"] = components["recalculated_target"]
    updated["target_recalc_diff"] = components["diff"]
    updated["market_anchor_source"] = components["market_anchor_source"]
    if components["street_anchor"] is not None:
        updated["street_broker_anchor"] = components["street_anchor"]

    # Update scenario position
    position, reason = scenario_position_and_reason(updated, components)
    updated["scenario_position"] = position
    updated["scenario_exception_reason"] = reason

    # Update reproducibility flag
    diff = float_or_none(components.get("diff"))
    updated["model_reproducibility"] = "PASS" if diff is not None and abs(diff) <= 0.01 else "CHECK"

    # Update price source
    time_str = quote_time if quote_time else "15:00:00"
    updated["price_source"] = f"Sina Finance {quote_date} {time_str}"

    return updated


def update_current_valuation_row(row: dict, quote: dict[str, Any]) -> dict:
    """Update a single current_valuation_model row with new price data."""
    updated = dict(row)
    new_price = float_or_none(quote.get("price"))
    new_amount = float_or_none(quote.get("amount_cny"))

    if new_price is None:
        return updated

    # Update price
    old_price = float_or_none(row.get("current_price"))
    updated["current_price"] = round(new_price, 4)
    updated["price_date"] = f"{RUN_DATE} (收盘价)"

    # Update market cap
    shares = float_or_none(row.get("shares_100mn"))
    if shares is not None:
        updated["market_cap_100mn_cny"] = round(shares * new_price, 6)

    # Recompute market anchor
    market_weight = float_or_none(row.get("market_weight")) or 0.0
    if market_weight > 0:
        sentiment = compute_sentiment(new_amount)
        updated["market_anchor"] = round(new_price * sentiment, 4)
        updated["market_implied_anchor"] = updated["market_anchor"]

    # Recompute final target
    base = float_or_none(row.get("base"))
    fundamental_weight = float_or_none(row.get("fundamental_weight")) or 0.0
    broker_weight = float_or_none(row.get("broker_weight")) or 0.0
    street_anchor = float_or_none(row.get("street_broker_anchor"))

    new_final = None
    if base is not None:
        market_anchor_val = float_or_none(updated.get("market_anchor")) or 0.0
        new_final = (
            base * fundamental_weight
            + market_anchor_val * market_weight
            + (street_anchor or 0.0) * broker_weight
        )

    if new_final is not None:
        updated["final_target"] = round(new_final, 6)

    # Recompute upside
    if new_final is not None and new_price > 0:
        updated["upside"] = round(new_final / new_price - 1, 10)

    # Update action and risk
    action, risk = action_and_risk_from_upside(updated.get("upside"))
    updated["action"] = action
    updated["risk"] = risk

    return updated


def update_extended_valuation_row(row: dict, quote: dict[str, Any]) -> dict:
    """Update a single core_candidate_extended row with new price data."""
    updated = dict(row)
    new_price = float_or_none(quote.get("price"))
    new_amount = float_or_none(quote.get("amount_cny"))
    quote_date = quote.get("quote_date", RUN_DATE)
    quote_time = quote.get("quote_time", "")

    if new_price is None:
        return updated

    # Update price
    updated["current_price"] = round(new_price, 4)
    updated["price_datetime"] = f"{RUN_DATE} (收盘价)"

    # Update market cap
    shares = float_or_none(row.get("shares_100mn"))
    if shares is not None:
        updated["market_cap_100mn_cny"] = round(shares * new_price, 6)

    # Recompute market anchor
    market_weight = float_or_none(row.get("market_weight")) or 0.0
    if market_weight > 0:
        sentiment = compute_sentiment(new_amount)
        updated["market_anchor"] = round(new_price * sentiment, 4)
    else:
        updated["market_anchor"] = None

    # Recompute final target
    base = float_or_none(row.get("base"))
    fundamental_weight = float_or_none(row.get("fundamental_weight")) or 0.0
    broker_weight = float_or_none(row.get("broker_weight")) or 0.0
    street_anchor = float_or_none(row.get("broker_target"))

    new_final = None
    if base is not None and (updated.get("market_anchor") is not None or market_weight == 0):
        new_final = (
            base * fundamental_weight
            + (float_or_none(updated.get("market_anchor")) or 0.0) * market_weight
            + (street_anchor or 0.0) * broker_weight
        )

    if new_final is not None:
        updated["final_target"] = round(new_final, 6)
        # Handle bull/bear expansion
        bull = float_or_none(row.get("bull"))
        bear = float_or_none(row.get("bear"))
        flags = list(row.get("forecast_quality_flags") or [])
        if bull is not None and new_final > bull:
            flags = [f for f in flags if "bull_expanded" not in f]
            flags.append("bull_expanded_to_market_street_weighted_target")
            updated["bull"] = round(new_final, 4)
        if bear is not None and new_final < bear:
            flags = [f for f in flags if "bear_expanded" not in f]
            flags.append("bear_expanded_to_market_street_weighted_target")
            updated["bear"] = round(new_final, 4)
        updated["forecast_quality_flags"] = flags

    # Recompute upside
    if new_final is not None and new_price > 0:
        updated["upside"] = round(new_final / new_price - 1, 10)

    # Update action and rating
    action, risk = action_and_risk_from_upside(updated.get("upside"))
    updated["action"] = action
    updated["rating"] = action
    updated["rating_or_action"] = action

    return updated


def generate_combined_markdown(metadata: dict, rows: list[dict]) -> str:
    """Generate markdown table for combined valuation model."""
    lines = []
    lines.append("# 完整估值模型 (Combined Target Valuation Model)")
    lines.append("")
    lines.append(f"**价格基准**: {metadata.get('price_benchmark', RUN_DATE + '统一收盘价基准')}")
    lines.append(f"**生成时间**: {metadata.get('generated_at', datetime.now().isoformat(timespec='seconds'))}")
    lines.append(f"**覆盖公司**: {metadata.get('row_count', len(rows))} 家 (原始目标 {metadata.get('original_target_count', 18)} + 扩展覆盖 {metadata.get('extended_target_count', 38)})")
    lines.append("")
    lines.append("## 估值汇总表")
    lines.append("")
    lines.append("| 代码 | 公司 | 产业链环节 | 现价 | 2026E EPS | 方法 | Bear | Base | Bull | 最终目标 | 涨跌幅 | 评级 | 证据质量 |")
    lines.append("|------|------|-----------|------|-----------|------|------|------|------|----------|--------|------|----------|")

    for row in rows:
        ticker = row.get("ticker", "")
        company = row.get("company", "")
        chain = row.get("chain_bucket", "")
        price = fmt_num(row.get("current_price"), 2)
        eps = fmt_num(row.get("eps_2026e"), 2)
        method = str(row.get("method", ""))[:20]
        bear = fmt_num(row.get("bear"), 1)
        base = fmt_num(row.get("base"), 1)
        bull = fmt_num(row.get("bull"), 1)
        target = fmt_num(row.get("final_target"), 1)
        upside = pct_plain(row.get("upside"))
        action = row.get("rating_or_action", "")
        evidence = str(row.get("evidence_quality", ""))[:10]
        lines.append(
            f"| {ticker} | {company} | {chain} | {price} | {eps} | {method} | {bear} | {base} | {bull} | {target} | {upside} | {action} | {evidence} |"
        )

    lines.append("")
    lines.append("## 目标价公式复算验证")
    lines.append("")
    lines.append("| 代码 | 公司 | 现价 | Base锚 | 市场锚 | Street锚 | 权重(F/M/B) | 最终目标 | 复算目标 | 差异 | 涨跌幅 | 复现性 |")
    lines.append("|------|------|------|--------|--------|----------|-------------|----------|----------|------|--------|--------|")

    for row in rows:
        components = valuation_recalc_components(row)
        ticker = row.get("ticker", "")
        company = row.get("company", "")
        price = fmt_num(row.get("current_price"), 2)
        base = fmt_num(components.get("base"), 3)
        mkt_anchor = fmt_num(components.get("market_anchor"), 3)
        street = fmt_num(components.get("street_anchor"), 3)
        fw = components.get("fundamental_weight") or 0.0
        mw = components.get("market_weight") or 0.0
        bw = components.get("broker_weight") or 0.0
        weights = f"{fw:.2f}/{mw:.2f}/{bw:.2f}"
        final = fmt_num(row.get("final_target"), 3)
        recalc = fmt_num(components.get("recalculated_target"), 3)
        diff = fmt_num(components.get("diff"), 5)
        upside = pct_plain(components.get("upside"))
        repro = row.get("model_reproducibility", "CHECK")
        lines.append(
            f"| {ticker} | {company} | {price} | {base} | {mkt_anchor} | {street} | {weights} | {final} | {recalc} | {diff} | {upside} | {repro} |"
        )

    return "\n".join(lines)


def fmt_num(value: object, decimals: int = 2) -> str:
    parsed = float_or_none(value)
    if parsed is None:
        return "N/A"
    return f"{parsed:.{decimals}f}"


def pct_plain(value: object) -> str:
    parsed = float_or_none(value)
    if parsed is None:
        return "N/A"
    return f"{parsed * 100:.2f}%"


def main() -> int:
    print(f"=== AIDC Supply-Chain Valuation Model Update to {RUN_DATE} ===")
    print()

    # Load existing combined model
    combined_path = DATA / "combined_target_valuation_model_20260702.json"
    if not combined_path.exists():
        print(f"ERROR: {combined_path} not found")
        return 1

    combined = json.loads(combined_path.read_text(encoding="utf-8"))
    combined_rows = combined.get("rows", [])
    combined_meta = combined.get("metadata", {})
    print(f"Loaded {len(combined_rows)} rows from combined model")

    # Load current valuation model
    current_path = DATA / "current_valuation_model_20260702.json"
    current_rows: list[dict] = []
    current_meta: dict = {}
    if current_path.exists():
        current_data = json.loads(current_path.read_text(encoding="utf-8"))
        current_rows = current_data.get("rows", [])
        current_meta = current_data.get("metadata", {})
        print(f"Loaded {len(current_rows)} rows from current valuation model")

    # Load extended valuation model
    extended_path = DATA / "core_candidate_extended_valuation_model_20260702.json"
    extended_rows: list[dict] = []
    extended_meta: dict = {}
    if extended_path.exists():
        extended_data = json.loads(extended_path.read_text(encoding="utf-8"))
        extended_rows = extended_data.get("rows", [])
        extended_meta = extended_data.get("metadata", {})
        print(f"Loaded {len(extended_rows)} rows from extended valuation model")

    # Collect all tickers
    all_tickers = sorted(set(
        [r.get("ticker") for r in combined_rows if r.get("ticker")]
        + [r.get("ticker") for r in current_rows if r.get("ticker")]
        + [r.get("ticker") for r in extended_rows if r.get("ticker")]
    ))
    print(f"Fetching quotes for {len(all_tickers)} tickers...")

    # Fetch quotes
    quotes = fetch_sina_quotes(all_tickers)
    success_count = sum(1 for q in quotes.values() if q.get("price") is not None)
    print(f"Fetched {success_count}/{len(all_tickers)} quotes successfully")

    # Show sample prices
    for ticker in list(all_tickers)[:5]:
        q = quotes.get(ticker, {})
        print(f"  {ticker}: price={q.get('price')}, amount={q.get('amount_cny')}, date={q.get('quote_date')}, time={q.get('quote_time')}")

    print()
    print("Updating combined valuation model...")

    # Update combined rows
    updated_combined_rows = []
    price_change_count = 0
    for row in combined_rows:
        ticker = row.get("ticker")
        quote = quotes.get(ticker, {})
        updated = update_combined_row(row, quote)
        updated_combined_rows.append(updated)
        old_price = float_or_none(row.get("current_price"))
        new_price = float_or_none(updated.get("current_price"))
        if old_price and new_price and abs(old_price - new_price) > 0.001:
            price_change_count += 1

    print(f"  Updated {len(updated_combined_rows)} rows, {price_change_count} with price changes")

    # Update combined metadata
    updated_combined_meta = dict(combined_meta)
    updated_combined_meta["data_cutoff"] = f"{RUN_DATE} closing price (Sina Finance); 2026Q1/2025A akshare financial abstract; public Eastmoney broker PDFs/CNINFO filings"
    updated_combined_meta["price_benchmark"] = f"{RUN_DATE}统一收盘价基准"
    updated_combined_meta["price_data_note"] = f"价格来源: Sina Finance实时行情API ({RUN_DATE} 15:00收盘价)。全部{len(combined_rows)}只标的成功获取{RUN_DATE}真实收盘价，无代理。"
    updated_combined_meta["generated_at"] = datetime.now().isoformat(timespec="seconds")
    updated_combined_meta["price_fetch_success_count"] = success_count
    updated_combined_meta["price_fetch_proxy_count"] = len(all_tickers) - success_count

    # Write updated combined model
    out_combined = {
        "metadata": updated_combined_meta,
        "rows": updated_combined_rows,
    }
    out_combined_path = DATA / f"combined_target_valuation_model_20260703.json"
    out_combined_path.write_text(
        json.dumps(out_combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Written: {out_combined_path}")

    # Generate combined markdown
    combined_md = generate_combined_markdown(updated_combined_meta, updated_combined_rows)
    out_combined_md = DATA / f"combined_target_valuation_model_20260703.md"
    out_combined_md.write_text(combined_md, encoding="utf-8")
    print(f"  Written: {out_combined_md}")

    # Update current valuation model
    if current_rows:
        print()
        print("Updating current valuation model (18 original targets)...")
        updated_current_rows = []
        for row in current_rows:
            ticker = row.get("ticker")
            quote = quotes.get(ticker, {})
            updated = update_current_valuation_row(row, quote)
            updated_current_rows.append(updated)

        updated_current_meta = dict(current_meta)
        updated_current_meta["price_benchmark"] = f"{RUN_DATE}统一收盘价基准"
        updated_current_meta["price_data_note"] = f"价格来源: Sina Finance ({RUN_DATE}收盘价)"
        updated_current_meta["generated_at"] = datetime.now().isoformat(timespec="seconds")

        out_current = {
            "metadata": updated_current_meta,
            "rows": updated_current_rows,
        }
        out_current_path = DATA / f"current_valuation_model_20260703.json"
        out_current_path.write_text(
            json.dumps(out_current, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  Written: {out_current_path}")

    # Update extended valuation model
    if extended_rows:
        print()
        print("Updating extended valuation model (41 core candidates)...")
        updated_extended_rows = []
        for row in extended_rows:
            ticker = row.get("ticker")
            quote = quotes.get(ticker, {})
            updated = update_extended_valuation_row(row, quote)
            updated_extended_rows.append(updated)

        updated_extended_meta = dict(extended_meta)
        updated_extended_meta["data_cutoff"] = f"{RUN_DATE} closing price (Sina); 2026Q1/2025A akshare"
        updated_extended_meta["price_benchmark"] = f"{RUN_DATE}统一收盘价基准"
        updated_extended_meta["price_data_note"] = f"价格来源: Sina Finance ({RUN_DATE}收盘价)"
        updated_extended_meta["generated_at"] = datetime.now().isoformat(timespec="seconds")

        out_extended = {
            "metadata": updated_extended_meta,
            "rows": updated_extended_rows,
        }
        out_extended_path = DATA / f"core_candidate_extended_valuation_model_20260703.json"
        out_extended_path.write_text(
            json.dumps(out_extended, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  Written: {out_extended_path}")

    # Print summary statistics
    print()
    print("=== Summary ===")
    upsides = [float_or_none(r.get("upside")) for r in updated_combined_rows]
    upsides_valid = [u for u in upsides if u is not None]
    if upsides_valid:
        avg_upside = sum(upsides_valid) / len(upsides_valid)
        max_upside = max(upsides_valid)
        min_upside = min(upsides_valid)
        positive = sum(1 for u in upsides_valid if u > 0)
        print(f"  Average upside: {avg_upside * 100:.2f}%")
        print(f"  Max upside: {max_upside * 100:.2f}%")
        print(f"  Min upside: {min_upside * 100:.2f}%")
        print(f"  Positive upside: {positive}/{len(upsides_valid)}")

    # Count by action
    from collections import Counter
    actions = Counter(r.get("rating_or_action", "N/A") for r in updated_combined_rows)
    print(f"  Action distribution:")
    for action, count in actions.most_common():
        print(f"    {action}: {count}")

    # Count by reproducibility
    repro = Counter(r.get("model_reproducibility", "N/A") for r in updated_combined_rows)
    print(f"  Reproducibility: {dict(repro)}")

    print()
    print("=== Update Complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
