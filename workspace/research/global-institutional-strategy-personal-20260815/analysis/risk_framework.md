# Risk Framework

## Common NAV and cash waterfall

All future research reports must calculate NAV from marked assets plus eligible cash, less documented liabilities and costs. External flows are excluded from time-weighted return periods and reconciled separately to investor money-weighted return. Cash receipts are recorded once; return-of-capital-like movements are not silently counted as income.

## China securities mechanics

Ordinary stock purchases must not be modelled as having an assured same-day disposal path (S13). This sentence is deliberately scoped: ETFs, bonds, options and other products can have different rules. Any strategy report must establish its exact product mechanics, price limits, suspension/halts, corporate actions, liquidity and cost state on the relevant date.

## Domestic futures mechanics

Futures paper research must carry margin, price-limit, position-limit, delivery, roll, daily-settlement and forced-close assumptions as dated fields, not immutable constants (S11, S12, S15). A stop is a risk instruction, not a guarantee of an executable fill; cross-margin and offsetting positions cannot be presumed to survive stress.

## Crypto boundary

The framework has no China-mainland implementation route. Crypto market research cannot assume a lawful access path, 24/7 exit, reliable mark, safe custody, stable funding, withdrawal availability or recovery rights. No workaround is proposed. See S14 and the separate applicability packet.

## Freeze/escalation triggers

1. data availability or source timestamp cannot be demonstrated;
2. product/account jurisdiction or eligibility is unclear;
3. a price limit, suspension, margin change, delivery risk or liquidity shock breaks the replay assumption;
4. a cash receipt cannot be classified without double counting;
5. portfolio loss, drawdown or margin rule is not approved; or
6. a narrative requires a proprietary/institutional capability that cannot be evidenced.
