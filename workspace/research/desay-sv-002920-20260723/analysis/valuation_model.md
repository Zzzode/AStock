# Valuation Model — 德赛西威（002920.SZ）

## Final Valuation Table

| Ticker | Current price / date | Shares | Market cap | 2026E revenue | 2026E NP / EPS | Method | Bear / Base / Bull | Final target | Upside | Action | Evidence quality |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|---|
| 002920.SZ | CNY83.48 / 2026-07-23 intraday | 5.968 亿股 | CNY49.82bn | CNY38.0bn | CNY2.80bn / CNY4.69 | base forward P/E + risk-adjusted Physical AI real option | CNY69.1 / CNY86.8 / CNY105.6 base business | **CNY88.9** | **+6.5%** | market-supported watch / event-driven validation | 2025A products/customer facts high; 2026E base model conditional; Physical AI option low confidence |

选择前瞻 P/E 是因为公司已有盈利、三条产品线已形成收入和公开 EPS 参照；次要检查为分部收入/毛利桥与当前价隐含 P/E。我们不用 PS 给整个公司赋高成长溢价：智能驾驶虽增长较快，但产品和客户级 ASP、收入确认与利润率未披露，且 2025A 智能驾驶毛利率低于座舱。Physical AI不改变该基础P/E分母，而以单列、概率加权并折现的真实期权层进入最终参考值。

## Three-Tier Targets

| Scenario | Revenue (CNYbn) | NP (CNYbn) | EPS (CNY) | P/E (x) | Value (CNY) | Bubble degree vs base |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 35.5 | 2.50 | 4.19 | 16.5 | 69.1 | -20.4% |
| Base | 38.0 | 2.80 | 4.69 | 18.5 | 86.8 | 0.0% |
| Bull | 40.0 | 3.15 | 5.28 | 20.0 | 105.6 | +21.7% |

熊市对应收入放缓、智驾毛利率受压和营运资本占用；基准对应中双位数收入增长及毛利率不继续恶化；牛市要求量产和产品上移同时兑现。现价相对于 CNY86.8 基本面基准的 bubble degree 为约 -4.0%，并非极端泡沫，也因此缺少在证据未升级前大幅上调倍数的理由。

上表是**汽车电子基础业务**的三档价值，而非把机器人/低速无人车混入2026E EPS。最终显示目标在该基础上叠加风险调整后的Physical AI期权，故CNY86.8仍是基础业务基准，CNY88.9才是包含未来机会权重后的综合参考值。

## Relative / PEG / PSG Comparison

| Cross-check | Observation | Valuation implication |
|---|---|---|
| Public 2026E EPS | 开源证券 CNY4.88；现价隐含约 17.1x | 市场以中高增速成长 Tier-1 的区间定价，不是明显低估 |
| House base EPS | CNY4.69；现价隐含约 17.8x | 本院基准较公开预测保守，源于量产/ASP/利润率证据缺口 |
| Segment mix | 座舱为 2025A 收入 63.23%，智驾为 29.79% | 不应用纯软件或纯智驾 PS/PEG 到合并收入 |
| Quality cross-check | 2025A 毛利率：座舱 18.83%，智驾 16.36% | 收入组合变动需要与毛利/现金流一起评估 |

PEG / PSG 不是主方法：公司缺少可审计的产品级增长持续期和细分纯度，使用它会制造精确感而不是提高可比性。

## Seasonality Calibration

2025A 收入 CNY32.557bn、归母 CNY2.454bn；2026Q1 收入 CNY6.495bn、归母 CNY0.461bn，同比均下降，不能把该季度机械年化。基准全年收入 CNY38.0bn、归母 CNY2.80bn 的含义是后续季度恢复交付和确认，但没有假定超过年报和公开盈利预测能够支撑的产品/客户细节。公开预测 CNY38.40bn/CNY2.914bn 是外部参照，不能代替公司正式中报。

## Next-Quarter Threshold

| Validation item | Upgrade threshold | Downgrade threshold |
|---|---|---|
| Revenue | 正式中报显示全年收入可回到中双位数增长轨道 | 连续低个位数增长或较基准明显落后 |
| Intelligent driving margin | 16.36% 2025A 毛利率企稳或改善，并能解释产品/成本变化 | 毛利率继续显著下滑且没有可审计的成本恢复路径 |
| Cash conversion | 经营现金流与收入增长匹配，存货/应收不异常快于销售 | 存货或应收累积、经营现金流明显弱于利润 |
| Platform proof | 客户、车型、量产、价值量或收入确认至少闭合一条新增产品链 | 只有定点/订单新闻，仍无收入、ASP、毛利证据 |

## Method and Assumption Bridge

- **Primary method:** 2026E forward P/E, 16.5x / 18.5x / 20.0x；适合已盈利、产品为硬件+软件系统交付且行业成长/竞争并存的 Tier-1。
- **Secondary check:** 2025A 产品线收入/毛利率、公开 EPS、现价隐含 P/E 与市值/股本一致性。
- **Base assumptions:** CNY38.0bn revenue、CNY2.80bn NP、CNY4.69 EPS；不把订单年化销售额、客户名单、中央计算/AR-HUD/机器人定点直接转为收入。
- **Catalyst needed:** 中报验证收入、智驾毛利率及现金转换；新平台出现可审计的量产/收入字段。
- **Invalidation:** 交付放缓、智驾毛利率下行、营运资本恶化、客户/芯片/海外风险转化为业绩偏差。

## Physical AI Risk-Adjusted Option Layer

