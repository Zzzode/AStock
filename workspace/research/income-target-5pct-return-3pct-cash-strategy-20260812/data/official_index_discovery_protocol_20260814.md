# CSI Public Index Discovery Protocol

- Protocol: `CSI-PUBLIC-DISCOVERY-v1`
- Frozen before result retrieval: `2026-08-14T12:15:00+08:00`
- Status: **public-source discovery only; q=0.**

This protocol checks a short, predeclared set of already-published CSI index
rules against the weak discovery condition of every complete rolling five-year
close-to-close index-value window reaching 5%. It neither builds a portfolio
nor chooses weights. It cannot establish a cost-aware investor TWRR, because
an index observation does not prove product tracking, tradeability, spreads,
fees, taxes, access or capacity.

## Predeclared index rules

| Code | Published rule / role |
|---|---|
| `H00300` | CSI 300 Total Return — broad-equity reference |
| `H00922` | CSI Dividend Total Return — dividend-factor equity reference |
| `932410` | CSI Dividend Equity and Bond Risk Parity — published equity-bond risk-parity reference |
| `932411` | CSI Dividend Equity and Bond Constant Proportion 10/90 |
| `932412` | CSI Dividend Equity and Bond Constant Proportion 20/80 |
| `932413` | CSI Dividend Equity and Bond Constant Proportion 30/70 |

The cross-asset entries are included because CSI publishes their methodology;
they are not assumed to be purchasable products or suitable implementations.
If an official response includes values dated before a rule's publication, the
result is treated as methodology back-history, not live investable history.

## Fixed mechanics

- Request only CSI's official public-history endpoint for 2017-06-30 through
  2026-08-14; preserve the raw response, request URL, retrieval time and hash.
- Evaluate each index independently. Do not blend indices, optimize weights,
  substitute a missing series or add costs/taxes/cash flows after inspection.
- Report all complete five-year windows, including every miss. A missing or
  malformed response remains unavailable.
- For each observed end date, pair the close with the latest observed close on
  or before the same calendar date five years earlier. Retain only elapsed
  periods from 1,825 to 1,832 days and annualise the index-value change using
  the actual elapsed days.

A public index observation at or above 5% can only pass this **weak discovery
screen**. It does not change T1/T2/T3/T4 admission, the scale-neutral formal
replay requirements, the absence of a cash-receipt objective, or the current
no-action state.
