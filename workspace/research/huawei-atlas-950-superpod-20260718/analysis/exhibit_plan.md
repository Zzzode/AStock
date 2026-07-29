# Exhibit Plan

## Decision Rule

Use tables for exact status/valuation mappings and Mermaid only for architecture or evidence-flow diagrams. Every exhibit must answer a decision question, carry a source note, preserve roadmap versus historical status, and avoid unsupported market-share graphics.

| ID | Chapter | Decision question | Format | Data source | Key conclusion | Failure mode avoided |
|---|---|---|---|---|---|---|
| E01 | IC summary | Which names combine relationship evidence and valuation headroom? | Ranked table | current valuation model; claim audit | No name combines confirmed Atlas order with low valuation | Concept-list ranking |
| E02 | Evidence | What evidence admits a claim into valuation? | Claim/evidence matrix | source registry; claim audit | Supplier/order claims require primary product, order and economics evidence | Rumor upgrade |
| E03 | Industry | What is physical, roadmap or predecessor? | Product status table | Huawei H1-H4 | 1,024 physical; 8,192 roadmap | Status conflation |
| E04 | Industry | How do competing scale-up architectures differ? | Comparison table | Huawei/NVIDIA/AMD official | Card count is not a normalized benchmark | Vendor-number comparison |
| E05 | Supply chain | Which of eight AIDC blocks are mapped and what remains unknown? | Eight-block table | full-chain universe | All blocks covered; Atlas supplier allocation not disclosed | Listed-stock-only scope |
| E06 | Companies | Which companies have historical earnings support? | Financial/valuation table | verified financials; valuation model | Broad AIDC earnings exist but Atlas credit remains zero | Double-counted revenue |
| E07 | Street | How strong is external forecast coverage? | Consensus table | 38 original PDFs | Forecasts are usable; explicit targets are sparse | Invented Street target |
| E08 | Valuation | What are bear/base/bull and final targets? | Valuation table | current valuation JSON | Low-purity names screen cheaper; higher-linkage names are expensive | Price-free thematic view |
| E09 | Risk | What would invalidate the thesis? | Risk matrix | risk framework | Roadmap, yield, topology, order and valuation risks are measurable | Generic risk paragraph |
| E10 | Appendix | Is the full chain complete? | 50-node long table | full-chain universe JSON | Every node has classification and evidence state | Omitted unavailable nodes |

## Layout Rules

- Prose precedes the first major table in supply-chain and valuation chapters.
- No chart uses an unsupported TAM, CR3/CR5 or Atlas company revenue estimate.
- Repeated disclaimer text is kept in the cover, valuation chapter and appendix only.
- Tables use concise labels and no reader-facing English full sentences.
- Any future architecture diagram must originate from a `.mmd` Mermaid source and be rendered to a report-local image.
