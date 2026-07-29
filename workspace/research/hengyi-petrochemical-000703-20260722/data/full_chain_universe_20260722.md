# 全链条节点池（2026-07-22）

| node_id | chain_block | subsegment | node_name | node_type | listed_ticker | market | company_status | chain_role | product_or_service | demand_anchor_or_customer | evidence_status | source_count | strongest_source | evidence_gap | classification | valuation_status | next_verification_path | upgrade_trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|---|
| N01 | 原油/凝析油 | 基准与供给 | Brent / North Sea Dated | overseas | — | 全球 | 基准 | 成本锚 | 原油 | 全球炼厂 | confirmed | 2 | EIA-STEO-202607 | 恒逸实际贴水未披露 | upstream benchmark | proxy only | 公司采购披露 | 实际贴水/数量可核验 |
| N02 | 原油/凝析油 | 区域供应 | 文莱及马来西亚原油供应方 | private | — | 文莱/马来西亚 | 未具名 | 上游供应 | 原油/凝析油 | 恒逸文莱 | official-disclosed | 1 | HY-AR-2025 | 供应商、数量、合同未披露 | upstream supplier | no valuation credit | IR/供应合同 | 具名供应商和合同条款 |
| N03 | 物流 | 油轮运输 | VLCC/Clean tanker 航运商 | private | — | 亚太 | 分散 | 物流 | 原油/成品油运输 | 文莱炼厂 | not found | 1 | SSE-CTFI-20260717 | 公司实际运费未披露 | service node | proxy only | 运输合同/IR | 实际美元/吨与航线 |
| N04 | 文莱炼化 | 一期 | 恒逸实业（文莱）有限公司 | listed | 000703.SZ | 文莱 | 70%控股 | 核心生产 | 油品、PX、苯 | 东南亚/澳大利亚 | confirmed | 5 | HY-AR-2025 | 2026分部利润/客户未披露 | core direct | eligible conditional | 半年报子公司附注 | 分部利润与少数股东桥 |
| N05 | 炼油产品 | 区域市场 | 东南亚/澳大利亚成品油需求 | demand_anchor | — | 亚太 | 市场 | 需求锚 | 汽柴油/航煤 | 文莱炼厂 | official-disclosed | 2 | HY-AR-2025 | 区域销量与客户未披露 | demand anchor | no direct valuation credit | 海关/客户侧数据 | 区域销量与价差 |
| N06 | 芳烃 | PX/苯 | 恒逸文莱 PX/BZ | listed | 000703.SZ | 文莱 | 70%控股 | 上游原料与外销 | PX、苯 | PTA/化工客户 | confirmed | 3 | HY-AR-2025 | PX/BZ收入、价差未拆分 | core direct | eligible conditional | 半年报/产品ASP | 分品种利润披露 |
| N07 | PTA/PIA | 国内参控股 | 恒逸 PTA/PIA 平台 | listed | 000703.SZ | 中国 | 控股+参股 | 中游转化 | PTA、PIA | 聚酯工厂 | confirmed | 4 | HY-AR-2025 | 各基地权益/开工/内部消化不同口径 | core direct | eligible conditional | 参股公司披露 | 同口径产销和加工费 |
| N08 | MEG | 聚酯原料 | 恒逸外购 MEG | unavailable | — | 中国/进口 | 未披露供应商 | 成本输入 | MEG | 恒逸聚酯 | official-disclosed | 2 | HY-AR-2025 | 长约/现货、库存、对冲未披露 | unavailable supplier | proxy only | 采购附注/IR | 采购结构可核验 |
| N09 | 聚酯 | 长丝/短纤/切片 | 恒逸 PET Fiber 平台 | listed | 000703.SZ | 中国 | 控股 | 下游制造 | POY/FDY/DTY/PSF/切片 | 加弹/织造/服装/家纺 | confirmed | 5 | HY-AR-2025 | 分品种收入/毛利/库存未披露 | core direct | eligible conditional | 半年报细分 | 分品种加工费和开工 |
| N10 | 聚酯 | 瓶片/RPET | 恒逸 PET Bottle Chip 平台 | listed | 000703.SZ | 中国 | 参控股 | 包装材料 | 瓶片、RPET | 饮料/食品/包装 | official-disclosed | 2 | HY-AR-2025 | 收入、认证、订单未拆分 | core direct | watchlist credit | 客户认证/分部披露 | 食品级认证和利润 |
| N11 | CPL/PA6 | 锦纶链 | 广西 CPL/PA6 平台 | listed | 000703.SZ | 中国 | 控股 | 新增制造 | CPL、PA6 | 锦纶纺织/工程塑料 | official-disclosed | 3 | HY-AR-2025 | 爬坡、良率、认证、分产品利润未披露 | core direct | option only | 半年报/验收 | 产销量与单吨利润 |
| N12 | 聚酯替代 | 回收/低等级 | 非食品级 rPET 与回收短纤 | low_purity | — | 中国 | 分散 | 替代品 | 回收切片/短纤 | 低成本纺织/包装 | inferred | 1 | CZCE-PSF | 供给、价差和恒逸敞口未量化 | substitution | no valuation credit | 行业认证与价格 | 质量等级/价差可核验 |
| N13 | 织造/服装 | 加弹与织机 | 私营加弹、织造与贸易商 | private | — | 中国 | 分散 | 直接下游 | DTY/坯布 | 服装/家纺 | confirmed | 3 | CCFA-2025 | 恒逸客户未具名 | downstream customer pool | demand proxy only | 客户侧/IR | 客户份额和订单 |
| N14 | 服装/家纺 | 终端消费 | 中国服装鞋帽/家纺零售 | demand_anchor | — | 中国 | 终端市场 | 需求锚 | 服装/家纺 | 消费者 | confirmed | 2 | CNTAC-2025 | 无公司转化率 | demand anchor | no direct valuation credit | 订单/库存链 | 零售转长丝销量的可核验桥 |
| N15 | 包装 | 饮料/食品 | 食品饮料与包装企业 | demand_anchor | — | 中国/海外 | 分散 | 瓶片需求锚 | PET包装 | 消费者 | not found | 1 | HY-AR-2025 | 具名客户/认证未披露 | demand anchor | no direct valuation credit | 客户侧供应商名录 | 认证、份额、合同 |
| N16 | 工业用途 | 产业用纺织 | 汽车/土工/输送带等应用 | demand_anchor | — | 中国/全球 | 分散 | 需求锚 | 产业用纤维 | 制造/基建 | official-disclosed | 2 | TONGKUN-2025 | 恒逸产品等级/客户未披露 | demand anchor | no direct valuation credit | 认证/客户侧 | 规格和订单 |
| N17 | 同业 | 大炼化 | 荣盛石化 | listed | 002493.SZ | A股 | 上市 | 竞争锚 | 炼化/PX/PTA/聚酯 | 全球/中国 | confirmed | 1 | RONGSHENG-2025 | 当前估值未做 | satellite | watchlist only | 独立估值 | 同口径归母利润桥 |
| N18 | 同业 | 油煤化 | 恒力石化 | listed | 600346.SH | A股 | 上市 | 竞争锚 | 炼化/PX/MEG/PTA/聚酯 | 中国/全球 | confirmed | 1 | HENGLI-2025 | 聚酯统一利润口径不足 | satellite | watchlist only | 分部模型 | 同口径加工费/估值 |
| N19 | 同业 | 炼化新材料 | 东方盛虹 | listed | 000301.SZ | A股 | 上市 | 竞争锚 | 炼化/PX/MEG/聚酯/新材料 | 中国/全球 | confirmed | 1 | SHENGHONG-2025 | 业务可比性弱 | satellite | watchlist only | 分部模型 | 拆分炼化/新材料 |
| N20 | 同业 | 聚酯龙头 | 桐昆股份 | listed | 601233.SH | A股 | 上市 | 竞争锚 | PTA/MEG/聚合/长丝 | 织造服装 | confirmed | 1 | TONGKUN-2025 | 炼化仅权益量 | satellite | watchlist only | 权益利润桥 | 同口径归母敞口 |
| N21 | 同业 | PTA聚酯 | 新凤鸣 | listed | 603225.SH | A股 | 上市 | 竞争锚 | PTA/长丝/短纤 | 织造服装 | confirmed | 1 | XFM-2025 | 无炼化利润池 | satellite | watchlist only | 加工费可比 | 同口径现金流和估值 |
| N22 | 价格数据 | 付费价差 | Platts柴油裂解/PX-石脑油序列 | unavailable | — | 全球 | 付费数据 | 价格锚 | 日度价差 | 估值模型 | not found | 1 | HY-AR-2025引用 | 无可复核原始序列 | unavailable | excluded | 合规数据库 | 原始序列取得 |

