# Model Portfolio Implementation Card — 2026-08-12

## Status

This is a controlled model portfolio. The linked execution-eligibility policy is **NOT RUN** because the case has no current product-and-market packet. The model contains target notionals and a deterministic deferral rule; it does not contain a price, share quantity, timing, broker channel, return forecast or suitability conclusion.

## Designated model targets

| Sleeve | Designated model instrument | Target | Conditional model action | If the execution-day check fails |
|---|---|---:|---|---|
| Protected liquidity | Eligible insured-bank deposit or a directly held government bond matched to the horizon | CNY40,000 | Establish at T0 | Hold as a pending protected-liquidity reserve, not as staging cash; do not substitute a wealth-management product or fund. |
| Staging cash | Settlement cash or bank demand deposit; 511880 is optional only after a separate check | CNY10,000 | Retain at T0; hard cap CNY10,000 | Keep only this CNY10,000 sleeve as cash. |
| Rate bonds | 511010 — 国泰上证5年期国债ETF | CNY70,000 | Establish at T0 only when q=1 | Do not trade; retain the amount in eligible protected liquidity. |
| Dividend equity A | 510880 — 华泰柏瑞上证红利ETF | CNY30,000 | Build in six scheduled tranches only when q=1 | Do not trade the failed tranche; retain it in eligible protected liquidity. |
| Dividend equity B | 512890 — 华泰柏瑞中证红利低波动ETF | CNY30,000 | Build in six scheduled tranches only after q=1 and the combined-holdings test | Do not trade; retain the full CNY30,000 in eligible protected liquidity. |
| Gold | 518880 — 华安易富黄金ETF | CNY20,000 | Build in six scheduled tranches only when q=1 | Do not trade the failed tranche; retain it in eligible protected liquidity. |
| Public REITs / direct stocks | None | CNY0 | Do not buy at launch | Remain at zero until their separate gates pass. |

The rule is one-way: a failed or missing validation never increases staging cash beyond CNY10,000 and never substitutes 511010, another ETF, REITs or direct stocks. A fresh complete pass is required at the next scheduled tranche or review; there is no catch-up trade.

## Eligibility packet

data/execution_eligibility_policy_20260812.json defines the current-session source/timestamp fields, q status, premium/discount, quoted-spread and tranche-liquidity controls. It also requires a dated combined 510880/512890 look-through: a sector may not exceed 25% of total portfolio and top-ten issuer groups may not exceed 35% of the equity sleeve. Its controlled thresholds are risk controls, not observed market facts. At this draft date all ETF q values remain 0.

## Sequence

1. At T0, establish CNY40,000 protected liquidity, retain CNY10,000 staging cash, and establish up to CNY70,000 of 511010 only after q=1.
2. In each of months 1--5, allocate CNY5,000 toward 510880, CNY5,000 toward eligible 512890, and CNY3,333 toward 518880 only if their relevant q is 1.
3. In month 6, allocate CNY5,000 / CNY5,000 / CNY3,335 to the same sleeves subject to the same gates.
4. Rebalance only after a quarterly measurement and normally on a semiannual cycle; do not treat a price decline as an automatic buy signal.

The cited product identities are supported by S08--S12. Any live action would require current product, IOPV, premium/discount, spread, liquidity, account and look-through records in the eligibility packet.
