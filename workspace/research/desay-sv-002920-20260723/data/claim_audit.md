# 卖方主张审计

机器可读版本：`data/claim_audit.json`；共 12 条高影响主张。所有主张均禁止直接进入目标价数学。

| ID | 可采用表述 | 证据层级 | 估值后果 |
|---|---|---|---|
| BRK-001 | 辉立曾给 CNY147 历史目标价 | original_pdf | context only |
| BRK-002–004 | 开源、东吴、中银分别披露的盈利预测 | original_pdf | cross-check only |
| BRK-005–007 | 公开快照的评级计数、EPS均值和离散区间 | auditable snapshot | context only |
| BRK-008 | 当前原始PDF未给目标价 | original_pdf | blocks target anchor |
| BRK-009–010 | 申万转载摘要的预测与看多逻辑 | media repost | context/watchlist only |
| BRK-011 | 辉立历史目标的报告日隐含涨幅 | original_pdf | context only |
| BRK-012 | 无人车、机器人、海外属于待核验催化剂 | broker assertions | watchlist only |
| PAI-001 | 2025年汽车智能驾驶收入CNY9.700bn、同比+32.63%，是能力与交付底座 | issuer primary | 仅作为已实现汽车智驾经济性，不重复计为机器人/无人车收入 |
| PAI-002 | AI Cube已发布为机器人AI计算终端 | issuer primary | 产品技术期权，零收入/EPS信用 |
| PAI-003 | 机器人域控有定点、规划2026量产交付 | issuer primary | 2026里程碑期权；计划非实际量产，零基础EPS |
| PAI-004--005 | 川行致远S6已发布且有未具名相关客户订单 | issuer primary | 有条件商业期权；不得把订单写成backlog、收入或EPS |
| PAI-006--007 | Thor POC及与元戎启行L4合作成立 | issuer primary | 技术/生态催化剂；无项目、SOP或经济学信用 |

对客户、订单、SOP、ASP、利用率与利润率的券商表述，必须由公司或客户侧一手材料另行闭环，不能因本文件的原始PDF身份而自动获得估值信用。
