# Eastmoney Share Pledge Evidence

**Source:** Eastmoney DataCenter `RPT_CSDC_LIST` for pledge-ratio time series and `RPTA_APP_ACCUMDETAILS` for pledge detail rows. Raw JSON is archived under `data/raw_eastmoney_pledge/`.

**Unit note:** The ratio table reports pledged shares in 10k shares and pledge market cap in 10k CNY by Eastmoney page convention. Detail rows use `PF_NUM` in shares and `MARKET_CAP` in CNY.

## Latest pledge ratio snapshot

| Ticker | Name | Latest date | Pledge ratio | Pledged shares | Pledge market cap | Pledge deals | Active detail mcap | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| 688519 | 南亚新材 | 2020-09-18 | 3.28% | 770.00万股 | 2.92亿元 | 1 | 0.00亿元 |  |
| 603186 | 华正新材 | 2019-04-30 | 1.93% | 250.00万股 | 0.79亿元 | 4 | 0.00亿元 |  |
| 002938 | 鹏鼎控股 | 2021-06-18 | 1.26% | 2906.12万股 | 8.70亿元 | 4 | 0.00亿元 | detail: 返回数据为空 |
| 301200 | 大族数控 | 2026-06-12 | 0.75% | 323.19万股 | 8.95亿元 | 1 | 0.96亿元 |  |
| 300400 | 劲拓股份 | 2025-06-06 | 0.27% | 65.00万股 | 0.10亿元 | 1 | 0.00亿元 |  |
| 300476 | 胜宏科技 | 2026-06-12 | 0.16% | 136.36万股 | 4.46亿元 | 3 | 5.33亿元 |  |
| 002916 | 深南电路 | 2022-05-06 | 0.03% | 15.00万股 | 0.14亿元 | 1 | 0.00亿元 | detail: 返回数据为空 |
| 002463 | 沪电股份 | 2020-04-24 | 0.00% | 5.97万股 | 0.02亿元 | 2 | 1.18亿元 |  |
| 600183 | 生益科技 | 2021-02-19 | 0.00% | 0.29万股 | 0.00亿元 | 1 | 0.00亿元 |  |
| 002436 | 兴森科技 | N/A | N/A | N/A | N/A | N/A | 15.20亿元 | ratio: JSONDecodeError('Unterminated string sta |
| 688630 | 芯碁微装 | N/A | N/A | N/A | N/A | N/A | 0.00亿元 | ratio: 返回数据为空; detail: 返回数据为空 |
| 301377 | 鼎泰高科 | N/A | N/A | N/A | N/A | N/A | 0.00亿元 | ratio: 返回数据为空; detail: 返回数据为空 |

## Boundary

- Eastmoney states warning-line and liquidation-line fields are estimated using market-standard assumptions; they may differ from actual pledge contracts.
- Pledge data is a controlling-shareholder / governance-risk proxy, not institutional ownership or order flow.
- Empty rows can mean no Eastmoney public pledge data in the queried table, not necessarily no pledge risk.
