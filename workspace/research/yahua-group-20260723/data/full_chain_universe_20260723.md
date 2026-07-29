# 全链宇宙：锂盐与民爆

**数据截止日：2026-07-23。** 每行的实体类型、估值资格和缺口均与 JSON 同步。分类含义：core_valuation 仅指可纳入雅化经审计历史经营模型；satellite_watch 指链条相关但尚缺估值经济性；demand_anchor 仅证明下游场景；unavailable 指不可缺省的重要节点。

| node_id | chain_block | subsegment | node_name | node_type | listed_ticker | chain_role | evidence_status | classification | valuation_status |
|---|---|---|---|---|---|---|---|---|---|
| U01 | lithium_resource | 李家沟 | 能投锂业/李家沟锂矿 | private | not applicable | 37.25%权益与优先供料 | confirmed_with_boundary | satellite_watch | supply diversification only |
| U02 | lithium_resource | KMC | Kamativi Mining Company | private | not applicable | 自有矿供给来源 | confirmed_with_boundary | satellite_watch | supply diversification only |
| U03 | lithium_resource | external_contract | Pilbara Minerals | overseas | PLS.AX | 外购/包销渠道 | confirmed_with_boundary | satellite_watch | no contract economics credit |
| U04 | lithium_resource | external_contract | Atlas Lithium | overseas | ATLX.US | 外购/包销渠道 | confirmed_with_boundary | satellite_watch | no contract economics credit |
| U05 | lithium_resource | external_contract | Electramin DMCC | private | not applicable | 外购/包销渠道 | confirmed_with_boundary | satellite_watch | no contract economics credit |
| U06 | lithium_resource | external_contract | MGLIT | unavailable | not applicable | 公司点名渠道 | entity_type_not_verified | unavailable | no credit |
| U07 | conversion_input | chemical_inputs | 液碱、纯碱、硫酸 | unavailable | not applicable | 锂盐转化辅料 | type_confirmed_supplier_unknown | unavailable | no cost credit |
| U08 | lithium_conversion | mining_and_conversion | 雅化锂业务 | listed | 002497.SZ | 采选与锂盐转化 | confirmed | core_valuation | audited history eligible |
| U09 | lithium_product | battery_grade_salts | 雅化锂产品销售 | listed | 002497.SZ | 收入与毛利池 | confirmed | core_valuation | audited history eligible |
| U10 | customer_chain | named_partners | Tesla、LGES、SK ON、LGC、宁德时代等 | demand_anchor | not applicable | 下游合作/合同对手 | confirmed_with_boundary | demand_anchor | no named-customer credit |
| U11 | demand | NEV_and_ESS | 新能源车、储能 | demand_anchor | not applicable | 终端需求 | confirmed_context | demand_anchor | no order credit |
| U12 | competition | lithium_peers | 天齐、赣锋、盛新 | listed | 002466/002460/002240 | 行业β交叉验证 | confirmed_context | satellite_watch | no multiple transfer |
| U13 | technology_option | lithium_sulphide | 雅化硫化锂 | listed | 002497.SZ | 长期技术选择权 | confirmed_precommercial | satellite_watch | excluded |
| U14 | civil_inputs | nitrates_and_emulsion | 硝酸铵、硝酸钠、乳化剂、油相 | unavailable | not applicable | 民爆原料 | type_confirmed_supplier_unknown | unavailable | no cost credit |
| U15 | civil_regulation | licence_and_safety | 民爆许可、安全与数智化要求 | unavailable | not applicable | 准入和合规约束 | confirmed | unavailable | no revenue credit |
| U16 | civil_manufacture | explosives_and_detonators | 雅化民爆产品 | listed | 002497.SZ | 许可制造利润池 | confirmed | core_valuation | audited history eligible |
| U17 | civil_service | blasting_and_mining | 雅化爆破矿服 | listed | 002497.SZ | 服务利润池 | confirmed_with_boundary | core_valuation | audited history eligible |
| U18 | civil_logistics | hazardous_transport | 雅化危化运输 | listed | 002497.SZ | 配送/运输 | confirmed_with_boundary | satellite_watch | revenue structure only |
| U19 | civil_demand | end_markets | 矿山、能源、水利、交通、基建 | demand_anchor | not applicable | 民爆需求场景 | confirmed_context | demand_anchor | no project credit |
| U20 | civil_customer | strategic_partners | 中铁建、中电建、中建材、神华等 | demand_anchor | not applicable | 战略合作/历史服务对手 | confirmed_with_boundary | demand_anchor | no future order credit |
| U21 | competition | civil_peers | 民爆统一可比公司集 | unavailable | not applicable | 相对估值和竞争验证 | not_collected | unavailable | no relative-multiple credit |

详情、来源、缺口、升级条件见同名 JSON 与 analysis/coverage_gap_matrix.md。
