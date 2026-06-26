# Professional Standards Checklist

## Report Formatting

- [ ] Cover page has: title (bilingual), date, data cutoff, version number
- [ ] Table of contents auto-generated and correct (2 XeLaTeX passes)
- [ ] Page headers: report title (left), date (right)
- [ ] Page footers: page number (center), disclaimer (right)
- [ ] Disclaimer page at end with both Chinese and English text

## Number Formatting

- [ ] All monetary values have units (亿元, 万元, $B, $M)
- [ ] PE/PS/PB multiples written as `XX×` (not "XXx" or "XX倍" inconsistently)
- [ ] Percentages always with % sign: +42.96% (not "增长42.96")
- [ ] Value ranges use consistent delimiter: `+107--142%` (en-dash throughout)
- [ ] Large numbers use Chinese units: 1.4万亿 (not 14000亿)
- [ ] Decimals consistent: financial data 2 decimals, growth rates 1-2 decimals

## Valuation Model Standards

- [ ] Every investable or explicitly covered ticker has current price/date, share count, market cap, currency/share class, forecast EPS/net profit, valuation method, bull/base/bear values, final target price or fair-value range, implied upside/downside, rating/action, catalysts, invalidation, and evidence quality
- [ ] The reader-facing report includes a final valuation summary table covering the full investable universe
- [ ] Broker target prices are separated from AStock final targets and clearly cited by broker/date/source
- [ ] Upside/downside is calculated from current price: `(target or range midpoint / current price - 1) × 100%`
- [ ] Any ticker without enough data for a defensible target is labeled `insufficient evidence / watchlist only` and is not given an investable recommendation

## Table Standards

- [ ] All tables use booktabs (no vertical lines, \toprule/\midrule/\bottomrule)
- [ ] Every table has numbered caption below
- [ ] Column headers are bold
- [ ] Risk colors used consistently (red=severe, amber=warning, green=positive)
- [ ] Comprehensive tables include ALL tickers in coverage universe (no omissions)
- [ ] Tables that score/rank include a methodology note

## Chart Standards

- [ ] Every chart has numbered caption below
- [ ] Axis labels are readable (not too small)
- [ ] Legend is present and unambiguous
- [ ] Source attribution below chart (tiny font, grey)
- [ ] Radar charts have accompanying "decision table" explaining implications
- [ ] Scatter plots have all points listed in a legend/reference table
- [ ] No overlapping labels (adjust anchor positions)

## Reference System

- [ ] Every factual claim has source citation [Ax] or footnote
- [ ] [Ax] references map to Appendix A entries
- [ ] ESG claims reference [ESG-Ex] codes
- [ ] Appendix A covers all referenced numbers (no orphan references)

## Compliance/Risk Disclosures

- [ ] BIS entity list: full details (date, entities affected, business impact %)
- [ ] CSRC penalties: amount, reason, date, current status
- [ ] Shareholder pledges: exact %, whether at margin call level
- [ ] Official clarifications (澄清公告): quoted with date
- [ ] ST/delisting history: dates and current status
- [ ] Criminal/regulatory: custody (留置), investigation dates

## Language & Tone

- [ ] Analytical, not promotional (no "exciting opportunity" language)
- [ ] Risks stated directly, not buried in footnotes
- [ ] "Bubble" and "overvalued" used without hedging when data supports it
- [ ] Conclusions are actionable (specific: "buy below X", "sell above Y")
- [ ] No unexplained jargon without glossary reference
