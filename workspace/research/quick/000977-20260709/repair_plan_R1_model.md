# Repair Plan R1 Model

Status: open

1. Create missing structured growth and supply-chain artifacts:
   - data/growth_driver_model.json
   - data/supply_chain_relationships.md/json
   - data/customer_chain_audit.md/json
   - analysis/value_chain_economics.md
   - analysis/chain_earnings_bridge.md

2. Create source governance closure:
   - source_exhaustion_log.md/json

3. Fix broker evidence weighting:
   - Set media_repost and third_party_aggregate broker rows to valuation_weight 0.
   - Keep original PDFs as positive-weight Street evidence.

4. Repair render issues:
   - Remove Overfull hbox >20pt warnings.
   - Improve tables that wrap labels awkwardly in the PDF.

5. Rebuild and rerun review:
   - Build report.pdf with XeLaTeX.
   - Rerun log scan and PDF text scan.
   - Close findings only after evidence confirms fixes.
