# Claim Audit

| ID | Claim status | Source IDs | Disallowed leap |
|---|---|---|---|
| C01 | Supported with boundary | E01--E05 | Product structure/fee → return, liquidity or allocation |
| C02 | Supported with boundary | E06--E07 | Generic trading mechanics → a current fill |
| C03 | Non-admissible exploratory diagnostic | P01 | Unresolved-basis daily-bar output → total-return approval |
| C04 | Supported with boundary | F05--F06 | Retrospective actual daily rows → complete historical execution replay |
| C05 | Supported with boundary | F01--F04 | Rules → user eligibility or live permission |
| C06 | Supported with boundary | D01 | Data documentation → subscription or data rights |
| C07 | Supported by gaps | C01--C06, C09--C21 | Missing evidence → a market forecast |
| C08 | Supported with boundary | M01 | Government yield curve → tradable investor return or 5% forecast |
| C09 | Non-admissible exploratory diagnostic | P02 | Public-close screening result → total-return conclusion, product ranking, allocation or action |
| C10 | Non-admissible exploratory diagnostic | P03 | Official public-close screening result → total-return conclusion, formal replay or action |
| C11 | Supported with boundary | P04 | Endpoint source access → entitlement, PIT data, personal access or action |
| C12 | Supported with boundary | P05 | Selected H1/H3 endpoint fields → complete PIT replay input, total return, execution or action |
| C13 | Supported with boundary | P06 | Route/terms page → data entitlement, coverage/PIT proof, formal replay or action |
| C14 | Supported with boundary | E11 | Dated rules and six retrospective actual-contract samples → a strict 5% return result, personal feasibility or action |
| C15 | Non-admissible exploratory diagnostic | E12 | Four-name gross-cash result → a conclusion about the direct-equity universe, total return, allocation or action |
| C16 | Supported with boundary | E13 | Manager-published accumulated NAV proxy → holder dealing result, future return, allocation or action |
| C17 | Supported with boundary | E14 | Cash/futures rules and samples → matched cash-and-carry result, delivery feasibility, personal operability or action |
| C18 | Supported with boundary | E15 | Option mechanics disclosures → complete actual-contract test, user eligibility, return result, allocation or action |
| C19 | Non-admissible exploratory diagnostic | E16 | Fixed ETF market-price failure → total return, cross-universe failure, allocation or action |
| C20 | Non-admissible exploratory diagnostic | E17 | Fixed convertible-bond ETF price-proxy failure → investor net return, product ranking, allocation or action |
| C21 | Non-admissible exploratory diagnostic | E18 | One REIT's zero-cost cash diagnostic → personal net result, public-REIT-universe conclusion, allocation or action |

The machine-readable source of truth is `claim_audit.json`.
