# Extended Public ETF Observation Manifest

One raw public-observation archive is retained in `manifest.json`: daily ETF
bars for 510300, 510880, 518880 and 511010 through 2026-08-13, accessed
through the AkShare Sina adapter and originally captured at `2026-08-14T14:01:57.358656+00:00`.

The archive SHA-256 is `c08eeb5f45417d96e5fa8dc19b9d6fb559382a7f4dc5cace84faca36a4c3aabd`. It is a tier-3 public observation, not an
official or licensed point-in-time archive. It does not establish an adjustment
basis, investor total return, historical availability, corporate actions, NAV,
trading status, costs, market depth or executable fills. It is retained only
to falsify research hypotheses and cannot approve a strategy or action.

## Hash control

The source manifest is sealed through `research_source_freeze_control.v1`
at `2026-08-14T14:44:20.991562+00:00`. Scripted verify/derived-refresh
modes compare the retained raw bytes and declared dependencies against this
control and never rewrite it. This is a case-local tamper-evident control, not
external notarization or a data-rights assertion.

## Descriptive-only dependencies

- `workspace/research/domestic-personal-securities-futures-strategy-20260814/sources/probe-public-etf-price-r0-20260814/e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda.portfolio.replay.json`（SHA-256 `8829c0a065aa688c874212500c345c7dd92aff6c88b2bba760f7de7921b15217`）：仅作descriptive_overlap_only。
