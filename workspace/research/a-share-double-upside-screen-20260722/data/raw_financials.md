# Raw Financial Data — Deep-Model Pool

## Scope and source hierarchy

- Coverage: `600150`, `301308`, `002812`, `002240`, `300390`, and cycle-added deep-model candidate `002497`.
- Financial cutoff: FY2025 audited annual reports, unaudited 2026Q1 reports, and official unaudited 2026H1 earnings previews available by `2026-07-22`.
- Primary evidence: issuer filings archived from CNINFO in `sources/official-20260722/`; the same-name `.txt` files are `pdftotext -layout` derivatives for search only.
- Structured cross-check: `.venv/bin/python -m astock.cli financials <ticker> --periods 6 --json`, captured `2026-07-22 16:20-16:27 CST`. It matched the official FY2025 and 2026Q1 figures below.
- The H1 rows are company preliminary estimates. They are **not audited results**, are not mechanically annualized, and are not treated as FY2026 forecasts.

## FY2025 reported financials

Currency is CNY. Values are full-year reported amounts, not TTM.

| Ticker | Company | Revenue | Parent NP | Deducted parent NP | OCF | Source status |
|---|---|---:|---:|---:|---:|---|
| 600150 | 中国船舶 | CNY151.978bn | CNY7.848bn | CNY6.126bn | CNY7.767bn | Audited annual report; same-control merger-combined presentation |
| 301308 | 江波龙 | CNY22.766bn | CNY1.423bn | CNY1.289bn | -CNY1.201bn | Audited annual report |
| 002812 | 恩捷股份 | CNY13.633bn | CNY0.143bn | CNY0.111bn | CNY1.144bn | Audited annual report |
| 002240 | 盛新锂能 | CNY5.064bn | -CNY0.888bn | -CNY0.812bn | CNY0.950bn | Audited annual report |
| 300390 | 天华新能 | CNY7.549bn | CNY0.402bn | CNY0.150bn | -CNY0.322bn | Corrected audited annual report; same-control comparison adjusted |
| 002497 | 雅化集团 | CNY8.543bn | CNY0.632bn | CNY0.694bn | -CNY0.570bn | Audited annual report |

Exact filing values:

| Ticker | Revenue (CNY) | Parent NP (CNY) | Deducted NP (CNY) | OCF (CNY) |
|---|---:|---:|---:|---:|
| 600150 | 151,977,991,216.09 | 7,848,378,198.33 | 6,126,096,600.00 | 7,766,831,729.43 |
| 301308 | 22,766,169,990.55 | 1,423,298,162.88 | 1,289,178,618.90 | -1,201,201,037.10 |
| 002812 | 13,632,727,136.01 | 142,548,339.91 | 110,802,429.81 | 1,143,637,807.97 |
| 002240 | 5,064,315,775.69 | -888,079,510.10 | -812,336,830.65 | 949,962,734.60 |
| 300390 | 7,548,826,104.54 | 402,189,233.13 | 150,340,015.73 | -321,825,657.49 |
| 002497 | 8,543,171,263.90 | 632,380,161.87 | 693,585,735.36 | -569,778,007.60 |

## 2026Q1 reported financials

Currency is CNY. All six quarterly reports state that their first-quarter financial information was unaudited.

| Ticker | Revenue | YoY | Parent NP | YoY | Deducted parent NP | YoY | OCF | OCF / revenue |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 600150 | CNY43.312bn | +54.90% | CNY4.832bn | +251.64% | CNY4.767bn | +326.69% | CNY8.152bn | +18.82% |
| 301308 | CNY9.909bn | +132.79% | CNY3.862bn | +2,644.05% | CNY3.943bn | +2,051.40% | -CNY2.875bn | -29.01% |
| 002812 | CNY3.908bn | +43.21% | CNY0.260bn | +901.70% | CNY0.261bn | +793.83% | CNY0.207bn | +5.29% |
| 002240 | CNY3.284bn | +378.58% | CNY0.464bn | +399.89% | CNY0.622bn | +409.93% | -CNY0.667bn | -20.32% |
| 300390 | CNY3.200bn | +89.62% | CNY0.969bn | +1,471.98% adjusted | CNY0.946bn | +3,554.97% | -CNY0.183bn | -5.73% |
| 002497 | CNY2.830bn | +84.16% | CNY0.339bn | +310.87% | CNY0.357bn | +419.73% | -CNY0.431bn | -15.21% |

Exact filing values:

| Ticker | Revenue (CNY) | Parent NP (CNY) | Deducted NP (CNY) | OCF (CNY) |
|---|---:|---:|---:|---:|
| 600150 | 43,312,405,150.04 | 4,832,277,995.78 | 4,767,343,200.00 | 8,151,528,825.13 |
| 301308 | 9,908,726,244.41 | 3,862,236,561.17 | 3,942,639,469.07 | -2,874,539,454.35 |
| 002812 | 3,907,690,531.54 | 260,308,751.63 | 260,959,203.60 | 206,660,110.96 |
| 002240 | 3,284,048,555.59 | 464,035,684.07 | 622,318,509.18 | -667,158,854.50 |
| 300390 | 3,200,150,765.28 | 968,906,491.73 | 945,718,935.46 | -183,248,547.52 |
| 002497 | 2,830,218,496.20 | 338,821,317.99 | 356,555,349.32 | -430,615,777.34 |

