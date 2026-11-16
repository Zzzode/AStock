# Final Sign-off — PASS for Conditional Research Publication

## Disposition

- Case: `stable-income-multi-asset-strategy-20260811`
- Scope ID: `strategic-allocation-etf-first-v2-20260811`
- Data cutoff: 2026-08-11
- Independent review timestamp: 2026-08-12T05:09:15+08:00
- Sign-off status: **PASS — conditional research framework only**
- Publishability score: **95/100**
- Open S-level findings: **0**
- Open A-level findings: **0**
- Gate outcomes: case-local verifier **105 PASS / 0 FAIL**; repository research gate **138 PASS / 0 FAIL — RESULT PASS**.

The final review is bound to reader-source SHA-256 `04ba969991bb6cb70e21da378ff4b1c93ea8dd100fc0dedf884f05260a55f94d`, source-graph SHA-256 `8dc0c58118162f8e456caf8ec025ed9312c5c900b97c5f3ee94af0a2c00302e4`, PDF SHA-256 `ece9c8436ca4117889587a17177251a1ba93cf3af945e05ecd75bb20098a50f9`, extracted-text SHA-256 `374cc0f1dd2c6b6fbb00aeedff324c6b93a094f03b4702508f34c3e9b360435b`, and all 14 A4 page images in `rendered/full-20260812-0457/`.

This PASS authorizes publication only as a conditional, educational research framework. It does not authorize a trade, validate suitability, set an execution price or quantity, or state that any ETF is currently eligible.

## What the independent review confirmed

1. **Evidence scope.** The current reader scope has 15 archived active materials—S01--S13 and S15--S16—and all 15 local payload hashes matched the two active manifests. S14, M01 and D01--D08 remain historical, retired records. Their unrecovered bytes were not recreated or described as recovered, and they cannot support an active target, allocation, valuation, cash or execution conclusion.
2. **Model arithmetic and actions.** The CNY200,000 model reconciles to CNY40,000 protected liquidity, CNY10,000 staging cash, CNY70,000 `511010`, CNY30,000 `510880`, conditional CNY30,000 `512890`, and CNY20,000 `518880`; public REITs and direct stocks are CNY0 at launch. The common-stress arithmetic is -16.30% / CNY32,600. Formula return parameter `r`, actual receipt ledger `D_0`, and observed account drawdown `DD_t` remain distinct.
3. **Control boundary.** The execution policy remains `not_run` and every ETF flag remains `q=0`. Any missing or failed field produces no trade and leaves only the affected amount in eligible protected liquidity; staging cash cannot exceed CNY10,000 and no substitute risk asset is inferred. `512890` additionally requires a dated combined-holdings, sector and issuer-group look-through.
4. **Reader and render quality.** The Chinese reader logic is coherent and contains no active direct-stock snapshot, historical-quote order proxy or unqualified return promise. The independent render review inspected all 14 final pages and found no clipping, overlap, table truncation, border breach, missing glyph or active-reader legacy-evidence leak. The single recorded cover-page underfull box has no visible effect.

## Continuing constraints (not publication blockers)

- Execution-day market, product, account and look-through records have deliberately not been produced. This means `q=0`, not that a gate has passed.
- Any future implementation requires a fresh current-session packet, account/suitability review and the policy controls in `data/execution_eligibility_policy_20260812.json`.
- Any change to the active evidence scope, reader-source graph, target model or PDF requires a new R0--R4 cycle.

## Historical checkpoint treatment

Earlier 17-page author-build records and pre-retirement review notes remain retained for audit history only. They do not override this hash-bound 14-page independent sign-off.
