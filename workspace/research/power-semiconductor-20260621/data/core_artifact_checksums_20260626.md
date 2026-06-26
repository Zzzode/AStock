# 功率半导体深度研报 · 核心工件校验和（R272 · 22 files）

> R272大幅补录刷新 · 估值模型(Ch07) + 投资建议(Ch09) + 估值审计整改 · SHA三相闭环。版本日期 20260626。

|#|文件名|SHA-256[:12]|字节数|分类|基线对比|
|---|---|---|---|---|---|
|1|`sections/ch00_abstract.tex`|`a0fa7d3cee3f`|3,825|latex_chapter|SAME|
|2|`sections/ch01_executive_summary.tex`|`3d2d9aa45556`|7,736|latex_chapter|SAME|
|3|`sections/ch02_industry_overview.tex`|`3a982946618b`|31,514|latex_chapter|SAME|
|4|`sections/ch03_demand_analysis.tex`|`8620056a75c5`|12,195|latex_chapter|SAME|
|5|`sections/ch04_technology.tex`|`4a6cb979603d`|53,258|latex_chapter|SAME|
|6|`sections/ch05_competition.tex`|`ebf4f7aff299`|10,741|latex_chapter|SAME|
|7|`sections/ch06_companies.tex`|`bba96dd8422b`|16,983|latex_chapter|SAME|
|8|`sections/ch07_valuation.tex`|`71a399936ead`|46,282|latex_valuation|**DIFF**|
|9|`sections/ch08_catalysts_risks.tex`|`c53461bf05b6`|8,086|latex_chapter|SAME|
|10|`sections/ch08_policy_geopolitical.tex`|`1c5279ca2832`|33,136|latex_chapter|SAME|
|11|`sections/ch09_investment_advice.tex`|`862628aaab88`|42,935|latex_investment|**DIFF**|
|12|`sections/ch09_secondary_market.tex`|`5c41c0cf3b07`|38,386|latex_chapter|SAME|
|13|`sections/appA_data.tex`|`ba6a115cb2e4`|6,245|latex_appendix|SAME|
|14|`analysis/valuation_model.md`|`3e77b839a307`|6,622|analysis_valuation|**DIFF**|
|15|`analysis/valuation_audit.md`|`70b9cdf719a6`|20,663|analysis_audit|**DIFF**|
|16|`main.tex`|`ae2fa3c583c6`|3,690|core_output|SAME|
|17|`main.pdf`|`6de122879c33`|1,251,529|core_output|**DIFF**|
|18|`data/financial_detail_data.json`|`54676cdf251a`|7,888|data_raw|SAME|
|19|`data/official_financials_summary.md`|`8403e12e47cb`|7,417|data_raw|SAME|
|20|`data/verified_market_data.md`|`9ad86b4bd94d`|4,426|data_raw|SAME|
|21|`data/broker_target_price_history.md`|`c032ced0b1ad`|22,866|data_raw|SAME|
|22|`data/ir_guidance_summary.md`|`923f35b68ef8`|16,636|data_raw|SAME|

**Hash 变更统计**：DIFF=5 / SAME=17 / NEW=0

**R272 变更说明**：
- `sections/ch07_valuation.tex` — 新增完整估值模型（表7-M1~M5 + SOTP + 数学公式 + 10家26E业绩）
- `sections/ch09_investment_advice.tex` — 章节结构重组，表11-1~11-10重排，图11-1~11-3修正，新增推导桥表(11-5)与三情景矩阵(11-6)
- `analysis/valuation_model.md` — 新增10家三情景目标价全表
- `analysis/valuation_audit.md` — 从7项BLOCK改写为整改完成+4项持续跟踪
- `main.tex` + `main.pdf` — 重新编译成功 109页
