#!/usr/bin/env python3
"""Update core_candidate_extended_valuation_model.md with 2026-07-03 prices."""

from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"


def main() -> int:
    # Load updated extended model
    with open(DATA / "core_candidate_extended_valuation_model_20260703.json") as f:
        extended = json.load(f)

    # Build lookup by ticker
    by_ticker = {}
    for row in extended.get("rows", []):
        ticker = row.get("ticker", "")
        if ticker:
            by_ticker[ticker] = row

    # Read the markdown file
    md_path = ANALYSIS / "core_candidate_extended_valuation_model.md"
    content = md_path.read_text(encoding="utf-8")

    # Update summary stats
    meta = extended.get("metadata", {})
    target_ready = meta.get("target_model_ready_count", 38)
    broker_target = meta.get("explicit_broker_target_model_count", 13)
    house_model = meta.get("house_target_model_count", 24)
    ps_sotp = meta.get("ps_sotp_target_model_count", 1)
    watchlist = meta.get("watchlist_only_count", 3)

    content = re.sub(
        r"- Target-model ready: \d+",
        f"- Target-model ready: {target_ready}",
        content,
    )
    content = re.sub(
        r"- Explicit broker-target models: \d+",
        f"- Explicit broker-target models: {broker_target}",
        content,
    )
    content = re.sub(
        r"- AStock house fair-value models without explicit Street target: \d+",
        f"- AStock house fair-value models without explicit Street target: {house_model}",
        content,
    )
    content = re.sub(
        r"- PS/SOTP target models for loss-making names: \d+",
        f"- PS/SOTP target models for loss-making names: {ps_sotp}",
        content,
    )
    content = re.sub(
        r"- Watchlist-only: \d+",
        f"- Watchlist-only: {watchlist}",
        content,
    )

    # Update per-company sections
    # Pattern: ## TICKER Company ... - Denominator: price X.XX, shares Y.YY亿股, market cap Z.ZZ亿元.
    for ticker, row in by_ticker.items():
        price = row.get("current_price")
        shares = row.get("shares_100mn")
        mcap = row.get("market_cap_100mn_cny")
        action = row.get("action", row.get("rating", ""))
        target = row.get("final_target")
        upside = row.get("upside")

        if price is None:
            continue

        # Format values
        price_str = f"{float(price):.2f}" if price else "N/A"
        shares_str = f"{float(shares):.2f}" if shares else "N/A"
        mcap_str = f"{float(mcap):.1f}" if mcap else "N/A"
        target_str = f"{float(target):.1f}" if target else "N/A"
        upside_str = f"{float(upside) * 100:.1f}%" if upside is not None else "N/A"

        # Map action to Chinese label
        action_map = {
            "核心关注": "core focus",
            "回调验证": "pullback validation",
            "市场支撑观察": "market support watch",
            "高估值风险": "high valuation risk",
            "回避": "avoid",
            "证据不足": "insufficient evidence",
        }
        action_en = action_map.get(str(action), str(action).lower())

        # Update denominator line
        # Pattern: - Denominator: price XX.XX, shares YY.YY亿股, market cap ZZZ.Z亿元.
        old_denom_pattern = re.compile(
            rf"(## {re.escape(ticker)} [^\n]+\n(?:[^\n]*\n)*?- Denominator: )price [\d.]+, shares [\d.]+亿股, market cap [\d.]+亿元\."
        )

        def replace_denom(match, p=price_str, s=shares_str, m=mcap_str):
            return f"{match.group(1)}price {p}, shares {s}亿股, market cap {m}亿元."

        content = old_denom_pattern.sub(replace_denom, content)

        # Update action/rating line
        # Pattern: - Status: ...; action: ...; rating label: ...
        status_pattern = re.compile(
            rf"(## {re.escape(ticker)} [^\n]+\n(?:[^\n]*\n)*?- Status: [^;]+; )action: [^;]+;( rating label: )[^\n]+\."
        )

        def replace_status(match, a=action, ae=action_en):
            return f"{match.group(1)}action: {ae};{match.group(2)}{a}."

        content = status_pattern.sub(replace_status, content)

    # Write updated content
    md_path.write_text(content, encoding="utf-8")
    print(f"Updated: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
