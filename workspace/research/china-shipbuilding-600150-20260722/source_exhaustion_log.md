# 来源检索穷尽记录（R0）

截止：2026-07-22。`blocks_valuation=true` 指阻断该字段/方法获得估值信用；并非每项都阻断 600150 合并口径估值。

| probe_id | query_or_target | source_attempted | result | reason_unresolved | artifacts_saved | next_verification_path | blocks_valuation | owner |
|---|---|---|---|---|---|---|---|---|
| EX-01 | 13 份原始券商报告的明确目标价 | BR-01—BR-13 全文估值表/预测表 | 全部 `not disclosed` | 原报告未给目标价 | 13 PDF+13 text | 券商授权报告或保留报告身份/估值表的 Wind/Choice/iFinD 导出 | true：有效 Street 目标价 | report-collector |
| EX-02 | 华泰 2026-05-03 原始报告/58.96 元 | 券商官网、聚合页、公开 F10 | 仅第三方转述；原始 PDF 未取得 | 原始报告不可公开访问 | `sources/probe-20260722/huatai-600150-260503-preview.html` | 华泰官方研究平台或授权终端导出 | true：目标价；当前权重 0 | report-collector |
| EX-03 | 国泰海通 2026-05-19 原始报告/47.00 元 | 第三方预览与搜索线索 | 本地 artifact 为 404，无可核预测字段 | 页面失效且原始 PDF 未取得 | `sources/probe-20260722/guotai-haitong-600150-260519-preview.html` | 国泰海通官方平台或授权终端导出 | true：目标价；当前权重 0 | report-collector |
| EX-04 | iFinD 公开一致预期 | 同花顺/iFinD 页面 | Nginx forbidden | 权限/反爬 | `sources/probe-20260722/10jqka-ifind-consensus-600150-20260518.html` | 授权终端结构化导出 | true：该共识源不可用 | report-collector |
| EX-05 | 同时点流通市值与换手率 | AStock quote packet后，补充东方财富结构化截止日行情快照 | 已解析75.2562亿流通A股本、2,484.96亿元流通市值和1.44%换手率，并以量/股本、价/股本机械勾稽 | 严格自由流通仍无统一、可复核的账户可交易性分类 | `sources/market-structure-20260722/`及其manifest | 若需要严格自由流通，须取得统一锁定/战略/长期分类数据 | false：流通市值/换手已闭环；true：严格自由流通口径 | data-collector |
| EX-19 | 2026-07-21沪股通5/20日净持股变化 | 上交所单只证券季度持有量；东方财富日频个股端点 | 上交所公开单只证券口径为季度持有量；日频端点返回`9201/返回数据为空` | 不能以季度末持仓差冒充5/20日净流 | `sources/capital-positioning-20260722/eastmoney_northbound_daily_600150_20260721_unavailable.json` | 可获得交易所或授权终端日频逐证券数据后再更新 | true：日频北向流方法；false：季度存量分析 | data-collector |
| EX-06 | 全部资产权属登记完成清单 | CF-12/14/15/16、公告索引 | 未找到逐资产完成清单 | 披露仅说明实质承继/手续办理 | 官方 PDF/JSON 已归档 | 后续持续督导、工商/产权登记公告 | true：禁止“全部手续完成”表述 | source-governance-analyst |
| EX-07 | 原 601989 法人注销完成 | 退市决定、实施公告、持续督导、公告索引 | 未找到明确注销完成文件 | 退市不等于法人注销 | CF-13—16 | 国家企业信用信息公示系统或后续交易所公告 | true：禁止“法人已注销”表述 | source-governance-analyst |
| EX-08 | 船型/船厂/年度交付排程及合同额 | 2025 年报、2026Q1、业绩说明会、重组报告 | 聚合订单充分，逐船排程未披露 | 商业保密/披露粒度 | CF-03/04/12/17 | 半年报、重大合同进度、船东交付清单 | true：船型收入模型；false：合并情景估值 | growth-earnings-modeler |
| EX-09 | 船型 ASP 与签价/现价差 | 公司披露、Clarksons 公共报告 | 付费船价库及逐合同价格不可得 | 数据库付费/合同保密 | CF-03/17、II-08 | Clarksons 船型价格库+签单年份映射 | true：船型 ASP 估值 | valuation-modeler |
| EX-10 | 七家船厂 CGT 产能、船位、利用率 | 年报、重组报告、行业公开材料 | 无统一可比口径 | 公司未统一披露 | CF-03/12 | 地方环评、船坞排产、公司调研交叉 | true：产能利用率溢价；false：官方交付计划约束 | supply-chain-analyst |
| EX-11 | 军品订单/收入/毛利/在手 | 年报、重组报告、监管回复 | 未披露 | 涉密且无独立分部经济性 | CF-03/12、II-05 | 仅使用合法公开监管/分部披露 | true：军品 SOTP | fundamental-analyst |
| EX-12 | 沪东中华资产/订单边界与中远约 500 亿元项目细项 | 公司/集团材料、年报、说明会 | 沪东中华仍在上市体外；中远 87 艘/约 500 亿元项目已确认均由公司下属相关子公司承建，但含意向订单且细项未披露 | 沪东中华注入未披露；中远项目确定/意向比例、船厂、排期、利润率未披露 | CF-03/12/17 | 600150 重大合同/资产注入公告及船东订单清单 | true：沪东中华/项目级利润法；false：中远项目上市公司聚合归属 | source-governance-analyst |
| EX-13 | 上游供应商/BOM/认证/单船价值量 | 年报供应商集中度、OECD、供应商公共资料 | 无双向项目级证据 | 名称、产品、认证、收入暴露未披露 | CF-03、II-10 | 船级证书、供应商公告、招标/合同双向核验 | true：上游供应商估值 | supply-chain-analyst |
| EX-14 | 600150 公司级全球/中国 CR3/CR5 | MIIT、CANSI、UNCTAD、OECD、Clarksons、公司年报 | 仅国家或集团层数据 | 口径不到上市公司 | II-06—11、CF-03 | Clarksons 船厂数据库并统一母集团/上市边界 | true：公司份额溢价 | industry-analyst |
| EX-15 | UNCTAD 2025 chapter 2 本地原件 | UNCTAD PDF URL | 远端归档受阻；精确集中度/船型比例已从发布材料删除 | 下载限制 | 原始 URL 记录于 `SOURCE_INDEX.md`，无本地 PDF | 重试官方 CDN/机构库；保留文件哈希与页码后再恢复数字 | false：零权重检索线索 | data-collector |
| EX-16 | USTR/White House 暂停政策本地快照 | 两个政府网页 | 仅 URL，未归档；精确起止日和法律效果已从发布材料删除 | 本案收集未保存网页 | URL 记录于 `SOURCE_INDEX.md` | 重新抓取并记录生效期后再恢复精确表述 | false：零权重监测线索 | industry-analyst |
| EX-17 | 2026H1 正式结果 | 上交所公告索引截至 cutoff | 截止日只有业绩预告 | 半年报尚未发布 | CF-05 | 半年报发布后替换预告并重跑估值 | false：预告可作阶段锚；最终值待验 | data-verifier |
| EX-18 | 同口径海外可比估值 | 扬子江、韩国三大、Fincantieri 官方页面/URL | 能力/部分订单可见，未完成分部财务和估值标准化 | 业务组合、币种、会计口径不同；部分网页未归档 | URL 记录于 `SOURCE_INDEX.md` | 归档原始年报并建立同口径分部模型 | true：海外可比倍数法 | valuation-modeler |

## 耗尽结论

- 合并口径估值所需的法定实际、重述比较期、股本、聚合订单、现金流和当前价格已闭环。
- 有效 Street 目标价、军品 SOTP、船型 ASP/排程/利用率、沪东中华注入、上游供应商和海外可比估值尚未闭环；这些字段保持 0 权重或阻断。中远约 500 亿元项目的上市公司聚合归属已闭环，但细项和利润率未闭环，且不得与聚合新签/在手重复相加。
- 58.96 元仅为零权重第三方线索；国泰海通 47.00 元的本地 artifact 为 404，目标价、EPS、倍数和上涨空间均已从一致预期包删除。
