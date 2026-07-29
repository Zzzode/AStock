# 经营驱动关系表

- Scope: cross-sectional market screen, not a full single-industry-chain universe.
- Data cutoff: 2026-07-22; operating evidence is current through the latest cited filing/report.
- Gate: **CONDITIONAL**. 301308 and 002812 remain valuation-blocked; other names are usable only under stated model boundaries.
- Evidence labels: `official-disclosed` / `broker-stated` / `inferred` / `not found`. Demand anchors never prove company orders.

## Source keys

- S1: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/data/raw_a_share_h1_2026_preview_20260715.json`; Eastmoney/Akshare company-preview table, original announcement URLs not captured.
- S2: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/600150-中国船舶/2026-07-14-华源证券-26H1预告点评-Q2业绩预计同比大增-关注后续船价与集团整合.pdf`.
- S3: `workspace/research/low-position-capital-layout-20260711/sources/launched-official-20260711/301308_H1_guidance_20260703.pdf`; Eastmoney notice archive infocode `AN202607031826702637`, exchange direct URL not captured.
- S4: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/301308-江波龙/2026-05-07-国信证券-1Q26归母净利润同比增长2644.05-端侧应用多维拓展.pdf`.
- S5: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002812-恩捷股份/2026-07-10-东吴证券-26H1业绩预告点评-Q2业绩超我们预期-隔膜供需紧张盈利持续提升.pdf`.
- S6: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002240-盛新锂能/2026-07-09-东吴证券-26H1业绩预告点评-Q2锂盐出货高增-自有矿贡献利润.pdf`.
- S7: `workspace/research/a-share-double-upside-screen-20260722/sources/official-20260722/002497_2025_annual_report.pdf` and `002497_2026_h1_earnings_preview.pdf`; CNINFO originals archived locally, exact download URLs pending source registry.
- S8: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/002497-雅化集团/2026-07-08-东吴证券-26H1业绩预告点评-Q2锂盐量利齐升-略超我们预期.pdf`.
- S9: `workspace/research/low-position-capital-layout-20260711/refresh-20260715/sources/broker-reports-20260715/300390-天华新能/2026-06-06-华源证券-氢氧化锂龙头-深度绑定大客户-锂资源加速布局.pdf`.

## Relationship rows

