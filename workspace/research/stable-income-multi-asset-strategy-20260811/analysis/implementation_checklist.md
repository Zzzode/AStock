# 执行清单与12个月治理节奏

## 建仓前（必须全部回答）

1. 确认本报告的资金口径：固定CNY200,000就是全额投资本金 $V$，不从中扣除家庭安全垫；并确认未来至少五年不把这笔 $V$ 改作确定支出。
2. 是否存在信用卡循环、高息消费贷、融资、担保或家庭债务？如有，先处理债务。
3. 最大可承受账面回撤和最长可不动用期限分别是多少？是否能承受基准稳健核心压力线约-16.3%（REITs激活后约-17.3%）？
4. 现金分配默认全部再投资；若以后主动改为消费用途，应暂停本策略的自动追加并单独制定取现计划。
5. 已有房产、社保、保险、存款、基金和职业收入是否已经隐含金融、能源或地产暴露？
6. 本人风险测评、账户权限、税务身份、个人养老金资格是否匹配？
7. 每只ETF的最新合同/概要、费率、跟踪指数、前十大、行业权重、规模、成交、折溢价和做市状态是否已复核？
8. 是否确认黄金本身不生息、任何基金非固定分配也不计入生活收入预算，且明确放弃期货和任何杠杆形式？

## Designated model portfolio and product validation

- The active model targets are: protected liquidity CNY40,000; staging cash CNY10,000; 511010 CNY70,000; 510880 CNY30,000; conditional 512890 CNY30,000; and 518880 CNY20,000. Public REITs and direct stocks are CNY0 at launch.
- Establish the protected-liquidity, cash and validated 511010 sleeves at T0. Build 510880, eligible 512890 and 518880 over six tranches: CNY5,000 / CNY5,000 / CNY3,333 in months 1--5 and CNY5,000 / CNY5,000 / CNY3,335 in month 6.
- If a sleeve fails its execution-day test, defer only that sleeve to eligible protected liquidity under `data/model_portfolio_implementation_20260812.json`; do not substitute a correlated product, increase 511010, breach the CNY10,000 staging-cash cap or force the target weight.

## 建仓和产品核验

- 组合内受保障流动性和债券层先完成；风险资产按六个月固定节奏实施。
- 每只场内基金按 `data/execution_eligibility_policy_20260812.json` 独立核验同一市场时段的来源、时间戳、IOPV/参考值、折溢价、盘口价差、成交活跃度、停复牌与当日公告；缺任一字段或未通过受控阈值时，$q=0$。
- 红利ETF组合持仓合并后做行业和前十大集团穿透；512890未通过总组合25%行业或权益桶35%前十大集团阈值时保持0，CNY30,000唯一留在受保障流动性。
- REITs必须逐只核验项目收入、债务、出租率/收费量、运营方、可分配金额质量、估值、二级市场溢价、流动性与最小交易单位；少于三只独立项目通过或任一项目缺失即为0%。
- 本清单同时定义模型持仓目标与研究治理步骤；它不提供即时下单价格、数量、通道或自动交易指令。

## 复核节奏

| 频率 | 必查项目 | 可能动作 |
|---|---|---|
| 月度 | 组合内流动性权重、账户/机构集中度、费用变动、赎回可得性 | 修复流动性偏离；不因短期涨跌调整风险预算 |
| 季度 | ETF合并持仓、行业集中、基金规模/规则、债券久期/信用、黄金折溢价 | 暂停超限产品新增；更新税后现金流表 |
| 半年 | 权重偏离、回撤和投资目标 | 按阈值再平衡，优先使用新资金/分配 |
| 年度 | 年追加金额、个人养老金资格、债务或资金用途变化 | 重选保守/基准/增长版本 |

## 事件触发器

本金性质改变为三年内需动用、组合内受保障流动性偏离目标超过5个百分点、交易现金超过CNY10,000或在分批期内低于目标、红利削减或现金流恶化、债券信用/久期漂移、基金暂停申赎、异常溢价、产品规则/费用变化，或已记录的实际$DD_t$达到复核线，均要求停止自动风险加仓并重新完成本清单。压力情景数值本身不是实际$DD_t$。
