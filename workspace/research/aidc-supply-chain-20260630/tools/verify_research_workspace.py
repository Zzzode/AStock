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
    "data/valuation_triage_20260630.json",
    "data/valuation_triage_20260630.md",
    "data/core_candidate_valuation_disposition_20260630.json",
    "data/core_candidate_valuation_disposition_20260630.md",
    "data/core_candidate_extended_market_financials_20260701.json",
    "data/core_candidate_extended_broker_consensus_20260701.json",
    "data/core_candidate_extended_valuation_model_20260701.json",
    "data/combined_target_valuation_model_20260701.json",
    "data/combined_target_valuation_model_20260701.md",
    "data/combined_broker_street_coverage_20260701.json",
    "data/combined_broker_street_coverage_20260701.md",
    "data/valuation_quality_audit_20260701.json",
    "data/valuation_quality_audit_20260701.md",
    "data/proxy_field_official_filing_collection_20260701.json",
    "data/proxy_field_official_filing_collection_20260701.md",
    "data/residual_proxy_field_audit_20260701.json",
    "data/residual_proxy_field_audit_20260701.md",
    "data/field_evidence_completion_20260701.json",
    "data/field_evidence_completion_20260701.md",
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
    "analysis/core_candidate_company_cards.md",
    "analysis/core_candidate_extended_valuation_model.md",
    "analysis/field_evidence_completion_audit.md",
    "analysis/residual_proxy_field_audit.md",
    "analysis/valuation_coverage_reconciliation.md",
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

def current_pdf_page_count(default: int = 0) -> int:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return default
    try:
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return default
    m = re.search(r"Pages:\s+(\d+)", out.stdout)
    return int(m.group(1)) if m else default

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
    relationships = data.get("relationships", [])
    required_fields = {
        "ticker",
        "company",
        "chain_layer",
        "node_type",
        "downstream_customer_or_platform",
        "relationship_type",
        "source_tier",
        "evidence_score",
        "revenue_exposure",
        "capacity_or_certification",
        "order_visibility",
        "ASP_or_price_proxy",
        "utilization_or_yield",
        "valuation_eligibility",
        "downgrade_trigger",
    }
    missing = [
        row.get("company", "<missing>")
        for row in relationships
        if required_fields - set(row.keys())
    ]
    return len(relationships) >= 58 and not missing, f"relationships={len(relationships)} missing_schema={len(missing)}"

def customer_chain_audit_count() -> tuple[bool, str]:
    data = json.loads(text("data/customer_chain_audit.json"))
    audits = data.get("audits", [])
    required_fields = {
        "ticker",
        "company",
        "customer_or_platform",
        "product_or_process",
        "certification_status",
        "order_or_backlog",
        "ASP_or_price_proxy",
        "capacity",
        "utilization_or_yield",
        "revenue_exposure",
        "margin_impact",
        "source_tier",
        "evidence_score",
        "source",
        "evidence_gap",
        "blocks_valuation",
        "downgrade_trigger",
        "adopted_wording",
    }
    missing = [
        row.get("company", "<missing>")
        for row in audits
        if required_fields - set(row.keys())
    ]
    target_rows = [
        row
        for row in audits
        if row.get("claim_type") in {"target_model_customer_chain", "extended_target_model_customer_chain", "extended_house_fair_value_customer_chain", "extended_ps_sotp_customer_chain"}
    ]
    blocked_targets = [
        row.get("company", "<missing>")
        for row in target_rows
        if row.get("blocks_valuation") is True
    ]
    return (
        len(audits) >= 58
        and len(target_rows) >= 31
        and not blocked_targets
        and not missing
    ), f"audits={len(audits)} target_rows={len(target_rows)} blocked_targets={len(blocked_targets)} missing_schema={len(missing)}"

def field_evidence_completion_count() -> tuple[bool, str]:
    data = json.loads(text("data/field_evidence_completion_20260701.json"))
    rows = data.get("rows", [])
    metadata = data.get("metadata", {})
    fields = (
        "revenue_exposure",
        "customer_or_platform",
        "order_or_backlog",
        "capacity_or_certification",
        "asp_or_price_proxy",
        "utilization_or_yield",
        "margin_impact",
    )
    missing_schema = []
    unresolved_target = []
    for row in rows:
        cells = row.get("fields", {})
        if set(fields) - set(cells.keys()):
            missing_schema.append(row.get("ticker", "<missing>"))
        if row.get("target_model"):
            for field in fields:
                status = cells.get(field, {}).get("status")
                if status in {"source_exhausted", "watchlist_blocked", None}:
                    unresolved_target.append(f"{row.get('ticker')}:{field}")
    total_cells = int(metadata.get("total_field_cells") or 0)
    return (
        len(rows) >= 59
        and total_cells >= len(rows) * len(fields)
        and not missing_schema
        and not unresolved_target
    ), f"rows={len(rows)} cells={total_cells} missing_schema={len(missing_schema)} unresolved_target={len(unresolved_target)} statuses={metadata.get('status_counts')}"