用户的研究问题是未来机会而非仅当前合理价值，故本模型将Physical AI明确写入估值体系，但不把未披露新业务收入伪装为2026E利润。方法是**基础业务P/E + 风险调整真实期权（ROV）**：以FY2028可能形成的独立收入/利润池估算条件价值，按12%折现两年，并以一手披露成熟度给出本院概率。概率是本院假设、不是公司指引或一致预期。

| FY2028结果（互斥） | 概率 | 收入 / 净利率 / P/E | FY2028条件价值 | 两年后现值 | 概率加权现值 |
|---|---:|---|---:|---:|---:|
| 未形成可计量商业化 | 55% | CNY0bn / -- / -- | CNY0.00 | CNY0.00 | CNY0.00 |
| 首次商业化规模 | 35% | CNY1.0bn / 8% / 22x | CNY2.95 | CNY2.35 | CNY0.82 |
| 可复制平台规模 | 10% | CNY5.0bn / 10% / 25x | CNY20.94 | CNY16.69 | CNY1.67 |
| **Physical AI风险调整期权** | **100%** | -- | -- | -- | **CNY2.49** |

概率的约束如下：公司披露AI Cube、机器人域控定点与规划2026量产、川行致远产品/订单和生态合作，因而期权不是零；但客户、实际交付、单位、收入、毛利和现金均未披露，因而55%分配给未转化，平台化概率仅10%。CNY1.0bn和CNY5.0bn是条件情景，非管理层收入预测。若2026量产没有实际交付/验收，或后续仍没有商业化字段，应下调35%和10%分支；反之，G1客户身份、G2交付转换、G3单位经济和G4复制性逐步提高可估值性。

| 最终两层估值桥 | 每股价值（CNY） | 处理 |
|---|---:|---|
| 汽车电子基础业务多锚价值 | 86.44 | 0.8×基础内在价值86.8 + 0.2×市场锚85.0；不包含Physical AI增量EPS |
| Physical AI风险调整期权 | 2.49 | FY2028条件价值按12%折现、概率加权；不计入2026E EPS |
| **综合本院参考值** | **88.93，显示为CNY88.9** | **较CNY83.48为+6.5%；行动为market-supported watch / event-driven validation** |

## Market-Expectation Valuation Bridge

市场在 CNY83.48 已对公开 2026E EPS CNY4.88 支付约 17.1x P/E。基础目标的上行并非依赖多倍数扩张，而取决于收入恢复增长与利润率守住；牛市上行需要收入、毛利和产品平台三者共同上修。最终综合值再以CNY2.49体现Physical AI的风险调整未来机会，但不声称市场已经或尚未为该期权支付了确切金额。换言之，投资者支付的是“座舱存量 + 智驾增长 + 量产执行”，并可能获得一份低概率、高凸性的Physical AI期权。

## Broker/Street Comparison

| Broker | Date | Rating | 2026E Revenue / NP / EPS | Target / method | Source quality | Valuation use |
|---|---|---|---|---|---|---|
| 开源证券 | 2026-03-08 | 买入 | CNY38.400bn / CNY2.914bn / CNY4.88 | not disclosed / not disclosed | original_pdf | 盈利预测交叉检查；目标价权重 0 |

截至截止日，本案例未取得可审计的原始券商目标价及估值方法字段，因此没有将媒体转载、搜索摘要或内部推断伪装成 Street target。具体探测记录见 `source_exhaustion_log.md`；该限制降低目标价置信度，但不会阻止基于公开预测、公司披露和多情景的区间估值。

## Market-Implied Sentiment Anchor

| Anchor | Value (CNY) | Weight | Rationale |
|---|---:|---:|---|
| Fundamental / intrinsic | 86.8 | 80% | 基准 EPS CNY4.69 × 18.5x；需要中报验证 |
| Market-implied sentiment | 85.0 | 20% | 接近 17.4x × 公共 2026E EPS CNY4.88；认可当前成长估值但不给无证据溢价 |
| Broker/Street target | not disclosed | 0% | 有原始盈利预测，但无可审计目标价/估值法 |
| Base-business multi-anchor value | **86.4** | **100%** | 0.8×86.8 + 0.2×85.0，四舍五入；不含Physical AI |
| Risk-adjusted Physical AI option | **CNY2.49** | separate layer | FY2028条件价值按12%折现并概率加权 |
| Final blended house target | **CNY88.9** | **100%** | CNY86.44 + CNY2.49 = CNY88.93，四舍五入 |

这不是机械的“内在价值低于市场即卖出”。当前价接近可验证的基本面与市场锚，加入风险调整期权后也只有约6.5%的综合上行，适合 `market-supported watch / event-driven validation`：在中报前等待经营验证、Physical AI的G1--G3证据或更有安全边际的回撤；若市场情绪溢价明显扩大而业绩/毛利/商业化未跟上，行动转为 `sentiment premium breaking`。

## Growth Earnings Dependency

估值依赖 `analysis/growth_earnings_model.md`与`analysis/physical_ai_growth_model.md`：座舱为基础业务，智驾为增长业务；本院以收入代理而非未披露单位/ASP，基础业务不计中央计算、AR-HUD、区域控制器和机器人收入。Physical AI在不进入2026E EPS的前提下，以单列风险调整期权给予CNY2.49估值信用；若这些产品未来出现单位、ASP、确认比例、毛利和增量费用的可审计披露，才以实际盈利桥替换概率情景。

## Full-Chain Classification Dependency

德赛西威是本案例唯一 `core_valuation` 公司；上游芯片、显示、传感器、软件和下游 OEM 是关系/需求节点，不被估值为本公司收入。估值资格来自已有产品收入、年报客户/量产描述及产品线毛利率；逐客户收入、订单金额、ASP、产能利用率的缺口已在客户链审计和 coverage gap matrix 中记录，并限制目标价上行幅度。
