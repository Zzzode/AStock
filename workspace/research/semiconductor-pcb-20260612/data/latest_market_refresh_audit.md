# Latest Market Refresh Audit

**Attempt date:** 2026-06-16

## Result

**Updated 2026-06-16:** Eastmoney realtime `ulist` still returned HTTP 502, but Tencent `qt.gtimg.cn` quote feed succeeded and refreshed price, total market capitalization, PE and PB for 12/12 current-universe tickers. The refreshed evidence is stored in:

- `data/raw_tencent_quote/quote_20260616.txt`
- `data/tencent_realtime_market_snapshot_20260616.json`
- `data/tencent_realtime_market_snapshot_20260616.md`

**Updated 2026-06-18:** Tencent `qt.gtimg.cn` quote feed was refetched for all 12 current-universe tickers. The HTTP fetch succeeded for 12/12 tickers, with embedded quote timestamps around 2026-06-17 16:14 CST. The refreshed evidence is stored in:

- `data/raw_tencent_quote/quote_20260618.txt`
- `data/tencent_realtime_market_snapshot_20260618.json`
- `data/tencent_realtime_market_snapshot_20260618.md`

The older table below is retained as the 2026-06-15 close proxy audit; valuation anchors should now prefer the Tencent 2026-06-18 fetched / 2026-06-17 embedded timestamp quote snapshot where applicable.

| Ticker | Name | Latest public close | Close date | Source | Market cap status |
|---|---|---:|---:|---|---|
| 002463 | 沪电股份 | 133.76 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 300476 | 胜宏科技 | 344.50 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 002916 | 深南电路 | 399.80 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 600183 | 生益科技 | 166.41 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 603186 | 华正新材 | 187.33 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 688519 | 南亚新材 | 338.30 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 002436 | 兴森科技 | 40.09 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 301200 | 大族数控 | 304.40 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 688630 | 芯碁微装 | 438.19 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 300400 | 劲拓股份 | 43.21 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |
| 301377 | 鼎泰高科 | 553.56 | 2026-06-15 | Eastmoney fund-flow dayline / Yahoo cross-check | Not reliably refreshed; use archived market cap for valuation anchors |

## Failed refresh attempts

- `ak.stock_zh_a_spot_em()` returned remote disconnected.
- `ak.stock_individual_info_em()` and `ak.stock_bid_ask_em()` returned JSON decode errors for sample tickers.
- `ak.stock_zh_a_hist()` returned remote disconnected for sample tickers.

## Use in report

- Use Tencent 2026-06-18 fetched / 2026-06-17 embedded timestamp quote snapshot as the latest public price / market-cap / PE / PB proxy in valuation tables.
- Keep archived 2026-06-12 market cap only as a historical baseline, not as the latest valuation anchor.
- Tencent quote fields can be used as a refreshed public valuation snapshot. Do not call it a Wind/Choice standardized valuation database, audited closing valuation, beneficial-owner positioning, or terminal-grade order-flow evidence.
