# Skill Evolution Log

## 2026-08-11 — Portable XeLaTeX/CJK build rule

- Trigger: the user challenged the macOS-only render requirement while the active source and preamble already support Linux XeLaTeX with Noto CJK fonts.
- Root cause: `AGENTS.md`, mirrored research skills and the case-local R3 verifier converted a CJK/XeLaTeX requirement into a macOS/MacTeX brand requirement. The verifier checked a literal phrase rather than technical provenance.
- Change: consolidate the repository policy around XeLaTeX on any supported host; retain XeLaTeX as the engine requirement; make macOS `/Library/TeX/texbin` an optional discovery fallback; require R3 provenance for host, engine path/version/distribution, CJK font, command and artifact identity.
- Case control update: the current-scope R3 finding and verifier now require XeLaTeX provenance rather than `macOS MacTeX XeLaTeX` text.
- Regression evidence: Linux preflight found `/usr/bin/xelatex`, `ctexrep.cls`, `xeCJK.sty`, Noto Serif/Sans CJK SC and built reader-source SHA `b7756913ec376f7b6262bfd215490aa2e9751f555f97055b019ce08933d7faf7` (graph SHA `187ed27fbd7b473e6c352e8f911eed6c296b00bf0ba884dcffe540f8c28b6cc5`) twice into an isolated output directory. The output was an 18-page A4 PDF (SHA `27d838031f86ac92a4e76a4bd0cb63dc9a232ef186dfeac0d9c82c10c2d7c630`); it is not release evidence because it was isolated and reported an `Overfull \\hbox` diagnostic of 76.82506pt.
- Residual release state: BLOCKED. The policy change removes the false host constraint only; source archival, durable current artifact identity, diagnostic repair and independent R0--R4 review remain open.

## 2026-08-12 — Superseded current-source portable build evidence

- The long `\\texttt{...}` paths in `sections/app_sources.tex` caused a 76.82506pt `Overfull \\hbox` in the isolated preflight. They were changed to breakable `\\nolinkurl{...}` paths; no shared template was changed for that repair.
- The active source was then built twice with Linux XeLaTeX / TeX Live 2022/Debian and resolved Noto CJK fonts. This former artifact is now superseded after the reader-facing model-target/action-card revision; it is archived under `rendered/superseded-20260812-0010/`.
- The report-local footer was cleared in `main.tex` so the disclaimer no longer overlaps the page number. It remains present in the final disclosure.
- Residual release state: BLOCKED. This historical build does not release the revised source.

## 2026-08-12 — Allocation-strategy actionability feedback

- Trigger: the user correctly challenged a report called a configuration strategy that did not state what the model actually owns or what the model does first.
- Failure mode: the reader-facing TeX supplied asset sleeves and CNY amounts, but treated 511010, 510880, 512890 and 518880 only as representative examples. The detailed map was isolated in `analysis/product_universe.md`, leaving no reader-facing instrument, sequence, fallback or action card.
- Root cause: the strategic-allocation artifact contract required sleeve vectors, caps and gates, but did not require per-sleeve designated implementation, staged action and fallback. The first-chapter equity-research actionability requirement was not bound into this case's contract.
- Case repair: `data/model_portfolio_implementation_20260812.{md,json}` now declares model targets, and the reader source names the instruments, CNY targets, six-month actions and gate-failure destinations. The repair does not convert the dated M01 quote into a live order; 512890 remains conditional on a current combined-holdings check.
- Prompt/skill change: **not applied**. The user asked for a report correction, not a skill/prompt edit. Proposed prevention rule is recorded in `analysis/delta_audit.md` pending explicit approval.
- Regression proposal: a strategic-allocation case must fail an actionability test if an active sleeve lacks a reader-facing designated instrument (or explicit cash/deposit implementation), target notional, staged action, validation gate and fallback destination.
- Residual release state: BLOCKED. The author repair needs an independent R2 read, a current R3 render review, and the pre-existing evidence gates remain open.

## 2026-08-12 — Actionability-corrected build evidence

- The actionability repair was compiled twice with Linux XeLaTeX / TeX Live 2022/Debian and resolved Noto CJK fonts. The durable current artifact is `main.pdf`: 18 A4 pages, SHA-256 `d485b96227d0caca0abcb79b263b7a26301ee2d4e0395cb6ad39f41227d93102`.
- Source identity is SHA-256 `ff771a67bcefc9f1c22987f3115c6caca56c4dbc3c40aa91e79969e01f031a13` (graph `d208de98baeacae25ec56fcca51b2685aa45721c7c715f7f7880a255cacf7e55`); matched extracted text and 18 rendered pages are retained. The recorded build diagnostics have no fatal, undefined-control-sequence, missing-character or overfull record.
- The author inspected physical pages 5, 6, 9, 10 and 15, which contain the reader-facing target/action, designated-instrument, staged-allocation and implementation cards; no clipping, overlap or table truncation was observed.
- Residual release state: BLOCKED. The build is author evidence only; independent R2/R3 review, primary-source archival and fresh R0--R4 closure are still required.
