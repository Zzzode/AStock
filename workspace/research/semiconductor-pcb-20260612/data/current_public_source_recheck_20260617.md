# Current Public Source Recheck

**Run date:** 2026-06-17

**Purpose:** Re-check whether the items still marked as unfinished can be completed from the current local environment or public web/API sources.

## 1. Paid / Terminal Data Capability

The project `.venv` was rechecked for market-data and paid-terminal SDKs.

| Provider | Current status | Evidence |
|---|---|---|
| Tushare | unavailable | Python `importlib.util.find_spec("tushare")` returned `None`. |
| WindPy / Wind | unavailable | `find_spec("WindPy")` returned `None`. |
| iFinD | unavailable | `find_spec("iFinDPy")` returned `None`. |
| Choice | unavailable | `find_spec("choice")` returned `None`. |
| JQData | unavailable | `find_spec("jqdatasdk")` returned `None`; no relevant env key found. |
| RQData | unavailable | `find_spec("rqdatac")` returned `None`; no relevant env key found. |
| Datayes | unavailable | `find_spec("datayes")` returned `None`; no relevant env key found. |
| Bloomberg / xbbg / blpapi | unavailable | `find_spec("xbbg")` and `find_spec("blpapi")` returned `None`. |
| Refinitiv / Eikon | unavailable | `find_spec("eikon")` returned `None`. |
| Paid BOL / customs providers | unavailable | No Panjiva / ImportGenius / Volza SDK or env key found. |
| AkShare | available | Version `1.18.41`. |
| Baostock | available | Version `00.8.90`. |

Environment variable scan found no keys containing Tushare, Wind, iFinD, Choice, JQData, RQData, Datayes, Bloomberg, Refinitiv, Eikon, Panjiva, ImportGenius or Volza.

## 2. Public Web Search Recheck

Targeted searches were rerun for:

- `沪电股份 NVIDIA Google TPU AI服务器 PCB 收入 拆分 2026 客户`
- `胜宏科技 NVIDIA Google ASIC TPU UBB AI PCB 收入 拆分 2026 客户`
- `生益科技 M9 M10 CCL GPU AI 认证客户 收入占比 2026`
- `沪电股份 胜宏科技 深南电路 北向资金 持股 明细 2026 日度 受益所有人 Wind Choice`

Result treatment:

| Topic | Search result quality | Treatment |
|---|---|---|
| Hudian named customer / platform revenue | Results were mainly Eastmoney wealth-account posts, Sina stock-board posts and Xueqiu claims with specific Google / NVIDIA / Rubin / TPU numbers. | Do not use as confirmed evidence. They are not issuer filings, original broker PDFs, official customer disclosures or auditable terminal datasets. |
| Shenghong named customer / platform revenue | Results were mainly Securities Star, Toutiao, Xueqiu and Eastmoney wealth-account posts with specific NVIDIA / Google / ASIC shares and order claims. | Do not use as confirmed evidence. Keep in rumor boundary only. |
| Shengyi M9 / M10 revenue and customer certification | Results were mainly Toutiao, Xueqiu and Weibo posts with specific NVIDIA certification and market-share claims. | Do not use as confirmed evidence. Existing official SSE IR evidence remains the reliable public boundary. |
| Northbound / Stock Connect | Search exposed Eastmoney `data.eastmoney.com/hsgt/<code>.html` pages and mobile pages. | Useful for public Stock Connect top-10 deal / page-shell evidence, but not beneficial-owner data or terminal-grade order flow. |

## 3. Eastmoney Public Stock Connect API Recheck

The Eastmoney desktop page loads a public page shell and JavaScript. The mobile script shows `RPT_MUTUAL_TOP10DEAL` for Stock Connect top-10 deal rows. Direct API calls were tested:

```text
https://datacenter-web.eastmoney.com/api/data/v1/get
  ?reportName=RPT_MUTUAL_TOP10DEAL
  &columns=ALL
  &pageNumber=1
  &pageSize=5
  &sortColumns=TRADE_DATE
  &sortTypes=-1
  &source=WEB
  &client=WEB
  &filter=(SECURITY_CODE="<ticker>")
```

Observed coverage:

| Ticker | Result | Latest visible row / boundary |
|---|---|---|
| 002463 | success | 2026-06-17 row returned: `RANK=7`, `DEAL_AMT=2165357816`, close `146.55`, change `4.20%`; buy/sell/net-buy fields were null. |
| 300476 | success | Latest returned row was 2026-05-29; buy/sell/net-buy fields were null. |
| 002916 | success | Latest returned row was 2026-01-21; buy/sell/net-buy fields were null. |
| 600183 | success | 2026-06-17 row returned: `RANK=3`, `DEAL_AMT=2522804855`, close `180.15`, change `0.42%`; buy/sell/net-buy fields were null. |
| 603186 | empty | API returned `返回数据为空`. |
| 002938 | success, stale | Two historical rows returned, latest 2024-08-14; not current. |
| 688519 | empty | API returned `返回数据为空`. |
| 002436 | success, sparse | Latest returned row was 2025-07-30; not current. |
| 301200 | empty | API returned `返回数据为空`. |
| 688630 | empty | API returned `返回数据为空`. |
| 300400 | empty | API returned `返回数据为空`. |
| 301377 | empty | API returned `返回数据为空`. |

The desktop JavaScript also references `RPT_MUTUAL_BOARD_HOLDRANK_WEB` for Stock Connect holding-rank pages. A direct test with `sortColumns=HOLD_DATE` returned `HOLD_DATE排序列不存在` for the tested universe, so this pass did not improve beyond the already archived HKEX quarterly shareholding and Eastmoney participant/custodian bridge.

## 4. Conclusion

The recheck does not close the strict unresolved requirements:

1. Named NVIDIA / Google ASIC / domestic compute / optical-module / Apple platform revenue split remains unavailable from reliable public evidence.
2. Terminal-grade realtime order flow, post-2024 daily northbound beneficial-owner changes and official active/passive ownership classification remain unavailable.
3. A full customer/platform bottom-up EPS model remains impossible without customer revenue, ASP, shipment, segment margin, depreciation and working-capital assumptions.

What the recheck adds:

- Current confirmation that no paid-terminal SDK or env credential exists in the local environment.
- Current confirmation that public search results with specific customer/platform numbers are still secondary/social or repost-style material and should not be promoted to confirmed evidence.
- Current Eastmoney `RPT_MUTUAL_TOP10DEAL` evidence that can supplement Stock Connect top-10 deal context for a subset of tickers, but not the missing institutional-positioning requirement.
