# Delta Audit — 数据、模型与范围修正记录

## 修正触发

用户指出旧报告的市场数据并非最新，且股息率被高估。复核进一步发现，旧的“直接高股息个股 30%”分支与本案已批准的 ETF/资产层基准模型相冲突。

## 已作出的范围决定

本次修复冻结为“ETF/资产层优先的条件性战略框架”：初始直接股票配置为 0%，任何未来直接股票只可替换红利权益 ETF 的一部分，合计不超过 15%、单一发行人不超过 5%。因此，历史个股股息率只保留为非决策观察数据；它们不再驱动组合配置、现金流、年化收益或十年复利预测。

## 失效的旧分支

| 旧内容 | 处理 | 原因 |
|---|---|---|
| 8 只个股平均股息率 6.29% | 禁用 | 旧分母与分红口径不可复现，且与当前个股观察快照显著不符。 |
| 组合预期年化 4.73% / 现金分红 3.53% | 禁用 | 由失效的直接股票权重、固定 ETF 分配率与未披露假设混合而成。 |
| “修正后约 3.89%” | 不作为替代值 | 该数值仍不能由当时披露的资产权重与输入复算。 |
| CNY7,060 年现金、CNY9,460 年收益、约 CNY317,499 十年终值 | 删除 | 都依赖上述不可复现的点预测。 |

## 历史证据口径（已被当前范围退休决定替代）

1. `data/raw_quote_snapshot_20260811.json` 记录了 Tencent 行情接口于 2026-08-11 约 16:14 的结构化价格摘录、原始响应 SHA-256、来源与局限。其质量为第三方快照，仅可用于观察池的历史分母。
2. `data/dividend_evidence_20260811.json` 记录官方发行人公告 URL、每股现金分配的组成和不可比警告。URL 已保存；原始 PDF 尚未在本地完整归档，因此不能把该包升级为执行证据。
3. `data/high_dividend_stock_pool_20260811.json` 仅展示截至日的历史毛股息率观察，明确排除中国神华的简单收益率比较，并不生成组合平均收益预测。
4. `data/portfolio_return_model_20260811.json` 改为透明的 3%--6%长期规划区间及复利敏感性；不包含点收益率或固定现金分配预测。

## 受影响交付物

已重写研究简报、主文摘要、七个正文章节、数据附录和收益模型，使其与 `analysis/allocation_model.md`、`analysis/scenario_model.md` 和 `analysis/cashflow_and_tax.md` 的 ETF/资产层模型一致。旧 PDF、提取文本、渲染图和任何声称通过的视觉审查均不代表当前 TeX 源文件；它们已保留到 `rendered/superseded-*`。当前源已在支持 CJK 的 XeLaTeX 环境中重新生成，完整溯源见 `data/build_provenance_20260812_actionability.{md,json}`，但尚未完成独立审查，因此仍不可发布。

## 历史开放条件（已被后续最终范围修复替代）

1. 将所有材料性发行人/产品原始文件以不可变本地路径、哈希和页码定位归档；
2. 由独立审查者检查当前 18 页渲染结果，并记录哈希绑定的 R3 结论；
3. 重新完成 R0--R4 审查、工作流评估和最终签署。

## 平台构建规则修正 — 2026-08-11

此前把 CJK 排版需求错误地写成“仅 macOS MacTeX”的发布条件。该条件不是 XeLaTeX、`ctex`、`xeCJK` 或本案字体配置的技术要求，现已改为平台中立的 XeLaTeX/CJK 规则：任何能够通过 CJK 预检的主机均可构建；必须记录操作系统、XeLaTeX 可执行文件及版本/发行版、构建命令、源文件哈希、PDF 哈希和页数。macOS 的 `/Library/TeX/texbin` 仅是可选发现路径。此次规则修正不使旧 PDF 恢复有效；当前范围仍需重新构建和独立审查。

## 已被替代的当前源构建刷新 — 2026-08-12 00:10

当时的 TeX 源已用 Linux 上的 XeLaTeX（TeX Live 2022/Debian）双轮构建为 18 页 A4 PDF；源文件 SHA-256 为 `cf5d712284859b46340069d61d216f5a6c58b5cfe1ffbe419be0bf157a742ceb`，PDF SHA-256 为 `f6c9318abd5672515e0be4a34da2ccefc60294687ab336f0ae39608356bf1cf3`。该构件已因下述标的/动作卡修复而被替代，历史 PDF 与页图位于 `rendered/superseded-20260812-0010/`。

## Actionability correction — 2026-08-12

- User correction: the report must state the investable model targets and the intended investment actions. Asset-class weights without a designated instrument, amount, sequence, fallback and rebalance behavior are not an actionable allocation strategy.
- Original miss: `sections/ch01_decision.tex` and `sections/ch03_portfolio.tex` state the asset-layer weights, but reduce 511010, 510880, 512890 and 518880 to illustrative examples. The only detailed product map is in `analysis/product_universe.md`, which is not a reader-facing report section.
- Missing artifact/gate: a source-linked, reader-facing model-portfolio implementation card was absent from the investment-committee summary, despite the equity-research first-chapter requirement to answer what to buy or track, why now, and how to add, trim or defer it.
- Responsible workflow: `equity-research` drafting/orchestration and the LaTeX-writer output contract; this is a report-actionability failure, not a claim that the existing price data can generate live orders.
- Evidence used for the repair: current case product-source records S08--S12 and the dated M01 ETF quote snapshot. M01 remains a Tier-3 historical snapshot and is not used to prescribe price, share count, premium/discount or execution timing.
- Implemented repair: added a designated model-instrument table and an explicit staged implementation/rebalance card to the reader source; updated the structured allocation packet, artifact contract and review finding, then rebuilt the PDF.
- Prevention rule to propose, not yet apply: any report labelled an allocation strategy must have a reader-facing table with each active sleeve's designated model instrument (or explicit cash/deposit implementation), target amount, action, fallback when the validation gate fails and rebalance/stop trigger. Generic "representative examples" cannot satisfy this gate.

