# Extended Core Candidate Valuation Synthesis

This file replaces the prior generic 'wait for more evidence' text with ticker-level valuation or downgrade decisions.

- Target-model ready: 38
- Explicit broker-target models: 13
- AStock house fair-value models without explicit Street target: 24
- PS/SOTP target models for loss-making names: 1
- Watchlist-only: 3

## 000063 中兴通讯

- Status: target_model_ready; action: core focus; rating label: 核心关注.
- Denominator: price 36.38, shares 48.05亿股, market cap 1748.2亿元.
- 2026E: revenue 1666.9亿元, net profit 92.6亿元, EPS 1.94.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: 60.00.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/000063-中兴通讯/AP202509011737603598-群益证券-运营商业务承压-AI服务器相关业务快速增长.pdf.

## 601728 中国电信

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 5.43, shares 929.82亿股, market cap 5048.9亿元.
- 2026E: revenue 5618.8亿元, net profit 390.5亿元, EPS 0.42.
- Method: PB/ROE plus EV/EBITDA check; PE is secondary; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=None, eps=0.42, reason=missing net profit or EPS; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 新增 MW/机架、上架率、算力收入和 capex/现金流验证。
- Invalidation: 若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/601728-中国电信/02-AP202509031738356169-东莞证券-2025年半年报点评-上半年稳健增收-算力支持能力持续增强.txt.

## 600941 中国移动

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 87.48, shares 217.23亿股, market cap 19003.7亿元.
- 2026E: revenue 11257.6亿元, net profit 1562.3亿元, EPS 7.24.
- Method: PB/ROE plus EV/EBITDA check; PE is secondary; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 新增 MW/机架、上架率、算力收入和 capex/现金流验证。
- Invalidation: 若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/600941-中国移动/AP202504141656394300-山西证券-重点布局5-5G-推理算力-AI投资-新业务领域开辟新业态.pdf.

## 600050 中国联通

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 4.07, shares 698.32亿股, market cap 2842.2亿元.
- 2026E: revenue 4018.1亿元, net profit 235.3亿元, EPS 0.34.
- Method: PB/ROE plus EV/EBITDA check; PE is secondary; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=105.4, eps=0.337, reason=EPS/share mismatch expected 0.1509 vs EPS 0.3370; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 新增 MW/机架、上架率、算力收入和 capex/现金流验证。
- Invalidation: 若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/600050-中国联通/01-AP202603201820670142-国金证券-营收稳健增长-ai带动盈利质量优化.txt.

## 601179 中国西电

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 14.29, shares 58.08亿股, market cap 829.9亿元.
- 2026E: revenue 242.5亿元, net profit 22.9亿元, EPS 0.40.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_pdf; broker target: 7.90.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=8.85, eps=0.395, reason=EPS/share mismatch expected 0.1524 vs EPS 0.3950; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/601179-中国西电/AP202503141644357609-国金证券-一次设备老牌巨头-主网景气再腾飞.pdf.

## 002364 中恒电气

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 52.90, shares 5.70亿股, market cap 301.7亿元.
- 2026E: revenue 32.6亿元, net profit 3.7亿元, EPS 0.65.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002364-中恒电气/AP202505271679991867-西南证券-数据中心HVDC龙头-受益于AIDC需求增长.pdf.

## 300936 中英科技

- Status: watchlist_only_insufficient_model; action: insufficient evidence; rating label: 证据不足.
- Denominator: price 101.93, shares 0.75亿股, market cap 76.3亿元.
- 2026E: revenue 3.0亿元, net profit -0.0亿元, EPS -0.06.
- Method: PS/PB or milestone valuation watchlist; positive EPS denominator not valid; broker source quality: official_filing_no_broker_target; broker target: not disclosed.
- Forecast quality flags: financial_proxy_profit_eps_used.
- Decision: 当前收入、股本和市值已补齐，但 2026E EPS 代理为负或不可用；PE/PEG 不适用，需等待盈利路径或改用明示 PS/PB/SOTP 证据。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/source-exhausted-official-filings-20260701/300936-中英科技/annual-2025年年度报告.txt.

## 002922 伊戈尔

- Status: target_model_ready; action: market support watch; rating label: 市场支撑观察.
- Denominator: price 29.65, shares 4.28亿股, market cap 126.8亿元.
- 2026E: revenue 73.1亿元, net profit 4.9亿元, EPS 1.15.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_pdf; broker target: 45.80.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002922-伊戈尔/AP202512141800437415-东吴证券-新能源变压器龙头加速出海-布局AIDC打造第二增长曲线.pdf.

