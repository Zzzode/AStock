# R2 H1/H3 official data-readiness raw sample

This directory retains fifteen small, read-only Shanghai Stock Exchange response bodies captured on 2026-08-14.  They are field-level availability evidence only.

The sample demonstrates that selected SSE routes returned limited report-index, corporate-action, suspension, public-REIT NAV/distribution/disclosure, ETF PCF/snapshot/disclosure, and convertible terms/price/disclosure metadata.  It does not demonstrate a complete population, PIT `available_at`, source versioning, revision lineage, data rights, historical replay readiness, or execution feasibility.

`manifest.json` is the authoritative integrity record.  It records the query parameterization, retrieval time, observed fields, byte size, and SHA-256 for every retained response.  No PDF was downloaded or interpreted in this probe.

Research-only boundary: quantity is zero.  These files cannot support product admission, allocation, holding, trading, order, or performance conclusions.
