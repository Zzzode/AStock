# 价值链经济学与估值信用

单位均为人民币；`not disclosed` 不是零，也不以行业常识填补。数据主要来自 S1（公司 2025 年年报）。

| chain_block | value_amount_or_proxy | ASP_or_price_proxy | margin_pool | supply_demand_state | capacity | utilization_or_yield | customer_certification | order_or_backlog_visibility | economics_source | evidence_gap | valuation_credit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 智能座舱 | 2025 收入 CNY20.585bn；新项目订单年化 >CNY20bn | 单车/项目 ASP `not disclosed` | 2025 毛利率 18.83%；毛利约 CNY3.876bn（收入减成本） | 已实现收入增长；订单为未来潜在需求 | 量产工厂网络有披露，设计产能 `not disclosed` | `not disclosed` | 产品/客户认证与车型映射 `not disclosed` | 有具名客户的新订单及已配套，未披露 backlog/SOP | S1 | 客户收入、车型、ASP、项目毛利/回款缺失 | 可使用已确认分部收入/毛利；订单增量 `watchlist only` |
| 智能驾驶 | 2025 收入 CNY9.700bn；新项目订单年化 >CNY13bn | 域控/传感器/算法 ASP `not disclosed` | 2025 毛利率 16.36%；毛利约 CNY1.586bn；同比 -3.55pct | 智驾收入同比 +32.63%，成本同比 +38.52% | 高算力域控/摄像头/4D 雷达工艺突破；数量产能 `not disclosed` | `not disclosed` | 部分系统 ASIL D 认证；项目/车型认证 `not disclosed` | 多 OEM 域控已大规模量产；订单年化非 backlog | S1 | SoC/BOM、客户/车型、ASP、软件收费、项目毛利和利用率缺失 | 已确认分部收入/毛利可用；高阶智驾/订单转化不可给估值信用 |
| 网联服务及其他 | 2025 收入 CNY2.272bn | 软件服务/订阅 ASP `not disclosed` | 分部毛利率 `not disclosed` | 与多家 OEM 持续合作，服务需求有证据 | 主要是研发/交付能力，容量口径 `not disclosed` | 不适用/`not disclosed` | 网络安全、OTA 等具体认证 `not disclosed` | 战略合作存在；合同年限/订单额 `not disclosed` | S1 | 收费模式、续费率、客户份额、毛利率缺失 | `watchlist only / insufficient economics`，不单列软件高估值 |
| 中央计算与第五代座舱 | 国内多家头部客户订单；项目已定点/开发中 | `not disclosed` | `not disclosed` | 技术选型窗口存在，未验证收入 | `not disclosed` | `not disclosed` | 产品级认证/客户资格 `not disclosed` | 订单/定点，无客户实名、SOP、金额或收入 | S1、S2 | 所有经济学关键字段缺失 | 仅长期可选性；`blocks valuation: true` |
| 显示、HUD、区域控制器 | 量产中控副驾一体屏；HUD/区域控制器获部分客户订单 | 尺寸、分辨率与单车 ASP `not disclosed` | 产品级毛利 `not disclosed` | 部分量产/订单 | 产线/能力有披露，产能 `not disclosed` | `not disclosed` | 项目认证 `not disclosed` | 奇瑞/吉利量产显示；多个 OEM 订单；AR-HUD 即将量产 | S1 | BOM、ASP、SOP、客户收入和项目毛利缺失 | 只作为产品结构验证，不做增量估值 |
| 上游材料/BOM | 原材料 CNY24.183bn，占营业成本 91.78% | SoC、存储、显示、传感器与连接器价格 `not disclosed` | 影响座舱/智驾两分部毛利 | 供给状态与锁价 `not disclosed` | 供应商产能不适用 | 供应商交付/良率 `not disclosed` | 车规认证有重要性，但供应商映射 `not disclosed` | 前五供应商采购额 41.13%，供应商匿名 | S1 | 供应商名称、采购价、用量、锁价、替代认证缺失 | 可做方向性风险，不做精确成本敏感性 |
| 制造与营运资本 | 销售 40.346m 套；生产 43.041m 套；期末库存 6.569m 套 | 不适用 | 固定成本吸收与减值风险取决于利用率/产品结构 | 订单和备货上升；库存同比 +69.59% | 惠南二期投产、成都建设、墨西哥首个量产、西班牙设备安装 | `not disclosed` | IATF 16949、ISO 26262 等体系披露；项目级认证 `not disclosed` | 生产/销售量已披露；各厂订单和利用率未披露 | S1 | 设计产能、利用率、良率、单厂现金回报缺失 | 汇总营运资本和现金流可用；“产能→收入”不可用 |
| 回款与现金 | 应收 CNY9.778bn、存货 CNY4.789bn、合同负债 CNY1.005bn、经营现金流 CNY2.884bn | 不适用 | 现金转换受账期、库存、减值、供应链付款影响 | 经营现金流同比 +93.09%，但营运资本余额高 | 不适用 | 不适用 | 不适用 | 无可审计 backlog；收入确认遵循交付/客户控制权 | S1 | 客户/产品账期、专用库存、降价和减值拆分缺失 | 历史现金流可用；客户项目 DCF `watchlist only` |

## 经济学判断

1. **收入与毛利：** 智能座舱和智能驾驶已经形成可审计的收入/毛利池，故可供汇总预测与估值校验。智驾收入增长更快而毛利率更低，模型须显式设置毛利率，不能用“更高算力”自动上调利润率。
2. **ASP：** 公司没有披露单车、车型、项目或客户 ASP。所有以“屏数/算力/NOA 渗透率 × ASP”生成的收入都应标为未验证情景，不得进入 base case。
3. **产能：** 工厂投产/建设是交付能力线索；没有利用率、良率、客户资格、订单或价格，不能换算销售额。

The value-chain boundary is explicit: ASP, margin, capacity, utilization and order fields are monitored, while valuation credit is granted only to reported revenue, profit and cash-flow evidence.
4. **现金：** 专用订单生产提高项目匹配度，也使车型变动时库存减值成为直接风险。应收、存货、合同负债和 CFO 是后续季报的必要验证指标。