## 603912 佳力图

- Status: watchlist_only_insufficient_model; action: insufficient evidence; rating label: 证据不足.
- Denominator: price 7.70, shares 5.57亿股, market cap 42.9亿元.
- 2026E: revenue 7.1亿元, net profit -0.9亿元, EPS -0.17.
- Method: PS/PB or milestone valuation watchlist; positive EPS denominator not valid; broker source quality: official_filing_no_broker_target; broker target: not disclosed.
- Forecast quality flags: financial_proxy_profit_eps_used.
- Decision: 当前收入、股本和市值已补齐，但 2026E EPS 代理为负或不可用；PE/PEG 不适用，需等待盈利路径或改用明示 PS/PB/SOTP 证据。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/source-exhausted-official-filings-20260701/603912-佳力图/annual-603912-佳力图2025年年度报告.txt.

## 300249 依米康

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 14.82, shares 4.52亿股, market cap 66.9亿元.
- 2026E: revenue 14.5亿元, net profit 0.6亿元, EPS 0.13.
- Method: normalised PE/SOTP with data-center order validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/300249-依米康/AP202606091823393919-华鑫证券-公司事件点评报告-数据中心温控解决方案服务商-定增加码液冷促进产品升级.pdf.

## 603986 兆易创新

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 677.77, shares 7.08亿股, market cap 4797.3亿元.
- 2026E: revenue 85.1亿元, net profit 31.5亿元, EPS 4.45.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: 120.00.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=None, eps=4.45, reason=missing net profit or EPS; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/603986-兆易创新/AP202501141641912457-高盛-CEO电话会-2025年展望及边缘AI机会要点-买入.pdf.

## 002281 光迅科技

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 217.33, shares 8.10亿股, market cap 1761.0亿元.
- 2026E: revenue 150.1亿元, net profit 15.4亿元, EPS 1.90.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: 78.31.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=10.6, eps=1.9, reason=EPS/share mismatch expected 1.3082 vs EPS 1.9000; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002281-光迅科技/AP202512291810626232-国信证券-自研光芯片垂直布局-受益国内AI算力发展.pdf.

## 000530 冰山冷热

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 5.36, shares 8.59亿股, market cap 46.0亿元.
- 2026E: revenue 55.2亿元, net profit 2.1亿元, EPS 0.25.
- Method: normalised PE/SOTP with data-center order validation; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/000530-冰山冷热/01-AP202505141672798964-华安证券-冷热核心事业稳步发展-并购与新事业未来可期.txt.

## 603083 剑桥科技

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 209.37, shares 3.57亿股, market cap 747.0亿元.
- 2026E: revenue 79.0亿元, net profit 9.0亿元, EPS 2.52.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=6.74, eps=2.52, reason=EPS/share mismatch expected 1.8892 vs EPS 2.5200; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/603083-剑桥科技/AP202508221732325413-华鑫证券-公司事件点评报告-高速光模块放量贡献强劲利润-多地量产支撑AI旺盛需求.pdf.

## 300223 北京君正

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 259.56, shares 4.84亿股, market cap 1256.5亿元.
- 2026E: revenue 58.9亿元, net profit 6.6亿元, EPS 1.36.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/300223-北京君正/01-AP202512251807948565-中邮证券-计算-存储-感知-执行-多元化全面布局ai.txt.

## 000988 华工科技

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 153.95, shares 10.13亿股, market cap 1559.3亿元.
- 2026E: revenue 200.6亿元, net profit 15.5亿元, EPS 1.99.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: 46.20.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/000988-华工科技/AP202505211676548456-国金证券-国内光模块市场兴起-光电器件业务有望迎来突破.pdf.

## 603186 华正新材

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 199.99, shares 1.58亿股, market cap 316.2亿元.
- 2026E: revenue 53.1亿元, net profit 2.8亿元, EPS 1.77.
- Method: PE/PEG plus cycle/product-mix check; broker source quality: official_filing_no_broker_target; broker target: not disclosed.
- Forecast quality flags: financial_proxy_profit_eps_used.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/source-exhausted-official-filings-20260701/603186-华正新材/annual-浙江华正新材料股份有限公司2025年年度报告-修订版.txt.

