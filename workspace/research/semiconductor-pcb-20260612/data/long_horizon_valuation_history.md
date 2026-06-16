# Long-Horizon Valuation History

**Source:** Baidu valuation API via AkShare `stock_zh_valuation_baidu`.

**Boundary:** Public valuation series. Percentiles are within each fetched Baidu period and are not Wind/Choice standardized valuation bands.

## Core names: three-year PE/PB/PCF percentile

| Ticker | Name | PE rec | PE latest | PE pctile | PB latest | PB pctile | PCF latest | PCF pctile |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | 1097 | 59.83 | 99.73% | 15.33 | 99.73% | 66.48 | 98.27% |
| 300476 | 胜宏科技 | 1097 | 72.35 | 86.78% | 19.45 | 91.70% | 73.56 | 74.02% |
| 002916 | 深南电路 | 1097 | 74.93 | 99.54% | 15.05 | 99.54% | N/A | N/A% |
| 600183 | 生益科技 | 1097 | 102.90 | 100.00% | 22.55 | 100.00% | 76.65 | 77.67% |
| 603186 | 华正新材 | 1097 | 101.55 | 100.00% | 12.54 | 100.00% | 82.96 | 100.00% |

## Watchlist: three-year PE/PB percentile

| Ticker | Name | PE rec | PE latest | PE pctile | PB latest | PB pctile |
|---|---|---:|---:|---:|---:|---:|
| 688519 | 南亚新材 | 1097 | 215.42 | 97.81% | 27.58 | 100.00% |
| 002436 | 兴森科技 | 1097 | 472.15 | 99.82% | 12.77 | 99.82% |
| 301200 | 大族数控 | 1097 | 144.46 | 100.00% | 13.29 | 97.45% |
| 688630 | 芯碁微装 | 1097 | 166.62 | 100.00% | 23.87 | 100.00% |
| 300400 | 劲拓股份 | 1097 | 123.60 | 100.00% | 14.84 | 100.00% |
| 301377 | 鼎泰高科 | 1097 | 366.37 | 100.00% | 78.49 | 100.00% |

## Five-year availability check

| Ticker | Name | PE records | PB records | PE latest | PE pctile | PB latest | PB pctile |
|---|---|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | 914 | 914 | 59.83 | 99.89% | 15.33 | 99.89% |
| 300476 | 胜宏科技 | 914 | 914 | 72.35 | 92.23% | 19.45 | 94.97% |
| 002916 | 深南电路 | 914 | 914 | 74.93 | 99.78% | 15.05 | 99.78% |
| 600183 | 生益科技 | 914 | 914 | 102.90 | 100.00% | 22.55 | 100.00% |
| 603186 | 华正新材 | 914 | 914 | 101.55 | 98.14% | 12.54 | 100.00% |
| 688519 | 南亚新材 | 914 | 914 | 215.42 | 98.69% | 27.58 | 100.00% |
| 002436 | 兴森科技 | 914 | 914 | 472.15 | 100.00% | 12.77 | 100.00% |
| 301200 | 大族数控 | 1568 | 1568 | 144.46 | 100.00% | 13.29 | 98.21% |
| 688630 | 芯碁微装 | 914 | 914 | 166.62 | 100.00% | 23.87 | 100.00% |
| 300400 | 劲拓股份 | 914 | 914 | 123.60 | 99.34% | 14.84 | 100.00% |
| 301377 | 鼎泰高科 | 1301 | 1301 | 366.37 | 100.00% | 78.49 | 100.00% |

## Interpretation

- Three-year and five-year histories materially improve the previous one-year valuation percentile view.
- Several names remain near the top of their longer public valuation bands, so the valuation crowding conclusion is robust beyond the one-year window.
- Public Baidu data can have missing/unstable values for loss-making or small-cap names; use as valuation context, not exact trading signal.
