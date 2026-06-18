# Cloud Customer Supplier Disclosure Recheck

**Run date:** 2026-06-17

**Purpose:** Recheck whether Google, Microsoft, Amazon/AWS or public supply-chain transparency paths disclose PCB/CCL suppliers or named platform revenue for the report universe.

## Sources Checked

| Source | Local archive | Result | Treatment |
|---|---|---|---|
| Amazon 2024 Sustainability Report | `sources/probe-cloud-customer-side-20260617/2024-amazon-sustainability-report.pdf`; `.txt` | The report says Amazon's 2024 supplier list included nearly 2,300 finished-product suppliers and component suppliers, and that Amazon shares its supplier list to Open Supply Hub. Search in the PDF text did not surface Victory Giant, WUS, Avary, Shennan, PCB or printed-circuit-board supplier rows. | Confirms Amazon has a supplier transparency channel, but the archived report does not itself disclose named PCB suppliers or platform revenue. |
| Amazon AWS summary | `sources/probe-cloud-customer-side-20260617/2024-amazon-sustainability-report-aws-summary.pdf`; `.txt` | Discusses AWS hardware circularity and suppliers at a high level. No PCB company names or platform revenue split found. | Not usable for named PCB supplier evidence. |
| Amazon Supplier Manual / Supply Chain Standards | `amazon-supplier-manual-english.pdf`; `amazon-supply-chain-standards-english.pdf` | General supplier requirements and standards. No named PCB supplier or customer revenue data. | Governance evidence only. |
| Amazon Supplier List guessed URLs | `amazon-supplier-list.pdf`, `amazon-supplier-list-english.pdf`, `supplier-list.pdf`, `supply-chain-supplier-list.pdf`, `amazon-supplier-list-2022.pdf` | All guessed public paths returned HTTP 404. | Supplier list file was not recovered from public URL guesses. |
| Open Supply Hub API | `https://opensupplyhub.org/api/facilities/?q=...` | Anonymous API calls for Amazon, Victory Giant, Avary, WUS Printed and Shennan returned `Authentication credentials were not provided.` | OS Hub route requires credentials; no public query result was recovered in this environment. |
| Microsoft responsible sourcing / Top 100 suppliers | `microsoft-responsible-sourcing-full.html`; `Microsoft-Top-100-Production-Suppliers-FY24.pdf`; `.txt`; `data/microsoft_top100_supplier_pcb_evidence_20260617.md` | Re-fetching with a desktop user agent recovered the full responsible-sourcing page. `https://aka.ms/Top100Suppliers` resolved to Microsoft FY24 Top 100 Production Suppliers PDF. The official list includes AVARY HOLDING (SHENZHEN), VICTORY GIANT TECHNOLOGY (HUIZHOU), HANNSTAR BOARD, TRIPOD TECHNOLOGY, UNIMICRON TECHNOLOGY (KUNSHAN), SUZHOU DONGSHAN PRECISION and other board/component suppliers. | Strong customer-side official named-supplier evidence for Microsoft commercial hardware. It still does not disclose product category, PCB revenue, AI/cloud platform allocation, ASP, shipment or order value. |
| Google supplier / responsibility searches | web search results only | Search did not reveal an official Google supplier list naming PCB/CCL suppliers; results were generic, secondary or non-Google pages. | No official Google supplier evidence recovered. |
| 2026-06-18 targeted search refresh | live web search; no new local archive | Targeted searches for Amazon supplier list + Victory Giant/PCB, Google supplier list + Victory Giant/Avary/Tripod/Unimicron, and Microsoft Top 100 + Victory Giant/Avary/Tripod/PCB did not reveal new official customer-side supplier pages beyond the already archived Microsoft Top 100 list and Amazon/Open Supply Hub public-list path. | No new customer-official PCB supplier revenue, platform allocation, ASP, shipment or order-value evidence recovered. |

## Conclusion

- Microsoft FY24 Top 100 Production Suppliers is now the strongest recovered customer-side official named-supplier evidence: it names Avary Holding and Victory Giant Technology among Microsoft commercial-hardware top production suppliers.
- No cloud-customer official path recovered named PCB/CCL supplier revenue, named platform allocation, ASP, shipment or order value.
- Amazon remains a transparency lead because its report states supplier-list sharing via Open Supply Hub, but OS Hub API access requires credentials and the public report does not expose PCB supplier rows.
- Google official paths did not yield usable named PCB supplier evidence in this environment.
- Keep Google / Microsoft / AWS named PCB customer claims as broker-stated or secondary until a customer official list, Open Supply Hub authenticated data, paid supply-chain database or direct company/customer confirmation is available.
