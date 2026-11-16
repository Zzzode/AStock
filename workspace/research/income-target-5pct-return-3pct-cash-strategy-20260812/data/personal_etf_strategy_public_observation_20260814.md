# Personal ETF Rule — Frozen Public Observation

- Scope ID: `total-return-open-universe-v3-20260814`
- Status: `candidate_rule_rejected_as_stable_5pct_evidence`
- Research-only / formal decision eligible / portfolio q: `true / false / 0`

## Result

The predeclared ETF rule is **rejected as evidence for a stable 5% total-return
objective**. At the primary 10-basis-point one-way-turnover sensitivity, its
full-period annualized *price* return is
5.09%, but
281 of 611 complete,
overlapping rolling five-year price windows fall below 5%; the minimum is
3.88%. It is not total return and
is not an allocation instruction.

## Frozen rule

- At the first observed session of each calendar month, use only the preceding
  observed close.
- A risk sleeve must have positive 252-observation price momentum and close
  above its 200-observation simple moving average.
- Rank 510300, 510880 and 518880 by momentum; hold at most two. Their combined
  marked weight is 50%, split equally. The remainder is 511010; if none pass,
  511010 is 100%.
- Apply a marked target only after one following observed session. No future
  observation is used in the rule calculation.
- This is price-only and uses no cash-receipt target or automatic reinvestment.

## Sensitivity result

| One-way turnover cost (bps) | Annualized price return | Annualized price volatility | Maximum drawdown | 5Y windows at/above 5% | Minimum 5Y annualized price return |
|---:|---:|---:|---:|---:|---:|
| 0 | 5.21% | 7.41% | -12.38% | 385 / 611 | 3.99% |
| 5 | 5.15% | 7.41% | -12.44% | 355 / 611 | 3.93% |
| 10 | 5.09% | 7.41% | -12.49% | 330 / 611 | 3.88% |
| 20 | 4.97% | 7.41% | -12.60% | 300 / 611 | 3.76% |

The windows overlap and are not independent observations. The 0/5/10/20-bps
rows are generic price-impact sensitivities, not assertions about a broker's
charges or execution quality.

## Calendar price rows at 10 bps

| Year | Net price return |
|---:|---:|
| 2019 | 5.59% |
| 2020 | 7.11% |
| 2021 | 1.15% |
| 2022 | -0.39% |
| 2023 | 6.62% |
| 2024 | 8.15% |
| 2025 | 17.34% |
| 2026 | -6.85% |

## Boundary

- Frozen input: `sources/probe-public-market-20260814/e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda.portfolio.replay.json`
  (`SHA-256 8829c0a065aa688c874212500c345c7dd92aff6c88b2bba760f7de7921b15217`).
- The provider is a public aggregation path and values are unadjusted
  secondary-market observations. Product distributions, corporate actions,
  taxes, spreads, T+1, suspensions, limits, lots, settlement, capacity and
  fills are not modelled.
- Latest rule observation: 2026-08-03：risk_on_guardrailed；风险筛选 510880。
- Current action: **do not activate**. The rule remains a research design until
  it has a source-consistent total-return ledger, product-level diligence,
  cost/tax/settlement evidence and independent validation.
