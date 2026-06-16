# Flow and Positioning Evidence

**Attempt date:** 2026-06-15
**Purpose:** Fill institutional positioning / fund-flow gap with public proxy sources.

| Source | Function | Test ticker | Result |
|---|---|---|---|
| Eastmoney northbound holding detail via AkShare | `stock_hsgt_individual_em` | 002463 | TimeoutError after 12s |
| Eastmoney individual fund-flow via AkShare | `stock_individual_fund_flow` | 002463 | ConnectionError / remote disconnected |
| Eastmoney holder-category data via AkShare | `stock_report_fund_hold` | multiple periods/categories | TypeError in current environment |

## Conclusion

Main shareholder and CNInfo filing metadata are available in `filings_holders_evidence.md`, but public proxy sources for northbound holdings, category institutional holdings, and fund-flow data were not reliable in this environment. The report must not claim complete institutional positioning coverage.

## Additional IR / Positioning Probe

- `stock_notice_report(symbol="002463")` was tested but the function expects announcement type rather than ticker and returned `KeyError('002463')`.
- Official annual reports contain investor-relations activity tables for some companies, especially Hudian and Shennan, including participant names and discussion topics such as 800G switch, Thailand capacity, capital expenditure, AI server and company revenue structure. These are useful qualitative evidence but not downloadable per-event transcripts from the tested interface.
