# Gate Manifest

| Field | Control |
|---|---|
| Case / cutoff | `income-strategy-product-due-diligence-20260812`; 2026-08-12 market snapshot, 2026-06-30 routine reporting cutoff |
| Report type | Strategic-allocation product due-diligence evidence memo |
| Coverage pack | `custom_income_etf_public_reit_liquidity_products_v1` |
| Covered universe | 511010, 510880, 512890, 508069, 508011, 508068, 508077, 508055, 508080, 508096; plus two explicitly unnamed categories |
| Required skills | `equity-research`, `reports`, `valuation`, `research-report-review`, `research-prose-polish`, `agent-resilience`, `exhibit-format-reviewer` |
| Review cycles | R0 evidence, R1 model, R2 draft, R3 render/compliance, R4 final IC |
| Publication state | Research-framework evidence memo only; implementation `NOT_APPROVED`, all market products `q=0` |

## Pre-publish depth checklist

- [x] Evidence depth — each named product has source-linked legal, exposure, financial/cash, market and limitation fields; S27/S28 bundles are resolved by the atomic manifest.
- [x] Product-structure depth — ETF benchmark/holdings and REIT project/operator/economics are displayed, not inferred from labels.
- [x] Model depth — total return, cash receipts, dated NAV diagnostics and date-mismatch controls are reproducible.
- [x] Valuation depth — no current fair-value or target-price assertion appears without same-date valuation inputs and a valid method bridge.
- [x] Broker-consensus depth — source quality, unavailable fields and zero valuation weights are explicit.
- [x] IC readiness — common-factor risk, liquidity limits, categories without an identity, account/tax/suitability and q=0 boundaries are reader-facing.
- [ ] Render / provenance — refresh after the final source freeze and XeLaTeX rebuild.

The machine-readable authority is [gate_manifest.json](gate_manifest.json). The checklist is deliberately not marked complete until the related artifacts and independent review records exist.
