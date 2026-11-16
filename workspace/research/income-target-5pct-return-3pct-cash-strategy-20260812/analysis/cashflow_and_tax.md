# Performance Measurement, Distribution Accounting and Tax Boundary

## Return measurement: TWRR for the strategy, MWRR for the investor

The previous one-period return formula was not valid in the presence of intermediate subscriptions, withdrawals or cash transfers. The strategy must be judged by time-weighted return (TWRR). Split the record at every external cash flow. For subperiod \(j\), use the marked portfolio value immediately after the preceding external flow and immediately before the next external flow:

\[
r_j=\frac{V^{pre-flow}_{j,end}}{V^{post-flow}_{j,start}}-1,\qquad TWRR=\prod_{j=1}^{m}(1+r_j)-1.
\]

All assets, including settled distributions retained as cash, remain in \(V\). Therefore distributions are not added separately to a cum-income marked value. A withdrawal made after a distribution is an external flow and creates a new subperiod; it does not erase the return earned before the withdrawal.

The investor experience must separately report money-weighted return (MWRR / XIRR) from actual dated contributions, withdrawals and terminal value:

\[
0=\sum_{k=0}^{n}\frac{CF_k}{(1+r)^{t_k/365}}+\frac{V_T}{(1+r)^{T/365}}.
\]

Cash-flow signs and timestamps must be retained in the ledger. TWRR is the manager/strategy assessment; MWRR is the investor cash-timing outcome. They must not be substituted for each other.

## Cash ledger and eligible receipts

\[
Y_{cash,net,TTM}=D_{net,TTM}/\overline{V}_{flow-neutral}.
\]

Only settled interest, dividends, ETF distributions and REIT cash distributions
enter the receipt ledger. Each line records receipt date, source sleeve, gross
amount, tax, receipt fee, net amount, settlement date and source evidence.
Sale proceeds, NAV appreciation, unrealized gains, external contributions and
unsettled receivables are excluded. A daily unitized marked-value series
neutralizes each external contribution or withdrawal at its immediately pre-
flow marked value, so a later withdrawal cannot mechanically alter past
performance. It changes only the subsequent portfolio path, TWRR and future
cash capacity. An issuer-labelled or economically similar capital-repayment
component needs a separate ledger flag and predeclared accounting/tax treatment;
it is not labelled investment return until independently resolved.

Cash is part of total return, but it is not a second return added on top of price/NAV performance. Receipt eligibility and cash disposition are separate: the investor may retain, withdraw or take no action with a receipt, with ledger recording only. A later proposal for a new market allocation is separately reviewed; the framework sets no default action.

## Distribution accounting boundary

The former gross-yield entry budget is retired. Distribution history may inform
product mechanics, operating analysis, valuation and risk assessment, but it
does not create a cash-coverage test, target or selection threshold. A receipt
record must reconcile holder entitlement, taxes, receipt fees and settlement
dates. If this evidence is missing, the relevant attribution component is
unresolved; it may not be replaced by a historical headline yield, a quarterly
annualisation or sale proceeds.

For downside analysis, a candidate-specific distribution-cut history or
operating-cash-flow stress may be considered alongside price, NAV, leverage,
refinancing and liquidity evidence. It is a risk input, not a yield hurdle.

## Benchmarks and attribution

Before any formal replay, freeze three benchmark definitions and publish their daily total-return construction, costs, cash convention and rebalancing rule:

| Benchmark | Purpose | Current state |
|---|---|---|
| B0 — protected-liquidity comparator | Opportunity cost of remaining in the current fallback state | Not specified because the actual eligible account instrument is not yet identified. |
| B1 — frozen T2 cross-asset portfolio | Point-in-time total return for the named direct-equity, ETF, REIT, sovereign/cash candidates and documented substitutions, with cost-aware rebalancing | Not computable: no finite T2 candidate set, history, weights or substitution rule has been frozen. |

Attribution must reconcile total return into market price/NAV change, gross
cash distributions, tax/fees, trading costs, allocation/rebalancing effect and
residual. Any unexplained residual is a model failure, not alpha.

## Product-mechanics boundary

The CSRC public-REIT distribution rule and the historical ETF/REIT notices in
this case document cash mechanisms, not guaranteed cash or total return. The
511010 and 510880 reports show that historical fund-level performance and
distribution records can diverge. They cannot substitute for total-return
attribution or a formal strategy replay.
