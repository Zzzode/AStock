#!/usr/bin/env python3
"""Generate the Atlas 950 case supply-chain evidence package.

This generator keeps the Markdown/JSON twins synchronized. It intentionally
separates Atlas-specific evidence from generic AIDC product capability.
"""

from __future__ import annotations

import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
CUTOFF = "2026-07-18"


def node(
    node_id: str,
    block: str,
    subsegment: str,
    name: str,
    node_type: str,
    ticker: str,
    role: str,
    product: str,
    anchor: str,
    evidence: str,
    source_count: int,
    source: str,
    gap: str,
    classification: str,
    valuation_status: str,
    market: str = "China",
) -> dict:
    return {
        "node_id": node_id,
        "chain_block": block,
        "subsegment": subsegment,
        "node_name": name,
        "node_type": node_type,
        "listed_ticker": ticker,
        "market": market,
        "company_status": "listed" if node_type == "listed" else node_type,
        "chain_role": role,
        "product_or_service": product,
        "demand_anchor_or_customer": anchor,
        "evidence_status": evidence,
        "source_count": source_count,
        "strongest_source": source,
        "evidence_gap": gap,
        "classification": classification,
        "valuation_status": valuation_status,
        "next_verification_path": "Obtain official customer qualification, Atlas 950 BOM/order, shipment, ASP, utilization, and margin evidence.",
        "upgrade_trigger": "An official filing or customer-side source identifies the Atlas 950 product, order, certification, revenue exposure, and margin conversion.",
    }


BLOCKS = {
    "B1": "Compute platform and accelerator demand anchors",
    "B2": "Server, OEM, ODM and rack integration",
    "B3": "Power, UPS, transformer and electrical infrastructure",
    "B4": "Thermal management and liquid cooling",
    "B5": "Optical, networking and interconnect",
    "B6": "Storage, memory and HBM",
    "B7": "PCB, CCL, connectors, cables and precision components",
    "B8": "IDC, cloud, operator and downstream applications",
}


