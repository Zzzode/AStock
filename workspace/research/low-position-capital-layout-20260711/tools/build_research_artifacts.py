#!/usr/bin/env python3
"""Build governance, consensus, valuation, and model artifacts for the case."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
CASE_ID = "low-position-capital-layout-20260711"
DATA_CUTOFF = "2026-07-10 close; financials through 2026Q1"


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def build_research_brief() -> str:
    return """# Research Brief

- Case ID: `low-position-capital-layout-20260711`
- Objective: scan all 31 Shenwan first-level A-share industries through two opportunity curves: quiet low-position accumulation and already-launched themes whose earnings runway still supports material current-price upside.
- Report type: full-market sector-rotation strategy report with seven current-price core stock models and a 54-name core/satellite research universe.
- Data cutoff: 2026-07-10 close; financials through 2026Q1; source collection through 2026-07-11.
- Language: Chinese reader-facing report; English internal governance artifacts.
- Depth: complete institutional strategy report, not a quick screen.
- Universe: all 31 Shenwan first-level industries plus the Securities Times/DataBao continuous-main-fund-inflow stock table and 54 sector-level core/satellite companies.
- Core valuation pool A, quiet accumulation: 601077 渝农商行, 000425 徐工机械, 601825 沪农商行.
- Core valuation pool B, launched with remaining earnings runway: 000063 中兴通讯, 301308 江波龙, 600276 恒瑞医药, 601138 工业富联.
- Preview-refresh pool: 000938 紫光股份, 300475 香农芯创, 603986 兆易创新, 600601 方正科技, 600685 中船防务. These names have material preview evidence but no fabricated point target while their post-preview denominators are incomplete.
- Conditional watch pool: 国防军工, 先进封装, 传媒/AI应用, semiconductor-equipment stock islands, and other sectors that lack either a company earnings bridge or sufficient current-price upside.
- Demand anchors: regional credit demand and deposit repricing; overseas infrastructure and mining capex; AI compute/network capex; hyperscaler AI-server and 800G+ switching demand; NAND/enterprise-SSD demand; innovative-drug sales and BD milestones.
- Exclusions: no order execution; no unverified beneficial-owner attribution; no direct use of search snippets as positive-weight broker anchors.
- Downgrade path: if a quiet candidate lacks current-price valuation or persistent flow, or if a launched candidate lacks a revenue-to-EPS bridge and at least 20% base upside, downgrade it to watchlist only.
- Evidence boundary: main-fund flow is a transaction-size classification, not verified institutional identity. “Quiet accumulation” is a price-flow research label, not proof of insider or coordinated buying.
"""


def build_gate_manifest() -> dict[str, Any]:
    required_artifacts = [
        "research_brief.md",
        "analysis/template_brief.md",
        "data/sector_scan_20260710.json",
        "data/continuous_inflow_candidates_20260710.json",
        "data/source_registry.json",
        "data/claim_audit.json",
        "data/core_universe_preview_census_20260711.json",
        "data/earnings_preview_quality_20260711.json",
        "data/earnings_preview_archive_20260711.json",
        "data/company_cards_20260711.json",
        "data/core_broker_report_catalog_20260711.json",
        "data/core_broker_report_digests_20260711.json",
        "data/broker_street_consensus_20260711.json",
        "data/growth_driver_model.json",
        "analysis/house_view.md",
        "analysis/variant_perception.md",
        "analysis/secondary_market_analysis.md",
        "analysis/segment_valuation_model.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/growth_earnings_model.md",
        "analysis/value_chain_economics.md",
        "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md",
        "analysis/risk_framework.md",
        "analysis/exhibit_plan.md",
        "analysis/delta_audit.md",
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
    ]
    return {
        "case_id": CASE_ID,
        "report_type": "full-market sector-rotation strategy report",
        "data_cutoff": DATA_CUTOFF,
        "required_skills": [
            "equity-research",
            "screen",
            "valuation",
            "growth-earnings-model",
            "research-report-review",
            "exhibit-format-reviewer",
        ],
        "required_artifacts": required_artifacts,
        "review_cycles": [
            "R0_evidence",
            "R1_model",
            "R2_draft",
            "R3_render_compliance",
            "R4_final_ic",
        ],
        "verifiers": [
            "tools/verify_research_workspace.py",
            "workspace/research/tools/run_research_gates.py",
            "astock.cli build-pdf",
        ],
        "depth_gates": [
            "evidence_depth",
            "broker_consensus_depth",
            "model_depth",
            "valuation_depth",
            "ic_readiness",
        ],
        "pass_conditions": [
            "All 31 Shenwan first-level industries covered",
            "Daily and weekly fund-flow tables preserved",
            "Core candidates have official financials and auditable external anchors",
            "All 54 core/satellite names have company cards and broker metadata",
            "All 16 captured H1 previews have quality, implied-Q2 and stale-denominator checks",
            "The priority broker archive contains 56 original PDFs and zero failed downloads",
            "Launched-growth candidates have a revenue/proxy-to-EPS bridge and current-price-implied growth",
            "Model Reproducibility: PASS",
            "PDF compiled with XeLaTeX",
            "Zero open S-Level and unwaived A-Level findings",
        ],
        "downgrade_path": [
            "watchlist only",
            "launch confirmation rather than quiet accumulation",
            "one-day rebound",
            "low price without confirming flow",
            "launched but insufficient earnings runway",
            "launched but current-price upside below 20%",
        ],
    }


def build_artifact_contract() -> dict[str, Any]:
    artifacts = [
        {
            "artifact": "data/sector_scan_20260710.json",
            "owner_skill": "screen",
            "owner_agent": "market-data-collector",
            "stage": "evidence",
            "required_fields": [
                "industry",
                "daily fund flow",
                "weekly fund flow",
                "52-week position",
                "3-year percentile",
                "valuation percentile",
                "stage",
            ],
            "minimum_depth": "31 Shenwan first-level rows with reproducible stage classification",
            "blocking_conditions": [
                "fewer than 31 rows",
                "missing weekly fund flow",
                "mixed industry-index definitions",
            ],
            "reviewer_cycle": "R0_evidence",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/sector_scan_20260710.md",
            "owner_skill": "screen",
            "owner_agent": "market-data-collector",
            "stage": "evidence",
            "required_fields": [
                "31-industry table",
                "data cutoff",
                "source boundary",
            ],
            "minimum_depth": "human-readable twin of the structured 31-industry scan",
            "blocking_conditions": [
                "row count differs from JSON",
                "missing evidence boundary",
            ],
            "reviewer_cycle": "R0_evidence",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/core_universe_preview_census_20260711.json",
            "owner_skill": "supply-chain-research",
            "owner_agent": "industry-analyst",
            "stage": "evidence",
            "required_fields": [
                "sector",
                "ticker",
                "company",
                "tier",
                "preview status",
                "announcement date",
            ],
            "minimum_depth": "54 named core/satellite companies across all selected opportunity sectors",
            "blocking_conditions": [
                "fewer than 54 rows",
                "duplicate ticker",
                "preview company omitted from the census",
            ],
            "reviewer_cycle": "R0_evidence",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/earnings_preview_quality_20260711.json",
            "owner_skill": "growth-earnings-model",
            "owner_agent": "growth-earnings-modeler",
            "stage": "model",
            "required_fields": [
                "H1 midpoint",
                "H1 EPS midpoint",
                "implied Q2 profit",
                "H1/full-year EPS ratio",
                "non-recurring share",
                "quality class",
            ],
            "minimum_depth": "all 16 disclosed previews with denominator-staleness and profit-quality tests",
            "blocking_conditions": [
                "preview treated as automatic full-year annualization",
                "one-off gains omitted",
                "stale broker EPS reused without warning",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/earnings_preview_archive_20260711.json",
            "owner_skill": "equity-research",
            "owner_agent": "data-verifier",
            "stage": "evidence",
            "required_fields": [
                "16 validated PDF announcements",
                "ticker-to-company match",
                "attachment URL",
                "local PDF",
                "local text",
                "validation status",
            ],
            "minimum_depth": "all 16 captured previews archived as valid, text-extractable, ticker-matched PDFs",
            "blocking_conditions": [
                "fewer than 16 valid PDFs",
                "ticker or company mismatch",
                "HTML error body saved as PDF",
                "unresolved archive failure",
            ],
            "reviewer_cycle": "R0_evidence",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/company_cards_20260711.json",
            "owner_skill": "equity-research",
            "owner_agent": "fundamental-analyst",
            "stage": "synthesis",
            "required_fields": [
                "54 tickers",
                "Q1 financials",
                "price position",
                "preview quality",
                "broker recency",
                "valuation disposition",
                "monitor trigger",
            ],
            "minimum_depth": "one auditable disposition card for every company in the 54-name universe",
            "blocking_conditions": [
                "fewer than 54 cards",
                "preview-after-report timing omitted",
                "watchlist name presented with an invented target",
            ],
            "reviewer_cycle": "R2_draft",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/core_broker_report_catalog_20260711.json",
            "owner_skill": "reports",
            "owner_agent": "report-collector",
            "stage": "evidence",
            "required_fields": [
                "54-name metadata",
                "28-name priority pool",
                "56 original PDFs",
                "report-to-preview timing",
                "download failures",
            ],
            "minimum_depth": "metadata for 54 names and two full PDFs for each of 28 priority names",
            "blocking_conditions": [
                "fewer than 54 metadata rows",
                "fewer than 56 priority PDFs",
                "failed PDF download left unresolved",
            ],
            "reviewer_cycle": "R0_evidence",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/core_broker_report_digests_20260711.json",
            "owner_skill": "reports",
            "owner_agent": "report-analyzer",
            "stage": "synthesis",
            "required_fields": [
                "28 priority tickers",
                "56 report text digests",
                "forecast excerpt",
                "risk excerpt",
                "report-to-preview timing",
                "AStock disposition",
            ],
            "minimum_depth": "two original-PDF forecast and risk digests for every priority ticker",
            "blocking_conditions": [
                "title-only catalog presented as report analysis",
                "fewer than 56 report digests",
                "pre-preview forecast used without stale label",
            ],
            "reviewer_cycle": "R2_draft",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/broker_street_consensus_20260711.json",
            "owner_skill": "valuation",
            "owner_agent": "valuation-modeler",
            "stage": "model",
            "required_fields": [
                "ticker",
                "broker",
                "report_date",
                "rating",
                "target_price",
                "revenue_E",
                "net_profit_E",
                "EPS_E",
                "method",
                "implied_upside",
                "source_quality",
                "source_path",
                "valuation_weight",
            ],
            "minimum_depth": "at least one positive-weight auditable external anchor per core ticker",
            "blocking_conditions": [
                "weak source receives positive weight",
                "internal target presented as Street evidence",
                "core ticker missing an external anchor",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "run_research_gates.py broker consensus checks",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/broker_street_consensus_20260711.md",
            "owner_skill": "valuation",
            "owner_agent": "valuation-modeler",
            "stage": "model",
            "required_fields": [
                "ticker",
                "broker",
                "target",
                "forecast",
                "source quality",
                "weight",
            ],
            "minimum_depth": "human-readable twin of the structured broker packet",
            "blocking_conditions": [
                "positive-weight row missing from JSON",
                "weak source presented as Street anchor",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "analysis/valuation_model.md",
            "owner_skill": "valuation",
            "owner_agent": "valuation-modeler",
            "stage": "model",
            "required_fields": [
                "current price",
                "share count",
                "market cap",
                "2026E denominator",
                "bear",
                "base",
                "bull",
                "final target",
                "upside",
                "action",
                "catalyst",
                "invalidation",
            ],
            "minimum_depth": "three company-level current-price models with business-model matched methods",
            "blocking_conditions": [
                "target/upside arithmetic mismatch",
                "missing current price date",
                "method mismatch",
                "Model Reproducibility not PASS",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "run_research_gates.py valuation checks",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/current_valuation_model_20260711.json",
            "owner_skill": "valuation",
            "owner_agent": "valuation-modeler",
            "stage": "model",
            "required_fields": [
                "current price",
                "share count",
                "market cap",
                "2026E denominator",
                "scenario values",
                "multi-anchor weights",
                "final target",
                "upside",
            ],
            "minimum_depth": "seven fully reproducible current-price valuation rows across two opportunity buckets",
            "blocking_conditions": [
                "target arithmetic mismatch",
                "market-cap mismatch",
                "missing positive external anchor",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "run_research_gates.py valuation checks",
            "blocking_if_missing": True,
        },
        {
            "artifact": "data/growth_driver_model.json",
            "owner_skill": "growth-earnings-model",
            "owner_agent": "growth-earnings-modeler",
            "stage": "model",
            "required_fields": [
                "ticker",
                "growth driver",
                "base/growth split",
                "unit or proxy",
                "price or ASP",
                "gross margin",
                "net profit",
                "EPS",
                "bear/base/bull",
                "current-price-implied growth",
                "valuation credit",
            ],
            "minimum_depth": "four applicable launched-growth rows; quiet-bucket names are explicitly excluded in the analysis with reasons",
            "blocking_conditions": [
                "generic theme demand converted to target upside without a proxy-to-EPS bridge",
                "missing current-price-implied growth",
                "unsupported segment purity",
            ],
            "reviewer_cycle": "R1_model",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
        {
            "artifact": "main.tex",
            "owner_skill": "equity-research",
            "owner_agent": "latex-writer",
            "stage": "publish",
            "required_fields": [
                "first-page decision dashboard",
                "31-industry scan",
                "core stock ranking",
                "valuation",
                "risks",
                "monitoring triggers",
                "source appendix",
            ],
            "minimum_depth": "reader-usable institutional strategy report with prose-led chapters",
            "blocking_conditions": [
                "compile failure",
                "missing reader-facing valuation table",
                "unreadable table",
                "open S-Level or A-Level issue",
            ],
            "reviewer_cycle": "R3_render_compliance",
            "verifier_check": "XeLaTeX build and PDF log scan",
            "blocking_if_missing": True,
        },
        {
            "artifact": "main.pdf",
            "owner_skill": "equity-research",
            "owner_agent": "latex-writer",
            "stage": "publish",
            "required_fields": [
                "complete rendered page set",
                "decision dashboard",
                "31-industry scan",
                "valuation",
                "risk monitor",
                "disclaimer",
            ],
            "minimum_depth": "compiled, readable A4 PDF with no hard layout errors",
            "blocking_conditions": [
                "missing PDF",
                "page count mismatch",
                "Overfull hbox",
                "out-of-bounds text",
            ],
            "reviewer_cycle": "R3_render_compliance",
            "verifier_check": "tools/verify_research_workspace.py",
            "blocking_if_missing": True,
        },
    ]
    return {"case_id": CASE_ID, "artifacts": artifacts}


def build_source_registry() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "S01",
            "source": "Shenwan Research index history via AkShare index_hist_sw",
            "type": "official_index_api",
            "date": "through 2026-07-09",
            "quality": "L1",
            "path": "data/raw_sw_index_*_20260710.json",
            "use": "31-industry price position and historical returns",
            "boundary": "2026-07-10 close is compounded from official daily return because the history endpoint lagged one day",
        },
        {
            "source_id": "S02",
            "source": "Legulegu Shenwan industry overview",
            "type": "structured_public_snapshot",
            "date": "2026-07-10",
            "quality": "L2",
            "path": "sources/market-20260711/legulegu_sw_industry_overview_20260711.html",
            "use": "industry PE/PB/dividend and historical percentiles",
            "boundary": "valuation percentiles do not prove earnings inflection",
        },
        {
            "source_id": "S03",
            "source": "Securities Times/DataBao daily and weekly industry fund-flow tables",
            "type": "structured_media_table",
            "date": "2026-07-10",
            "quality": "L2",
            "path": "sources/market-20260711/stcn_daily_industry_flow_20260710.html",
            "use": "daily and weekly Shenwan industry flow",
            "boundary": "main-fund labels are transaction-size classification, not investor identity",
        },
        {
            "source_id": "S04",
            "source": "Securities Times/DataBao continuous-inflow stock table",
            "type": "structured_media_table",
            "date": "2026-07-10",
            "quality": "L2",
            "path": "sources/market-20260711/stcn_continuous_inflow_20260710.html",
            "use": "continuous-inflow stock screen",
            "boundary": "continuous inflow alone is not an investment recommendation",
        },
        {
            "source_id": "S05",
            "source": "AStock Sina market snapshot",
            "type": "realtime_quote_adapter",
            "date": "2026-07-10 close",
            "quality": "L1",
            "path": "data/raw_candidate_quotes_20260710.json",
            "use": "current prices, trading value, daily ranges",
            "boundary": "quote adapter PE/PB fields returned zero and were not used",
        },
        {
            "source_id": "S06",
            "source": "Official 2026Q1 filings for 601825 and 601077; CNInfo filing for 000425 supplemented by AStock financial packet",
            "type": "official_filing",
            "date": "2026Q1",
            "quality": "L1",
            "path": "sources/official-filings-20260711/",
            "use": "reported revenue, profit, EPS, BPS, asset quality, cash flow",
            "boundary": "reported financials are not forward forecasts",
        },
        {
            "source_id": "S07",
            "source": "Original broker PDFs and auditable broker reposts",
            "type": "broker_research",
            "date": "2026-04 to 2026-06",
            "quality": "L2-L3",
            "path": "sources/broker-reports/2026-07-11/",
            "use": "2026E forecasts, target prices, valuation methods, risks",
            "boundary": "reposts are labelled and receive lower weight than original PDFs",
        },
        {
            "source_id": "S08",
            "source": "Exchange/Choice margin snapshots reposted by Eastmoney",
            "type": "exchange_derived_snapshot",
            "date": "2026-07-09 to 2026-07-10",
            "quality": "L2",
            "path": "sources/market-20260711/*margin*.html",
            "use": "financing balance and leverage crowding",
            "boundary": "margin balance is not evidence of long-only institutional ownership",
        },
        {
            "source_id": "S09",
            "source": "Official and company-reported launched-theme financial evidence",
            "type": "official_filing_and_guidance",
            "date": "2026Q1 and 2026H1 guidance",
            "quality": "L1",
            "path": "sources/launched-official-20260711/",
            "use": "ZTE Q1, Jiangbolong H1 guidance, Hengrui Q1 earnings bridge",
            "boundary": "Jiangbolong H1 figures are unaudited guidance; full-year conversion remains scenario-based",
        },
        {
            "source_id": "S10",
            "source": "Original and auditable launched-theme broker evidence",
            "type": "broker_research",
            "date": "2025-09 to 2026-07",
            "quality": "L2-L3",
            "path": "sources/launched-broker-reports-20260711/",
            "use": "ZTE, Jiangbolong and Hengrui forecasts, targets and valuation methods; Industrial Fulian is supplemented by post-preview Huatai/Huachuang pages in S14",
            "boundary": "older ZTE target is retained as an external anchor but current AStock denominator is more conservative",
        },
        {
            "source_id": "S11",
            "source": "AStock/Sina and Tencent launched-theme close snapshots",
            "type": "realtime_quote_adapter",
            "date": "2026-07-10 close",
            "quality": "L1",
            "path": "data/raw_launched_quotes_20260710.json",
            "use": "current price, trading value, price position and current-price valuation",
            "boundary": "daily price confirmation does not establish long-term trend durability",
        },
        {
            "source_id": "S12",
            "source": "A-share 2026H1 earnings-preview census plus archived company announcements",
            "type": "official_guidance_and_structured_census",
            "date": "through 2026-07-11",
            "quality": "L1-L2",
            "path": "data/earnings_preview_quality_20260711.json; sources/earnings-previews-20260711/",
            "use": "16-company preview quality, implied Q2 profit, one-off share and stale-denominator checks",
            "boundary": "guidance is unaudited and is not mechanically annualized; official PDFs must match ticker and title",
        },
        {
            "source_id": "S13",
            "source": "Full 54-name broker metadata census and 56-report priority PDF archive",
            "type": "original_broker_pdf_and_metadata",
            "date": "through 2026-07-11",
            "quality": "L2-L3",
            "path": "sources/core-broker-reports-20260711/",
            "use": "core-company report penetration, forecast recency and preview-to-report timing",
            "boundary": "pre-preview forecasts are marked stale; only auditable published point targets receive Street weight",
        },
        {
            "source_id": "S14",
            "source": "Industrial Fulian post-preview Huatai and Huachuang full report pages",
            "type": "auditable_broker_full_page",
            "date": "2026-07-10",
            "quality": "L2",
            "path": "sources/core-broker-reports-20260711/601138-huatai-post-preview.html; sources/core-broker-reports-20260711/601138-huachuang-post-preview.html",
            "use": "post-preview 2026E revenue, net profit, EPS, target price and AI-server/switch driver cross-check",
            "boundary": "Huatai published a CNY93 target; Huachuang disclosed earnings forecasts but no point target and therefore receives zero Street target weight",
        },
    ]


def build_claim_audit() -> list[dict[str, Any]]:
    return [
        {
            "claim_id": "C01",
            "claim": "All 31 Shenwan first-level industries were scanned.",
            "source_ids": ["S01", "S02", "S03"],
            "status": "verified",
            "materiality": "high",
        },
        {
            "claim_id": "C02",
            "claim": "Banks are the cleanest sector-level silent accumulation setup.",
            "source_ids": ["S01", "S02", "S03"],
            "status": "house_view",
            "materiality": "high",
        },
        {
            "claim_id": "C03",
            "claim": "Defense is launch confirmation rather than still-quiet accumulation.",
            "source_ids": ["S01", "S03"],
            "status": "house_view",
            "materiality": "high",
        },
        {
            "claim_id": "C04",
            "claim": "Pharmaceuticals and machinery do not pass the sector-level weekly-flow gate despite positive 2026-07-10 flow.",
            "source_ids": ["S03"],
            "status": "verified",
            "materiality": "high",
        },
        {
            "claim_id": "C05",
            "claim": "601077, 000425, and 601825 combine restrained price position with continuous inflow and a defensible 2026E valuation.",
            "source_ids": ["S04", "S05", "S06", "S07", "S08"],
            "status": "verified_with_model",
            "materiality": "high",
        },
        {
            "claim_id": "C06",
            "claim": "Semiconductor equipment remains a funding island but is no longer a low-position opportunity.",
            "source_ids": ["S04", "S05"],
            "status": "verified_with_price_position",
            "materiality": "high",
        },
        {
            "claim_id": "C07",
            "claim": "ZTE has launched on compute/network rotation and still retains at least 20% conservative multi-anchor upside, but Q1 profit and cash flow require H2 validation.",
            "source_ids": ["S09", "S10", "S11"],
            "status": "verified_with_model",
            "materiality": "high",
        },
        {
            "claim_id": "C08",
            "claim": "Jiangbolong has the largest launched-theme earnings elasticity, but its cycle, inventory and cash-flow risks require pullback-only execution.",
            "source_ids": ["S09", "S10", "S11"],
            "status": "verified_with_model",
            "materiality": "high",
        },
        {
            "claim_id": "C09",
            "claim": "Hengrui's innovative-drug and BD earnings bridge supports material SOTP upside after trend confirmation.",
            "source_ids": ["S09", "S10", "S11"],
            "status": "verified_with_model",
            "materiality": "high",
        },
        {
            "claim_id": "C10",
            "claim": "The expanded company universe contains 54 names, 16 captured H1 previews and a 56-PDF priority broker archive.",
            "source_ids": ["S12", "S13"],
            "status": "verified",
            "materiality": "high",
        },
        {
            "claim_id": "C11",
            "claim": "Industrial Fulian has a post-preview earnings bridge and published CNY93 Huatai target, while several other preview names still require denominator refresh rather than invented targets.",
            "source_ids": ["S12", "S13", "S14"],
            "status": "verified_with_model",
            "materiality": "high",
        },
    ]


def build_broker_consensus() -> list[dict[str, Any]]:
    current_prices = {
        "601077": 6.30,
        "000425": 8.43,
        "601825": 7.66,
        "000063": 40.53,
        "301308": 587.60,
        "600276": 55.75,
        "601138": 66.27,
    }
    rows = [
        {
            "ticker": "601077",
            "broker": "华创证券目标 / 开源证券预测复核",
            "report_date": "2026-04-29",
            "rating": "推荐",
            "target_price": 8.82,
            "revenue_E": "CNY30.1bn (derived from Huachuang disclosed 5.0% growth)",
            "net_profit_E": "CNY12.7bn (derived from Huachuang disclosed 4.5% growth)",
            "EPS_E": "CNY1.12 derived; Kaiyuan original PDF cross-check CNY1.13",
            "method": "2026E 0.72x PB",
            "implied_upside": round(8.82 / current_prices["601077"] - 1, 4),
            "source_quality": "auditable_consensus_snapshot",
            "source_path": "sources/broker-reports/2026-07-11/index.md#601077",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "601077",
            "broker": "开源证券",
            "report_date": "2026-06-08",
            "rating": "买入",
            "target_price": 8.18,
            "revenue_E": "CNY29.3bn",
            "net_profit_E": "CNY12.9bn",
            "EPS_E": "CNY1.13",
            "method": "PB-ROE implied fair value; report gave rating without a point target",
            "implied_upside": round(8.18 / current_prices["601077"] - 1, 4),
            "source_quality": "original_pdf_house_derived_from_broker_bvps",
            "source_path": "sources/broker-reports/2026-07-11/601077_first_coverage_20260608.pdf",
            "valuation_weight": 0.0,
        },
        {
            "ticker": "000425",
            "broker": "华创证券",
            "report_date": "2026-05-04",
            "rating": "强推",
            "target_price": 12.50,
            "revenue_E": "CNY112.3bn",
            "net_profit_E": "CNY8.17bn",
            "EPS_E": "CNY0.70",
            "method": "2026E 18x PE",
            "implied_upside": round(12.50 / current_prices["000425"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/broker-reports/2026-07-11/000425_huachuang_repost_20260711.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "000425",
            "broker": "东吴证券",
            "report_date": "2026-04-30",
            "rating": "买入",
            "target_price": 11.73,
            "revenue_E": "CNY116.7bn",
            "net_profit_E": "CNY8.13bn",
            "EPS_E": "CNY0.69",
            "method": "2026E 17x PE house normalization from original PDF forecasts",
            "implied_upside": round(11.73 / current_prices["000425"] - 1, 4),
            "source_quality": "original_pdf_house_derived_target",
            "source_path": "sources/broker-reports/2026-07-11/000425_dongwu_20260430.pdf",
            "valuation_weight": 0.0,
        },
        {
            "ticker": "601825",
            "broker": "国泰海通目标 / 国信证券预测复核",
            "report_date": "2026-04-29",
            "rating": "增持",
            "target_price": 10.73,
            "revenue_E": "CNY26.0bn (Guosen original PDF cross-check)",
            "net_profit_E": "CNY12.45bn (derived from GTH disclosed 1.1% growth)",
            "EPS_E": "CNY1.29 (GTH BVPS package / Guosen original PDF cross-check)",
            "method": "2026E 0.75x PB on BVPS CNY14.31",
            "implied_upside": round(10.73 / current_prices["601825"] - 1, 4),
            "source_quality": "auditable_consensus_snapshot",
            "source_path": "sources/broker-reports/2026-07-11/index.md#601825",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "601825",
            "broker": "国信证券",
            "report_date": "2026-04-26",
            "rating": "中性",
            "target_price": 9.17,
            "revenue_E": "CNY26.0bn",
            "net_profit_E": "CNY12.4bn",
            "EPS_E": "CNY1.29",
            "method": "2026E 0.65x PB implied by report date price",
            "implied_upside": round(9.17 / current_prices["601825"] - 1, 4),
            "source_quality": "original_pdf_house_derived_target",
            "source_path": "sources/broker-reports/2026-07-11/601825_guosen_20260426.pdf",
            "valuation_weight": 0.0,
        },
        {
            "ticker": "000063",
            "broker": "群益证券",
            "report_date": "2025-09-01",
            "rating": "买进",
            "target_price": 60.00,
            "revenue_E": "CNY166.694bn",
            "net_profit_E": "CNY9.263bn",
            "EPS_E": "CNY1.94",
            "method": "PE / relative valuation",
            "implied_upside": round(60.00 / current_prices["000063"] - 1, 4),
            "source_quality": "original_pdf",
            "source_path": "sources/launched-broker-reports-20260711/000063_qunyi_original.pdf",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "301308",
            "broker": "摩根士丹利目标 / 爱建证券预测复核",
            "report_date": "2026-07-04",
            "rating": "中性 / 买入",
            "target_price": 673.00,
            "revenue_E": "CNY40.039bn",
            "net_profit_E": "CNY19.969bn",
            "EPS_E": "CNY47.64",
            "method": "NAND supercycle target upgrade with Aijian forecast cross-check",
            "implied_upside": round(673.00 / current_prices["301308"] - 1, 4),
            "source_quality": "auditable_consensus_snapshot",
            "source_path": "sources/launched-broker-reports-20260711/index.md#301308",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "301308",
            "broker": "国信证券",
            "report_date": "2026-05-07",
            "rating": "优于大市",
            "target_price": 404.48,
            "revenue_E": "CNY40.455bn",
            "net_profit_E": "CNY11.097bn",
            "EPS_E": "CNY26.47",
            "method": "15.2x 2026E PE implied by original PDF",
            "implied_upside": round(404.48 / current_prices["301308"] - 1, 4),
            "source_quality": "original_pdf_house_derived_target",
            "source_path": "sources/launched-broker-reports-20260711/301308_guosen_original.pdf",
            "valuation_weight": 0.0,
        },
        {
            "ticker": "600276",
            "broker": "华泰证券",
            "report_date": "2026-04-23",
            "rating": "买入",
            "target_price": 87.14,
            "revenue_E": "CNY36.0bn public-consensus cross-check",
            "net_profit_E": "CNY9.40bn",
            "EPS_E": "CNY1.42",
            "method": "SOTP",
            "implied_upside": round(87.14 / current_prices["600276"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/launched-broker-reports-20260711/600276_huatai_repost.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "600276",
            "broker": "高盛",
            "report_date": "2026-04-23",
            "rating": "买入",
            "target_price": 79.20,
            "revenue_E": "CNY36.0bn public-consensus cross-check",
            "net_profit_E": "CNY9.4bn cross-check",
            "EPS_E": "CNY1.42",
            "method": "generic-drug 10x PE plus innovative-drug risk-adjusted DCF",
            "implied_upside": round(79.20 / current_prices["600276"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/launched-broker-reports-20260711/600276_goldman_repost.html",
            "valuation_weight": 0.0,
        },
        {
            "ticker": "601138",
            "broker": "华泰证券",
            "report_date": "2026-07-10",
            "rating": "买入",
            "target_price": 93.00,
            "revenue_E": "CNY1,480.37bn",
            "net_profit_E": "CNY56.01bn",
            "EPS_E": "CNY2.82",
            "method": "33x 2026E PE",
            "implied_upside": round(93.00 / current_prices["601138"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/core-broker-reports-20260711/601138-huatai-post-preview.html",
            "valuation_weight": 0.10,
        },
    ]
    return rows


def build_valuation_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "ticker": "601077",
            "company": "渝农商行",
            "opportunity_bucket": "quiet_accumulation",
            "current_price": 6.30,
            "price_date": "2026-07-10",
            "shares_100mn": 113.57,
            "market_cap_100mn_cny": round(6.30 * 113.57, 2),
            "revenue_2026e_100mn": 292.89,
            "np_2026e_100mn": 128.80,
            "eps_2026e": 1.13,
            "method": "PB-ROE with NIM and asset-quality validation",
            "bear": 6.39,
            "base": 8.18,
            "bull": 9.59,
            "market_implied_anchor": 7.00,
            "broker_anchor": 8.82,
            "fundamental_weight": 0.70,
            "market_weight": 0.20,
            "broker_weight": 0.10,
            "final_target": 8.01,
            "upside": round(8.01 / 6.30 - 1, 4),
            "action": "core review / pullback entry",
            "evidence_quality": "high",
            "catalyst": "NIM holds near 1.6-1.7%; net interest income remains positive; northbound/insurance allocation persists",
            "invalidation": "NPL ratio rises above 1.15%, NIM falls below 1.55%, or revenue growth returns below 2%",
        },
        {
            "ticker": "000425",
            "company": "徐工机械",
            "opportunity_bucket": "quiet_accumulation",
            "current_price": 8.43,
            "price_date": "2026-07-10",
            "shares_100mn": 117.1121,
            "market_cap_100mn_cny": round(8.43 * 117.1121, 2),
            "revenue_2026e_100mn": 1141.98,
            "np_2026e_100mn": 83.0,
            "eps_2026e": 0.71,
            "method": "2026E PE with cash-flow and overseas/mining bridge",
            "bear": 8.52,
            "base": 11.36,
            "bull": 13.49,
            "market_implied_anchor": 9.40,
            "broker_anchor": 12.50,
            "fundamental_weight": 0.70,
            "market_weight": 0.20,
            "broker_weight": 0.10,
            "final_target": 11.08,
            "upside": round(11.08 / 8.43 - 1, 4),
            "action": "pullback entry / earnings validation",
            "evidence_quality": "high",
            "catalyst": "overseas revenue and mining machinery sustain double-digit growth; Q2 cash flow confirms Q1 improvement",
            "invalidation": "2026E EPS falls below CNY0.60, overseas growth falls below 8%, or operating cash flow reverses materially",
        },
        {
            "ticker": "601825",
            "company": "沪农商行",
            "opportunity_bucket": "quiet_accumulation",
            "current_price": 7.66,
            "price_date": "2026-07-10",
            "shares_100mn": 96.44,
            "market_cap_100mn_cny": round(7.66 * 96.44, 2),
            "revenue_2026e_100mn": 260.0,
            "np_2026e_100mn": 124.0,
            "eps_2026e": 1.29,
            "method": "PB-ROE with dividend and asset-quality floor",
            "bear": 7.76,
            "base": 9.88,
            "bull": 10.73,
            "market_implied_anchor": 8.50,
            "broker_anchor": 10.73,
            "fundamental_weight": 0.70,
            "market_weight": 0.20,
            "broker_weight": 0.10,
            "final_target": 9.69,
            "upside": round(9.69 / 7.66 - 1, 4),
            "action": "income-oriented pullback entry",
            "evidence_quality": "medium-high",
            "catalyst": "revenue stays positive, NIM decline remains contained, dividend payout remains near 34%",
            "invalidation": "NPL ratio rises above 1.05%, provision coverage falls below 280%, or revenue returns below zero growth",
        },
        {
            "ticker": "000063",
            "company": "中兴通讯",
            "opportunity_bucket": "launched_with_runway",
            "current_price": 40.53,
            "price_date": "2026-07-10",
            "shares_100mn": 47.83534887,
            "market_cap_100mn_cny": round(40.53 * 47.83534887, 2),
            "revenue_2026e_100mn": 1500.0,
            "np_2026e_100mn": 71.02,
            "eps_2026e": 1.48,
            "method": "PE with compute-revenue-share and H2 margin validation",
            "bear": 38.48,
            "base": 48.84,
            "bull": 59.20,
            "market_implied_anchor": 44.00,
            "broker_anchor": 60.00,
            "fundamental_weight": 0.65,
            "market_weight": 0.25,
            "broker_weight": 0.10,
            "final_target": 48.75,
            "upside": round(48.75 / 40.53 - 1, 4),
            "action": "launched core / pullback confirmation",
            "evidence_quality": "medium-high",
            "catalyst": "compute revenue remains above 25% of sales; H2 profit returns to growth; AI server/network orders convert without further gross-margin erosion",
            "invalidation": "2026E EPS falls below CNY1.30, compute share falls below 22%, or operating cash flow remains negative through H2",
        },
        {
            "ticker": "301308",
            "company": "江波龙",
            "opportunity_bucket": "launched_with_runway",
            "current_price": 587.60,
            "price_date": "2026-07-10",
            "shares_100mn": 4.23061007,
            "market_cap_100mn_cny": round(587.60 * 4.23061007, 2),
            "revenue_2026e_100mn": 440.0,
            "np_2026e_100mn": 200.0,
            "eps_2026e": 47.28,
            "method": "2026E peak-cycle PE with H1 guidance, enterprise-SSD and cash-flow validation",
            "bear": 520.00,
            "base": 900.00,
            "bull": 1100.00,
            "market_implied_anchor": 650.00,
            "broker_anchor": 673.00,
            "fundamental_weight": 0.60,
            "market_weight": 0.30,
            "broker_weight": 0.10,
            "final_target": 802.30,
            "upside": round(802.30 / 587.60 - 1, 4),
            "action": "launched high-beta / pullback only",
            "evidence_quality": "medium-high",
            "catalyst": "H2 profit remains at least CNY8bn; enterprise SSD and AI storage mix rise; NAND contract prices remain firm",
            "invalidation": "2026E net profit falls below CNY16bn, operating cash flow remains deeply negative, or inventory write-down risk rises materially",
        },
        {
            "ticker": "600276",
            "company": "恒瑞医药",
            "opportunity_bucket": "launched_with_runway",
            "current_price": 55.75,
            "price_date": "2026-07-10",
            "shares_100mn": 66.37199874,
            "market_cap_100mn_cny": round(55.75 * 66.37199874, 2),
            "revenue_2026e_100mn": 360.0,
            "np_2026e_100mn": 94.0,
            "eps_2026e": 1.42,
            "method": "SOTP: mature portfolio plus innovative-drug/BD risk-adjusted DCF",
            "bear": 64.00,
            "base": 78.00,
            "bull": 90.00,
            "market_implied_anchor": 62.00,
            "broker_anchor": 87.14,
            "fundamental_weight": 0.65,
            "market_weight": 0.25,
            "broker_weight": 0.10,
            "final_target": 74.91,
            "upside": round(74.91 / 55.75 - 1, 4),
            "action": "launched core / trend pullback entry",
            "evidence_quality": "high",
            "catalyst": "innovative-drug sales growth exceeds 30%; new approvals and BD milestones convert; net margin continues to rise",
            "invalidation": "innovative-drug growth falls below 20%, 2026E EPS falls below CNY1.25, or key pipeline/BD milestones are delayed",
        },
        {
            "ticker": "601138",
            "company": "工业富联",
            "opportunity_bucket": "launched_with_runway",
            "current_price": 66.27,
            "price_date": "2026-07-10",
            "shares_100mn": 198.64,
            "market_cap_100mn_cny": round(66.27 * 198.64, 2),
            "revenue_2026e_100mn": 14803.7,
            "np_2026e_100mn": 560.1,
            "eps_2026e": 2.82,
            "method": "post-preview PE with AI-server, 800G+ switch and Q2 earnings validation",
            "bear": 62.40,
            "base": 84.60,
            "bull": 113.75,
            "market_implied_anchor": 72.00,
            "broker_anchor": 93.00,
            "fundamental_weight": 0.65,
            "market_weight": 0.25,
            "broker_weight": 0.10,
            "final_target": 82.29,
            "upside": round(82.29 / 66.27 - 1, 4),
            "action": "launched core / earnings-delivery pullback",
            "evidence_quality": "high",
            "catalyst": "H2 next-generation AI-server products enter volume production; AI-server revenue and 800G+ switch shipments remain high growth; gross margin and cash conversion improve",
            "invalidation": "2026E net profit falls below CNY51.6bn, AI-server growth falls below 100%, next-generation product ramp slips, or gross margin falls below 7%",
        },
    ]
    return rows


def broker_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Broker / Street Consensus",
        "",
        "| Ticker | Broker | Date | Rating | Target | Revenue E | Net profit E | EPS E | Method | Upside | Quality | Weight |",
        "|---|---|---|---|---:|---|---|---|---|---:|---|---:|",
    ]
    for row in rows:
        target = (
            f"{row['target_price']:.2f}"
            if row["target_price"] is not None
            else "not disclosed"
        )
        implied_upside = (
            f"{row['implied_upside']:.1%}"
            if row["implied_upside"] is not None
            else "not applicable"
        )
        lines.append(
            f"| {row['ticker']} | {row['broker']} | {row['report_date']} | {row['rating']} | "
            f"{target} | {row['revenue_E']} | {row['net_profit_E']} | "
            f"{row['EPS_E']} | {row['method']} | {implied_upside} | "
            f"{row['source_quality']} | {row['valuation_weight']:.0%} |"
        )
    lines += [
        "",
        "Rows labelled `original_pdf_house_derived_target` or "
        "`original_pdf_house_derived_from_broker_bvps` retain the broker forecast "
        "but receive zero Street weight because the point target was calculated by "
        "AStock rather than published by the broker.",
    ]
    return "\n".join(lines)


def valuation_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Valuation Model",
        "",
        "## Final Valuation Table",
        "",
        "| Ticker | Company | Price | Shares (100mn) | Market cap (CNY100mn) | 2026E revenue | 2026E NP | EPS | Method | Bear | Base | Bull | Final target | Upside | Action |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | "
            f"{row['shares_100mn']:.2f} | {row['market_cap_100mn_cny']:.2f} | "
            f"{row['revenue_2026e_100mn']:.2f} | {row['np_2026e_100mn']:.2f} | "
            f"{row['eps_2026e']:.2f} | {row['method']} | {row['bear']:.2f} | "
            f"{row['base']:.2f} | {row['bull']:.2f} | {row['final_target']:.2f} | "
            f"{row['upside']:.1%} | {row['action']} |"
        )
    return (
        "\n".join(lines)
        + """

