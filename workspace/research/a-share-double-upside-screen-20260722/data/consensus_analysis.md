# Broker Consensus Analysis — 2026-07-22

## Bottom line

Two names have complete, auditable Street point-target evidence in the public original-PDF set. Only 002497 has positive house anchor weight; 002812 is zero weight because company-level driver evidence blocks formal valuation:

| Ticker | Target | 2026-07-22 price | Implied upside | Valuation basis | Target horizon | Year-end applicability |
|---|---:|---:|---:|---|---|---|
| 002497 雅化集团 | CNY42 | CNY16.79 | +150.15% | 2026E EPS CNY2.63 × 16x PE | Not disclosed | Not established; do not call it a 2026 year-end target |
| 002812 恩捷股份 | CNY103 | CNY47.84 | +115.30% | 2027E EPS CNY5.16 × 20x PE | Not disclosed | Not established; do not call it a 2026 year-end target |

The targets mechanically clear the report screen's +100% threshold versus the captured prices, but neither report defines a 2026-12-31 horizon. They are Street upside anchors, not proof of a year-end base-case double.

## Auditable point-target reading

### 002497 雅化集团 — CNY42 target

- Original report date: 2026-07-07; public aggregation publish date: 2026-07-08.
- Forecasts: 2026E revenue CNY17.052bn, attributable net profit CNY3.032bn, EPS CNY2.63; 2027E revenue CNY22.215bn, attributable net profit CNY3.575bn, EPS CNY3.10.
- Explicit method: “给予26年16x估值，对应目标价42元.” The mechanical value is CNY2.63 × 16 = CNY42.08, rounded to CNY42.
- Operating assumptions stated in the report: about 120,000 tonnes of 2026 lithium-salt shipments, 25% equity resource self-sufficiency, and fading hedging losses in 2026H2.
- Main risks: weaker lithium prices, lower lithium-salt shipments, and slower resource development.
- Horizon conclusion: `target_horizon = not disclosed`. A 2026E earnings basis is not the same as a 2026 year-end target date.

### 002812 恩捷股份 — CNY103 target

- Original and publish date: 2026-07-10.
- Forecasts: 2026E revenue CNY20.058bn, attributable net profit CNY2.279bn, EPS CNY2.32; 2027E revenue CNY31.115bn, attributable net profit CNY5.068bn, EPS CNY5.16.
- Explicit method: “给予27年20x估值，对应目标价103元.” The mechanical value is CNY5.16 × 20 = CNY103.20, rounded to CNY103.
- Thesis: separator supply-demand tightness, price recovery, and shipment growth drive the 2027E earnings step-up.
- Main risks: downstream demand, excessive industry expansion, and price volatility.
- Horizon conclusion: `target_horizon = not disclosed`. A 2027E earnings basis is not a stated 2026 year-end target.

## Zero-weight coverage gaps

These rows remain outside `broker_street_consensus_20260722.json` because no explicit target price was found. Their original PDFs remain useful as earnings-estimate context, but they carry zero weight in the formal target/upside packet.

| Ticker | Archived original PDFs | Latest public report | Earnings anchors | Missing field / exhaustion reason | Target weight | Next verification path |
|---|---:|---|---|---|---:|---|
| 600150 中国船舶 | 5 | 2026-07-14 华源证券 | Five complete 2026E/2027E forecast tables; simple-mean 2026E/2027E NP CNY17.902bn/CNY23.856bn | Five PDFs and live public metadata disclose no explicit target price; current-price PE cannot be reversed into one | 0 | Licensed Wind/Choice/iFinD target-price table or broker client export |
| 301308 江波龙 | 2 | 2026-05-07 国信证券 / 爱建证券 | 2026E NP range CNY11.097bn-CNY19.969bn; 2027E CNY11.311bn-CNY21.908bn | No report after 2026-05-07, no explicit target, and a large forecast divergence; public average-target aggregations are excluded | 0 | Post-2026H1 original report or licensed broker-terminal export |
| 002240 盛新锂能 | 4 | 2026-07-09 东吴证券 | 2026E NP range CNY1.585bn-CNY2.243bn; 2027E CNY2.141bn-CNY3.050bn | Four PDFs disclose current-price PE but no explicit target price | 0 | Licensed Wind/Choice/iFinD target-price table or broker client export |
| 300390 天华新能 | 1 | 2026-06-06 华源证券 | 2026E/2027E NP CNY4.733bn/CNY5.315bn; EPS CNY5.70/CNY6.40 | Only one report was found since 2025; it is older than 30 days and gives peer/current PE without an explicit target | 0 | Post-2026H1 original report or licensed broker-terminal export |

## Earnings forecast comparison

Simple means below describe the archived PDF set; they are not a licensed all-Street consensus and are not used as target prices.

| Ticker | Reports | 2026E revenue mean / range | 2026E NP mean / range | 2027E revenue mean / range | 2027E NP mean / range | Key interpretation |
|---|---:|---:|---:|---:|---:|---|
| 600150 | 5 | CNY181.131bn / CNY173.501bn-CNY192.407bn | CNY17.902bn / CNY16.550bn-CNY20.036bn | CNY207.972bn / CNY197.304bn-CNY224.537bn | CNY23.856bn / CNY22.728bn-CNY25.712bn | Broad agreement on high-priced order delivery and margin expansion; target absent |
| 301308 | 2 | CNY40.247bn / CNY40.039bn-CNY40.455bn | CNY15.533bn / CNY11.097bn-CNY19.969bn | CNY48.984bn / CNY48.461bn-CNY49.507bn | CNY16.610bn / CNY11.311bn-CNY21.908bn | Revenue agrees, profit does not; cycle-margin assumptions dominate |
| 002240 | 4 | CNY15.475bn / CNY14.851bn-CNY17.000bn | CNY2.011bn / CNY1.585bn-CNY2.243bn | CNY16.742bn / CNY15.642bn-CNY18.700bn | CNY2.680bn / CNY2.141bn-CNY3.050bn | Lithium price, owned resources, and capacity ramp explain most dispersion |
| 300390 | 1 | CNY21.621bn | CNY4.733bn | CNY24.898bn | CNY5.315bn | Single-report evidence; no cross-broker consensus |
| 002497 | 1 | CNY17.052bn | CNY3.032bn | CNY22.215bn | CNY3.575bn | Complete positive-weight target row; 2026E valuation basis |
| 002812 | 1 | CNY20.058bn | CNY2.279bn | CNY31.115bn | CNY5.068bn | Complete point-target evidence; zero house valuation weight; 2027E basis |

## Consensus and divergence

- All 14 archived original reports carry bullish ratings; there are no neutral or bearish original reports in this selected set. This is collection bias, not a market-wide rating distribution.
- The cleanest point-target evidence is the two current Eastmoney-hosted original PDFs, not abstracts or search snippets; only 002497 passes the separate valuation-eligibility gate.
- `002497` and `002812` use different forecast years for target construction. The nominal target multiples and upside percentages are therefore not directly comparable.
- `301308` has the largest model risk: the two reports' 2026E profit forecasts differ by CNY8.872bn despite very similar revenue forecasts.
- Lithium-chain reports share a bullish price/recovery premise. A weaker lithium-price path simultaneously undermines shipment economics, profit forecasts, and the target multiples.
- No abstract, repost, third-party preview, or search snippet receives valuation weight.

## Publication boundary

The formal Street packet can support a statement that two public original reports imply more than 100% upside from the captured 2026-07-22 prices. It cannot support a statement that Street expects either stock to double by 2026-12-31, because the target horizons are not disclosed. Any year-end conversion must be an explicit AStock scenario assumption, separately labeled and audited.
