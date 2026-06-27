# Valuation Frameworks Reference

## Mandatory Final Valuation Package

Every full research report must publish AStock's own final valuation, not just broker target history or scenario commentary. For every investable or explicitly covered ticker, include:

| Required Field | Purpose |
|---|---|
| Current price/date, share count, market cap, currency/share class | Anchor the valuation to observable market data |
| Forecast revenue/net profit/EPS | Define the earnings denominator |
| Primary method and secondary check | Explain why PE, EV/EBITDA, PS, PB, SOTP, or DCF is appropriate |
| Bull/base/bear values | Show sensitivity and downside protection |
| Final target price or fair-value range | State AStock's own valuation conclusion |
| Implied upside/downside | Convert valuation into investment space |
| Rating/action, catalysts, invalidation | Connect valuation to portfolio behavior |
| Evidence quality | Separate verified data, broker forecast, company guidance, and inference |

If a defensible target cannot be computed, label the ticker `insufficient evidence / watchlist only`. Do not publish an investable recommendation without current-price-based target price or fair-value range.

## Market-Implied Expectations and Sentiment Anchor

Modern equity research must triangulate intrinsic value against observable market pricing. The market can be wrong, crowded, or reflexive, but it is still a live consensus mechanism. A full report therefore needs three valuation anchors:

| Anchor | Purpose | Typical Inputs | Output |
|---|---|---|---|
| Intrinsic/fundamental anchor | Estimate what normalized fundamentals support | Forward revenue, EPS, margin, ROE, cash flow, business-model matched multiples | Fundamental value and downside if sentiment fades |
| Market-implied expectations anchor | Reverse-engineer what current price already assumes | Current price, implied PE/PS/PB/EV multiples, liquidity/turnover, price momentum, crowding, sector sentiment | Market-consensus support level and embedded expectation gap |
| Broker/Street anchor | Compare with external sell-side expectations | Broker target, rating, forecast revenue/NP/EPS, valuation method, source quality | Street gap and bias-adjusted external reference |

The final research target should not mechanically equal the intrinsic anchor when market evidence is strong. It should publish both the intrinsic value and a market-consensus adjusted target, with explicit weights. A typical blend is:

```
final target = intrinsic value × Wf + market-implied anchor × Wm + broker anchor × Ws
```

Suggested weight bands:

| Situation | Wf | Wm | Ws | Guardrail |
|---|---:|---:|---:|---|
| Stable earnings compounder with clean forecasts | 60-75% | 10-25% | 0-20% | Market anchor cannot override deteriorating EPS/cash flow |
| High-growth or strategically scarce technology asset | 45-65% | 20-40% | 0-25% | Require customer/order evidence before using a high sentiment weight |
| Fiber/cable, carrier project, network equipment or asset-heavy cyclical with visible market premium | 40-60% | 25-45% | 0-20% | Do not force a deep-downside target if liquidity and consensus pricing remain strong |
| Low-liquidity, rumor-driven, loss-making or unverifiable theme stock | 65-90% | 0-15% | 0-15% | Sentiment can be discussed but cannot support an investable target |

Required diagnostics:

- Current price versus intrinsic value, broker target and market-implied anchor.
- Implied 2026E PE/PS/PB/EV multiple at the current price.
- Sentiment/crowding indicators: short/medium-term momentum where available, turnover/volume ratio, trading value percentile, rating concentration, target-price dispersion, and sector narrative strength.
- Embedded-expectation gap: what revenue growth, margin, EPS, multiple or duration must be true for the market price to be reasonable.
- Sentiment premium/discount and whether it is supported by evidence, liquidity, broker consensus, policy/capex narrative, or only by theme trading.

Rating/action guardrail: if intrinsic value is far below price but the market-implied anchor is strong, do not automatically publish a mechanical `Reduce`. Use an action such as `Neutral / market-supported watch`, `Event-driven`, or `Hold while validating` and state the trigger that would collapse the sentiment premium. Conversely, strong sentiment alone cannot create a `Buy` without evidence that fundamentals can catch up.

## When to Use Each Method

| Method | Best For | Formula | A-Share Benchmark |
|--------|----------|---------|-------------------|
| PE (市盈率) | Profitable stable growers | Price ÷ EPS | CSI300 ~13×; Growth tech ~30-50× |
| PEG | Comparing growth stocks | PE ÷ EPS Growth% | <1 = undervalued, >2 = expensive |
| PS (市销率) | Revenue-stage / loss-making | Market Cap ÷ Revenue | SaaS ~10-20×; Hardware ~1-3× |
| PSG | Comparing loss-makers | PS ÷ Revenue Growth% | <0.5 = attractive for high-growth |
| PB (市净率) | Asset-heavy / banks | Price ÷ Book Value | Manufacturing ~2-5×; Tech ~8-15× |
| EV/EBITDA | Cross-border / leveraged | Enterprise Value ÷ EBITDA | Industrial ~10-15× |
| DCF | Mature / predictable cash flows | NPV(future FCFs) | Rarely used for A-share tech |