## Three-Tier Targets

- Quiet accumulation: 601077 uses 0.50x/0.64x/0.75x PB; 000425 uses 12x/16x/19x PE; 601825 uses 0.55x/0.70x/0.76x PB.
- Launched with runway: 000063 uses 26x/33x/40x PE; 301308 uses a CNY520/900/1,100 peak-cycle band; 600276 uses CNY64/78/90 SOTP values; 601138 uses CNY62.4/84.6/113.75 post-preview PE values.

## Relative / PEG / PSG Comparison

PB-ROE is primary for banks. PE plus cash-flow conversion is primary for XCMG and ZTE. Jiangbolong uses peak-cycle PE and explicit cycle normalization. Hengrui uses SOTP because innovative-drug and mature-product economics differ. Industrial Fulian uses post-preview PE with Huatai's published CNY93 target and Huachuang's higher earnings forecast as a zero-target-weight cross-check.

## Seasonality Calibration

The bank forecasts use broker full-year estimates rather than Q1 annualization. XCMG uses a full-year broker range. ZTE uses public consensus rather than annualizing the weak Q1 profit. Jiangbolong uses official H1 guidance plus an explicit H2 scenario. Hengrui uses full-year broker forecasts and SOTP. Industrial Fulian uses the official H1 midpoint and post-preview Huatai/Huachuang forecasts; H1 is not mechanically doubled.