## 已被替代的标的与动作卡构建检查点 — 2026-08-12 00:57

该历史检查点首次明确了 CNY70,000 的 511010、CNY30,000 的 510880、条件性 CNY30,000 的 512890、CNY20,000 的 518880、CNY40,000 受保障流动性和 CNY10,000 交易现金。其后续范围修复已替代当时的失败回退表述：当前规则要求任何未通过ETF资格或穿透的金额唯一留在受保障流动性，既不自动转入511010，也不增加交易现金。

该源已双轮构建为 18 页 A4 PDF：源文件 SHA-256 为 `ff771a67bcefc9f1c22987f3115c6caca56c4dbc3c40aa91e79969e01f031a13`，PDF SHA-256 为 `d485b96227d0caca0abcb79b263b7a26301ee2d4e0395cb6ad39f41227d93102`，文本 SHA-256 为 `171c58b604fac021ffae3ecc2733319c581a9509864855bce1144e3290c2085a`。18 张 150 DPI 页图保存在 `rendered/full-20260812-0057/`；作者已检查标的、建仓和实施卡所在页，无裁切、重叠或表格截断。完整构建记录为 `data/build_provenance_20260812_actionability.{md,json}`。这仍不替代独立 R2/R3 审查、当日交易质量核验或 R0--R4 发布签署。

## 综合模型／正文修复构建检查点 — 2026-08-12 04:20

作者完成了模型边界、资料边界、中文正文与版面修复：读者正文将目标仓位、受控 `q` 门槛、确定性的受保障流动性回退、`r`／`D_0` 的边界，以及情景压力与已观测回撤的区别放在可核对的位置。该检查点曾生成一份 17 页 A4 作者构件：`main.pdf` SHA-256 `86ac768d39f425aa116c4ef8fac2492b5c192329bfe00935826be5b68cea5440`，文本 SHA-256 `adcab61e68a792b427fd04ad5be09c98d25637297624980816402eb51fc26a2d`，页图位于 `rendered/full-20260812-0420/`。XeLaTeX 双轮构建记录为 0 个 fatal／undefined-control-sequence／missing-character／`Overfull \\hbox`；仅封面源代码第 23 行有一个不影响可见内容的 `Underfull \\hbox`。作者检查了全部 17 张页图。

上述构件只作为修复完成时的历史检查点保存，**不是**可发布的最终工件身份。资料范围清理现已完成：非决策性的直接股票／期货历史观察已从活跃读者范围和活跃证据范围退休，必须重新编译并重新绑定源、PDF、文本和渲染哈希；本段的 17 页哈希不得被当作最终发布哈希。无论重新构建结果如何，本记录不构成独立 R1、R2、R3 或 R4 签署。

活跃范围的归档现为 15 成功／0 部分／0 失败；此前 25 个来源的 21 成功／1 部分／3 失败仍完整保留为历史背景。该历史缺口的原始字节没有被恢复或重新创建，也**不**可被称为已解决；它们只是退休且禁止支撑当前的目标、配置、估值、现金或执行结论。因此，活跃范围的归档门槛是通过范围退休而非原始文件恢复得到满足。

发布仍被以下事实阻断：未取得完整当日执行包时执行资格为 `not_run`、所有 ETF 的 `q=0`，并且没有独立 R1、R2、R3 或 R4 签署。该研究不是交易指令；不得把模型目标、历史快照或作者构建记录解释为可下单价格、数量、适当性判断或执行授权。

## 当前最终范围与构建 — 2026-08-12 04:57

当前读者范围已经重新生成并绑定到 `data/build_provenance_20260812_actionability.{md,json}`：14页A4 PDF，读者源SHA-256为`04ba969991bb6cb70e21da378ff4b1c93ea8dd100fc0dedf884f05260a55f94d`，源图SHA-256为`8dc0c58118162f8e456caf8ec025ed9312c5c900b97c5f3ee94af0a2c00302e4`，PDF SHA-256为`ece9c8436ca4117889587a17177251a1ba93cf3af945e05ecd75bb20098a50f9`。此前18页和17页构件均为已替代的历史检查点，不能用作当前身份或签署依据。

活跃来源范围为S01--S13、S15和S16，共15项本地归档材料（15成功／0部分／0失败）。S14、M01及D01--D08仍保留为未恢复的审计历史，但已从活跃范围退休，不能支持当前目标、配置、估值、现金或执行结论；范围完整并不是对旧原始字节已恢复的声称。

当前模型动作固定为CNY40,000受保障流动性、CNY10,000交易现金、在$q=1$时于T0建立CNY70,000的511010、六个月分批建立CNY30,000的510880和经穿透核验的CNY30,000的512890，以及六个月分批建立CNY20,000的518880；REITs和直接股票初始为CNY0。资格包当前为`not_run`且所有$q=0$，这是实施日核验尚未发生的边界，而不是已经通过的交易授权；未通过的金额仅留在受保障流动性。
