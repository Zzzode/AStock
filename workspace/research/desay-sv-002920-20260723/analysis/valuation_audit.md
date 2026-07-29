# Valuation Audit

## Arithmetic and price/share reconciliation

| Item | Calculation | Result | Check |
|---|---|---:|---|
| Current price | 2026-07-23 intraday market snapshot | CNY83.48 | PASS |
| Shares outstanding | 2025 annual-report post-issuance share capital | 5.96809294 亿股 | PASS |
| Market cap | CNY83.48 × 5.96809294 亿股 | CNY49.822bn | PASS |
| Base EPS | CNY2.80bn / 5.96809294 亿股 | CNY4.6916 | PASS |
| Base intrinsic value | CNY4.6916 × 18.5x | CNY86.795 | PASS |
| Base-business multi-anchor value | 80% × CNY86.8 + 20% × CNY85.0 + 0% Street | CNY86.44 → CNY86.4 | PASS |
| Physical AI risk-adjusted option | 35% × CNY2.95 / 1.12² + 10% × CNY20.94 / 1.12² | CNY2.49 | PASS |
| Final blended target | CNY86.44 + CNY2.49 | CNY88.93 → CNY88.9 | PASS |
| Upside | CNY88.9 / CNY83.48 - 1 | +6.49% → +6.5% | PASS |

## Forecast availability and method fit

- **Reported base:** 2025A CNY32.557bn revenue, CNY2.454bn attributable profit; 2026Q1 CNY6.495bn revenue, CNY0.461bn attributable profit.
- **External forecast:** 开源证券原始 PDF 的 2026E CNY38.400bn revenue / CNY2.914bn NP / EPS CNY4.88；保留为外部交叉检查。
- **House base:** CNY38.0bn / CNY2.80bn / EPS CNY4.69，低于外部预测以反映客户/ASP/订单确认和智驾毛利率缺口。
- **Method fit:** 已盈利的系统级汽车电子供应商适用 forward P/E，次要检查为分部收入/毛利率、现价隐含 P/E 和公开预测；不以未披露的高成长分部作为全公司 PS/PEG 分母。

## Scenario-band and market-implied checks

| Check | Result |
|---|---|
| Bear < Base < Bull | CNY69.1 < CNY86.8 < CNY105.6, PASS |
| 2026E implied P/E at current price | 17.8x House base EPS / 17.1x public EPS, PASS |
| Bubble degree | Current/base - 1 = -4.0%, PASS |
| Final weights | fundamental 0.80 + market 0.20 + broker 0.00 = 1.00, PASS |
| Broker target treatment | original profit forecast present; target/method unavailable; zero weight and source exhaustion recorded, PASS |
| Physical AI option arithmetic | 55% / 35% / 10% mutually exclusive probabilities sum to 100%; FY2028 values discounted at 12% for two years; expected value CNY2.49, PASS |

## Supply-chain and growth dependency audit

| Dependency | Status | Consequence |
|---|---|---|
| 已披露产品线收入、客户/平台量产描述 | PASS | 支持座舱/智驾存量盈利信用 |
| 订单年化销售额 | CONDITIONAL | 仅作需求可见度；不能直接入收入/EPS |
| 客户/车型份额、ASP、单项目毛利、利用率 | not disclosed | 不给新增产品精确 EPS 贡献 |
| 智驾收入/毛利率 | PASS with risk | 2025A 有收入和 16.36% 毛利率，仍需中报验证 |
| 中央计算、AR-HUD、区域控制器、机器人 | base EPS optionality | 不进基准 EPS；Physical AI以单列CNY2.49风险调整期权进入最终综合参考值 |

## Physical AI option-value audit

| Check | Result | Conclusion |
|---|---|---|
| Scenario exclusivity | 55% no conversion + 35% first commercial scale + 10% platform scale = 100% | PASS |
| First-commercial-scale arithmetic | CNY1.0bn × 8% / 0.5968bn shares × 22x = CNY2.95; / 1.12² = CNY2.35; ×35% = CNY0.82 | PASS |
| Platform-scale arithmetic | CNY5.0bn × 10% / 0.5968bn shares × 25x = CNY20.94; / 1.12² = CNY16.69; ×10% = CNY1.67 | PASS |
| Risk-adjusted value | CNY0.00 + CNY0.82 + CNY1.67 = CNY2.49 | PASS |
| Evidence permission | Product, nomination, planned delivery, S6 order language, POC and cooperation are not treated as 2026E revenue/EPS | PASS |
| Probability quality | AStock house probabilities, explicitly low confidence and tied to G1--G4 evidence gates; not company guidance or consensus | PASS with low-confidence label |

## Fake-precision and reproducibility conclusion

基础业务模型仅保留与披露和公开预测可对齐的收入、利润、股本、P/E 和权重。Physical AI概率不伪装为披露事实：其CNY2.49被单独标记为低置信度本院真实期权假设，且没有客户金额、车型份额或单车 ASP 的小数化预测。所有情景值按 CNY0.1bn、EPS CNY0.01 和股价 CNY0.1 四舍五入。

**Model Reproducibility: PASS**

从 `data/current_valuation_model_20260723.json`与`data/physical_ai_option_model_20260723.json`的价格、股数、收入、利润、EPS、倍数、基础权重、期权情景、概率和折现率可复算市值、三档基础业务价值、CNY2.49期权、最终目标和涨跌幅；误差仅来自显示四舍五入。