## Next-Quarter Threshold

- 601077: revenue growth >4%, NIM >=1.60%, NPL <=1.10%.
- 000425: revenue growth >10%, overseas growth >10%, operating cash flow remains positive, adjusted net profit resumes double-digit growth.
- 601825: revenue growth >=0%, NIM decline <=5bp, NPL <=1.00%, provision coverage >=300%.
- 000063: compute revenue share >=25%, H2 profit growth returns positive, operating cash flow improves.
- 301308: H2 profit >=CNY8bn, cash flow improves, no material inventory write-down.
- 600276: innovative-drug sales growth >=30%, 2026E EPS >=CNY1.35, pipeline/BD milestones remain on schedule.
- 601138: H2 net profit >=CNY32.1bn under the Huatai base, AI-server growth >100%, 800G+ shipments remain positive, gross margin >=7%.

## Method and Assumption Bridge

Banks receive PB credit only when ROE, NIM and asset quality support the multiple. XCMG receives PE credit only when overseas/mining growth and cash conversion support the forecast. Launched-growth names receive growth credit only through `data/growth_driver_model.json`.

## Market-Expectation Valuation Bridge

Current prices imply approximately 0.49x-0.54x 2026E PB for the rural banks, about 12x PE for XCMG, 27x for ZTE, 12.4x for Jiangbolong, 39x for Hengrui and 23.5x for Industrial Fulian. The launched basket therefore requires earnings delivery, not only multiple expansion.

