# Valuation Frameworks Reference

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

## Three-Tier Framework

```
🟠 Bull (乐观档) = Sell-side remote-year logic
   Method: 2028-30E profit × mature PE → WACC折现 to present
   Purpose: "What price reflects all dreams coming true"
   Equivalent: current profit × 100-400× PE (but disguised as "rational")

🔵 Base (中性档) = Your cold assessment  
   Method: 2026E static profit × sector consensus PE
   Purpose: "What's the stock worth based on THIS year's actual earnings"
   This is the SAFETY MARGIN anchor

🟢 Bear (悲观档) = Narrative break floor
   Method: Trough profit × de-rated PE (25×)
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
