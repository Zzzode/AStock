# Artifact Contract

| artifact | owner_skill | stage | required_fields | minimum_depth | blocking_conditions | verifier_check |
|---|---|---|---|---|---|---|
| data/source_registry.md/json | equity-research | evidence | source, type, date, quality, use | material claims tied to sources | missing source for H1 forecast or broker target | manual review |
| data/claim_audit.md/json | equity-research | evidence | claim, evidence, quality, adopted wording | high-impact claims classified | unsupported customer/order/margin claim | manual review |
| data/broker_street_consensus_20260709.md/json | reports/valuation | broker gate | broker, date, rating, target, forecasts, method, source quality | post-H1-preannouncement PDFs plus public aggregates | target without source quality | valuation audit |
| analysis/supply_chain_model.md | supply-chain-research | supply chain | chain role, upstream, downstream, economics, gaps | AIDC single-stock map | no customer/order/economics consequence | report grep |
| analysis/growth_earnings_model.md | growth-earnings-model | model | base/growth split, H1 bridge, Q2 implied, scenario | 2026E EPS bridge | no EPS bridge | valuation audit |
| analysis/valuation_model.md | valuation | valuation | current price, shares, market cap, bear/base/bull, target, upside | current-price-based | arithmetic mismatch | valuation audit |
| report.tex/pdf | latex-writer | publish | house view, evidence, valuation, risks, action | reader-usable Chinese note | compile failure or missing action | build-pdf |
