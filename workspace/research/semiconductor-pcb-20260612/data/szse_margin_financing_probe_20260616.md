# SZSE Official Margin Financing Probe

## Purpose

Probe whether Shenzhen Stock Exchange official margin-financing data can replace or improve the existing Eastmoney public proxy for Shenzhen-listed names, especially `300400` Jintuo Technology, which returned empty rows in the Eastmoney long-window margin-financing table.

## Official Interface Identified

AkShare exposes SZSE official margin-financing wrappers that point to Shenzhen Stock Exchange pages:

| Function | Source page | CATALOGID | TABKEY | Intended data |
|---|---|---|---|---|
| `stock_margin_detail_szse(date)` | `https://www.szse.cn/disclosure/margin/margin/index.html` | `1837_xxpl` | `tab2` | 融资融券交易明细 |
| `stock_margin_szse(date)` | `https://www.szse.cn/disclosure/margin/margin/index.html` | `1837_xxpl` | `tab1` | 融资融券交易总量 |
| `stock_margin_underlying_info_szse(date)` | `https://www.szse.cn/disclosure/margin/object/index.html` | `1834_xxpl` | `tab1` | 标的证券信息 |

AkShare source file inspected:

`/Users/bytedance/Develop/AStock/.venv/lib/python3.14/site-packages/akshare/stock_feature/stock_margin_szse.py`

The official download endpoint is:

`https://www.szse.cn/api/report/ShowReport`

The official JSON endpoint can be:

`https://www.szse.cn/api/report/ShowReport/data`

## Attempts

| Attempt | Result | Treatment |
|---|---|---|
| Direct `curl` to `https://www.szse.cn/disclosure/margin/margin/index.html` | Empty response in this environment. | Not usable as page evidence. |
| Direct `curl` to `https://www.szse.cn/disclosure/margin/object/index.html` | Connection reset by peer or empty response. | Not usable as page evidence. |
| `ak.stock_margin_detail_szse(date="20260616")` | Python requests failed with `ConnectionResetError: [Errno 54] Connection reset by peer`. | Official wrapper identified, but data not retrieved. |
| `ak.stock_margin_underlying_info_szse(date="20260616")` | Python requests failed with `ConnectionResetError: [Errno 54] Connection reset by peer`. | Official wrapper identified, but data not retrieved. |
| `curl` xlsx detail endpoint with `CATALOGID=1837_xxpl`, `TABKEY=tab2`, `txtDate=2026-06-16` | `curl: (35) Recv failure: Connection reset by peer`. | No valid xlsx file; do not use. |
| `curl` xlsx underlying endpoint with `CATALOGID=1834_xxpl`, `TABKEY=tab1`, `txtDate=2026-06-16` | `curl: (35) Recv failure: Connection reset by peer`. | No valid xlsx file; do not use. |
| `curl` JSON summary endpoint with `CATALOGID=1837_xxpl`, `TABKEY=tab1` | One exploratory call returned a JSON payload for market-level financing summary metadata and rows; repeat archival call returned `000 0` after connection reset. | Interface path confirmed, but no durable archived JSON file was produced. |

## Boundary

This probe does not improve the report's numeric margin-financing table because no durable SZSE official detail data was retrieved.

The existing Eastmoney public proxy remains the usable Shenzhen-listed margin-financing source in the report. The SZSE official interface should be retried from a network environment where `www.szse.cn` API downloads are stable.

Do not mark `300400` margin-financing coverage as complete from this probe. The current public-source state remains:

- Eastmoney margin-financing endpoint returned empty rows for `300400`.
- SZSE official interface was identified but not successfully downloaded in the local environment.
- No terminal-grade financing / order-flow / beneficial-owner dataset is available locally.
