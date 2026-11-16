# Valuation Audit

## Scope

This audit evaluates whether a new target can be published, rather than forcing a number from incomplete inputs. The outcome is intentionally “no new house target.”

## Market arithmetic checks

| Ticker | Close × total shares (CNY100m) | Recorded market cap | Result |
|---|---:|---:|---|
| 000703 | 18.18 × 38.215621 = 694.76 | 694.76 | Pass |
| 002379 | 19.76 × 130.311182 = 2,574.95 | 2,574.95 | Pass |
| 300014 | 55.22 × 21.732969 = 1,200.09 | 1,200.09 | Pass |
| 002497 | 19.09 × 11.525625 = 220.02 | 220.02 | Pass |

The share count is taken from the pre-open quote only as a stable share-count field; all price and market-cap calculations use the 2026-08-10 completed-session close.

## External-anchor arithmetic checks

| External reference | Calculation at refreshed close | Result |
|---|---|---|
| 000703 CNY16.50–17.60 | 16.50/18.18−1 to 17.60/18.18−1 = about -9% to -3% | Pass; does not support a low-position entry label. |
| 002379 CNY29 | 29/19.76−1 = about +47% | Pass; external reference only. |
| 300014 CNY77 / CNY103 | 77/55.22−1 = about +39%; 103/55.22−1 = about +87% | Pass; values are not averaged. |
| 002497 CNY42 | 42/19.09−1 = about +120% | Pass; external reference only. |
| 002812 CNY103 | 103/55.95−1 = about +84% | Pass; no longer a double at the refreshed close. |

## Evidence and methodology audit

- **Actuality:** only 000703 and 301308 have actual H1 reports. No preview was annualized.
- **Earnings denominator:** 002379’s broker number is adjusted NP; 300014 has two non-reconciled EPS/target constructions; neither is adopted as a house denominator.
- **Cash:** 000703, 300014, 002497 and 301308 retain negative reported OCF observations in relevant periods. Negative cash does not imply invalid profit, but it blocks an unqualified re-rating claim.
- **External-anchor independence:** every relevant target is one broker source. 300014 has dispersion; 002497’s operating assumptions and target share the same source logic.
- **Action audit:** no row is labelled as a recommendation, and all historical high-upside values remain explicitly non-formal.

## Reproducibility outcome

**Model Reproducibility: PASS** — all market-cap and external-upside arithmetic recalculates from disclosed price/share/anchor inputs, and the decision not to publish a house target follows the documented eligibility gates. This PASS applies to the audit trail, not to a claim that a current target price is supported.
