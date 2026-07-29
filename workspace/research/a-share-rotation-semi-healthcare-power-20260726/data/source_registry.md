# Source Registry

## Source-quality policy

- `primary_official`: issuer, regulator, exchange or index-provider original record; may support only the fields actually disclosed.
- `original_pdf`: archived dated sell-side report; useful for attributed market framing, but company model fields require the report to show them.
- `secondary_low`: media repost or AI-generated/secondary page; discovery lead only and never valuation evidence.

| Source ID | Local path | Publisher / date | Type / quality | Admissible use | Material limitation |
|---|---|---|---|---|---|
| SRC-01 | `sources/official-policy-20260726/202312-CSI-931743-semiconductor-material-equipment-methodology.pdf` | CSI, 2023-12 | primary_official | Semiconductor equipment/materials universe definition | Not company exposure, flow or earnings evidence |
| SRC-02 | `sources/official-policy-20260726/202310-CSI-931723-optical-communication-methodology.pdf` | CSI, 2023-10 | primary_official | Optical-communication comparison universe | Includes telecom/data-center links; not a pure optical-module or PCB basket |
| SRC-03 | `sources/official-policy-20260726/202408-SSE-950161-star-innovative-drug-methodology.pdf` | SSE / CSI, 2024-08 | primary_official | STAR innovative-drug universe definition | No BD contract or earnings evidence |
| SRC-04 | `sources/official-policy-20260726/20260130-CSI-931932-power-equipment-factsheet.pdf` | CSI, 2026-06-30 | primary_official | Power-equipment universe and static factsheet | Not the 2026-07-24 market close or company order evidence |
| SRC-05 | `sources/official-policy-20260726/20260726_gsk_hengrui_licensing_announcement.html` | Hengrui / GSK, archived 2026-07-26 | primary_official | Contract terms only where expressly disclosed | Do not treat headline consideration as recognized profit |
| SRC-06 | `sources/official-policy-20260726/20260726_innovent_2025_annual_results.pdf` | Innovent, FY2025 results | primary_official | Issuer reported financial and pipeline context | Not a sector-wide BD proxy |
| SRC-07 | `sources/official-policy-20260726/20260726_nea_2026h1_power_statistics.html` | National Energy Administration, 2026H1 | primary_official | Power-system demand context | Does not prove equipment-company orders or margin |
| SRC-08 | `sources/official-policy-20260726/20260726_nea_2026_power_regulation_notice.html` | National Energy Administration, 2026 | primary_official | Policy / regulatory context | Policy is not earnings conversion |
| SRC-09 | `sources/official-policy-20260726/20260726_sec_amat_fy2025_10k.html` | Applied Materials, FY2025 10-K | primary_official | Overseas equipment reference / industry context | Not China A-share revenue evidence |
| SRC-10 | `sources/official-policy-20260726/20260726_sec_acmr_2025q3_10q.html` | ACM Research, 2025 Q3 10-Q | primary_official | Overseas equipment reference / industry context | Not China A-share revenue evidence |
| SRC-11 | `sources/broker-reports/2026-07-26/01-cinda-semicon-china-equipment-materials-20260329.pdf` | Cinda Securities, 2026-03-29 | original_pdf | Attributed semiconductor sector framing | No standardized ticker targets / forecasts in this case |
| SRC-12 | `sources/broker-reports/2026-07-26/02-boc-electronics-2025a-2026q1-review-20260512.pdf` | BOC International, 2026-05-12 | original_pdf | Attributed sector operating-trend view | Aggregate industry review, not company consensus |
| SRC-13 | `sources/broker-reports/2026-07-26/03-dongguan-semi-2025a-2026q1-review-20260522.pdf` | Dongguan Securities, 2026-05-22 | original_pdf | Attributed semiconductor sector framing | No usable core-ticker valuation fields |
| SRC-14 | `sources/broker-reports/2026-07-26/04-dongwu-ai-interconnect-pcb-cpo-20260225.pdf` | Dongwu Securities, 2026-02-25 | original_pdf | PCB/CPO candidate discovery and attributed sector view | Named companies are not a target-price consensus set |
| SRC-15 | `sources/broker-reports/2026-07-26/05-kaiyuan-innovative-drugs-globalization-20260208.pdf` | Kaiyuan Securities, 2026-02-08 | original_pdf | Innovative-drug BD theme discovery | Every transaction requires issuer-level confirmation |
| SRC-16 | `sources/broker-reports/2026-07-26/06-guojin-innovative-drug-bd-20260517.pdf` | Guojin Securities, 2026-05-17 | original_pdf | Innovative-drug watch-list discovery | Not an initiation or comparable forecast set |
| SRC-17 | `sources/broker-reports/2026-07-26/07-kaiyuan-innovative-drug-global-cooperation-20260628.pdf` | Kaiyuan Securities, 2026-06-28 | original_pdf | Recent BD leads | Terms require primary verification |
| SRC-18 | `sources/broker-reports/2026-07-26/08-dongwu-power-equipment-fund-holdings-20260427.pdf` | Dongwu Securities, 2026-04-27 | original_pdf | Sector positioning discussion | Not an order, earnings or target-price model |
| SRC-19 | `sources/broker-reports/2026-07-26/09-huajing-phoenix-tech-300480-20260329.pdf` | Huajin Securities, 2026-03-29 | original_pdf | Single-broker historical forecast fields for 300480 only | No target price / method; not Street consensus |
| SRC-20 | `sources/official-policy-20260726/20260129-sina-public-fund-stock-exposure-secondary.html` | Sina page, 2026-01-29 | secondary_low | Discovery lead concerning a claimed 88% threshold | Page is AI-labelled and lacks auditable sample/method; zero use |
| SRC-21 | `sources/official-policy-20260726/20260723-sina-public-fund-ai-5857-secondary.html` | Sina repost, 2026-07-23 | secondary_low | Discovery lead concerning 58.57% claim | No disclosed fund universe, classification or calculation; zero use |
| SRC-22 | `sources/broker-reports/2026-07-26/10-zhaoshang-semicon-autonomy-preview-20260515.md` through `13-citic-innovative-drug-media-repost-20260706.md` | Public previews / reposts, 2026 | secondary_low | Search audit only | No valuation or consensus use |
| SRC-23 | `sources/official-policy-20260726/20260726_nea_2025_energy_conditions_release.html` and `20260726_nea_2025_energy_investment_release.html` | National Energy Administration, 2026-01-30 | primary_official | 2025 energy / grid demand context | Macro project investment is not supplier order, margin or cash evidence |
| SRC-24 | `sources/official-policy-20260726/20260726_nea_power_system_pilots.html` | National Energy Administration, 2026-02 | primary_official | New power-system pilot context | A pilot does not prove tender award, delivery or profit |
| SRC-25 | `sources/official-policy-20260726/CAPTURE_INDEX.md` | Case source index, 2026-07-26 | derived_index | Provenance pointer for the above primary captures | Does not create independent factual evidence |

## Admissibility summary

- The registry contains primary context, original sell-side sector material and explicitly downgraded secondary leads.
- No registered source currently validates the article's Tuesday-flow assertion, 88% public-fund exposure, or 58.57% AI-position number.
- No registered broker corpus provides the complete comparable target-price / forecast set required for a core valuation universe. This blocks final core selection until ticker-level collection and verification are complete.
