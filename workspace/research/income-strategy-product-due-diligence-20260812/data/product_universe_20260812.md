# Product Universe — Initial Freeze

**Case:** `income-strategy-product-due-diligence-20260812`  
**As of:** 2026-08-12  
**Status:** `intake_frozen_for_research_only`

This is the initial universe freeze for product due diligence. It identifies every named product and every unnamed allocation category in the legacy 5% total-return / 3% cash reference design. It is not a portfolio, investment recommendation, suitability conclusion, or execution instruction.

## Non-investability boundary

- All market-traded sleeves remain `q=0`; implementation is not authorized.
- A product cannot be selected, assigned a target price, used to support the cash objective, or treated as an implementation candidate until its R0-R4 package and the portfolio-level return, risk, suitability, account and current-session market gates independently pass.
- Direct equities, derivatives, margin financing, futures, leveraged products and lower-credit yield substitutes are excluded from this universe.

## Status definitions

| Status | Meaning |
|---|---|
| `active_research_universe_watch_only` | Explicit reference anchor or public-REIT candidate in the legacy strategy. It must be fully researched, but is not eligible for allocation. |
| `conditional_research_candidate_watch_only` | Secondary or contingent candidate. It must be fully researched if retained and has no approved allocation role. |
| `unnamed_category_not_researchable` | Allocation category without a product identity. It cannot be diligenced, valued or selected until a finite candidate list is frozen. |

## Named products

| ID | Product | Status | Legacy role and scope | Minimum product-specific evidence modules | Current boundary |
|---|---|---|---|---|---|
| ETF-511010 | `511010` 国泰上证5年期国债ETF | Active / watch-only | Five-year Treasury ETF anchor; 15% conditional reference weight (CNY30,000). Rate exposure, not protected liquidity. | Current legal terms; index and constituent bonds; duration/DV01/convexity and curve shocks; NAV/tracking/distributions; current price/NAV/IOPV and 20-session liquidity; tax/settlement/capacity; peers, stress and correlation. | No current duration, market-quality, account or portfolio-risk pass; `q=0`. |
| ETF-510880 | `510880` 华泰柏瑞上证红利ETF | Active / watch-only | High-dividend equity ETF anchor; 40% conditional reference weight (CNY80,000). | Current legal terms and index rules; full dated holdings and material constituent/overlap cards; dividend quality and TTM cash; NAV/tracking/drawdown/peers; current price/NAV/IOPV and liquidity; tax/settlement/capacity; REIT overlap, stress, catalysts and invalidation. | Index yield or historical distribution is not future holder cash; `q=0`. |
| ETF-512890 | `512890` 华泰柏瑞中证红利低波ETF | Conditional / watch-only | Secondary dividend ETF only; no approved reference weight. | Current legal terms and index rules; full dated holdings and material overlap cards; actual TTM cash; NAV/tracking/drawdown/low-vol factor/peers; current market packet; tax/settlement/capacity; conditional role test versus 510880 and REITs. | Cannot repair the income target or replace a failed sleeve; `q=0`. |
| REIT-508069 | `508069` 华夏南京交通高速公路REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; full project rights and concession/valuation history; traffic/tariff/network/term economics; financials, distributable cash, capex and refinancing; price/NAV and project-cash-flow valuation; liquidity/free float; cluster/overlap, scenarios and invalidation. | Historical annual-report/distribution facts are not current valuation, cash coverage, liquidity or independence; `q=0`. |
| REIT-508011 | `508011` 嘉实物美消费REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; full project rights and valuation history; footfall, sales linkage where disclosed, leases, tenants, occupancy and consumer economics; financials/cash/debt; price/NAV valuation; liquidity; cluster/overlap, scenarios and invalidation. | A distribution notice alone is not product or project due diligence; `q=0`. |
| REIT-508068 | `508068` 华夏北京保障房REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; project rights and valuation history; occupancy, rent, leases, tenants, affordable-housing policy and local supply; financials/cash/debt; price/NAV valuation; liquidity; rental-housing clusters, overlap, scenarios and invalidation. | Cannot be presumed independent from other rental-housing REITs; `q=0`. |
| REIT-508077 | `508077` 华夏华润有巢租赁住房REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; project rights and valuation history; occupancy, rent, leases, tenants and local rental-market analysis; financials/cash/debt; price/NAV valuation; liquidity; rental-housing clusters, overlap, scenarios and invalidation. | A distribution notice alone is insufficient; `q=0`. |
| REIT-508055 | `508055` 汇添富上海地产租赁住房REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; project rights and valuation history; occupancy, rent, leases, tenants, Shanghai supply and policy; financials/cash/debt; price/NAV valuation; liquidity; rental-housing clusters, overlap, scenarios and invalidation. | A distribution notice alone is insufficient; `q=0`. |
| REIT-508080 | `508080` 中金亦庄产业园REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; project rights and valuation history; occupancy, leases, tenants, industrial-park demand and local supply; financials/cash/debt; price/NAV valuation; liquidity; industry-demand clusters, overlap, scenarios and invalidation. | Not a cash-reinvestment vehicle or selected REIT without full evidence; `q=0`. |
| REIT-508096 | `508096` 中航京能国际能源REIT | Active / watch-only | Candidate for the 25% aggregate public-REIT sleeve; no individual target; 5% total-portfolio project cap. | Legal/fund/sponsor/operator documents; official rename and expansion history; complete current asset inventory; confirmed energy operating drivers; financials/cash/debt; price/NAV valuation; liquidity; energy/offtaker/regulatory clusters, overlap, scenarios and invalidation. | The legacy name **中航京能光伏REIT** is not the current product name. A legacy distribution notice cannot establish current scope or investment eligibility; `q=0`. |

