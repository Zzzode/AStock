# Customer Annual Risk Disclosure Recheck

**Run date:** 2026-06-18

**Purpose:** Recheck latest customer annual-report / SEC-style risk disclosures for named cloud and hardware customers to see whether primary filings disclose supplier concentration, PCB/substrate suppliers, product allocation, revenue split or bottom-up model variables.

**Raw archive:** `sources/probe-customer-annual-risk-disclosures-20260618/`

**Boundary:** These annual reports provide primary-source supply-chain risk, contract-manufacturer and infrastructure commitment evidence. They do not disclose named PCB/CCL/substrate suppliers, customer/platform revenue, ASP, shipments, order values, margins or EPS assumptions.

## Archived Source Files

| Issuer / customer | Archived filing | Extracted text / excerpts | Incremental evidence |
|---|---|---|---|
| Apple | `apple-2025-10k.html` | `apple-2025-10k.txt`; `apple-2025-10k-supplier-risk-excerpts.txt` | Single/limited-source component risk; outsourcing partners in China mainland, India, Japan, South Korea, Taiwan and Vietnam; single-source partners for many components; manufacturing purchase obligations of USD56.2bn. |
| Amazon | `amazon-2025-10k.html` | `amazon-2025-10k.txt`; `amazon-2025-10k-supplier-risk-excerpts.txt` | Significant suppliers and limited/single-source supply risk; electronic device components from suppliers; several contract manufacturers; non-cancellable purchase commitments for device components. |
| Alphabet / Google | `alphabet-2025-10k.html` | `alphabet-2025-10k.txt`; `alphabet-2025-10k-supplier-risk-excerpts.txt` | AI infrastructure uses GPUs and custom TPUs; technical infrastructure includes servers, network equipment and data centers; purchase commitments of USD149.1bn, mostly technical infrastructure and inventory orders; contract manufacturers for technical infrastructure and device assembly. |
| Meta | `meta-2025-10k.html` | `meta-2025-10k.txt`; `meta-2025-10k-supplier-risk-excerpts.txt` | Technical infrastructure scaling risk; third-party providers; supply-chain challenges; dependence on a small number of third-party manufacturers/components in some regions; no named PCB supplier fields. |
| Microsoft | `microsoft-2025-annual-report.html` | `microsoft-2025-annual-report.txt`; `microsoft-2025-annual-report-supplier-risk-excerpts.txt` | Datacenters depend on energy, networking supplies, servers, GPUs and other components; few qualified suppliers for certain server/device components; devices manufactured by third-party contract manufacturers; purchase commitments of USD109.953bn primarily related to datacenters. |
| Dell Technologies | `dell-submissions-CIK0001571996.json`; `dell-fy2026-10k-sec.html` | `dell-fy2026-10k-sec.txt`; `dell-fy2026-10k-alt.html` | SEC submissions API identified FY2026 10-K accession `0001571996-26-000008`; FY2026 10-K discloses supplier/contract-manufacturer structure, AI-optimized server revenue disaggregation, purchase obligations of USD18.8bn, and receivables from the three largest contract manufacturers. |

## Targeted Search Results

| Search target | Result |
|---|---|
| Relevant supplier names | No annual-report text hit for Victory Giant, Avary, Tripod, Unimicron, Dongshan, HannStar, Gold Circuit, Delton, Meiko, Mektec, Shennan or WUS. |
| PCB / printed circuit / substrate | No annual-report text hit that identifies a PCB, printed-circuit-board or substrate supplier for NVIDIA, Google, Amazon, Microsoft, Meta, Apple or Dell. |
| Revenue / platform allocation | No annual-report route discloses PCB/CCL/substrate revenue by named customer/platform, ASP, shipment, order value, gross margin or EPS inputs. |

## Interpretation

- This pass improves the customer-side primary-source boundary: latest annual reports confirm that the largest relevant customers acknowledge component, server, network-equipment, contract-manufacturer, limited-source and purchase-commitment risks.
- The disclosures support demand and supply-chain risk analysis but do not identify the PCB/CCL/substrate suppliers required for named-platform revenue split or customer/platform EPS modeling.
- The remaining requirement still needs direct company/customer/supplier confirmation, paid supply-chain/BOL/customer databases, or paid terminal/sell-side channel checks.

Machine-readable absence result: No material annual-report text hits for target PCB supplier names or PCB/substrate supplier disclosure.

Machine-readable remaining gap: Latest annual-report / SEC-style routes do not close named platform/customer revenue split, terminal-grade positioning/order flow, or customer/platform EPS model requirements.
