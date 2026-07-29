# 600150 Broker Report Archive Manifest

- Collection date: 2026-07-22
- Window: 90 days, expanded to 12 months because the primary public report API returned fewer than 10 original PDFs in the initial window
- Original PDFs: 13
- Extracted texts: 13
- Failed PDF downloads: 0
- Source API capture: `eastmoney-reportapi-600150-20250722-20260722.json`
- Normalized catalog: `../../../data/report_catalog.md`
- Consensus packets: `../../../data/broker_street_consensus_20260722.md` and `.json`

| ID | Broker | Report date | PDF | Text | Perimeter |
|---|---|---:|---|---|---|
| 01 | 华源证券 | 2026-07-14 | `01-huayuan-2026h1-preview.pdf` | `01-huayuan-2026h1-preview.txt` | Post-merger |
| 02 | 诚通证券 | 2026-05-06 | `02-chengtong-2025ar-2026q1.pdf` | `02-chengtong-2025ar-2026q1.txt` | Post-merger |
| 03 | 东吴证券 | 2026-05-05 | `03-dongwu-2025ar-2026q1.pdf` | `03-dongwu-2025ar-2026q1.txt` | Post-merger |
| 04 | 华源证券 | 2026-05-01 | `04-huayuan-2026q1.pdf` | `04-huayuan-2026q1.txt` | Post-merger |
| 05 | 国金证券 | 2026-04-29 | `05-guojin-2026q1.pdf` | `05-guojin-2026q1.txt` | Post-merger |
| 06 | 国金证券 | 2026-01-29 | `06-guojin-2025-performance-preview.pdf` | `06-guojin-2025-performance-preview.txt` | Post-merger |
| 07 | 诚通证券 | 2025-10-30 | `07-chengtong-2025q3.pdf` | `07-chengtong-2025q3.txt` | Post-merger |
| 08 | 东吴证券 | 2025-10-30 | `08-dongwu-2025q3.pdf` | `08-dongwu-2025q3.txt` | Post-merger |
| 09 | 国金证券 | 2025-09-18 | `09-guojin-merger-close.pdf` | `09-guojin-merger-close.txt` | Post-merger pro forma |
| 10 | 诚通证券 | 2025-08-29 | `10-chengtong-2025h1.pdf` | `10-chengtong-2025h1.txt` | Pre-merger; zero current-consensus weight |
| 11 | 华源证券 | 2025-09-02 | `11-huayuan-2025h1.pdf` | `11-huayuan-2025h1.txt` | Pre-merger; zero current-consensus weight |
| 12 | 东吴证券 | 2025-09-01 | `12-dongwu-2025h1.pdf` | `12-dongwu-2025h1.txt` | Pre-merger; zero current-consensus weight |
| 13 | 国金证券 | 2025-08-29 | `13-guojin-2025h1.pdf` | `13-guojin-2025h1.txt` | Pre-merger; zero current-consensus weight |

The extracted `.txt` files preserve report page order and tables using Poppler layout extraction. Downstream agents should use the normalized catalog for forecast fields and the local text for claim-level verification.
