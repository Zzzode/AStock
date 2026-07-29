# Skill Evolution Log

## 2026-07-22 — Secondary-market data omission

- Failure mode: a single-stock full report passed with market-structure prose that did not contain a continuous adjustment-labelled K-line series, free-float/turnover basis, margin-trading data, Stock Connect holdings, fund ownership or Dragon-Tiger List evidence.
- Root cause: `SINGLE_STOCK_INSTITUTIONAL_DEPTH_TERMS` in the quality gate checked only generic keywords; R2/R4 did not require source-backed field coverage.
- Affected skill/roles: `equity-research`, data collector, data verifier, market analyst, research-report reviewer.
- Corrective report action: reopened through a delta audit; collected 727-day labelled front-adjusted K-line, turnover/circulating-share, daily margin, quarterly Shanghai Connect/fund and Dragon-Tiger packets; connected them to the reader-facing chapter. PDF rebuild and independent R2-R4 remain mandatory.
- Proposed reusable prevention rule: require dated, sourced field coverage for all seven market-positioning categories or an archived negative-query record and explicit downgrade consequence.
- Prompt/skill changes: none in this turn pending explicit user authorization.
- Regression evidence: will be added only if reusable prompt/quality-gate changes are authorized.