## Official 2026H1 earnings previews

| Ticker | Parent NP range | Deducted NP range | Revenue range | Comparison / status | Company-stated driver |
|---|---:|---:|---:|---|---|
| 600150 | CNY9.20-11.00bn | CNY9.00-10.80bn | N/A (not disclosed) | Parent NP +143.56%-191.21% versus merger-restated 2025H1; +212.29%-273.39% versus standalone historical presentation; unaudited | Full order book, more civil vessels delivered, greater mid/high-end mix, higher average price per ship, cost control |
| 301308 | CNY9.20-11.00bn | CNY9.00-10.50bn | CNY22.00-25.00bn | Parent NP +62,204.03%-74,393.95%; unaudited | Storage upcycle, constrained global wafer-capacity growth, renewed supplier LTA/MOU, own-controller/software/package capabilities |
| 002812 | CNY0.736-0.900bn | CNY0.762-0.930bn | N/A (not disclosed) | Turnaround from 2025H1 loss; unaudited | Separator demand and volume growth, full-process cost control, product prices stabilizing/recovering from prior-year low |
| 002240 | CNY1.00-1.20bn | CNY1.30-1.50bn | N/A (not disclosed) | Turnaround from 2025H1 loss; unaudited | Lithium-salt price increase, production efficiency/cost control, Indonesian plant volume ramp, volume and price growth |
| 300390 | CNY2.20-2.40bn | CNY2.1617-2.3617bn | N/A (not disclosed) | Turnaround from restated 2025H1 loss; unaudited | Storage and EV-battery demand, lithium-material volume and price growth; estimated non-recurring gain about CNY38.3m |
| 002497 | CNY1.10-1.30bn | CNY1.125-1.315bn | N/A (not disclosed) | Parent NP +710.17%-857.48%; unaudited | Rising lithium-salt prices, higher volume and ASP, mine/production/sales balancing and cost control; company also disclosed 2026Q2 parent NP CNY0.761-0.961bn |

## Key operating disclosures

| Ticker | Period | Reported operating evidence | What it does not prove |
|---|---|---|---|
| 600150 | FY2025 | New civil/offshore orders: 237 vessels, 30.5067m dwt, CNY175.836bn; deliveries: 161 vessels, 13.6775m dwt; year-end civil/offshore backlog: 652 vessels, 79.9730m dwt, CNY467.451bn | Does not disclose 2026H1 backlog value, delivery margin by vessel, or customer-level timing |
| 301308 | FY2025 / 2026H1 preview | Enterprise storage revenue CNY1.783bn (+93.30%); Zilia revenue CNY2.924bn (+26.49%); Lexar revenue CNY4.741bn (+34.53%). H1 preview says multiple major wafer suppliers renewed LTA/MOU | No H1 product-level volume, wafer procurement price, ASP, gross margin, or binding minimum-take terms disclosed |
| 002812 | FY2025 | Separator revenue CNY11.630bn; sales 12.840bn m2; production 11.824bn m2; weighted design capacity 14.4bn m2 and utilization 94.91% | H1 preview gives no volume, ASP, utilization, customer mix, or product-mix bridge |
| 002240 | FY2025 / 2026H1 preview | Built lithium-salt capacity: 137kt/year; disclosed capacity table includes 75kt carbonate and 65kt hydroxide, with flexible lines. H1 preview says Indonesian capacity released materially | No H1 tonnage, realized ASP, unit cash cost, or plant-level margin disclosed |
| 300390 | FY2025 / 2026H1 preview | Lithium-material sales value CNY6.667bn (+15.87%) and inventory value down 55.62%; H1 preview says lithium-material volume and price both increased | Annual sales table is value-based, not physical tonnage; no H1 tonnage, ASP, or unit-cost disclosure |
| 002497 | FY2025 / 2026H1 preview | Existing lithium-salt design capacity about 130kt/year; Kamativi mine at 2.30m t/year ore-processing scale and 350kt/year concentrate; Lijiagou designed for 1.05m t/year ore and 180-200kt/year concentrate, entering formal production in Sep-2025. H1 preview says lithium-salt volume and ASP both increased | No H1 tonnage, realized ASP, self-supply ratio, mine cost, or customer mix disclosed |

## Evidence boundary

- FY2025 annual-report figures are reported audited history. 2026Q1 figures and all H1 preview ranges are unaudited.
- No H1 midpoint is labeled “actual,” no H1 range is doubled to create a full-year estimate, and no Q1 growth rate is extrapolated through FY2026.
- Parent NP exceeding or falling below deducted NP is preserved as disclosed. In particular, `301308`, `002240`, and `002497` had deducted NP above parent NP in 2026Q1 because net non-recurring items were negative; this is not a transcription error.
- `600150` and `300390` have same-control combination effects. Comparable growth must use the restated bases disclosed by the issuer.
- Company-stated drivers are evidence of management's explanation, not independent proof that the improvement will persist through year-end.
