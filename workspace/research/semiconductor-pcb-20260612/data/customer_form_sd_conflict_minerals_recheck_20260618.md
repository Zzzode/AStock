# Customer Form SD Conflict Minerals Recheck

**Run date:** 2026-06-18

**Purpose:** Recheck latest SEC Form SD / Conflict Minerals Report routes for key customer-side companies to determine whether primary 3TG due-diligence filings disclose PCB/CCL/substrate supplier identities, product allocation, revenue split or bottom-up EPS model variables.

**Raw archive:** `sources/probe-customer-form-sd-20260618/`

**Boundary:** Form SD filings provide responsible-minerals due-diligence evidence, supplier survey mechanics, CMRT response rates and smelter/refiner lists. They do not disclose named PCB/CCL/substrate suppliers, platform revenue, ASP, shipment, order value, margin or EPS assumptions.

## Archived Source Files

| Issuer / customer | Archived route | Extracted text | Incremental evidence |
|---|---|---|---|
| Apple | `apple-2025-form-sd.html` | `apple-2025-form-sd.txt` | Apple relies on the 2017 SEC statement and does not file a full Conflict Minerals Report, but states that 100% of identified 3TG smelters/refiners in Apple's supply chain are required to participate in annual third-party audits. Apple requires suppliers using 3TG in iPhone, Mac, iPad, AirPods, Apple TV, Apple Watch, Apple Vision Pro, Beats, HomePod and accessories to submit CMRTs. |
| Amazon | `amazon-2025-form-sd.html`; `amazon-2025-form-sd-ex101.html` | `amazon-2025-form-sd.txt`; `amazon-2025-form-sd-ex101.txt` | Amazon completed analysis for suppliers of electronic devices, fashion/apparel and other consumer products; uses RMI CMRT; identifies no suppliers sourcing minerals through a supply chain that benefited armed groups in the DRC region, while some suppliers are still determining country-of-origin/facility data. |
| Alphabet / Google | `alphabet-2025-form-sd.html` | `alphabet-2025-form-sd.txt` | Alphabet Form SD points to an Exhibit 1.01 Conflict Minerals Report available through Alphabet investor ESG materials. The archived SEC cover confirms the reporting route; the static filing does not itself expose PCB supplier or platform revenue fields. |
| Meta | `meta-2025-form-sd.html`; `meta-2025-form-sd-ex101.html` | `meta-2025-form-sd.txt`; `meta-2025-form-sd-ex101.txt` | Meta Form SD and exhibit were archived from SEC. They provide conflict-minerals due-diligence context but do not identify target PCB suppliers or revenue/model variables. |
| Microsoft | `microsoft-2025-form-sd.html`; `microsoft-2025-form-sd-ex101-own.html` | `microsoft-2025-form-sd.txt`; `microsoft-2025-form-sd-ex101-own.txt` | Microsoft surveyed 79 Devices direct suppliers with a 100% CMRT response rate; identified 266 eligible 3TG smelters/refiners; 31 SORs sourced from Covered Countries and all 31 were conformant; Microsoft found no reasonable basis that any SOR financed or benefited armed groups. |
| Dell Technologies | `dell-2025-form-sd.html`; `dell-2025-form-sd-ex101-own.html` | `dell-2025-form-sd.txt`; `dell-2025-form-sd-ex101-own.txt` | Dell covered branded hardware, peripherals, server, storage and networking products; 100% of in-scope suppliers provided CMRTs; 245 unique 3TG smelter/refiner facilities were identified; 219 were conformant as of Dec. 31, 2025; 31 were known to source from DRC/adjoining countries and all were conformant. |
| NVIDIA | `nvidia-2025-form-sd.html`; `nvidia-2025-form-sd-ex101.html`; `nvidia-submissions-CIK0001045810.json` | `nvidia-2025-form-sd.txt`; `nvidia-2025-form-sd-ex101.txt` | NVIDIA discloses a fabless and contract-manufacturing strategy, notes memory, substrates and components, surveyed 164 direct suppliers, received 100% in-scope supplier responses, identified 246 processing facilities, 31 Covered-Country smelters/refiners and 206 RMAP-compliant facilities. |

## Route Notes

- Alphabet external page probe: `alphabet-conflict-minerals-page.html` returned HTTP 403 from the `abc.xyz` investor ESG conflict-minerals route, and public search did not recover a direct report page. The SEC Form SD cover remains archived, but the external report body is not available through this public route.

- `amazon-submissions-CIK0001018724.json`, `alphabet-submissions-CIK0001652044.json`, `meta-submissions-CIK0001326801.json`, `microsoft-submissions-CIK0000789019.json` and `dell-submissions-CIK0001571996.json` were archived to resolve current Form SD accessions.
- `microsoft-2025-form-sd-ex101.html` was downloaded from a public search result but is an Intel filing, not Microsoft. It is retained as a raw misroute artifact and excluded from conclusions. The valid Microsoft exhibit is `microsoft-2025-form-sd-ex101-own.html`.

Machine-readable excluded-artifact reason: Downloaded from search result but is an Intel filing, not Microsoft; retained as raw misroute artifact and excluded from conclusions.

## Targeted Absence Checks

| Search target | Result |
|---|---|
| PCB supplier names | No Form SD text hit for Victory Giant, Avary, Tripod, Unimicron, Dongshan, HannStar, Gold Circuit, Delton, Meiko, Mektec, Shennan or WUS as customer PCB/CCL/substrate suppliers. |
| PCB / printed circuit / substrate fields | No Form SD route discloses customer PCB/CCL/substrate supplier identity or product-platform allocation. |
| Model fields | No Form SD route discloses revenue split, ASP, shipment, order value, margin, depreciation, working capital or EPS inputs. |

## Interpretation

- This pass removes another primary-source route from the uncollected bucket: customer-side Form SD / conflict-minerals reports are archived and searched.
- The filings improve responsible-minerals and supplier due-diligence context, especially Microsoft and Dell supplier response-rate and smelter/refiner counts.
- The hard blockers remain unresolved because Form SD operates at the 3TG smelter/refiner and supplier-survey level, not at PCB/CCL/substrate supplier revenue or customer-platform model level.

Machine-readable absence result: No customer Form SD route discloses target PCB supplier names, PCB/substrate product allocation, revenue split, ASP, shipment, order value, margin or EPS assumptions.

Machine-readable remaining gap: Form SD / Conflict Minerals Report routes, including NVIDIA, do not close named platform/customer revenue split, terminal-grade positioning/order flow, or customer/platform EPS model requirements.
