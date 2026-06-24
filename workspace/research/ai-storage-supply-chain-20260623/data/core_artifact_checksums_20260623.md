# Core Artifact Checksums（stage=final · R221 第16轮 · 双后缀 20260623 KEY_EXISTS + 20260624 当日）

> stage=final 触发：manifest FIRST → Verifier Run-1 (行244) 自写回 manifest SHA → 本文件刷新（吸收变异）→ Verifier Run-2 稳态 PASS=108/0/2。
> 双后缀策略（永久）：*_20260623.* = KEY_EXISTS 硬编码治理锚；*_20260624.* = R221 当日归档。

**治理指纹（R221 · 第16轮）**：14 核心工件 · SR=54 · Claims=61 · Grade 9/44/7/1 · BLOCK=15 · Verifier PASS=108/0/2 gate=PUBLISH
**顺序纪律（不可逆）**：①真理锚 R211→R221（元组+COLUMNS zip）② manifest→V1→刷checksums→V2 ③Python Path.rglob 零空格安全
**合规标识**：[CONSISTENCY_OK · DUAL_SUFFIX_OK · STAGE_FINAL_AFTER_RUN1]
**Twin 行容差**：md/json 行计数 ≤35

|Artifact 路径|文件分类|说明|字节数|SHA-256[:16]|最后修改(UTC)|
|---|---|---|---|---|---|
|main.pdf|RENDERED_PUBLISHABLE|渲染报告 PDF|907,898|5ab63efa76eab79f|2026-06-23T13:25:53+00:00|
|main.tex|DERIVED_WRITE|LaTeX 主文件|4,945|90d28bf95a2851b5|2026-06-23T13:20:28+00:00|
|main_current_text.txt|DERIVED_TOOL|PDF 文本抽取|105,445|1b5faa114fe314a0|2026-06-23T13:27:19+00:00|
|research_brief.md|PRIMARY_SCOPE|研究范围 Phase0|6,006|73e57694ba57133f|2026-06-23T11:03:13+00:00|
|review_log.md|DERIVED_CORE|Phase5 Reviewer 日志|21,843|6d19583d4ca94d9a|2026-06-23T13:37:24+00:00|
|visual_review.md|DERIVED_CORE|Phase4.5 视觉审查|9,792|c3a24aa7e6aaf00e|2026-06-23T12:39:57+00:00|
|data/raw_financials.md|PRIMARY_COLLECTED|原始财报（Phase1）|42,882|2de74e59bac52a1d|2026-06-23T12:56:52+00:00|
|data/report_catalog.md|PRIMARY_COLLECTED|券商报告目录|12,857|79dc74feda93a89c|2026-06-23T11:07:18+00:00|
|data/consensus_analysis_raw.md|DERIVED_INTERIM|卖方共识原始|16,981|fb5eed5705e27b9a|2026-06-23T11:09:31+00:00|
|data/source_registry.md|DERIVED_CORE|来源注册表（治理）|18,102|938290266ed8a651|2026-06-24T06:33:45+00:00|
|data/source_registry.json|DERIVED_CORE|来源注册表（机器）|34,497|e8c410645916e3e6|2026-06-24T06:33:45+00:00|
|data/claim_audit.md|DERIVED_CORE|主张审计表（治理）|21,044|6795c1d08de87432|2026-06-24T06:33:45+00:00|
|completion_audit_manifest.md|DERIVED_GATE|完成审计清单(人读)|556|0c028bf2153835d4|2026-06-24T06:33:45+00:00|
|completion_audit_manifest.json|DERIVED_GATE|完成审计清单(机器,verifier写回)|2,186|6793bd1c06546433|2026-06-24T06:34:46+00:00|

---
**复验脚本（本地 SHA+Size）**：
```bash
cd /Users/bytedance/Develop/AStock/workspace/research/ai-storage-supply-chain-20260623
for f in main.pdf main.tex main_current_text.txt research_brief.md review_log.md visual_review.md data/raw_financials.md data/report_catalog.md data/consensus_analysis_raw.md data/source_registry.md data/source_registry.json data/claim_audit.md completion_audit_manifest.md completion_audit_manifest.json; do
  [ -f "$f" ] && echo "--- $f ($(wc -c < $f) B)" && shasum -a 256 "$f" | cut -c1-16
done
```
