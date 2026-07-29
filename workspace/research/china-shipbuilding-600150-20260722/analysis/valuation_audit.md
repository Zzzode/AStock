# 中国船舶（600150.SH）R1 Valuation Audit

**审计日：** 2026-07-22  
**审计对象：** `analysis/valuation_model.md`、`analysis/segment_valuation_model.md`、`data/current_valuation_model_20260722.json`  
**结论：** 估值算术、场景顺序、价格/股本/市值、冻结盈利分母、多锚权重、发布目标价与涨跌幅均可从披露输入复算。

`Model Reproducibility: PASS`

## Price / Share-Count Reconciliation

| Check | Disclosed input | Recalculation | Result |
|---|---|---|---|
| Price/date | 33.02；2026-07-22 | 盘后未复权现货快照 | PASS |
| Share class/currency | A 股普通股；CNY | 75.25621288 亿股 | PASS |
| Shares outstanding | 7,525,621,288 股 | 4,472,428,758 + 3,053,192,530 | PASS |
| Market cap | 33.02 × 75.25621288 | 2,484.9601492976 亿元 | PASS |
| 2026E EPS denominator | 172.762156 / 75.25621288 | 2.295653068，冻结值 2.295653，差 0.000000068 | PASS |
| 2027E EPS denominator | 216.489959 / 75.25621288 | 与冻结 EPS 2.876705 在六位小数容差内一致 | PASS |
| 2028E EPS denominator | 246.810914 / 75.25621288 | 与冻结 EPS 3.279608 在六位小数容差内一致 | PASS |

2025A 法定 EPS 使用披露的加权平均股本，不被 75.25621288 亿股反算替换；当前估值和 2026E 以后统一使用合并后期末股本。价格、股本、市值、EPS 均为同一 A 股/CNY 口径。

## Forecast Availability

| Item | Bear | Base | Bull | Status |
|---|---:|---:|---:|---|
| 2026E revenue | 1,652.487134 | 1,775.000000 | 1,935.000000 | 冻结 growth JSON 可用 |
| 2026E parent NP | 112.071122 | 172.762156 | 217.340737 | 冻结 growth JSON 可用 |
| 2026E EPS | 1.489194 | 2.295653 | 2.888011 | 分母一致 |
| 2027E parent NP / EPS | 93.715809 / 1.245290 | 216.489959 / 2.876705 | 279.849133 / 3.718618 | 主估值年度可用 |
| 2028E parent NP / EPS | 80.197081 / 1.065654 | 246.810914 / 3.279608 | 331.629435 / 4.406672 | 持续期交叉可用 |

H1 仅为未经审计业绩预告，不作 H1×2；季度/半年机械年化未作为最终分母。Forecast availability：**PASS**。

## Scenario-Band Checks

| Scenario | EPS | PE | Recalculated target | Current-price return | Check |
|---|---:|---:|---:|---:|---|
| Bear | 1.245290 | 9.0x | 1.245290 × 9.0 = **11.207610** | -66.0581% | PASS |
| Base | 2.876705 | 11.5x | 2.876705 × 11.5 = **33.0821075** | +0.1881% | PASS |
| Bull | 3.718618 | 13.0x | 3.718618 × 13.0 = **48.342034** | +46.4023% | PASS |

顺序 `Bear < Base < Bull` 成立；三情景都使用同一 2027E cycle-normalized PE 方法，倍数与盈利同时随叙事变化。基础公允区间为 2.876705 × 11.0—12.5x = **31.643755—35.9588125 元**。Bubble degree = `(33.02 / 33.0821075 - 1) × 100% = -0.1877%`。Scenario-band checks：**PASS**。

## Multi-Anchor and Final-Target Check

| Anchor | Value | Weight | Contribution |
|---|---:|---:|---:|
| Fundamental / intrinsic | 33.0821075 | 0.85 | 28.119791375 |
| Market-implied sentiment | 33.02 | 0.15 | 4.953000000 |
| Broker/Street target | not disclosed | **0.00** | 0 |
| Total | — | **1.00** | **33.072791375** |

精确多锚值 33.072791375 元四舍五入为发布目标 **33.07 元**。JSON `rows[0].final_target=33.07`，故发布涨跌幅按同一发布值复算：

```text
upside = 33.07 / 33.02 - 1
       = 0.0015142337977
       = +0.1514% ≈ +0.15%
```

最终动作是 **中性偏多（持有/等待验证） / event-driven validation**，与几乎为零的预期回报一致，未写成买入。权重和、最终目标、舍入与 upside：**PASS**。

## Market-Implied Sentiment Anchor Checks

| Check | Recalculation / evidence | Result |
|---|---|---|
| Current-implied 2026E PE | 33.02 / 2.295653 = 14.3837x | PASS |
| Current-implied 2027E PE | 33.02 / 2.876705 = 11.4784x | PASS |
| Current-implied 2028E PE | 33.02 / 3.279608 = 10.0683x | PASS |
| Current-implied 2026/2027/2028 PS | 2,484.960149 / 1,775 / 2,000 / 2,150 = 1.4000x / 1.2425x / 1.1558x | PASS |
| PB/ROE | verified packet 无归母权益/BPS；标记 not disclosed | PASS |
| Trading-value percentile | 冻结 packet 无分位数据；标记 not disclosed，不推断 | PASS |
| Sentiment regime | 13/13 原始报告正向、仅 4 家券商重复覆盖；目标价不可用 | PASS |
| Market anchor | 33.02 元现价；无额外期权溢价 | PASS |

