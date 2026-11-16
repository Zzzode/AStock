# H2 Feasibility Memo — CFFEX Actual-Contract Treasury Futures

## Decision

**Not usable as a personal strategy or a predeclared return test in the current
public-observation evidence state.** `portfolio_q=0`; there is no selected
contract, direction, weight, leverage, order, risk budget, return result or
recommendation.

H2 is deliberately a **new** research family: exchange-traded, actual-contract
financial futures rather than the earlier commodity-futures samples or the R5
ETF proxy. The 10-year Treasury-futures family (`T`) appears below only as a
well-documented *reference family* for feasibility work. It is not an admission
to a universe and is not a product choice.

The desired 5% annualized outcome remains a research hurdle, never a guarantee.
No H2 performance has been calculated, and no evidence here establishes that
any futures overlay can deliver a stable 5% result.

## What the official route does establish

### Dated contract mechanics — reference only

The retained 2020 CFFEX contract rule gives an auditable template for an actual
contract ledger, not an investable position. For the `T` reference family it
states the following.

| Field | Dated official rule evidence | Research implication |
|---|---|---|
| Contract and quote | Nominal CNY 1m long Treasury, quoted per CNY 100 face value; minimum tick 0.005 | A ledger must use the rule-versioned multiplier and tick, rather than a generic continuous-price proxy. |
| Listed months / expiry | Three nearest quarterly months; last trading day is the second Friday of the delivery month; a new month starts on the next trading day | A calendar roll is possible to define, but the rule alone does not say which listed contract was liquid, eligible or selected on each historical date. |
| Daily P&L | The rule defines settlement-price-based daily P&L | Any valid outcome needs an actual-contract, daily-settlement ledger with rolls represented as close/open events. A back-adjusted continuous series is only a diagnostic, not portfolio P&L. |
| Delivery | Physical delivery | A frozen delivery buffer and account/eligibility state are mandatory; a 2024 CFFEX delivery reminder states that affected delivery-month positions may be forcibly closed if the required bond-custody-account review is absent. |
| Base controls | Minimum margin 2%; 3% from settlement two trading days before delivery; daily price limit ±2% of prior settlement; client position limits also exist | These are a dated base rule, not a historical session-by-session margin, limit-lock or broker-margin record. |

Source: `sources/official-h2-cffex-treasury-futures-20260815/ecffex_t_contract_rules_20200612.pdf`, Articles 4–24, effective 2020-07-20. The exchange risk-control rules also permit dynamic margin, limit and other interventions; these cannot be imputed from the base contract rule.

### Rules and data route — partial only

| Requirement | Official route discovered | Present evidence status | Why it is insufficient |
|---|---|---|---|
| Product terms / expiry logic | CFFEX product and dated contract-rule pages | **PARTIAL** | The retained rule is a single dated version; a full effective-date rule history and listed-contract lifecycle are absent. |
| Actual-contract EOD fields | CFFEX daily-statistics page advertises OHLC, prior settlement, settlement, volume and open interest by contract | **ROUTE IDENTIFIED, NOT VALIDATED** | No dated raw responses, request schema, full date coverage, original-date availability or source rights were captured. |
| Historical intraday / quote data | CFFEX historical-data service describes Level-1/Level-2 and one-/five-minute products with an application process | **PROCUREMENT ROUTE ONLY** | No entitlement, purchase, retention right, raw delivery or point-in-time archive exists in the case. It is not a public-observation input. |
| Trading calendar | CFFEX publishes a current calendar and annual closure notices | **PARTIAL** | A complete historical master calendar, exceptional closures and source hashes are absent. |
| Margin / limit / position changes | CFFEX risk-control rules and notices | **PARTIAL** | The rules allow adjustments. No full historical, effective-session archive of changes or broker margin add-ons is retained. |
| Fees | CFFEX publishes an exchange fee schedule directed to settlement members | **PARTIAL** | It is not a personal broker commission confirmation; time-varying exchange fees, broker pass-through, minimum charge and taxes are not frozen. |
| Delivery / forced-close state | Contract and delivery rules/notices | **PARTIAL** | No per-contract delivery-account status, delivery eligibility or historical forced-close event file is retained. |
| Actual executable fill / slippage | None in the official public material collected | **FAIL** | Daily bars and volume cannot determine bid/ask, queue, limit-lock, capacity, rejected orders or fills. |

The primary web pages are listed with URL and access limitation in
`sources/probe-h2-cffex-public-route-20260815/manifest.json`. Direct access to
`www.cffex.com.cn` timed out from this research environment; that is a local
transport observation, **not** evidence that the exchange is unavailable to an
entitled user. Conversely, the discovery of a CFFEX page is not evidence of a
complete, reproducible historical data set.

