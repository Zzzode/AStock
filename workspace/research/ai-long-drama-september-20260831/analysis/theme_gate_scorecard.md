# Theme Gate Scorecard

## Common dataset rule

At each close, create one dated packet. `mapping_tier` is mandatory: `project_direct`, `platform_exposure`, or `broad_content`. Only `project_direct` and `platform_exposure` are eligible for the project-main-theme gates; `broad_content` can document AI-content diffusion only. Each cohort row must include `ticker`, `board`, `mapping_tier`, `mapping_source_id`, `close`, `prior_close`, `change_pct`, `amount_cny`, `limit_status`, `board_count`, and `trading_status`. Missing any field means the linked gate is **FAIL / incomplete**, not inferred from a narrative.

| Gate | Field definition | Pass test | Cadence / source | Decision if failed |
|---|---|---|---|---|
| Continuous catalyst | Timestamped project or industry event with a primary source ID | At D+1 or D+2, one new official platform, producer, regulator, or company source contains post-launch operating feedback or a second traceable event | D+1 and D+2 close; S04 plus new Tier 1 source | Keep event observation only |
| Core anchor | Company-level project/platform linkage | Mango TV programme-page hosting exposure remains verified; any replacement anchor needs a primary company source showing project relationship | D+1 and D+2; S04 or replacement Tier 1 source | Remove leader-replacement narrative |
| Vertical ladder | `board_count` and mapping status of direct-project main-board cohort | At least one `project_direct` main-board row has `board_count >= 2`, and at least one new `project_direct` main-board row has `board_count = 1` | D+1 and D+2; same-date market packet | Reject main-theme hypothesis |
| Main-board capacity | Amount rank, close acceptance and limit-state of direct-project main-board cohort | A `project_direct` main-board candidate ranks top two by `amount_cny` for two consecutive closes, `close >= prior_close`, and `limit_status != all_day_one_word` | D+1 and D+2; same-date market packet | Retain broad-content diffusion observation only |
| Market permission | Qualified cohort breadth and market-state flags | Qualified cohort has at least three rows, at least two-thirds have positive close change, and market packet has no risk-release or execution-block flag | D+1 and D+2; market desk packet | Stop any paper-plan upgrade |

## State logic

Only five PASS results at the same close can move the memo from `WATCH` to `CONDITIONAL_PAPER_RESEARCH`. Any FAIL returns it to `WATCH` or `REJECTED` as stated above. This scorecard contains no order, price, position or exit instruction.
