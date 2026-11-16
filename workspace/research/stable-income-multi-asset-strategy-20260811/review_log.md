# Review Log — Stable-Income Multi-Asset Strategy

## Historical pre-final disposition

- Scope ID: `strategic-allocation-etf-first-v2-20260811`
- Historical pre-final score: 15/100
- Status: BLOCKED — this was the pre-final-recompile state before the current hash-bound independent R0--R4 review.
- Data cutoff: 2026-08-11.
- Scope: fixed-CNY200,000 strategic allocation; zero initial direct-stock and REIT weights; no individual security target price, order instruction or fixed cash-distribution forecast.

## Current final disposition — 2026-08-12T05:09:15+08:00

- Publishability Score: **95/100**
- Status: **PASS — conditional research framework only**
- Open S-level findings: **0**; open A-level findings: **0**.
- Gate outcomes: case-local verifier **105 PASS / 0 FAIL**; repository research gate **138 PASS / 0 FAIL — RESULT PASS**.
- Review identity: source `04ba969991bb6cb70e21da378ff4b1c93ea8dd100fc0dedf884f05260a55f94d`; graph `8dc0c58118162f8e456caf8ec025ed9312c5c900b97c5f3ee94af0a2c00302e4`; PDF `ece9c8436ca4117889587a17177251a1ba93cf3af945e05ecd75bb20098a50f9`; text `374cc0f1dd2c6b6fbb00aeedff324c6b93a094f03b4702508f34c3e9b360435b`; 14 rendered pages in `rendered/full-20260812-0457/`.
- This status does not authorize implementation. Execution remains `not_run` / `q=0`; a later use requires a current-session packet, account/suitability review and the `512890` combined-holdings check.

## Cycle record

| Cycle | Independent review focus | Findings | Current lifecycle | Result |
|---|---|---|---|---|
| R0 evidence | primary-source authority, claim scope, governance evidence | R0-S-001 to R0-S-003; R0-A-001 | active-source archive complete through scope retirement (15/15/0/0); legacy 21/1/3 bytes remain unrecovered and prohibited from active use | historical record requires lifecycle reconciliation; not an active-scope archive blocker |
| R1 model | annual-add arithmetic, active vectors, liquidity layers, cash-distribution mechanics, full scenario matrix, REIT limits | R1-S-001 to R1-S-004; R1-A-001 to R1-A-007 | the current model repair is author-fixed; final-source recompile and independent R1 re-read remain open | blocked |
| R2 draft | Chinese reader-facing action logic, capital boundary and model-portfolio actionability | R2-S-001, R2-A-002 to R2-A-003, R2-S-002, R2-S-003 | the model/prose/action-card repair is author-fixed; final-source recompile and independent R2 re-read remain open | blocked |
| R3 render/compliance | XeLaTeX build, text extraction and visual exhibits | R3-S-001; R3-B-002; R3-S-003 | the 04:20 17-page author-build checkpoint is historical only; final recompile, final render and independent R3 full-page review remain open | blocked |
| R4 final IC | issue closure and publication conditions | R4-S-001, R4-S-002 | no independent R4 sign-off has been issued for the current scope; all prior IC conclusions remain historical | blocked |

## Maker-checker boundary

The report author applied the documented repairs. Independent reviewers have re-read and verified earlier historical R0 claim-scope, R1 model and R2 source-level corrections, but those checks do not sign the active scope. The current model/prose repair has no independent R1 or R2 re-read; the final source/PDF/text/render identity is pending a source-scope recompile; and no independent R3 or R4 sign-off exists. The user-directed full-principal correction is separately documented in analysis/delta_audit.md and has independently passed its historical R1/R2 re-review. No S-Level finding is waived. No A-Level finding is waived.

## Remaining release blockers