def residual_proxy_field_audit_count() -> tuple[bool, str]:
    field_data = json.loads(text("data/field_evidence_completion_20260701.json"))
    proxy_cells = []
    for row in field_data.get("rows", []):
        for field, cell in row.get("fields", {}).items():
            if isinstance(cell, dict) and cell.get("status") == "proxy":
                proxy_cells.append((str(row.get("ticker")), field))
    audit = json.loads(text("data/residual_proxy_field_audit_20260701.json"))
    rows = audit.get("rows", [])
    covered = {(str(row.get("ticker")), str(row.get("field"))) for row in rows}
    missing = [f"{ticker}:{field}" for ticker, field in proxy_cells if (ticker, field) not in covered]
    shallow = [
        f"{row.get('ticker')}:{row.get('field')}"
        for row in rows
        if not row.get("remaining_gap") or not row.get("valuation_consequence") or not row.get("next_verification_path")
    ]
    return (
        len(rows) == len(proxy_cells)
        and not missing
        and not shallow
    ), f"proxy_cells={len(proxy_cells)} audit_rows={len(rows)} missing={missing[:5]} shallow={shallow[:5]}"

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

def extended_core_model_count() -> tuple[bool, str]:
    data = json.loads(text("data/core_candidate_extended_valuation_model_20260701.json"))
    rows = data.get("rows", [])
    target_ready_statuses = {"target_model_ready", "house_target_model_ready", "ps_sotp_target_model_ready"}
    target_ready = [row for row in rows if row.get("publication_status") in target_ready_statuses]
    explicit = [row for row in rows if row.get("publication_status") == "target_model_ready"]
    house = [row for row in rows if row.get("publication_status") == "house_target_model_ready"]
    ps_sotp = [row for row in rows if row.get("publication_status") == "ps_sotp_target_model_ready"]
    no_street = [row for row in rows if row.get("publication_status") == "financial_model_ready_no_street_anchor"]
    watchlist = [row for row in rows if row.get("publication_status") == "watchlist_only_insufficient_model"]
    missing = [
        row.get("company", "<missing>")
        for row in rows
        if not row.get("current_price") or not row.get("publication_status") or not row.get("company_specific_disposition")
    ]
    return (
        len(rows) == 41 and len(target_ready) == 38 and len(explicit) == 13 and len(house) == 24 and len(ps_sotp) == 1 and len(no_street) == 0 and len(watchlist) == 3 and not missing
    ), f"extended_rows={len(rows)} target_ready={len(target_ready)} explicit={len(explicit)} house={len(house)} ps_sotp={len(ps_sotp)} no_street={len(no_street)} watchlist={len(watchlist)} missing={len(missing)}"

def valuation_specific_gate() -> tuple[bool, str]:
    combined = json.loads(text("data/combined_target_valuation_model_20260701.json"))
    broker = json.loads(text("data/combined_broker_street_coverage_20260701.json"))
    quality = json.loads(text("data/valuation_quality_audit_20260701.json"))
    rows = combined.get("rows", [])
    broker_rows = broker.get("rows", [])
    ch07 = text("sections/ch07_valuation.tex")
    financial_failures = []
    for row in rows:
        revenue = row.get("revenue_2026e_100mn")
        profit = row.get("np_2026e_100mn")
        eps = row.get("eps_2026e")
        shares = row.get("shares_100mn")
        if isinstance(revenue, (int, float)) and isinstance(profit, (int, float)) and revenue > 0 and profit / revenue > 0.75:
            financial_failures.append(f"{row.get('ticker')}:margin")
        if isinstance(profit, (int, float)) and isinstance(eps, (int, float)) and isinstance(shares, (int, float)) and shares > 0:
            expected_eps = profit / shares
            if abs(expected_eps - eps) > max(0.15, abs(eps) * 0.25):
                financial_failures.append(f"{row.get('ticker')}:eps")
    required_ch07_terms = (
        "统一",
        "隐含预期",
        "明示目标价",
        "forecast-only",
        "zero-weight",
        "链条语义匹配",
        "汉钟精机",
    )
    missing_terms = [term for term in required_ch07_terms if term not in ch07]
    bad_threshold = any(
        "中科曙光" in line
        and ("CDU" in line or "冷板" in line or "Manifold" in line)
        and "不是" not in line
        and "而不是" not in line
        for line in ch07.splitlines()
    )
    return (
        len(rows) == 56
        and len(broker_rows) == 56
        and quality.get("status") == "PASS"
        and not financial_failures
        and not missing_terms
        and "可发布目标价/公允价值组合 & 55" not in ch07
        and not bad_threshold
    ), f"rows={len(rows)} broker_rows={len(broker_rows)} quality={quality.get('status')} financial_failures={financial_failures[:5]} missing_terms={missing_terms} bad_threshold={bad_threshold}"