ROWS = [
    node("FC001", BLOCKS["B1"], "AI accelerator", "Huawei Ascend 950DT", "private", "not listed", "Primary compute engine", "1 PFLOPS FP8 / 2 PFLOPS FP4 planning target; 144 GB HiZQ 2.0 memory", "Atlas 950 SuperPoD", "official roadmap", 2, "HUAWEI-20250918", "Independent benchmark, yield, shipment and cost are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC002", BLOCKS["B1"], "SuperPoD platform", "Huawei Atlas 950 SuperPoD", "private", "not listed", "System demand anchor", "1024-card physical deployment; architecture planned to scale to 8192 cards", "Large-model training and high-concurrency inference", "official physical disclosure", 3, "HUAWEI-20260717", "The physical system is not evidence of volume shipment or third-party performance.", "demand_anchor", "not investable", market="China private"),
    node("FC003", BLOCKS["B1"], "AI accelerator competitor", "NVIDIA Rubin NVL platform", "overseas", "NVDA.US", "Global architecture benchmark", "Rack-scale GPU platform and NVLink fabric", "Global hyperscalers", "official benchmark context", 1, "NVIDIA-OFFICIAL", "Cross-vendor low-precision peak figures are not workload-equivalent.", "out_of_scope", "benchmark only", market="United States"),
    node("FC004", BLOCKS["B1"], "AI accelerator competitor", "AMD Instinct / UALink ecosystem", "overseas", "AMD.US", "Global alternative platform", "GPU and open scale-up interconnect ecosystem", "Global cloud and OEM platforms", "official ecosystem context", 1, "AMD-UALINK-OFFICIAL", "Product timing and system-scale comparability remain incomplete.", "out_of_scope", "benchmark only", market="United States"),
    node("FC005", BLOCKS["B1"], "Model training application", "iFlytek", "listed", "002230.SZ", "Explicit downstream platform validator", "Flagship-model co-development on Ascend 950", "Huawei Ascend 950", "official-disclosed", 2, "CNINFO-002230-FY2025", "No Atlas 950 procurement amount, compute cost, or revenue contribution is disclosed.", "core_valuation", "eligible for downstream validation valuation, not supplier valuation"),
    node("FC006", BLOCKS["B1"], "Domestic accelerator competitors", "Cambricon / Hygon / Moore Threads", "listed", "688256.SH / 688041.SH / 688795.SH", "Domestic compute alternatives", "AI accelerators and compute platforms", "Chinese AI infrastructure", "official product context", 1, "PUBLIC-FILINGS", "These are competitors or alternatives, not Atlas suppliers.", "out_of_scope", "peer context"),

    node("FC007", BLOCKS["B2"], "SuperPoD system integration", "Huawei computing product line", "private", "not listed", "Atlas 950 system owner and integrator", "Compute cabinets, communication cabinets, UnifiedBus and system software", "Operators, cloud and enterprise customers", "official-disclosed", 3, "HUAWEI-20260717", "Supplier allocation and subsystem BOM are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC008", BLOCKS["B2"], "Server ecosystem", "Talkweb Information / Zhaohan", "listed", "002261.SZ", "Ascend server and intelligent-compute ecosystem partner", "Kunpeng+Ascend servers and appliances", "Huawei ecosystem and industry customers", "official-disclosed", 2, "CNINFO-002261-FY2025", "No Atlas 950 qualification or order is disclosed; 2025 recurring earnings were weak.", "satellite_watch", "watchlist only pending Atlas qualification and recurring profit"),
    node("FC009", BLOCKS["B2"], "Server ecosystem", "Digital China / Kuntai", "listed", "000034.SZ", "Domestic AI infrastructure and server ecosystem", "Kuntai compute/network products and AI infrastructure services", "Enterprise and public-sector customers", "official-disclosed", 2, "CNINFO-000034-IR20260402", "AI-related revenue includes distribution and is not Atlas-specific; profit purity is low.", "satellite_watch", "conditional valuation"),
    node("FC010", BLOCKS["B2"], "Server OEM", "xFusion", "private", "not listed", "Major domestic server OEM reference", "General and AI servers", "Operators and enterprise customers", "industry context", 1, "COMPANY-OFFICIAL", "Atlas 950 subsystem role is not disclosed.", "out_of_scope", "private benchmark", market="China private"),
    node("FC011", BLOCKS["B2"], "Server OEM competitor", "Inspur Information", "listed", "000977.SZ", "Domestic server competitor / integrator", "AI servers and clusters", "Cloud, operator and enterprise customers", "official product capability", 1, "CNINFO-FILING", "No evidence of being an Atlas 950 supplier.", "satellite_watch", "generic AIDC only"),
    node("FC012", BLOCKS["B2"], "Rumored ODM mapping", "Sichuan Changhong", "low_purity", "600839.SH", "Explicitly excluded rumored server ODM", "Company stated it does not conduct the claimed AI-server ODM business", "not applicable", "official denial", 1, "CNINFO-600839-IR20260514", "Market mapping conflicts with the company's answer.", "out_of_scope", "exclude from Atlas 950 beneficiary list"),

    node("FC013", BLOCKS["B3"], "Integrated power", "Huawei Digital Power", "private", "not listed", "Internal/affiliate power-system reference", "UPS, power conversion and data-center energy systems", "Huawei and third-party data centers", "company capability context", 1, "HUAWEI-OFFICIAL", "Atlas 950 internal sourcing and external share are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC014", BLOCKS["B3"], "UPS and integrated infrastructure", "Kehua Data", "listed", "002335.SZ", "AIDC power and liquid-cooling infrastructure provider", "UPS, modular data center, liquid-cooling POD and sidecar", "Domestic compute centers", "official-disclosed", 2, "CNINFO-002335-FY2025", "Company serves Ascend innovation infrastructure but no Atlas 950 order is disclosed.", "satellite_watch", "conditional valuation"),
    node("FC015", BLOCKS["B3"], "HVDC power", "Zhongheng Electric", "listed", "002364.SZ", "Data-center power equipment", "HVDC and power systems", "Data centers and telecom customers", "official product capability", 1, "CNINFO-FILING", "Huawei/Atlas customer, order, ASP and segment margin are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC016", BLOCKS["B3"], "Transformer and magnetic components", "Eaglerise Electric", "listed", "002922.SZ", "Power conversion and transformer candidate", "High-frequency transformer and power magnetic components", "AIDC power systems", "official product capability", 1, "CNINFO-FILING", "Atlas linkage and AIDC revenue share are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC017", BLOCKS["B3"], "UPS", "KSTAR", "listed", "002518.SZ", "UPS and infrastructure candidate", "UPS and data-center power products", "Data centers", "official product capability", 1, "CNINFO-FILING", "Atlas linkage is not disclosed.", "satellite_watch", "generic AIDC only"),
    node("FC018", BLOCKS["B3"], "Busway / transformer / backup power", "Atlas-specific electrical BOM", "unavailable", "not available", "Missing high-density electrical node", "Busway, switchgear, transformer, backup generation and power shelf", "Atlas 950 deployment", "not found", 0, "SOURCE-GAP", "Per-rack power density, supplier list, equipment value and delivery cycle are not public.", "unavailable", "blocks Atlas-specific earnings credit"),

    node("FC019", BLOCKS["B4"], "End-to-end liquid cooling", "Shenling Environment", "listed", "301018.SZ", "Huawei-related data-service thermal supplier", "CDU, manifold, cold source, pipework, quick connectors and cold plates", "Huawei/H company and major cloud/colo customers", "official-disclosed", 3, "CNINFO-301018-FY2025", "Huawei is named as a historical customer, but Atlas 950 order and product allocation are not disclosed.", "core_valuation", "eligible for broader Huawei/AIDC liquid-cooling valuation"),
    node("FC020", BLOCKS["B4"], "End-to-end liquid cooling", "Envicool", "listed", "002837.SZ", "Liquid-cooling platform leader", "Cold plates, CDU, manifolds, quick connectors and facility cooling", "Compute chip, equipment, cloud and colocation customers", "official-disclosed", 2, "CNINFO-002837-FY2025", "Named Atlas/Huawei customer, revenue split and order value are not disclosed.", "core_valuation", "eligible for broader AIDC thermal valuation; Atlas optionality only"),
    node("FC021", BLOCKS["B4"], "Industrial liquid cooling", "Tongfei", "listed", "300990.SZ", "Liquid-cooling equipment candidate", "CDU and industrial/compute cooling", "Industrial and data-center customers", "official product capability", 1, "CNINFO-FILING", "Atlas customer and AI segment economics are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC022", BLOCKS["B4"], "Liquid-cooling system", "Gaolan", "listed", "300499.SZ", "Thermal-management candidate", "Liquid-cooling systems and components", "Compute and power customers", "official product capability", 1, "CNINFO-FILING", "Atlas customer, orders and margin are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC023", BLOCKS["B4"], "Liquid-cooling connectors", "Aerospace Electric", "listed", "002025.SZ", "High-speed and liquid-cooling connector candidate", "Backplane/high-speed connectors, liquid-cooling connectors and pipes", "Undisclosed downstream compute customers", "official product capability", 2, "CNINFO-002025-IR20260420", "The investor question named Ascend 950, but the company answer did not confirm that customer or platform.", "satellite_watch", "watchlist only / insufficient customer evidence"),
    node("FC024", BLOCKS["B4"], "Coolant, pumps and valves", "Atlas-specific fluid subsystem", "unavailable", "not available", "Missing fluid-loop BOM", "Coolant, pump, valve, seals and monitoring", "Atlas 950 deployment", "not found", 0, "SOURCE-GAP", "Fluid specification, supplier, unit value, maintenance economics and qualification are not public.", "unavailable", "blocks Atlas-specific earnings credit"),

    node("FC025", BLOCKS["B5"], "Scale-up interconnect", "Huawei UnifiedBus / Lingqu", "private", "not listed", "Core scale-up fabric", "Unified memory addressing, TB-class NPU links and optical cabinet interconnect", "Atlas 950", "official-disclosed", 3, "HUAWEI-20250918", "Switch silicon, topology, optical-port count and component suppliers are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC026", BLOCKS["B5"], "Optical switching / OCS", "Huawei optical cabinet interconnect", "private", "not listed", "Inter-cabinet optical fabric", "All-optical links between compute and communication cabinets", "Atlas 950", "official-disclosed at architecture level", 1, "HUAWEI-20250918", "OCS architecture, suppliers and optical BOM are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC027", BLOCKS["B5"], "Optical modules and engines", "HGTECH", "listed", "000988.SZ", "High-speed optical and copper interconnect candidate", "800G/1.6T modules, 3.2T optical engines, AEC/ACC and liquid-cooling paths", "Global AI infrastructure customers", "official-disclosed product and delivery", 3, "CNINFO-000988-FY2025", "No official Atlas 950 customer, share, exclusive-supply or order evidence.", "core_valuation", "eligible for broader AI interconnect valuation; Atlas optionality only"),
    node("FC028", BLOCKS["B5"], "Optical modules", "Accelink Technologies", "listed", "002281.SZ", "Domestic optical-module candidate", "High-speed optical modules and components", "Telecom and data-center customers", "official product capability", 1, "CNINFO-FILING", "Atlas-specific customer and order are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC029", BLOCKS["B5"], "Optical components", "TFC Optical / Advanced Fiber Resources", "listed", "300394.SZ / 300620.SZ", "Precision optical component candidates", "Optical engines, passive components and fiber devices", "Optical-module makers and cloud platforms", "official product capability", 1, "CNINFO-FILINGS", "Domestic Atlas allocation and product value are not disclosed.", "satellite_watch", "generic AI optical exposure"),
    node("FC030", BLOCKS["B5"], "High-speed copper cable", "Woer / Zhaolong Interconnect mapping", "listed", "002130.SZ / 300913.SZ", "AEC/ACC and high-speed cable candidate", "High-speed copper connectivity", "AI server and switch platforms", "official product capability", 1, "CNINFO-FILINGS", "Atlas qualification and revenue exposure are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC031", BLOCKS["B5"], "High-speed connector", "Dingtong Technology", "listed", "688668.SH", "Connector candidate", "High-speed connectors and precision components", "Communication and compute customers", "official product capability", 1, "CNINFO-FILING", "Atlas customer, port count and ASP are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC032", BLOCKS["B5"], "Switch/NIC silicon", "Huawei in-house switch and NIC stack", "private", "not listed", "Networking silicon control point", "Switch ASIC, NIC and fabric control", "Atlas 950", "inferred from system ownership", 0, "SOURCE-GAP", "Public technical disclosure is insufficient to assign A-share supplier exposure.", "unavailable", "no A-share valuation credit", market="China private"),

    node("FC033", BLOCKS["B6"], "HBM-like memory", "Huawei HiZQ 2.0", "private", "not listed", "950DT memory subsystem", "144 GB capacity and 4 TB/s bandwidth planning target", "Ascend 950DT", "official roadmap", 1, "HUAWEI-20250918", "Manufacturer, die source, packaging, yield, cost and shipment are not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC034", BLOCKS["B6"], "DRAM wafer manufacturing", "Domestic DRAM manufacturing mapping", "unavailable", "not available", "Potential upstream memory node", "DRAM/HBM-class dies", "Huawei memory subsystem", "rumor / not confirmed", 0, "SOURCE-GAP", "No official evidence identifies a manufacturer for HiZQ 2.0.", "unavailable", "blocks valuation"),
    node("FC035", BLOCKS["B6"], "Memory interface", "Montage Technology", "listed", "688008.SH", "Server-memory interface beneficiary candidate", "DDR5/DDR6 memory interface chips", "General AI servers", "official product capability", 1, "CNINFO-FILING", "950DT uses an integrated memory subsystem; Atlas-specific interface content is not disclosed.", "satellite_watch", "generic server-memory exposure"),
    node("FC036", BLOCKS["B6"], "SPD / EEPROM", "Giantec Semiconductor", "listed", "688123.SH", "Server-memory supporting-chip candidate", "SPD and EEPROM", "General DDR5 server memory", "official product capability", 1, "CNINFO-FILING", "Atlas-specific content is not disclosed.", "satellite_watch", "generic server exposure"),
    node("FC037", BLOCKS["B6"], "Enterprise SSD", "Biwin / Longsys / Datalink", "listed", "688525.SH / 301308.SZ / 001309.SZ", "Storage capacity candidates", "Enterprise SSD and storage products", "AI training data and KV cache", "official product capability", 1, "CNINFO-FILINGS", "Atlas 950 storage architecture, qualification and order share are not disclosed.", "satellite_watch", "generic AIDC storage exposure"),

    node("FC038", BLOCKS["B7"], "High-speed CCL", "Shengyi Technology", "listed", "600183.SH", "High-speed laminate candidate", "Low-loss/high-speed CCL", "AI server, switch and communication boards", "official product capability", 1, "CNINFO-FILING", "Atlas-specific material grade, layer stack, qualification and volume are not disclosed.", "satellite_watch", "generic AI PCB exposure"),
    node("FC039", BLOCKS["B7"], "High-speed PCB", "Shennan Circuits", "listed", "002916.SZ", "Server/switch PCB and substrate candidate", "High-layer PCB and packaging substrate", "Communication and data-center customers", "official product capability", 1, "CNINFO-FILING", "Atlas-specific board, substrate and customer allocation are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC040", BLOCKS["B7"], "High-speed PCB", "WUS Printed Circuit", "listed", "002463.SZ", "High-speed PCB candidate", "High-layer/high-speed server and switch PCB", "AI infrastructure customers", "official product capability", 1, "CNINFO-FILING", "Atlas-specific qualification and revenue are not disclosed.", "satellite_watch", "generic AI PCB exposure"),
    node("FC041", BLOCKS["B7"], "High-density PCB", "Victory Giant Technology", "listed", "300476.SZ", "High-density AI PCB candidate", "High-layer and high-density PCB", "Global AI compute platforms", "official product capability", 1, "CNINFO-FILING", "Huawei/Atlas customer and revenue allocation are not disclosed.", "satellite_watch", "generic AI PCB exposure"),
    node("FC042", BLOCKS["B7"], "ABF substrate / PCB", "Fastprint", "listed", "002436.SZ", "Packaging-substrate and PCB optionality", "IC substrate and high-end PCB", "Advanced packaging and compute customers", "official product capability", 1, "CNINFO-FILING", "Ascend 950 substrate allocation and economics are not disclosed.", "satellite_watch", "watchlist only"),
    node("FC043", BLOCKS["B7"], "Probe card", "Qiangyi Technology", "listed", "688809.SH", "Chip-test optionality candidate", "Probe cards for semiconductor testing", "Undisclosed chip customers", "company did not confirm", 1, "CNINFO-688809-IR20260511", "The company declined to confirm Ascend 950 or memory customers.", "satellite_watch", "watchlist only / insufficient customer evidence"),

    node("FC044", BLOCKS["B8"], "Cloud platform", "Huawei Cloud", "private", "not listed", "Cloud deployment and service demand anchor", "CloudMatrix/Ascend cloud services", "Enterprise and model customers", "official demand anchor", 1, "HUAWEI-OFFICIAL", "Atlas 950 purchase/deployment volume is not disclosed.", "demand_anchor", "not investable", market="China private"),
    node("FC045", BLOCKS["B8"], "Telecom operator", "China Mobile", "listed", "600941.SH / 00941.HK", "Operator demand anchor", "Intelligent-compute centers and network infrastructure", "Enterprise and public-sector workloads", "official demand anchor", 1, "OPERATOR-FILING", "Atlas 950 deployment and economics are not disclosed.", "demand_anchor", "do not value as upstream supplier"),
    node("FC046", BLOCKS["B8"], "Telecom operator", "China Telecom", "listed", "601728.SH / 00728.HK", "Operator demand anchor", "Cloud and intelligent-compute infrastructure", "Enterprise and public-sector workloads", "official demand anchor", 1, "OPERATOR-FILING", "Atlas 950 deployment and economics are not disclosed.", "demand_anchor", "do not value as upstream supplier"),
    node("FC047", BLOCKS["B8"], "Telecom operator", "China Unicom", "listed", "600050.SH / 00762.HK", "Operator demand anchor", "Cloud and intelligent-compute infrastructure", "Enterprise and public-sector workloads", "official demand anchor", 1, "OPERATOR-FILING", "Atlas 950 deployment and economics are not disclosed.", "demand_anchor", "do not value as upstream supplier"),
    node("FC048", BLOCKS["B8"], "Model application", "iFlytek", "listed", "002230.SZ", "Direct Ascend 950 software/model validation", "Flagship-model training and inference", "Education, healthcare, enterprise and government users", "official-disclosed", 2, "CNINFO-002230-FY2025", "The link supports platform adoption, not an upstream supplier order or guaranteed model revenue.", "core_valuation", "downstream event-driven valuation only"),
    node("FC049", BLOCKS["B8"], "IDC / colocation", "Domestic IDC operators", "listed", "300738.SZ / 300442.SZ / 600845.SH", "Facility demand and deployment anchors", "Data-center capacity and colocation", "Cloud, operator and enterprise customers", "official capacity context", 1, "CNINFO-FILINGS", "No Atlas 950 signed capacity, utilization or contract is disclosed.", "satellite_watch", "generic AIDC exposure"),
    node("FC050", BLOCKS["B8"], "Policy and public compute", "National and local intelligent-compute programs", "demand_anchor", "not applicable", "Policy demand anchor", "Compute-network and public AI infrastructure programs", "Public-sector and industry users", "official policy context", 1, "GOVERNMENT-OFFICIAL", "Policy budget does not prove company orders or margins.", "demand_anchor", "context only"),
]