| ticker | company | chain_layer | node_type | upstream_input | product_or_process | downstream_customer_or_platform | relationship_type | confidence | source_tier | evidence_score | revenue_exposure | capacity_or_certification | order_visibility | ASP_or_price_proxy | utilization_or_yield | margin_or_earnings_impact | source | evidence_gap | valuation_eligibility | downgrade_trigger | used_in_valuation |
|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| 600150 | 中国船舶 | 船舶交付 | listed | 船钢/船机/外协，传导未披露 | 民船建造、高价值船型、节拍化生产 | 船东，名称未披露 | official-disclosed | high | L1-derived | 88 | 造船核心；并表后分部占比未在复用包给出 | 任务饱满；有效产能未披露 | 官方确认订单充足 | 单船均价同比提升 | not disclosed | H1 归母 92--110 亿元，数量/结构/均价共同提升 | S1 | 订单金额、船型毛利、利用率、并表序列 | eligible with normalization | 交付/回款走弱、毛利连续回落、订单覆盖下降 | true |
| 600150 | 中国船舶 | 行业订单/船价锚 | listed | 船厂产能 | 高价订单交付 | 油轮/散货船需求 | broker-stated | medium-high | L3 | 74 | not separately disclosed | 船厂产能紧张 | 交付排至 2028--2030；行业覆盖 4.31 年 | 新造船价指数 182.08→185.39 | not disclosed | 华源 2026E 归母 181.98 亿元/毛利率 16.84% | S2 | 公司订单金额和订单级经济性 | supporting scenario | 行业指标与公司交付利润背离 | true |
| 301308 | 江波龙 | 存储模组/嵌入式存储 | listed | NAND/DRAM 晶圆；上游 LTA/MOU | 嵌入式、SSD、内存条、移动存储、自研主控/封测 | AMD 联合调优；下游订单未披露 | official-disclosed | high for results | L1-derived | 78 | H1 营收 220--250 亿元，分产品未披露 | 自有封测；产能/利用率/良率未披露 | 上游协议确认；下游订单未披露 | not disclosed | not disclosed | H1 归母 92--110 亿元，量价库存结构未拆 | S3 | bit 出货、ASP、库存成本层、下游订单、现金转换 | watchlist only / insufficient economics | 毛利骤降、OCF持续深负、库存继续上升 | false |
| 301308 | 江波龙 | 企业级/端侧认证 | listed | 存储晶圆 | eSSD/RDIMM/UFS/ePOP4x/mSSD | 鲲鹏、海光、飞腾、AMD；未命名头部客户 | broker-stated | medium | L3 | 66 | 券商称 2025 企业级 17.83 亿元 | 四平台兼容认证；产能未披露 | 进入供应链但订单未披露 | 行业 NAND/DRAM 指数，不是公司 ASP | not disclosed | 报告早于 H1 预告，全年预测已失去时点匹配 | S4 | 认证转量、客户、订单、ASP、利用率 | watchlist only | 认证不转可核验收入 | false |
| 002812 | 恩捷股份 | 湿法隔膜 | listed | PE/白油/涂覆料/能源/设备 | 高品质锂电隔膜 | 电池厂；客户和订单未披露 | official-disclosed | high for direction | L1-derived | 76 | 隔膜核心，分部占比未复核 | 公司称积极调配产能；有效产能/认证未披露 | not disclosed | 价格企稳回升；实际 ASP 未披露 | not disclosed | H1 归母 7.36--9.00 亿元，量/成本/价改善 | S1 | 客户、订单、出货、ASP、单平利润、良率 | watchlist only / insufficient customer evidence | 涨价延迟、单位经济反转、新线良率不及预期 | false |
| 002812 | 恩捷股份 | 隔膜恢复经济性 | listed | PE 与设备供给 | 湿法出货和新线爬坡 | 未命名大客户/海外/3C | broker-stated | medium | L3 | 64 | 东吴 2026E 营收 200.58 亿元 | 2027 有效产能 220 亿平；玉溪/SK常州增量 | 涨价部分待落地；订单未披露 | PE 涨价 20%--30% | 2026/2027 利用率 90%/97%；良率未披露 | Q2 出货 41--42 亿平、调整后单平利润 0.15 元 | S5 | 单一来源的量/利/利用率；客户和良率缺失 | discounted sensitivity only | Q3 单平利润低于约0.12元或涨价不落地 | false |
| 002240 | 盛新锂能 | 锂盐/资源一体化 | listed | 自有/权益矿及外购精矿 | 印尼及国内锂盐冶炼 | 电池材料应用；客户未披露 | official-disclosed | high for direction | L1-derived | 80 | 锂盐为核心驱动 | 印尼产能大幅释放；名义产能/利用率未披露 | not disclosed | 售价同比大涨；实现价未披露 | not disclosed | H1 归母 10--12 亿元、扣非 13--15 亿元 | S1 | ASP、客户/订单、印尼利用率、自供比、OCF | conditional eligible | 锂价/出货/爬坡不及预期或 OCF持续负 | true |
| 002240 | 盛新锂能 | 锂盐量/吨利敏感性 | listed | 萨比星、奥依诺及外购矿 | 锂盐出货 | not disclosed | broker-stated | medium | L3 | 65 | 东吴 2026E 营收 150.49 亿元 | 印尼贡献增量；木绒2028投产不进2026 | not disclosed | Q2 锂价中枢环比 +2 万元/吨 | 萨比星/奥依诺接近满产；印尼未披露 | Q2 出货3万吨+、综合吨利约2万元 | S6 | 公司确认的吨位、吨利、利用率、客户 | supporting commodity scenario | Q3 出货<约3万吨、吨利<约2万元或 OCF负 | true |
| 002497 | 雅化集团 | 锂盐与客户合同 | listed | 卡玛蒂维/李家沟及多家长协矿 | 电池级氢氧化锂/碳酸锂 | Tesla、LGES、SK ON、LGC、松下、宁德时代等 | official-disclosed | high | L1 | 94 | 2025 锂收入48.24亿元/56.46%；头部客户占锂收入90%+ | 当前综合产能近13万吨；CNAS/ESG认证 | 多份重大销售合同正常履行 | H1 销量与均价同步增长；实际 ASP未披露 | 2025产6.86/销6.95万吨；同口径利用率未披露 | 2025锂毛利率12.22%；H1归母11--13亿元 | S7 | 2026 ASP、H2客户量、库存/套保、自供比 | conditional eligible; exclude one-offs | 合同/出货不及预期、规范化吨利<约2万元、OCF负 | true |
| 002497 | 雅化集团 | 民爆/矿服 | listed | 许可产能与区域网络 | 炸药、雷管、导爆器材、爆破与矿服 | 中铁建、中电建、中建材、神华；西部重点项目 | official-disclosed | high | L1 | 92 | 2025民爆收入33.16亿元/38.82% | 炸药26.25万吨/83.74%；雷管8777万发/78.5%；2026-04炸药许可33万吨 | 战略合作/项目暴露；backlog金额未披露 | not disclosed | 官方披露2025产品利用率；新增许可利用率未披露 | 2025整体毛利37.46%，产品47.22%，服务19.67% | S7 | 2026项目backlog、分部利润、新许可利用率 | stability credit only | 安全事故、项目回款恶化、新许可闲置 | true |
| 002497 | 雅化集团 | 锂盐吨利敏感性 | listed | 自有+长协锂精矿 | 出货、库存/套保归一化 | 客户官方已命名；2026客户量未披露 | broker-stated | medium-high | L3 | 72 | 东吴2026E营收170.5亿元/归母30.32亿元 | 近13万吨产能 | 券商估全年出货约12万吨 | Q2行业均价16--17万元/吨 | 全年出货接近名义产能为券商假设 | Q2吨利2.6--3.4万元，含低价库存/套保 | S8 | 剔除库存/套保后的吨利和H2客户量 | supporting conditional scenario | Q3规范化吨利<约2万元、出货<约3万吨或OCF负 | true |
| 300390 | 天华新能 | 氢氧化锂/资源一体化 | listed | 外购精矿+Ogapa及在建/勘探矿 | 氢氧化锂/碳酸锂 | 电池/储能需求；官方未披露客户采购 | official-disclosed | high for direction | L1-derived | 80 | 锂材料为主要利润驱动 | H1预告未披露产能 | not disclosed | H1量价齐升；实际 ASP未披露 | not disclosed | H1归母22--24亿元、扣非21.62--23.62亿元 | S1 | ASP、订单、客户占比、利用率、自供成本、OCF | conditional eligible | 锂价/销量反转、毛利<约30%或 OCF负 | true |
| 300390 | 天华新能 | 产能/客户关联/资源期权 | listed | Ogapa、金子峰、Tantale、容须卡南等 | 13.5万吨氢氧化锂+3万吨碳酸锂 | 宁德时代持股13.54%并持核心子公司25%；不是采购证明 | broker-stated | medium-high | L3 | 73 | 券商称2025锂材料66.3亿元，2026E 207.1亿元 | 16.5万吨现有产能；6万吨二期在建 | CATL股权不是订单；采购未披露 | 华源假设2026锂均价18万元/吨 | 2025产量约10万吨仅为粗略代理；2026E销量13万吨 | 华源2026E锂材料毛利率36%、归母47.33亿元 | S9 | CATL采购、实现价、同口径利用率、自供成本 | commodity scenario; no customer premium | 销量<约13万吨、项目延迟、毛利<30%或 OCF负 | true |

## Valuation blockers

- **301308:** `blocks_valuation: true` for any sustainable company-level target. H1 earnings are usable as a reported fact, not as an annualized denominator.
- **002812:** `blocks_valuation: true` for an unhaircut core model. The shipment/unit-profit/utilization stack is single-broker evidence and customer price execution is undisclosed.
- **600150, 002240, 002497, 300390:** usable only within the stated model boundaries; customer or long-duration optionality not explicitly supported is assigned zero valuation credit.