1. The active-source archive is complete at 15 success / 0 partial / 0 failed after scope retirement. The historical 25-ID context remains 21 success / 1 partial / 3 failed, but its unrecovered raw bytes are retired and prohibited from active conclusions rather than represented as recovered.
2. The 04:20 author-build checkpoint records the completed model/prose repair. The source-scope retirement is now complete, so the active evidence package must be rebuilt and newly bound before independent R1/R2 reader checks and an independent R3 full-page inspection can be recorded.
3. The section 6.2 pagination note is resolved: its heading, setup and fixed-CNY200,000 amount table now co-locate on rendered page 10.
4. The remaining release blockers are final-source artifact identity, independent R1/R2/R3/R4 review, and an execution-day eligibility packet. The active archive is complete through scope retirement; the unrecovered legacy bytes remain prohibited from active use. macOS/MacTeX branding is not a blocker.

## Fixed-principal reparameterization — 2026-08-11

- The user replaced the earlier amount range with one fixed full investment principal of CNY200,000.
- The active model, reader-facing source, structured valuation record and governance contracts were reparameterized. The base core is CNY40,000/CNY10,000/CNY70,000/CNY30,000/CNY30,000/CNY20,000; REITs remain CNY0 unless up to CNY10,000 is transferred from rates after all gates pass.
- Independent R1/R2 review passed: the base total, CNY10,000 maximum REIT transfer, CNY4,000 per-name REIT cap, CNY32,600/CNY34,600 common stresses, CNY6,000 illustration and CNY80,000/CNY90,000 staged tranches all reconcile. R1-A-007 and R2-A-003 are verified; R3/R4 evidence remains to be refreshed.

## Scope transition — ETF-first rewrite, 2026-08-11

- Current scope ID: `strategic-allocation-etf-first-v2-20260811`.
- The earlier fixed-principal notes above are preserved as historical lifecycle evidence only. They do not verify the current reader source.
- The active source now starts direct stocks and REITs at 0%, treats direct-stock data as a non-decisive historical observation, removes the 4.73% point-return branch and uses a 3%--6% long-horizon planning sensitivity with actual $D_0$ cash records.
- Then-current disposition: **BLOCKED, 15/100**. This historical checkpoint was author-built only; it was superseded by the current independent R0--R4 review.
- Current review finding IDs: `R0-S-003`, `R1-S-004`, `R2-S-002`, `R2-S-003`, `R3-S-003`, and `R4-S-002`. No finding is waived.

## Source-archive remediation — 2026-08-11

- Three archive manifests now preserve 21 successful local originals with response headers and SHA-256 values: `sources/official-20260811/archive/s01-s08/`, `s09-s16/` and `m01-d01-d08/`.
- The R0 blocker remains open, not waived: S14 returned a WAF challenge, the original M01 GB18030 bytes were not retained, the D05 host was unreachable, and D07 lacks its final SSE PDF. Page/section locators and fresh independent R0 claim verification are also still required.

## Source-scope retirement — 2026-08-12

- The active strategy now excludes all historical direct-stock, futures and related non-decisive observations. Its active archive contains 15 complete records (S01--S13 and S15--S16): **15 success / 0 partial / 0 failed**.
- The prior 25-ID archive remains visible as historical context: **21 success / 1 partial / 3 failed**, with S14, M01, D05 and D07-final unrecovered. Those raw-byte gaps were not repaired or waived. They are retired from the active scope and cannot support an active target, allocation, valuation, cash or execution conclusion.
- This resolves the active-scope archive gate by narrowing the evidence scope, not by claiming primary-source recovery. Current release blockers are execution eligibility, final artifact identity and independent R1--R4 review.

## Platform-build policy correction — 2026-08-11

- The historical R3 record noted TeX Live 2022/Debian against a then-stated macOS/MacTeX requirement. That host requirement has been retired because CJK support requires XeLaTeX, packages and resolved fonts—not macOS or a branded distribution.
- The current release rule accepts XeLaTeX on a supported host only when the R3 evidence records host OS, executable path/version/distribution, selected CJK font, command, source/PDF hashes, page count and diagnostics. The old 15-page source does not become current evidence merely because the policy changed.

