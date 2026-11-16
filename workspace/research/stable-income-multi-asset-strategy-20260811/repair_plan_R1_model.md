# R1 Repair Plan — Model (Closed)

Scope ID: `strategic-allocation-etf-first-v2-20260811`

Status: **resolved by independent review on 2026-08-12T05:09:15+08:00**.

The independent review recomputed the CNY200,000 model total and its -16.30% / CNY32,600 common stress. It verified the protected-liquidity fallback, CNY10,000 staging-cash cap, q-gated ETF actions, zero launch weights for REITs/direct stocks, `r`/`D_0` separation, and observed-`DD_t` controls. It also confirmed that retired legacy observations do not drive the active model.

The `not_run`/`q=0` execution state is intentionally retained as a non-authorization boundary. Reopen the plan if the allocation model, active scope or reader source changes.