### `508096` naming control

The Shanghai Stock Exchange's 2026-02-13 notice `508096_20260213_XUHW.pdf` states that the fund name, on-market short name and expanded short name changed effective 2026-02-13. The current name is **中航京能国际能源封闭式基础设施证券投资基金 / 中航京能国际能源REIT**. Archive that primary notice in the R0 source set. Do not retain a photovoltaic-only characterization until the current prospectus and asset inventory are verified.

## Unnamed categories

| ID | Category | Status | Legacy role and scope | Required action before research | Current boundary |
|---|---|---|---|---|---|
| CATEGORY-PROTECTED-LIQUIDITY | Eligible protected liquidity or direct very-short sovereign exposure | Unnamed / not researchable | Current 100% fallback (CNY200,000); 10% conditional reserve (CNY20,000). | Freeze the exact bank deposit, direct sovereign instrument or finite candidate list; then review issuer/legal claim, insurance aggregation where relevant, maturity/redemption, rate/fee/tax and account eligibility. | It is a category, not an identified product. It cannot be called eligible or used as a benchmark until exact terms and account facts are verified. |
| CATEGORY-DEFENSIVE-DIVERSIFIER | Defensive diversifier | Unnamed / not researchable | 10% conditional reference allocation (CNY20,000); diversification only, with zero cash-target role. | Approve non-leveraged selection criteria and a finite named candidate list; then complete current product, liquidity, stress, correlation, overlap, tax, settlement, valuation/risk-method and peer work for each candidate. | No generic stress input, placeholder allocation or implied cash yield is permitted. It remains `q=0`. |

## Selection constraints

Passing a product note is necessary but not sufficient. The final public-REIT sleeve requires at least five independently eligible projects, at least three manager/sponsor groups and at least three operating cash-flow sectors. Its hard caps are 25% aggregate REIT exposure, 5% per project, 10% per manager/sponsor or common risk cluster, and 15% for a shared dividend-ETF/REIT operating-risk cluster.

The current file records scope only. Strategy-case notices, annual reports and product disclosures are not a completed R0 evidence review, current market packet, valuation conclusion or investment decision in this due-diligence case.
