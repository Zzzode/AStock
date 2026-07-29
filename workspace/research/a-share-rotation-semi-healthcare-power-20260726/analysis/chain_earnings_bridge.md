# Chain Earnings Bridge

**Gate:** `CONDITIONAL`. No earnings forecasts are created. The bridge specifies what must be observed before a theme can become company revenue, margin, EPS and valuation credit.

## Theme-level profit-pool bridge

| Theme | Realized-driver sequence | Optionality / sentiment that remains outside EPS | Current evidence result |
|---|---|---|---|
| Semiconductor | product/process qualification → order → shipment/acceptance → recognized revenue → mix/price/cost → gross margin → operating profit/cash | AI demand, global equipment cycle, localization and sector attention | No test-company conversion record; zero earnings credit. |
| Innovative drugs | asset rights/data → clinical/regulatory progress → contract cash and obligations → accounting recognition/royalty → R&D, tax and shares → EPS | total headline consideration, future option exercise, all milestones achieved, broad “BD wave” | Hengrui counterparty/terms only; no recognition/EPS bridge. Biocytogen has no retained company package. |
| Power equipment | qualification/tender → award → order/backlog → delivery/acceptance → revenue → price/cost margin → receivable/cash → earnings | policy, grid investment, pilots and technical-strength narrative | No 002028/600406 order-to-cash record; zero earnings credit. |

## Ticker-level bridge and next-quarter thresholds

| Ticker | Current bridge state | Next-quarter validation threshold | Evidence needed to upgrade | Downgrade / no-credit condition |
|---|---|---|---|---|
| 002371.SZ 北方华创 | no retained company relationship or economics bridge | A dated issuer disclosure identifies product/process, qualification/customer and order/acceptance; paired revenue/margin/cash evidence is reconcilable | FY2025/2026H1/next report, IR/fab evidence, order/acceptance, product economics | sector/localization narrative remains sole support; `used_in_valuation=false` |
| 688012.SH 中微公司 | no retained company relationship or economics bridge | Same fields must be evidenced independently for this issuer | issuer filing/IR, process/customer, order/acceptance and product economics | peer or sector extrapolation; `used_in_valuation=false` |
| 600276.SH 恒瑞医药 | GSK counterparty/selected agreement terms only | Accounting note separates cash, contract liability/revenue recognition, costs and per-share impact; partner/asset progress is dated | agreement, issuer accounting, partner filing, clinical/registration, royalty/cost/probability | headline consideration/milestones treated as current profit; `used_in_valuation=false` |
| 688506.SH 百奥赛图 | no retained partner/asset/economics bridge | Dated issuer/counterparty evidence links a named asset/platform to contract, recognition/cash and economics | issuer/partner announcements, asset rights, clinical and cost/probability records | platform theme without a disclosed commercial bridge; `used_in_valuation=false` |
| 002028.SZ 思源电气 | no retained tender/order-to-cash bridge | Dated tender/contract and issuer disclosure connect qualification, award/order, delivery/acceptance and margin/cash | tender award, contract, filing and receivable/cash evidence | grid investment/policy becomes revenue/margin; `used_in_valuation=false` |
| 600406.SH 国电南瑞 | no retained tender/order-to-cash bridge | Same fields must be evidenced independently for this issuer | tender award, contract, filing and receivable/cash evidence | grid investment/policy becomes revenue/margin; `used_in_valuation=false` |

The next earnings bridge may be constructed only after these thresholds are met, reconciled to `data/verified_financials.md`, and consumed by the growth/valuation gates. Until then every item is monitoring evidence, not a base-case forecast.
