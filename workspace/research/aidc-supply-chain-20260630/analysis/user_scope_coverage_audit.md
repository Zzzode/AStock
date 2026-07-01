# User Scope Coverage Audit

This audit maps the user's explicit AIDC full-chain request to the generated full-chain universe. `covered_with_gap` means the chain node exists, but target-price credit is unavailable until customer/order/ASP/MW/utilization evidence supports a company-level model.

| Category | Requested item | Status | Universe row(s) | Classification | Evidence gap / next verification |
|---|---|---|---|---|---|
| 上游算力芯片与存储 | GPU/ASIC | covered | FC001 GPU/AI ASIC | core_valuation | 客户验证、软件生态、HBM 绑定和出货节奏必须逐项验证。 |
| 上游算力芯片与存储 | CPU | covered_with_gap | FC002 CPU/Host CPU | satellite_watch | 国产 CPU 与 AIDC 直接收入拆分不足。 |
| 上游算力芯片与存储 | HBM/DRAM | covered | FC003 HBM/DRAM | core_valuation | A 股多为接口和配套，不等同于 HBM 颗粒供应商。 |
| 上游算力芯片与存储 | SSD | covered_with_gap | FC005 企业级 SSD | satellite_watch | 只有企业级 SSD 和云厂认证披露明确时才进模型。 |
| 上游算力芯片与存储 | DPU/NIC | covered_with_gap | FC006 DPU/NIC/SuperNIC | satellite_watch | A 股缺高纯度 DPU/NIC 芯片标的。 |
| 上游算力芯片与存储 | 交换芯片 | covered_with_gap | FC007 交换 ASIC | satellite_watch | 国产交换 ASIC 需客户导入和高端端口出货验证。 |
| 服务器零部件 | 电源 | covered_with_gap | FC012 服务器电源 PSU, FC013 Power shelf/板级/模组化电源 | satellite_watch | 需确认 AI 电源批量收入，而非送样或通用电源。; 板级与模组化电源 AIDC 收入披露不足。 |
| 服务器零部件 | 连接器 | covered_with_gap | FC014 高速连接器 | satellite_watch | 客户认证和 112G/224G 收入占比是门槛。 |
| 服务器零部件 | 高速线缆 | covered_with_gap | FC015 高速铜缆 DAC/ACC/AEC | satellite_watch | 送样、认证和量产收入要区分。 |
| 服务器零部件 | 背板 | covered | FC016 背板/主板/Riser | core_valuation | 高层数、低损耗和良率决定毛利。 |
| 服务器零部件 | 机柜 | covered_with_gap | FC017 机柜 | satellite_watch | A 股缺高纯度机柜标的，不能给高估值信用。 |
| 服务器零部件 | 滑轨 | covered_with_gap | FC018 滑轨 | satellite_watch | 滑轨收入通常并入结构件或服务器供应链，AIDC 直接收入披露弱。 |
| 服务器零部件 | 散热材料 | covered_with_gap | FC020 热界面材料 TIM | satellite_watch | 必须拆出服务器/AI 客户收入。 |
| 服务器零部件 | 结构件 | covered_with_gap | FC019 结构件 | satellite_watch | 结构件需要客户平台、单机价值量和量产收入证据。 |
| 服务器零部件 | BMC | covered_with_gap | FC021 BMC/管理芯片 | satellite_watch | 不能把 BMC 稀缺性转移给无直接业务的 A 股标的。 |
| 服务器零部件 | 主板 | covered | FC016 背板/主板/Riser | core_valuation | 高层数、低损耗和良率决定毛利。 |
| 服务器零部件 | 模组化电源 | covered_with_gap | FC013 Power shelf/板级/模组化电源 | satellite_watch | 板级与模组化电源 AIDC 收入披露不足。 |
| 网络与光通信 | 光芯片 | covered_with_gap | FC029 光芯片/EML/VCSEL/CW laser | satellite_watch | 需验证 100G/200G 单通道量产和客户认证。 |
| 网络与光通信 | DSP | covered_with_gap | FC026 DSP/SerDes/TIA | satellite_watch | DSP 不是光模块 A 股公司的自动利润池。 |
| 网络与光通信 | 硅光 | covered_with_gap | FC025 光引擎/硅光 | satellite_watch | 硅光平台核心仍多在海外，A 股更多是配套。 |
| 网络与光通信 | EML/VCSEL | covered_with_gap | FC029 光芯片/EML/VCSEL/CW laser | satellite_watch | 需验证 100G/200G 单通道量产和客户认证。 |
| 网络与光通信 | AWG | covered_with_gap | FC030 AWG | satellite_watch | AWG 价值量和客户导入差异大。 |
| 网络与光通信 | FAU | covered_with_gap | FC031 FAU | satellite_watch | FAU 需要客户平台认证和批量收入证据。 |
| 网络与光通信 | 陶瓷套管 | covered_with_gap | FC032 陶瓷套管 | satellite_watch | AIDC 价值量需与通信用无源器件收入区分。 |
| 网络与光通信 | 光纤光缆 | covered_with_gap | FC033 光纤光缆/MPO | satellite_watch | 收入规模大但 AIDC 弹性和价值密度低于模块。 |
| 网络与光通信 | 交换机 | covered | FC023 AI 交换机/路由器 | core_valuation | 系统设备和交换 ASIC 要分开估值。 |
| 网络与光通信 | 路由器 | covered | FC023 AI 交换机/路由器 | core_valuation | 系统设备和交换 ASIC 要分开估值。 |
| 网络与光通信 | CPO/LPO | covered_with_gap | FC027 LPO/LRO, FC028 CPO/NPO/OIO | satellite_watch | 系统调试和客户采用节奏不确定。; 核心 ASIC 与硅光平台多数非 A 股。 |
| PCB/材料更上游 | 高频高速覆铜板 | covered | FC038 高速 CCL | core_valuation | 客户准入和高端材料收入占比是门槛。 |
| PCB/材料更上游 | 低损耗树脂 | covered_with_gap | FC039 低损耗树脂/填料 | satellite_watch | 材料进入高端 CCL 才能获得 AIDC 信用。 |
| PCB/材料更上游 | 玻纤布 | covered_with_gap | FC040 电子玻纤布 | satellite_watch | 普通玻纤周期不能等同 AI 服务器材料。 |
| PCB/材料更上游 | 铜箔 | covered_with_gap | FC041 铜箔/HVLP 铜箔 | satellite_watch | HVLP 收入和客户认证需单独披露。 |
| PCB/材料更上游 | 钻孔/电镀/压合设备 | covered_with_gap | FC043 PCB 钻孔/曝光设备, FC044 电镀/压合设备 | satellite_watch | 设备弹性来自 PCB 扩产周期。; 高端制程设备国产替代需客户验证。 |
| PCB/材料更上游 | IC 载板 | covered_with_gap | FC042 IC 载板/ABF | satellite_watch | ABF 高端供给仍海外主导。 |
| PCB/材料更上游 | HDI/高多层板 | covered_with_gap | FC037 HDI/高多层板 | satellite_watch | 普通多层板不能直接给 AI 溢价。 |
| 供配电全链条 | 变压器 | covered | FC046 变压器 | core_valuation | 高纯度在数据中心订单，而非通用电网设备。 |
| 供配电全链条 | 高低压柜 | covered_with_gap | FC047 高低压柜/开关柜 | satellite_watch | 通用设备需剥离 AIDC 订单。 |
| 供配电全链条 | UPS | covered | FC048 UPS/HVDC | core_valuation | 认证、项目和机房收入确认是关键。 |
| 供配电全链条 | HVDC | covered | FC048 UPS/HVDC | core_valuation | 认证、项目和机房收入确认是关键。 |
| 供配电全链条 | PDU | covered_with_gap | FC049 PDU/母线槽 | satellite_watch | 母线和 PDU 的数据中心收入占比需验证。 |
| 供配电全链条 | 母线槽 | covered_with_gap | FC049 PDU/母线槽 | satellite_watch | 母线和 PDU 的数据中心收入占比需验证。 |
| 供配电全链条 | BBU | covered_with_gap | FC050 BBU/电池备电 | satellite_watch | 大电池公司 AIDC 收入弹性低。 |
| 供配电全链条 | 柴油发电机 | covered_with_gap | FC051 柴油/燃气发电机 | satellite_watch | 必须有数据中心项目合同才进估值。 |
| 供配电全链条 | 储能 | covered_with_gap | FC052 储能/PCS | satellite_watch | 不能把通用储能景气直接计入 AIDC。 |
| 供配电全链条 | 电力 EPC | covered_with_gap | FC053 电力 EPC/微网 | satellite_watch | 项目毛利和可复制性比政策标题重要。 |
| 供配电全链条 | 绿电直供 | covered_with_gap | FC054 绿电直供/PPA/算电协同 | satellite_watch | 绿电是成本和准入约束，不是所有电力股的估值信用。 |
| 供配电全链条 | 算电协同 | covered_with_gap | FC054 绿电直供/PPA/算电协同 | satellite_watch | 绿电是成本和准入约束，不是所有电力股的估值信用。 |
| 液冷与温控全链条 | 冷板 | covered_with_gap | FC055 冷板 | satellite_watch | 冷板收入和客户认证需披露。 |
| 液冷与温控全链条 | CDU | covered | FC056 CDU | core_valuation | CDU 批量交付优先于概念。 |
| 液冷与温控全链条 | Manifold | covered_with_gap | FC057 Manifold/分液器 | satellite_watch | 常作为系统集成部件，单独收入披露少。 |
| 液冷与温控全链条 | 快接头 | covered_with_gap | FC058 快接头 | satellite_watch | 军工/新能源连接器不能自动等同 AIDC。 |
| 液冷与温控全链条 | 泵阀 | covered_with_gap | FC059 泵阀/控制 | satellite_watch | 通用工业属性强，需要数据中心客户证据。 |
| 液冷与温控全链条 | 管路 | covered_with_gap | FC060 管路/软管 | satellite_watch | 价值量小且认证周期长。 |
| 液冷与温控全链条 | 冷却液 | covered_with_gap | FC061 冷却液 | satellite_watch | A 股多为材料映射，缺直接收入披露。 |
| 液冷与温控全链条 | 干冷器 | covered_with_gap | FC062 干冷器/冷却塔 | satellite_watch | 项目属性强，需中标/验收证据。 |
| 液冷与温控全链条 | 冷水机组 | covered | FC063 冷水机组/精密空调 | core_valuation | 传统 IDC 与 AIDC 液冷要分开。 |
| 液冷与温控全链条 | 精密空调 | covered | FC063 冷水机组/精密空调 | core_valuation | 传统 IDC 与 AIDC 液冷要分开。 |
| 液冷与温控全链条 | 液冷机柜 | covered_with_gap | FC064 液冷机柜 | satellite_watch | 系统集成能力和运维可靠性是溢价来源。 |
| 液冷与温控全链条 | 漏液检测 | covered_with_gap | FC065 漏液检测 | satellite_watch | 漏液检测多作为系统配套，独立收入和客户证据不足。 |
| 数据中心建设与运营 | 土地 | covered | FC066 土地/园区/能耗指标 | core_valuation | 指标稀缺不等于高上架率。 |
| 数据中心建设与运营 | 电力指标 | covered | FC045 电力指标/接入, FC066 土地/园区/能耗指标 | core_valuation | 运营资产必须看已获容量、交付和上架率。; 指标稀缺不等于高上架率。 |
| 数据中心建设与运营 | 机房设计 | covered_with_gap | FC067 机房设计/咨询 | satellite_watch | 设计费弹性远低于设备和运营资产。 |
| 数据中心建设与运营 | EPC | covered_with_gap | FC068 土建/EPC | satellite_watch | 通用工程公司 AIDC 弹性通常被摊薄。 |
| 数据中心建设与运营 | IDC/AIDC 运营商 | covered | FC069 IDC/AIDC 运营 | core_valuation | 上架率、电价、折旧和客户租约是核心。 |
| 数据中心建设与运营 | 上架率 | covered | FC069 IDC/AIDC 运营 | core_valuation | 上架率、电价、折旧和客户租约是核心。 |
| 数据中心建设与运营 | 客户租约 | covered_with_gap | FC074 REITs/不动产资产证券化, FC069 IDC/AIDC 运营 | core_valuation, satellite_watch | 看底层租约、NOI、分派率和扩募能力。; 上架率、电价、折旧和客户租约是核心。 |
| 数据中心建设与运营 | 运维 | covered_with_gap | FC072 运维/监控/DCIM | satellite_watch | 软件化收入和续费率需验证。 |
| 数据中心建设与运营 | 网络接入 | covered_with_gap | FC071 网络接入/专线 | satellite_watch | 网络资源是运营质量，不一定独立提升估值。 |
| 数据中心建设与运营 | REITs/不动产资产 | covered_with_gap | FC074 REITs/不动产资产证券化 | satellite_watch | 看底层租约、NOI、分派率和扩募能力。 |
| 下游需求 | 云厂商 | covered_with_gap | FC076 全球云厂商, FC077 中国云厂商 | demand_anchor | 海外 capex 不能自动证明 A 股公司收入。; 需官方采购、合同或供应链交叉确认。 |
| 下游需求 | 互联网大模型 | covered_with_gap | FC078 互联网大模型/MaaS, FC085 内容/互联网推理 | demand_anchor | 模型热度不是供应商收入证据。; 推理成本下降可能同时带来量增和单价压力。 |
| 下游需求 | AI 应用 | covered_with_gap | FC079 AI 应用/SaaS/Agent | demand_anchor | 应用公司不是 AIDC 设备商，估值逻辑不同。 |
| 下游需求 | 政企智算 | covered_with_gap | FC080 政企智算 | demand_anchor | 招投标、验收和 PFLOPS/MW 是硬锚。 |
| 下游需求 | 科研超算 | covered_with_gap | FC081 科研超算/AI4S | demand_anchor | 科研需求需对应采购或平台用量。 |
| 下游需求 | 金融 | covered_with_gap | FC082 金融 AI | demand_anchor | 金融 IT 预算与 AIDC 设备收入需分开。 |
| 下游需求 | 制造 | covered_with_gap | FC083 制造/工业 AI | demand_anchor | 边缘推理和云训练的硬件需求不同。 |
| 下游需求 | 自动驾驶 | covered_with_gap | FC084 自动驾驶/机器人/具身智能 | demand_anchor | 产业热度不能直接推导 AIDC 上游收入。 |
| 下游需求 | 机器人 | covered_with_gap | FC084 自动驾驶/机器人/具身智能 | demand_anchor | 产业热度不能直接推导 AIDC 上游收入。 |

- Explicit requested items: 78
- Missing items: 0
- Result: PASS
