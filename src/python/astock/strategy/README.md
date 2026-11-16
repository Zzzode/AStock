# Personal Strategy Research System

This package translates selected global institutional return families into
transparent, personal-account research sleeves.  It does not imitate a fund's
proprietary alpha and never routes broker orders.

For a Chinese, user-facing global-institutional-to-personal applicability
matrix and operating protocol, see [PERSONAL_STRATEGY_PLAYBOOK.md](PERSONAL_STRATEGY_PLAYBOOK.md).

## Strategy boundary

| Family | Personal implementation | Status |
| --- | --- | --- |
| Strategic allocation | Core reserve / liability-aware allocation | Paper research |
| Global macro / risk-balanced allocation | Public-instrument risk-budget research | Conditional; research only |
| PE / public-underwriting analogue | Public-information underwriting process | Research only; ownership and allocation are not portable |
| Private credit / real assets | Product and cash-flow due-diligence research | Research only; no origination or product-access claim |
| Systematic equity | Liquid A-share long-only factor tilt | Conditional |
| Event driven | Timestamped public-announcement earnings repricing | Conditional |
| Merger / special situations | Public filing-timeline and scenario research | Research only; no merger-arbitrage claim |
| CTA trend | Domestic futures multi-horizon time-series momentum | Conditional; paper only |
| Domestic calendar / RV | Actual-contract futures term-structure diligence | Research only; no global-carry proxy claim |
| Liquid crypto trend | Crypto time-series-momentum research | Research only; explicit legal-access non-inference gate |
| Market-neutral stat arb | No economic-equivalent implementation | Blocked |
| Global carry / RV | No economic-equivalent implementation | Blocked |
| Volatility dispersion | No economic-equivalent implementation | Blocked |

`catalog.py` records the distinction.  A personal access profile can make a
conditional sleeve paper-eligible, but it cannot override a structural
non-replicability gate.

## Crypto jurisdiction boundary

`lawful_crypto_market_access` is a self-attested profile fact only. It cannot
be inferred from `lawful_global_market_access` or `permitted_markets`, and is
not a legal opinion. A target-bearing research proposal additionally needs a
dated non-Mainland residency/jurisdiction record, venue permission, custody
review, data-entitlement evidence and immutable source archives. It can never
make the crypto sleeve execution-eligible. The catalog treats a
Mainland-resident retail crypto implementation as non-actionable; a foreign
venue, a generic global-access assertion, or a self-attestation is never a
Mainland workaround. Users must independently obtain current, jurisdiction-
specific legal, tax, venue, custody and suitability advice before considering
any action.

## Public taxonomy and research sources

These sources inform strategy names and research questions only. They do not
validate expected returns, product availability, suitability, execution, or
legal status:

