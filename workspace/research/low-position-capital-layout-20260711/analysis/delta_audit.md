# Delta Audit

## User Corrections

The user required a true whole-market refresh, inclusion of both quiet and already-launched opportunities, detailed core-stock research, latest earnings previews, an independent review, and complete repair of every identified data, sector and valuation defect.

## Root Causes

- A 54-name thematic sample was mislabeled as a whole-market universe.
- Official preview EPS and deducted-profit fields were not consistently consumed.
- Street rows mixed sources or gave positive weight to detailed reposts.
- Several bear cases were not genuine downside.
- Hengrui, Jiangbolong and other growth models lacked sufficient revenue-to-EPS sensitivity depth.
- A first-pass priority rule admitted a negative-growth new listing and misclassified a launched media name.
- The raw interface included four B-share securities; BOE A/B duplicated the same issuer result and inflated the electronics total.
- The first repaired report still valued only five formal names while publishing sixteen priority names, seventy-three H1 candidates and a fifty-four-name thematic appendix.
- Section 4.3 presented six 100%+ model-upside tickers as an open "evidence to add" task even though original broker PDFs and API metadata were already partially archived. The report did not distinguish a true missing source from counterevidence or verified non-disclosure.
- The target parser recognized explicit target-price labels but missed source-faithful phrases such as "corresponding per-share value", causing the Jiuaan Medical 70.28 yuan original-PDF fair value to be omitted.
- The model assigned a 5% external weight to any stale target, which conflicted with the source policy that stale evidence is counterevidence only and must carry zero valuation weight.

## Repairs

- Rebuilt the mother universe to 364 eligible A-share companies across all 31 industries and reconciled 73 high-impact candidates.
- Excluded 4 B-share securities and 12 metric rows, leaving 937 eligible A-share metric rows.
- Corrected the priority screen to positive growth plus full-year price history, yielding 16 names.
- Rebuilt preview quality from official EPS and deducted-profit fields.
- Rebuilt five formal valuations with explicit probabilities, zero market-anchor weight and original-PDF Street anchors.
- Added Hengrui segment SOTP, Industrial Fulian H2 bridge and Jiangbolong cycle sensitivity; downgraded ZTE, Jiangbolong and Shaanxi Coal.
- Added sixteen company-specific priority models, seventy-three H1 candidate valuation rows and a 117-name deduplicated report-wide valuation ledger.
- Rewrote the report around the 31/364/73/16/5/3 hierarchy and reduced the old theme work to an appendix.
- Closed rendering overflow with short Chinese labels and safe line breaking.
- Added a 2026-07-15 official-announcement increment: nine validated H1 preview PDFs, deducted-profit bridges, implied-Q2 calculations and explicit disposition changes.
- Preserved the 2026-07-11 full-market baseline instead of silently replacing it with a partial nine-name refresh.
- Built `data/high_upside_evidence_closure_20260716.md/json` for all six Section 4.3 rows. Each row now records original API count, archived original-PDF count, current target-field proof, accepted historical/counterevidence or documented non-disclosure, Q1 operating cash flow, pool status, final admission decision, future-event validation and exact source paths.
- Archived raw Eastmoney `/report/list` responses under `sources/high-upside-evidence-20260716/eastmoney-report-metadata/`, preserving `indvAimPriceL/T` fields that the AkShare adapter drops.
- Reclassified historical original targets, the China State Shipbuilding 50 yuan media repost, third-party aggregation pages and failed probes as zero-weight evidence. No search snippet, media repost or user content is treated as a positive broker/Street anchor.
- Replaced Section 4.3 and the high-upside appendix from open evidence tasks to completed audit conclusions: six of six gaps are closed, zero current positive-weight original targets were found, and zero tickers were upgraded to the formal pool.
- Corrected stale-target valuation weighting to zero and rebuilt all 142 candidate models and row-level valuation audits.

## Prevention Rules

1. Whole-market claims require a reproducible mother universe before thematic selection.
2. Direct official preview EPS and deducted profit override share-count inference.
3. Only source-pure original PDFs receive positive Street target weight.
4. Every formal bear case must be below current price and every target must use disclosed probabilities.
5. High-growth credit requires revenue/proxy, margin, profit, EPS, sensitivity and current-price implication.
6. Negative-growth or insufficient-history names cannot enter a low-position earnings priority pool.
7. A-share scope must explicitly exclude B-share security codes and prevent A/B duplicate issuer counting.
8. Every reported ticker must have a linked valuation range or an explicit not-priceable reason; a watchlist label alone is insufficient.
9. Incremental official previews must be archived with code/company/title/amount validation and must not automatically create a target-price upgrade.
10. A partial post-cutoff notice scan must be labeled incremental; it cannot be presented as a full-universe refreshed screen.
11. A reader-facing evidence gap must close in one of three auditable states: direct evidence found, counterevidence found, or source exhaustion / verified non-disclosure. Do not leave a generic "add target price" placeholder after the source corpus has been checked.
12. Original API metadata must be preserved when an adapter drops material fields such as target-price bounds.
13. Historical broker targets, media reposts, third-party aggregations, search snippets and user-generated estimates always receive zero valuation weight.
14. Future H2 earnings, cash flow, orders, prices or pool re-entry are event-validation conditions, not completed evidence.
