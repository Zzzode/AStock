# Paid Data Access Audit

**Purpose:** Check whether the remaining gaps can be solved through local paid/semi-paid data terminals or SDKs.

## Environment / SDK Check

| Provider | Local status | Evidence |
|---|---|---|
| Tushare | unavailable | `ModuleNotFoundError: No module named 'tushare'` |
| WindPy / Wind | unavailable | `ModuleNotFoundError: No module named 'WindPy'` |
| iFinD / 同花顺 | unavailable | `ModuleNotFoundError: No module named 'iFinDPy'` |
| Choice | unavailable | `ModuleNotFoundError: No module named 'choice'` |
| AkShare | available | version 1.18.41 |
| Baostock | available | version 00.8.90 |
| JQData / 聚宽 | unavailable | `ModuleNotFoundError: No module named 'jqdatasdk'`; no JQData env token found |
| RQData / RiceQuant | unavailable | `ModuleNotFoundError: No module named 'rqdatac'`; no RQData env token found |
| Datayes | unavailable | no SDK / env credential found |
| Bloomberg / Refinitiv | unavailable | no SDK / terminal credential found |
| Panjiva / ImportGenius / Volza / paid BOL | unavailable | no SDK / env credential / local config found; only public pages were accessible |

**2026-06-16 refresh:** The SDK check was run against the project `.venv`. `akshare` and `baostock` are available in `.venv`; paid-terminal SDKs and credentials are not. A broad environment-variable scan found only non-market credentials (`COCO_PROXY_API_KEY`, code repository token). A home-directory config scan found no market-data or customs/BOL credential files.

## Environment Variables

No Tushare/Wind/Choice/iFinD financial data token was found in the environment. A code repository private token exists, but it is not a market-data credential.

## Conclusion

The remaining unsolved requirements require data not available in this local environment:

1. Named customer/platform revenue split by NVIDIA / Google ASIC / domestic compute / optical module chain.
2. Complete live institutional holdings / fund-flow / northbound positioning across all core tickers.
3. Full customer-by-platform bottom-up EPS assumptions.

Current accessible sources are AkShare, Baostock, public company filings, public broker PDFs, public IR PDFs, public web pages, public customs/BOL pages, Tencent quote feed and Eastmoney public endpoints. These have already been used and audited.