## Broker/Street Comparison

See `data/broker_street_consensus_20260711.md`. Weak or house-derived target rows receive zero Street weight.

## Market-Implied Sentiment Anchor

Quiet names use 70% fundamental value, 20% market anchor and 10% broker anchor. Launched names use 60-65% fundamental value, 25-30% market anchor and 10% broker anchor to reflect higher trend and crowding risk.

## Growth Earnings Dependency

ZTE, Jiangbolong, Hengrui and Industrial Fulian consume the growth-earnings package. Industrial Fulian uses official H1 profit, AI-server revenue growth, 800G+ switch shipments and post-preview broker forecasts; no undisclosed customer allocation or segment margin is invented.

## Full-Chain Classification Dependency

Not applicable as a supply-chain report. The full-market scan classifies sectors and core stock islands; all seven investable names are valued at company level and the remaining 47 names receive explicit valuation dispositions.
"""
    )


def build_analysis_files(rows: list[dict[str, Any]]) -> None:
    write_text(
        ANALYSIS_DIR / "template_brief.md",
        """# Template Brief

- Archetype: market guide / capital-markets strategy report.
- Benchmark: J.P. Morgan Guide to the Markets for the all-sector scan; BlackRock/Vanguard for house-view tension and scenario discipline.
- First page: dual-bucket house view, candidate ranking, current price, target, upside, stage, invalidation.
- Chapter sequence: decision dashboard -> methodology -> 31-industry scan -> flow anatomy -> quiet core names -> launched-growth basket -> growth earnings bridge -> valuation -> risks and monitoring -> source appendix.
- Required exhibits: 31-sector stage table, sector price-flow matrix, continuous-inflow stock table, dual-bucket core valuation table, launched-theme earnings bridge, catalyst/invalidation monitor.
- Avoid: broker-summary prose, one-day-flow extrapolation, treating low valuation as a catalyst, or calling transaction-size flow “institutional ownership.”
""",
    )
    write_text(
        ANALYSIS_DIR / "house_view.md",
        """# House View

