# Residual Proxy Field Audit

- Residual proxy cells: 4
- Target-model residual proxy cells: 3
- Rule: proxy fields are disclosed model boundaries; they do not add standalone valuation uplift.

| Ticker | Company | Field | Official filings | Source | Remaining gap | Valuation consequence | Next verification |
|---|---|---|---:|---|---|---|---|
| 301291 | 明阳电气 | 利用率/良率/爬坡 | 3 | sources/blocked-core-candidate-broker-reports-20260701/301291-明阳电气/02-AP202509041738768805-华金证券-上半年业绩高增-aidc带来新机遇.md | 明阳电气 未披露独立利用率、上架率、稼动率或良率口径；模型改用订单/交付、运营效率、毛利率和现金流证据做交叉验证。 | AStock 自建公允价值模型保留，broker 权重为 0；该 proxy 字段只作折价边界，不触发目标价上修。 | 下一轮必须检查季度经营更新、IR 问答、上架率/稼动率/良率、PUE、毛利率、现金流和项目验收节奏。 |
| 603881 | 数据港 | 产能/认证 | 3 | sources/blocked-core-candidate-broker-reports-20260701/603881-数据港/01-AP202604211821396756-中邮证券-业绩维持稳健-智算业务贡献增量.txt | 数据港 已有 MW/项目交付或订单侧证据，但未披露可直接入模的独立产能、认证或产线利用明细；产能/认证只能作为容量边界，不作为单独扩张溢价。 | AStock 自建公允价值模型保留，broker 权重为 0；该 proxy 字段只作折价边界，不触发目标价上修。 | 下一轮必须检查年报/半年报、IR 记录、中标公告、客户侧项目验收、机柜/MW/产线/认证披露。 |
| 688041 | 海光信息 | 利用率/良率/爬坡 | 3 | sources/blocked-core-candidate-broker-reports-20260701/688041-海光信息/01-AP202605251822847721-中银证券-双芯驱动-生态筑基-引领国产算力新纪元.md | 海光信息 未披露独立利用率、上架率、稼动率或良率口径；模型改用订单/交付、运营效率、毛利率和现金流证据做交叉验证。 | 明示券商/Street 锚和 2026E 分母可复算，目标价模型保留；该 proxy 字段只限制上修空间，不提供增量倍数。 | 下一轮必须检查季度经营更新、IR 问答、上架率/稼动率/良率、PUE、毛利率、现金流和项目验收节奏。 |
| 002334 | 英威腾 | 利用率/良率/爬坡 | 3 | sources/source-exhausted-official-filings-20260701/002334-英威腾/annual-2025年年度报告.txt | 英威腾 未披露独立利用率、上架率、稼动率或良率口径；模型改用订单/交付、运营效率、毛利率和现金流证据做交叉验证。 | 该公司已因盈利或模型分母不足留在观察名单；残余 proxy 不发布目标价，只作为后续跟踪变量。 | 下一轮必须检查季度经营更新、IR 问答、上架率/稼动率/良率、PUE、毛利率、现金流和项目验收节奏。 |
