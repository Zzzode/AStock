# 客户链与高影响经营主张审计

- Gate: **CONDITIONAL**.
- Authoritative structured rows: `data/customer_chain_audit.json`.
- Rule: certification/equity linkage is not an order; capacity is not sales; broker estimates retain broker wording.

## Source keys

- S1: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/data/raw_a_share_h1_2026_preview_20260715.json`; official-preview table, original announcement URLs not captured.
- S2: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/600150-中国船舶/2026-07-14-华源证券-26H1预告点评-Q2业绩预计同比大增-关注后续船价与集团整合.pdf`.
- S3: `workspace/research/low-position-capital-layout-20260711/sources/launched-official-20260711/301308_H1_guidance_20260703.pdf`; Eastmoney notice infocode `AN202607031826702637`.
- S4: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/301308-江波龙/2026-05-07-国信证券-1Q26归母净利润同比增长2644.05-端侧应用多维拓展.pdf`.
- S5: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002812-恩捷股份/2026-07-10-东吴证券-26H1业绩预告点评-Q2业绩超我们预期-隔膜供需紧张盈利持续提升.pdf`.
- S6: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002240-盛新锂能/2026-07-09-东吴证券-26H1业绩预告点评-Q2锂盐出货高增-自有矿贡献利润.pdf`.
- S7: `workspace/research/a-share-double-upside-screen-20260722/sources/official-20260722/002497_2025_annual_report.pdf`, `002497_2026_q1_report.pdf`, `002497_2026_h1_earnings_preview.pdf`; CNINFO originals locally archived, exact download URLs pending source registry.
- S8: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002497-雅化集团/2026-07-08-东吴证券-26H1业绩预告点评-Q2锂盐量利齐升-略超我们预期.pdf`.
- S9: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/300390-天华新能/2026-06-06-华源证券-氢氧化锂龙头-深度绑定大客户-锂资源加速布局.pdf`.

## Audit rows

| ticker | company | customer_or_platform | claim_type | product_or_process | certification_status | order_or_backlog | ASP_or_price_proxy | capacity | utilization_or_yield | revenue_exposure | margin_impact | source_tier | evidence_score | source | evidence_gap | blocks_valuation | downgrade_trigger | adopted_wording |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|
| 600150 | 中国船舶 | 未命名船东/民船订单 | order_backlog_and_price | 民船建造交付 | not found；非模型前提 | 官方确认订单充足；金额未披露 | 单船均价同比提升 | 有效产能未披露 | 任务饱满；数值未披露 | 造船核心；并表可比占比缺失 | H1归母92--110亿元，量/结构/均价提升 | L1-derived | 88 | S1 | 订单金额、客户、船型毛利、利用率 | false | 交付/回款走弱或毛利连续回落 | 公司确认订单和均价改善；只按总量交付估值 |
| 600150 | 中国船舶 | 全球造船市场 | delivery_horizon | 高价订单交付 | n/a | 券商称排至2028--2030 | 船价指数182.08→185.39 | 船厂产能紧张 | not disclosed | not separately disclosed | 华源2026E毛利16.84%/归母181.98亿元 | L3 | 74 | S2 | 公司订单金额/订单经济性 | false | 行业订单/船价反转且公司毛利不跟 | 保留券商措辞，仅作能见度辅助 |
| 301308 | 江波龙 | 多家全球晶圆原厂 | upstream_supply_agreement | LTA/MOU晶圆采购 | n/a | 上游协议确认；名称/量/价未披露 | not disclosed | 下游封测产能未披露 | not disclosed | 无协议关联收入拆分 | 保障供应但采购成本/毛利未量化 | L1-derived | 82 | S3 | 供应商、承诺量、采购ASP、条款 | true | 替换成本上升时协议不能保护毛利 | 上游供货协议不表述为下游订单或锁定毛利 |
| 301308 | 江波龙 | AMD、鲲鹏、海光、飞腾、未命名客户 | platform_qualification | eSSD/RDIMM/端侧AI存储 | AMD联合调优官方；四平台认证券商 | 下游订单未披露 | not disclosed | 自有封测；数值未披露 | not disclosed | 券商称2025企业级17.83亿元；认证关联份额未披露 | 产品结构或改善毛利，但转量未量化 | L1-derived + L3 | 68 | S3+S4 | 客户采购、订单、出货、ASP、利用率 | true | 认证不转出货/收入/现金流 | 认证只作技术进展，不作订单证明 |
| 002812 | 恩捷股份 | 未命名电池客户 | volume_price_margin_recovery | 湿法隔膜 | not disclosed | not disclosed | 官方称价格企稳回升 | 公司称调配产能；数值未披露 | not disclosed | 隔膜核心；份额未复核 | 官方确认量增、单位成本下降和毛利改善 | L1-derived | 76 | S1 | 客户、订单、出货、ASP、单平、产能、良率 | true | H2价格或单位经济反转 | 只写方向改善，不写未披露客户/单平/利用率 |
| 002812 | 恩捷股份 | 未命名大客户/海外/3C | price_pass_through_and_unit_profit | 湿法隔膜/新线 | 验证约束供给；状态未披露 | not disclosed | 券商称PE涨价20%--30%，部分未落地 | 券商估2027有效产能220亿平 | 2026/27利用率90%/97%；良率缺失 | 2026E营收200.58亿元 | Q2调整后0.15元/平、出货41--42亿平 | L3 | 64 | S5 | 同源量/利/利用率，客户和良率缺失 | true | Q3单平<约0.12元、涨价延迟或良率不及预期 | 全部标为东吴估计并折价 |
| 002240 | 盛新锂能 | 未命名电池材料客户 | lithium_price_volume_and_indonesia_ramp | 锂盐冶炼 | not disclosed | not disclosed | 售价同比大涨；实现价未披露 | 印尼产能释放；名义数值缺失 | not disclosed | 锂盐主驱动 | H1归母10--12亿元、扣非13--15亿元 | L1-derived | 80 | S1 | 客户/订单、ASP、印尼利用率、自供比、现金 | false | 锂价/印尼量反转且OCF持续负 | 只用于商品量价模型，不给客户溢价 |
| 002240 | 盛新锂能 | not disclosed | shipment_and_unit_profit | 锂盐出货 | not disclosed | not disclosed | Q2锂价中枢环比+2万元/吨 | 印尼贡献增量；木绒2028排除 | 印尼利用率未披露 | 2026E营收150.49亿元 | Q2出货3万吨+、综合吨利约2万元 | L3 | 65 | S6 | 公司确认的吨位/吨利/利用率/客户 | false | Q3出货<约3万吨、吨利<约2万元或OCF负 | 吨位吨利为券商估计，仅作敏感性 |
| 002497 | 雅化集团 | Tesla、SK ON、LGES、LGC、宁德时代等 | named_customer_and_sales_contract | 电池级氢氧化锂/碳酸锂 | 头部供应链及溯源体系披露 | 重大合同正常履行；2026客户量未披露 | H1均价提升；实际ASP未披露 | 综合产能近13万吨 | 2025产6.86/销6.95万吨；同口径利用率缺失 | 2025锂收入48.24亿元，头部客户占锂收入90%+ | 2025锂毛利12.22%；H1量价成本改善 | L1 | 96 | S7 | 2026客户量、ASP、库存/套保、自供比 | false | 合同履行/出货不及预期或客户集中压价 | 确认客户与合同，不推断2026单客户量价 |
| 002497 | 雅化集团 | 中铁建、中电建、中建材、神华等 | civil_explosives_customer_capacity_and_utilization | 民爆产品/爆破矿服 | 许可和矿服资质披露 | 战略合作/项目暴露；backlog金额未披露 | not disclosed | 炸药26.25万吨；雷管8777万发；2026-04炸药许可33万吨 | 炸药83.74%、雷管78.5%、导爆索65.13%、导爆管8.24%；新增许可未知 | 2025民爆33.16亿元/38.82% | 整体毛利37.46%；产品47.22%；服务19.67% | L1 | 94 | S7 | 2026backlog/分部利润/新增许可利用率 | false | 安全事故、回款恶化、新产能闲置 | 民爆按稳定分部；许可不直接转销量 |
| 002497 | 雅化集团 | 官方已命名客户；H2量未披露 | lithium_shipment_unit_profit_and_self_supply | 锂盐出货 | 无新增认证 | 券商估全年约12万吨；非公司指引 | Q2行业均价16--17万元/吨 | 近13万吨 | 全年出货接近产能为券商假设 | 2026E总营收170.5亿元 | Q2吨利2.6--3.4万元，含库存/套保 | L3 | 72 | S8 | 规范化吨利、H2客户量、自供权益 | false | Q3规范化吨利<约2万元、出货<约3万吨或OCF负 | 模型剔除库存收益和套保影响 |
| 300390 | 天华新能 | 未命名电池/储能客户 | official_volume_price_recovery | 氢氧化锂/碳酸锂 | not disclosed | not disclosed | 官方称量价齐升；实际ASP缺失 | H1预告未披露 | not disclosed | 锂材料主驱动；份额未捕获 | H1归母22--24亿元、扣非21.62--23.62亿元 | L1-derived | 80 | S1 | 客户/订单、ASP、利用率、自供成本、现金 | false | 量价反转、毛利<约30%或OCF负 | 仅按商品模型，不推断客户订单 |
| 300390 | 天华新能 | 宁德时代 | equity_linkage_not_order | 锂盐及资源子公司 | not disclosed | 采购量/订单未披露 | not disclosed | 券商称现有16.5万吨 | 2025产量/名义仅粗略代理 | CATL关联收入未披露 | 股权协同无量化毛利影响 | L3 | 70 | S9 | 采购、订单、价格、收入占比 | false | 无采购转化或项目延迟 | 股权关系不是订单，不给客户溢价 |
| 300390 | 天华新能 | 商品锂市场 | capacity_volume_margin_forecast | 13.5万吨氢氧化锂+3万吨碳酸锂 | not disclosed | not disclosed | 华源假设2026均价18万元/吨 | 16.5万吨现有+6万吨在建 | 华源假设2026销量13万吨；良率缺失 | 2026E锂材料207.1亿元 | 2026E锂材料毛利36%、归母47.33亿元 | L3 | 72 | S9 | 公司确认的量/价/利用率/良率/自供成本 | false | 销量<13万吨、毛利<30%、项目延迟或OCF负 | 全部保留券商假设措辞，只作敏感性 |

## Valuation consequences

- 301308: `blocks_valuation: true` — H1结果可引用，但缺少可持续单位经济与现金转换。
- 002812: `blocks_valuation: true` — 核心量/利/利用率为单一券商估计，客户涨价未量化。
- 600150: 可用交付模型；订单金额和合并口径要求区间折价。
- 002240: 可用商品模型；无客户溢价，远期矿山不进2026。
- 002497: 可用分部模型；锂盐剔除库存/套保，民爆使用稳定分部倍数。
- 300390: 可用商品模型；CATL股权关系不计采购溢价，未投产项目不进2026。