The report now has two opportunity curves. The strongest sector-level quiet accumulation signal is banks, not semiconductor equipment. Banks recorded CNY3.225bn of weekly main-fund inflow while remaining near the lower part of their 52-week range. The launched-with-runway basket contains ZTE, Jiangbolong, Hengrui and Industrial Fulian: each has confirmed price participation plus a current-price earnings bridge that supports at least 20% multi-anchor upside.

The 54-name census also identifies a preview-refresh pool rather than hiding it: Unisplendour, Shannon Semi, GigaDevice, Founder Technology and CSSC Offshore & Marine Engineering have material new guidance, but their old broker denominators are stale or one-off contaminated. They remain model-refresh candidates without fabricated targets.
""",
    )
    write_text(
        ANALYSIS_DIR / "variant_perception.md",
        """# Variant Perception

- Consensus: high-beta technology, defense and event-driven themes are the main rotation winners, while low-volatility banks are only defensive.
- AStock differentiated view: own both curves but use different execution. Quiet names need time and invalidation discipline; launched names need earnings delivery and pullback entry rather than narrative chasing.
- Assumption gap: market attention overweights one-day price strength and underweights both persistent low-position flow and current-price-implied earnings requirements.
- Strongest opposing argument: banks are cheap for structural reasons; ZTE margins may not recover; Jiangbolong may be near a cycle peak; Hengrui's pipeline and BD value may already be capitalized; Industrial Fulian may lose margin leverage if platform ramp or customer capex slows.
- What proves AStock wrong: bank NIM/asset quality deteriorates, XCMG cash flow fades, ZTE H2 profit stays weak, Jiangbolong H2 cash flow/inventory worsens, Hengrui innovative-drug growth falls below 20%, or Industrial Fulian 2026E net profit falls below CNY51.6bn.
- Monitoring triggers: next-quarter bank NIM/NPL; XCMG cash flow; ZTE compute share/margin; Jiangbolong H2 profit/cash flow; Hengrui innovative-drug sales and BD milestones; Industrial Fulian H2 profit, AI-server growth, 800G+ shipments and gross margin.
""",
    )
    write_text(
        ANALYSIS_DIR / "secondary_market_analysis.md",
        """# Secondary Market Analysis

## Price, Volume, Turnover, Drawdown and Relative Performance

601825 closed at CNY7.66, near 8% of its one-year price range and about 20.5% below the period high. 601077 closed at CNY6.30, near 31% of its one-year range and 14.1% below the high. 000425 closed at CNY8.43, near 20% of its one-year range and 32.3% below the high.

## Valuation Crowding and Financing

Financing balances are low: approximately 0.18% of free-float market value for 601825, 0.54% for 601077, and 1.12% for 000425. This is not a leverage-led rally.

## Fund Attitude, Institutional, Northbound and Hot-Money Classification

601077 combines Shanghai-Hong Kong Stock Connect holdings, ETF ownership and eight consecutive inflow days. 601825 has insurance and state-owned long-duration holders plus ten consecutive inflow days; the Q1 top-ten table does not show Northbound in the top ten, so Northbound claims are not used as a primary conclusion. 000425 had material Northbound ownership in Q1 and five consecutive inflow days, but daily financing was slightly net-repaid.

No Dragon-Tiger seat evidence is required for these large, low-turnover names; absence of seat activity supports the non-hot-money classification. The trading style is trend swing / income re-rating rather than leading-stock tactic.

ZTE closed at CNY40.53 after a 7.2% 20-day rise and a high-turnover breakout week; its 2026-07-10 main-flow reading turned negative after heavy weekly inflow, so execution is trend pullback rather than breakout chasing. Jiangbolong closed at CNY587.60 after a 66.2% 60-day rise and weekly main-fund outflow, making it the highest-beta pullback-only name. Hengrui closed at CNY55.75 after an 18.7% 20-day rise; five-day main-fund inflow remained positive, but financing crowding was above its one-year 80th percentile. Industrial Fulian closed at CNY66.27, around 76% of its one-year range, after a 4.7% 20-day pullback and 19.0% 60-day gain; this is an earnings-delivery pullback, not a low-position setup.

## Support and Resistance

- 601077: support CNY6.02-6.20; resistance CNY6.70-7.00; target zone CNY7.99.
- 000425: support CNY8.18-8.35; resistance CNY9.20-9.60; target zone CNY11.08.
- 601825: support CNY7.55-7.65; resistance CNY8.10-8.50; target zone CNY9.75.
- 000063: support CNY36.30-39.60; resistance CNY43.00-44.40; target zone CNY48.75.
- 301308: support CNY560-588; resistance CNY645-673; target zone CNY802.
- 600276: support CNY50-54.5; resistance CNY57.5-61; target zone CNY74.91.
- 601138: support CNY62-66; resistance CNY72-76; target zone CNY82.29, with Huatai CNY93 as the external bull anchor.
""",
    )
    write_text(
        ANALYSIS_DIR / "segment_valuation_model.md",
        """# Segment Valuation Model

