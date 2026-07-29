# Source Registry

数据截止：2026-07-22 CST。详细结构化登记见 `source_registry.json`。

| ID | 来源 | 层级 | 用途 | 关键边界 |
|---|---|---|---|---|
| HY-OFF-2025AR | 2025 年报 | L1 official | 历史财务、分部、产能、债务、担保 | 行业数据仍是公司引用口径 |
| HY-OFF-2026Q1 | 2026Q1 | L1 official | Q1 利润、现金流、资产负债表 | 未审计、无项目利润拆分 |
| HY-OFF-2026H1P | H1 业绩预告 | L1 official unaudited | 55--60 亿元归母及驱动 | 预告、待追溯调整 |
| HY-OFF-P2 | 文莱二期进展 | L1 official | 产能、工期、税惠与融资意向 | 不等于完整金融交割 |
| HY-OFF-CB | Q2 转股结果 | L1 official | 股本、转债本金、转股价 | Q3 后续转股未知 |
| HY-OFF-DIV | 分红实施 | L1 official | 回购库存股口径 | 登记日后可变化 |
| HY-OFF-ESOP7 | 第七期员工持股计划 | L1 official | 最多 1.508 亿股、12.43 元/股、股份支付 | 最终认购/过户及费用不确定 |
| HY-OFF-RATING | 跟踪评级 | L1 archived / agency | 刚债、短债、项目支出 | 非审计列报口径 |
| HY-MKT-QUOTE | AStock 行情快照 | realtime | 15.06 元盘中价、量价 | 非收盘；错误零值估值已剔除 |
| HY-MKT-KLINE | 前复权历史 | L2 | 年度高低、短期成交 | 非交易所官方文件 |
| HY-BRK-GUOXIN | 国信原始 PDF | original PDF | 预测、目标区间、FCFE | 券商判断，重新稀释股本 |
| IND-IEA-202607 | IEA OMR 摘要 | L1 excerpt | 全球油品与裂解环境 | 公开摘要，非公司利润 |
| IND-EIA-202607 | EIA STEO | L1 forecast | Brent 情景 | 预测，不是实现值 |
| IND-NBS | 国家统计局 | L1 | 化纤产量、行业利用率 | 不能套用公司装置 |
| IND-PTA-202606 | 商务预报转载 | L2-L3 | PTA/聚酯开工、库存、加工费 | 原始资讯机构未具名 |
| IND-CZCE | 郑商所材料 | L1 methodology | 物耗和价差方法 | 理论公式，不是公司成本 |
| IND-PEERS | 五家可比公司年报 | L1 | 产能与模式比较 | 口径不同，不直接排名利润 |
| IND-BRUNEI | 文莱政府网站 | L1 context | 税制、汇率、项目背景 | 公司税惠仍以年报为准 |
| IND-SSE-FREIGHT | 上海航交所 | L1 benchmark | 运费外部锚 | 非公司实际运费 |

## 治理结论

目标价使用的正权重外部研究仅为已归档且哈希核验的国信证券原始 PDF。媒体转述、搜索摘要、付费墙和未具名行业转载不承担核心公司利润证明。行业开工、价差和库存只作为情景验证，不能替代公司分部利润。
