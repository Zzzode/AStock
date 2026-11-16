# Artifact Contract

| Artifact | Stage | Minimum field-level requirement | Blocking condition | Review |
|---|---|---|---|---|
| `research_brief.md` | Intake | Frozen 10+2 universe, cutoff, custom product pack and downgrade | An unnamed category is treated as a researched product | R0 |
| `data/product_universe_20260812.*` | Intake | ID, role, product-specific evidence modules and q boundary | A legacy product is omitted or 508096 retains an obsolete identity | R0 |
| ETF raw/verified/look-through packets | Evidence | Mandate, benchmark, holdings, NAV/assets, performance, distribution and limitations | Index label substitutes for dated holdings or Q2 is called audited | R0 |
| REIT raw/verified/project/look-through packets | Evidence | Rights, projects, operators, dated financial/cash/NAV fields and risks | Historical distribution is converted to a forward yield | R0 |
| Market raw/verified packets | Evidence | Same-session source, timestamp, last/volume/amount/OHLC and gaps | A one-day snapshot is called executable liquidity | R0 |
| Source registry / atomic manifest / claim audit / exhaustion log | Evidence | Claim-to-source IDs, authority, document date, period, atomic relative path, SHA-256, limitation and probe record | Weak source upgraded, bundle-only citation or material claim unresolved | R0 |
| Broker catalog / consensus / analysis | Evidence | One product disposition per ticker; source quality and zero-weight gaps | Snippet or repost is called Street consensus | R0 |
| Return and cash control model | Model | TWRR/MWRR, receipt definition, no-double-counting and blocked gates | The 5%/3% objectives become a promise or projection | R1 |
| Product valuation model / audit | Model | Dated price and NAV diagnostic, method, mismatch, target disposition | A dated mismatch becomes a current valuation call | R1 |
| Overlap / selection / cash / liquidity analyses | Model | Common risks, caps, cash boundary, current execution fields and q decision | A label supplies diversification, cash or capacity proof | R1 |
| House view / variant / risk | Model | Testable thesis, opposing case, invalidation and risk hierarchy | Promotional conclusion or hidden evidence gap | R1 |
| Template / exhibit / narrative plan | Draft | Decision dashboard, required product-card exhibits and source mapping | Decorative exhibit implies untested performance | R2 |
| `main.tex` + sections | Draft | All products, product economics, valuation boundary, q=0, glossary | Missing product or implied allocation authorization | R2 |
| PDF, provenance, visual review | Render | XeLaTeX build, hashes, extracted text, page review | Stale/non-XeLaTeX/unreviewed artifact | R3 |
| R0–R4 findings / repair plans / sign-off | Review | Closed findings, maker-checker evidence and implementation block | Open S/A finding or generic PASS | R4 |

The machine-readable field contract is [artifact_contract.json](artifact_contract.json). Each row specifies ownership, `required_fields`, `minimum_depth`, `blocking_conditions`, review cycle and verifier check; it is the authority if this summary conflicts with the JSON.