## 688519 南亚新材

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 371.22, shares 2.35亿股, market cap 871.5亿元.
- 2026E: revenue 60.1亿元, net profit 4.9亿元, EPS 2.08.
- Method: PE/PEG plus cycle/product-mix check; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=0.8, eps=2.08, reason=EPS/share mismatch expected 0.3408 vs EPS 2.0800; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688519-南亚新材/AP202508011719656440-华金证券-高端高速产品获全球知名AI服务器认证-持续受益国产算力发展.pdf.

## 300990 同飞股份

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 100.10, shares 1.71亿股, market cap 170.7亿元.
- 2026E: revenue 43.6亿元, net profit 4.7亿元, EPS 2.76.
- Method: normalised PE/SOTP with data-center order validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=None, eps=2.76, reason=missing net profit or EPS; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/300990-同飞股份/AP202604301821823442-东莞证券-深度报告-储能与数据中心液冷双核驱动-全球化开启新篇章.pdf.

## 002913 奥士康

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 57.15, shares 3.26亿股, market cap 186.3亿元.
- 2026E: revenue 67.4亿元, net profit 6.9亿元, EPS 2.18.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/002913-奥士康/02-AP202508271735306248-中邮证券-高阶hdi持续放量.txt.

## 600845 宝信软件

- Status: house_target_model_ready; action: market support watch; rating label: 市场支撑观察.
- Denominator: price 18.25, shares 30.98亿股, market cap 565.3亿元.
- 2026E: revenue 155.3亿元, net profit 27.6亿元, EPS 1.03.
- Method: PB/ROE plus EV/EBITDA check; PE is secondary; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 新增 MW/机架、上架率、算力收入和 capex/现金流验证。
- Invalidation: 若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/600845-宝信软件/01-AP202504101654109806-国元证券-2024年年度报告点评-营收实现稳健增长-ai驱动转型升级.txt.

## 688256 寒武纪

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 1353.00, shares 4.22亿股, market cap 5708.5亿元.
- 2026E: revenue 108.5亿元, net profit 67.9亿元, EPS 16.10.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: 1903.00.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=0.678, eps=16.1, reason=EPS/share mismatch expected 0.1607 vs EPS 16.1000; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688256-寒武纪/AP202604281821702568-第一上海证券-AI-Agent时代来临-国产算力支撑AI建设.pdf.

## 688795 摩尔线程

- Status: ps_sotp_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 643.81, shares 4.70亿股, market cap 3026.1亿元.
- 2026E: revenue 26.7亿元, net profit -10.0亿元, EPS -2.13.
- Method: PS/PB or milestone valuation watchlist; positive EPS denominator not valid; broker source quality: original_pdf; broker target: 182.25.
- Forecast quality flags: broker_2026E_revenue_outlier_rejected: broker=2595.8400, proxy=26.7268; broker_2026E_profit_eps_pair_rejected: net_profit=-1003.0, eps=-2.134, reason=implausible net margin -3752.79%; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: PS/SOTP 里程碑目标已完成；当前不把未兑现利润提前资本化，后续以收入、毛利率、费用率、现金流和盈利拐点更新。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688795-摩尔线程/AP202511301791284379-国金证券-以全功能GPU为核心的国产加速计算平台领军者.pdf.

## 603881 数据港

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 25.21, shares 7.19亿股, market cap 181.3亿元.
- 2026E: revenue 18.2亿元, net profit 1.7亿元, EPS 0.23.
- Method: PB/ROE plus EV/EBITDA check; PE is secondary; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若上架率、算力收入或现金流不能覆盖 capex 和折旧压力，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/603881-数据港/01-AP202604211821396756-中邮证券-业绩维持稳健-智算业务贡献增量.txt.

## 301291 明阳电气

- Status: house_target_model_ready; action: core focus; rating label: 核心关注.
- Denominator: price 36.19, shares 3.12亿股, market cap 113.0亿元.
- 2026E: revenue 126.2亿元, net profit 10.3亿元, EPS 3.30.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/301291-明阳电气/AP202509301753286098-开源证券-公司首次覆盖报告-新能源输配电翘楚-海外-海风-AIDC多域突破.pdf.

## 002396 星网锐捷

- Status: house_target_model_ready; action: core focus; rating label: 核心关注.
- Denominator: price 23.40, shares 8.52亿股, market cap 199.4亿元.
- 2026E: revenue 249.2亿元, net profit 10.3亿元, EPS 1.21.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=None, eps=1.21, reason=missing net profit or EPS; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002396-星网锐捷/AP202507131708177975-民生证券-2025年中报预告点评-数据中心交换机驱动利润高增-探索跨境支付应用.pdf.

