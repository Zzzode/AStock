# 来源登记

机器可读版本：`data/source_registry.json`。本批登记券商/市场来源和 Physical AI 一手来源；后者包括年报、公司IR记录及公司新闻页。公司新闻可确认产品或合作发布，但不自动成为客户、收入或利润证据。

| ID | 层级 | 用途 | 估值后果 | 关键限制 |
|---|---|---|---|---|
| BRK-PDF-PHILLIP-20260105 | original_broker_pdf | 历史目标价和预测 | context only | 2025E基准、过时 |
| BRK-PDF-KY-20260308 | original_broker_pdf | 预测交叉核对 | cross-check only | 无目标价 |
| BRK-PDF-DW-20260310 | original_broker_pdf | 预测交叉核对 | cross-check only | 无目标价 |
| BRK-PDF-BOC-20260331 | original_broker_pdf | 预测交叉核对 | cross-check only | 无目标价 |
| BRK-EM-SNAPSHOT-20260723 | auditable_consensus_snapshot | 机构/日期/评级/NP/EPS | context only | 无营收、目标、方法、原文 |
| BRK-EM-REPORTS-20260723 | broker_abstract | 标题、日期、摘要 | context only | 不是原文 |
| BRK-SINA-SW-20260625 | media_repost | 申万观点线索 | context only | 转载非原文 |
| PROBE-THS-20260723 | not_found | 失败探测 | blocks target validation | 无个股研报入口 |
| PAI-AICUBE-20251105 | issuer corporate news | AI Cube产品与技术架构 | technology option only | 未披露客户、订单、SOP、收入、ASP、毛利 |
| PAI-ROBOT-IR-20260310 | issuer IR record | 机器人合作、域控定点与2026量产计划 | 2026里程碑期权，基础EPS为零 | 客户、金额、数量、SOP、收入、利润与现金未披露；计划不等于完成 |
| PAI-CHUANXING-20250903 | issuer corporate news | 川行致远S6产品与适用场景 | product/scenario option only | 未披露客户、部署、收入、商业模式、ASP、毛利 |
| PAI-CHUANXING-IR-20250926 | issuer IR record | 低速无人车取得相关客户订单 | conditional commercial option | 客户、订单额、车辆数、交付、验收、收入与回款未披露 |
| PAI-NVIDIA-20260423 | issuer corporate news | Thor方案POC和面向量产开发 | technology catalyst only | 无车型项目、SOP、交付、收入或毛利 |
| PAI-DEEPROUTE-20260427 | issuer corporate news | 与元戎启行的海外L4 Robotaxi合作 | ecosystem option only | 合作不是采购订单；终端客户、项目、交付和经济学未披露 |
