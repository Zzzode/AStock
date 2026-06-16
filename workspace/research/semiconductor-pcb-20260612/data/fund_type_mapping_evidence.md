# Fund Type Mapping Evidence

**Sources:** AkShare `fund_name_em` and top visible funds from `fund_holding_enhanced_evidence.json`.

**Boundary:** This maps top visible fund codes to Eastmoney fund types. It improves official type labeling for examples, but full stock-level active/passive exposure still relies on the rule-based style proxy.

| Ticker | Name | Top mapped fund types | Examples |
|---|---|---|---|
| 002463 | 沪电股份 | 混合型-偏股: 15.39亿元; 指数型-股票: 37.88亿元; 混合型-灵活: 7.52亿元 | 永赢科技智选混合发起A; 易方达上证50增强C; 东吴移动互联混合A |
| 300476 | 胜宏科技 | 混合型-偏股: 15.59亿元; 指数型-股票: 22.21亿元; 混合型-灵活: 16.41亿元 | 睿远成长价值混合A; 易方达创业板ETF; 德邦鑫星价值C |
| 002916 | 深南电路 | 混合型-偏股: 22.71亿元; 股票型: 8.26亿元 | 永赢科技智选混合发起A; 富国新兴产业股票C |
| 600183 | 生益科技 | 混合型-偏股: 3.35亿元; 混合型-灵活: 8.75亿元 | 大摩数字经济混合A; 博时成长领航混合A |
| 603186 | 华正新材 | 债券型-混合一级: 0.60亿元; 混合型-偏股: 0.69亿元; 指数型-股票: 0.11亿元 | 华夏双债债券A; 易方达行业领先混合; 华泰柏瑞中证2000指数增强C |
| 688519 | 南亚新材 | 股票型: 8.22亿元; 混合型-灵活: 1.49亿元; 混合型-偏股: 1.24亿元 | 易方达战略新兴产业股票A; 易方达新常态混合; 易方达港股通优质增长混合C |
| 002436 | 兴森科技 | 债券型-混合二级: 0.94亿元; 混合型-灵活: 0.60亿元; 混合型-偏股: 0.90亿元 | 光大保德信信用添益债券A类; 汇添富优势精选混合; 汇添富美丽30混合D |
| 301200 | 大族数控 | 混合型-灵活: 9.02亿元; 股票型: 2.57亿元 | 财通成长优选混合A; 财通集成电路产业股票C |
| 688630 | 芯碁微装 | 股票型: 1.33亿元; 混合型-偏股: 0.90亿元; 混合型-灵活: 2.61亿元 | 路博迈资源精选股票发起A; 信澳匠心臻选两年持有期混合; 金信深圳成长混合E |
| 300400 | 劲拓股份 | 混合型-偏股: 0.27亿元; 指数型-股票: 0.09亿元 | 鹏华汇智优选混合A; 华泰柏瑞中证2000ETF |
| 301377 | 鼎泰高科 | 混合型-偏股: 10.90亿元; 混合型-灵活: 6.50亿元 | 永赢科技智选混合发起A; 财通成长优选混合A |

## Interpretation

- Top visible funds can be mapped to Eastmoney fund types such as 混合型-偏股, 股票型, 指数型, 债券型 and ETF-like names.
- This gives more formal labels for examples, but it does not provide complete active/passive ownership classification for every holder row.
- Use together with `fund_holder_style_proxy.md`, not as a standalone terminal-grade ownership database.
