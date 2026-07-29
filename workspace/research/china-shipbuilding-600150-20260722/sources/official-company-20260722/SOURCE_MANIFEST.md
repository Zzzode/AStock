# Official company evidence manifest

**Case:** China CSSC Holdings Limited / China Shipbuilding Industry Company Limited merger  
**Cutoff:** 2026-07-22  
**Retrieval date:** 2026-07-22  
**Primary host:** Shanghai Stock Exchange (SSE). PDF files were retrieved from the SSE Big5 mirror because the main static host returned an anti-bot HTML page to command-line requests. The document identifiers, publication dates, titles, and files are identical to those in the SSE announcement API.

| ID | Publication date | Official document | Official URL | Local archive |
|---|---|---|---|---|
| S00 | API query through 2026-07-22 | SSE 600150 announcement index, 2023-01-01 to 2026-07-22 | `https://query.sse.com.cn/security/stock/queryCompanyBulletin.do?isPagination=true&productId=600150&securityType=0101&reportType=ALL&pageHelp.pageSize=100&pageHelp.pageNo=1&beginDate=2023-01-01&endDate=2026-07-22` | `sse_600150_announcements_20230101_20260722.json` |
| S01 | 2024-04-27 | China CSSC 2023 annual report | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-04-27/600150_20240427_7VOC.pdf` | `2024-04-27_600150_2023-annual-report.pdf`; extracted text: same basename `.txt` |
| S02 | 2025-04-30 | China CSSC 2024 annual report | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-04-30/600150_20250430_T1GT.pdf` | `2025-04-30_600150_2024-annual-report.pdf`; extracted text: same basename `.txt` |
| S03 | 2026-04-30 | China CSSC 2025 annual report | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-30/600150_20260430_TC3V.pdf` | `2026-04-30_600150_2025-annual-report.pdf`; extracted text: same basename `.txt` |
| S04 | 2026-04-30 | China CSSC 2026 first-quarter report | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-30/600150_20260430_DRFR.pdf` | `2026-04-30_600150_2026Q1-report.pdf`; extracted text: same basename `.txt` |
| S05 | 2026-07-14 | China CSSC 2026 first-half earnings preview | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-07-14/600150_20260714_QX77.pdf` | `2026-07-14_600150_2026H1-earnings-preview.pdf`; extracted text: same basename `.txt` |
| S06 | 2024-09-03 | Merger-planning suspension announcement | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-09-03/600150_20240903_8MNP.pdf` | `2024-09-03_600150-merger-planning-suspension.pdf`; extracted text: same basename `.txt` |
| S07 | 2024-09-19 | Initial share-swap merger plan | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-09-19/600150_20240919_X34X.pdf` | `2024-09-19_600150-merger-plan.pdf`; extracted text: same basename `.txt` |
| S08 | 2025-01-08 | SASAC and industry-authority principle approvals | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-01-08/600150_20250108_NNCR.pdf` | `2025-01-08_600150-SASAC-industry-approvals.pdf`; extracted text: same basename `.txt` |
| S09 | 2025-02-19 | China CSSC first extraordinary general meeting resolution | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-02-19/600150_20250219_MC26.pdf` | `2025-02-19_600150-EGM-approval.pdf`; extracted text: same basename `.txt` |
| S10 | 2025-07-05 | SSE M&A Review Committee approval | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-07-05/600150_20250705_MIXH.pdf` | `2025-07-05_600150-SSE-MA-review-approval.pdf`; extracted text: same basename `.txt` |
| S11 | 2025-07-19 | CSRC registration approval announcement | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-07-19/600150_20250719_0695.pdf` | `2025-07-19_600150-CSRC-registration-approval.pdf`; extracted text: same basename `.txt` |
| S12 | 2025-07-19 | Final merger report | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-07-19/600150_20250719_8123.pdf` | `2025-07-19_600150-merger-report-final.pdf`; extracted text: same basename `.txt` |
| S13 | 2025-08-29 | SSE decision to delist 601989 from 2025-09-05 | `https://www.sse.com.cn/disclosure/announcement/listing/stock/c/c_20250829_10790128.shtml` | `2025-08-29_SSE-601989-delisting.html` |
| S14 | 2025-09-12 | Swap result, share change, and new-share listing announcement | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-09-12/600150_20250912_BPCR.pdf` | `2025-09-12_600150-swap-result-share-change-listing.pdf`; extracted text: same basename `.txt` |
| S15 | 2025-09-12 | Implementation and new-share listing memorandum | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-09-12/600150_20250912_YD4T.pdf` | `2025-09-12_600150-implementation-new-share-listing-memo.pdf`; extracted text: same basename `.txt` |
| S16 | 2026-05-15 | 2025 continuing-supervision opinion on the merger | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-15/600150_20260515_6WVW.pdf` | `2026-05-15_600150-merger-2025-continuing-supervision.pdf`; extracted text: same basename `.txt` |
| S17 | 2026-06-03 | 2025 annual and 2026 Q1 results briefing record | `https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-06-03/600150_20260603_Z8GR.pdf` | `2026-06-03_600150-2025-FY-2026Q1-briefing.pdf`; extracted text: same basename `.txt` |

## Extraction and integrity notes

- Text files were produced with Poppler `pdftotext -layout`; the PDFs remain the governing evidence.
- The project CLI commands `financials 600150 --json`, `financials 601989 --json`, and both `consistency-check` calls returned empty output on 2026-07-22. No CLI values were admitted into the verified tables.
- No company announcement found through the cutoff explicitly states that every title-transfer registration has been completed or that the China Shipbuilding Industry Company Limited legal entity has been deregistered. S14-S16 state that substantive rights and obligations pass from the contractual delivery date and that formal registrations are/shall be processed.
