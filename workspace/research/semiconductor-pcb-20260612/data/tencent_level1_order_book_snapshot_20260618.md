# Tencent Level-1 Order Book Snapshot

**Run date:** 2026-06-18

**Source:** Archived Tencent `qt.gtimg.cn` quote feed at `data/raw_tencent_quote/quote_20260618.txt`.

**Boundary:** Public delayed/post-close five-level bid/ask proxy only. This is not exchange tick/order-book data, not beneficial-owner positioning, and not terminal-grade order flow.

| Ticker | Name | Timestamp | Last | Best bid | Best ask | Spread | Bid vol L1-L5 | Ask vol L1-L5 | Imbalance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 002463 | ɷ | 20260617161436 | 146.55 | 146.55 | 146.56 | 0.01 | 5328 | 421 | 0.85354 |
| 300476 | ʤƼ | 20260617161418 | 361.7 | 361.69 | 361.7 | 0.01 | 374 | 1097 | -0.491502 |
| 002916 | ϵ· | 20260617161445 | 444.27 | 444.27 | 0.0 | None | 11795 | 0 | 1.0 |
| 600183 | Ƽ | 20260617161404 | 180.15 | 180.14 | 180.15 | 0.01 | 5845 | 51 | 0.9827 |
| 603186 | ² | 20260617161411 | 226.67 | 226.67 | 0.0 | None | 1678 | 0 | 1.0 |
| 688519 | ² | 20260617161451 | 395.01 | 395.01 | 395.03 | 0.02 | 146 | 18 | 0.780488 |
| 002436 | ɭƼ | 20260617161418 | 47.8 | 47.8 | 47.81 | 0.01 | 12958 | 158 | 0.975907 |
| 301200 |  | 20260617161445 | 328.08 | 328.08 | 328.27 | 0.19 | 34 | 10 | 0.545455 |
| 688630 | о΢װ | 20260617161449 | 475.77 | 475.77 | 475.78 | 0.01 | 25 | 93 | -0.576271 |
| 300400 | عɷ | 20260617161421 | 43.61 | 43.61 | 43.62 | 0.01 | 567 | 214 | 0.451985 |
| 301377 | ̩߿ | 20260617161457 | 590.0 | 590.0 | 590.01 | 0.01 | 102 | 33 | 0.511111 |
| 002938 | ع | 20260617161439 | 119.01 | 119.01 | 0.0 | None | 12112 | 0 | 1.0 |

## Interpretation

- The archived Tencent feed contains five bid and five ask levels for all 12 report-universe tickers.
- This improves public market microstructure context beyond price/PE/PB anchors.
- It still does not satisfy the strict terminal-grade positioning/order-flow requirement because it lacks tick-level exchange order book history, active/passive trade classification, beneficial-owner positioning and official institutional labels.
