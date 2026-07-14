# Artifact Contract

| Artifact | Required fields | Minimum depth | Blocking condition | Reviewer | Verifier |
|---|---|---|---|---|---|
| research_brief.md | scope, cutoff, exclusions, downgrade | explicit data boundary | missing or unsupported data | R0-R4 | case verifier |
| data/verified_financials.md | reported/guided financials and mix | official paths and units | missing or unsupported data | R0-R4 | case verifier |
| analysis/growth_earnings_model.md | driver bridge, scenarios and credit | no unsupported growth multiple | missing or unsupported data | R0-R4 | case verifier |
| analysis/valuation_model.md | price, shares, scenarios, target and action | reproducible formulas | missing or unsupported data | R0-R4 | case verifier |
| analysis/secondary_market_analysis.md | institution, LHB, financing, score | layered identity limits | missing or unsupported data | R0-R4 | case verifier |
| final_signoff.json | score, gates, residual risks | maker-checker closure | missing or unsupported data | R0-R4 | case verifier |
