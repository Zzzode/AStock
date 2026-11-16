# Research Brief — Income Strategy Product Due Diligence

**Case ID:** `income-strategy-product-due-diligence-20260812`  
**Scope ID:** `income-strategy-product-diligence-v1-20260812`  
**Data cutoff:** 2026-08-12 for the exchange snapshot; 2026-06-30 for the latest routine semiannual reports unless an explicitly dated later announcement is cited.  
**Language / form:** Chinese institutional research memorandum, LaTeX and XeLaTeX PDF.  
**Coverage depth:** Cross-asset master due-diligence report with ten named-product notes, project look-through for every public REIT, and a portfolio-level overlap and implementation gate.

## Mandate and reader decision

The legacy framework seeks at least 5% annual total return and at least 3% cash available for reinvestment. Those are investor objectives, not promised outcomes, product features, or a basis for selecting a security. This case tests whether every product or category named in that framework has enough product-level evidence to enter a later allocation decision. It does **not** authorize a trade, set a target price, or assert that the objectives can be met.

The current implementation decision is unchanged: every market-traded product has `q=0`; the only current state is CNY200,000 in an as-yet product-unspecified eligible protected-liquidity fallback. The fallback category itself is not an investable instrument until the exact issuer/product/account terms are frozen and reviewed.

## Product universe

The frozen research universe has ten named products and two unnamed categories:

| Group | Coverage | Legacy reference role | Research disposition at intake |
|---|---|---|---|
| Treasury ETF | 511010 国泰上证5年期国债ETF | 15% conditional reference weight | Active research; rate-risk sleeve, not protected liquidity |
| Dividend equity ETFs | 510880 上证红利ETF; 512890 中证红利低波ETF | 40% anchor and secondary alternative | Active/conditional research; equity and factor exposure must be made explicit |
| Public REITs | 508069, 508011, 508068, 508077, 508055, 508080, 508096 | 25% aggregate conditional sleeve; 5% per-project cap | Active research; no individual selection or active weight |
| Protected liquidity | Unnamed bank-deposit/direct-sovereign category | 100% current fallback; 10% conditional reserve | Not researchable until a finite product list is supplied |
| Defensive diversifier | Unnamed category | 10% conditional reference weight | Not researchable until a finite product list and role definition are supplied |

Direct equities, leverage, derivatives, margin financing, lower-credit yield substitution and forced reinvestment are excluded. The current 508096 identity is **中航京能国际能源REIT**, following the 2026-02-13 name change after hydro assets were added; an obsolete photovoltaic-only label cannot be used for current due diligence.

## Custom coverage pack

This is a custom `income_etf_public_reit_liquidity_products_v1` pack, because the universe is a product portfolio rather than a corporate industry chain. Each named instrument needs all of the following before it could pass product-level research:

1. Legal identity, manager/custodian/sponsor, mandate and benchmark or asset rights.
2. Dated financial, NAV and cash-distribution facts; a clear distinction between audited annual data and unaudited semiannual data.
3. Look-through exposure: index constituents for ETFs, and projects, geography, operators and operating drivers for REITs.
4. Product-appropriate valuation: market price versus a dated NAV only where comparable, with date mismatch explicitly disclosed; no false same-day premium, target price or yield forecast.
5. Current market-data, trading-capacity, tax, settlement and account-eligibility fields. A one-day exchange snapshot is not a full liquidity clearance.
6. Concentration, common-factor and downside-scenario analysis, including overlap among dividend ETFs and rental-housing REITs.
7. A broker/Street evidence audit. Weak, abstract-only or unavailable broker material has zero valuation weight.

## Evidence standard and downgrade path

Primary fund/REIT disclosures, exchange market snapshots and official regulatory material are the decision evidence hierarchy. Product pages, media and broker reposts are contextual only. The Q2 reports are labelled unaudited. Dated annual NAVs and periodic cash-distribution ratios are historical observations, not current fair value, TTM cash coverage, forward yield or portfolio-return evidence.

The intended deliverable is therefore an `EVIDENCE_MEMO / WATCHLIST_ONLY` product research report. A product with missing same-session NAV/IOPV, bid-ask/depth, 20-session capacity, account/tax evidence, full broker anchor or risk approval remains `NOT_APPROVED`, even if its disclosure-based product card is complete. The overall strategy cannot be activated by substituting a high-yield asset for an unresolved evidence gap.

## House questions

1. What economic exposure, not label, does each product deliver?
2. Which cash-flow facts are observed, and which are merely manager annualizations or historical distributions?
3. Which products have overlapping rate, equity-style, rental-housing, sponsor, traffic, energy or local-property risks?
4. Can any product currently support a selection, valuation or reinvestment claim? If not, what exact evidence is missing?
5. What must be true for the legacy strategy to move from research framework to implementation review?

## Required outputs and review route

The case produces an R0 primary-source archive and claim ledger; R1 product valuation and overlap model; R2 reader-facing 10-product note; R3 XeLaTeX render/format review; and R4 investment-committee sign-off. The maker-checker split is maintained through documented repair plans. A passed research-framework gate means only that the evidence memo is accurately scoped and reproducible; it does not approve an allocation.
