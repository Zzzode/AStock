from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

REQUIRED = [
    "research_brief.md",
    "main.tex",
    "main.pdf",
    "main_current_text.txt",
    "review_log.md",
    "sections/ch09_full_chain.tex",
    "data/raw_market_financials_20260630.json",
    "data/raw_market_data.md",
    "data/raw_financials.md",
    "data/verified_market_data.md",
    "data/verified_financials.md",
    "data/source_registry.md",
    "data/source_registry.json",
    "data/claim_audit.md",
    "data/claim_audit.json",
    "data/supply_chain_relationships.md",
    "data/supply_chain_relationships.json",
    "data/customer_chain_audit.md",
    "data/customer_chain_audit.json",
    "data/full_chain_universe_20260630.md",
    "data/full_chain_universe_20260630.json",
    "data/growth_driver_model.json",
    "data/current_valuation_model_20260630.json",
    "data/current_valuation_model_20260630.md",
    "data/consensus_analysis.md",
    "analysis/full_chain_taxonomy.md",
    "analysis/agent_research_synthesis.md",
    "analysis/template_brief.md",
    "analysis/industry_landscape.md",
    "analysis/supply_chain_model.md",
    "analysis/company_fundamental_cards.md",
    "analysis/chain_earnings_bridge.md",
    "analysis/growth_earnings_model.md",
    "analysis/segment_forecast_bridge.md",
    "analysis/implied_growth_sensitivity.md",
    "analysis/valuation_model.md",
    "analysis/valuation_audit.md",
    "analysis/risk_framework.md",
    "analysis/house_view.md",
    "analysis/exhibit_plan.md",
    "analysis/aidc_chain_map.mmd",
    "sections/ch01_dashboard.tex",
    "sections/ch02_evidence.tex",
    "sections/ch03_industry.tex",
    "sections/ch04_supply_chain.tex",
    "sections/ch05_companies.tex",
    "sections/ch06_sentiment.tex",
    "sections/ch07_valuation.tex",
    "sections/ch08_risks.tex",
    "sections/app_source_audit.tex",
    "sections/app_model_disclosure.tex",
]

def text(path: str) -> str:
    return (BASE / path).read_text(encoding="utf-8")

def exists(path: str) -> tuple[bool, str]:
    p = BASE / path
    return p.exists() and p.stat().st_size > 0, path

def pdf_pages() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=20)
    m = re.search(r"Pages:\s+(\d+)", out.stdout)
    if not m:
        return False, "pdfinfo missing Pages"
    pages = int(m.group(1))
    return pages >= 18, f"pages={pages}"

def source_count() -> tuple[bool, str]:
    data = json.loads(text("data/source_registry.json"))
    return len(data.get("sources", [])) >= 30, f"sources={len(data.get('sources', []))}"

def relationship_count() -> tuple[bool, str]:
    data = json.loads(text("data/supply_chain_relationships.json"))
    return len(data.get("relationships", [])) == 18, f"relationships={len(data.get('relationships', []))}"

def full_chain_count() -> tuple[bool, str]:
    data = json.loads(text("data/full_chain_universe_20260630.json"))
    return len(data.get("rows", [])) >= 80, f"full_chain_rows={len(data.get('rows', []))}"

def full_chain_blocks() -> tuple[bool, str]:
    data = json.loads(text("data/full_chain_universe_20260630.json"))
    blocks = {row.get("chain_block") for row in data.get("rows", [])}
    return len(blocks) == 8, f"blocks={len(blocks)}"

def valuation_count() -> tuple[bool, str]:
    data = json.loads(text("data/current_valuation_model_20260630.json"))
    return len(data.get("rows", [])) == 18, f"valuations={len(data.get('rows', []))}"

def growth_count() -> tuple[bool, str]:
    data = json.loads(text("data/growth_driver_model.json"))
    return len(data.get("drivers", [])) == 18, f"drivers={len(data.get('drivers', []))}"

def no_ascii_diagram() -> tuple[bool, str]:
    forbidden = ["+---", "|---+", "---->", "<----"]
    body = text("main_current_text.txt") if (BASE / "main_current_text.txt").exists() else text("main.tex")
    return not any(token in body for token in forbidden), "no ASCII architecture diagram"

def mermaid() -> tuple[bool, str]:
    body = text("analysis/aidc_chain_map.mmd")
    return "flowchart LR" in body and "AIDC" in body, "Mermaid flowchart"

def chinese_text() -> tuple[bool, str]:
    body = text("main_current_text.txt")
    return "投资委员会概要" in body and "全产业链" in body and "估值模型" in body and "风险" in body, "Chinese sections extracted"

def no_unfinished() -> tuple[bool, str]:
    body = text("main_current_text.txt")
    bad = ["TODO", "PLACEHOLDER", "<Report Title>", "??"]
    return not any(x in body for x in bad), "no unfinished markers"

def source_files() -> tuple[bool, str]:
    files = list((BASE / "sources" / "public-web-20260630").glob("*"))
    return len(files) >= 40, f"source_files={len(files)}"

def rendered_pages() -> tuple[bool, str]:
    files = list((BASE / "rendered" / "current-20260630").glob("page-*.png"))
    return len(files) >= 3, f"rendered_pages={len(files)}"

checks = []
for path in REQUIRED[:23]:
    checks.append((f"exists:{path}", lambda p=path: exists(p)))
checks += [
    ("pdf_pages", pdf_pages),
    ("source_count", source_count),
    ("relationship_count", relationship_count),
    ("full_chain_count", full_chain_count),
    ("full_chain_blocks", full_chain_blocks),
    ("valuation_count", valuation_count),
    ("growth_count", growth_count),
    ("no_ascii_diagram", no_ascii_diagram),
    ("mermaid", mermaid),
    ("chinese_text", chinese_text),
    ("no_unfinished", no_unfinished),
    ("source_files", source_files),
    ("rendered_pages", rendered_pages),
]
for path in REQUIRED[23:26]:
    checks.append((f"exists:{path}", lambda p=path: exists(p)))

if len(checks) != 39:
    raise SystemExit(f"Verifier definition error: expected 39 checks, got {len(checks)}")

failures = []
for name, fn in checks:
    ok, detail = fn()
    status = "PASS" if ok else "FAIL"
    print(f"{status} {name}: {detail}")
    if not ok:
        failures.append(name)
print(f"SUMMARY: {39 - len(failures)} PASS / {len(failures)} FAIL")
raise SystemExit(1 if failures else 0)