## 603228 景旺电子

- Status: target_model_ready; action: market support watch; rating label: 市场支撑观察.
- Denominator: price 71.97, shares 10.00亿股, market cap 719.8亿元.
- 2026E: revenue 170.4亿元, net profit 21.8亿元, EPS 2.18.
- Method: PE/PEG plus cycle/product-mix check; broker source quality: original_pdf; broker target: 34.32.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=14.5614, eps=2.18, reason=EPS/share mismatch expected 1.4559 vs EPS 2.1800; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/603228-景旺电子/AP202505141672723916-西南证券-看好PCB全平台工艺能力下客户突破机会.pdf.

## 002158 汉钟精机

- Status: house_target_model_ready; action: market support watch; rating label: 市场支撑观察.
- Denominator: price 35.97, shares 5.38亿股, market cap 193.4亿元.
- 2026E: revenue 34.6亿元, net profit 7.2亿元, EPS 1.34.
- Method: normalised PE/SOTP with data-center order validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=54.43, eps=1.34, reason=implausible net margin 157.31%; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002158-汉钟精机/AP202509171745482711-国信证券-AIDC压缩机-半导体真空泵打造新成长曲线.pdf.

## 688041 海光信息

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 325.40, shares 26.87亿股, market cap 8743.2亿元.
- 2026E: revenue 206.6亿元, net profit 46.7亿元, EPS 2.01.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: 260.00.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688041-海光信息/AP202512101797605876-群益证券-重大重组终止-长期仍看好公司算力产业发展.pdf.

## 000021 深科技

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 55.91, shares 19.56亿股, market cap 1093.4亿元.
- 2026E: revenue 163.8亿元, net profit 12.5亿元, EPS 0.64.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: official_filing_no_broker_target; broker target: not disclosed.
- Forecast quality flags: financial_proxy_profit_eps_used.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/source-exhausted-official-filings-20260701/000021-深科技/annual-2025年年度报告.txt.

## 688008 澜起科技

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 266.80, shares 12.18亿股, market cap 3249.8亿元.
- 2026E: revenue 71.6亿元, net profit 23.4亿元, EPS 1.92.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: 95.00.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=None, eps=1.92, reason=missing net profit or EPS; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688008-澜起科技/AP202502211643357942-群益证券-中国AI算力需求大爆发-利好内存接口龙头.pdf.

## 600089 特变电工

- Status: house_target_model_ready; action: pullback validation; rating label: 回调验证.
- Denominator: price 22.01, shares 73.61亿股, market cap 1620.1亿元.
- 2026E: revenue 1129.4亿元, net profit 73.3亿元, EPS 1.21.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/600089-特变电工/01-AP202510101759490773-华鑫证券-公司动态研究报告-输变电订单高增-中标沙特大单.txt.

## 688183 生益电子

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 122.89, shares 8.32亿股, market cap 1022.2亿元.
- 2026E: revenue 90.3亿元, net profit 12.1亿元, EPS 1.46.
- Method: PE/PEG plus cycle/product-mix check; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 高端板/高速材料收入占比、认证进度、扩产稼动和毛利率验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688183-生益电子/AP202504291664395249-华鑫证券-公司事件点评报告-AI服务器高端PCB业绩放量-公司迈入高速成长通道.pdf.

## 688702 盛科通信

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 323.64, shares 4.10亿股, market cap 1326.9亿元.
- 2026E: revenue 12.1亿元, net profit 0.5亿元, EPS 0.11.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/688702-盛科通信/02-AP202604241821529215-开源证券-公司信息更新报告-营收增速符合预期-超节点龙头研发持续加速.txt.

## 002518 科士达

- Status: target_model_ready; action: market support watch; rating label: 市场支撑观察.
- Denominator: price 47.80, shares 5.93亿股, market cap 283.4亿元.
- 2026E: revenue 83.5亿元, net profit 9.4亿元, EPS 1.59.
- Method: normalised PE plus order-cycle / working-capital check; broker source quality: original_pdf; broker target: 64.00.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=6.1089, eps=1.59, reason=EPS/share mismatch expected 1.0305 vs EPS 1.5900; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/002518-科士达/AP202604281821658543-东吴证券-2026年一季报点评-数据中心产品及订单发展提速-新能源重回增长通道.pdf.

