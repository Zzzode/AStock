# 智能汽车电子全链节点池（2026-07-23）

节点表保留上市、海外、私营、需求锚点、低纯度与不可得节点；`evidence_status` 仅描述其与德赛西威的关系，不描述该公司自身行业地位。S1=德赛西威 2025 年报；S2=Qualcomm G10PH 官方新闻稿；S3=NVIDIA 小鹏 P7 官方材料。

| node_id | chain_block | subsegment | node_name | node_type | listed_ticker | market | company_status | chain_role | product_or_service | demand_anchor_or_customer | evidence_status | source_count | strongest_source | evidence_gap | classification | valuation_status | next_verification_path | upgrade_trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|---|
| U01 | 上游芯片 | 智驾 SoC | NVIDIA | overseas | NVDA.US | US | listed overseas | GPU/DRIVE 平台 | DRIVE Xavier/Orin/Thor | 小鹏 P7 历史项目 | official-disclosed | 2 | S1,S3 | 当前采购/车型/收入未披露 | satellite_watch | not valued | 双方项目公告 | 车型+SOP+收入确认 |
| U02 | 上游芯片 | 座舱 SoC | Qualcomm | overseas | QCOM.US | US | listed overseas | 座舱 SoC | Snapdragon Cockpit Elite | G10PH 面向 OEM | official-disclosed | 2 | S1,S2 | G10PH OEM/SOP/收入未披露 | satellite_watch | not valued | 双方/OEM公告 | OEM定点+SOP/收入 |
| U03 | 上游芯片 | MCU/座舱 SoC | Renesas | overseas | 6723.T | Japan | listed overseas | 车规芯片候选 | MCU/SoC | not disclosed | not found | 0 | not found | 与公司采购关系未披露 | unavailable | not valued | 供应商或公司公告 | 采购/项目证据 |
| U04 | 上游芯片 | MCU/雷达 | NXP | overseas | NXPI.US | US | listed overseas | 车规芯片候选 | MCU/雷达/连接 | not disclosed | not found | 0 | not found | 与公司采购关系未披露 | unavailable | not valued | 供应商或公司公告 | 采购/项目证据 |
| U05 | 上游芯片 | ADAS SoC | Mobileye | overseas | MBLY.US | US | listed overseas | ADAS 平台候选 | EyeQ | not disclosed | not found | 0 | not found | 与公司采购关系未披露 | unavailable | not valued | 双方项目公告 | 项目级证据 |
| U06 | 上游芯片 | 国产智驾 SoC | 地平线 | listed | 9660.HK | HK | listed | 国产化平台候选 | Journey 系列 | not disclosed | not found | 1 | S1 仅称国产芯片平台量产 | 未披露芯片厂商/车型 | satellite_watch | not valued | 双方/OEM公告 | 芯片+车型+SOP |
| U07 | 上游芯片 | 国产座舱 SoC | 芯驰科技 | private | — | China | private | 国产化平台候选 | 座舱/车控 SoC | not disclosed | not found | 1 | S1 仅称国产芯片平台量产 | 未披露采购及项目 | unavailable | not valued | 双方公告 | 平台/项目证据 |
| U08 | 上游芯片 | 国产智驾 SoC | 黑芝麻智能 | listed | 2533.HK | HK | listed | 国产化平台候选 | 华山系列 | not found | 1 | S1 仅称国产芯片平台量产 | 未披露采购及项目 | satellite_watch | not valued | 双方公告 | 平台/项目证据 |
| U09 | 上游存储 | DRAM/NAND | Samsung Electronics | overseas | 005930.KS | Korea | listed overseas | 存储候选 | DRAM/NAND | not disclosed | not found | 0 | not found | 供应商/价格/用量未披露 | unavailable | not valued | 采购公告 | BOM/供应证据 |
| U10 | 上游存储 | DRAM/NAND | Micron | overseas | MU.US | US | listed overseas | 存储候选 | DRAM/NAND | not disclosed | not found | 0 | not found | 供应商/价格/用量未披露 | unavailable | not valued | 采购公告 | BOM/供应证据 |
| U11 | 上游存储 | DRAM/NAND | SK hynix | overseas | 000660.KS | Korea | listed overseas | 存储候选 | DRAM/NAND | not disclosed | not found | 0 | not found | 供应商/价格/用量未披露 | unavailable | not valued | 采购公告 | BOM/供应证据 |
| U12 | 上游显示 | 面板 | 京东方 A | listed | 000725.SZ | A-share | listed | 面板候选 | LCD/OLED/车载显示 | not disclosed | not found | 0 | not found | 与显示系统的供货关系未披露 | low_purity | not valued | 供应商/项目公告 | 面板+项目证据 |
| U13 | 上游显示 | 面板 | 天马微电子 | listed | 000050.SZ | A-share | listed | 面板候选 | 车载显示 | not disclosed | not found | 0 | not found | 与显示系统的供货关系未披露 | low_purity | not valued | 供应商/项目公告 | 面板+项目证据 |
| U14 | 上游感知 | CIS | 韦尔股份/OmniVision | listed | 603501.SH | A-share | listed | 图像传感器候选 | CIS | not disclosed | not found | 0 | not found | 与摄像头产品的供货关系未披露 | low_purity | not valued | 供应商/项目公告 | CIS+项目证据 |
| U15 | 上游感知 | 激光雷达 | 速腾聚创 | listed | 2498.HK | HK | listed | 感知候选 | LiDAR | not disclosed | not found | 0 | not found | 公司披露摄像头/雷达，不披露 LiDAR 关系 | low_purity | not valued | 双方项目公告 | 项目级证据 |
| U16 | 上游感知 | 激光雷达 | 禾赛科技 | overseas | HSAI.US | US | listed overseas | 感知候选 | LiDAR | not disclosed | not found | 0 | not found | 公司披露摄像头/雷达，不披露 LiDAR 关系 | low_purity | not valued | 双方项目公告 | 项目级证据 |
| U17 | 上游连接 | 连接器/线束 | 立讯精密 | listed | 002475.SZ | A-share | listed | 连接候选 | 连接器/线束 | not disclosed | not found | 0 | not found | 采购关系未披露 | low_purity | not valued | 采购/项目公告 | BOM证据 |
| U18 | 上游软件 | 车载 OS | BlackBerry QNX | overseas | BB.US | US | listed overseas | OS 候选 | QNX | not disclosed | not found | 0 | not found | 第三方 OS/工具链未披露 | unavailable | not valued | 双方项目公告 | 软件栈证据 |
| U19 | 上游软件 | 中间件/工具 | Elektrobit | private | — | Germany | private | 软件候选 | AUTOSAR/中间件 | not disclosed | not found | 0 | not found | 第三方软件栈未披露 | unavailable | not valued | 双方项目公告 | 软件栈证据 |
| M01 | 中游系统 | 座舱/智驾/网联 | 德赛西威 | listed | 002920.SZ | A-share | listed | Tier-1 系统集成 | 座舱、智驾、网联 | 80+ OEM | official-disclosed | 3 | S1,S2,S3 | 客户/车型/ASP/利用率未披露 | core_valuation | eligible aggregate segment only | 财报/客户SOP | 分部收入、毛利和现金流持续验证 |
| M02 | 中游系统 | 座舱/HUD | 华阳集团 | listed | 002906.SZ | A-share | listed | 竞争参照 | 座舱/HUD/域控 | not disclosed | not found | 0 | not found | 本案例未建客户/经济学包 | satellite_watch | not valued | 单独研究 | T1客户/财务证据 |
| M03 | 中游系统 | 全球汽车电子 | 均胜电子 | listed | 600699.SH | A-share | listed | 竞争参照 | 汽车电子/安全 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | 单独研究 | 平台级竞争证据 |
| M04 | 中游系统 | 车身/域控 | 科博达 | listed | 603786.SH | A-share | listed | 竞争参照 | 车载电控 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | 单独研究 | 平台级竞争证据 |
| M05 | 中游系统 | 域控/软件 | 经纬恒润 | listed | 688326.SH | A-share | listed | 竞争参照 | 域控/软件服务 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | 单独研究 | 平台级竞争证据 |
| M06 | 中游系统 | 全球 Tier-1 | Bosch | private | — | Germany | private | 竞争参照 | 座舱/ADAS/EEA | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | OEM项目公告 | 项目级证据 |
| M07 | 中游系统 | 全球 Tier-1 | Continental | overseas | CON.DE | Germany | listed overseas | 竞争参照 | 座舱/ADAS/软件 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | OEM项目公告 | 项目级证据 |
| M08 | 中游系统 | 全球 Tier-1 | Aptiv | overseas | APTV.US | US | listed overseas | 竞争参照 | EEA/软件/连接 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | OEM项目公告 | 项目级证据 |
| M09 | 中游系统 | 座舱 | Visteon | overseas | VC.US | US | listed overseas | 竞争参照 | 座舱/显示 | not disclosed | not found | 0 | not found | 项目重叠未验证 | satellite_watch | not valued | OEM项目公告 | 项目级证据 |
| D01 | 下游 OEM | 自主品牌 | 理想汽车 | demand_anchor | LI.US/2015.HK | US/HK | listed OEM | 客户/需求锚 | 车型平台 | 座舱配套、智驾量产、网联合作 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D02 | 下游 OEM | 自主品牌 | 小米汽车 | demand_anchor | 1810.HK | HK | listed OEM | 客户/需求锚 | 车型平台 | 座舱配套、智驾量产 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D03 | 下游 OEM | 自主品牌 | 吉利汽车 | demand_anchor | 0175.HK | HK | listed OEM | 客户/需求锚 | 车型平台 | 座舱/显示配套、订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D04 | 下游 OEM | 自主品牌 | 奇瑞汽车 | demand_anchor | — | China | private OEM | 客户/需求锚 | 车型平台 | 座舱/显示/智驾/传感器订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D05 | 下游 OEM | 自主品牌 | 长城汽车 | demand_anchor | 601633.SH/2333.HK | A/HK | listed OEM | 客户/需求锚 | 车型平台 | 座舱订单、智驾量产 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D06 | 下游 OEM | 合资品牌 | 广汽丰田 | demand_anchor | — | China | JV OEM | 客户/需求锚 | 车型平台 | 座舱订单、智驾量产、传感器订单、网联合作 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D07 | 下游 OEM | 合资品牌 | 广汽本田 | demand_anchor | — | China | JV OEM | 客户/需求锚 | 车型平台 | 座舱订单、智驾量产、HUD订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D08 | 下游 OEM | 合资品牌 | 东风日产 | demand_anchor | — | China | JV OEM | 客户/需求锚 | 车型平台 | 座舱突破、智驾量产、HUD订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D09 | 下游 OEM | 海外品牌 | Volkswagen | demand_anchor | VOW3.DE | Germany | listed OEM | 客户/需求锚 | 车型平台 | 新项目订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D10 | 下游 OEM | 海外品牌 | Toyota | demand_anchor | 7203.T | Japan | listed OEM | 客户/需求锚 | 车型平台 | 新项目订单/客户池 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D11 | 下游 OEM | 海外品牌 | Mercedes-Benz | demand_anchor | MBG.DE | Germany | listed OEM | 客户/需求锚 | 车型平台 | 新项目订单/网联合作 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D12 | 下游 OEM | 海外品牌 | Honda | demand_anchor | 7267.T | Japan | listed OEM | 客户/需求锚 | 车型平台 | 白点客户突破/座舱订单 | official-disclosed | 1 | S1 | 车型/收入/ASP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| D13 | 下游 OEM | 合资/海外品牌 | 东风汽车/上汽通用 | demand_anchor | 600006.SH/GM.US | A/US | OEM | 客户/需求锚 | HUD/车型平台 | HUD订单 | official-disclosed | 1 | S1 | 车型/收入/ASP/SOP未披露 | demand_anchor | not valued | OEM/公司项目公告 | 车型+SOP+收入 |
| X01 | 上游通用部件 | 未能映射的候选部件 | 面板/连接器主题映射 | low_purity | — | not applicable | unavailable mapping | 低纯度主题节点 | 未证实的候选部件 | not disclosed | not found | 0 | not found | 主题相关但没有德赛西威供货、项目或收入证据 | out_of_scope | not valued | 供应商或项目公告 | 双方确认的供货+项目证据 |
| X02 | 上游供应链 | 匿名主要供应商 | 德赛西威前五供应商（匿名） | unavailable | — | China/overseas unknown | anonymous supplier group | 匿名 BOM 供给 | 原材料/电子元器件 | not disclosed | official-disclosed anonymous aggregate | 1 | S1 | 年报仅披露前五供应商合计采购占比41.13%，未披露名称/品类/价格 | unavailable | not valued | 公司采购或供应商公告 | 供应商名称+采购品类/金额证据 |

核心池仅为德赛西威；卫星公司和所有需求锚点都不进入本案估值模型。