## Superseded current-source XeLaTeX build — 2026-08-12 00:10

- This earlier 18-page build is retained under `data/build_provenance_20260812.{md,json}` and `rendered/superseded-20260812-0010/`. It was superseded after the reader-facing model-target/action-card correction.

## Actionability-corrected XeLaTeX build — 2026-08-12 00:57

- The active source was compiled twice with `/usr/bin/xelatex` on Linux / TeX Live 2022/Debian using Noto Serif CJK SC and Noto Sans CJK SC.
- `main.pdf` is 18 A4 pages with SHA-256 `d485b96227d0caca0abcb79b263b7a26301ee2d4e0395cb6ad39f41227d93102`; its source SHA is `ff771a67bcefc9f1c22987f3115c6caca56c4dbc3c40aa91e79969e01f031a13` and graph SHA is `d208de98baeacae25ec56fcca51b2685aa45721c7c715f7f7880a255cacf7e55`.
- `main_current_text.txt` and `rendered/full-20260812-0057/` are identity-matched derived artifacts. Build diagnostics are clean; the author inspected the target/action and implementation-card pages 5, 6, 9, 10 and 15.
- The reader now designates CNY70,000 of 511010, CNY30,000 of 510880, conditional CNY30,000 of 512890, CNY20,000 of 518880, CNY40,000 protected liquidity and CNY10,000 staging cash, with REITs/direct stocks at CNY0. The 512890 amount remains deferred unless the combined-holdings test passes.
- This is not independent R2 or R3 evidence. `R2-S-003` and `R3-S-003` remain unresolved until independent reviewers record hash-linked results.

## Comprehensive model/prose repair checkpoint — 2026-08-12 04:20

- The author completed a comprehensive repair of model boundaries, source boundaries, Chinese prose and pagination. The resulting historical checkpoint was a 17-page A4 `main.pdf` with SHA-256 `86ac768d39f425aa116c4ef8fac2492b5c192329bfe00935826be5b68cea5440`, text SHA-256 `adcab61e68a792b427fd04ad5be09c98d25637297624980816402eb51fc26a2d`, and 17-page render set `rendered/full-20260812-0420/`.
- The two-pass XeLaTeX diagnostics recorded zero fatal errors, undefined-control-sequence errors, missing-character records and `Overfull \\hbox` records; one benign cover-page `Underfull \\hbox` remained. This was author build/visual-QA evidence, not an independent sign-off.
- The subsequent source-scope retirement is complete, so this checkpoint is preserved as history only. It must not be used as the immutable active identity or as a replacement for a final recompile, R1/R2/R3/R4 review or execution-day validation.
- Then-current release state: **BLOCKED, 15/100**. This historical author checkpoint has been superseded by the current conditional-research PASS; execution remains `not_run` with all ETF `q=0` and is not a trading instruction.

## Final independent R0--R4 review — 2026-08-12T05:09:15+08:00

| Cycle | Independent evidence checked | Result |
|---|---|---|
| R0 | 15 declared active payloads, two manifests, source-scope retirement and claim boundaries | PASS — all active hashes matched; unrecovered historical bytes remain retired and unusable. |
| R1 | CNY200,000 target total, caps, q-gate/fallback, `r`/`D_0`, stress and observed `DD_t` logic | PASS — no active model inconsistency. |
| R2 | Full Chinese reader graph, structured implementation packet and non-authorization disclosures | PASS — named model targets/actions are conditional and no historical quote becomes a trade instruction. |
| R3 | Current source/PDF/text/render identity and all 14 rendered pages | PASS — no visible rendering defect or legacy-evidence leak. |
| R4 | Current lifecycle, sign-off and workflow records | PASS — conditional research publication only, 0 open S / 0 open A. |

No S-level or unwaived A-level issue was waived. Current-session execution evidence was not fabricated or inferred: the implementation state remains `not_run` / `q=0`, which is a deliberate non-authorization constraint rather than a report-quality defect.
