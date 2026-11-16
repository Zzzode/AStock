# Research brief — Global private equity methods translated for a China retail public-market investor

## Decision question

Which recurring investment disciplines used by leading global private-equity and alternative-asset managers can a mainland China retail investor use legally and realistically in public markets, and which apparent "strategies" should be excluded because they depend on control, leverage, proprietary access, or institutional infrastructure?

## Frozen scope

- **Data cutoff:** 2026-08-13.
- **Institutional reference set:** Blackstone, KKR, Apollo, Brookfield, Carlyle, Bain Capital and TPG; the work reads their current official filing, annual-information-form, shareholder-letter or official review material as descriptions of business model and process—not as independently verified performance attribution.
- **China translation:** mainland listed equities, exchange-traded funds and publicly offered real-estate REITs only as research categories. Infrastructure and commercial-real-estate contexts remain product-specific; no named security, product, live account, investor profile or execution instruction is in scope.
- **Deliverable:** an evidence memo and a reusable investment-committee-style underwriting checklist. It is not a portfolio allocation, a product suitability opinion, a return forecast, or an order instruction.

## Boundaries that cannot be relaxed

1. The active model has no named direct stock, ETF or REIT, and no live execution authority.
2. The framework assumes zero borrowing, zero financing add-on and zero naked short exposure.
3. A future named direct equity requires an issuer-specific public-information dossier, scenario valuation, liquidity test and independent red-team review; a future public REIT requires its own project-level dossier.
4. Institutional marketing statements may describe a manager's process, but cannot prove that a retail investor can reproduce its historical return.
5. A purchase cannot be assumed to have an immediate exit: ordinary secondary-market disposal is designed around the rule that purchased securities may not be sold before settlement unless a specified reverse-trading exception applies, plus liquidity constraints, rather than an intraday stop-loss assumption.

## Research standard

Primary materials are locally archived official issuer or regulator/exchange documents. Each material conclusion is mapped in `data/claim_audit.json`. Manager-process claims are Tier A for *what the manager says it does*, but only Tier B for claims about the causal source or repeatability of outperformance. China rule claims use current official exchange/regulator documents where available. The local AStock capability runtime could not be invoked because its environment lacks declared Python dependencies; this is recorded as a tooling degradation, not silently substituted for live data.

## Questions the report must answer

1. What is the common economic engine across the reference managers?
2. Which elements are high-, partial-, or non-transferable to a personal China account?
3. What is the highest-quality personal analogue: selection, underwriting, sizing, monitoring and failure discipline?
4. How should settlement-before-sale restrictions, product-specific reverse-trading exceptions, price-limit heterogeneity, liquidity, financing restrictions and public-REIT rules change that analogue?
5. What evidence is still required before this framework could become a personalised allocation or a named-security opinion?
