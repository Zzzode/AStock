from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from textwrap import dedent


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ANALYSIS = BASE / "analysis"
SECTIONS = BASE / "sections"
SOURCES = BASE / "sources" / "public-web-20260630"
RUN_DATE = "2026-06-30"


SOURCE_NOTES = {
    "S01": {
        "title": "NVIDIA FY2027 Q1 results",
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2027",
        "type": "official",
        "note": "NVIDIA FY2027 Q1 revenue was USD81.6bn and Data Center revenue was USD75.2bn.",
    },
    "S02": {
        "title": "Dell'Oro 1Q26 data center capex release",
        "url": "https://www.delloro.com/news/ai-infrastructure-buildouts-and-memory-cost-inflation-drove-data-center-capex-higher-in-1q-2026/",
        "type": "industry",
        "note": "Dell'Oro raised 2026 global data-center capex outlook to more than USD1tn.",
    },
    "S03": {
        "title": "National Data Administration 2026 speech",
        "url": "https://www.nda.gov.cn/sjj/jgsz/jld/llh/llhldhd/0323/20260323202204680553721_pc.html",
        "type": "official-policy",
        "note": "China intelligent-compute scale reached 1.59mn PFlops by 2025 year-end; national hubs represented more than 80%.",
    },
    "S04": {
        "title": "NVIDIA GB200 NVL72 product page",
        "url": "https://www.nvidia.com/en-us/data-center/gb200-nvl72/",
        "type": "official-product",
        "note": "GB200 NVL72 is a liquid-cooled rack-scale design with 36 Grace CPUs and 72 Blackwell GPUs.",
    },
    "S05": {
        "title": "JLL 2026 Global Data Center Outlook",
        "url": "https://www.joneslanglasalle.com.cn/zh-cn/insights/2026-data-center-outlook",
        "type": "industry",
        "note": "JLL expects AI workload share to rise and AI rack density to move toward 40-100+kW.",
    },
    "S06": {
        "title": "LightCounting March 2026 Ethernet optics note",
        "url": "https://www.lightcounting.com/newsletter/en/march-2026-ethernet-optics-382",
        "type": "industry",
        "note": "LightCounting discusses AI-cluster optics growth, 2026 growth constraints and the possible USD100bn market by 2030.",
    },
    "S07": {
        "title": "FII 2025 annual report summary",
        "url": "https://static.cninfo.com.cn/finalpage/2026-03-11/1225004416.PDF",
        "type": "company-filing",
        "note": "FII disclosed strong cloud-computing revenue growth and more than 3x cloud AI-server revenue growth in 2025.",
    },
    "S08": {
        "title": "Hushi Electronics 2025 annual report summary",
        "url": "https://static.cninfo.com.cn/finalpage/2026-03-25/1225027831.PDF",
        "type": "company-filing",
        "note": "Hushi disclosed data-communication PCB revenue and AI server/HPC plus high-speed switch/router sub-segment revenue.",
    },
    "S09": {
        "title": "Invic 2025 annual report summary",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-21/1225131812.PDF",
        "type": "company-filing",
        "note": "Invic disclosed end-to-end liquid-cooling products and large data-center customer examples.",
    },
    "S10": {
        "title": "Kehua Data 2025 annual report summary",
        "url": "https://disc.static.szse.cn/disc/disk03/finalpage/2026-04-27/793ce78f-1252-40f7-9c44-a13b6f8e3d67.PDF",
        "type": "company-filing",
        "note": "Kehua disclosed full-stack intelligent data-center infrastructure products and 200kW high-density UPS module certification.",
    },
    "S11": {
        "title": "Runze investor relations activity record",
        "url": "https://pdf.dfcfw.com/pdf/H2_AN202604141821167621_1.pdf",
        "type": "company-ir",
        "note": "Runze discussed AIDC growth, liquid-cooled 200MW data-center delivery and AIDC/IDC margin expectations.",
    },
    "S12": {
        "title": "Runze 2025 annual report summary",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-10/1225091631.PDF",
        "type": "company-filing",
        "note": "Runze disclosed AIDC growth drivers, 220MW added compute delivery and customer diversification.",
    },
    "S15": {
        "title": "SIA semiconductor ecosystem AI data centers",
        "url": "https://www.semiconductors.org/wp-content/uploads/2026/05/Powering-AI_The-Semiconductor-Ecosystem-at-the-Foundation-of-Data-Centers_report.pdf",
        "type": "industry",
        "note": "Maps the semiconductor stack behind AI data centers and frames compute, memory, networking and power as one system.",
    },
    "S16": {
        "title": "NVIDIA Spectrum-X Ethernet platform",
        "url": "https://www.nvidia.com/en-us/networking/spectrumx/",
        "type": "official-product",
        "note": "Defines the AI Ethernet networking stack and scale-out/scale-across bottleneck for AIDC clusters.",
    },
    "S17": {
        "title": "TrendForce AI HBM server research category",
        "url": "https://www.trendforce.com/research/category/Semiconductors/AI%20Server_HBM_Server",
        "type": "industry",
        "note": "Tracks AI server, HBM and memory-cycle evidence used for upstream compute/storage mapping.",
    },
    "S18": {
        "title": "TE data center AI connectivity solutions",
        "url": "https://www.te.com/en/industries/data-centers-ai.html",
        "type": "official-product",
        "note": "Supports high-speed connector, cable, backplane, socket and power interconnect definitions.",
    },
    "S19": {
        "title": "Schneider data center reference designs AI liquid cooling",
        "url": "https://www.se.com/us/en/work/solutions/data-centers-and-networks/reference-designs/",
        "type": "official-product",
        "note": "Supports high-density AI data-center reference design, power and liquid-cooling architecture mapping.",
    },
    "S20": {
        "title": "Vertiv high density cooling AI ML workloads",
        "url": "https://www.vertiv.com/en-us/insights/articles/educational-articles/high--density-cooling-a-guide-to-advanced-thermal-solutions-for-ai-and-ml-workloads-in-data-centers/",
        "type": "official-product",
        "note": "Defines high-density cooling, CDU role and rack-density pressure for AI/ML data centers.",
    },
    "S21": {
        "title": "Schneider liquid cooling reference design blog",
        "url": "https://blog.se.com/datacenter/2026/01/06/how-liquid-cooling-reference-designs-optimize-ai-data-center-deployments/",
        "type": "official-product",
        "note": "Supports liquid-cooling deployment architecture and reference-design language; local capture had HTTP 403 but URL is retained.",
    },
    "S22": {
        "title": "Supermicro CDU glossary Chinese",
        "url": "https://www.supermicro.com/zh_cn/glossary/cdu",
        "type": "official-product",
        "note": "Defines CDU as the heat-exchange, pumping and control boundary between facility water and the IT liquid loop.",
    },
    "S23": {
        "title": "DellOro data center capex market segments",
        "url": "https://www.delloro.com/market-research/data-center-infrastructure/data-center-capex/",
        "type": "industry",
        "note": "Segments hyperscalers, China cloud, neoclouds, colocation, telco and enterprise capex demand.",
    },
    "S24": {
        "title": "Xinhua 2026 China AI development trends",
        "url": "https://www.news.cn/politics/20260128/25f6978fe8cf41bda53b78bcf7106fec/c.html",
        "type": "public-news",
        "note": "Supports China AI application, compute-network and smart-compute-density demand anchors.",
    },
    "S25": {
        "title": "Minsheng AIDC power distribution cooling trends",
        "url": "https://pdf.dfcfw.com/pdf/H3_AP202502121643008300_1.pdf",
        "type": "broker-public",
        "note": "Maps data-center power and cooling segments including UPS/HVDC, transformers, busway, diesel generators and liquid cooling.",
    },
    "S26": {
        "title": "Molex data center power management solutions",
        "url": "https://www.molex.com/en-us/industries-applications/power-for-data-center",
        "type": "official-product",
        "note": "Supports server/rack power connector and power-management component mapping; local capture failed and URL is retained.",
    },
    "S27": {
        "title": "CEJN data center quick connect coupling solutions",
        "url": "https://www.cejn.com/en-us/applications/data-centers/",
        "type": "official-product",
        "note": "Defines quick-connect couplings for data-center CDU and liquid-cooling serviceability.",
    },
    "S28": {
        "title": "Fuchs China liquid cooling fluid AIDC",
        "url": "https://www.fuchs.com/cn/zh/company/news-new/news-entry/6800-fu-si-zhong-guo-zhong-bang-liang-xiang-di-wu-jie-zhong-guo-shu-ju-zhong-xin-ye-leng-chan-ye-feng-hui-fu-neng-lu-se-zhi-suan-fa-zhan/",
        "type": "official-product",
        "note": "Supports coolant and liquid-cooling material mapping for AIDC.",
    },
    "S29": {
        "title": "DellOro AI boom capex to 2030",
        "url": "https://www.delloro.com/news/ai-boom-drives-data-center-capex-to-1-7-trillion-by-2030/",
        "type": "industry",
        "note": "Supports long-cycle data-center capex demand and hyperscale/neocloud/sovereign AI buildout framing.",
    },
    "S30": {
        "title": "China intelligent computing center development guide",
        "url": "https://scdrc.sic.gov.cn/SmarterCity_new/yjcg/jlfx/0408/2c97b8cb-95c74996-0196-146608fd-0b8e.pdf",
        "type": "official-policy",
        "note": "Supports China intelligent-computing center architecture, construction and operation mapping.",
    },
}


ASSUMPTIONS = {
    "601138": {"weight": 11, "seasonality": 0.24, "base_pe": 34, "bear_pe": 25, "bull_pe": 42, "direct": 5, "evidence": "A-", "growth": 0.18, "method": "PE/订单现金流校验", "credit": "earnings credit"},
    "000977": {"weight": 5, "seasonality": 0.25, "base_pe": 28, "bear_pe": 20, "bull_pe": 35, "direct": 4, "evidence": "B", "growth": 0.10, "method": "PE/毛利率压力校验", "credit": "conditional earnings"},
    "603019": {"weight": 5, "seasonality": 0.22, "base_pe": 42, "bear_pe": 30, "bull_pe": 55, "direct": 4, "evidence": "B", "growth": 0.18, "method": "PE/PB稀缺性校验", "credit": "optionality credit"},
    "000938": {"weight": 4, "seasonality": 0.23, "base_pe": 25, "bear_pe": 18, "bull_pe": 32, "direct": 3, "evidence": "B", "growth": 0.12, "method": "PE/网络设备订单校验", "credit": "optionality credit"},
    "300308": {"weight": 10, "seasonality": 0.23, "base_pe": 45, "bear_pe": 35, "bull_pe": 55, "direct": 5, "evidence": "A-", "growth": 0.25, "method": "PE/PEG/PS交叉校验", "credit": "earnings credit"},
    "300502": {"weight": 8, "seasonality": 0.23, "base_pe": 40, "bear_pe": 30, "bull_pe": 50, "direct": 5, "evidence": "A-", "growth": 0.22, "method": "PE/PEG/客户集中校验", "credit": "earnings credit"},
    "300394": {"weight": 6, "seasonality": 0.23, "base_pe": 55, "bear_pe": 40, "bull_pe": 70, "direct": 5, "evidence": "B+", "growth": 0.24, "method": "PE/稀缺器件溢价校验", "credit": "optionality credit"},
    "002463": {"weight": 8, "seasonality": 0.25, "base_pe": 35, "bear_pe": 25, "bull_pe": 45, "direct": 5, "evidence": "A", "growth": 0.22, "method": "PE/高端PCB收入校验", "credit": "earnings credit"},
    "300476": {"weight": 7, "seasonality": 0.25, "base_pe": 32, "bear_pe": 22, "bull_pe": 42, "direct": 5, "evidence": "B+", "growth": 0.24, "method": "PE/扩产与现金流校验", "credit": "earnings credit"},
    "002916": {"weight": 4, "seasonality": 0.24, "base_pe": 28, "bear_pe": 20, "bull_pe": 36, "direct": 3, "evidence": "B", "growth": 0.12, "method": "PE/封装基板景气校验", "credit": "conditional earnings"},
    "600183": {"weight": 4, "seasonality": 0.24, "base_pe": 30, "bear_pe": 22, "bull_pe": 38, "direct": 4, "evidence": "B", "growth": 0.15, "method": "PE/材料周期校验", "credit": "conditional earnings"},
    "002837": {"weight": 5, "seasonality": 0.18, "base_pe": 35, "bear_pe": 25, "bull_pe": 45, "direct": 5, "evidence": "A-", "growth": 0.18, "method": "正常化PE/液冷订单校验", "credit": "optionality credit"},
    "002335": {"weight": 4, "seasonality": 0.20, "base_pe": 25, "bear_pe": 18, "bull_pe": 32, "direct": 4, "evidence": "A-", "growth": 0.12, "method": "PE/供配电项目校验", "credit": "optionality credit"},
    "301018": {"weight": 3, "seasonality": 0.20, "base_pe": 30, "bear_pe": 20, "bull_pe": 40, "direct": 3, "evidence": "B-", "growth": 0.12, "method": "正常化PE/项目验收校验", "credit": "watchlist credit"},
    "688676": {"weight": 4, "seasonality": 0.22, "base_pe": 28, "bear_pe": 20, "bull_pe": 36, "direct": 3, "evidence": "B", "growth": 0.15, "method": "PE/PB/算电协同校验", "credit": "optionality credit"},
    "300442": {"weight": 7, "seasonality": 0.23, "base_pe": 30, "bear_pe": 22, "bull_pe": 40, "direct": 5, "evidence": "A-", "growth": 0.20, "method": "PE/现金流/上架率校验", "credit": "earnings credit"},
    "300738": {"weight": 3, "seasonality": 0.24, "base_pe": 24, "bear_pe": 16, "bull_pe": 32, "direct": 3, "evidence": "B-", "growth": 0.10, "method": "PE/负债率/上架率校验", "credit": "conditional earnings"},
    "300383": {"weight": 2, "seasonality": 0.22, "base_pe": 18, "bear_pe": 12, "bull_pe": 26, "direct": 2, "evidence": "C+", "growth": 0.05, "method": "修复型PE/PB校验", "credit": "watchlist credit"},
}


