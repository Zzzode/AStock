# Capital-Flow Classification Algorithm

## 1. Why classify instead of naming a trader

The official Q1 report gives quarter-end holders, while the LHB gives daily seats. Neither source provides a complete beneficial-owner map. Therefore this algorithm classifies the stock's money structure without pretending that an institution seat is a named fund.

## 2. Institutional-base score

`Institution Base Score = 100 × [0.60 × min(named institutional ownership / 6%, 1) + 0.40 × min(HKSCC ownership / 5%, 1)]`

Inputs:

- named insurance: 3.05%;
- named public fund/ETF: 2.03%;
- named institutional total: 5.07%;
- HKSCC: 3.79%.

Result: `81.07 / 100`. This confirms a real institutional base, but it uses the 2026-03-31 snapshot and is not a live July position estimate.

## 3. Active-trading score

`Active Score = 100 × [0.35 × LHB participation + 0.25 × event repetition + 0.20 × direction conflict + 0.20 × financing crowding]`

Where:

- LHB participation = `min(29.67% / 30%, 1)`;
- event repetition = `min(4 LHB events / 4, 1)`;
- direction conflict = `1 − abs(sum institution net flow) / sum(abs(institution net flow))`;
- financing crowding = `min(4.28% / 5%, 1)`.

The four LHB institution net-flow observations are +4.24, -2.52, -8.70 and +4.37亿元-equivalent in CNY100m units across July 2, 3, 9 and 14. Direction consistency is only 0.1316, so the conflict score is high. Result: `94.11 / 100`.

## 4. Composite classification

`Composite = 45% × Institution Base Score + 55% × Active Score = 88.24`

Rule outcome: **institutional base + active trading reinforcement**.

This means:

- not pure游资票: insurance, public funds, ETF and HKSCC are present in the official holder table;
- not quiet institutional accumulation: LHB participation is extreme and institutional/Stock Connect direction alternates;
- not a pure机构票: active broker seats, financing leverage and short-window LHB drive the marginal price;
- not enough evidence to name a specific fund behind any institution seat.