## 301205 联特科技

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 297.99, shares 1.30亿股, market cap 386.6亿元.
- 2026E: revenue 12.4亿元, net profit 1.7亿元, EPS 1.28.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_public_broker_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=0.97, eps=1.28, reason=EPS/share mismatch expected 0.7476 vs EPS 1.2800; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/blocked-core-candidate-broker-reports-20260701/301205-联特科技/01-AP202502211643346322-东兴证券-三步走战略-成长为光模块行业小巨头.txt.

## 688123 聚辰股份

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 204.00, shares 1.55亿股, market cap 317.0亿元.
- 2026E: revenue 18.6亿元, net profit 5.5亿元, EPS 3.49.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: none.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688123-聚辰股份/AP202502241643441278-中邮证券-SPD5服务器PC齐发力-端侧AI赋能NorFlash走向大容量.pdf.

## 688521 芯原股份

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 303.00, shares 5.26亿股, market cap 1593.5亿元.
- 2026E: revenue 62.7亿元, net profit 0.8亿元, EPS 0.17.
- Method: SOTP/PS/PE blend with profit-path validation; broker source quality: original_pdf; broker target: 300.00.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 收入增长、客户认证、订单兑现和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/688521-芯原股份/AP202606151823568591-群益证券-中美算力竞争利好公司-目前估值较低.pdf.

## 002334 英威腾

- Status: watchlist_only_insufficient_model; action: insufficient evidence; rating label: 证据不足.
- Denominator: price 7.26, shares 8.23亿股, market cap 59.8亿元.
- 2026E: revenue 43.7亿元, net profit -1.4亿元, EPS -0.17.
- Method: PS/PB or milestone valuation watchlist; positive EPS denominator not valid; broker source quality: official_filing_no_broker_target; broker target: not disclosed.
- Forecast quality flags: financial_proxy_profit_eps_used.
- Decision: 当前收入、股本和市值已补齐，但 2026E EPS 代理为负或不可用；PE/PEG 不适用，需等待盈利路径或改用明示 PS/PB/SOTP 证据。
- Catalyst: AIDC/海外订单、交付节奏、回款和毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/source-exhausted-official-filings-20260701/002334-英威腾/annual-2025年年度报告.txt.

## 301165 锐捷网络

- Status: house_target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 94.89, shares 7.95亿股, market cap 754.8亿元.
- 2026E: revenue 182.2亿元, net profit 11.5亿元, EPS 1.44.
- Method: PE/PEG with shipment, customer and margin validation; broker source quality: original_pdf; broker target: not disclosed.
- Forecast quality flags: broker_2026E_profit_eps_pair_rejected: net_profit=16.05, eps=1.44, reason=EPS/share mismatch expected 2.0177 vs EPS 1.4400; broker_EPS_retained_net_profit_derived_from_share_count.
- Decision: AStock 自建公允价值已完成，broker 权重为 0；当前价、股本/市值、2026E 分母和三情景可复算，残余 proxy 只作折价边界。
- Catalyst: 800G/1.6T 出货、客户导入、毛利率和现金转化同步验证。
- Invalidation: 若产品升级不能转化为收入和毛利率，或客户/订单证据弱化，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/301165-锐捷网络/AP202606021823158258-开源证券-公司首次覆盖报告-从高端交换机到光模块全链条布局的网络设备龙头.pdf.

## 300499 高澜股份

- Status: target_model_ready; action: high valuation risk; rating label: 高估值风险.
- Denominator: price 36.60, shares 3.09亿股, market cap 113.3亿元.
- 2026E: revenue 12.7亿元, net profit 1.4亿元, EPS 0.45.
- Method: normalised PE/SOTP with data-center order validation; broker source quality: original_pdf; broker target: 32.51.
- Forecast quality flags: none.
- Decision: 明示券商/Street 目标价锚、当前价、股本/市值、2026E 分母和三情景复算已完成；订单、毛利率、客户/平台和现金流是更新触发，不是发布前置缺口。
- Catalyst: 液冷订单、批量验收、收入确认和项目毛利率验证。
- Invalidation: 若订单交付、收入确认、毛利率或回款任一环节失速，则估值信用下调。
- Source: sources/core-candidate-valuation-broker-reports-20260701/300499-高澜股份/AP202509161744822098-国信证券-特高压纯水冷却设备龙头-数据中心液冷打造第二成长曲线.pdf.