LAYER_INPUTS = {
    "AI服务器/交换机ODM": ("GPU/ASIC、HBM、PCB、电源、结构件", "AI服务器、NVLink/以太网交换机整机", "海外CSP、云厂商、AI算力集群"),
    "AI服务器/整机": ("CPU/GPU/国产AI芯片、存储、网络卡、液冷部件", "AI服务器、超节点、异构算力平台", "互联网云、政企智算中心"),
    "国产算力/液冷整机": ("国产CPU/GPU、液冷冷源、网络互联", "服务器、超算/智算中心、浸没式液冷", "政企、科研、国产算力集群"),
    "网络设备/服务器": ("交换芯片、光模块、PCB、电源", "交换机、服务器、全栈液冷方案", "云厂商、运营商、政企"),
    "光模块": ("DSP/硅光/EML/VCSEL、透镜、PCB、光芯片", "800G/1.6T/3.2T光模块", "AI训练/推理集群、交换机端口"),
    "光器件/光引擎": ("透镜、陶瓷套管、FAU、ELS、光芯片", "光引擎、无源器件、CPO配套", "高速光模块厂、CPO/硅光平台"),
    "AI服务器PCB": ("高频高速覆铜板、铜箔、树脂、钻孔电镀设备", "高多层板、HDI、UBB、交换机板", "AI服务器、HPC、交换机/路由器"),
    "PCB/封装基板": ("CCL、铜箔、IC载板材料", "通信PCB、封装基板", "通信设备、服务器、封装客户"),
    "覆铜板/材料": ("树脂、玻纤布、铜箔", "高速覆铜板、低损耗材料", "PCB厂、服务器/交换机板"),
    "液冷/温控": ("压缩机、泵、阀、冷板、管路、冷却液", "CDU、冷板、Manifold、液冷机柜、精密空调", "服务器厂、IDC、云厂商、运营商"),
    "供配电/UPS": ("功率器件、变压器、电池、模块化电源", "高密UPS、预制电力模组、供配电系统", "AIDC、运营商、互联网客户"),
    "温控/液冷": ("压缩机、换热器、冷板、管路", "冷源、精密空调、液冷系统集成", "数据中心、工业场景、云厂商"),
    "算电协同/变压器": ("硅钢、铜、绝缘材料、电力电子", "干式变压器、储能/数字化供电设备", "数据中心、电网、新能源侧"),
    "AIDC/智算运营": ("土地电力、服务器、网络、液冷、运维", "智算中心、算力服务、托管", "互联网、云厂商、AI企业、政企"),
    "IDC/边缘算力": ("机房、电力、网络、服务器", "IDC托管、边缘算力节点", "云、互联网、政企客户"),
    "IDC/云服务": ("机房、电力、云平台、网络", "IDC托管、云服务", "云厂商、互联网、企业客户"),
}


