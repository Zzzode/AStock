# R4 SSE ETF Public-Universe Probe — Capture Manifest

This 2026-08-15 (Asia/Shanghai) batch tests, for research only, whether the
Shanghai Stock Exchange public fund master/listing endpoint can enumerate a
broad current ETF cohort mechanically. It does not select a product, set an
allocation, create a holding, calculate a return, or authorize an order.

The canonical machine-readable manifest is manifest.json.

## Source and access

| Field | Value |
|---|---|
| Authority | Shanghai Stock Exchange |
| Source page | https://www.sse.com.cn/assortment/fund/list/ |
| Read-only endpoint | https://query.sse.com.cn/commonSoaQuery.do |
| Method / query | GET; sqlId=FUND_LIST |
| Authentication | None; no cookies or credentials |
| Filter | fundType=00; subClass=01,02,03,04,06,08,09,31,32,33,34,35,36,37,38 |
| Response | HTTP 200; application/json;charset=UTF-8 |

The API objectively exposes fundType/subClass codes. Its captured JSON does
not include a textual codebook, so the query partitions below are code groups,
not a substitute for a separately versioned SSE taxonomy record.

## Raw source inventory

The source bodies were one-line JSON. Repository storage adds exactly one final
LF byte. The raw hash is the wire-body SHA-256 before that LF; the stored hash
is the on-disk-file SHA-256. Removing exactly the final LF reproduces each raw
hash. All JSON files were syntax-validated.

| ID | Raw file | Requested / received UTC | Raw SHA-256 | Stored SHA-256 |
|---|---|---|---|---|
| master_page_1 | fund_list_master_page_1.json | 2026-08-14T16:17:22.609632432Z / 2026-08-14T16:17:23.286953319Z | 04c5b1cf4b3439765927e91d0b481609c9e8422f1b63feeffc5c01495b3fd0e1 | 07b3bd29cbee0c219a3b52be53d787af05c1541bf07ef9e4bee785379c8a77ea |
| master_page_2 | fund_list_master_page_2.json | 2026-08-14T16:17:23.360346605Z / 2026-08-14T16:17:24.076102092Z | 89a025f6f1e68c152844af93b4e149a85cde4a748c39e3534eaf54308e2c345f | 49b1426a4c1f1635c4ade9c0f24379ad7fa6cf35a3c8d82792e3d42b93936edc |
| equity_partition_page_1 | fund_list_equity_family_page_1.json | 2026-08-14T16:16:14.575552467Z / 2026-08-14T16:16:15.295551756Z | 399a976ace0b646cb3f95511c34daa70f13bdbc47a33f84381db43c92de4c111 | 904de2abbd57a32a35eeb5ef63c2437ee19110d9d0ec9070f42587df209c8c99 |
| bond_partition_page_1 | fund_list_bond_family_page_1.json | 2026-08-14T16:16:15.368164073Z / 2026-08-14T16:16:16.078630041Z | a924dad498314e8f30c8fffcac7eeb08ba4232caf3e443fdc1a0e1869e072088 | 446c2e2e875830cffb8f39471a031efac67286df75c5c3f09264a9da43baa426 |
| crossborder_partition_page_1 | fund_list_crossborder_family_page_1.json | 2026-08-14T16:16:16.160396490Z / 2026-08-14T16:16:16.823149987Z | 417601d5ffb82c33f9d385c6c9a9075fedbcc99b85c5d642f731f17355957434 | b543ae57c76546988f2b1c72dd1e4e4d156344dc8d71d45c1f2674f33bf120e3 |
| commodity_partition_page_1 | fund_list_commodity_family_page_1.json | 2026-08-14T16:16:16.899961187Z / 2026-08-14T16:16:17.646999229Z | f794561441a96d82fa87cf4d7781014561032a39f4aeca92efb3857a43299054 | 142c02b14ed701dc14f20b5a09c7d22952d70e1fd259d8bcebabc1b9b29527b3 |

Exact URLs, byte counts, local paths, pagination metadata, and Asia/Shanghai
timestamps are in manifest.json.

## Enumeration test

| Query partition | Total | Pages at size 5 |
|---|---:|---:|
| All configured codes | 893 | 179 |
| 01,03,08,09,31 | 725 | 145 |
| 02,32,36,37 | 34 | 7 |
| 33,34,35 | 126 | 26 |
| 06,38 | 8 | 2 |
| Partition sum | 893 | — |

The partition sum equals the master total. Master page one returns 510010,
510020, 510030, 510040, 510050; page two returns 510060, 510090, 510100,
510130, 510140. The page samples are disjoint, confirming page advancement.
The full 893 rows were not archived. No server snapshot ID, query-as-of date,
or stable cursor is returned, so a live all-page pull can drift.

## Fields and limitations

Rows expose fundCode, fundType, subClass, listingDate, fundAbbr, secNameFull,
companyName, fundManager, TRUSTEE_NAME, INDEX_CODE, INDEX_NAME, LAW_FIRM, and
CONTACT_MOBILE. Identity/classification and manager/trustee fields were
non-empty in all sampled rows. INDEX_CODE and INDEX_NAME were blank in every
commodity sample row; LAW_FIRM and CONTACT_MOBILE were blank in every sample.

The response has no explicit listing/trading/lifecycle status, delisting date,
suspension/resumption state, source as-of timestamp/version, historical
membership, price/NAV/IOPV, liquidity, holdings, shares/float, fees,
distribution/action events, rights/access, broker route, settlement, or tax
field. It therefore supports only a timestamped discovery snapshot—not a
point-in-time, event-aware, rights-aware, total-return, or executable cohort.
