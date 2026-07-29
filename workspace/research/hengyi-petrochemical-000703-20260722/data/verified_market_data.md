# 恒逸石化已核验市场数据

核验日期：2026-07-22  
实时截止：2026-07-22 13:52；完整交易日截止：2026-07-21。  
市值说明：价格与股本不是同一时点，故使用“约”并保留可转债转股导致的后续稀释风险。

## 市场数据（截至 2026-07-22 13:52）

| Ticker | Price | Total MCap | Unrestricted-share MCap | 5d Avg Volume | NB Holding% | Lock-up / Treasury | Source | Confidence |
|---|---:|---:|---:|---:|---|---|---|---|
| 000703 | CNY15.06（盘中） | 约 CNY57.553bn | 约 CNY57.264bn；不等同 free float | 95.963m shares/day | N/A（官方渠道未取得） | 限售 19.172m；回购专户 381.840m（分红登记口径） | AStock/Sina + 巨潮股本公告 | 价格高；市值中高 |

## 核验明细

| 指标 | 核验值 | 类型 | 核验说明 |
|---|---:|---|---|
| 盘中价 | CNY15.06 | reported snapshot | `market-snapshot` 与 `quote` 同时核验；均指向 13:52 左右 |
| 日内涨跌 | +2.8689% | reported snapshot | 前收 CNY14.64；不是收盘涨幅 |
| 总股本 | 3,821,562,147 shares | reported at 2026-06-30 | 巨潮 Q2 可转债转股公告 p.3；较 Q1 末增加 479,032 股 |
| 总市值 | CNY57.552726bn | derived | `CNY15.06 × 3,821,562,147`；未包含 2026Q3 尚未披露的潜在转股变化 |
| 无限售股份 | 3,802,389,897 shares | reported at 2026-06-30 | 巨潮公告；占总股本 99.50% |
| 无限售口径市值 | CNY57.263992bn | derived | 不能标记为 free-float market cap，因为无限售账户口径受回购专户影响 |
| 5 日平均成交量 | 95,963,399.2 shares/day | derived | 2026-07-15、16、17、20、21 五个完整交易日 |
| 5 日平均成交额 | CNY1.406392bn/day | derived | 同上 |
| 一年 QFQ 高 / 低 | CNY18.29 / 5.87 | reported history | 2026-05-06 / 2025-08-14；前复权口径 |

## 质量判定

- 实时价格：`realtime`，高置信；明确为盘中快照。
- 历史 K 线：`delayed_complete_sessions`，中高置信；前复权且截止前一完整交易日。
- 总市值：`derived`，中高置信；股本官方但滞后于实时价格 22 天，且“恒逸转 2”仍可转股。
- Free float 与北向持股：未用非官方替代值，保留 N/A。
- AStock quote 返回的 PE/PB/市值零值已排除，不进入研报或估值输入。