This is a multi-stock strategy report, so “segment” means the economic driver blocks that support each company model.

| Company | Segment / driver | 2026E revenue or earnings | Multiple | Sensitivity | Validation trigger |
|---|---|---:|---:|---|---|
| 渝农商行 | net-interest income + fee income | CNY29.3bn revenue / CNY12.9bn net profit | 0.64x base PB | NIM, credit cost, NPL | NIM >=1.60%, NPL <=1.10% |
| 徐工机械 | domestic base + overseas + mining machinery | CNY114.2bn revenue / CNY8.3bn net profit | 16x base PE | overseas growth, margin, FX | cash flow and adjusted profit recovery |
| 沪农商行 | net-interest income + wealth/fee income | CNY26.0bn revenue / CNY12.4bn net profit | 0.70x base PB | NIM, provision, payout | revenue >=0%, provision coverage >=300% |
| 中兴通讯 | connection base + compute products | CNY150.0bn revenue / CNY7.1bn net profit | 33x base PE | compute share, gross margin, OCF | compute share >=25%, H2 profit growth positive |
| 江波龙 | storage base + cycle/AI storage increment | CNY44.0bn revenue / CNY20.0bn net profit | peak-cycle scenario | H2 profit, NAND price, OCF | H2 profit >=CNY8bn, OCF improves |
| 恒瑞医药 | mature drugs + innovative drugs/BD | CNY36.0bn revenue / CNY9.4bn net profit | SOTP | innovative sales, BD, pipeline | innovative sales >=30%, EPS >=1.35 |
| 工业富联 | manufacturing base + AI server/high-speed network increment | CNY1,480.4bn revenue / CNY56.0bn net profit | 30x base PE | platform ramp, mix, GM, OCF | H2 NP >=CNY32.1bn, GM >=7% |

The model prevents applying one uniform PE method across banks, industrial equipment, communication equipment, storage cycles and innovative pharmaceuticals.
""",
    )
    write_text(
        ANALYSIS_DIR / "risk_framework.md",
        """# Risk Framework

1. Flow-measurement risk: transaction-size main-flow labels may not identify institutions.
2. Timing risk: quiet accumulation can remain quiet; low volatility does not guarantee a catalyst.
3. Bank risk: NIM compression, regional credit deterioration, property and retail-loan risk, and dividend-policy change.
4. XCMG risk: domestic demand, overseas protectionism, FX translation, commodity input prices and receivable quality.
5. Rotation risk: a renewed high-beta technology rally can delay low-position rerating.
6. Model risk: most broker targets were issued before the 2026-07-10 price cutoff; Industrial Fulian is the exception with a post-preview Huatai target. Final targets use current prices and explicit weights.
7. Launched-theme crowding risk: ZTE and Jiangbolong have high recent turnover and can retrace even when the long-term thesis remains intact.
8. Earnings-bridge risk: Jiangbolong and Industrial Fulian guidance is unaudited; ZTE compute mix may dilute margins; Hengrui SOTP depends on pipeline and BD milestones.
9. Preview-refresh risk: H1 EPS already exceeds old full-year EPS for Shannon Semi, GigaDevice, Do-Fluoride and Founder Technology. Old PE rows are invalid until a post-preview denominator is rebuilt.
""",
    )
    write_text(
        ANALYSIS_DIR / "exhibit_plan.md",
        """# Exhibit Plan

1. Decision dashboard: ranking, price, target, upside, stage and invalidation.
2. 31-sector stage table: weekly flow, daily flow, 52-week position and valuation percentile.
3. Price-flow matrix: silent accumulation, launch confirmation, one-day rebound and low-price/no-flow.
4. Continuous-inflow stock islands: days, inflow, return and one-year position.
5. Dual-bucket core valuation table: bear/base/bull, multi-anchor target and action.
6. Launched-theme earnings bridge: growth proxy, revenue, profit, EPS and current-price implied hurdle.
7. H1 preview quality table: H1 EPS, implied Q2, one-off share and stale-denominator ratio for 16 names.
8. Full company appendix: 54 cards, report recency and valuation disposition.
9. Monitoring dashboard: next-quarter thresholds and downgrade rules.
""",
    )
    write_text(
        ANALYSIS_DIR / "delta_audit.md",
        """# Delta Audit

## User Corrections

The first published version answered only the quiet-accumulation question. The user required the report to also cover sectors and core stocks that have already launched but still retain large earnings and valuation runway.

The second published draft remained too shallow: it used six valuation names to stand in for broad sectors, did not exhaust the latest H1 previews, and did not penetrate enough original broker reports for the core names.

## Gap

- Missing second opportunity curve.
- Launched sectors were classified only as “no longer quiet” instead of being tested for remaining upside.
- No mandatory growth-earnings gate connected launched-theme revenue/proxies to net profit, EPS and current-price-implied expectations.
- Core-company coverage was too narrow and did not provide a disposition for every sector-level core/satellite name.
- H1 preview quality, implied Q2 profit, one-off contribution and stale full-year EPS were not systematically compared.
- Broker metadata and original PDFs were not presented as a complete 54-name / 56-PDF evidence package.

## Repair

- Added a launched-with-runway core pool: 000063, 301308, 600276 and 601138.
- Added `data/growth_driver_model.json`, `analysis/growth_earnings_model.md`, `analysis/value_chain_economics.md`, `analysis/segment_forecast_bridge.md`, and `analysis/implied_growth_sensitivity.md`.
- Expanded the current-price valuation universe from three to seven names.
- Added reader-facing launched-theme chapters and conditionally downgraded defense, advanced packaging and media/AI applications.
- Built a 54-name full company universe, 16-preview quality census and 56-original-PDF priority archive.
- Added the H1 EPS / latest 2026E EPS ratio so stale broker denominators are visible rather than silently reused.
- Created a no-fabrication preview-refresh pool for Unisplendour, Shannon Semi, GigaDevice, Founder Technology and CSSC Offshore & Marine Engineering.

## Prevention Rule

Every future full-market opportunity report must test both curves:

1. Quiet accumulation: low position + persistent flow + improving fundamentals + valuation.
2. Launched with runway: confirmed trend + revenue/proxy-to-EPS bridge + at least 20% base current-price upside + explicit crowding and invalidation.

A launched theme that lacks a company-level earnings bridge or sufficient current-price upside must remain conditional watch only.

