# Source Exhaustion Log

| Scope | Source class | Status | Why not collected or used | Consequence | Next verification path |
|---|---|---|---|---|---|
| Retired historical stock, market and futures records | S14, M01 and D01--D08 | retired_from_active_scope | The historical archive state is retained without recovering missing raw bytes. These records are outside the current zero-direct-stock and zero-futures strategy. | Cannot support a target, allocation, valuation, cash or execution conclusion and does not reduce active-source completeness. | Preserve only as audit history; any future separate scope requires a new, independently captured evidence package. |
| Current exchange price, IOPV, premium/discount and turnover | implementation-date market packet | not collected | The current case does not contain a fresh implementation-date packet. Retired historical records do not fill this gap. | No execution-price, timing or liquidity conclusion. | Obtain a timestamped implementation-date observation from an approved exchange or broker interface. |
| Fund legal documents at implementation date | current product filing | pending implementation date | The case cutoff is 2026-08-11 and an implementation date is not set. | Product examples remain a research pool, not a mandate. | Check the latest prospectus, product summary, fee schedule and announcements immediately before implementation. |
| REIT project information | project-level operating and valuation package | intentionally not collected | No individual REIT is included in the core allocation. | REIT sleeve remains 0% until project review. | Collect project cash flow, debt, operations, valuation and premium evidence for each candidate. |

Broker target-price records are deliberately outside this asset-allocation scope. This statement is not evidence that such records are unavailable for all listed instruments.
