#!/usr/bin/env python3
# R237 Stage 参数化 checksums 刷新脚本：14core双后缀 + 6twins双后缀
import hashlib, json, sys
from pathlib import Path
CASE=Path(sys.argv[1]); STAGE=sys.argv[2]; ROUND=sys.argv[3]
DATA=CASE/"data"
ARTS=["main.pdf","main.tex","main_current_text.txt","research_brief.md","review_log.md","visual_review.md","data/raw_financials.md","data/report_catalog.md","data/consensus_analysis_raw.md","data/source_registry.md","data/source_registry.json","data/claim_audit.md","completion_audit_manifest.md","completion_audit_manifest.json"]
def sh(p): b=p.read_bytes(); return hashlib.sha256(b).hexdigest(), len(b)
its=[]
for r in ARTS:
    p=CASE/r; s,z=sh(p)
    if "raw" in r or "report_catalog" in r or "consensus" in r: cat="data_raw"
    elif "source" in r or "claim" in r or "manifest" in r: cat="governance"
    else: cat="core_output"
    its.append({"path":f"workspace/research/ai-storage-supply-chain-20260623/{r}","filename":p.name,"sha256":s,"sha256_short":s[:12],"size_bytes":z,"category":cat})
obj={"schema_version":"1.0","case":"ai-storage-supply-chain-20260623","polling_round":f"R{ROUND}","generated_by":STAGE,"total_files":len(its),"files":its}
jt=json.dumps(obj, ensure_ascii=False, indent=2)+"\n"
rows="\n".join([f"|{i+1}|{a['filename']}|`{a['sha256_short']}`|{a['size_bytes']:,}|{a['category']}|" for i,a in enumerate(its)])
md=f"# AI 存储产业链 · 核心工件校验和（R{ROUND} · {len(its)} files）\n\n> Stage={STAGE} · SHA三相闭环中。双后缀 20260623（硬编码锚）+ 20260624（当日归档）。\n\n|#|文件名|SHA-256[:12]|字节数|分类|\n|---|---|---|---|---|\n{rows}\n"
for s in ("20260623","20260624"):
    (DATA/f"core_artifact_checksums_{s}.json").write_text(jt, encoding="utf-8")
    (DATA/f"core_artifact_checksums_{s}.md").write_text(md, encoding="utf-8")
# 6 twins
TW=[("root_artifact_inventory",ARTS),("top_level_data_artifact_inventory",[a for a in ARTS if a.count("/")==0]),("source_artifact_inventory",[a for a in ARTS if "source_registry" in a or "claim_audit" in a]),("rendered_artifact_inventory",["main.pdf","main.tex","main_current_text.txt","visual_review.md"]),("raw_data_artifact_inventory",["data/raw_financials.md","data/report_catalog.md","data/consensus_analysis_raw.md"]),("completion_audit_manifest_twin",["completion_audit_manifest.md","completion_audit_manifest.json"])]
for name,rels in TW:
    ti=[]
    for r in rels:
        p=CASE/r; s,z=sh(p); ti.append({"path":f"workspace/research/ai-storage-supply-chain-20260623/{r}","filename":p.name,"sha256":s,"sha256_short":s[:12],"size_bytes":z})
    for s in ("20260623","20260624"):
        (DATA/f"{name}_{s}.json").write_text(json.dumps({"schema_version":"1.0","polling_round":f"R{ROUND}","inventory_type":name,"total_files":len(ti),"files":ti}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        tbl="\n".join([f"|{i+1}|{t['filename']}|`{t['sha256_short']}`|{t['size_bytes']:,}|" for i,t in enumerate(ti)])
        (DATA/f"{name}_{s}.md").write_text(f"# {name.replace('_',' ').title()}（R{ROUND} · {len(ti)} files）\n\n|#|工件|SHA-256[:12]|字节数|\n|---|---|---|---|\n{tbl}\n", encoding="utf-8")
print(f"[R{ROUND} stage={STAGE}] 14core×2 + 6twins×2 刷完 ✓")