## Business-Model Matched Valuation Is Mandatory

Industry-chain reports cover companies with different profit mechanics. A single PE template is not acceptable across modules, chips, devices, fiber/cable, network equipment, materials and equipment. The valuation model must choose a primary method by business model, then add a secondary sanity check.

| Business Model | Primary Method | Secondary Check | Blocked Method |
|---|---|---|---|
| AI datacenter optical-module leader with durable orders and positive EPS | Forward PE or PEG on normalized EPS | PS and customer/order durability | Pure PS that ignores margin conversion |
| Optical chip, laser, silicon-photonics or scarce precision-device platform | PE plus PS/SOTP scarcity check | Qualification pipeline, gross margin, revenue scale | Low-current-EPS PE as sole target |
| Fiber/cable, carrier project, submarine cable, ODN or asset-heavy transmission company | PB/ROE, EV/EBITDA, PS or SOTP-style blend | Cycle-normalized EPS and cash conversion | Single-quarter annualized EPS × sector PE as sole target |
| Network equipment or carrier/cloud system vendor | PE plus order backlog/cash-flow bridge | PS/PB and segment mix | Treating it as a pure optical-module stock |
| Connector, high-speed copper, cable assembly or mixed interconnect company | SOTP or PE/PS/PB blend by segment | AI exposure purity and working-capital check | One optical-module PE multiple |
| Loss-making, near-zero EPS, early equipment/material option | PS, EV/Sales, transaction comparables or watchlist only | Funding runway and customer validation | PE |

If the selected method produces a nonsensical target because the denominator is temporarily depressed, switch method or label the ticker watchlist-only. Do not publish a mechanically low or high target that contradicts the business model.

## Three-Tier Framework

```
🟠 Bull (乐观档) = Sell-side remote-year logic
   Method: method-matched remote-year scenario → WACC折现 to present
   Purpose: "What price reflects all dreams coming true"
   Equivalent: current profit × 100-400× PE (but disguised as "rational")

🔵 Base (中性档) = Your cold assessment  
   Method: business-model matched valuation on normalized 2026-27E drivers
   Purpose: "What's the stock worth based on the relevant economic driver"
   This is the SAFETY MARGIN anchor

🟢 Bear (悲观档) = Narrative break floor
   Method: de-rated version of the same primary method, or liquidation/cycle floor for asset-heavy names
   Purpose: "Where does it fall if the story dies"
   This is the STOP-LOSS level
```

## PEG Interpretation Guide

| PEG Range | Verdict | Action |
|-----------|---------|--------|
| < 0.3 | Severely undervalued OR growth unsustainable | Verify growth sustainability first |
| 0.3 - 0.7 | Attractive | Core position candidate |
| 0.7 - 1.0 | Fair | Hold, don't chase |
| 1.0 - 2.0 | Fairly valued to slightly expensive | Reduce on strength |
| 2.0 - 5.0 | Expensive | Only for momentum traders |
| > 5.0 | Extreme bubble | Institutional investors must avoid |

## Seasonality Calibration Formula

```
Full-year estimate = Q1 actual profit ÷ Q1 historical share%

Example: 德赛西威
  Q1 actual: 4.61亿
  Q1 historical share: 18% (auto Tier-1 pattern)
  Calibrated full year: 4.61 ÷ 0.18 = 25.6亿
  Calibrated PE: 534亿 ÷ 25.6亿 = 20.9×
```

Sector seasonal patterns:
| Sector | Q1 | Q2 | Q3 | Q4 | Driver |
|--------|----|----|----|----|--------|
| Robot components | 15% | 22% | 30% | 33% | Year-end delivery rush |
| Auto Tier-1 | 18% | 25% | 28% | 29% | Vehicle sales cycle |
| AI compute/servers | 27% | 25% | 24% | 24% | Roughly flat |
| Optical modules | 23% | 27% | 25% | 25% | Q2 overseas ordering peak |

## Sell-Side Bias Decomposition

Sell-side target prices systematically overstate by 50-100%. Mechanism:

```
Analyst "rational" math:
  2028E profit 18.4亿 × 25× mature PE = 460亿
  ÷ WACC折现 2 years (1.25×) = 368亿
  ÷ 1.83亿 shares = 200元/股
  + "execution premium" 30% = 260元
  + "scarcity premium" 25% = 326元

ACTUAL equivalent:
  2026E profit 2亿 × 184× PE = 368亿 = 200元/股
  
The sell-side just disguises 184× PE as "DCF with growth assumptions"
```

Why they do this: giving conservative targets → clients miss rallies → clients leave → revenue drops. Giving optimistic targets → wrong 3 years later → no one remembers. Asymmetric incentive.