- [HFR Hedge Fund Strategy Classification System](https://www.hfr.com/hfr-indices/hfr-hedge-fund-strategy-classifications/)
  for broad macro, event-driven, relative-value and crypto taxonomy.
- [AQR, *Understanding Risk Parity*](https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Understanding-Risk-Parity.pdf)
  for risk-budgeting concepts.
- [Moskowitz, Ooi and Pedersen, *Time Series Momentum*](https://doi.org/10.1016/j.jfineco.2011.11.003)
  for the academic time-series-momentum reference.
- [Fama and French, *A five-factor asset pricing model*](https://doi.org/10.1016/j.jfineco.2014.10.010)
  for factor terminology.
- [PBOC, CSRC and other agencies' 6 February 2026 virtual-currency risk notice](https://www.csrc.gov.cn/csrc/c100028/c7614318/content.shtml?f_link_type=f_linkinlinenote)
  for the current Mainland regulatory boundary represented in this catalog.

## Domestic futures CTA

`cta.py` is a low-frequency, cross-sectional diversified time-series momentum
sleeve using 21/63/126-session signals, volatility sizing, signed contract
targets, group and margin caps, a next-session execution delay, daily
settlement marking, and conservative participation limits.

It requires a dated broker/exchange account-and-instrument eligibility record,
source-labelled contract facts, and an explicit futures access profile. A
historical P&L replay additionally needs an immutable source archive plus
*each session's* active contract, multiplier, initial/maintenance margin,
position limit, execution status and verified roll exit/entry facts. A public
continuous series can be frozen and inspected exactly through `data.py`, but
it remains a `contract_lifecycle_coverage="proxy"` input and cannot generate a
manual trade target or P&L replay.

### Minimum usable CTA data contract

The user account never supplies credentials or an account number. It supplies
only a dated evidence record, for example:

```json
{
  "profile_id": "personal-futures-paper",
  "futures_eligible": true,
  "licensed_eod_data": true,
  "risk_capital": 1000000,
  "futures_access_evidence": {
    "as_of": "2026-08-15",
    "source_ref": "broker-eligibility-record:2026-08-15",
    "data_entitlement_source_ref": "market-data-entitlement:2026-08-15",
    "permitted_exchanges": ["shfe", "dce", "czce", "cffex", "ine", "gfex"],
    "eligible_instruments": ["rb", "au", "m", "if"]
  }
}
```

For every instrument and every historical session, the CTA input must include
the actual `active_contract`, `settlement`, `volume`, `open_interest`,
`execution_status`, `days_to_expiry`, `contract_multiplier`, initial and
maintenance margin rates, position limit, `contract_facts_as_of`, and the
source reference for those facts. A contract change requires explicit
`roll_from_contract`, `roll_exit_price`, `roll_entry_price`, and
`roll_source_ref`. The engine rejects a continuous front-month series that
tries to stand in for those facts.

This is intentionally more demanding than a charting backtest: it makes a
futures result answerable to the same operational questions that determine
whether a personal account could actually carry the position through a limit,
margin change, roll, or delivery window.

## Equity, crypto sleeves and portfolio control

`equity.py` contains two bounded, long-only translations.  Their default
gross budgets are deliberately kept separate (40% for factor, 20% for event)
so a later allocator can retain a cash reserve and a distinct futures risk
budget:

- `ashare_factor_tilt`: quality/value/momentum/investment ranking with current
  timezone-aware trading-state cutoff, verified SSE/SZSE/BSE A-share identity,
  liquidity, listing-age, risk-warning, halt and price-limit vetoes.
- `earnings_event_repricing`: only timestamped public announcements with an
  immutable identifier, timezone-aware publication **and availability** times,
  a declared surprise score, freshness and the same executable-state gates.

`crypto.py` is a separate 24/7 market path, not an A-share or domestic-futures
adapter. It accepts only caller-supplied, source-labelled OHLCV observations
with timestamp and availability time, dated venue metadata, immutable archives
and verified funding records for perpetual targets. It applies multi-horizon
trend, volatility sizing, asset/venue concentration caps, liquidity,
listing-age, bar-gap and funding-quality gates. The public capability requires
a dated non-Mainland jurisdiction/venue/custody/data access artifact and still
returns research-only paper targets; no China-mainland access route or legal
clearance is created.

`allocation.py` aggregates source-labelled sleeve proposals into separate
security, futures and crypto paper ledgers using one common-NAV cash and
collateral waterfall. Futures are integer-sized before their dated per-lot
margin is booked; zero-contract remnants are dropped. Crypto legs are never
netted across venue, market type or direction, and cannot enter an active
paper ledger from JSON alone: an external trusted validator and a formal,
unexpired, point-in-time artifact are required. A hard risk veto freezes all
new targets; it does not silently net instruments or manufacture fills.
`registry.py` records immutable strategy versions, lifecycle transitions and
paper/backtest runs in a local SQLite audit log.

## CLI

```bash
python -m astock.cli strategy catalog --json
python -m astock.cli strategy cta-proposal \
  --market-data-path bars.json \
  --instruments-path contracts.json \
  --access-profile-path domestic-futures-access.json \
  --capital 1000000 --json
python -m astock.cli strategy cta-backtest \
  --market-data-path bars.json \
  --instruments-path contracts.json \
  --access-profile-path domestic-futures-access.json \
  --capital 1000000 --json
python -m astock.cli strategy crypto-proposal \
  --market-data-path crypto-bars.json \
  --assets-path crypto-assets.json \
  --access-profile-path lawful-non-mainland-profile.json \
  --as-of 2026-08-15T00:00:00Z --json
python -m astock.cli strategy factor-proposal --universe-path universe.json \
  --source-ref "archive:universe-20260814" --json
python -m astock.cli strategy earnings-proposal --announcements-path events.json \
  --source-ref "archive:announcements-20260814" --json
python -m astock.cli strategy allocate --sleeves-path sleeves.json --json
```

All results are research or paper-trading records.  Before any manual action,
the user must independently verify current broker eligibility, contract,
margin, position-limit, delivery/roll, liquidity, and market-status facts.
