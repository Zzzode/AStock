# Artifact Contract — Low-Position Capital Layout Update

| Artifact | Owner | Stage | Required fields / minimum depth | Blocking conditions | Review / verifier |
|---|---|---|---|---|---|
| `data/raw_market_data_20260811.json` | equity-research / data collector | R0 | Ticker, company, 8月10日收盘、8月11日盘前快照、timestamp、URL、quality、one-year position or gap for all 13 names; raw endpoint captures | Missing ticker, unattributed price, pre-open price labelled as close, name mismatch | R0 / case verifier |
| `data/raw_financials_20260811.json` | equity-research / data collector | R0 | Official FY2025, 2026Q1, and latest H1 filing/preview or explicit gap; dates, revenue, NP, cash-flow field/gap, URLs | Media used as filing, period mix-up, source/date absent | R0 / case verifier |
| `data/broker_street_consensus_20260811.json` | reports / report collector | R0 | Broker/date/rating/target/source quality/path/weight or explicit not-found row per ticker | Weak source gets positive weight, inferred target, missing coverage | R0 / case verifier |
| `data/source_registry_20260811.json` | equity-research / source governance | R0 | Registered source, claim scope, timestamp, quality tier, warnings and boundary | Material source unregistered or quality absent | R0 / case verifier |
| `analysis/valuation_model.md` | valuation / valuation specialist | R1 | Current price, eligibility method, market/Street anchors or explicit absence, cash/earnings boundary, target or event-validation boundary, catalyst and invalidation for four primary candidates | Target without normalized denominator, method mismatch, historic target reused | R1 / case verifier |
| `analysis/valuation_audit.md` | valuation / valuation auditor | R1 | Arithmetic, price/share reconciliation, scenario, source checks, `Model Reproducibility: PASS` | Arithmetic mismatch, fake precision, unsupported action | R1 / case verifier |
| `main.pdf` | equity-research / LaTeX writer | R3 | Chinese conclusion, ranking, valuation, catalysts, invalidation, data-quality note, sources | Build error, clipping, table-only decision chapter, stale data presented as current | R3 / case verifier |