def valuation_chapter_visual_layout() -> tuple[bool, str]:
    ch07 = text("sections/ch07_valuation.tex")
    required = [
        "估值数值明细",
        "方法、证据与外部锚",
        "催化与失效条件",
        "Broker/Street 明细",
        "目标超出情景区间",
    ]
    banned = [
        r"L{0.92cm}L{1.25cm}L{1.35cm}R{0.78cm}",
        "final\\_target\\_outside\\_scenario\\_guardrail",
        "explicit\\_target\\_price\\_anchor",
        "forecast\\_only\\_no\\_target",
        "official\\_filing\\_no\\_broker\\_target",
        "original\\_public\\_broker\\_pdf",
        "EPS 1.3400000000",
    ]
    missing = [term for term in required if term not in ch07]
    raw_hits = [term for term in banned if term in ch07]
    return not missing and not raw_hits, f"missing={missing} raw_hits={raw_hits}"

def valuation_triage_count() -> tuple[bool, str]:
    data = json.loads(text("data/valuation_triage_20260630.json"))
    rows = data.get("rows", [])
    missing = [
        row.get("company", "<missing>")
        for row in rows
        if not row.get("valuation_disposition") or not row.get("target_price_status")
    ]
    return len(rows) >= 173 and not missing, f"triage_rows={len(rows)} missing_disposition={len(missing)}"

def core_candidate_count() -> tuple[bool, str]:
    data = json.loads(text("data/core_candidate_valuation_disposition_20260630.json"))
    rows = data.get("rows", [])
    missing = [
        row.get("company", "<missing>")
        for row in rows
        if not row.get("candidate_method") or not row.get("valuation_disposition") or not row.get("residual_proxy_boundary") or not row.get("upgrade_trigger")
    ]
    return len(rows) >= 58 and not missing, f"core_candidates={len(rows)} missing_fields={len(missing)}"

def growth_count() -> tuple[bool, str]:
    data = json.loads(text("data/growth_driver_model.json"))
    drivers = data.get("drivers", [])
    required_fields = {
        "growth_segment_revenue",
        "unit_volume_or_proxy",
        "ASP_or_price",
        "value_amount_or_proxy",
        "supply_demand_state",
        "capacity_or_utilization",
        "certification_or_customer_qualification",
        "recognized_revenue_ratio",
        "incremental_opex",
        "growth_gross_profit_100mn",
        "growth_net_profit_100mn",
        "growth_EPS",
        "current_price_implied_growth",
        "next_quarter_validation_threshold",
    }
    missing = [
        row.get("company", "<missing>")
        for row in drivers
        if required_fields - set(row.keys())
    ]
    return len(drivers) == 18 and not missing, f"drivers={len(drivers)} missing_schema={len(missing)}"

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

def no_generic_valuation_placeholders() -> tuple[bool, str]:
    body = text("main_current_text.txt")
    banned = [
        "核心候选" + "，暂列观察",
        "补齐" + "官方收入拆分",
        "产能利用率、" + "ASP 或毛利证据后，才可升级",
        "评级仍取决于后续订单",
        "多数公司" + "未披露 AI 订单",
        "只有当产品、客户/平台认证、订单或项目交付、ASP/价格代理、产能利用率和毛利率形成闭环，才可以进入目标价模型",
    ]
    hits = [item for item in banned if item in body]
    return not hits, "generic valuation placeholder hits=" + ",".join(hits)

def source_files() -> tuple[bool, str]:
    files = list((BASE / "sources" / "public-web-20260630").glob("*"))
    return len(files) >= 40, f"source_files={len(files)}"

def rendered_pages() -> tuple[bool, str]:
    files = list((BASE / "rendered" / "current-20260630").glob("page-*.png"))
    return len(files) >= 3, f"rendered_pages={len(files)}"

checks = []
for path in REQUIRED:
    checks.append((f"exists:{path}", lambda p=path: exists(p)))
checks += [
    ("pdf_pages", pdf_pages),
    ("source_count", source_count),
    ("relationship_count", relationship_count),
    ("customer_chain_audit_count", customer_chain_audit_count),
    ("field_evidence_completion_count", field_evidence_completion_count),
    ("residual_proxy_field_audit_count", residual_proxy_field_audit_count),
    ("full_chain_count", full_chain_count),
    ("full_chain_blocks", full_chain_blocks),
    ("valuation_count", valuation_count),
    ("extended_core_model_count", extended_core_model_count),
    ("valuation_specific_gate", valuation_specific_gate),
    ("valuation_chapter_visual_layout", valuation_chapter_visual_layout),
    ("valuation_triage_count", valuation_triage_count),
    ("core_candidate_count", core_candidate_count),
    ("growth_count", growth_count),
    ("no_ascii_diagram", no_ascii_diagram),
    ("mermaid", mermaid),
    ("chinese_text", chinese_text),
    ("no_unfinished", no_unfinished),
    ("no_generic_valuation_placeholders", no_generic_valuation_placeholders),
    ("source_files", source_files),
    ("rendered_pages", rendered_pages),
]

expected = len(checks)

failures = []
for name, fn in checks:
    ok, detail = fn()
    status = "PASS" if ok else "FAIL"
    print(f"{status} {name}: {detail}")
    if not ok:
        failures.append(name)
print(f"SUMMARY: {expected - len(failures)} PASS / {len(failures)} FAIL")
raise SystemExit(1 if failures else 0)
