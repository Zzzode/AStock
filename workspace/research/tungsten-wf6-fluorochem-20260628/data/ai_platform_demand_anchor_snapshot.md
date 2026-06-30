# AI平台/HBM/网络需求锚

门禁状态：有条件通过。本包把NVIDIA、SK hynix HBM、Google TPU、AWS Trainium、Intel Gaudi、华为昇腾和Spectrum-X网络放进同一张平台需求图，用于解释AI叙事为何会传导到晶圆制造、HBM、先进封装、CVD/刻蚀/清洗气体和前道材料。它不是客户订单表；没有客户侧供应商名录、认证阶段、采购合同、平均售价和产品毛利前，不能把平台需求直接折成A股上游公司每股收益。

| 平台组 | 厂商 | 平台 | 公开证据 | 材料链传导 | 跟踪项 | 语料缺口 | 估值用途 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AI GPU/HBM | NVIDIA | Blackwell / Blackwell Ultra | 官方Blackwell资料和开发者资料显示，Blackwell系统围绕AI factory、NVLink域和高容量HBM3E内存扩展。 | 先进逻辑晶圆、CoWoS/先进封装、HBM、CVD/刻蚀/清洗特气和前道薄膜材料需求锚。 | GPU出货、HBM供应、先进封装产能、CVD/etch装机和晶圆厂资本开支。 | 未取得NVIDIA客户侧材料供应商名录或A股供应商采购订单。 | 需求锚和市场叙事强度；不进入单公司每股收益。 |
| HBM与AI存储 | SK hynix | HBM3E / HBM4 | SK hynix公开资料把HBM3E/HBM4定位为AI和HPC先进内存产品，说明AI加速器对高带宽内存的依赖。 | DRAM/HBM晶圆、TSV/堆叠封装、清洗刻蚀气体、前驱体和高纯材料需求锚。 | HBM代际切换、认证、产能扩张、良率和封装瓶颈。 | 未取得SK hynix客户侧电子特气/钨材采购清单。 | 解释HBM/3D存储需求锚；不证明国内供应商订单。 |
| 云端ASIC | Google Cloud | Cloud TPU v6e / Trillium | Google Cloud文档披露TPU是用于加速机器学习工作负载的定制ASIC，v6e/Trillium面向训练、微调和服务。 | 定制ASIC先进制程、HBM/高速存储、先进封装和前道材料需求锚。 | TPU代际、Pod规模、云厂商资本开支和ASIC代工投片。 | 未取得Google TPU供应链中A股材料供应商认证或采购文件。 | 作为云ASIC需求锚；不进入上游材料公司收入桥。 |
| 云端ASIC与HBM | AWS | Trainium / Trainium2 | AWS公开资料披露Trainium系列为AI训练/推理芯片，Trainium2实例使用HBM并强调内存带宽。 | 云厂商自研ASIC、HBM、先进封装、前道制造和网络互连材料需求锚。 | Trn实例放量、HBM容量、云资本开支和供应链认证。 | 未取得AWS Trainium供应链中A股电子材料订单。 | 作为云ASIC和HBM需求锚；不进入单公司每股收益。 |
| AI加速器与HBM | Intel | Gaudi 3 | Intel官方资料披露Gaudi 3 AI加速器使用HBM并强调大模型训练/推理性能。 | AI加速器晶圆制造、HBM、封装和高速互连材料需求锚。 | Gaudi云端部署、HBM供应、以太网互连和晶圆代工节奏。 | 未取得Intel Gaudi供应链映射到A股电子材料供应商的订单证据。 | 作为非NVIDIA AI加速器需求锚；不进入A股材料公司目标价。 |
| 国产AI算力 | Huawei | Ascend / Atlas 900 A3 SuperPoD | 华为公开演讲资料披露Atlas 900 A3 SuperPoD与Ascend 910C系统级算力，用于国产AI基础设施观察。 | 国产AI芯片、国产晶圆/封装、国产材料替代和供应链安全需求锚。 | 国产AI集群建设、昇腾代际、国产晶圆制造和材料国产化验证。 | 未取得华为/昇腾客户侧材料采购、电子特气供应商或A股材料订单文件。 | 国产算力需求锚；只提升观察优先级，不给订单信用。 |
| AI networking/optical | NVIDIA | Spectrum-X Ethernet / Photonics | NVIDIA公开资料把Spectrum-X定位为面向AI factory的以太网平台，可扩展到大规模GPU集群。 | 高速交换芯片、硅光/光模块、先进封装和数据中心互连需求锚，间接影响前道材料和设备需求。 | AI网络交换机、光模块、硅光、数据中心互连和GPU集群规模。 | 未取得网络/光模块需求向WF6或A股电子特气订单的直接映射。 | 作为AI集群网络需求锚；不能替代半导体材料订单。 |

- 覆盖平台：7
- 使用边界：平台链只解释AI/HBM/云ASIC/国产算力/网络需求锚，不证明A股上游订单、平均售价、收入确认或单品毛利。