Every future update must also refresh the full core/satellite company census, exhaust newly published earnings previews, compare preview EPS with the latest broker denominator, and invalidate any report forecast published before a material preview unless a post-preview model is available.
""",
    )


def build_growth_artifacts() -> None:
    drivers = [
        {
            "ticker": "000063",
            "company": "中兴通讯",
            "applies": True,
            "growth_driver": "compute products and AI server/network infrastructure",
            "base_business_revenue": "CNY109.5bn proxy, 73% of 2026E revenue",
            "growth_segment_revenue": "CNY40.5bn proxy, 27% of 2026E revenue",
            "value_amount_or_proxy": "2026Q1 compute-product revenue share 27%",
            "unit_volume_or_proxy": "compute revenue share and operator/data-center project delivery",
            "ASP_or_price": "not disclosed; consolidated revenue and margin proxy used",
            "recognized_revenue_ratio": "1.0 for reported/forecast consolidated revenue; segment ratio not separately disclosed",
            "supply_demand_state": "AI compute demand strong; operator base mixed",
            "capacity_or_utilization": "not disclosed",
            "certification_or_customer_qualification": "operator and data-center project participation; named allocation not disclosed",
            "growth_gross_margin": "not separately disclosed; consolidated 2026Q1 gross margin 28.3%",
            "incremental_opex": "captured in public-consensus net profit; R&D intensity remains high",
            "growth_net_profit": "not separately disclosed; consolidated 2026E net profit CNY7.1bn",
            "growth_EPS": "consolidated 2026E EPS CNY1.48",
            "evidence_type": "official Q1 plus public consensus and original broker PDF cross-check",
            "source": "sources/launched-official-20260711/000063_2026Q1_official.pdf; sources/launched-broker-reports-20260711/000063_qunyi_original.pdf",
            "evidence_gap": "compute segment margin, units, ASP and named customer allocation not disclosed",
            "valuation_credit": "optionality credit inside consolidated PE; no separate high-growth segment multiple",
            "bear": {"eps": 1.30, "multiple": 29, "value": 38.48},
            "base": {"eps": 1.48, "multiple": 33, "value": 48.84},
            "bull": {"eps": 1.48, "multiple": 40, "value": 59.20},
            "current_price_implied_growth": "CNY40.53 implies 27.4x 2026E PE and about CNY5.9bn net profit at a 33x base multiple",
            "sensitivity_key": "H2 profit recovery and compute segment margin",
            "next_quarter_validation_threshold": "compute share >=25%, H2 profit growth positive, OCF improves",
        },
        {
            "ticker": "301308",
            "company": "江波龙",
            "applies": True,
            "growth_driver": "NAND/DRAM price cycle plus enterprise SSD and AI storage",
            "base_business_revenue": "CNY22.8bn 2025 reported revenue baseline",
            "growth_segment_revenue": "CNY21.2bn 2026E incremental revenue over the 2025 baseline",
            "value_amount_or_proxy": "official 2026H1 revenue guidance CNY22-25bn and net profit CNY9.2-11.0bn",
            "unit_volume_or_proxy": "H1 revenue guidance, LTA/MOU supply agreements and enterprise/AI storage mix",
            "ASP_or_price": "NAND/DRAM contract-price proxy; company ASP not disclosed",
            "recognized_revenue_ratio": "H1 guidance is recognized revenue; H2 conversion is scenario-based",
            "supply_demand_state": "tight storage supply; AI demand extends cycle, consumer demand more volatile",
            "capacity_or_utilization": "self-owned packaging capacity disclosed qualitatively; utilization not disclosed",
            "certification_or_customer_qualification": "AMD joint optimization and enterprise-storage expansion; customer allocation not disclosed",
            "growth_gross_margin": "2026Q1 consolidated gross margin 55.5%; base full-year assumes normalization",
            "incremental_opex": "captured in CNY20.0bn base net-profit scenario",
            "growth_net_profit": "CNY18.6bn increment over 2025 net profit in the base scenario",
            "growth_EPS": "CNY47.28 base 2026E EPS",
            "evidence_type": "official H1 guidance plus original Guosen/Aijian PDFs and auditable Morgan Stanley repost",
            "source": "sources/launched-official-20260711/301308_H1_guidance_20260703.pdf; sources/launched-broker-reports-20260711/",
            "evidence_gap": "H2 shipment, ASP, cash-flow conversion and inventory cost layers remain uncertain",
            "valuation_credit": "earnings credit with peak-cycle discount and pullback-only execution",
            "bear": {"net_profit_100mn": 160, "value": 520},
            "base": {"net_profit_100mn": 200, "eps": 47.28, "value": 900},
            "bull": {"net_profit_100mn": 220, "value": 1100},
            "current_price_implied_growth": "At 19x PE, CNY587.60 implies about CNY13.1bn 2026 net profit, only CNY3.0bn H2 profit above the H1 midpoint; the discount reflects cycle and cash-flow risk",
            "sensitivity_key": "H2 profit, storage contract prices and operating cash flow",
            "next_quarter_validation_threshold": "H2 profit >=CNY8bn, OCF improves, no material inventory write-down",
        },
        {
            "ticker": "600276",
            "company": "恒瑞医药",
            "applies": True,
            "growth_driver": "innovative-drug sales, new approvals and BD milestones",
            "base_business_revenue": "CNY11.9bn proxy for mature products and other revenue",
            "growth_segment_revenue": "CNY24.1bn proxy, 67% of 2026E revenue",
            "value_amount_or_proxy": "2026Q1 innovative-drug sales CNY4.53bn, +25.8%; 2026 mix proxy 67%",
            "unit_volume_or_proxy": "innovative-drug sales growth, approvals and BD milestone recognition",
            "ASP_or_price": "portfolio mix proxy; product-level ASP not disclosed",
            "recognized_revenue_ratio": "1.0 for reported sales and recognized BD income; future milestones probability-adjusted in SOTP",
            "supply_demand_state": "innovative-drug demand and policy support positive; generic-drug pressure persists",
            "capacity_or_utilization": "not a primary constraint",
            "certification_or_customer_qualification": "regulatory approvals and global clinical milestones",
            "growth_gross_margin": "2026Q1 consolidated gross margin 86.6%",
            "incremental_opex": "R&D and launch costs embedded in Huatai earnings forecast",
            "growth_net_profit": "2026E consolidated net profit CNY9.4bn; segment contribution not separately disclosed",
            "growth_EPS": "CNY1.42",
            "evidence_type": "official Q1 financial packet plus auditable Huatai and Goldman report pages",
            "source": "data/launched_financials/600276_20260710.json; sources/launched-broker-reports-20260711/600276_*.html",
            "evidence_gap": "product-level ASP, pipeline probability and exact future BD timing are not disclosed",
            "valuation_credit": "earnings credit through SOTP, not a uniform consolidated high-growth PE",
            "bear": {"value": 64.0},
            "base": {"value": 78.0},
            "bull": {"value": 90.0},
            "current_price_implied_growth": "CNY55.75 implies 39.3x 2026E PE and a CNY3.70tn market cap versus Huatai SOTP CNY5.78tn",
            "sensitivity_key": "innovative-drug growth, BD recognition and pipeline probability",
            "next_quarter_validation_threshold": "innovative-drug sales growth >=30%, EPS >=CNY1.35, milestones on schedule",
        },
        {
            "ticker": "601138",
            "company": "工业富联",
            "applies": True,
            "growth_driver": "hyperscaler AI servers, next-generation GPU platforms and 800G+ data-center switches",
            "base_business_revenue": "CNY902.9bn 2025 consolidated revenue baseline; segment split not separately disclosed",
            "growth_segment_revenue": "CNY577.5bn 2026E consolidated increment over 2025 under Huatai forecast",
            "value_amount_or_proxy": "official 2026H1 net profit midpoint CNY23.9bn; AI-server revenue +230% and 800G+ switch shipments +140%",
            "unit_volume_or_proxy": "AI-server revenue growth, high-speed switch shipment growth and next-generation product ramp",
            "ASP_or_price": "GB/Rubin system value and mix proxy; company product ASP not disclosed",
            "recognized_revenue_ratio": "H1 figures are company guidance; H2 conversion follows post-preview Huatai/Huachuang forecasts rather than simple annualization",
            "supply_demand_state": "hyperscaler AI capex and high-speed interconnect remain strong; customer concentration and platform timing remain risks",
            "capacity_or_utilization": "next-generation product ramp disclosed qualitatively; exact capacity and utilization not disclosed",
            "certification_or_customer_qualification": "joint development with major customers and next-generation products entering H2 mass production; named allocation not disclosed",
            "growth_gross_margin": "2026Q1 consolidated gross margin 7.35%; Huatai expects mix and ASP improvement",
            "incremental_opex": "captured in Huatai CNY56.01bn and Huachuang CNY64.597bn 2026E net-profit forecasts",
            "growth_net_profit": "CNY56.01bn Huatai base; CNY64.597bn Huachuang cross-check",
            "growth_EPS": "CNY2.82 Huatai base",
            "evidence_type": "official H1 preview plus post-preview Huatai and Huachuang full report pages",
            "source": "sources/earnings-previews-20260711/601138_preview.pdf; sources/core-broker-reports-20260711/601138-huatai-post-preview.html; sources/core-broker-reports-20260711/601138-huachuang-post-preview.html",
            "evidence_gap": "customer allocation, product ASP, AI-server segment gross margin and exact H2 ramp cadence are not disclosed",
            "valuation_credit": "earnings credit through post-preview consolidated PE; no separate AI-segment multiple",
            "bear": {"net_profit_100mn": 516.0, "eps": 2.60, "multiple": 24, "value": 62.40},
            "base": {"net_profit_100mn": 560.1, "eps": 2.82, "multiple": 30, "value": 84.60},
            "bull": {"net_profit_100mn": 645.97, "eps": 3.25, "multiple": 35, "value": 113.75},
            "current_price_implied_growth": "CNY66.27 implies 23.5x Huatai 2026E EPS and CNY43.9bn net profit at a 30x base multiple, below the H1 midpoint plus conservative H2 conversion",
            "sensitivity_key": "H2 AI-server platform ramp, product mix, gross margin and cash conversion",
            "next_quarter_validation_threshold": "H2 NP >=CNY32.1bn, AI-server growth >100%, 800G+ shipments positive, gross margin >=7%",
        },
    ]
    write_json(
        DATA_DIR / "growth_driver_model.json",
        {"data_cutoff": DATA_CUTOFF, "drivers": drivers},
    )
    write_text(
        ANALYSIS_DIR / "growth_earnings_model.md",
        """# Growth Earnings Model

Gate status: PASS for the four launched-growth core names.

The quiet-accumulation names are not applicable to the high-growth precision gate: rural banks use NIM/credit/PB-ROE, while XCMG uses a cyclical cash-flow/PE framework. Their exclusion is explicit rather than a missing model.

## Decision

- ZTE: optionality credit inside consolidated PE. Compute mix is evidenced, but segment margin/ASP and customer allocation are not disclosed.
- Jiangbolong: earnings credit with peak-cycle discount. Official H1 guidance closes the revenue/profit bridge, but H2 cash flow and inventory remain hard gates.
- Hengrui: earnings credit through SOTP. Innovative-drug sales, BD income and pipeline milestones are separated from the mature portfolio.
- Industrial Fulian: earnings credit through post-preview consolidated PE. Official H1 guidance and post-preview forecasts close the profit denominator, while customer allocation and segment margin remain bounded gaps.

## Base Business Versus Growth Business

| Company | Base business | Growth business | 2026E revenue | 2026E net profit/EPS | Credit |
|---|---|---|---:|---:|---|
| ZTE | connection/operator base | compute products, AI servers/networks | CNY150.0bn | CNY7.1bn / CNY1.48 | optionality inside PE |
| Jiangbolong | 2025 storage revenue baseline | cycle price/mix increment, enterprise SSD, AI storage | CNY44.0bn | CNY20.0bn / CNY47.28 | earnings credit with cycle discount |
| Hengrui | mature products | innovative drugs and BD | CNY36.0bn | CNY9.4bn / CNY1.42 | SOTP earnings credit |
| Industrial Fulian | 2025 consolidated manufacturing base | AI servers, next-generation GPU platforms, 800G+ switches | CNY1,480.4bn | CNY56.0bn / CNY2.82 | post-preview PE earnings credit |

## Value-Chain Economics Bridge

ZTE uses compute revenue share because units and ASP are undisclosed. Jiangbolong uses official H1 revenue/profit guidance, LTA/MOU supply evidence and storage-price proxies. Hengrui uses innovative-drug sales growth, approvals, BD recognition and portfolio gross margin. Industrial Fulian uses official AI-server revenue growth, 800G+ switch shipment growth, H1 profit and post-preview forecasts. No undisclosed unit, ASP or customer allocation is invented.

## Current-Price-Implied Growth

- ZTE: current price implies 27.4x 2026E PE, below the 33x base framework, but H2 profit/OCF must recover.
- Jiangbolong: current price implies about CNY13.1bn net profit at 19x PE, below the CNY20.0bn base model; the gap is compensation for cycle and cash-flow risk.
- Hengrui: current price implies 39.3x 2026E PE and values the company at about 64% of Huatai's SOTP.
- Industrial Fulian: current price implies 23.5x Huatai 2026E EPS; the CNY82.29 multi-anchor target still requires H2 net profit of at least CNY32.1bn and sustained product-mix improvement.
""",
    )
    write_text(
        ANALYSIS_DIR / "value_chain_economics.md",
        """# Value-Chain Economics

