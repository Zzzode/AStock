# Valuation Audit — Strategic Allocation Arithmetic

## Active-vector arithmetic

- Conservative core: protected liquidity 40% + trading cash 5% + high-quality rates 35% + dividend equity 10% + gold 10% = 100%.
- Base core: protected liquidity 20% + trading cash 5% + high-quality rates 35% + dividend equity 30% + gold 10% = 100%.
- Base REIT-enabled: the same base core, with 5 percentage points transferred only from rates to approved REITs: 20% + 5% + 30% + 30% + 10% + 5% = 100%.
- Growth core: protected liquidity 10% + trading cash 5% + high-quality rates 30% + dividend equity 35% + broad equity 10% + gold 10% = 100%.
- Growth REIT-enabled: 10% + 5% + 25% + 35% + 10% + 10% + 5% = 100%.

The fixed-CNY200,000 base-core mapping recomputes to CNY40,000 + CNY10,000 + CNY70,000 + CNY30,000 + CNY30,000 + CNY20,000 = CNY200,000. This is the full investment capital $V$, with no prior reserve deduction.

## Annual-addition control tests

The published formula uses post-contribution $V^+=V+C$ and capped gaps

\[
d_i=q_i\times\min\left(\max(0,w_iV^+-H_i),\max(0,u_iV^+-H_i)\right).
\]

It allocates pro rata only when $\sum d_i\ge C$; otherwise it fills the gaps and retains the residual in protected liquidity. The following deterministic checks are included to prevent the prior pre-contribution-$V$ overshoot failure:

| Test | Inputs | Expected result | Status |
|---|---|---|---|
| A01: non-active REIT activation arithmetic | $V=100$, $C=20$, $H=(26,30,29,10,5)$ for cash/rates/dividend/gold/REIT; $V^+=120$ | $d=(4,6,7,2,1)$; final weights are 25/30/30/10/5. Dividend is 30%, below 35% hard cap. This is a future-activation arithmetic test, not a current REIT allocation. | PASS |
| A02: inactive REIT | $V=100$, $C=10$, $H=(25,35,30,10,0)$; inactive target 25/35/30/10/0 and $u_{REIT}=q_{REIT}=0$ | $d=(2.5,3.5,3,1,0)$; no addition can enter REIT, and final weights are core targets. | PASS |
| A03: breached dividend cap | Existing dividend value is above $0.35V^+$ | The second capped term is zero, so $d_{dividend}=0$; new money is barred pending manual review. | PASS |
| A04: seven-sleeve base core | $V=100$, $C=20$, $H=(24,5,33,28,0,10,0)$ for protected/trading/rates/dividend/broad/gold/REIT; $V^+=120$ | $d=(0,1,9,8,0,2,0)$; the final full vector is 20/5/35/30/0/10/0 with every sleeve represented. | PASS |
| A05: eligibility failure residual | $V=100$, $C=10$; core holdings at 20/5/35/30/0/10/0, while only protected liquidity has $q=1$ | The target protected-liquidity gap is 2; CNY2 is allocated there and CNY8 remains in the same protected layer. Its 100% safety upper bound prevents a risk-cap breach. | PASS |

## Scenario arithmetic

Base-core common-stress outcome: $0.20\times0+0.05\times(-1\%)+0.35\times(-5\%)+0.30\times(-45\%)+0.10\times(-10\%)=-16.30\%$.

Base REIT-enabled common-stress outcome: $0.20\times0+0.05\times(-1\%)+0.30\times(-5\%)+0.30\times(-45\%)+0.10\times(-10\%)+0.05\times(-25\%)=-17.30\%$.

Base REIT-enabled distribution-cut outcome: $0.20\times0+0.05\times(-1\%)+0.30\times(+1\%)+0.30\times(-25\%)+0.10\times0+0.05\times(-15\%)=-8.00\%$.

At fixed $V=\text{CNY200,000}$, the base-core common-stress outcome is CNY32,600 and the REIT-enabled common-stress outcome is CNY34,600.

The scenario table deliberately uses a 12-month, simultaneous-shock planning horizon. It is not a calibrated correlation model, a probability estimate, or a maximum-loss estimate. Its -16.30% or -17.30% figures are scenario outputs only; they do not trigger the observed-drawdown controls, which require a dated account-value and high-water-mark record.

## Method fit

Company-style PE/PB/DCF/target-price valuation is not fit for cash, index ETFs, gold exposure or a yet-unselected REIT. The appropriate method is role suitability, allocation cap, duration/quality, combined-holding concentration and execution-date liquidity control. Every `not_applicable` price field in the structured model is intentional and blocks any claim of a security-specific upside.

## Evidence boundary and release status

- Scope ID: `strategic-allocation-etf-first-v2-20260811`.
- Official sources support rules and product structure; no current price, indicative yield or broker target supports an allocation conclusion.
- Broker weight is zero for every row; the broker target-price boundary is documented in `source_exhaustion_log.*`.
- The strategy is conditional on the not-run execution eligibility policy: current product documents, current-session price/IOPV/premium/discount/spread/liquidity, account feasibility and dated combined holdings where required.
- The controlled allocation arithmetic tests pass, but this scope rewrite has not yet had an independent current-source R1 review. Institutional publication remains blocked pending primary-source archival, completed current-scope review lifecycle, and compliant XeLaTeX/PDF visual verification.

Model Reproducibility: PASS (static allocation arithmetic only; this is not a current-scope review or publication sign-off).
