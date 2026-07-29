---
name: analyze
description: Use when the user asks for a stock's price structure, volume/turnover behaviour, support and resistance formed by real trading, relative strength, catalyst reaction, or a discretionary chart read. Trigger for “技术分析”, “走势怎么看”, “承接”, “分歧”, “突破是否有效”, “趋势位置”, “量价”, or “交易结构”. Do not use a KDJ, RSI, MACD, moving-average crossover, or any single indicator as a directional shortcut; route portfolio or whole-market decisions to market-desk.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /analyze - Price Structure Review

Produce an evidence-labelled, discretionary price-structure review. The Python
packet contains timestamped bars and a quote; it does not generate buy/sell
signals. This review explains *who may be trapped or in control, what changed,
and what would prove the read wrong* rather than applying oscillator thresholds.

This skill may provide a descriptive structure read only. Any question that
asks what to trade, whether to hold/add/reduce/exit, or how to implement a
strategy must be escalated to `market-desk` for a compulsory team decision and
completed shared evidence packet.

## Data collection

```bash
.venv/bin/python -m astock.cli quote <CODE> --json
.venv/bin/python -m astock.cli analyze <CODE> --json --days 120
.venv/bin/python -m astock.cli market-overview --json
```

Supplement only when needed with a source-labelled catalyst, filing, sector
mapping, or a reproducible order-book/auction source. Daily bars never justify
claims about queue position, intraday absorption, or auction intent.

## Reasoning contract

Build the conclusion in this order:

1. **Location** — prior range, gap, high/low, key turnover exchange area, and
   whether the move is an expansion, contraction, failed break, or repair.
2. **Participation** — turnover, range, liquidity, sector/leader behaviour, and
   relative performance where evidence exists. Never infer fund flow from price.
3. **Catalyst and expectation** — what public fact changed, what the market may
   already have priced, and what evidence would distinguish a repricing from
   pure trading heat.
4. **Game hypothesis** — identify the specific, falsifiable proposition (for
   example: leader retains liquidity after a divergence; event reaction is
   absorbed; range failure forces trapped supply out). Do not use named-trader
   folklore as evidence.
5. **Decision boundary** — observable confirmation, invalidation, time stop,
   and the data required before any portfolio action. A structure review alone
   never authorizes an order.

## Output format

```text
Structure State: <initiative / balance / failed expansion / repair / unavailable>
One-line Read: <what the market is testing, not an indicator verdict>
Evidence:
- <timestamped price-volume or relative-performance fact>
- <sector, catalyst, or liquidity fact; otherwise explicitly unavailable>
Game Hypothesis: <falsifiable proposition>
Confirmation: <future observable condition>
Invalidation / Time Stop: <observable condition and review date>
What We Do Not Know: <order book, position, flow, or catalyst gap>
Data Quality: <tier and cutoff>
```

## Non-negotiable boundaries

- MA, MACD, KDJ, RSI, golden/death crosses, and their counts have zero decision
  weight. Do not display them as bullish, bearish, overbought, or oversold.
- A single bar, one-day sector move, or public “fund-flow” claim is not proof of
  control, continuation, or a tradable edge.
- In A shares, state T+1, price-limit, suspension, and overnight-gap constraints
  whenever the user asks for a holding or exit plan.
- Keep this research-only. Portfolio sizing and conditional paper plans belong
  to `market-desk`; no analysis output may place, route, or manage an order.