市场锚不是独立内在价值，不替代盈利验证；15% 权重与有限情绪证据相匹配。Market-implied sentiment anchor checks：**PASS**。

## Target-Price Comparability and Broker/Street Check

- 当前五份合并后原始报告可作 2026—2028 盈利预测对照，`forecast_weight=1.0`。
- 13 份原始 PDF 均未披露可用目标价；华泰 58.96 元仅为 `third_party_preview`，国泰海通为 `not_found`。
- 所有目标价 `valuation_weight=0`，JSON `broker_weight=0.0`；未计算原始 PDF Street 一致目标价。
- House 2026/2027/2028 归母 172.76/216.49/246.81 亿元低于 Street 中位 176.38/235.38/299.43 亿元的幅度随期限扩大，已明确披露持续期分歧。

Target-price comparability：**PASS with zero-weight Street target constraint**。

## Seasonality and Cash-Quality Checks

| Check | Recalculation | Result |
|---|---|---|
| Historical Q1 share | 2025Q1 重述 13.742 / 2025A 78.4838 = 17.5093% | PASS；仅一年观察 |
| Mechanical seasonal stress | 48.32 / 17.5093% = 275.9669 | PASS；明确禁止作为预测 |
| 2026 Base calibrated PE | 33.02 / 2.295653 = 14.3837x | PASS |
| Q2 parent NP minimum | H1 中点 101 - Q1 48.32 = 52.68 | PASS |
| Q2 adjusted NP minimum | H1 扣非中点 99 - Q1 扣非 47.67 = 51.33 | PASS |
| 2026 Base OCF | 172.762156 × 0.85 = 146.847833 | PASS，与模型 146.85 四舍五入一致 |
| 2026 simplified FCF | 146.847833 - capex 50 = 96.847833 | PASS，与模型 96.85 四舍五入一致 |

货币资金不机械加回；合同负债不视为自由现金。现金只作为保留/下调 multiple 的质量门槛。Seasonality and cash-quality checks：**PASS**。

## Growth Earnings Dependency Checks

| Required dependency | Audit result |
|---|---|
| Base/Growth split | 追溯至 `analysis/segment_forecast_bridge.md`；只作分析拆分 |
| Unit / ASP proxy | effective DWT × revenue-intensity proxy × price/mix；明确不是 vessel ASP |
| Revenue recognition | recognized revenue ratio 为情景系数，不是合同履约百分比 |
| Margin / opex / tax / minority | 通过冻结合并桥进入 parent NP/EPS |
| Scenario sensitivity | Bear/Base/Bull 与 Growth GM、确认、交付、OCF 一致 |
| Current-price-implied growth | 2026/2027/2028 隐含 NP 与 GM 缺口已披露 |
| High-growth standalone multiple | 未使用；Growth standalone EPS not disclosed |
| COSCO project | 只作去重质量证据；增量信用 0 |
| Military/Hudong/group/weak target | 全部 0 信用 |

Growth earnings dependency checks：**PASS**。

## Full-Chain / Core-Satellite and Value-Chain Checks

- R0 cycle 为 `PASS`，恰好一个 valuation parent：`N15 / 600150.SH`。
- 全部经营子公司均为 `consolidated_component`；没有独立 investable action、target 或 multiple。
- 船型 ASP、逐厂 revenue/net profit、统一 utilization、付款节点等缺口阻断 yard/ship-type SOTP。
- 在手订单只作可见性，不能直接转 revenue/EPS；中远项目不得二次加总。
- 估值方法、催化、失效与 Next-Quarter Threshold 均连接到合并交付、价格/结构、GM、归属和 OCF。

Full-chain/core-satellite dependency：**PASS**。Value-chain economics dependency：**PASS for consolidated valuation; segment/SOTP remains blocked**。

## Fake-Precision and Method-Mismatch Review

| Risk | Control | Result |
|---|---|---|
| EPS 六位小数造成伪精确 | JSON 保留冻结输入；读者目标价发布至 0.01 元并披露舍入 | PASS |
| 目标价与 upside 舍入错配 | `rows` 用 33.07 与 0.0015142337977 同口径 | PASS |
| 单季/半年年化 | 只列 stress test，未作为最终分母 | PASS |
| 现金加回 | 未机械加回货币资金 | PASS |
| 周期公司使用单一高增长 PE | 主方法为 2027E cycle-normalized PE，并用 2026/2028/现金交叉 | PASS |
| 子公司重复 SOTP | 明确只有 600150 一个 valuation parent | PASS |
| Street 弱目标价进入权重 | broker_weight=0 | PASS |
| Option value | 军品、沪东中华、集团订单均为 0 | PASS |

## Final Valuation Completeness

| Required item | Status |
|---|---|
| Current price/date, shares, market cap | PASS |
| 2026E revenue, NP and EPS | PASS |
| Business-model matched primary and secondary methods | PASS |
| Bear/Base/Bull and full math | PASS |
| Fair-value range, final target and upside/downside | PASS |
| Relative/PEG/PSG with limitations | PASS |
| Seasonality calibration and next-quarter threshold | PASS |
| Market-expectation bridge | PASS |
| Broker/Street comparison and zero target weight | PASS |
| Market-implied anchor and weights summing to one | PASS |
| Growth/full-chain dependencies | PASS |
| Catalysts, invalidation and action | PASS |

**Required fixes:** none for valuation arithmetic. R1 maker-checker and downstream R2—R4 publication gates remain outside this arithmetic PASS；本结论不代表整份报告已可发布。

`Model Reproducibility: PASS`