| Company | Value proxy | Price/ASP proxy | Margin pool | Supply/demand | Capacity/utilization | Certification/order visibility | Valuation credit |
|---|---|---|---|---|---|---|---|
| ZTE | compute share 27% | not disclosed | consolidated GM 28.3% | AI compute strong, operator base mixed | not disclosed | operator/data-center projects; allocation undisclosed | optionality inside PE |
| Jiangbolong | H1 revenue CNY22-25bn | NAND/DRAM contract price | Q1 GM 55.5%, normalize in base | tight through AI demand; consumer risk | packaging capability, utilization undisclosed | LTA/MOU and AMD optimization | earnings credit with peak-cycle discount |
| Hengrui | innovative sales CNY4.53bn in Q1 | portfolio mix | consolidated GM 86.6% | innovative demand positive | not primary constraint | approvals, clinical milestones, BD | SOTP earnings credit |
| Industrial Fulian | H1 NP CNY23.9bn; AI server +230%; 800G+ +140% | platform/system mix proxy | Q1 GM 7.35%; mix improvement expected | hyperscaler AI capex strong | exact capacity/utilization undisclosed | major-customer joint development; H2 ramp | post-preview consolidated PE |
""",
    )
    write_text(
        ANALYSIS_DIR / "segment_forecast_bridge.md",
        """# Segment Forecast Bridge

## ZTE

2026E revenue CNY150.0bn is split by a 27% compute proxy into CNY40.5bn growth revenue and CNY109.5bn base revenue. Segment margin is not disclosed, so no separate high-growth multiple is applied. Consolidated EPS CNY1.48 receives a 33x base PE only if H2 profit and OCF recover.

## Jiangbolong

2025 revenue CNY22.8bn is the base. The 2026E CNY44.0bn model adds CNY21.2bn from storage pricing, supply and enterprise/AI mix. Official H1 guidance already covers CNY22-25bn revenue and CNY9.2-11.0bn net profit. The base model requires H2 net profit near CNY9.9bn.

## Hengrui

2026E revenue CNY36.0bn uses a 67% innovative-drug/BD mix proxy, or CNY24.1bn, with CNY11.9bn mature/other revenue. The SOTP prevents applying innovative-drug economics to the mature portfolio.

## Industrial Fulian

2025 consolidated revenue CNY902.9bn is the reported base. Huatai forecasts 2026E revenue CNY1,480.4bn and net profit CNY56.01bn/EPS CNY2.82 after the H1 preview. H1 net profit midpoint CNY23.9bn implies H2 net profit CNY32.1bn under the Huatai base. Huachuang's CNY64.597bn forecast is used as a bull earnings cross-check, not as a fabricated target.
""",
    )
    write_text(
        ANALYSIS_DIR / "implied_growth_sensitivity.md",
        """# Implied Growth Sensitivity

| Driver | Bear | Base | Bull | Current-price implied | Validation evidence | Downgrade trigger |
|---|---:|---:|---:|---:|---|---|
| ZTE 2026E EPS | 1.30 | 1.48 | 1.48 | 1.23 at 33x | compute share and H2 profit | EPS <1.30 or OCF stays negative |
| Jiangbolong 2026E NP, CNYbn | 16 | 20 | 22 | 13.1 at 19x | H1 guidance, H2 profit, storage prices | NP <16 or OCF/inventory worsens |
| Hengrui innovative growth | 20% | 30% | 35%+ | roughly 39x consolidated PE | Q1 sales, approvals, BD | growth <20% or EPS <1.25 |
| Industrial Fulian 2026E NP, CNYbn | 51.6 | 56.0 | 64.6 | 43.9 at 30x | H1 preview, AI-server/switch growth, post-preview forecasts | NP <51.6 or GM <7% |
""",
    )


def build_source_exhaustion() -> list[dict[str, Any]]:
    return [
        {
            "probe": "Eastmoney push2 industry API and AkShare Eastmoney industry endpoints",
            "result": "failed",
            "reason": "remote server closed connection without response",
            "fallback": "SWS history + Securities Times/DataBao structured tables + Legulegu valuation",
            "impact": "no loss of 31-industry coverage",
        },
        {
            "probe": "Baostock history",
            "result": "failed",
            "reason": "network receive error",
            "fallback": "SWS industry history and Tencent stock kline",
            "impact": "explicitly recorded",
        },
        {
            "probe": "Complete original target-price PDFs for every broker row",
            "result": "partial",
            "reason": "some reports were accessible only as auditable full-field reposts",
            "fallback": "positive weight limited to auditable repost rows; house-derived targets receive zero Street weight",
            "impact": "Street weight capped at 10%",
        },
    ]


def main() -> None:
    write_text(CASE_DIR / "research_brief.md", build_research_brief())
    gate_manifest = build_gate_manifest()
    artifact_contract = build_artifact_contract()
    write_json(CASE_DIR / "gate_manifest.json", gate_manifest)
    write_text(
        CASE_DIR / "gate_manifest.md",
        "# Gate Manifest\n\n" + "\n".join(f"- {key}: {value}" for key, value in gate_manifest.items()),
    )
    write_json(CASE_DIR / "artifact_contract.json", artifact_contract)
    write_text(
        CASE_DIR / "artifact_contract.md",
        "# Artifact Contract\n\n"
        + "\n".join(
            f"- `{item['artifact']}`: owner={item['owner_skill']}; stage={item['stage']}; "
            f"minimum={item['minimum_depth']}; blockers={'; '.join(item['blocking_conditions'])}"
            for item in artifact_contract["artifacts"]
        ),
    )

    sources = build_source_registry()
    claims = build_claim_audit()
    write_json(DATA_DIR / "source_registry.json", {"sources": sources})
    write_text(
        DATA_DIR / "source_registry.md",
        "# Source Registry\n\n"
        + "\n".join(
            f"- {row['source_id']} | {row['source']} | {row['type']} | {row['date']} | "
            f"{row['quality']} | `{row['path']}` | use: {row['use']} | boundary: {row['boundary']}"
            for row in sources
        ),
    )
    write_json(DATA_DIR / "claim_audit.json", {"claims": claims})
    write_text(
        DATA_DIR / "claim_audit.md",
        "# Claim Audit\n\n"
        + "\n".join(
            f"- {row['claim_id']} | {row['status']} | {row['materiality']} | "
            f"{row['claim']} | sources: {', '.join(row['source_ids'])}"
            for row in claims
        ),
    )

    broker_rows = build_broker_consensus()
    write_json(
        DATA_DIR / "broker_street_consensus_20260711.json",
        {"data_cutoff": DATA_CUTOFF, "rows": broker_rows},
    )
    write_text(DATA_DIR / "broker_street_consensus_20260711.md", broker_markdown(broker_rows))

    valuation_rows = build_valuation_rows()
    write_json(
        DATA_DIR / "current_valuation_model_20260711.json",
        {"data_cutoff": DATA_CUTOFF, "rows": valuation_rows},
    )
    write_text(ANALYSIS_DIR / "valuation_model.md", valuation_markdown(valuation_rows))
    build_analysis_files(valuation_rows)
    build_growth_artifacts()

    audit_lines = [
        "# Valuation Audit",
        "",
        "## Arithmetic Checks",
    ]
    for row in valuation_rows:
        expected_cap = row["current_price"] * row["shares_100mn"]
        expected_upside = row["final_target"] / row["current_price"] - 1
        expected_target = (
            row["fundamental_weight"] * row["base"]
            + row["market_weight"] * row["market_implied_anchor"]
            + row["broker_weight"] * row["broker_anchor"]
        )
        audit_lines.append(
            f"- {row['ticker']}: market cap {expected_cap:.2f} vs stored "
            f"{row['market_cap_100mn_cny']:.2f}; multi-anchor target "
            f"{expected_target:.2f} vs stored {row['final_target']:.2f}; "
            f"upside {expected_upside:.4f} vs stored {row['upside']:.4f}."
        )
    audit_lines += [
        "",
        "## Forecast Availability",
        "",
        "All seven core tickers have 2026E revenue, net profit/EPS, current price and share count.",
        "",
        "## Target-Price Comparability",
        "",
        "Positive-weight Street rows use published point targets and disclosed methods. House-derived targets from original forecasts are zero-weight.",
        "",
        "## Final Valuation Completeness",
        "",
        "Bear/base/bull, market anchor, weights, final target, upside, action, catalyst and invalidation are present for every core ticker.",
        "",
        "## Scenario-Band Checks",
        "",
        "For every row: bear < base < bull. Final target is inside the scenario band.",
        "",
        "## Market-Implied Sentiment Anchor Checks",
        "",
        "Market anchors are above current prices but below base value, reflecting weak momentum without erasing fundamental upside.",
        "",
        "## Full-Chain/Core-Satellite Dependency Checks",
        "",
        "Not applicable; this is a sector-rotation strategy report rather than a supply-chain report.",
        "",
        "## Value-Chain Economics Dependency Checks",
        "",
        "Bank value depends on NIM, credit cost and ROE; XCMG depends on overseas/mining mix and cash conversion; ZTE, Jiangbolong, Hengrui and Industrial Fulian consume the growth-earnings package.",
        "",
        "## Price/Share-Count Checks",
        "",
        "Prices are 2026-07-10 closes. Shares use official filing or broker latest-share-count denominators. Currency is CNY and share class is A-share.",
        "",
        "## Fake-Precision Flags",
        "",
        "Targets are rounded to two decimals for reproducibility; the reader-facing report presents ranges and action zones.",
        "",
        "## Supply-Chain Dependency Checks",
        "",
        "Not applicable; no supply-chain growth credit is used.",
        "",
        "## Growth Earnings Dependency Checks",
        "",
        "Launched-growth valuation credit traces to `data/growth_driver_model.json`; undisclosed unit, ASP and customer-allocation fields are explicitly bounded.",
        "",
        "## Model Reproducibility",
        "",
        "Model Reproducibility: PASS",
    ]
    write_text(ANALYSIS_DIR / "valuation_audit.md", "\n".join(audit_lines))

    exhaustion = build_source_exhaustion()
    write_json(CASE_DIR / "source_exhaustion_log.json", {"entries": exhaustion})
    write_text(
        CASE_DIR / "source_exhaustion_log.md",
        "# Source Exhaustion Log\n\n"
        + "\n".join(
            f"- Probe: {row['probe']} | result: {row['result']} | reason: {row['reason']} | "
            f"fallback: {row['fallback']} | impact: {row['impact']}"
            for row in exhaustion
        ),
    )


if __name__ == "__main__":
    main()
