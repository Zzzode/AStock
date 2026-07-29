# Institutional Report Review and Repair — R5

- Case: `low-position-capital-layout-20260711`
- Review date: 2026-07-15
- Benchmark: JPM equity note / JPM Guide to the Markets / BlackRock BII / Vanguard outlook

## Initial Findings

### S-Level
1. Main body was a working-paper dump: 142-row audit table plus 142 formula blocks preceded the investment case, forcing decision content to page 69 and valuation to page 88.
2. Main chapters were table-led and contained untranslated English valuation labels, weakening Chinese reader-facing professionalism.
3. The report did not separate a reader-facing strategy note from the reproducibility ledger; it therefore met traceability but failed information architecture.

### A-Level
1. Chapter titles described process rather than making investment judgments.
2. The first chapter lacked explicit portfolio/monitoring behavior and did not distinguish validation models from event-driven observations.
3. Dense appendix tables repeated full rationale for every row, used overly small type, and left long English strings in reader-facing columns.
4. Source/reproduction page resembled an internal file-path inventory rather than a publication-grade provenance statement.
5. Several pages had excessive unused lower-page whitespace after short tables.

### B-Level
1. Cover metadata and subtitle were mechanical rather than a thesis tension.
2. Exhibit captions were generic and several tables did not give a post-exhibit “so what” synthesis.

## Repair Design

1. Rebuild the report as a two-layer product:
   - Main strategy report: decision, market state, valuation framework, focus names, risks, data boundary and provenance.
   - Appendices: full universe, 142-name valuation ledger, and priority-pool evidence upgrades.
2. Move full valuation formulas and row-level evidence to Appendix B while retaining the complete JSON/Markdown audit package.
3. Rewrite all main-body headers as investor questions/judgments and translate reader-facing process labels to Chinese.
4. Add action tiers, explicit upgrade/downgrade rules, sector-stage implications, valuation-method matrix and risk-monitoring framework.
5. Replace raw source path dumps with a controlled source hierarchy and coverage exhibit.

## Target Acceptance

- Main body must make the decision before the ledger.
- All 142 formulas and evidence rows remain in PDF appendices and structured audit files.
- No untranslated English prose in main body except formulas, ticker names and source-specific terms.
- No hard LaTeX diagnostics, no overfull boxes, and verifier/gates pass.

## Repair Verification

### Verified Closures

1. **Decision-first structure:** The reader-facing report is now organized as investment conclusion, market state, valuation discipline, focus names, risk monitoring, evidence boundary, and then three appendices. The 142-name candidate screen, full valuation ledger, and 39-name evidence bridge remain available after the main decision chapters.
2. **Actionability:** Chapter 1 now separates validated allocation, event validation, and valuation-discipline observations; each group has a distinct execution rule. Chapter 4 adds a side-by-side comparison of the three formal models rather than leaving readers to infer cross-name differences from prose.
3. **Valuation transparency:** The main body contains the probability-weighted target formula and method-family matrix. Appendix B retains the per-name denominator, LaTeX formula substitution, bear/base/bull outcome, probability value, evidence role, and monitoring logic for all 142 candidates.
4. **Reader-facing language:** `House`, `Street`, and `Exhibit` labels were removed from the reader-facing PDF and replaced with Chinese terms such as “本机构情景”, “市场一致预期”, and “图表”.
5. **Render quality:** Repeated long row rationale was moved to method-family explanations; Appendix B is more compact without dropping formulas. The isolated disclaimer page was merged into the evidence-boundary chapter. All hard XeLaTeX diagnostics and all Overfull boxes were eliminated in the two-pass release build.
6. **Governance alignment:** The case verifier now checks the decision-first main-body structure, auditable appendix ledger, reader-facing language boundary, and explicit pre-listing boundary instead of obsolete workpaper headings. Review findings and repair plans record these closures rather than returning an empty PASS payload.

### Residual Boundaries

- The report is a full-market strategy and valuation refresh, not a substitute for an independent company deep dive before stronger single-name action language.
- Industry daily/weekly flow coverage is complete at 31/31, but observed through 2026-07-14 and the week ending 2026-07-10; continuous-flow coverage remains partial at 30/112.
- Broker PDF coverage is 138/142. Weak or stale sources remain zero-weight and cannot be presented as market-consensus valuation anchors.
