# Core Artifact Checksums · 20260624

> stage=final · polling_round=R218。顺序纪律：manifest FIRST → Verifier Run1(写回manifest) → 刷新checksums → Verifier Run2(终态)。

## 清单（14 项）

|#|路径（case-relative）|文件名|字节数|SHA-256[:20]|分类|
|---|---|---|---|---|---|
|1|workspace/research/ai-storage-supply-chain-20260623/main.pdf|main.pdf|907,898|5ab63efa76eab79fc4f3|RENDERED_PUBLISHABLE|
|2|workspace/research/ai-storage-supply-chain-20260623/main.tex|main.tex|4,945|90d28bf95a2851b5233d|DERIVED_WRITE|
|3|workspace/research/ai-storage-supply-chain-20260623/sections/ch01_ic_summary.tex|ch01_ic_summary.tex|13,913|c86b1ec58124c7d0053f|DERIVED_WRITE|
|4|workspace/research/ai-storage-supply-chain-20260623/sections/ch02_executive_summary.tex|ch02_executive_summary.tex|13,060|2b9917a158811b0d7460|DERIVED_WRITE|
|5|workspace/research/ai-storage-supply-chain-20260623/sections/ch08_valuation.tex|ch08_valuation.tex|15,365|29e5cd0c51d5db6a8083|DERIVED_WRITE|
|6|workspace/research/ai-storage-supply-chain-20260623/sections/ch11_investment_reco.tex|ch11_investment_reco.tex|9,951|7b35f4b6ceb6c53f9796|DERIVED_WRITE|
|7|workspace/research/ai-storage-supply-chain-20260623/sections/app_sources_audit.tex|app_sources_audit.tex|9,849|305e189e5fa195949fd3|DERIVED_WRITE|
|8|workspace/research/ai-storage-supply-chain-20260623/data/source_registry.md|source_registry.md|18,907|5ac7e2cd523780929138|DERIVED_CORE|
|9|workspace/research/ai-storage-supply-chain-20260623/data/source_registry.json|source_registry.json|34,497|04350d570b68c1f49b62|DERIVED_CORE|
|10|workspace/research/ai-storage-supply-chain-20260623/data/claim_audit.md|claim_audit.md|22,333|52cfc83a0cc041384382|DERIVED_CORE|
|11|workspace/research/ai-storage-supply-chain-20260623/data/root_artifact_inventory_20260623.md|root_artifact_inventory_20260623.md|1,261|c3694ca6a3e713164866|DERIVED_GOVERNANCE|
|12|workspace/research/ai-storage-supply-chain-20260623/data/root_artifact_inventory_20260623.json|root_artifact_inventory_20260623.json|3,661|2c78e87c56f293afbd07|DERIVED_GOVERNANCE|
|13|workspace/research/ai-storage-supply-chain-20260623/completion_audit_manifest.md|completion_audit_manifest.md|623|b7a33646320712aa77ea|DERIVED_GATE|
|14|workspace/research/ai-storage-supply-chain-20260623/completion_audit_manifest.json|completion_audit_manifest.json|2,419|730d725f766c2500f590|DERIVED_GATE|

## 汇总

- 工件数：14（目标 14）
- 合计字节：1,058,682
- stage：final（post Verifier Run-1，已吸收 manifest 自写回 SHA 变异）

> SHA-256 = sha256sum(file)；字节数 = stat.st_size；last_modified = 磁盘 mtime。