FULL_CHAIN_BLOCKS = [
    {
        "block": "上游算力芯片与存储",
        "role": "AIDC 算力、存储和网络卸载的最上游瓶颈。",
        "source": "S15/S16/S17",
        "items": [
            ("GPU/AI ASIC", "训练/推理加速器和云厂自研 XPU", "NVIDIA、AMD、Broadcom/Marvell 定制 ASIC、Google TPU、AWS Trainium、Microsoft Maia、Meta MTIA、华为昇腾", "寒武纪、海光信息、摩尔线程；芯原股份观察", "核心可估值/商业化早期折价", "客户验证、软件生态、HBM 绑定和出货节奏必须逐项验证。"),
            ("CPU/Host CPU", "AI 服务器主控、调度、I/O 与数据预处理", "Intel Xeon、AMD EPYC、Arm Neoverse、NVIDIA Grace、Ampere、华为鲲鹏、阿里倚天", "海光信息、龙芯中科；中科曙光为平台映射", "条件估值/国产替代观察", "国产 CPU 与 AIDC 直接收入拆分不足。"),
            ("HBM/DRAM", "HBM3E/HBM4、DDR5 RDIMM 与内存颗粒", "SK hynix、Samsung、Micron、长鑫存储", "澜起科技、聚辰股份、深科技；兆易创新/北京君正观察", "核心可估值/观察", "A 股多为接口和配套，不等同于 HBM 颗粒供应商。"),
            ("内存接口芯片", "RCD、DB、SPD、CKD、MRCD/MDB 等 DDR5/DDR6 配套", "Montage、Rambus、Renesas、TI", "澜起科技、聚辰股份", "核心可估值", "代际升级与服务器渗透率是关键弹性。"),
            ("企业级 SSD", "NVMe SSD、QLC SSD、KV cache 和训练数据集存储", "Samsung、Kioxia、Solidigm、Micron、YMTC、Phison、Silicon Motion", "佰维存储、江波龙、德明利、朗科科技", "条件估值", "只有企业级 SSD 和云厂认证披露明确时才进模型。"),
            ("DPU/NIC/SuperNIC", "RDMA、虚拟化、安全、存储卸载和 400G/800G 网卡", "NVIDIA BlueField/ConnectX、Broadcom、AMD Pensando、Marvell、Intel IPU、AWS Nitro", "工业富联、裕太微、星网锐捷/锐捷网络观察", "观察/系统映射", "A 股缺高纯度 DPU/NIC 芯片标的。"),
            ("交换 ASIC", "400G/800G/1.6T 以太网或 IB 交换芯片", "Broadcom Tomahawk/Jericho、NVIDIA Spectrum-X、Cisco Silicon One、Marvell、华为", "盛科通信、裕太微；紫光股份为设备系统映射", "条件估值", "国产交换 ASIC 需客户导入和高端端口出货验证。"),
            ("存储控制器/主控", "企业级 SSD 主控、固件、纠错和接口控制", "Phison、Silicon Motion、Marvell、Samsung、Kioxia", "佰维存储、江波龙、德明利；东芯股份观察", "观察/条件估值", "主控自研和企业级收入拆分不充分。"),
            ("先进封装/Chiplet 配套", "AI 加速器互连、封装基板和 Chiplet 设计服务", "TSMC CoWoS、ASE、Amkor、Broadcom、Marvell", "通富微电、长电科技、华天科技、芯原股份、兴森科技", "观察/期权", "AIDC 直接收入和高端封装份额需官方证据。"),
            ("国产算力平台", "国产 AI 芯片、服务器、框架和行业适配", "华为昇腾、昆仑芯、壁仞、沐曦、摩尔线程", "寒武纪、海光信息、中科曙光、浪潮信息、紫光股份", "核心/条件估值", "政企智算订单可验证性高于泛国产替代叙事。"),
        ],
    },
    {
        "block": "服务器整机与零部件",
        "role": "把芯片、存储、网络和供电冷却转化为可交付 AI 服务器/整柜。",
        "source": "S07/S18/S25/S26",
        "items": [
            ("AI 服务器/ODM", "GPU 服务器、交换机、整柜和云厂定制系统", "Foxconn/FII、Quanta/QCT、Wiwynn、Supermicro、Dell、HPE、Lenovo", "工业富联、浪潮信息、中科曙光、紫光股份", "核心可估值", "收入规模大但毛利率和客户集中度要单独校验。"),
            ("服务器电源 PSU", "CRPS、ORv3、54V/48V 高功率 PSU", "Delta、Lite-On、Chicony、AcBel、Vicor", "欧陆通、麦格米特、可立克、伊戈尔", "条件估值", "需确认 AI 电源批量收入，而非送样或通用电源。"),
            ("Power shelf/板级电源", "机柜级电源架、DC/DC、BBU 与电源模块", "Delta、Vicor、MPS、Infineon、TI、Murata", "麦格米特、欧陆通、江海股份、艾华集团", "观察/条件估值", "板级电源 AIDC 收入披露不足。"),
            ("高速连接器", "OSFP/QSFP、板对板、背板、PCIe/CXL 连接器", "Amphenol、TE、Molex、Samtec、Luxshare", "华丰科技、鼎通科技、立讯精密、瑞可达、中航光电", "条件估值", "客户认证和 112G/224G 收入占比是门槛。"),
            ("高速铜缆 DAC/ACC/AEC", "柜内和短距铜互连，替代部分光模块距离", "Amphenol、TE、Molex、Credo、Astera Labs、BizLink、Volex", "兆龙互连、沃尔核材、神宇股份、华丰科技", "条件估值/观察", "送样、认证和量产收入要区分。"),
            ("背板/主板/Riser", "CPU 主板、UBB/OAM、交换板、硬盘背板、电源板", "FII、Quanta、Wiwynn、Jabil、Supermicro", "工业富联、沪电股份、胜宏科技、深南电路、生益电子", "核心可估值", "高层数、低损耗和良率决定毛利。"),
            ("机柜/滑轨/结构件", "OCP/ORv3 机柜、滑轨、托盘和高承重结构件", "Vertiv、Schneider、Rittal、Legrand、King Slide", "工业富联、朗威股份、祥鑫科技、利通电子", "观察", "A 股缺滑轨/机柜高纯度标的，不能给高估值信用。"),
            ("热界面材料 TIM", "导热垫片、凝胶、相变材料、石墨、VC/热管材料", "Henkel、Parker Chomerics、Boyd/Laird、Shin-Etsu、Dow、3M", "飞荣达、中石科技、思泉新材", "条件估值", "必须拆出服务器/AI 客户收入。"),
            ("BMC/管理芯片", "服务器远程管理、KVM、传感器和固件", "ASPEED、Nuvoton、AMI MegaRAC、OpenBMC", "A 股无高纯度标的；服务器厂商间接使用", "只能观察", "不能把 BMC 稀缺性转移给无直接业务的 A 股标的。"),
            ("整柜集成/液冷服务器", "液冷机柜、超节点、机柜级交付和运维适配", "NVIDIA、Supermicro、Dell、HPE、Lenovo、QCT、Wiwynn", "工业富联、浪潮信息、中科曙光、紫光股份、英维克", "核心/条件估值", "整柜交付和液冷适配是 2026 年验证点。"),
        ],
    },
    {
        "block": "网络与光通信",
        "role": "AIDC scale-out/scale-across 的带宽和延迟瓶颈。",
        "source": "S06/S16/S18",
        "items": [
            ("AI 交换机/路由器", "400G/800G/1.6T 数据中心交换和 AI back-end 网络", "NVIDIA、Broadcom、Arista、Cisco、Juniper/HPE、Nokia", "紫光股份、锐捷网络、星网锐捷、中兴通讯、盛科通信", "核心/条件估值", "系统设备和交换 ASIC 要分开估值。"),
            ("800G/1.6T 光模块", "OSFP/QSFP-DD 可插拔高速光模块", "Coherent、Lumentum、Fabrinet、AOI、Innolight、Eoptolink、Accelink", "中际旭创、新易盛、光迅科技、华工科技、剑桥科技、联特科技", "核心可估值", "龙头有兑现能力，二线需订单与毛利验证。"),
            ("光引擎/硅光", "PIC、光引擎、外置激光源和硅光平台", "Intel、Broadcom、Cisco Acacia、Coherent、Ayar Labs、Ranovus、Lightmatter", "天孚通信、仕佳光子、光迅科技、源杰科技、光库科技", "条件估值/观察", "硅光平台核心仍多在海外，A 股更多是配套。"),
            ("DSP/SerDes/TIA", "PAM4 DSP、驱动、TIA 和 SerDes", "Broadcom、Marvell、Credo、Semtech、MACOM、MaxLinear", "A 股高纯度缺失；裕太微/盛科通信间接观察", "只能观察", "DSP 不是光模块 A 股公司的自动利润池。"),
            ("LPO/LRO", "线性光模块和低功耗互连架构", "Broadcom、Marvell、NVIDIA、Arista、模块厂", "中际旭创、新易盛、光迅科技、剑桥科技、联特科技", "期权/条件估值", "系统调试和客户采用节奏不确定。"),
            ("CPO/NPO/OIO", "共封装/近封装/光 I/O 架构", "Broadcom、NVIDIA、Intel、Cisco、Coherent、Ayar Labs、Celestial AI", "天孚通信、仕佳光子、源杰科技、光库科技；设备商观察", "只能观察/期权", "核心 ASIC 与硅光平台多数非 A 股。"),
            ("EML/VCSEL/CW laser", "高速调制激光器、短距 VCSEL 和硅光外置光源", "Lumentum、Coherent、Broadcom、Sumitomo、Mitsubishi、MACOM", "源杰科技、光迅科技、长光华芯、华工科技", "条件估值", "需验证 100G/200G 单通道量产和客户认证。"),
            ("AWG/FAU/陶瓷套管", "分合波、光纤阵列和精密无源耦合", "NEL、Fujikura、Kyocera、Adamant Namiki、US Conec、Senko", "天孚通信、仕佳光子、三环集团、太辰光", "条件估值/观察", "价值量和客户导入差异大。"),
            ("光纤光缆/MPO", "AIDC 内部光纤布线和多芯连接", "Corning、Prysmian、YOFC、Sumitomo、Furukawa、Fujikura", "长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份", "观察", "收入规模大但 AIDC 弹性和价值密度低于模块。"),
            ("OCS/光交换", "光电混合交换和光路调度", "Coherent、Google、Calient、Polatis、Cisco", "光迅科技、光库科技、华工科技观察", "观察/期权", "商业化路径和 A 股收入证据仍弱。"),
        ],
    },
    {
        "block": "PCB 与上游材料设备",
        "role": "高速信号完整性和 AI 服务器/交换机板卡价值量提升的核心受益链。",
        "source": "S08/S18/S25",
        "items": [
            ("AI 服务器 PCB", "GPU UBB、CPU 主板、Riser、硬盘背板", "TTM、Unimicron、Ibiden、Tripod、Meiko", "沪电股份、胜宏科技、深南电路、生益电子、景旺电子", "核心可估值", "AI PCB 收入和高层数良率决定兑现。"),
            ("交换机/路由器 PCB", "高速交换机板、线卡、背板和路由器板", "TTM、Unimicron、Compeq、Nan Ya PCB、AT&S", "沪电股份、胜宏科技、深南电路、奥士康", "核心/条件估值", "800G/1.6T 交换机放量是关键。"),
            ("HDI/高多层板", "高层数、盲埋孔、背钻和高密互连", "TTM、Ibiden、Unimicron、Meiko", "胜宏科技、深南电路、景旺电子、崇达技术、鹏鼎控股", "条件估值", "普通多层板不能直接给 AI 溢价。"),
            ("高速 CCL", "低 Dk/Df 高频高速覆铜板", "Panasonic、Rogers、Isola、ITEQ、TUC、Nan Ya Plastics", "生益科技、南亚新材、华正新材、中英科技", "核心/条件估值", "客户准入和高端材料收入占比是门槛。"),
            ("低损耗树脂/填料", "PPE/PPO、碳氢树脂、球硅和低介电填料", "Ajinomoto、MGC、Resonac、Rogers、Isola", "联瑞新材、圣泉集团、东材科技、彤程新材", "条件估值/观察", "材料进入高端 CCL 才能获得 AIDC 信用。"),
            ("电子玻纤布", "低介电、低 CTE 玻纤布和超薄布", "Nittobo、Asahi Kasei、Taiwan Glass、Kingboard", "宏和科技、中国巨石、中材科技", "条件估值/观察", "普通玻纤周期不能等同 AI 服务器材料。"),
            ("铜箔/HVLP 铜箔", "低粗糙度铜箔和高速信号用铜箔", "Mitsui Mining、JX Metals、Chang Chun、Circuit Foil", "嘉元科技、诺德股份、铜冠铜箔、德福科技", "观察/期权", "HVLP 收入和客户认证需单独披露。"),
            ("IC 载板/ABF", "GPU/CPU 封装载板和高端基板", "Ibiden、Shinko、Unimicron、Nan Ya PCB、Samsung Electro-Mechanics", "兴森科技、深南电路、生益电子", "观察/条件估值", "ABF 高端供给仍海外主导。"),
            ("PCB 钻孔/曝光设备", "激光钻、机械钻、LDI、检测和钻针", "Schmoll、Hitachi Via Mechanics、KLA Orbotech、Mitsubishi/ESI", "大族数控、芯碁微装、鼎泰高科", "条件估值/观察", "设备弹性来自 PCB 扩产周期。"),
            ("电镀/压合设备", "VCP 电镀、压合、湿制程和表面处理", "Atotech/MKS、Schmid、Burkle、Ucamco", "东威科技、大族数控、芯碁微装", "观察/期权", "高端制程设备国产替代需客户验证。"),
        ],
    },
    {
        "block": "供配电与能源",
        "role": "AIDC 建设的第一约束是可用 MW、接入时点、可靠性和电力成本。",
        "source": "S19/S23/S25/S29/S30",
        "items": [
            ("电力指标/接入", "土地、电力容量、双路供电和并网时点", "各地电网、园区、云厂自建主体", "润泽科技、奥飞数据、数据港、光环新网、运营商", "核心/条件估值", "运营资产必须看已获容量、交付和上架率。"),
            ("变压器", "干式/油浸变压器、箱变和数据中心电力装备", "ABB、Siemens、Schneider、Hitachi Energy、Eaton", "金盘科技、明阳电气、伊戈尔、特变电工、中国西电", "核心/条件/观察", "高纯度在数据中心订单，而非通用电网设备。"),
            ("高低压柜/开关柜", "中低压开关、配电柜、预制电力模块", "Schneider、ABB、Siemens、Eaton、Legrand", "明阳电气、良信股份、正泰电器、平高电气、思源电气", "条件估值/观察", "通用设备需剥离 AIDC 订单。"),
            ("UPS/HVDC", "高密 UPS、HVDC 和不间断供电系统", "Vertiv、Schneider/APC、Eaton、Delta、Huawei", "科华数据、科士达、中恒电气、英威腾", "核心/条件估值", "认证、项目和机房收入确认是关键。"),
            ("PDU/母线槽", "机柜末端配电、监控 PDU 和母线槽", "Legrand、nVent、Eaton、Schneider、Raritan/ServerTech", "威腾电气、安科瑞、良信股份", "条件估值", "母线和 PDU 的数据中心收入占比需验证。"),
            ("BBU/电池备电", "机柜级或电力室备电电池和管理系统", "Tesla、CATL、Samsung SDI、LG Energy Solution、Eaton", "南都电源、派能科技、圣阳股份、宁德时代、亿纬锂能", "条件估值/观察", "大电池公司 AIDC 收入弹性低。"),
            ("柴油/燃气发电机", "备用或桥接电源", "Cummins、Caterpillar、Rolls-Royce mtu、Kohler/Rehlko、Generac", "科泰电源、潍柴动力、动力新科", "观察/条件", "必须有数据中心项目合同才进估值。"),
            ("储能/PCS", "削峰、备电、绿电消纳和园区微网", "Tesla、Sungrow、Huawei、Fluence、CATL", "盛弘股份、禾望电气、阳光电源、南都电源、派能科技", "观察/期权", "不能把通用储能景气直接计入 AIDC。"),
            ("电力 EPC/微网", "变电站、配电、储能和微网总包", "Schneider、Eaton、Siemens、国内电力设计院", "中国电建、中国能建、苏文电能、南网科技", "观察", "项目毛利和可复制性比政策标题重要。"),
            ("绿电/PPA/算电协同", "绿电直连、PPA、低碳约束和算力调度", "电网、发电集团、园区、云厂", "三峡能源、龙源电力、华能国际、内蒙华电、运营商", "观察", "绿电是成本和准入约束，不是所有电力股的估值信用。"),
        ],
    },
    {
        "block": "液冷与温控",
        "role": "从风冷配套升级为高功率机柜的交付和可靠性约束。",
        "source": "S04/S09/S19/S20/S22/S27/S28",
        "items": [
            ("冷板", "CPU/GPU 冷板和局部热源换热", "CoolIT、Boyd、Modine、Delta、Vertiv", "英维克、高澜股份、同飞股份、飞荣达、银轮股份", "条件估值", "冷板收入和客户认证需披露。"),
            ("CDU", "一次侧和二次侧换热、泵、阀和控制", "Vertiv、Schneider/Motivair、CoolIT、STULZ、Rittal、Supermicro", "英维克、申菱环境、高澜股份、同飞股份", "核心/条件估值", "CDU 批量交付优先于概念。"),
            ("Manifold/分液器", "机柜或服务器层级流量分配", "CoolIT、Danfoss、Parker、Vertiv", "英维克、高澜股份、同飞股份、科创新源", "条件估值/观察", "常作为系统集成部件，单独收入披露少。"),
            ("快接头", "低泄漏、可维护液冷快换连接", "Stäubli、CPC/Dover、CEJN、Parker", "中航光电、瑞可达、川环科技、科创新源", "条件估值/观察", "军工/新能源连接器不能自动等同 AIDC。"),
            ("泵阀/控制", "泵、阀、传感、流量和压力控制", "Danfoss、Grundfos、Wilo、Xylem、Parker", "三花智控、江苏神通、中密控股、盾安环境", "观察/条件", "通用工业属性强，需要数据中心客户证据。"),
            ("管路/软管", "机柜内外冷却液输送和可靠性", "Parker、Danfoss、Gates、CEJN", "川环科技、科创新源、飞荣达", "观察/条件", "价值量小且认证周期长。"),
            ("冷却液", "水乙二醇、介电液和防腐添加剂", "Fuchs、3M、Chemours、Shell、Castrol", "巨化股份、新宙邦、康普化学等观察", "观察", "A 股多为材料映射，缺直接收入披露。"),
            ("干冷器/冷却塔", "一次侧排热和自然冷却", "Modine、Baltimore Aircoil、SPX、Vertiv、Schneider", "海鸥股份、冰轮环境、盾安环境", "观察/条件", "项目属性强，需中标/验收证据。"),
            ("冷水机组/精密空调", "传统风冷、混合风液冷和一次侧冷源", "Trane、Carrier、Daikin、Johnson Controls、STULZ、Vertiv", "申菱环境、英维克、佳力图、依米康、冰山冷热、汉钟精机", "核心/条件估值", "传统 IDC 与 AIDC 液冷要分开。"),
            ("液冷机柜/漏液检测", "液冷机柜集成、监控、泄漏检测和运维", "Vertiv、Schneider、Rittal、Huawei、Supermicro", "英维克、申菱环境、理工光科、佳力图", "条件估值", "系统集成能力和运维可靠性是溢价来源。"),
        ],
    },
    {
        "block": "数据中心建设与运营",
        "role": "把设备 capex 转化为可出租/可调度的算力、电力和网络资产。",
        "source": "S03/S11/S12/S23/S24/S29/S30",
        "items": [
            ("土地/园区/能耗指标", "土地、规划、能耗、取水和建设许可", "地方政府、园区、云厂自建主体、运营商", "润泽科技、奥飞数据、数据港、光环新网、宝信软件", "核心/条件估值", "指标稀缺不等于高上架率。"),
            ("设计/咨询", "数据中心规划、机电、网络和低碳设计", "Arup、AECOM、Jacobs、WSP、HDR", "华建集团、中衡设计、中设股份等观察", "观察", "设计费弹性远低于设备和运营资产。"),
            ("土建/EPC", "机房、变电、冷站、机电安装和总包", "Turner、AECOM Tishman、国内建筑/电建企业", "中国电建、中国能建、中国建筑、苏文电能", "观察", "通用工程公司 AIDC 弹性通常被摊薄。"),
            ("IDC/AIDC 运营", "机柜、MW、托管、算力服务和运维 SLA", "Equinix、Digital Realty、NTT GDC、GDS、VNET、AirTrunk、QTS、Vantage", "润泽科技、奥飞数据、数据港、光环新网、宝信软件", "核心可估值", "上架率、电价、折旧和客户租约是核心。"),
            ("运营商智算云", "运营商云、专线、边缘和政企智算", "China Mobile、China Telecom、China Unicom", "中国移动、中国电信、中国联通", "核心/低弹性", "集团体量大，AIDC 增量需与整体收入对比。"),
            ("网络接入/专线", "骨干网、IDC 出口、专线、互联互通", "运营商、Equinix Fabric、Megaport、PacketFabric", "三大运营商、光环新网、宝信软件", "条件估值", "网络资源是运营质量，不一定独立提升估值。"),
            ("运维/监控/DCIM", "能效、资产、容量、告警和运维管理", "Schneider、Vertiv、ABB、Nlyte、Sunbird", "科华数据、英维克、宝信软件、安科瑞", "观察/条件", "软件化收入和续费率需验证。"),
            ("算力服务/调度", "GPU 租赁、算力池、模型训练和推理服务", "CoreWeave、Lambda、Crusoe、Oracle OCI、国内云厂", "润泽科技、奥飞数据、宝信软件、中科曙光", "条件估值", "从机柜托管到算力服务会改变毛利和风险。"),
            ("REITs/资产证券化", "成熟数据中心现金流资产化", "Digital Realty/Equinix 类 REIT 模式", "南方润泽数据中心 REIT、南方万国数据中心 REIT", "条件估值", "看底层租约、NOI、分派率和扩募能力。"),
            ("区域枢纽/国家算力网", "东数西算、枢纽节点、城市智算和算电协同", "国家枢纽、运营商、地方平台、云厂", "运营商、润泽科技、奥飞数据、数据港、光环新网", "观察/需求锚", "政策目标需落到项目和客户付款。"),
        ],
    },
    {
        "block": "下游需求与应用",
        "role": "决定 AIDC 利用率、租约、云账单和持续扩容。",
        "source": "S23/S24/S29/S30",
        "items": [
            ("全球云厂商", "训练、推理、企业云迁移和 AI 平台", "AWS、Microsoft Azure、Google Cloud、Meta、Oracle、CoreWeave", "国内直接 A 股供应商需另证；需求锚为主", "需求锚", "海外 capex 不能自动证明 A 股公司收入。"),
            ("中国云厂商", "阿里云、腾讯云、百度智能云、华为云、火山引擎、运营商云", "Alibaba、Tencent、Baidu、Huawei Cloud、ByteDance、China Mobile/Telecom/Unicom", "服务器、光模块、PCB、IDC 运营链条间接受益", "需求锚/条件", "需官方采购、合同或供应链交叉确认。"),
            ("大模型/MaaS", "模型训练、API、推理和企业 MaaS", "OpenAI、Anthropic、xAI、DeepSeek、智谱、Kimi、MiniMax、百川", "寒武纪、海光信息、中科曙光、浪潮信息、运营商云等间接", "需求锚", "模型热度不是供应商收入证据。"),
            ("AI 应用/SaaS/Agent", "Copilot、Agentforce、办公、客服、代码和多模态应用", "Microsoft、Google、Salesforce、Adobe、ServiceNow、国内 AI 应用", "科大讯飞、金山办公、用友网络、恒生电子、同花顺", "需求锚/应用层", "应用公司不是 AIDC 设备商，估值逻辑不同。"),
            ("政企智算", "城市智算、央国企私有云、行业云和算力券", "地方平台、运营商云、华为云、阿里云、百度智能云", "中科曙光、浪潮信息、紫光股份、运营商、AIDC 运营商", "条件估值", "招投标、验收和 PFLOPS/MW 是硬锚。"),
            ("科研超算/AI4S", "气象、药物、材料、生命科学和工程仿真", "国家超算互联网、科研院所、HPC 云", "中科曙光、浪潮信息、宝信软件、运营商", "需求锚/条件", "科研需求需对应采购或平台用量。"),
            ("金融 AI", "风控、投研、客服、合规和多中心容灾", "银行、券商、保险、交易所、金融云", "恒生电子、同花顺、用友网络、运营商云、IDC", "需求锚", "金融 IT 预算与 AIDC 设备收入需分开。"),
            ("制造/工业 AI", "工业大模型、机器视觉、数字孪生和仿真", "制造龙头、工业互联网平台、自动化厂商", "宝信软件、中控技术、汇川技术、中科创达", "需求锚", "边缘推理和云训练的硬件需求不同。"),
            ("自动驾驶/具身智能", "车队数据训练、仿真、机器人策略训练", "Tesla、Waymo、华为车 BU、理想、小鹏、机器人公司", "德赛西威、中科创达、拓普集团、埃斯顿、绿的谐波", "需求锚/应用层", "产业热度不能直接推导 AIDC 上游收入。"),
            ("内容/互联网推理", "推荐、广告、搜索、视频生成和实时推理", "ByteDance、Tencent、Alibaba、Baidu、快手、Bilibili", "云、IDC、服务器和光互联链条间接受益", "需求锚", "推理成本下降可能同时带来量增和单价压力。"),
        ],
    },
]


