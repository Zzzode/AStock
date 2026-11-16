# Source Registry

The registry contains primary regulatory, exchange, fund/REIT annual, Q2, prospectus/product-summary and market-snapshot evidence archived locally under `sources/`. Every row in `source_registry.json` has a document date (or explicitly states that the archived source does not state one), reporting-period field, retrieval date, relative path, SHA-256 and archive status. Annual reports are treated as audited annual-report evidence; every 2026 Q2 report is explicitly treated as **unaudited**. Market snapshots are primary exchange observations but are execution-incomplete.

| ID | Evidence family | Product / use | Quality | Reader limitation |
|---|---|---|---|---|
| S01–S03 | CSRC / State Council / Ministry of Finance policy material | REIT distribution and protected-liquidity category boundaries | Tier 1 primary | No exact protected-liquidity instrument is identified |
| S04–S06 | 511010 annual, Q2, legal docs | Treasury ETF | Tier 1 primary; Q2 unaudited | No current duration, IOPV or execution clearance |
| S07–S09 | 510880 annual, Q2, index methodology | Dividend ETF | Tier 1 primary; Q2 unaudited | Historical distribution/holdings are not forward cash/current holdings |
| S10–S11 | 512890 annual and Q2 | Dividend-low-vol ETF | Tier 1 primary; Q2 unaudited | Factor label does not prove cash or diversification |
| S12–S13 | 508069 annual and Q2 | Traffic REIT | Tier 1 primary; Q2 unaudited | Cash figures cannot be simply annualized |
| S14–S15 | 508011 annual and Q2 | Consumer REIT | Tier 1 primary; Q2 unaudited | Dated NAV is not a current value |
| S16–S17 | 508068 annual and Q2 | Beijing rental-housing REIT | Tier 1 primary; Q2 unaudited | Expanded asset base requires current valuation work |
| S18–S19 | 508077 annual and Q2 | Rental-housing REIT | Tier 1 primary; Q2 unaudited | Expansion / rental cluster risk remains |
| S20–S21 | 508055 annual and Q2 | Shanghai rental-housing REIT | Tier 1 primary; Q2 unaudited | Short reporting history and cash variability remain |
| S22–S23 | 508080 annual and Q2 | Industrial-park REIT | Tier 1 primary; Q2 unaudited | Partial history and tenant/lease evidence need further clearance |
| S24–S26 | 508096 annual, Q2, name change | Diversified energy REIT | Tier 1 primary; Q2 unaudited | Current scope is not PV-only; cash has factoring/estimate caveats |
| S27 | Same-session SSE snapshots | All 10 products | Tier 1, execution incomplete | No spread/depth/IOPV/capacity/tax/account fields; resolved to 10 atomic files |
| S28 | 10 prospectus/PDS archive | Product legal terms | Tier 1 primary | Does not supply a live valuation or implementation approval; resolved to 20 atomic files |

Detailed URLs, local paths, intended claim use, document date, reporting period, SHA-256 and limitations are in [source_registry.json](source_registry.json). The file-level resolution of S27/S28 is in [legal_document_manifest_20260812.json](legal_document_manifest_20260812.json).
