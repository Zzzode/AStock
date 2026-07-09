# Gate Manifest

case_id: 000977-20260709
report_type: single-stock full note
data_cutoff: 2026-07-09 11:51 Asia/Shanghai
coverage_pack: AIDC

Required skills and gates:
- equity-research: PASS
- supply-chain-research: CONDITIONAL PASS for single-stock AIDC mapping
- growth-earnings-model: PASS with H1 preannouncement bridge
- valuation: PASS with current-price-based target
- research-report-review: self-review completed, no open blocking issue

Required artifacts:
- research_brief.md
- gate_manifest.md/json
- artifact_contract.md/json
- data/source_registry.md/json
- data/claim_audit.md/json
- source_exhaustion_log.md/json
- data/broker_street_consensus_20260709.md/json
- analysis/supply_chain_model.md
- analysis/growth_earnings_model.md
- analysis/segment_forecast_bridge.md
- analysis/implied_growth_sensitivity.md
- analysis/valuation_model.md
- analysis/valuation_audit.md
- analysis/house_view.md
- analysis/variant_perception.md
- report.tex
- report.pdf

Depth gates:
- evidence_depth: original broker PDFs plus local official filing pack and live data packet
- broker_consensus_depth: two original PDFs after H1 preannouncement plus public target aggregates
- model_depth: H1 preannouncement, Q2 implied profit, broker forecast reset, cash-flow stress
- valuation_depth: current price, share count, market cap, 2026E EPS, scenario PE, broker anchor, sentiment anchor
- ic_readiness: action, target, catalysts, invalidation, position discipline included

Pass conditions:
- No unsupported target price.
- H1 preannouncement must be the primary denominator.
- Broker target trend must be discussed separately from absolute target price.
- Institutional holdings / National Team / style classification must be included.
- PDF must compile with XeLaTeX through astock build-pdf.

Downgrade path:
- If Q2 profit does not continue into H2, action downgrades to watchlist only.
- If operating cash flow stays negative with receivable/inventory expansion, fair-value range shifts to bear/base.
- If upstream accelerator supply is constrained, remove bull case.