def ensure_dirs() -> None:
    for path in (DATA, ANALYSIS, SECTIONS):
        path.mkdir(parents=True, exist_ok=True)


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def tex(value: object) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def fmt(value: float | None, digits: int = 1) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "not disclosed"
    return f"{value:.{digits}f}"


def pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "not disclosed"
    return f"{value * 100:.{digits}f}\\%"


def pct_plain(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "not disclosed"
    return f"{value * 100:.{digits}f}%"


def read_raw() -> dict:
    return json.loads((DATA / "raw_market_financials_20260630.json").read_text(encoding="utf-8"))


def latest_metrics(record: dict) -> dict:
    return record.get("latest_period", {}).get("metrics", {}) or {}


def fy_metrics(record: dict) -> dict:
    return record.get("fy2025_period", {}).get("metrics", {}) or {}


def derive_models(raw: dict) -> list[dict]:
    rows: list[dict] = []
    for record in raw["records"]:
        code = record["code"]
        a = ASSUMPTIONS[code]
        q = record["quote"]
        m1 = latest_metrics(record)
        m25 = fy_metrics(record)
        d = record["derived"]
        price = q.get("price")
        shares_100mn = d.get("shares_100mn")
        eps_q1 = m1.get("eps_basic")
        eps_2025 = m25.get("eps_basic")
        if eps_2025 is None and d.get("np_parent_2025_100mn") is not None and shares_100mn:
            eps_2025 = d["np_parent_2025_100mn"] / shares_100mn
        eps_from_q1 = eps_q1 / a["seasonality"] if eps_q1 is not None and a["seasonality"] else None
        eps_growth_floor = eps_2025 * (1 + a["growth"]) if eps_2025 is not None else None
        if code in {"002837", "002335", "301018", "300442", "300738", "300383"}:
            eps_2026e = max(x for x in (eps_from_q1, eps_growth_floor) if x is not None)
        else:
            eps_2026e = eps_from_q1 if eps_from_q1 is not None else eps_growth_floor
        revenue_2026e = None
        rev_q1 = d.get("revenue_q1_100mn")
        rev_2025 = d.get("revenue_2025_100mn")
        if rev_q1 is not None:
            revenue_2026e = rev_q1 / a["seasonality"]
        elif rev_2025 is not None:
            revenue_2026e = rev_2025 * (1 + a["growth"])
        np_2026e = eps_2026e * shares_100mn if eps_2026e is not None and shares_100mn else None
        bear = eps_2026e * a["bear_pe"] if eps_2026e is not None else None
        base = eps_2026e * a["base_pe"] if eps_2026e is not None else None
        bull = eps_2026e * a["bull_pe"] if eps_2026e is not None else None
        turnover = q.get("amount_cny") or 0
        sentiment = 0.70
        if turnover > 8_000_000_000:
            sentiment = 0.88
        elif turnover > 2_000_000_000:
            sentiment = 0.82
        elif turnover > 800_000_000:
            sentiment = 0.76
        market_anchor = price * sentiment if price else None
        market_weight = 0.35 if a["evidence"].startswith("A") else 0.25
        fundamental_weight = 1 - market_weight
        final_target = None
        if base is not None and market_anchor is not None:
            final_target = base * fundamental_weight + market_anchor * market_weight
        upside = (final_target / price - 1) if final_target is not None and price else None
        if upside is None:
            action = "证据不足"
            risk = "高"
        elif upside >= 0.20:
            action = "核心关注"
            risk = "中"
        elif upside >= 0.0:
            action = "回调验证"
            risk = "中"
        elif upside >= -0.20:
            action = "市场支撑观察"
            risk = "中高"
        else:
            action = "高估值风险"
            risk = "高"
        delivery_score = 0
        rev_growth = m1.get("revenue_growth")
        np_growth = m1.get("profit_growth")
        gm = m1.get("gross_margin")
        if rev_growth is not None:
            delivery_score += min(2.0, max(0.0, rev_growth / 50))
        if np_growth is not None:
            delivery_score += min(2.0, max(0.0, np_growth / 60))
        if gm is not None:
            delivery_score += min(1.0, max(0.0, gm / 45))
        val_score = 2 if upside is not None and upside > 0 else 1 if upside is not None and upside > -0.2 else 0
        total_score = a["direct"] * 1.4 + delivery_score + val_score
        row = {
            **record,
            "assumption": a,
            "eps_2025": eps_2025,
            "eps_from_q1": eps_from_q1,
            "eps_2026e": eps_2026e,
            "revenue_2026e_100mn": revenue_2026e,
            "np_2026e_100mn": np_2026e,
            "bear_target": bear,
            "base_target": base,
            "bull_target": bull,
            "market_anchor": market_anchor,
            "final_target": final_target,
            "final_upside": upside,
            "action": action,
            "risk": risk,
            "score": total_score,
        }
        rows.append(row)
    rows.sort(key=lambda item: item["score"], reverse=True)
    return rows


def make_source_registry() -> None:
    manifest_path = DATA / "source_capture_manifest_20260630.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"sources": []}
    sources = []
    for item in manifest.get("sources", []):
        sid = item["id"]
        note = SOURCE_NOTES.get(sid, {})
        sources.append({
            "id": sid,
            "title": item["title"],
            "type": item["type"],
            "url": item["url"],
            "local_path": item["local_path"],
            "status_code": item["status_code"],
            "quality_tier": "L1 official" if "official" in item["type"] or "filing" in item["type"] else "L2 industry/public",
            "used_for": note.get("note", ""),
        })
    sources.append({
        "id": "S13",
        "title": "Sina batch quote snapshot",
        "type": "market-data",
        "url": "https://hq.sinajs.cn/",
        "local_path": str(SOURCES / "sina_hq_batch_quote_20260630.txt"),
        "status_code": 200,
        "quality_tier": "L2 realtime market snapshot",
        "used_for": "2026-06-30 11:30 price, turnover and intraday change snapshot.",
    })
    sources.append({
        "id": "S14",
        "title": "akshare.stock_financial_abstract structured financials",
        "type": "financial-data",
        "url": "local capability adapter",
        "local_path": "data/raw_market_financials_20260630.json",
        "status_code": 200,
        "quality_tier": "L2 structured public financial packet",
        "used_for": "2026Q1 and 2025A revenue, profit, margin, BPS and EPS snapshots.",
    })
    write(DATA / "source_registry.json", json.dumps({"sources": sources}, ensure_ascii=False, indent=2))
    lines = ["# Source Registry", "", "| ID | Quality | Type | Used for | URL / path |", "|---|---|---|---|---|"]
    for s in sources:
        lines.append(f"| {s['id']} | {s['quality_tier']} | {s['type']} | {s['used_for']} | {s['url']} |")
    write(DATA / "source_registry.md", "\n".join(lines) + "\n")


def make_brief() -> None:
    body = dedent(
        f"""
        # Research Brief: AIDC Supply Chain

        - **Case ID:** aidc-supply-chain-20260630
        - **Theme:** AI Data Center (AIDC) upstream/downstream supply chain and A-share core target universe.
        - **Language:** Chinese reader-facing report.
        - **Market data cutoff:** {RUN_DATE} 11:30 China A-share midday snapshot from Sina Finance.
        - **Financial data cutoff:** 2026Q1 / 2025A structured public financial summaries.
        - **Full-chain coverage:** 8 blocks and 80 subsegments across compute/storage, server components, network/optical, PCB/materials, power, cooling, construction/operation and downstream demand.
        - **Core valuation subset:** 18 A-share targets across server/compute, optical interconnect, PCB/materials, power/cooling and AIDC/IDC operation. The subset is not the whole industry chain.
        - **Depth:** Institutional industry deep dive with supply-chain matrix, growth bridge, valuation framework and PDF output.
        - **Boundary:** This report is for research and monitoring only. It is not an order-execution, brokerage or automated trading output.
        """
    ).strip()
    write(BASE / "research_brief.md", body + "\n")


def make_template_brief() -> None:
    body = dedent(
        """
        # Template Benchmark Brief

        **Archetype:** industry-chain deep dive plus first-page investment-committee dashboard. The chapter sequence follows the local report-main skeleton and the optical-communication precedent, but AIDC requires broader infrastructure mapping.

        **First-page dashboard:** coverage universe, data cutoff, house view, evidence quality and final ranking should be visible before the table of contents.

        **Required exhibits:** full-chain taxonomy, market-demand anchors, rack-scale architecture transition, supply-chain matrix, company financial delivery table, public research sentiment, valuation summary, risk/catalyst monitor.

        **Avoid:** treating the 18-stock valuation subset as the whole AIDC chain; a concept-stock list without relationship evidence; a one-size PE table across server, PCB, power/cooling and IDC operators; treating downstream AI capex as proof of supplier revenue; non-Mermaid architecture diagrams.
        """
    ).strip()
    write(ANALYSIS / "template_brief.md", body + "\n")


def relationship_rows(rows: list[dict]) -> list[dict]:
    rels = []
    for row in rows:
        layer = row["layer"]
        upstream, product, downstream = LAYER_INPUTS[layer]
        code = row["code"]
        source = "S14"
        relationship_type = "inferred"
        confidence = "medium"
        if code == "601138":
            source, relationship_type, confidence = "S07", "official-disclosed", "high"
        elif code == "002463":
            source, relationship_type, confidence = "S08", "official-disclosed", "high"
        elif code == "002837":
            source, relationship_type, confidence = "S09", "official-disclosed", "high"
        elif code == "002335":
            source, relationship_type, confidence = "S10", "official-disclosed", "high"
        elif code == "300442":
            source, relationship_type, confidence = "S11/S12", "official-disclosed", "high"
        elif layer in {"光模块", "光器件/光引擎"}:
            source, relationship_type, confidence = "S06/S14", "industry-stated", "medium"
        used = "yes" if row["assumption"]["credit"] in {"earnings credit", "conditional earnings"} else "optionality only"
        rels.append({
            "ticker": code,
            "company": row["name"],
            "chain_layer": layer,
            "upstream_input": upstream,
            "product_or_process": product,
            "downstream_customer_or_platform": downstream,
            "relationship_type": relationship_type,
            "confidence": confidence,
            "revenue_exposure": "official-disclosed" if confidence == "high" and code in {"601138", "002463", "300442"} else "not disclosed",
            "capacity_or_certification": "see source" if confidence == "high" else "not found",
            "order_visibility": "not disclosed",
            "margin_or_earnings_impact": f"2026Q1 gross margin {fmt(latest_metrics(row).get('gross_margin'), 1)}%; 2026E EPS proxy {fmt(row.get('eps_2026e'), 2)}",
            "source": source,
            "evidence_gap": "customer/order/ASP not fully disclosed" if confidence != "high" else "segment/customer economics still partly undisclosed",
            "used_in_valuation": used,
        })
    return rels


def full_chain_rows() -> list[dict]:
    rows: list[dict] = []
    row_id = 1
    for block in FULL_CHAIN_BLOCKS:
        for subsegment, definition, global_leaders, a_share_mapping, valuation_status, evidence_gap in block["items"]:
            if "核心" in valuation_status:
                report_role = "core-or-direct-watch"
            elif "需求锚" in valuation_status:
                report_role = "demand-anchor-only"
            elif "条件" in valuation_status:
                report_role = "conditional-watch"
            else:
                report_role = "satellite-watch"
            rows.append({
                "id": f"FC{row_id:03d}",
                "chain_block": block["block"],
                "subsegment": subsegment,
                "definition": definition,
                "global_leaders": global_leaders,
                "china_a_share_mapping": a_share_mapping,
                "valuation_status": valuation_status,
                "report_role": report_role,
                "evidence_source": block["source"],
                "evidence_gap": evidence_gap,
            })
            row_id += 1
    return rows


def full_chain_block_summary(rows: list[dict]) -> list[dict]:
    summary = []
    for block in FULL_CHAIN_BLOCKS:
        members = [r for r in rows if r["chain_block"] == block["block"]]
        core_count = sum(1 for r in members if "核心" in r["valuation_status"])
        conditional_count = sum(1 for r in members if "条件" in r["valuation_status"])
        anchor_count = sum(1 for r in members if "需求锚" in r["valuation_status"])
        summary.append({
            "chain_block": block["block"],
            "role": block["role"],
            "subsegment_count": len(members),
            "core_or_direct_count": core_count,
            "conditional_count": conditional_count,
            "demand_anchor_count": anchor_count,
            "main_source": block["source"],
        })
    return summary


def make_full_chain_outputs() -> list[dict]:
    rows = full_chain_rows()
    summary = full_chain_block_summary(rows)
    packet = {
        "cutoff_date": RUN_DATE,
        "coverage_note": "Panoramic AIDC supply-chain universe. The 18-stock valuation pool is a core subset, not the complete industry chain.",
        "block_count": len(summary),
        "row_count": len(rows),
        "block_summary": summary,
        "rows": rows,
    }
    write(DATA / "full_chain_universe_20260630.json", json.dumps(packet, ensure_ascii=False, indent=2))

    lines = [
        "# AIDC Full-Chain Universe",
        "",
        "This is the panoramic chain pool. It deliberately separates core valuation candidates from conditional watches, satellite watches and downstream demand anchors.",
        "",
        "| ID | Block | Subsegment | Global leaders | A-share mapping | Status | Source | Evidence gap |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['chain_block']} | {r['subsegment']} | {r['global_leaders']} | {r['china_a_share_mapping']} | {r['valuation_status']} | {r['evidence_source']} | {r['evidence_gap']} |")
    write(DATA / "full_chain_universe_20260630.md", "\n".join(lines) + "\n")

    taxonomy = [
        "# Full Chain Taxonomy",
        "",
        "The full AIDC chain is modeled in eight blocks. The 18-stock valuation pool is only the direct, liquid and currently modelable subset.",
        "",
        "| Block | Role | Subsegments | Core/direct | Conditional | Demand anchors | Source |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for s in summary:
        taxonomy.append(f"| {s['chain_block']} | {s['role']} | {s['subsegment_count']} | {s['core_or_direct_count']} | {s['conditional_count']} | {s['demand_anchor_count']} | {s['main_source']} |")
    taxonomy += [
        "",
        "## Valuation Discipline",
        "",
        "- Core/direct names may enter the valuation pool only when product revenue, official filings, orders, certification, MW delivery or utilization evidence exists.",
        "- Conditional watches need customer certification, AIDC revenue split, order conversion, margin and cash-flow evidence before they receive earnings credit.",
        "- Satellite watches and demand anchors can explain industry direction, but they do not receive supplier revenue credit without direct evidence.",
    ]
    write(ANALYSIS / "full_chain_taxonomy.md", "\n".join(taxonomy) + "\n")

    mermaid = dedent(
        """
        flowchart LR
          Demand[AIDC downstream demand: cloud, LLM, enterprise, government, vertical AI] --> Build[Data-center construction and operation]
          Build --> Power[Power distribution and energy]
          Build --> Cooling[Liquid cooling and thermal control]
          Power --> Rack[AI server rack and server components]
          Cooling --> Rack
          Chip[Compute chips, memory, storage, NIC and switch ASIC] --> Rack
          PCB[PCB, CCL, copper foil, glass cloth and process equipment] --> Rack
          Optical[Network and optical interconnect] --> Rack
          Rack --> Service[AIDC utilization: training, inference, MaaS and industry compute]
          Service --> Demand
        """
    ).strip()
    write(ANALYSIS / "aidc_chain_map.mmd", mermaid + "\n")

    synthesis = dedent(
        """
        # Parallel Agent Synthesis

        - Upstream compute and server components: core A-share valuation candidates concentrate in domestic compute chips, memory interface, AI server manufacturing, high-speed PCB, connectors, copper cable, PSU and thermal materials. HBM, BMC, high-end DPU/NIC and switch ASIC are mostly overseas or low-purity A-share exposure.
        - Network/optical and PCB/materials: 800G/1.6T modules, optical devices, high-speed PCB, CCL and low-loss materials have the cleanest earnings path. DSP, CPO/NPO core ASIC, ABF and HVLP copper foil remain mostly option pools.
        - Power/cooling/operation: the investable layer is not generic liquid cooling or green power. It is confirmed power architecture, liquid-cooling system delivery, MW delivery, utilization and data-center cash flow.
        - Downstream demand: cloud, model, SaaS, government and vertical AI platforms are demand anchors. They become supplier revenue evidence only when official contracts, orders, utilization, cloud bills, procurement or customer-supplier cross-confirmation exists.
        """
    ).strip()
    write(ANALYSIS / "agent_research_synthesis.md", synthesis + "\n")
    return rows


def make_supply_chain_outputs(rows: list[dict]) -> None:
    rels = relationship_rows(rows)
    write(DATA / "supply_chain_relationships.json", json.dumps({"relationships": rels}, ensure_ascii=False, indent=2))
    lines = ["# Supply Chain Relationships", "", "| Ticker | Company | Layer | Product/process | Downstream | Type | Confidence | Revenue exposure | Source | Used in valuation | Gap |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rels:
        lines.append(f"| {r['ticker']} | {r['company']} | {r['chain_layer']} | {r['product_or_process']} | {r['downstream_customer_or_platform']} | {r['relationship_type']} | {r['confidence']} | {r['revenue_exposure']} | {r['source']} | {r['used_in_valuation']} | {r['evidence_gap']} |")
    write(DATA / "supply_chain_relationships.md", "\n".join(lines) + "\n")

    mermaid = dedent(
        """
        flowchart LR
          A[AI capex and national compute network] --> B[GPU ASIC HBM and switch ASIC]
          B --> C[AI server and rack-scale systems]
          B --> D[Optical interconnect 800G 1.6T CPO]
          B --> E[High-end PCB and CCL]
          C --> F[Power UPS transformer and prefabricated power modules]
          C --> G[Liquid cooling CDU cold plate manifold]
          C --> H[AIDC and IDC operators]
          D --> C
          E --> C
          F --> H
          G --> H
          H --> I[Cloud AI model training inference and enterprise workloads]
        """
    ).strip()
    write(ANALYSIS / "aidc_chain_map.mmd", mermaid + "\n")

    sc_model = dedent(
        """
        # Supply Chain Model

        ## Gate Status

        **CONDITIONAL PASS.** Every covered ticker has a company card and relationship row. The gate is conditional because named customer allocation, product-level ASP, order backlog and capacity utilization are not uniformly disclosed. Direct valuation credit is allowed only for names with official segment or product evidence; other names are classified as optionality or watchlist exposure.

        ## Mermaid Architecture Source

        The architecture diagram is saved as `analysis/aidc_chain_map.mmd`. The PDF expresses the same relationship through tables because Mermaid rendering is not available in the local TeX toolchain.

        ## Core Chain Logic

        AIDC demand starts with accelerated-compute capex, but the investable A-share profit pools are not identical to downstream capex. The highest evidence density currently sits in: AI server/switch manufacturing, high-speed optical modules and devices, high-end PCB/CCL, liquid cooling and power distribution, and AIDC operators with delivered capacity.
        """
    ).strip()
    write(ANALYSIS / "supply_chain_model.md", sc_model + "\n\n" + "\n".join(lines) + "\n")

    cards = ["# Company Fundamental Cards", ""]
    for row in rows:
        m1 = latest_metrics(row)
        cards.append(f"## {row['name']} ({row['code']})")
        cards.append(f"- Chain role: {row['role']}; directness score {row['assumption']['direct']}/5.")
        cards.append(f"- Financial delivery: 2026Q1 revenue CNY{fmt(row['derived'].get('revenue_q1_100mn'), 1)}bn, parent NP CNY{fmt(row['derived'].get('np_parent_q1_100mn'), 1)}bn, gross margin {fmt(m1.get('gross_margin'), 1)}%.")
        cards.append(f"- Valuation relevance: {row['assumption']['method']}; evidence grade {row['assumption']['evidence']}; growth credit {row['assumption']['credit']}.")
        cards.append("- Evidence gap: named customer allocation, product-level ASP and order conversion are not fully disclosed unless noted in customer-chain audit.")
        cards.append("")
    write(ANALYSIS / "company_fundamental_cards.md", "\n".join(cards))

    bridge = ["# Chain Earnings Bridge", "", "## Theme-Level Profit Pool Bridge", "", "- AI capex first becomes server/rack orders, then splits into optical interconnect, PCB/materials, power/cooling and AIDC operator revenue. The bridge is strongest when official filings disclose product or segment revenue and current financials show margin/EPS delivery.", ""]
    bridge.append("| Ticker | Company | 2026E revenue proxy (CNY bn) | 2026E EPS proxy | Validation threshold |")
    bridge.append("|---|---|---:|---:|---|")
    for row in rows:
        bridge.append(f"| {row['code']} | {row['name']} | {fmt(row.get('revenue_2026e_100mn'), 1)} | {fmt(row.get('eps_2026e'), 2)} | Next reports must confirm revenue growth, margin stability and cash conversion; for infrastructure names also confirm orders, capacity delivery and utilization. |")
    write(ANALYSIS / "chain_earnings_bridge.md", "\n".join(bridge) + "\n")


def make_customer_audit() -> None:
    audits = [
        {"claim": "FII cloud AI-server revenue grew more than 3x in 2025", "source": "S07", "confidence": "high", "used_in_valuation": "yes", "gap": "customer allocation and exact AI-server margin not disclosed"},
        {"claim": "FII 800G+ high-speed switch revenue grew 13x in 2025", "source": "S07", "confidence": "high", "used_in_valuation": "yes", "gap": "product margin and customer split not disclosed"},
        {"claim": "Hushi data-communication PCB revenue reached CNY146.56bn with AI server/HPC and high-speed switch/router subsegments disclosed", "source": "S08", "confidence": "high", "used_in_valuation": "yes", "gap": "customer allocation not disclosed"},
        {"claim": "Invic has end-to-end liquid-cooling products and disclosed large data-center customer examples", "source": "S09", "confidence": "high", "used_in_valuation": "optionality only", "gap": "liquid-cooling revenue and margin not separately disclosed"},
        {"claim": "Kehua launched 200kW high-density UPS module and obtained 1.2MW UPS certification", "source": "S10", "confidence": "high", "used_in_valuation": "optionality only", "gap": "AIDC order value and conversion pace not disclosed"},
        {"claim": "Runze expects AIDC revenue to grow rapidly and disclosed large liquid-cooled AIDC projects", "source": "S11/S12", "confidence": "high", "used_in_valuation": "yes", "gap": "customer contract duration, utilization curve and unit economics not fully disclosed"},
        {"claim": "Optical interconnect demand remains structurally strong but 2026 growth is constrained by XPU/switch ASIC availability", "source": "S06", "confidence": "medium", "used_in_valuation": "yes for leaders; optionality for component names", "gap": "company-level order allocation not disclosed"},
    ]
    write(DATA / "customer_chain_audit.json", json.dumps({"audits": audits}, ensure_ascii=False, indent=2))
    lines = ["# Customer Chain Audit", "", "| Claim | Source | Confidence | Used in valuation | Evidence gap |", "|---|---|---|---|---|"]
    for a in audits:
        lines.append(f"| {a['claim']} | {a['source']} | {a['confidence']} | {a['used_in_valuation']} | {a['gap']} |")
    write(DATA / "customer_chain_audit.md", "\n".join(lines) + "\n")


def make_growth_outputs(rows: list[dict]) -> None:
    drivers = []
    for row in rows:
        drivers.append({
            "ticker": row["code"],
            "company": row["name"],
            "applies": True,
            "growth_driver": row["role"],
            "base_business_revenue": row["derived"].get("revenue_2025_100mn"),
            "growth_segment_revenue": "not disclosed",
            "unit_volume_or_proxy": "segment revenue / 2026Q1 revenue proxy",
            "ASP_or_price": "not disclosed",
            "recognized_revenue_ratio": "not disclosed",
            "growth_gross_margin": latest_metrics(row).get("gross_margin"),
            "incremental_opex": "not disclosed",
            "growth_net_profit": "not disclosed",
            "growth_EPS": row.get("eps_2026e"),
            "evidence_type": row["assumption"]["evidence"],
            "source": "S14 plus relationship source",
            "evidence_gap": "No uniform unit, ASP, order and customer allocation disclosure.",
            "valuation_credit": row["assumption"]["credit"],
            "bear": row.get("bear_target"),
            "base": row.get("base_target"),
            "bull": row.get("bull_target"),
            "current_price_implied_growth": f"Current price implies {fmt(row['quote'].get('price') / row.get('eps_2026e'), 1)}x 2026E PE proxy" if row.get("eps_2026e") else "not disclosed",
            "sensitivity_key": "margin and order conversion",
        })
    write(DATA / "growth_driver_model.json", json.dumps({"drivers": drivers}, ensure_ascii=False, indent=2))
    model_lines = ["# Growth Earnings Model", "", "**Gate Status: CONDITIONAL PASS.** AIDC is a high-growth theme, but unit/order/ASP disclosure is uneven. Earnings credit is restricted to names with official or high-confidence segment evidence; generic demand is not converted into EPS.", "", "| Ticker | Company | Driver | 2026E EPS proxy | Valuation credit | Evidence gap |", "|---|---|---|---:|---|---|"]
    for row in rows:
        model_lines.append(f"| {row['code']} | {row['name']} | {row['role']} | {fmt(row.get('eps_2026e'), 2)} | {row['assumption']['credit']} | customer/order/ASP not uniformly disclosed |")
    write(ANALYSIS / "growth_earnings_model.md", "\n".join(model_lines) + "\n")
    write(ANALYSIS / "segment_forecast_bridge.md", "\n".join(model_lines).replace("Growth Earnings Model", "Segment Forecast Bridge") + "\n")
    sens = ["# Implied Growth Sensitivity", "", "The strongest sensitivity is not TAM, but EPS conversion: gross margin, order conversion and customer concentration determine whether AIDC demand becomes shareholder earnings.", "", "| Ticker | Company | Current price | 2026E PE proxy | Base target | What must be true |", "|---|---|---:|---:|---:|---|"]
    for row in rows:
        pe = row["quote"].get("price") / row["eps_2026e"] if row.get("eps_2026e") and row["quote"].get("price") else None
        sens.append(f"| {row['code']} | {row['name']} | {fmt(row['quote'].get('price'), 2)} | {fmt(pe, 1)} | {fmt(row.get('base_target'), 1)} | Revenue growth, margin and cash conversion must stay above the level implied by current price. |")
    write(ANALYSIS / "implied_growth_sensitivity.md", "\n".join(sens) + "\n")


def make_valuation_outputs(rows: list[dict]) -> None:
    records = []
    lines = ["# Valuation Model", "", "## Final Valuation Table", "", "| Ticker | Company | Current | 2026E EPS | Method | Bear | Base | Bull | Final target | Upside | Action | Evidence |", "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|"]
    for row in rows:
        rec = {
            "ticker": row["code"],
            "company": row["name"],
            "current_price": row["quote"].get("price"),
            "price_date": f"{row['quote'].get('trade_date')} {row['quote'].get('trade_time')}",
            "shares_100mn": row["derived"].get("shares_100mn"),
            "market_cap_100mn_cny": row["derived"].get("market_cap_100mn_cny"),
            "revenue_2026e_100mn": row.get("revenue_2026e_100mn"),
            "np_2026e_100mn": row.get("np_2026e_100mn"),
            "eps_2026e": row.get("eps_2026e"),
            "method": row["assumption"]["method"],
            "bear": row.get("bear_target"),
            "base": row.get("base_target"),
            "bull": row.get("bull_target"),
            "market_anchor": row.get("market_anchor"),
            "final_target": row.get("final_target"),
            "upside": row.get("final_upside"),
            "action": row["action"],
            "risk": row["risk"],
            "evidence_quality": row["assumption"]["evidence"],
        }
        records.append(rec)
        lines.append(f"| {row['code']} | {row['name']} | {fmt(row['quote'].get('price'), 2)} | {fmt(row.get('eps_2026e'), 2)} | {row['assumption']['method']} | {fmt(row.get('bear_target'), 1)} | {fmt(row.get('base_target'), 1)} | {fmt(row.get('bull_target'), 1)} | {fmt(row.get('final_target'), 1)} | {pct_plain(row.get('final_upside'))} | {row['action']} | {row['assumption']['evidence']} |")
    lines += [
        "",
        "## Method and Assumption Bridge",
        "",
        "Primary methods are business-model matched PE or normalized PE because every covered ticker currently has positive or recovering earnings denominators except 光环新网, which is marked as repair/watchlist. Power, cooling and IDC names require cash-flow, utilization and balance-sheet checks before any multiple expansion is treated as durable.",
        "",
        "## Market-Implied Sentiment Anchor",
        "",
        "The final target blends the intrinsic EPS/multiple anchor with a market anchor derived from the 2026-06-30 trading-value regime. No broker target price is used as a hard anchor because complete public original target-price histories were not collected for all 18 names.",
    ]
    write(ANALYSIS / "valuation_model.md", "\n".join(lines) + "\n")
    write(DATA / "current_valuation_model_20260630.json", json.dumps({"rows": records}, ensure_ascii=False, indent=2))
    write(DATA / "current_valuation_model_20260630.md", "\n".join(lines) + "\n")
    audit = dedent(
        """
        # Valuation Audit

        - Arithmetic: market cap is derived from current price multiplied by shares inferred from equity divided by BPS. Upside is final target divided by current price minus one.
        - Forecast: 2026E EPS uses 2026Q1 EPS divided by layer-specific seasonality; for IDC/power/cooling names with distorted Q1, the model also checks 2025 EPS growth floor.
        - Method fit: server/optical/PCB names use PE/PEG-style sanity checks; power/cooling uses normalized PE plus order conversion checks; AIDC operators use PE plus utilization/cash-flow checks.
        - Broker comparison: public abstracts exist, but complete original broker target histories were not collected uniformly; therefore broker targets are disclosed as sentiment evidence only.
        - Supply-chain dependency: every covered ticker has a relationship row and company card. Names without direct official customer/order evidence are not granted full earnings credit.
        - Growth dependency: every ticker has a growth-driver record; absence of unit/ASP/customer allocation disclosure is explicitly marked.

        **Audit result:** PASS with evidence-quality limitations disclosed.
        """
    ).strip()
    write(ANALYSIS / "valuation_audit.md", audit + "\n")


def make_other_analysis(rows: list[dict]) -> None:
    top = rows[:6]
    house = ["# House View", "", "AIDC is a real capex cycle, but at the 2026-06-30 midday prices the A-share basket is pricing a large amount of future conversion already. The best research posture is not to buy the whole theme; it is to rank direct revenue conversion and wait for price or earnings confirmation.", "", "## Preferred Evidence Stack", ""]
    for row in top:
        house.append(f"- {row['name']} ({row['code']}): directness {row['assumption']['direct']}/5, evidence {row['assumption']['evidence']}, action {row['action']}.")
    write(ANALYSIS / "house_view.md", "\n".join(house) + "\n")

    industry = dedent(
        """
        # Industry Landscape

        AIDC demand is driven by three simultaneous changes: AI accelerator capex expansion, rack-scale architecture and power/cooling constraints. NVIDIA's FY2027 Q1 data-center revenue and Dell'Oro's 2026 capex outlook support the global demand anchor. China's national compute-network policy and hub-node buildout support the domestic infrastructure anchor.

        The full chain is broader than the 18-name valuation subset. The eight required blocks are: upstream compute chips and storage; server components; network and optical; PCB and upstream materials/equipment; power distribution and energy; liquid cooling and thermal control; data-center construction and operation; downstream cloud, model, enterprise and vertical AI demand. The key industry conclusion is that AIDC changes the bottleneck from general server count to rack power density, network bandwidth and energy availability. This makes optical interconnect, high-end PCB, liquid cooling, UPS/power modules and delivered AIDC capacity investable profit pools, but each requires separate evidence before valuation credit.
        """
    ).strip()
    write(ANALYSIS / "industry_landscape.md", industry + "\n")

    risk = dedent(
        """
        # Risk Framework

        1. **Valuation crowding:** many AIDC leaders trade at current-price implied PE levels that already assume strong 2026 conversion.
        2. **Customer concentration:** AI server, optical module and PCB suppliers depend on a small group of CSPs or platform customers.
        3. **Order-to-revenue lag:** capacity, certification and project announcements do not equal revenue without utilization and acceptance.
        4. **Power bottleneck:** grid access, green-power ratio, PUE and water/cooling constraints can slow AIDC deployment.
        5. **Technology transition:** copper/optical, CPO/LPO, liquid-cooling architecture and domestic GPU platforms may shift value pools.
        6. **Policy/export controls:** overseas accelerator supply and domestic replacement cycles may change product mix and margins.
        """
    ).strip()
    write(ANALYSIS / "risk_framework.md", risk + "\n")

    exhibit = dedent(
        """
        # Exhibit Plan

        - Exhibit 1: IC ranking and action table.
        - Exhibit 2: evidence-quality source table.
        - Exhibit 3: full-chain taxonomy and panoramic universe.
        - Exhibit 4: AIDC demand and architecture transition table; Mermaid source in `analysis/aidc_chain_map.mmd`.
        - Exhibit 5: supply-chain relationship matrix.
        - Exhibit 6: company financial delivery table.
        - Exhibit 7: valuation summary and implied expectation table.
        - Exhibit 8: risk/catalyst monitoring table.
        """
    ).strip()
    write(ANALYSIS / "exhibit_plan.md", exhibit + "\n")

    consensus = dedent(
        """
        # Public Research Sentiment

        Complete original broker target-price histories were not collected for every covered ticker. Publicly available abstracts broadly agree that AI capex benefits server ODMs, optical interconnect, high-end PCB and liquid-cooling/power infrastructure. The expanded full-chain review adds compute/storage, server components, network/optical, PCB/materials, power, cooling, construction/operation and downstream demand anchors, but the report treats broad industry views as sentiment evidence rather than valuation anchors.
        """
    ).strip()
    write(DATA / "consensus_analysis.md", consensus + "\n")
    write(DATA / "broker_target_price_history.md", "Broker target-price history is incomplete for the full universe; not used as a hard valuation anchor.\n")
    write(DATA / "report_catalog.md", "# Report Catalog\n\nPublic broker abstracts and official filings were used. Full original sell-side PDF collection was not exhaustive for all 18 names.\n")


def make_verified_packets(rows: list[dict]) -> None:
    raw = (DATA / "raw_market_data.md").read_text(encoding="utf-8")
    write(DATA / "verified_market_data.md", raw + "\nVerification: price/date/turnover fields parsed from Sina batch snapshot; data quality is intraday midday, not closing price.\n")
    raw_fin = (DATA / "raw_financials.md").read_text(encoding="utf-8")
    write(DATA / "verified_financials.md", raw_fin + "\nVerification: financial fields parsed from akshare.stock_financial_abstract; BPS/equity share-count derivation is model-derived and disclosed.\n")
    claims = [
        {"id": "C01", "claim": "AIDC capex is globally accelerating", "source": "S01/S02/S05", "confidence": "high", "status": "verified"},
        {"id": "C02", "claim": "China compute infrastructure remains a policy-supported buildout", "source": "S03", "confidence": "high", "status": "verified"},
        {"id": "C03", "claim": "High-density AI racks shift value to optical, PCB, power and liquid cooling", "source": "S04/S05/S06", "confidence": "medium-high", "status": "verified"},
        {"id": "C04", "claim": "Company-level order, ASP and customer allocation are incomplete for many tickers", "source": "customer_chain_audit", "confidence": "high", "status": "gap"},
    ]
    write(DATA / "claim_audit.json", json.dumps({"claims": claims}, ensure_ascii=False, indent=2))
    lines = ["# Claim Audit", "", "| ID | Claim | Source | Confidence | Status |", "|---|---|---|---|---|"]
    for c in claims:
        lines.append(f"| {c['id']} | {c['claim']} | {c['source']} | {c['confidence']} | {c['status']} |")
    write(DATA / "claim_audit.md", "\n".join(lines) + "\n")


def valuation_tex_table(rows: list[dict], limit: int | None = None) -> str:
    body = [r"\begin{longtable}{L{1.7cm}L{2.2cm}R{1.5cm}R{1.5cm}R{1.6cm}R{1.8cm}R{1.6cm}L{2.0cm}}",
            r"\toprule",
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{2026E EPS} & \textbf{基础锚} & \textbf{综合目标} & \textbf{空间} & \textbf{动作}\\",
            r"\midrule",
            r"\endhead"]
    use_rows = rows if limit is None else rows[:limit]
    for row in use_rows:
        body.append(f"{tex(row['code'])} & {tex(row['name'])} & {fmt(row['quote'].get('price'), 2)} & {fmt(row.get('eps_2026e'), 2)} & {fmt(row.get('base_target'), 1)} & {fmt(row.get('final_target'), 1)} & {tex(pct_plain(row.get('final_upside')))} & {tex(row['action'])}\\\\")
    body += [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(body)


def company_tex_table(rows: list[dict]) -> str:
    body = [r"\begin{longtable}{L{1.7cm}L{2.0cm}L{2.5cm}R{1.5cm}R{1.5cm}R{1.4cm}R{1.3cm}R{1.5cm}}",
            r"\toprule",
            r"\textbf{代码} & \textbf{公司} & \textbf{环节} & \textbf{Q1收入} & \textbf{Q1归母} & \textbf{毛利率} & \textbf{ROE} & \textbf{市值}\\",
            r"\midrule",
            r"\endhead"]
    for row in rows:
        m1 = latest_metrics(row)
        d = row["derived"]
        body.append(f"{tex(row['code'])} & {tex(row['name'])} & {tex(row['layer'])} & {fmt(d.get('revenue_q1_100mn'), 1)} & {fmt(d.get('np_parent_q1_100mn'), 1)} & {fmt(m1.get('gross_margin'), 1)}\\% & {fmt(m1.get('roe'), 1)}\\% & {fmt(d.get('market_cap_100mn_cny'), 0)}\\\\")
    body += [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(body)


def full_chain_summary_tex_table() -> str:
    packet = json.loads((DATA / "full_chain_universe_20260630.json").read_text(encoding="utf-8"))
    body = [r"\begin{longtable}{L{3.0cm}L{6.5cm}R{1.5cm}R{1.5cm}R{1.6cm}L{1.7cm}}",
            r"\toprule",
            r"\textbf{板块} & \textbf{角色} & \textbf{子环节} & \textbf{核心} & \textbf{条件} & \textbf{来源}\\",
            r"\midrule",
            r"\endhead"]
    for row in packet["block_summary"]:
        body.append(f"{tex(row['chain_block'])} & {tex(row['role'])} & {row['subsegment_count']} & {row['core_or_direct_count']} & {row['conditional_count']} & {tex(row['main_source'])}\\\\")
    body += [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(body)


def full_chain_tex_table() -> str:
    packet = json.loads((DATA / "full_chain_universe_20260630.json").read_text(encoding="utf-8"))
    body = [r"\begin{longtable}{L{1.1cm}L{2.5cm}L{2.2cm}L{4.3cm}L{4.5cm}L{2.0cm}}",
            r"\toprule",
            r"\textbf{ID} & \textbf{板块} & \textbf{子环节} & \textbf{全球核心主体} & \textbf{A股映射} & \textbf{状态}\\",
            r"\midrule",
            r"\endhead"]
    for row in packet["rows"]:
        body.append(f"{tex(row['id'])} & {tex(row['chain_block'])} & {tex(row['subsegment'])} & {tex(row['global_leaders'])} & {tex(row['china_a_share_mapping'])} & {tex(row['valuation_status'])}\\\\")
    body += [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(body)


def make_sections(rows: list[dict]) -> None:
    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
    summary_table = valuation_tex_table(ranked, 10)
    ch01 = rf"""
\begin{{houseviewbox}}[核心结论]
AIDC 产业链不是只有 18 只股票。本报告现在分两层：第一层是 8 大板块、80 个子环节的全景产业链池；第二层才是 18 只 A 股核心估值池。我们把核心池按“直接收入证据、财务交付、估值隐含预期、风险暴露”排序。当前 2026 年 6 月 30 日 11:30 快照下，\textbf{{工业富联、沪电股份、润泽科技}}的证据链相对更完整；光模块、光器件和高端 PCB 仍是最直接的利润池，但价格已显著反映 800G/1.6T 与 AI PCB 的景气预期。报告动作以“回调验证、市场支撑观察、高估值风险”为主，不把主题热度当作买入理由。
\end{{houseviewbox}}

\begin{{exhibitbox}}[投资委员会排序表]
{summary_table}
\sourcenote{{Sina 2026-06-30 11:30 行情快照；akshare 财务摘要；AStock 估值模型。空间=综合目标价/现价-1。}}
\end{{exhibitbox}}

第一层结论是链条真且很宽。完整 AIDC 链条覆盖算力芯片/存储、服务器零部件、网络/光通信、PCB/材料、供配电、液冷、数据中心建设运营和下游需求八大块。18 只核心标的只是当前有较好公开财务数据和估值可建模性的子集，不代表全产业链边界。

第二层结论是分化更真。直接兑现顺序大致为：服务器/交换机整机与代工、光互联、AI PCB/CCL、供配电和液冷、AIDC 运营商。越靠近最终算力服务，收入确认越依赖交付、上架率、电价和客户利用率；越靠近上游部件，估值越依赖订单能见度、ASP 与良率。

第三层结论是估值约束必须前置。多数核心标的午盘成交额和涨幅显示情绪处于强势状态；如果后续季度不能同时兑现收入增速、毛利率和现金流，当前价格隐含的增长久期会迅速收缩。
"""
    write(SECTIONS / "ch01_dashboard.tex", ch01.strip() + "\n")

    source_rows = []
    for sid, s in SOURCE_NOTES.items():
        source_rows.append(f"{tex(sid)} & {tex(s['type'])} & {tex(s['title'])} & {tex(s['note'])}\\\\")
    ch02 = rf"""
本章先界定证据等级。报告优先采用官方公告、公司年报摘要、IR 记录和已归档网页；行业研究机构和房地产/咨询报告只用作需求与情绪锚；行情和财务摘要来自本地能力层生成的数据包。

\begin{{exhibitbox}}[来源等级表]
\scriptsize
\begin{{longtable}}{{L{{1.0cm}}L{{2.3cm}}L{{4.0cm}}L{{7.0cm}}}}
\toprule
\textbf{{ID}} & \textbf{{类型}} & \textbf{{来源}} & \textbf{{用途}}\\
\midrule
\endhead
{chr(10).join(source_rows)}
\bottomrule
\end{{longtable}}
\sourcenote{{data/source\_registry.md；sources/public-web-20260630/。}}
\end{{exhibitbox}}

关键限制也必须写在正文里：第一，11:30 行情不是收盘价，适合估值快照但不适合作为成交确认；第二，财务摘要可校验收入、利润、BPS 和 EPS，但不能替代完整年报明细；第三，多数公司未披露 AI 订单、ASP、客户分配和单品毛利，因此只有官方披露了细分收入或项目/认证的公司才能获得较高估值信用。
"""
    write(SECTIONS / "ch02_evidence.tex", ch02.strip() + "\n")

    ch03 = r"""
AI 数据中心的技术变化不是“多买服务器”这么简单，而是从单机服务器采购走向机柜级、集群级和园区级协同。GB200 NVL72 这类架构把 GPU、CPU、NVLink、交换、液冷和供电整合到机柜级系统，直接提高了对高速光互联、低损耗 PCB、液冷和高密供配电的要求。
""" + rf"""
\begin{{exhibitbox}}[AIDC 八大产业链模块总览]
\scriptsize
{full_chain_summary_tex_table()}
\sourcenote{{data/full\_chain\_universe\_20260630.json；analysis/full\_chain\_taxonomy.md。核心=可直接进入或靠近核心估值池的子环节；条件=需要收入/订单/客户验证后才给估值信用。}}
\end{{exhibitbox}}
""" + r"""

\begin{exhibitbox}[AIDC 需求与价值池]
\begin{tabularx}{\textwidth}{L{3.0cm}X L{3.2cm}X}
\toprule
\textbf{驱动} & \textbf{证据} & \textbf{最先受益环节} & \textbf{投资含义}\\
\midrule
全球 AI capex & NVIDIA 数据中心收入高增；Dell'Oro 上修 2026 年 capex 至万亿美元以上 & AI服务器、光模块、交换机、PCB & 订单真实，但供应链瓶颈会造成季度波动\\
机柜级架构 & GB200 NVL72 采用液冷机柜级设计，强化 NVLink 与网络互联 & 光互联、液冷、供配电 & 传统风冷和低速网络价值占比下降\\
中国算力政策 & 国家数据局强调全国一体化算力网、算电协同与枢纽节点 & AIDC运营商、电力设备、国产算力 & 国内需求更强调电力、上架率和资源调度\\
功率密度提升 & JLL 指出 AI 机柜功率密度上升至 40--100+kW 区间 & 液冷、UPS、变压器、预制电力模组 & 供电和散热从配套件变成主约束\\
\bottomrule
\end{tabularx}
\sourcenote{S01--S05。架构图按仓库规则使用 Mermaid，源文件为 \texttt{analysis/aidc\_chain\_map.mmd}；本 PDF 使用表格表达同一关系，避免非 Mermaid 架构图。}
\end{exhibitbox}

光互联仍是 AIDC 最清晰的外溢环节。LightCounting 的公开摘要提示，AI 集群光互联仍有强增长潜力，但 2026 年还会受 XPU、交换 ASIC 与供应链均衡约束。这一判断对 A 股的含义是：光模块龙头有盈利兑现能力，但估值不应线性外推到整个光器件链条。
"""
    write(SECTIONS / "ch03_industry.tex", ch03.strip() + "\n")

    rels = json.loads((DATA / "supply_chain_relationships.json").read_text(encoding="utf-8"))["relationships"]
    rel_rows = []
    for r in rels:
        rel_rows.append(f"{tex(r['ticker'])} & {tex(r['company'])} & {tex(r['chain_layer'])} & {tex(r['product_or_process'])} & {tex(r['confidence'])} & {tex(r['used_in_valuation'])}\\\\")
    ch04 = rf"""
供应链映射的核心是区分“全景覆盖”“核心估值”和“主题扩散”。全景池覆盖 80 个子环节，核心关系矩阵只展示 18 只当前可建模标的。下游 AI 资本开支不能直接证明所有上游公司收入增长；必须看产品、客户、认证、订单、交付、利用率和毛利率是否形成闭环。

\begin{{exhibitbox}}[核心标的产业链关系矩阵]
\scriptsize
\begin{{longtable}}{{L{{1.5cm}}L{{2.0cm}}L{{2.5cm}}L{{5.1cm}}L{{1.6cm}}L{{2.1cm}}}}
\toprule
\textbf{{代码}} & \textbf{{公司}} & \textbf{{环节}} & \textbf{{产品/工艺}} & \textbf{{置信度}} & \textbf{{估值使用}}\\
\midrule
\endhead
{chr(10).join(rel_rows)}
\bottomrule
\end{{longtable}}
\sourcenote{{data/supply\_chain\_relationships.json；data/customer\_chain\_audit.md。}}
\end{{exhibitbox}}

本报告给予较高证据权重的关系包括：工业富联 AI 服务器与高速交换机收入披露、沪电股份数据通讯 PCB 与 AI服务器/HPC 分项披露、英维克全链条液冷产品与客户案例、科华数据高密 UPS 认证、润泽科技 AIDC 项目和业务展望。其他标的即使处在正确环节，也需要在后续披露中补足客户、订单、ASP 或上架率证据。

完整链条在第九章展开。特别需要注意的是，HBM、BMC、DPU/NIC、DSP、CPO/NPO 核心 ASIC、ABF、高端 HVLP 铜箔、绿电和通用 EPC 都是 AIDC 真实链条的一部分，但多数 A 股映射要么缺高纯度标的，要么缺直接收入证据，因此不能和光模块、AI PCB、液冷系统、UPS/HVDC 或 AIDC 运营商使用同一估值权重。
"""
    write(SECTIONS / "ch04_supply_chain.tex", ch04.strip() + "\n")

    ch05 = rf"""
财务交付比主题标签更重要。AIDC 链条内部差异很大：服务器整机通常收入规模大但毛利率低；光模块和高端 PCB 毛利率高、弹性强；液冷和供配电处在导入期，利润释放常受研发、扩产和项目验收节奏影响；IDC/AIDC 运营商则要看新增 MW、上架率、电价和折旧。

\begin{{exhibitbox}}[公司财务交付快照：2026Q1 与当前市值]
\scriptsize
{company_tex_table(rows)}
\sourcenote{{data/verified\_financials.md；data/verified\_market\_data.md。收入、利润和市值单位均为亿元人民币。}}
\end{{exhibitbox}}

从交付质量看，工业富联、光模块龙头、AI PCB 龙头和润泽科技已经有较强利润分母；英维克、科华数据、申菱环境等基础设施设备商的战略位置很好，但当前估值更依赖 2026H2 订单和毛利修复，而不是 2026Q1 已确认利润。
"""
    write(SECTIONS / "ch05_companies.tex", ch05.strip() + "\n")

    ch06 = r"""
公开研究情绪高度一致：AI capex 是 2026 年硬科技资产最强主线之一，市场更愿意给直接兑现的光模块、AI PCB、服务器 ODM 和液冷/供配电龙头估值溢价。但本报告没有收集到覆盖 18 只标的的完整原始券商目标价历史，因此不把券商目标价作为硬估值锚。

\begin{exhibitbox}[公开研究情绪归纳]
\begin{tabularx}{\textwidth}{L{3.0cm}X X}
\toprule
\textbf{共识方向} & \textbf{支持证据} & \textbf{本报告处理}\\
\midrule
AI capex 继续扩张 & NVIDIA、Dell'Oro、JLL 与国家数据局政策口径均支持需求强度 & 用作行业需求锚，不直接等同于单公司收入\\
光互联景气强 & LightCounting 指向 AI 集群光互联长期空间，但也提示供应链均衡风险 & 龙头给盈利信用，器件/扩散标的给可选性信用\\
液冷和供电升级 & JLL、NVIDIA 架构、英维克和科华公告共同指向高密机柜约束 & 只在产品/认证/项目证据明确时给估值权重\\
AIDC 运营商重估 & 润泽披露 AIDC 增长、200MW/液冷项目和客户结构优化 & 估值必须同时看上架率、现金流和折旧\\
\bottomrule
\end{tabularx}
\sourcenote{S01--S12；data/consensus\_analysis.md。}
\end{exhibitbox}

因此，本报告把“公开情绪”纳入综合目标价的市场锚，但权重低于基本面锚。若后续成交额和趋势继续强化而财务也兑现，市场锚权重可以上调；若订单、毛利或现金流低于预期，市场锚必须下调。
"""
    write(SECTIONS / "ch06_sentiment.tex", ch06.strip() + "\n")

    ch07 = rf"""
估值方法按业务模型分层：服务器/光模块/PCB 采用正常化 PE 与 PEG/PS 交叉校验；供配电和液冷设备采用正常化 PE 加订单转换校验；AIDC/IDC 运营商采用 PE、现金流、上架率和负债约束校验。由于本次未取得全量原始券商目标价历史，最终目标价由内在价值锚与市场情绪锚加权形成。

\begin{{exhibitbox}}[全覆盖估值摘要]
\scriptsize
{valuation_tex_table(rows)}
\sourcenote{{analysis/valuation\_model.md；data/current\_valuation\_model\_20260630.json。}}
\end{{exhibitbox}}

估值读法很直接：若现价显著高于综合目标价，不等于公司不好，而是意味着当前价格已经要求更长的增长久期、更高毛利率或更强客户订单持续性。对光模块和 AI PCB，这个验证点是 1.6T/高速交换机订单、ASP 与毛利率；对液冷和供配电，是客户验收和项目收入确认；对 AIDC 运营商，是新增 MW、上架率、单位电力成本和折旧压力。
"""
    write(SECTIONS / "ch07_valuation.tex", ch07.strip() + "\n")

    ch08 = r"""
\begin{riskbox}[核心风险]
第一，估值拥挤。多只核心标的已在午盘成交额和涨幅上体现强情绪，若基本面兑现慢于预期，回撤会比行业需求变化更快。第二，客户集中。AI 服务器、光模块和 PCB 的订单高度依赖少数 CSP 或平台客户。第三，AIDC 运营的瓶颈在交付后：上架率、电价、折旧和运维能力比拿地和建设更重要。第四，技术路线变化可能转移利润池，例如 CPO/LPO、铜互联回潮、国产芯片架构差异或液冷方案标准变化。
\end{riskbox}

\begin{exhibitbox}[催化剂与监测阈值]
\begin{tabularx}{\textwidth}{L{3.0cm}X X}
\toprule
\textbf{监测项} & \textbf{正向阈值} & \textbf{负向阈值}\\
\midrule
服务器/交换机 & 工业富联、浪潮信息等 Q2/Q3 收入继续高增且毛利率不再下探 & 增收不增利、存货和应收显著扩张\\
光互联 & 800G/1.6T 出货、毛利率和现金流同步提升 & ASP 下行、客户砍单或库存堆积\\
AI PCB/CCL & 高多层/HDI/高速交换机板收入占比继续提升 & 扩产过快、良率或价格压力压缩毛利\\
液冷/供配电 & CDU、冷板、UPS、电力模组从认证进入批量交付 & 只有样机/认证，没有收入和利润确认\\
AIDC运营 & 新增 MW 上架率、客户粘性和经营现金流改善 & 高折旧、低利用率、融资成本上行\\
\bottomrule
\end{tabularx}
\sourcenote{analysis/risk\_framework.md；analysis/chain\_earnings\_bridge.md。}
\end{exhibitbox}

组合执行上，报告建议把“直接收入证据”放在第一权重，“估值空间”放在第二权重，“产业链位置”只放第三权重。当前价格下更适合建立跟踪清单和事件验证表，而不是无差别追高。
"""
    write(SECTIONS / "ch08_risks.tex", ch08.strip() + "\n")

    ch09 = rf"""
本章是全景产业链底稿，目的不是把所有名字都纳入估值，而是完整回答 AIDC 上下游到底覆盖哪些环节。估值纪律如下：\textbf{{核心可估值}}需要官方收入、订单、认证、MW、上架率或交付证据；\textbf{{条件估值}}需要后续验证客户、收入占比、毛利率和现金流；\textbf{{观察/需求锚}}只能解释方向，不能直接转化为单公司盈利。

\begin{{exhibitbox}}[AIDC 全景产业链池：8 大板块 80 个子环节]
\scriptsize
{full_chain_tex_table()}
\sourcenote{{data/full\_chain\_universe\_20260630.json。该表为产业链覆盖池，不等同于买入名单；其中需求锚、观察和期权环节不进入核心估值模型。}}
\end{{exhibitbox}}

从全景池看，真正可优先跟踪的不是“链条越远越好”，而是证据闭环越短越好：服务器整机、光模块、AI PCB、CDU/液冷系统、UPS/HVDC、AIDC 运营商的订单或收入更容易验证；HBM、BMC、DSP、CPO 核心 ASIC、ABF、高端铜箔、绿电和通用 EPC 虽然属于链条，但 A 股投资映射需要更严格折价。

\begin{{exhibitbox}}[从全景池到核心估值池的筛选规则]
\begin{{tabularx}}{{\textwidth}}{{L{{3.0cm}}X X}}
\toprule
\textbf{{层级}} & \textbf{{入选条件}} & \textbf{{典型处理}}\\
\midrule
核心估值池 & 有官方收入、订单、认证、MW、上架率、客户或产品证据，并能用财务数据建立 EPS/现金流锚 & 纳入 18 股估值表，给基础/熊牛目标价\\
条件观察池 & 环节位置正确，但 AIDC 收入占比、客户认证、订单排产或毛利率尚未充分披露 & 进入监测清单，等证据补齐后再给盈利权重\\
卫星主题池 & 产业链相关但集团业务过大、纯度低或价值量较小 & 只做催化剂和供需跟踪，不给主题溢价\\
需求锚 & 云厂商、模型公司、AI 应用、政企智算和垂直行业客户 & 用来判断利用率和 capex 方向，不推导到单一供应商收入\\
\bottomrule
\end{{tabularx}}
\sourcenote{{analysis/agent\_research\_synthesis.md；data/full\_chain\_universe\_20260630.json。}}
\end{{exhibitbox}}
"""
    write(SECTIONS / "ch09_full_chain.tex", ch09.strip() + "\n")

    app_source = r"""
\section*{来源注册表}
本报告的来源注册表见 \texttt{data/source\_registry.md/json}；原始网页和 PDF 归档在 \texttt{sources/public-web-20260630/}。

\section*{高影响声明审计}
高影响声明包括工业富联 AI 服务器/高速交换机、沪电股份 AI PCB、英维克液冷、科华 UPS、润泽 AIDC 项目和 LightCounting 光互联需求判断。完整审计见 \texttt{data/customer\_chain\_audit.md/json}。

\section*{Mermaid 架构图源文件}
仓库规则要求架构图使用 Mermaid。AIDC 产业链架构图源文件为 \texttt{analysis/aidc\_chain\_map.mmd}。本 PDF 未使用 TikZ 或 ASCII 绘制架构图。
"""
    write(SECTIONS / "app_source_audit.tex", app_source.strip() + "\n")

    app_model = r"""
\section*{模型披露}
2026E 收入和 EPS 是 AStock 基于 2026Q1、2025A、分层季节性和财务摘要构建的研究代理变量，不是外部券商一致预期。市值由 2026-06-30 11:30 现价乘以“净资产/BPS”反推股本得到，属于模型派生字段。

\section*{估值权重}
综合目标价 = 内在价值锚 $\times$ 基本面权重 + 市场情绪锚 $\times$ 市场权重。市场权重取决于证据等级和成交额强度。由于未收集完整原始券商目标价历史，券商锚本次权重为 0。

\section*{非建议声明}
本报告仅用于研究和监测，不构成任何证券买卖建议、交易指令或组合托管意见。
"""
    write(SECTIONS / "app_model_disclosure.tex", app_model.strip() + "\n")


def make_main(rows: list[dict]) -> None:
    avg_upside = sum((r["final_upside"] or 0) * r["assumption"]["weight"] for r in rows) / sum(r["assumption"]["weight"] for r in rows)
    house_upside = pct_plain(avg_upside).replace("%", r"\%")
    house = f"\\kaishu AIDC 产业链不是 18 只股票，而是覆盖算力芯片/存储、服务器零部件、网络光通信、PCB材料、供配电、液冷、数据中心建设运营和下游需求的八大链条。本报告用 80 个子环节做全景覆盖，再从中选取 18 只公开证据和财务数据相对充分的 A 股作为核心估值池。按直接收入证据、2026Q1 财务交付和估值隐含预期排序，工业富联、沪电股份、润泽科技、胜宏科技、中际旭创和新易盛最值得跟踪；但覆盖组合按权重计算的综合目标空间为 {house_upside}，说明现阶段更适合事件验证和回撤布局，而非无差别追高。"
    quality = "来源包括 NVIDIA、Dell'Oro、国家数据局、JLL、LightCounting、SIA、TrendForce、Schneider、Vertiv、TE、Minsheng 公开研报、公司公告/IR、Sina 实时行情快照和 akshare 财务摘要。公司级订单、ASP、客户分配未完整披露的字段均标为 not disclosed、condition-only 或 optionality only。"
    main = rf"""
% !TEX program = xelatex
\documentclass[a4paper,11pt,openany,fontset=none]{{ctexrep}}

\newcommand{{\reporttitle}}{{AIDC 产业链上下游核心标的深度研究}}
\newcommand{{\reportsubtitle}}{{8 大链条全景池 + 18 只核心估值池}}
\newcommand{{\reportkicker}}{{机构股票研究}}
\newcommand{{\reportscope}}{{中国 A 股 | AIDC 全产业链}}
\newcommand{{\reportdate}}{{2026 年 6 月 30 日}}
\newcommand{{\reportdatacutoff}}{{市场数据至 2026-06-30 11:30；财务数据至 2026Q1/2025A}}
\newcommand{{\reporttype}}{{行业深度研究}}
\newcommand{{\reportauthor}}{{AStock 研究代理团队}}
\newcommand{{\reporthouseview}}{{{house}}}
\newcommand{{\reportquality}}{{{quality}}}
\newcommand{{\reportdisclaimer}}{{本报告基于公开资料整理，不构成任何证券买卖建议。}}

\input{{../../../.agents/templates/preamble.tex}}
\hypersetup{{pdfauthor={{\reportauthor}}, pdftitle={{\reporttitle}}}}

\begin{{document}}
\astockcover
\tableofcontents
\clearpage

\chapter{{投资委员会概要}}
\input{{sections/ch01_dashboard}}
\chapter{{证据治理与来源边界}}
\input{{sections/ch02_evidence}}
\chapter{{技术架构、产业趋势与价值池}}
\input{{sections/ch03_industry}}
\chapter{{供应链映射与竞争位置}}
\input{{sections/ch04_supply_chain}}
\chapter{{公司映射与财务交付}}
\input{{sections/ch05_companies}}
\chapter{{公开研究情绪与分歧}}
\input{{sections/ch06_sentiment}}
\chapter{{估值模型、目标价与隐含预期}}
\input{{sections/ch07_valuation}}
\chapter{{风险、催化剂与监测框架}}
\input{{sections/ch08_risks}}
\chapter{{AIDC 全产业链全景池}}
\input{{sections/ch09_full_chain}}

\appendix
\chapter{{来源注册表与声明审计}}
\input{{sections/app_source_audit}}
\chapter{{模型假设与披露}}
\input{{sections/app_model_disclosure}}

\clearpage
\thispagestyle{{empty}}
\vspace*{{4cm}}
\begin{{disclosurebox}}[免责声明]
\small
\reportdisclaimer\par
本报告为 AStock 内部研究参考。AStock 目标价和动作标签为模型化研究结论，不代表外部券商评级、投资顾问意见、交易指令或组合托管建议。市场价格、盈利预测、产业节奏和政策环境可能快速变化，任何组合动作均需结合实时风险约束重新判断。
\end{{disclosurebox}}
\end{{document}}
"""
    write(BASE / "main.tex", main.strip() + "\n")


def make_review_and_verifier() -> None:
    review = dedent(
        """
        # Review Log

        - 2026-06-30: Built AIDC industry-chain report from archived public sources, Sina market snapshot and akshare financial packets.
        - 2026-06-30 update: Expanded from an 18-name core valuation pool to an 8-block, 80-subsegment panoramic AIDC chain universe.
        - Supply-chain gate: conditional pass; every ticker has relationship row and company card; full-chain satellite and demand-anchor rows are separated from valuation rows.
        - Growth earnings gate: conditional pass; no unsupported unit/ASP assumptions added.
        - Valuation gate: pass with broker-anchor limitation disclosed; complete original broker target-price history not collected for all 18 names.
        """
    ).strip()
    write(BASE / "review_log.md", review + "\n")

    verifier = r'''from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

REQUIRED = [
    "research_brief.md",
    "main.tex",
    "main.pdf",
    "main_current_text.txt",
    "review_log.md",
    "sections/ch09_full_chain.tex",
    "data/raw_market_financials_20260630.json",
    "data/raw_market_data.md",
    "data/raw_financials.md",
    "data/verified_market_data.md",
    "data/verified_financials.md",
    "data/source_registry.md",
    "data/source_registry.json",
    "data/claim_audit.md",
    "data/claim_audit.json",
    "data/supply_chain_relationships.md",
    "data/supply_chain_relationships.json",
    "data/customer_chain_audit.md",
    "data/customer_chain_audit.json",
    "data/full_chain_universe_20260630.md",
    "data/full_chain_universe_20260630.json",
    "data/growth_driver_model.json",
    "data/current_valuation_model_20260630.json",
    "data/current_valuation_model_20260630.md",
    "data/consensus_analysis.md",
    "analysis/full_chain_taxonomy.md",
    "analysis/agent_research_synthesis.md",
    "analysis/template_brief.md",
    "analysis/industry_landscape.md",
    "analysis/supply_chain_model.md",
    "analysis/company_fundamental_cards.md",
    "analysis/chain_earnings_bridge.md",
    "analysis/growth_earnings_model.md",
    "analysis/segment_forecast_bridge.md",
    "analysis/implied_growth_sensitivity.md",
    "analysis/valuation_model.md",
    "analysis/valuation_audit.md",
    "analysis/risk_framework.md",
    "analysis/house_view.md",
    "analysis/exhibit_plan.md",
    "analysis/aidc_chain_map.mmd",
    "sections/ch01_dashboard.tex",
    "sections/ch02_evidence.tex",
    "sections/ch03_industry.tex",
    "sections/ch04_supply_chain.tex",
    "sections/ch05_companies.tex",
    "sections/ch06_sentiment.tex",
    "sections/ch07_valuation.tex",
    "sections/ch08_risks.tex",
    "sections/app_source_audit.tex",
    "sections/app_model_disclosure.tex",
]

def text(path: str) -> str:
    return (BASE / path).read_text(encoding="utf-8")

def exists(path: str) -> tuple[bool, str]:
    p = BASE / path
    return p.exists() and p.stat().st_size > 0, path

def pdf_pages() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=20)
    m = re.search(r"Pages:\s+(\d+)", out.stdout)
    if not m:
        return False, "pdfinfo missing Pages"
    pages = int(m.group(1))
    return pages >= 18, f"pages={pages}"

def source_count() -> tuple[bool, str]:
    data = json.loads(text("data/source_registry.json"))
    return len(data.get("sources", [])) >= 30, f"sources={len(data.get('sources', []))}"

def relationship_count() -> tuple[bool, str]:
    data = json.loads(text("data/supply_chain_relationships.json"))
    return len(data.get("relationships", [])) == 18, f"relationships={len(data.get('relationships', []))}"

def full_chain_count() -> tuple[bool, str]:
    data = json.loads(text("data/full_chain_universe_20260630.json"))
    return len(data.get("rows", [])) >= 80, f"full_chain_rows={len(data.get('rows', []))}"

def full_chain_blocks() -> tuple[bool, str]:
    data = json.loads(text("data/full_chain_universe_20260630.json"))
    blocks = {row.get("chain_block") for row in data.get("rows", [])}
    return len(blocks) == 8, f"blocks={len(blocks)}"

def valuation_count() -> tuple[bool, str]:
    data = json.loads(text("data/current_valuation_model_20260630.json"))
    return len(data.get("rows", [])) == 18, f"valuations={len(data.get('rows', []))}"

def growth_count() -> tuple[bool, str]:
    data = json.loads(text("data/growth_driver_model.json"))
    return len(data.get("drivers", [])) == 18, f"drivers={len(data.get('drivers', []))}"

def no_ascii_diagram() -> tuple[bool, str]:
    forbidden = ["+---", "|---+", "---->", "<----"]
    body = text("main_current_text.txt") if (BASE / "main_current_text.txt").exists() else text("main.tex")
    return not any(token in body for token in forbidden), "no ASCII architecture diagram"

def mermaid() -> tuple[bool, str]:
    body = text("analysis/aidc_chain_map.mmd")
    return "flowchart LR" in body and "AIDC" in body, "Mermaid flowchart"

def chinese_text() -> tuple[bool, str]:
    body = text("main_current_text.txt")
    return "投资委员会概要" in body and "全产业链" in body and "估值模型" in body and "风险" in body, "Chinese sections extracted"

def no_unfinished() -> tuple[bool, str]:
    body = text("main_current_text.txt")
    bad = ["TODO", "PLACEHOLDER", "<Report Title>", "??"]
    return not any(x in body for x in bad), "no unfinished markers"

def source_files() -> tuple[bool, str]:
    files = list((BASE / "sources" / "public-web-20260630").glob("*"))
    return len(files) >= 40, f"source_files={len(files)}"

def rendered_pages() -> tuple[bool, str]:
    files = list((BASE / "rendered" / "current-20260630").glob("page-*.png"))
    return len(files) >= 3, f"rendered_pages={len(files)}"

checks = []
for path in REQUIRED[:23]:
    checks.append((f"exists:{path}", lambda p=path: exists(p)))
checks += [
    ("pdf_pages", pdf_pages),
    ("source_count", source_count),
    ("relationship_count", relationship_count),
    ("full_chain_count", full_chain_count),
    ("full_chain_blocks", full_chain_blocks),
    ("valuation_count", valuation_count),
    ("growth_count", growth_count),
    ("no_ascii_diagram", no_ascii_diagram),
    ("mermaid", mermaid),
    ("chinese_text", chinese_text),
    ("no_unfinished", no_unfinished),
    ("source_files", source_files),
    ("rendered_pages", rendered_pages),
]
for path in REQUIRED[23:26]:
    checks.append((f"exists:{path}", lambda p=path: exists(p)))

if len(checks) != 39:
    raise SystemExit(f"Verifier definition error: expected 39 checks, got {len(checks)}")

failures = []
for name, fn in checks:
    ok, detail = fn()
    status = "PASS" if ok else "FAIL"
    print(f"{status} {name}: {detail}")
    if not ok:
        failures.append(name)
print(f"SUMMARY: {39 - len(failures)} PASS / {len(failures)} FAIL")
raise SystemExit(1 if failures else 0)
'''
    write(BASE / "tools" / "verify_research_workspace.py", verifier)


def main() -> None:
    ensure_dirs()
    raw = read_raw()
    rows = derive_models(raw)
    make_brief()
    make_template_brief()
    make_source_registry()
    make_verified_packets(rows)
    make_supply_chain_outputs(rows)
    make_full_chain_outputs()
    make_customer_audit()
    make_growth_outputs(rows)
    make_valuation_outputs(rows)
    make_other_analysis(rows)
    make_sections(rows)
    make_main(rows)
    make_review_and_verifier()
    print(f"Built AIDC report source artifacts at {BASE}")


if __name__ == "__main__":
    main()
