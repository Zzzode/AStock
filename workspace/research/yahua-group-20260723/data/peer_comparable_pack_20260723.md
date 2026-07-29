# Lithium peer-comparable pack — valuation calibration boundary

**Purpose:** give the house valuation model a traceable external P/E range and verify whether 2026Q1 recovery was sector-wide. This is a **calibration packet**, not a mechanical peer-multiple transfer.

## Peer-selection and source boundary

| Company | Code | Why included | Why not a direct substitute for 雅化 | Evidence quality |
|---|---|---|---|---|
| 天齐锂业 | 002466.SZ | Large lithium producer; Q1 confirms sector price beta | SQM associate/investment income, resource mix and overseas exposure differ | Q1 L1; forward P/E L2 aggregation |
| 赣锋锂业 | 002460.SZ | Integrated lithium/resource comparator | Resource portfolio, PLS fair-value effects and scale differ | Q1 preview L1; forward P/E L2 aggregation |
| 盛新锂能 | 002240.SZ | China lithium-salt comparator with Indonesia expansion | Product/resource mix, shareholder structure and overseas capacity differ | Q1 L1; forward P/E L2 aggregation |

## Actual Q1 recovery: evidence for sector beta, not a unit-profit transfer

| Company | 2026Q1 revenue | 2026Q1 attributable NP | Primary disclosure read-through | Prohibited inference |
|---|---:|---:|---|---|
| 雅化 | CNY2.830bn | CNY0.339bn | H1 preview later confirms Q2 profit acceleration, but Q1 cash conversion was negative | Do not extrapolate Q1 or H1 annualized EPS. |
| 天齐 | CNY5.128bn | CNY1.876bn | Product selling prices and SQM investment income both contributed | Do not use its margin as 雅化's lithium margin. |
| 赣锋 | revenue not disclosed in preview | CNY1.60–2.10bn preview range | Lithium-price and resource-capacity factors; includes approximately CNY0.259bn PLS fair-value gain | Do not use as a clean operating-profit comparator. |
| 盛新 | CNY3.284bn | CNY0.464bn | Lithium price and Indonesia shipment growth both contributed | Do not use its growth rate as a volume forecast for 雅化. |

## Forward P/E snapshot: external calibration only

The values below are the `近六月平均` rows in the archived Eastmoney aggregation response as of 2026-07-23. They are secondary, aggregated market expectations—not issuer guidance, not a comparable-company valuation conclusion, and not evidence that the multiples are sustainable.

| Company | Aggregated 2026E EPS | Snapshot 2026E P/E | Aggregated 2027E P/E | 2026E revenue / NP | Permitted model use |
|---|---:|---:|---:|---:|---|
| 天齐 | CNY3.761 | 11.71x | 10.25x | CNY23.750bn / CNY6.426bn | External lithium-cycle reference only. |
| 赣锋 | CNY3.510 | 13.51x | 11.21x | CNY46.107bn / CNY7.360bn | External lithium-cycle reference only. |
| 盛新 | CNY2.102 | 13.16x | 10.18x | CNY13.466bn / CNY1.923bn | External lithium-cycle reference only. |
| Simple mean / median | — | 12.79x / 13.16x | 10.55x / 10.25x | — | **Maximum 20% calibration weight** in an approved house P/E cross-check; never a standalone target-price input. |

## Model-control rule

1. The house P/E must start from 雅化's own normalized EPS and a reasoned premium/discount for resource visibility, earnings quality, customer concentration, cash conversion, and the civil-explosives mix.
2. The L2 aggregation P/E range can test whether the house multiple is out of line. It cannot justify a positive premium, replace a peer-normalization schedule, or be combined with a broker target price.
3. A positive peer premium needs an L1/L2 company-specific bridge; absent that bridge, use a neutral-to-discounted position and show the sensitivity.

Sources: `PEER-TQ-Q1`, `PEER-GF-P`, `PEER-SX-Q1`, `PEER-EST-TQ`, `PEER-EST-GF`, `PEER-EST-SX`; raw paths and hashes are in `sources/rebuild-industry-peer-20260723/capture_manifest.md`.
