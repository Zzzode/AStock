# Source Registry

The active source population is limited to the 15 complete records S01--S13 and S15--S16. Authority, local archival completeness and implementation-date fitness are separate controls. Active archive paths and hashes remain in the archive manifests referenced by source_archive_status.json; this registry preserves the scope classification and record-level audit metadata.

| Source ID | active_scope | Authority / quality | Active-scope use and boundary |
|---|---|---|---|
| S01 | true | State Taxation Administration / Tier 1 primary | Tax-rule boundary for a separately reviewed future direct-stock case; not an individual tax opinion or an ETF-distribution rule. |
| S02 | true | State Taxation Administration / Tier 1 primary | Fund-distribution tax boundary; fees, product notices and current law still require review. |
| S03 | true | CSRC / Tier 1 primary | Fund risk-bearing and contract-governed distribution boundary. |
| S04 | true | CSRC regulator education / Tier 1 | Fund-distribution and NAV mechanics; not a performance source. |
| S05 | true | PBOC / Tier 1 primary | Deposit-insurance boundary; does not extend to fund or wealth-management products. |
| S06 | true | PBOC and financial regulators / Tier 1 primary | Asset-management non-guarantee boundary. |
| S07 | true | State Taxation Administration / Tier 1 primary | Personal-pension tax boundary; personal eligibility and lock-up remain separate checks. |
| S08 | true | SSE-hosted fund filing / Tier 1 product | Rate-bond fund identity and risk boundary; not an execution recommendation. |
| S09 | true | SSE / Tier 1 exchange | Dividend-low-volatility fund identity; implementation liquidity and suitability must be current. |
| S10 | true | SSE-hosted fund filing / Tier 1 product | Historical fund-distribution mechanism; not a distribution forecast. |
| S11 | true | SSE-hosted fund prospectus / Tier 1 product | Gold-spot fund identity and risk boundary; no current pricing or liquidity conclusion. |
| S12 | true | SSE-hosted fund product summary / Tier 1 product | Money-market fund risk boundary; refresh the filing at implementation. |
| S13 | true | SSE investor education / Tier 1 exchange | Holding-distribution and secondary-market-return distinction. |
| S15 | true | SSE / Tier 1 exchange | Public-REIT structure and risk boundary; not a project-selection or valuation conclusion. |
| S16 | true | China Securities Index / Tier 1 index provider | Index concentration reminder; full implementation-date look-through remains required. |

## Retired legacy context

| Source ID | active_scope | Scope status | Audit-only treatment |
|---|---|---|---|
| S14 | false | retired_from_active_scope | Retained as a legacy record only; no current-scope factual use. |
| M01 | false | retired_from_active_scope | Retained as a legacy market-data record only; its missing original bytes were not recovered. |
| D01--D08 | false | retired_from_active_scope | Retained as legacy issuer-source records only. |

No legacy row may support a target, allocation, valuation, cash or execution conclusion. The legacy rows remain in source_registry.json for traceability with active_scope set to false.
