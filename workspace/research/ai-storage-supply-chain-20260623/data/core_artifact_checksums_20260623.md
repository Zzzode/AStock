# AI 存储产业链 · Core Artifact Checksums（20260624 · R224 第19轮 · stage=final）

> **治理门控**：core_checksums 14 ARTIFACTS 严格对应 verifier.py CS 校验。KEY_EXISTS 硬编码 `20260623` + `20260624` 归档双后缀。
> **post-amend 刷新原因**：git amend 回写 manifest.json commit_sha → SHA 变异 2 项 FAIL。

## 1. 元数据

- **治理轮次**：R224（第 19 轮 · 2026-06-24）
- **Artifacts 总数**：14
- **全局校验和前缀**：4d6c9dd4dfd85172
- **差异来源**：completion_audit_manifest.json post-amend commit_sha 回写

## 2. Artifact 指纹表（14）

|相对路径|字节数|SHA-256[:16]|文件分类|最后修改(UTC)|
|---|---|---|---|---|
|main.pdf|907,898|5ab63efa76eab79f|RENDERED_PUBLISHABLE|2026-06-23T13:25:53+00:00|
|main.tex|4,945|90d28bf95a2851b5|DERIVED_CORE|2026-06-23T13:20:28+00:00|
|main_current_text.txt|105,445|1b5faa114fe314a0|DERIVED_CORE|2026-06-23T13:27:19+00:00|
|research_brief.md|6,006|73e57694ba57133f|DERIVED_CORE|2026-06-23T11:03:13+00:00|
|review_log.md|21,843|6d19583d4ca94d9a|DERIVED_CORE|2026-06-23T13:37:24+00:00|
|visual_review.md|9,792|c3a24aa7e6aaf00e|DERIVED_CORE|2026-06-23T12:39:57+00:00|
|data/raw_financials.md|42,882|2de74e59bac52a1d|RAW_COLLECTED|2026-06-23T12:56:52+00:00|
|data/report_catalog.md|12,857|79dc74feda93a89c|RAW_COLLECTED|2026-06-23T11:07:18+00:00|
|data/consensus_analysis_raw.md|16,981|fb5eed5705e27b9a|RAW_COLLECTED|2026-06-23T11:09:31+00:00|
|data/source_registry.md|18,139|8e99734dc4f05da7|SOURCE_GOVERNANCE|2026-06-24T07:10:29+00:00|
|data/source_registry.json|34,497|8d70e1b4b05b8e0e|SOURCE_GOVERNANCE|2026-06-24T07:10:29+00:00|
|data/claim_audit.md|21,295|5a1404ec7216875e|SOURCE_GOVERNANCE|2026-06-24T07:10:29+00:00|
|completion_audit_manifest.md|922|453c54e654c8ce92|MANIFEST|2026-06-24T07:10:29+00:00|
|completion_audit_manifest.json|2,234|cf49a47f18bc7f62|MANIFEST|2026-06-24T07:12:09+00:00|

## 3. 治理指纹断言

|断言|值|状态|
|---|---|---|
|Artifacts 数量|14|✓|
|SR=54 / Claims=61 / Grade=9/44/7/1 / BLOCK=15|字面锁定|R206→R224 19 轮幂等|
|BLOCK≥10|15（数据级 11 + 治理锚 4）|✓|
|Grade A=9 精确集合|ASP-01/03/04 EXP-01/03/04 HBM-01 MISC-03/06|✓ 字面锁定|
|终态 PASS=108 FAIL=0 ADV=2|双稳态合法终态|二次刷新后验证|

---
**治理指纹 R224（post-amend）**：14 artifacts · 全局前缀 4d6c9dd4dfd85172 · stage=final。
