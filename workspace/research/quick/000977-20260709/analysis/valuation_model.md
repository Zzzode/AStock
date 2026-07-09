# Valuation Model: 000977 浪潮信息

Model date: 2026-07-09
Current price: CNY85.99
Shares: 1.46848bn
Market cap: CNY126.3bn

## Final Valuation Table

| ticker | company | current price | shares | market cap | 2026E NP | 2026E EPS | method | bear | base | bull | final target | upside | action |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| 000977 | 浪潮信息 | 85.99 | 1.46848bn | CNY126.3bn | CNY5.55bn | 3.78 | blended PE + sentiment + Street revision | 67 | 91 | 126 | 96 | +11.6% | pullback entry / hold, do not chase limit-up |

## Three-Tier Targets

| scenario | EPS | PE | value | logic |
|---|---:|---:|---:|---|
| bear | 3.03 | 22x | 67 | Q2 profit partially reverses; cash flow remains weak |
| base | 3.78 | 24x | 91 | H1 profit reset is partly durable; H2 stable |
| bull | 4.66 | 27x | 126 | high-end AI server/liquid-cooling mix continues and 2027E EPS 5+ becomes credible |

Bubble degree vs base target: current / base - 1 = -5.5%; not a bubble on the new denominator, but the post-limit-up price is already close to fair value.

## Market-Implied Sentiment Anchor

Market anchor: CNY103. Current two-day limit-up and CNY18.19bn turnover imply the market is starting to price 2026E EPS around CNY3.8-4.0 and PE 22-25x. This is supportable only if H2 profit does not collapse and cash conversion improves.

Street anchor: CNY90. The Street anchor is capped because most absolute targets were published before or immediately after the H1 preannouncement and now lag the current price. The more useful signal is upward revision: Capital target 60 -> 90; Kaiyuan 2026E net profit 32.95 -> 51.26 CNY100mn.

Final target formula:
- Fundamental anchor: CNY91 * 60%
- Market-implied sentiment anchor: CNY103 * 25%
- Street target/revision anchor: CNY90 * 15%
- Final target = CNY93.85, rounded to CNY96 after allowing for the live limit-up sentiment premium and broker revision lag.

## Relative / PEG / PSG Comparison

At CNY85.99:
- 2025A PE: 52.5x, expensive on old denominator.
- 2026E base PE: 22.8x, reasonable for an AI server leader if margin reset holds.
- 2027E Kaiyuan PE: 16.6x, attractive only if 2027E EPS 5.17 becomes credible.

## Seasonality Calibration

H1 midpoint NP is CNY2.85bn. Q1 was CNY0.605bn, so implied Q2 is CNY2.245bn. The base case does not annualize Q2 directly; it assumes H2 CNY2.70bn, slightly below Q2 annualized run rate, to account for supply, customer pricing, and working-capital risk.

## Next-Quarter Threshold

The next report must validate:
- H2 gross margin above 5.8%.
- H2 operating cash flow turns positive or materially improves from Q1.
- Contract liabilities stop falling or new order commentary offsets the decline.
- Inventory and receivable growth remain proportional to revenue/order growth.

## Method and Assumption Bridge

Primary method: PE on 2026E EPS because the stock has positive earnings and earnings reset is the main thesis.
Secondary check: market-implied PE and broker revision trend.
Why not PS/SOTP: AI server revenue split and unit economics are not disclosed; using PS would reward low-margin revenue without proving EPS conversion.

## Broker/Street Comparison

See `data/broker_street_consensus_20260709.md`.

## Growth Earnings Dependency

See `analysis/growth_earnings_model.md`. The model uses earnings credit, not pure optionality credit, because H1 preannouncement already confirms profit conversion. Bull-case upside still requires H2 validation.

## Full-Chain Classification Dependency

See `analysis/supply_chain_model.md`. 000977 is eligible as a direct AIDC core valuation ticker, but the valuation carries a working-capital and customer-concentration discount.