def relationship(
    ticker: str,
    company: str,
    layer: str,
    upstream: str,
    product: str,
    downstream: str,
    relation_type: str,
    confidence: str,
    source_tier: str,
    score: int,
    revenue: str,
    capacity: str,
    orders: str,
    price: str,
    utilization: str,
    earnings: str,
    source: str,
    gap: str,
    eligibility: str,
    trigger: str,
    used: bool,
) -> dict:
    return {
        "ticker": ticker,
        "company": company,
        "chain_layer": layer,
        "node_type": "listed",
        "upstream_input": upstream,
        "product_or_process": product,
        "downstream_customer_or_platform": downstream,
        "relationship_type": relation_type,
        "confidence": confidence,
        "source_tier": source_tier,
        "evidence_score": score,
        "revenue_exposure": revenue,
        "capacity_or_certification": capacity,
        "order_visibility": orders,
        "ASP_or_price_proxy": price,
        "utilization_or_yield": utilization,
        "margin_or_earnings_impact": earnings,
        "source": source,
        "evidence_gap": gap,
        "valuation_eligibility": eligibility,
        "downgrade_trigger": trigger,
        "used_in_valuation": used,
    }


RELATIONSHIPS = [
    relationship("301018.SZ", "Shenling Environment", "liquid cooling", "compressors, heat exchangers, pumps, valves and controls", "CDU, manifold, cold source, pipework, quick connector and cold plate", "Huawei/H company plus cloud and colo customers", "official-disclosed", "high for general customer relation; low for Atlas-specific order", "official_filing", 82, "2025 data-service revenue +51.42%; Atlas share not disclosed", "New thermal manufacturing base commissioned; exact capacity not disclosed", "2025 data-service new orders +72%; customer-level allocation not disclosed", "not disclosed", "not disclosed", "2025 company revenue CNY4.209bn and NP CNY216.8m; Atlas contribution not disclosed", "CNINFO-301018-FY2025", "No Atlas 950 qualification, order, ASP, utilization or margin split", "eligible for broader Huawei/AIDC liquid-cooling valuation", "Downgrade if data-service orders or margin decelerate, or Huawei relationship cannot be linked to liquid-cooling delivery", True),
    relationship("000988.SZ", "HGTECH", "optical/networking", "optical chips, DSP, PCB, connectors and thermal components", "800G/1.6T modules, 3.2T optical engines, AEC/ACC and liquid-cooling path", "Global AI-infrastructure customers; Huawei/Atlas not disclosed", "official-disclosed product capability", "medium; low for Atlas-specific link", "official_filing", 74, "2025 connection revenue CNY6.097bn, +53.39%; Atlas share not disclosed", "Wuhan and Thailand capacity commissioned; exact Atlas allocation not disclosed", "Customer deliveries expanded; named Atlas order not disclosed", "not disclosed", "Production running at high load per company media; Atlas allocation not disclosed", "2025 company NP CNY1.471bn, +20.48%; product-margin bridge incomplete", "CNINFO-000988-FY2025", "Exclusive-supplier and Huawei share claims are unverified", "eligible for broader AI optical valuation; Atlas optionality only", "Downgrade if 800G+ shipment growth or connection-business margin misses", True),
    relationship("002837.SZ", "Envicool", "liquid cooling", "heat exchangers, pumps, valves, quick connectors and refrigerants", "Full-chain liquid-cooling products and systems", "Compute chip, equipment, cloud and colocation customers; names not disclosed", "official-disclosed product capability", "medium; low for Atlas-specific link", "official_filing", 72, "2025 revenue CNY6.068bn, +32.23%; Atlas share not disclosed", "Full-chain capability; exact compute-liquid-cooling capacity not disclosed", "Customer and order values not disclosed", "not disclosed", "not disclosed", "2025 NP CNY521.9m, +15.30%; mix and margin need verification", "CNINFO-002837-FY2025", "No named Atlas/Huawei customer, order, ASP or segment margin", "eligible for broader AIDC thermal valuation; Atlas optionality only", "Downgrade if compute-liquid-cooling growth or gross margin fails to validate", True),
    relationship("002230.SZ", "iFlytek", "downstream model application", "Ascend compute, CANN and model-training software", "Flagship-model co-development and training on Ascend 950", "Huawei Ascend 950 platform", "official-disclosed", "high for co-development", "official_filing", 90, "No Ascend 950-specific revenue disclosed", "Software/model capability; no hardware capacity concept", "No procurement or order amount disclosed", "Compute cost not disclosed", "Training efficiency not yet disclosed", "Model launch may affect AI platform economics; contribution not disclosed", "CNINFO-002230-FY2025", "No compute spend, efficiency benchmark or model revenue bridge", "eligible for downstream event-driven valuation only", "Downgrade if the October 2026 launch slips or fails cost/performance validation", True),
    relationship("002261.SZ", "Talkweb Information", "server/OEM ecosystem", "Huawei Ascend/Kunpeng components and software", "Zhaohan Ascend servers and AI appliances", "Huawei ecosystem and industry compute centers", "official-disclosed", "high for Huawei relationship; low for Atlas-specific role", "official_filing", 86, "Huawei represented 41.51% of 2025 sales; product/customer split not disclosed", "Certified Ascend component and Kunpeng system partner", "Atlas 950 order not disclosed", "not disclosed", "not disclosed", "2025 NP CNY63.7m but recurring NP -CNY40.2m", "CNINFO-002261-FY2025", "No Atlas 950 product qualification; high customer concentration and weak recurring profitability", "watchlist only pending recurring profit and Atlas qualification", "Downgrade if intelligent-compute subsidiary losses persist or Huawei concentration rises without cash conversion", False),
    relationship("000034.SZ", "Digital China", "server/OEM and distribution", "Kuntai hardware, third-party cloud and compute products", "Domestic AI infrastructure products and services", "Enterprise and public-sector customers", "official-disclosed", "medium", "company_ir", 68, "2025 AI-related revenue CNY33.03bn, +47.7%, but includes broad distribution", "Kuntai compute/network product system; exact capacity not disclosed", "Atlas order not disclosed", "not disclosed", "not disclosed", "AI revenue is high but margin/profit purity is low and not Atlas-specific", "CNINFO-000034-IR20260402", "No Atlas-specific product, gross profit or customer-order split", "conditional valuation", "Downgrade if self-brand product profit lags headline AI revenue", False),
    relationship("002335.SZ", "Kehua Data", "power and liquid cooling", "power electronics, cooling components and control systems", "UPS, 200kW-1.5MW CDU, 40-120kW/rack POD and sidecar", "Domestic compute centers including an Ascend innovation center", "official-disclosed", "medium", "official_filing", 70, "AIDC product revenue split not disclosed", "Published product specifications; capacity not disclosed", "Atlas order not disclosed", "not disclosed", "not disclosed", "Project margin and working-capital conversion not disclosed", "CNINFO-002335-FY2025", "No Atlas customer, order, ASP or product-margin evidence", "watchlist only / insufficient customer evidence", "Upgrade only with Atlas/Huawei qualification and order economics", False),
    relationship("002130.SZ", "Woer Heat-Shrinkable Material", "high-speed copper connectivity", "copper conductor, insulation material, connector and assembly inputs", "High-speed copper cable materials and assemblies", "AI server and switch platforms; Huawei/Atlas allocation not disclosed", "official product capability", "medium for broader AI copper demand; low for Atlas", "official_filing", 55, "2026E broker revenue CNY12.15bn and NP CNY1.88bn; Atlas share not disclosed", "High-speed cable capacity expansion is disclosed without Atlas allocation", "Atlas qualification and order not disclosed", "not disclosed", "not disclosed", "Broader high-speed copper earnings bridge is modeled; Atlas contribution remains zero", "CNINFO-FILING", "No Huawei/Atlas customer, qualification, volume, ASP or margin evidence", "eligible for broader high-speed-copper valuation; Atlas optionality only", "Downgrade if high-speed-cable qualification, utilization or margin misses", True),
    relationship("002025.SZ", "Aerospace Electric", "connectors and liquid-cooling components", "metals, engineering plastics, seals and precision machining", "High-speed/backplane connectors, liquid-cooling connectors and pipes", "Undisclosed compute customers", "official-disclosed product capability", "medium for product; low for Atlas customer", "official_filing", 62, "Compute-product revenue not disclosed", "Product portfolio disclosed; capacity not disclosed", "not disclosed", "not disclosed", "not disclosed", "2025 profit declined; AI connector contribution not disclosed", "CNINFO-002025-IR20260420", "Question named Ascend 950 but answer did not confirm it", "watchlist only / insufficient customer evidence", "Upgrade only with named platform qualification and revenue/margin evidence", False),
    relationship("002281.SZ", "Accelink", "optical/networking", "optical chips, components, PCB and DSP", "High-speed optical modules and components", "Telecom and data-center customers", "official product capability", "medium for product; low for Atlas link", "official_filing", 58, "Atlas exposure not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "CNINFO-FILING", "No Atlas customer/order/ASP evidence", "watchlist only", "Upgrade with named domestic scale-up platform qualification", False),
    relationship("600183.SH", "Shengyi Technology", "CCL", "resin, glass cloth and copper foil", "High-speed low-loss CCL", "AI server and switch PCB makers", "official product capability", "medium for general AI; low for Atlas", "official_filing", 56, "Atlas exposure not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "Product-mix uplift not tied to Atlas", "CNINFO-FILING", "No material grade, customer qualification, volume or margin for Atlas", "watchlist only", "Upgrade with Atlas board qualification and mix/ASP evidence", False),
    relationship("002916.SZ", "Shennan Circuits", "PCB/substrate", "CCL, copper foil, chemicals and equipment", "High-layer PCB and packaging substrate", "Communication and compute customers", "official product capability", "medium for general AI; low for Atlas", "official_filing", 56, "Atlas exposure not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "No Atlas earnings bridge", "CNINFO-FILING", "No Atlas qualification/order/layer-stack economics", "watchlist only", "Upgrade with official platform qualification and margin impact", False),
    relationship("002463.SZ", "WUS Printed Circuit", "PCB", "CCL, copper foil and process chemicals", "High-speed/high-layer PCB", "AI server and switch platforms", "official product capability", "medium for general AI; low for Atlas", "official_filing", 55, "Atlas exposure not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "No Atlas earnings bridge", "CNINFO-FILING", "No Huawei/Atlas customer allocation", "watchlist only", "Upgrade with official domestic platform qualification", False),
    relationship("300476.SZ", "Victory Giant Technology", "PCB", "CCL, copper foil and process chemicals", "High-density AI PCB", "Global AI compute platforms", "official product capability", "medium for global AI; low for Atlas", "official_filing", 54, "Atlas exposure not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "No Atlas earnings bridge", "CNINFO-FILING", "Huawei/Atlas mapping is unverified", "watchlist only", "Upgrade with official Huawei/Atlas qualification", False),
    relationship("688809.SH", "Qiangyi Technology", "semiconductor testing", "MEMS and precision probe components", "Probe cards", "Undisclosed semiconductor customers", "not confirmed", "low for Ascend 950", "official_filing", 35, "not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "not disclosed", "CNINFO-688809-IR20260511", "Company declined to confirm Ascend 950 and memory customers", "watchlist only / insufficient customer evidence", "Upgrade only with official customer and volume disclosure", False),
]


CUSTOMER_AUDIT = [
    {
        "ticker": "301018.SZ", "company": "Shenling Environment", "customer_or_platform": "Huawei / H company", "claim_type": "customer relationship", "product_or_process": "Data-service thermal systems including liquid cooling", "certification_status": "Customer relationship disclosed; Atlas-specific certification not disclosed", "order_or_backlog": "Data-service new orders +72% in 2025; customer allocation not disclosed", "ASP_or_price_proxy": "not disclosed", "capacity": "New manufacturing base commissioned; numeric capacity not disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "Data-service revenue +51.42%; Huawei and Atlas shares not disclosed", "margin_impact": "not disclosed", "source_tier": "official_filing", "evidence_score": 82, "source": "CNINFO-301018-FY2025", "evidence_gap": "No Atlas 950 order/product/ASP/margin link", "blocks_valuation": False, "downgrade_trigger": "If broader data-service growth is used as Atlas-specific revenue", "adopted_wording": "Huawei-related AIDC liquid-cooling candidate; no disclosed Atlas 950 order"
    },
    {
        "ticker": "002261.SZ", "company": "Talkweb Information", "customer_or_platform": "Huawei Ascend ecosystem", "claim_type": "ecosystem partnership and customer concentration", "product_or_process": "Ascend servers and intelligent-compute products", "certification_status": "Certified Ascend component partner and Kunpeng system partner", "order_or_backlog": "Atlas 950 order not disclosed", "ASP_or_price_proxy": "not disclosed", "capacity": "not disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "Huawei was 41.51% of 2025 sales across businesses", "margin_impact": "2025 recurring NP was negative", "source_tier": "official_filing", "evidence_score": 86, "source": "CNINFO-002261-FY2025", "evidence_gap": "No Atlas 950 qualification/order and no product-level Huawei margin", "blocks_valuation": True, "downgrade_trigger": "Recurring loss or no Atlas qualification", "adopted_wording": "Direct Ascend ecosystem partner, but Atlas 950 role and recurring profit remain unproven"
    },
    {
        "ticker": "002230.SZ", "company": "iFlytek", "customer_or_platform": "Ascend 950", "claim_type": "downstream co-development", "product_or_process": "Flagship-model training and model-architecture optimization", "certification_status": "Officially disclosed joint work", "order_or_backlog": "No procurement amount disclosed", "ASP_or_price_proxy": "Compute cost not disclosed", "capacity": "not applicable", "utilization_or_yield": "Training efficiency not disclosed", "revenue_exposure": "not disclosed", "margin_impact": "not disclosed", "source_tier": "official_filing", "evidence_score": 90, "source": "CNINFO-002230-FY2025", "evidence_gap": "No compute-cost or revenue bridge", "blocks_valuation": False, "downgrade_trigger": "October 2026 launch delay or weak performance/cost", "adopted_wording": "Explicit Ascend 950 downstream validator, not an upstream supplier"
    },
    {
        "ticker": "000988.SZ", "company": "HGTECH", "customer_or_platform": "Atlas 950", "claim_type": "rumored exclusive optical supplier", "product_or_process": "1.6T/3.2T optical modules and engines", "certification_status": "not found", "order_or_backlog": "not found", "ASP_or_price_proxy": "not disclosed", "capacity": "General AI capacity expanded", "utilization_or_yield": "Atlas allocation not disclosed", "revenue_exposure": "AI connection revenue disclosed only at segment level", "margin_impact": "not disclosed", "source_tier": "rumor", "evidence_score": 15, "source": "SOURCE-GAP", "evidence_gap": "No official Atlas customer, share or exclusivity evidence", "blocks_valuation": True, "downgrade_trigger": "Any valuation that uses rumored Atlas share", "adopted_wording": "Broader AI interconnect beneficiary; Atlas-specific supply relationship unverified"
    },
    {
        "ticker": "002837.SZ", "company": "Envicool", "customer_or_platform": "Atlas 950 / Huawei", "claim_type": "rumored liquid-cooling supplier", "product_or_process": "Full-chain liquid cooling", "certification_status": "not found", "order_or_backlog": "not found", "ASP_or_price_proxy": "not disclosed", "capacity": "not disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "not disclosed", "margin_impact": "not disclosed", "source_tier": "rumor", "evidence_score": 15, "source": "SOURCE-GAP", "evidence_gap": "No named Atlas/Huawei order", "blocks_valuation": True, "downgrade_trigger": "Any Atlas-specific EPS credit", "adopted_wording": "Broader AIDC thermal beneficiary; Atlas-specific supply relationship unverified"
    },
    {
        "ticker": "002025.SZ", "company": "Aerospace Electric", "customer_or_platform": "Ascend 950", "claim_type": "investor-question mapping", "product_or_process": "Backplane/high-speed and liquid-cooling connectors", "certification_status": "Company did not confirm platform", "order_or_backlog": "not disclosed", "ASP_or_price_proxy": "not disclosed", "capacity": "not disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "not disclosed", "margin_impact": "not disclosed", "source_tier": "official_filing", "evidence_score": 45, "source": "CNINFO-002025-IR20260420", "evidence_gap": "The answer confirmed products, not the named customer/platform", "blocks_valuation": True, "downgrade_trigger": "Treating the investor's question as company confirmation", "adopted_wording": "Relevant connector product set; Ascend 950 customer relationship unconfirmed"
    },
    {
        "ticker": "688809.SH", "company": "Qiangyi Technology", "customer_or_platform": "Ascend 950", "claim_type": "probe-card supplier question", "product_or_process": "Probe card", "certification_status": "Company declined to confirm", "order_or_backlog": "not disclosed", "ASP_or_price_proxy": "not disclosed", "capacity": "not disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "not disclosed", "margin_impact": "not disclosed", "source_tier": "official_filing", "evidence_score": 30, "source": "CNINFO-688809-IR20260511", "evidence_gap": "No customer confirmation", "blocks_valuation": True, "downgrade_trigger": "Using a question as evidence", "adopted_wording": "Probe-card optionality only; Ascend 950 relationship not confirmed"
    },
    {
        "ticker": "600839.SH", "company": "Sichuan Changhong", "customer_or_platform": "Ascend AI server ODM", "claim_type": "rumored ODM exposure", "product_or_process": "AI server ODM", "certification_status": "not applicable", "order_or_backlog": "not applicable", "ASP_or_price_proxy": "not applicable", "capacity": "not applicable", "utilization_or_yield": "not applicable", "revenue_exposure": "none under the claimed business", "margin_impact": "none under the claimed business", "source_tier": "official_filing", "evidence_score": 95, "source": "CNINFO-600839-IR20260514", "evidence_gap": "Company explicitly denied conducting the claimed business", "blocks_valuation": True, "downgrade_trigger": "Any inclusion as an Atlas 950 server-ODM beneficiary", "adopted_wording": "Excluded: company said it does not conduct the claimed AI-server ODM business"
    },
]


COMPANY_RECONCILIATION = [
    ("000034.SZ", "神州数码", "服务器/OEM与分销", 1, "广义华为/昇腾生态，中等；Atlas 未确认", "广义业务可估值", "观察", "生态关系不等于 Atlas 订单，分销利润率和现金周转决定倍数"),
    ("000988.SZ", "华工科技", "光互联", 1, "广义 AI 光连接能力，中等；Atlas 未确认", "广义业务可估值", "等待平台订单", "Atlas 卫星身份与全球 AI 光业务估值可以并存"),
    ("600183.SH", "生益科技", "CCL", 1, "广义 AI 材料能力，低；Atlas 规格未知", "广义业务可估值", "避免追高", "按 CCL 盈利估值，不给 Atlas 材料份额"),
    ("002916.SZ", "深南电路", "PCB/封装", 1, "广义 AI PCB 能力，低；Atlas 认证未知", "广义业务可估值", "回调验证", "按已披露 AI 业务估值，不给 Atlas 订单信用"),
    ("002463.SZ", "沪电股份", "PCB", 1, "广义 AI PCB 能力，低；Atlas 客户分配未知", "广义业务可估值", "回调验证", "卫星链节点但可用独立盈利建模"),
    ("300476.SZ", "胜宏科技", "PCB", 1, "全球 AI PCB 能力，中低；Atlas 未确认", "广义业务可估值", "选择性观察", "正空间来自全球 AI 盈利，不来自华为链纯度"),
    ("002837.SZ", "英维克", "液冷", 1, "端到端液冷能力，中；华为/Atlas 分配未确认", "广义业务可估值", "等待毛利恢复", "产品能力支持 AIDC 估值，Atlas 专属信用为零"),
    ("301018.SZ", "申菱环境", "液冷", 1, "华为客户关系高；Atlas 订单低/未确认", "广义业务可估值", "最高关系观察", "关系强度高但估值只计广义数据服务"),
    ("002335.SZ", "科华数据", "供电/液冷", 1, "昇腾邻近项目，中；Atlas 未确认", "广义业务可估值", "等待估值回落", "项目能力支持独立估值，平台专属性不足"),
    ("002130.SZ", "沃尔核材", "高速铜连接", 1, "广义高速连接能力，低；Atlas 未确认", "广义业务可估值", "低纯度价值卫星", "正空间仅依赖原有业务和高速连接景气"),
    ("002230.SZ", "科大讯飞", "下游模型/需求锚", 2, "昇腾 950 协同高；不是硬件供应商", "下游业务可估值", "事件验证", "需求锚可进入软件估值，但不得写成硬件订单"),
    ("002025.SZ", "航天电器", "连接器", 1, "产品能力中；投资者所称平台关系未确认", "广义业务可估值", "关系未确认观察", "问答只确认产品，不确认昇腾 950 客户"),
]


GAPS = [
    ("G01", BLOCKS["B1"], "Ascend 950DT wafer foundry, yield and shipment", "Determines actual production ramp and chip economics", "Huawei roadmap, official product releases and public filings", "Not publicly disclosed", "Huawei or customer shipment disclosure", True, "source-governance / industry"),
    ("G02", BLOCKS["B6"], "HiZQ 2.0 die source, packaging and cost", "Controls memory availability and the 950DT cost/performance trade-off", "Huawei roadmap and memory-industry public sources", "No official supplier identification", "Huawei technical paper or manufacturer filing", True, "source-governance / supply-chain"),
    ("G03", BLOCKS["B2"], "Atlas 950 supplier and subsystem BOM", "Required to distinguish suppliers from ecosystem partners", "Huawei disclosures and listed-company filings", "No public supplier list", "Procurement award, customer certification or company filing", True, "supply-chain-research"),
    ("G04", BLOCKS["B5"], "UnifiedBus switch/OCS topology, optical port count and module suppliers", "Determines optical/networking value per system", "Huawei official architecture material", "Architecture only; BOM unavailable", "Technical whitepaper or supplier qualification", True, "industry / supply-chain"),
    ("G05", BLOCKS["B4"], "Per-rack power density and cooling-loop BOM", "Required for CDU/cold-plate/connector value and margin", "Huawei launch material and thermal-company filings", "Not disclosed", "Product manual, tender or customer design specification", True, "supply-chain-research"),
    ("G06", BLOCKS["B3"], "Power shelf, UPS, busway, transformer and backup-power value", "Required for power-equipment earnings conversion", "Huawei launch material and equipment filings", "Not disclosed", "Tender or supplier order disclosure", True, "supply-chain-research"),
    ("G07", BLOCKS["B7"], "PCB layer count, CCL grade, substrate and connector content", "Required for ASP/mix and margin uplift", "Company filings and public technical material", "No Atlas-specific qualification", "Official board/material qualification", True, "supply-chain-research"),
    ("G08", BLOCKS["B8"], "Atlas 950 customer orders and 2026Q4 shipment volume", "Separates product availability from commercial adoption", "Huawei official releases and operator filings", "No disclosed volume or contract value", "Customer deployment or tender result", True, "source-governance"),
    ("G09", "Cross-chain", "Independent training/inference benchmark and reliability", "Peak FLOPS do not prove workload throughput or availability", "Huawei claims and public system papers", "No independent Atlas 950 benchmark", "Third-party benchmark or customer SOTA training paper", False, "industry-analyst"),
    ("G10", "Cross-chain", "Original broker target-price coverage for final modeled pool", "Needed for an external Street target anchor", "38 original PDFs across 14 priority tickers plus public repositories", "Search complete: explicit targets found for 3/12 modeled names; 9/12 remain not disclosed", "Licensed broker archive or broker official page; missing target receives zero Street weight", True, "reports"),
]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_escape(value: object) -> str:
    return str(value).replace("|", "/").replace("\n", " ")


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(md_escape(v) for v in row) + " |" for row in rows)
    return "\n".join(out)


def build_full_chain() -> None:
    block_summary = {block: sum(1 for row in ROWS if row["chain_block"] == block) for block in BLOCKS.values()}
    payload = {
        "case_id": CASE_DIR.name,
        "cutoff_date": CUTOFF,
        "row_count": len(ROWS),
        "block_count": len(block_summary),
        "block_summary": block_summary,
        "coverage_note": "Full-chain evidence universe. Listed-company relevance is not Atlas-specific supplier proof.",
        "rows": ROWS,
    }
    write_json(DATA_DIR / "full_chain_universe_20260718.json", payload)
    md_rows = [[r["node_id"], r["chain_block"], r["subsegment"], r["node_name"], r["node_type"], r["listed_ticker"], r["evidence_status"], r["source_count"], r["classification"], r["valuation_status"], r["evidence_gap"]] for r in ROWS]
    content = "# Full-Chain Universe\n\n**Cutoff:** 2026-07-18  \n**Coverage pack:** AIDC  \n**Rows:** %d across %d mandatory blocks.\n\nThis universe intentionally includes private, overseas, demand-anchor, low-purity, and unavailable nodes. A listed ticker is not a confirmed Atlas 950 supplier unless a company or customer source says so.\n\n%s\n" % (len(ROWS), len(block_summary), table(["ID", "Block", "Subsegment", "Node", "Type", "Ticker", "Evidence", "Sources", "Class", "Valuation", "Gap"], md_rows))
    (DATA_DIR / "full_chain_universe_20260718.md").write_text(content, encoding="utf-8")


def build_relationships() -> None:
    write_json(DATA_DIR / "supply_chain_relationships.json", {"case_id": CASE_DIR.name, "cutoff_date": CUTOFF, "row_count": len(RELATIONSHIPS), "rows": RELATIONSHIPS})
    keys = ["ticker", "company", "chain_layer", "product_or_process", "downstream_customer_or_platform", "confidence", "evidence_score", "revenue_exposure", "order_visibility", "evidence_gap", "valuation_eligibility", "used_in_valuation"]
    rows = [[r[k] for k in keys] for r in RELATIONSHIPS]
    (DATA_DIR / "supply_chain_relationships.md").write_text("# Supply-Chain Relationships\n\nAtlas-specific customer and order evidence is separated from general product capability.\n\n" + table(keys, rows) + "\n", encoding="utf-8")


def build_customer_audit() -> None:
    write_json(DATA_DIR / "customer_chain_audit.json", {"case_id": CASE_DIR.name, "cutoff_date": CUTOFF, "row_count": len(CUSTOMER_AUDIT), "rows": CUSTOMER_AUDIT})
    keys = ["ticker", "company", "customer_or_platform", "claim_type", "certification_status", "order_or_backlog", "revenue_exposure", "source_tier", "evidence_score", "blocks_valuation", "adopted_wording"]
    (DATA_DIR / "customer_chain_audit.md").write_text("# Customer-Chain Audit\n\nQuestions and rumors are not confirmations. `blocks_valuation=true` prevents the claim from supporting Atlas-specific EPS or target-price upside.\n\n" + table(keys, [[r[k] for k in keys] for r in CUSTOMER_AUDIT]) + "\n", encoding="utf-8")


def build_company_reconciliation() -> None:
    rows = [
        {"ticker": row[0], "company": row[1], "chain_role": row[2], "chain_node_occurrences": row[3],
         "atlas_relationship_status": row[4], "broader_business_valuation_eligibility": row[5],
         "research_action": row[6], "dimension_reconciliation": row[7]}
        for row in COMPANY_RECONCILIATION
    ]
    write_json(DATA_DIR / "company_level_reconciliation_20260718.json", {"case_id": CASE_DIR.name, "cutoff_date": CUTOFF, "row_count": len(rows), "rows": rows})
    (DATA_DIR / "company_level_reconciliation_20260718.md").write_text(
        "# Company-Level Relation / Valuation / Action Reconciliation\n\n"
        "Chain-node occurrence, Atlas relationship strength, broader-business valuation eligibility and research action are separate dimensions. iFlytek has two chain-node occurrences but one company-level row.\n\n" +
        table(["Ticker", "Company", "Chain role", "Node occurrences", "Atlas relationship", "Broader valuation", "Action", "Why dimensions diverge"], [list(row.values()) for row in rows]) + "\n",
        encoding="utf-8",
    )


def build_analysis() -> None:
    taxonomy = """# Full-Chain Taxonomy

**Coverage pack:** `workspace/templates/industry-coverage-packs/aidc.md`.

```mermaid
flowchart LR
  A["Ascend 950DT and HiZQ memory"] --> B["Atlas 950 compute and communication cabinets"]
  P["Power, UPS, busway and backup"] --> B
  T["CDU, cold plate, pipework, coolant and facility cooling"] --> B
  N["UnifiedBus, optical/OCS, NIC, switch and copper interconnect"] --> B
  C["PCB, CCL, substrate, connector and cable"] --> B
  S["Storage, SSD and data pipeline"] --> B
  B --> D["Huawei Cloud and operator intelligent-compute centers"]
  D --> M["Model training, inference and agent applications"]
  M --> U["Enterprise and public-sector workloads"]
```

The architecture creates scale-up demand across eight AIDC blocks, but Huawei retains the system, accelerator, memory-subsystem and interconnect control points. Public evidence does not disclose enough subsystem suppliers to convert the product launch directly into an A-share revenue list.
"""
    (ANALYSIS_DIR / "full_chain_taxonomy.md").write_text(taxonomy, encoding="utf-8")

    core_nodes = [r for r in ROWS if r["classification"] == "core_valuation"]
    core_by_ticker: dict[str, dict] = {}
    for row in core_nodes:
        core_by_ticker.setdefault(row["listed_ticker"], row)
    core = list(core_by_ticker.values())
    sat = [r for r in ROWS if r["classification"] == "satellite_watch"]
    anchors = [r for r in ROWS if r["classification"] == "demand_anchor"]
    excluded = [r for r in ROWS if r["classification"] in {"out_of_scope", "unavailable"}]
    core_md = table(["Node", "Ticker", "Role", "Eligibility", "Evidence gap"], [[r["node_name"], r["listed_ticker"], r["chain_role"], r["valuation_status"], r["evidence_gap"]] for r in core])
    sat_md = table(["Node", "Ticker", "Role", "Missing evidence", "Upgrade trigger"], [[r["node_name"], r["listed_ticker"], r["chain_role"], r["evidence_gap"], r["upgrade_trigger"]] for r in sat])
    anchor_md = table(["Anchor", "Role", "Why it is not supplier proof"], [[r["node_name"], r["chain_role"], r["evidence_gap"]] for r in anchors])
    excluded_md = table(["Node", "Type", "Reason"], [[r["node_name"], r["node_type"], r["evidence_gap"]] for r in excluded])
    (ANALYSIS_DIR / "core_vs_satellite_universe.md").write_text(f"""# Core Versus Satellite Universe

Company-level authority: `data/company_level_reconciliation_20260718.md/json`. The full-chain universe is node-level and may contain multiple nodes for one company; this table is de-duplicated by ticker. "Core valuation" means a complete broader-business valuation package, not confirmed Atlas supply. Atlas relationship strength, broader-business valuation eligibility and action are separate fields.

## Provisional Core Valuation Pool

Core status here means the company merits a complete current-price valuation package. It does not mean confirmed Atlas 950 supply. Hardware names receive Atlas optionality only unless a direct order is disclosed.

{core_md}

## Satellite Watch Pool

{sat_md}

## Demand Anchors

{anchor_md}

## Excluded or Unavailable Nodes

{excluded_md}
""", encoding="utf-8")

    gap_rows = [[*g] for g in GAPS]
    (ANALYSIS_DIR / "coverage_gap_matrix.md").write_text("# Coverage Gap Matrix\n\nA valuation-blocking gap cannot be replaced by a thematic proxy.\n\n" + table(["Gap ID", "Block", "Missing node/field", "Why it matters", "Sources checked", "Reason unresolved", "Next path", "Blocks valuation", "Owner"], gap_rows) + "\n", encoding="utf-8")

    (ANALYSIS_DIR / "supply_chain_model.md").write_text("""# Supply-Chain Model

## Gate Status: CONDITIONAL

The full chain is mapped, and every covered ticker has a relationship row. The gate remains conditional because Huawei has not publicly disclosed the Atlas 950 supplier BOM, Atlas-specific orders, component ASPs, utilization, or subsystem margins. Therefore the report may value proven broader AIDC businesses, but it must not assign Atlas-specific EPS credit.

## Evidence Ladder

1. **Explicit 950 platform evidence:** iFlytek is a downstream co-development user. This proves software/platform validation, not supplier revenue.
2. **Huawei/Ascend relationship plus relevant product:** Shenling and Talkweb have official Huawei relationships; Talkweb is an Ascend server partner. Neither discloses an Atlas 950 order.
3. **Relevant AIDC product capability:** HGTECH, Envicool, Kehua Data, Aerospace Electric, Accelink and the PCB/CCL group have relevant products. Their Atlas linkage is optionality only.
4. **Rumor or investor-question mapping:** exclusive-supplier, exact-share and probe-card claims are excluded from valuation unless independently confirmed.

## Profit-Pool Logic

The principal disclosed architecture change is scale-up: more accelerators operate as one logical computer through UnifiedBus and all-optical cabinet links. This can raise the importance of optical/electrical interconnect, high-density power, liquid cooling and high-speed boards. However, the highest-value control points remain inside Huawei: accelerator, memory subsystem, fabric, system architecture and software. A-share companies should receive credit only for disclosed segment delivery, not for a top-down allocation of Huawei's planned cabinet count.

## Gate Decision

- Pass for a full-chain evidence report.
- Conditional for investable valuation of broader AIDC businesses.
- Block Atlas-specific revenue, EPS, market share, or target-price uplift until customer/order/BOM evidence appears.
""", encoding="utf-8")

    cards = """# Company Fundamental Cards

## Shenling Environment (301018.SZ)

- **Chain role:** End-to-end thermal and liquid-cooling system provider.
- **Directness:** Official 2025 disclosure names Huawei among data-service customers and states cooperation with H company strengthened. No Atlas 950 order is identified.
- **Product exposure:** CDU, manifold, cold source, primary/secondary pipework, quick connector and cold plate.
- **Delivery evidence:** 2025 revenue CNY4.209bn (+39.55%), net profit CNY216.8m (+87.59%), data-service revenue +51.42%, and data-service new orders about +72%.
- **Capacity/certification:** New data-center thermal manufacturing base commissioned; numeric capacity and Atlas certification are not disclosed.
- **Moat:** Broad thermal architecture coverage, long operating record and disclosed customer base.
- **Risk:** Customer concentration, mix opacity, project working capital and no Atlas-specific economics.
- **Eligibility:** Eligible for broader Huawei/AIDC liquid-cooling valuation; Atlas optionality receives zero standalone EPS credit.

## HGTECH (000988.SZ)

- **Chain role:** Optical and copper high-speed interconnect.
- **Directness:** No official Atlas 950 customer or order evidence.
- **Product exposure:** 800G/1.6T optical modules, 3.2T optical engines, AEC/ACC, silicon photonics and liquid-cooling-compatible paths.
- **Delivery evidence:** 2025 revenue CNY14.355bn (+22.59%), net profit CNY1.471bn (+20.48%), connection revenue CNY6.097bn (+53.39%).
- **Moat:** Vertical optical-chip/module capability and actual 800G+ delivery.
- **Risk:** Atlas exclusivity/share rumors are unsupported; global AI optical demand may not translate to Huawei domestic scale-up.
- **Eligibility:** Eligible for broader AI interconnect valuation; Atlas exposure is optionality only.

## Envicool (002837.SZ)

- **Chain role:** Full-chain thermal management and liquid cooling.
- **Directness:** Company discloses cooperation across compute chips, equipment, cloud and colocation customers, but not Huawei or Atlas 950.
- **Delivery evidence:** 2025 revenue CNY6.068bn (+32.23%) and net profit CNY521.9m (+15.30%).
- **Moat:** Full thermal chain and long operating record.
- **Risk:** Mix/margin opacity, no named Atlas order, and valuation sensitivity to AI cooling expectations.
- **Eligibility:** Eligible for broader AIDC thermal valuation; Atlas optionality only.

## iFlytek (002230.SZ)

- **Chain role:** Downstream model developer and explicit Ascend 950 platform validator.
- **Directness:** Official filing states joint work with Huawei on Ascend 950 and a planned October 2026 flagship-model launch.
- **Economics:** No compute procurement, cost saving, model revenue, or margin contribution is disclosed.
- **Moat:** Full-stack domestic-compute training experience and application distribution.
- **Risk:** Launch delay, performance/cost gap, high model investment and valuation expectations.
- **Eligibility:** Event-driven downstream valuation, not upstream supplier valuation.

## Talkweb Information (002261.SZ)

- **Chain role:** Ascend server and intelligent-compute ecosystem partner.
- **Directness:** First-batch Ascend system partner; Huawei represented 41.51% of 2025 sales. Atlas 950 qualification is not disclosed.
- **Delivery evidence:** 2025 revenue CNY3.171bn (-22.79%), reported net profit CNY63.7m, recurring net profit -CNY40.2m.
- **Risk:** Customer concentration, weak recurring earnings and subsidiary losses.
- **Eligibility:** Watchlist only until recurring profit and Atlas qualification improve.

## Digital China (000034.SZ)

- **Chain role:** AI infrastructure, distribution, Kuntai compute/network products and services.
- **Directness:** Ascend/Kunpeng ecosystem exposure is official; Atlas 950 order is not disclosed.
- **Delivery evidence:** 2025 AI-related revenue CNY33.03bn (+47.7%), but the metric includes broad distribution and does not establish high-margin Atlas exposure.
- **Risk:** Low business purity and weak conversion from headline AI revenue to profit.
- **Eligibility:** Conditional valuation; monitor self-brand product revenue, gross profit and cash conversion.

## Woer Heat-Shrinkable Material (002130.SZ)

- **Chain role and product:** High-speed copper cable materials and assemblies for AI server/switch connectivity.
- **Customer/platform:** Broader AI connectivity only; Huawei/Atlas qualification and customer allocation are not disclosed.
- **Order/capacity/ASP:** Capacity expansion is disclosed, but Atlas order, utilization, units, ASP and product margin are not.
- **Revenue/earnings bridge:** 2026E broker revenue CNY12.15bn and NP CNY1.88bn support a broader-business model. Atlas-specific revenue, NP and EPS remain zero.
- **Valuation eligibility:** Low-purity value satellite. Upgrade only after named platform qualification, volume, utilization and margin evidence; downgrade if high-speed-cable conversion misses.

## Satellite Cards

Aerospace Electric, Kehua Data, Accelink, Shengyi Technology, Shennan Circuits, WUS PCB, Victory Giant and related optical/PCB/cable names have relevant products but lack Atlas-specific customer/order/ASP/margin evidence. Qiangyi remains a probe-card optionality name because the company declined to confirm the named customer. Sichuan Changhong is excluded from the rumored server-ODM mapping because the company explicitly denied that business.
"""
    (ANALYSIS_DIR / "company_fundamental_cards.md").write_text(cards, encoding="utf-8")

    econ_rows = [
        ["Atlas 950 system", "1024-card physical system; 8192-card design scale", "System price not disclosed", "Huawei system/integration control point", "Pre-commercial physical display; 2026Q4 availability plan", "1024 cards displayed / 8192 design", "not applicable", "No public customer order", "Huawei official", "Shipment, price, reliability and cost unavailable", "Demand context only"],
        ["Accelerator and memory", "1P FP8 / 2P FP4 per 950-series planning target; 144GB HiZQ for DT", "Chip price not disclosed", "Huawei accelerator and memory subsystem", "Supply/demand not disclosed", "Yield and capacity not disclosed", "not disclosed", "No public customer allocation", "Huawei roadmap", "Foundry, HBM source, yield and cost unavailable", "No A-share credit"],
        ["Optical/networking", "All-optical cabinet interconnect and TB-class NPU links", "Port/module/OCS ASP not disclosed", "Potential fabric, optical engine and connector pool", "Demand direction positive if scale-up ships", "Port count and suppliers not disclosed", "No Atlas supplier qualification", "No Atlas order", "Huawei architecture plus company filings", "Cannot convert cabinet count into module volume", "Broader AI optical credit only"],
        ["Liquid cooling", "Full liquid-cooled data-center system; component count not disclosed", "CDU/cold plate/loop ASP not disclosed", "Thermal equipment and service pool", "High-density compute supports structural demand", "Per-rack power and loop design unavailable", "Shenling general Huawei relation only", "No Atlas order", "Huawei and company filings", "No component allocation or margin", "Broader AIDC thermal credit only"],
        ["Power", "High-density power requirement implied", "MW/cabinet value not disclosed", "UPS, busway, power shelf, transformer and backup", "Demand direction positive if commercial deployment scales", "Power density and suppliers unavailable", "not disclosed", "No Atlas order", "Huawei and equipment filings", "No MW value, delivery or working-capital data", "Watchlist only"],
        ["PCB/CCL/connectors", "High-speed board and connector requirement implied", "Layer/spec/ASP uplift not disclosed", "Material, fabrication and connector pool", "General AI demand strong; Atlas allocation unknown", "Capacity exists but Atlas qualification unavailable", "not disclosed", "No Atlas order", "Company filings", "No layer stack, yield or margin link", "Generic AI exposure only"],
        ["Downstream model", "iFlytek co-development on 950 platform", "Compute cost not disclosed", "Model/application economics", "Platform validation scheduled for October 2026", "Software R&D capacity", "Joint work disclosed", "No compute procurement amount", "iFlytek annual report", "No training-efficiency or revenue bridge", "Event-driven optionality"],
    ]
    (ANALYSIS_DIR / "value_chain_economics.md").write_text("# Value-Chain Economics\n\nThe evidence does not support a top-down Atlas 950 BOM revenue model. Company valuation credit is limited to already disclosed broader segment economics.\n\n" + table(["Chain block", "Value amount/proxy", "ASP/price", "Margin pool", "Supply-demand", "Capacity", "Certification", "Order visibility", "Source", "Gap", "Valuation credit"], econ_rows) + "\n", encoding="utf-8")

    (ANALYSIS_DIR / "chain_earnings_bridge.md").write_text("""# Chain Earnings Bridge

## Theme-Level Bridge

`Atlas 950 commercial shipment -> disclosed customer order -> company product allocation -> recognized revenue -> product gross margin -> incremental operating profit -> net profit/EPS`.

The public evidence currently stops before the company product-allocation step for every upstream A-share candidate. Consequently, the report assigns no standalone Atlas 950 EPS to upstream names. It values broader AIDC delivery already visible in filings and treats Atlas as a catalyst/optionality layer.

## Ticker-Level Bridge and Next-Quarter Thresholds

| Ticker | Realized driver | Atlas optionality | Required next validation | Earnings consequence |
|---|---|---|---|---|
| 301018 | Data-service revenue +51.42%; new orders +72% in 2025 | Huawei/H-company relationship and complete liquid-cooling stack | 2026H1 data-service revenue, liquid-cooling mix, gross margin, cash conversion, named qualification if available | Upgrade only if order growth converts without margin/cash deterioration |
| 000988 | Connection revenue +53.39% in 2025; 800G/1.6T delivery | Domestic scale-up optical opportunity | 2026H1 800G+ shipments, connection gross margin, domestic customer mix, 3.2T qualification | Earnings credit follows delivered optical revenue, not rumored Atlas share |
| 002837 | Revenue +32.23% and full-chain liquid-cooling capability | Potential high-density thermal demand | Compute-liquid-cooling revenue/order disclosure and segment margin | Upgrade if mix and profit conversion are explicit |
| 002230 | Explicit joint Ascend 950 model work | October 2026 flagship-model launch | Launch timing, training efficiency, inference cost and commercialization | Event credit only after performance/cost and revenue evidence |
| 002261 | Direct Ascend partnership and Huawei customer concentration | Possible new-system ecosystem participation | Atlas qualification/order, intelligent-compute segment margin and recurring profit | Watchlist until recurring earnings turn positive |
| 000034 | AI-related revenue +47.7% in 2025 | Kuntai/Ascend infrastructure participation | Self-brand revenue/gross profit, project orders and cash conversion | Headline distribution revenue alone earns no high-growth multiple |
| 600183 | High-speed/low-loss CCL and strong 2026H1 profit preview | Atlas board material optionality | Material grade, qualification, mix, capacity utilization and copper/glass input spread | Broad CCL earnings only; zero Atlas mix credit |
| 002916 | AI PCB/package-substrate product mix and 2026H1 profit preview | Atlas high-layer board optionality | Layer stack, platform qualification, yield, new-line utilization and margin | Broad AI PCB earnings only; zero Atlas allocation |
| 002463 | AI server/switch PCB delivery and 2026H1 profit preview | Atlas PCB optionality | Named domestic platform, high-layer shipment mix, utilization and customer concentration | Credit delivered PCB profit; zero Atlas customer share |
| 300476 | Global AI accelerator/server PCB growth | Atlas PCB optionality | Huawei qualification, overseas capacity yield, customer mix and cash conversion | Positive target derives from global AI earnings, not Atlas purity |
| 002335 | Intelligent-compute power/POD and liquid-cooling equipment | Ascend-adjacent project participation | Project acceptance, deducted profit, receivables, AIDC mix and named Atlas qualification | Project earnings credit only after acceptance/cash evidence |
| 002130 | High-speed copper cable revenue/profit forecast | Atlas high-speed copper optionality | Platform qualification, order volume, capacity utilization, copper spread and segment margin | Low-purity value credit; Atlas revenue/NP/EPS remain zero |
| 002025 | High-speed/backplane and liquid-cooling connector capability | Unconfirmed Ascend 950 mapping | Named qualification, order, revenue purity, capacity and margin | Broader connector/defense-cycle earnings only; no platform credit |

For all twelve modeled tickers, public Atlas units, component ASP, recognized-revenue ratio, Atlas gross margin, incremental opex, tax, NP and EPS are unavailable and therefore recorded as zero credit in the growth-driver model. The broader-business NP/EPS bridge is separately quantified in `analysis/segment_forecast_bridge.md`; the table above supplies the operational driver, evidence threshold and invalidation needed to decide whether that broader forecast deserves its multiple.

## Upgrade and Downgrade Discipline

- **Upgrade:** official customer qualification, order/backlog, ASP/value amount, capacity utilization, product margin and recognized revenue.
- **Downgrade:** product launch without customer orders, high customer concentration, margin dilution, working-capital deterioration, delayed 950DT/Atlas availability, or independent performance below expectations.
""", encoding="utf-8")

    (ANALYSIS_DIR / "house_view.md").write_text("""# House View

Atlas 950 is a real architecture milestone, but the investable event is not a confirmed supplier windfall. Huawei has moved from a 2025 roadmap to a 1024-card physical system while retaining an 8192-card design-scale ambition. The architecture increases the strategic value of scale-up interconnect, power density, liquid cooling and high-speed boards, yet public evidence leaves most high-value control points and suppliers inside a black box.

Our differentiated view is to split the universe by evidence rather than by thematic proximity. Shenling, HGTECH and Envicool can be valued on broader AIDC segment delivery; iFlytek is a direct downstream 950 validation event; Talkweb and Digital China are ecosystem exposures whose profit quality and product purity limit valuation credit. The PCB, connector, power and optical satellites remain watchlist names until a customer/platform/order/ASP bridge appears.

The report should become more bullish only when 2026Q4 availability converts into named deployments and company-level order/margin evidence. It should become more cautious if the physical system remains a showcase, if 950DT shipment slips, or if market prices capitalize unsupported exclusive-supplier claims.
""", encoding="utf-8")

    (ANALYSIS_DIR / "variant_perception.md").write_text("""# Variant Perception

## Market Consensus

The event is commonly framed as a domestic scale-up inflection that should lift every liquid-cooling, optical, PCB, connector and power name associated with Huawei or AI infrastructure.

## AStock Differentiated View

The architecture inflection is real, but the public evidence supports only a small set of relationships and no upstream Atlas-specific revenue bridge. The investable distinction is between proven broader AIDC delivery, explicit downstream platform validation, ecosystem participation, and unsupported supplier rumor.

## Assumption Gap

The bullish market narrative assumes that an 8192-card design-scale system will ship near the 2026Q4 plan, that external A-share suppliers receive material content, and that the content converts at attractive margins. None of those three steps is publicly quantified.

## Strongest Opposing Argument

Supplier confidentiality often prevents named-customer disclosure; waiting for perfect evidence may miss the earnings inflection. Existing Huawei relationships, product portfolios and capacity expansion may be sufficient leading indicators.

## What Would Prove AStock Wrong

- A tender, filing or customer source confirms meaningful Atlas 950 content for a current satellite.
- 2026H2 company results show order and margin acceleration consistent with Atlas deployment before explicit naming.
- Huawei delivers volume systems on schedule and independent workloads validate the claimed scale-up advantage.

## Monitoring Triggers

- 2026Q4 950DT and Atlas 950 commercial availability.
- Named operator/cloud deployments and system count.
- Company disclosures of customer qualification, product mix, ASP, orders and margins.
- iFlytek's October 2026 model launch, training efficiency and cost.
- Any official denial or clarification of market-circulated supplier claims.
""", encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    build_full_chain()
    build_relationships()
    build_customer_audit()
    build_company_reconciliation()
    build_analysis()
    print(json.dumps({"rows": len(ROWS), "relationships": len(RELATIONSHIPS), "customer_audit": len(CUSTOMER_AUDIT), "gaps": len(GAPS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
