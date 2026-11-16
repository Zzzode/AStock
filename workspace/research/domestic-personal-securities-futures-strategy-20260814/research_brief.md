# 国内个人证券与商品期货策略：后继研究简报

- Case ID: `domestic-personal-securities-futures-strategy-20260814`
- Data cutoff: 2026-08-14
- Report type: interim evidence memo; not a reader-facing investment report
- Language: Chinese
- Status: R0/R1 evidence build; no approved decision universe and `q=0`

## Mandate

Research whether a scale-neutral, personally operable domestic securities and
commodity-futures process can **target** a strict ex-post, cost-aware result:
every complete calendar-year TWRR and every rolling five-year annualized TWRR
must be at least 5%. This is a test criterion only. It is not a return
guarantee, annual floor, forecast, probability estimate, allocation, holding,
subscription, sale, order or external-execution authorization.

The research has no separate cash-receipt target and no automatic-reinvestment
requirement. Every settled distribution, interest, coupon and redemption is an
accounting event recorded exactly once in a total-return ledger. A distinct
withdrawal treatment, if ever needed, must create an explicit TWRR subperiod
rather than be embedded in a result.

## Coverage and representative research routes

The universe is open to lawful domestic instruments that can pass a dated,
source-backed eligibility process. The **finite R0/R1 comparison set** below is
only a way to make the first tests reproducible; it is not a permanent asset
restriction or recommendation.

| Sleeve | Representative item/family | Research role | Current state |
|---|---|---|---|
| Treasury-bond ETF | `511010.SH` | Five-year Treasury-bond comparison sleeve; defensive behaviour unproven | R1 product facts only; `q=0` |
| Broad equity ETF | `510300.SH` | A-share beta comparison sleeve | R1 product facts only; `q=0` |
| Dividend equity ETF | `510880.SH` | Dividend-factor equity comparison sleeve | R1 product facts only; `q=0` |
| Gold ETF | `518880.SH` | Domestic gold-exposure comparison sleeve; diversification unproven | R1 product facts only; `q=0` |
| Money-market ETF | `511990.SH` | Money-market comparison; settlement functionality unverified | R1 product facts only; `q=0` |
| Static multi-asset ETF | `510300`, `510500`, `510880`, `511010`, `511990`, `518880` | Fixed core-satellite diagnostic | Historical market-price diagnostic has failures; not total return or execution; `q=0` |
| Convertible-bond ETF | `511180`, `511380`, `511010` | Fixed defensive-credit diagnostic | Historical price proxy has failures; not total return or execution; `q=0` |
| Direct A shares | `600519`, `600900`, `601398`, `601088` | Quality/distribution representative research basket | Dated issuer diligence plus bounded gross-cash diagnostic; two complete-year failures; `q=0` |
| Market-neutral public fund | `008856` | Manager-published NAV proxy route | Historical proxy has complete-year and rolling failures; not holder dealing result; `q=0` |
| Public infrastructure REIT | `508000` | Listed infrastructure-income representative route | Zero-cost cash diagnostic has annual and rolling failures; not personal net return; `q=0` |
| Commodity futures | `AU`, `CU`, `RU` actual listed contracts | Conditional diversification / trend research families | Dated rules and sparse actual-contract route only; no admissible return test; `q=0` |
| Treasury cash-futures basis | `T`, `TF`, `511260` | Conditional relative-value / delivery-basis route | Dated rules and sparse actual-contract route only; no admissible paired ledger; `q=0` |
| ETF covered call | `510300` plus SSE CSI 300 ETF calls | Conditional options-income route | Mechanics documented; actual-contract/execution package absent; `q=0` |

Direct equities and public REITs now have bounded representative research
tracks, not approved selections. Financial futures, other option structures,
leveraged/inverse products, other commodity families and any unlisted or
non-domestic instrument remain open research questions. No class has a weight
or execution permission in this case unless it is captured by the frozen U0
population, derived through the class-neutral T2 audit and taken through the
same evidence path.

## Operational open-universe control

The finite R0/R1 comparison set cannot become the de facto strategy universe
because it is easier to source. The U0 domestic-universe registry separates
class discovery from selection. Direct equities and public REITs now have only
bounded representative tracks; their universe-level status, as well as listed
bonds/convertibles, financial futures and options, remains unresearched rather
than rejected. A future decision universe must be drawn from a frozen U0
population snapshot with a class-neutral admission rule; a missing dossier or
data feed is never an economic exclusion.

## Hard boundaries

1. Preserve the predecessor case
   `income-target-5pct-return-3pct-cash-strategy-20260812` as a frozen
   framework release. Do not treat its PDF, verifier result or sign-off as a
   pass for this successor case.
2. Do not use a public continuous-futures series as actual-contract P&L or
   roll evidence.
3. Do not use a public ETF series with unresolved adjustment basis as a
   total-return result.
4. No product or contract can enter an approved decision universe without
   current product/contract facts, costs, tradability and independent review.
5. Commodity futures require separate suitability, broker-route and contract
   eligibility checks. No user-specific eligibility is assumed.
6. No finite probe universe, product label or convenient public data source may
   silently become a selection rule. The U0 population, U0-to-T2 derivation
   audit, formal replay protocol and data contract must be frozen before a
   formal test.
7. No issuer, security, fund, REIT, bond, contract or option series may enter
   a formal test without its parent U0 class having an accepted data/replay
   module. A partial class set is coverage-restricted, not an open-universe
   strategy.

## Upgrade path

The next executable stage also requires a frozen U0 population snapshot and a
versioned formal replay protocol that specifies the rolling-window statistic,
time semantics, population treatment, costs, execution state machine and
independent verification before any outcome is opened.

The next executable research stage requires an authorized, frozen data package
for ETF market prices/events and actual futures contracts, a rulebook frozen
before results are viewed, all-window cost-aware replay, current execution
checks, a paper reconciliation period and independent R0/R1/risk review. If
any of those gates fails, the relevant sleeve remains `q=0` and the case stays
an evidence memo.