## Personal-account feasibility is not established

The archived dated CFFEX trader-suitability management rule contains
exchange-level conditions for an individual trading code, including civil
capacity, futures knowledge, prescribed experience, account/suitability and
available-funds checks, and record-related conditions. The CSRC suitability rule
separately requires an intermediary to collect investor information, classify
risk, and match products or services to the investor.

Those are **gates**, not a conclusion about any person. This case holds no
account, broker, suitability, knowledge-test, experience, available-funds,
risk-grade, delivery-account or broker-route evidence. The result is therefore
`PERSONAL_ACTION_FEASIBILITY=UNKNOWN`, not “eligible” and not “ineligible.”

Source boundary:

- CFFEX `交易者适当性制度管理办法` (dated 2019-12-14) is retained in the H2 official manifest. Any action would also require confirmation from the selected licensed futures company of the rule version and account-specific application.
- CSRC `证券期货投资者适当性管理办法` is retained in the H2 official manifest. It does not replace the exchange or broker process.

## Why a genuine predeclared future test cannot start now

A real future test must be an **actual-contract settlement ledger**, not a
continuous series assembled after the result is known. The following blockers
are all open:

1. **No frozen actual-contract history.** There is no hash-bound every-session
   data archive for all listed/expired contracts, including settlement,
   volume, open interest, trading state and contract identity.
2. **No point-in-time lifecycle.** Listing, expiry, delivery, suspension,
   force-close, extraordinary-calendar and contract-status records are not
   joined to every session.
3. **No effective-session risk parameters.** Historical exchange margin,
   price-limit, position-limit, special holiday and broker-add-on margin rules
   are missing. The base 2% figure cannot be extended across history.
4. **No cost-and-fill evidence.** Historical broker commissions and fee
   pass-through, bid/ask, depth, limit-lock, capacity and conservative no-fill
   convention are missing. Exchange fees paid by settlement members cannot be
   silently treated as the investor's total cost.
5. **No frozen construction.** There is no predeclared universe, eligibility
   screen, signal, contract-selection rule, roll rule, delivery buffer,
   long/short permission, leverage ceiling, collateral treatment, stop/no-fill
   state or invalidation condition.
6. **No account feasibility proof.** Personal trading-code eligibility and the
   broker's current route are intentionally unobserved.
7. **No independent review or endpoint population.** No unitized ledger means
   no complete five-year endpoint set, no drawdown/capacity audit and no
   independent result check.

The public page that presents a continuous-looking or delayed quote must never
bridge these gaps. A continuous series has a construction convention; it does
not capture the actual close/open roll cost, margin path, limit state or
tradability of a strategy.

## The only permitted next research gate

No parameter search or contract ranking is permitted on H2. A distinct,
authorized evidence project could begin only after all of the following are
available and hash-frozen before the result is read:

1. Licensed/authorized acquisition of full historical actual-contract market
   data, with written rights, delivery manifest, timestamps and source hashes.
2. A point-in-time contract master plus daily status, calendar, delivery and
   extraordinary-event history for every candidate contract.
3. Historical effective exchange margin/limit/fee notices and actual
   broker-route commission/margin schedules; an unresolved item must produce
   `no-fill` / `not-testable`, not an assumed low cost.
4. A separate personal-account feasibility confirmation from a licensed broker;
   no personal data need be placed in this research case.
5. A signed rulebook before any result: candidate families, selection and roll
   logic, delivery buffer, settlement marking, cost/no-fill policy, collateral
   handling, unitization and risk/invalidation constraints.
6. Independent maker-checker review of the data population and all complete
   rolling five-calendar-year endpoints. Passing a historical hurdle would
   remain evidence, not a yield promise or investment instruction.

Until then, H2 remains an **evidence memo only**. It cannot solve the requested
strategy objective, and it must not be combined with R5 or the earlier
commodity-futures sample to manufacture a result.

## Status record

| Field | Value |
|---|---|
| Case | `domestic-personal-securities-futures-strategy-20260814` |
| Family | H2 actual-contract domestic financial-futures feasibility |
| Reference product | CFFEX 10-year Treasury futures (`T`) — documentation reference only |
| Data cutoff | 2026-08-15 source-access review |
| Research result | `NOT_FEASIBLE_FOR_PREDECLARED_TEST_OR_PERSONAL_ACTION` |
| `portfolio_q` | `0` |
| Formal decision eligible | `false` |
| Return / allocation / action | None |
