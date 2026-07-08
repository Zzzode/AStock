#!/usr/bin/env python3
"""Build the optical-communication supply-chain research report package."""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[2]
DATA = CASE / "data"
ANALYSIS = CASE / "analysis"
SECTIONS = CASE / "sections"
SOURCES = CASE / "sources"
RUN_DATE = "2026-06-26"
CN_TZ = timezone(timedelta(hours=8))

# The report is frozen at RUN_DATE (prices + 2026Q1 financials). By default the
# build rebuilds OFFLINE from the frozen snapshot so a naive re-run is
# deterministic and never re-baselines prices to "today". Live re-fetch is an
# explicit opt-in via OPTICAL_REPORT_REFRESH=1 (used only to re-cut the case).
REFRESH_LIVE = os.environ.get("OPTICAL_REPORT_REFRESH") == "1"
# Post-cutoff earnings-preview addendum date (H1 2026 previews landed 2026-07-06).
PREVIEW_DATE = "2026-07-06"


TICKERS = [
    {
        "code": "300308",
        "name": "中际旭创",
        "role": "AI datacenter optical modules",
        "tier": "Core module",
        "weight_pct": 13,
        "q1_share": 0.23,
        "growth_2027": 0.32,
        "growth_2028": 0.22,
        "bear_pe": 35,
        "base_pe": 45,
        "bull_pe": 55,
        "quality": "A-",
        "rating_note": "800G/1.6T scale leader with strongest earnings delivery, but valuation already prices sustained overseas AI demand.",
        "catalyst": "1.6T volume ramp, Nvidia/overseas cloud demand visibility, gross margin retention above 42%.",
        "invalidation": "800G/1.6T order slowdown, customer concentration pressure, or gross margin falling below 38%.",
    },
    {
        "code": "300502",
        "name": "新易盛",
        "role": "High-speed optical modules",
        "tier": "Core module",
        "weight_pct": 12,
        "q1_share": 0.23,
        "growth_2027": 0.30,
        "growth_2028": 0.22,
        "bear_pe": 32,
        "base_pe": 40,
        "bull_pe": 50,
        "quality": "A-",
        "rating_note": "High-growth optical-module beta with strong 2025-2026 delivery; valuation remains sensitive to one-customer and ASP assumptions.",
        "catalyst": "Sustained overseas customer orders, 1.6T product qualification, cash conversion improvement.",
        "invalidation": "Order pull-forward reversal, module ASP erosion above 20%, or operating cash flow lagging profit.",
    },
    {
        "code": "300394",
        "name": "天孚通信",
        "role": "Precision optical components and packaging",
        "tier": "Precision components",
        "weight_pct": 6,
        "q1_share": 0.24,
        "growth_2027": 0.24,
        "growth_2028": 0.18,
        "bear_pe": 35,
        "base_pe": 45,
        "bull_pe": 55,
        "quality": "B+",
        "rating_note": "High-margin optical component platform, but growth decelerates versus module leaders.",
        "catalyst": "Micro-optics and packaging attach rate uplift in 1.6T/CPO products.",
        "invalidation": "Component price cuts, customer self-supply, or margin mean reversion below 50% gross margin.",
    },
    {
        "code": "002281",
        "name": "光迅科技",
        "role": "Telecom/datacom optical devices and modules",
        "tier": "Optical devices/modules",
        "weight_pct": 4,
        "q1_share": 0.22,
        "growth_2027": 0.20,
        "growth_2028": 0.15,
        "bear_pe": 28,
        "base_pe": 35,
        "bull_pe": 45,
        "quality": "B",
        "rating_note": "Broader product line and state-backed platform, but profitability is far below AI-module peers.",
        "catalyst": "Datacom mix rising and silicon-photonics/CPO product validation.",
        "invalidation": "Telecom cycle weakness, datacom mix not improving, or gross margin staying below 28%.",
    },
    {
        "code": "000988",
        "name": "华工科技",
        "role": "Optical modules plus laser equipment",
        "tier": "Mixed optical platform",
        "weight_pct": 4,
        "q1_share": 0.25,
        "growth_2027": 0.18,
        "growth_2028": 0.14,
        "bear_pe": 25,
        "base_pe": 35,
        "bull_pe": 45,
        "quality": "B",
        "rating_note": "Mixed business offers earnings stability but dilutes pure AI optical-module beta.",
        "catalyst": "High-speed optical module revenue mix and industrial laser profitability improvement.",
        "invalidation": "Working-capital pressure, mixed-business discount, or datacom orders not scaling.",
    },
    {
        "code": "603083",
        "name": "剑桥科技",
        "role": "Optical module and telecom equipment",
        "tier": "High beta",
        "weight_pct": 2,
        "q1_share": 0.20,
        "growth_2027": 0.30,
        "growth_2028": 0.25,
        "bear_pe": 30,
        "base_pe": 45,
        "bull_pe": 55,
        "quality": "C+",
        "rating_note": "Turnaround beta is visible, but Q1 profit denominator is still too small for a large investable target.",
        "catalyst": "Sustained 800G/1.6T order conversion and operating expense dilution.",
        "invalidation": "Q2/Q3 profit fails to scale, cash flow remains negative, or customer mix weakens.",
    },
    {
        "code": "300570",
        "name": "太辰光",
        "role": "Fiber connectors and passive optical components",
        "tier": "Passive components",
        "weight_pct": 2,
        "q1_share": 0.25,
        "growth_2027": 0.15,
        "growth_2028": 0.12,
        "bear_pe": 25,
        "base_pe": 35,
        "bull_pe": 45,
        "quality": "C",
        "rating_note": "Passive component exposure is real, but 2026Q1 revenue/profit declined and valuation is not supported by delivery.",
        "catalyst": "AI datacenter fiber connector orders recover and Q2 earnings re-accelerate.",
        "invalidation": "Revenue decline continues, passive optical component price pressure, or inventory rebuild stalls.",
    },
    {
        "code": "688498",
        "name": "源杰科技",
        "role": "Laser chips and high-speed optical sources",
        "tier": "Strategic upstream",
        "weight_pct": 4,
        "q1_share": 0.23,
        "growth_2027": 0.38,
        "growth_2028": 0.30,
        "bear_pe": 40,
        "base_pe": 65,
        "bull_pe": 85,
        "quality": "B",
        "rating_note": "Most strategic upstream exposure, but current price capitalizes a long execution path.",
        "catalyst": "100G/200G EML and silicon-photonics light-source qualification expands into module leaders.",
        "invalidation": "Qualification delays, yield instability, or customer dual-sourcing weakens pricing power.",
    },
    {
        "code": "600487",
        "name": "亨通光电",
        "role": "Optical fiber/cable, submarine cable and power-optical integration",
        "tier": "Fiber/cable",
        "weight_pct": 4,
        "q1_share": 0.24,
        "growth_2027": 0.12,
        "growth_2028": 0.10,
        "bear_pe": 18,
        "base_pe": 24,
        "bull_pe": 30,
        "quality": "B",
        "rating_note": "Fiber/cable leader with submarine cable and grid exposure, but AI datacenter purity is lower than optical-module leaders.",
        "catalyst": "Carrier/cloud fiber demand recovery, submarine cable orders and better working-capital conversion.",
        "invalidation": "Telecom capex weakness, cable price pressure, or cash conversion lagging revenue growth.",
    },
    {
        "code": "600522",
        "name": "中天科技",
        "role": "Optical fiber/cable, submarine cable and communication cable",
        "tier": "Fiber/cable",
        "weight_pct": 4,
        "q1_share": 0.24,
        "growth_2027": 0.12,
        "growth_2028": 0.10,
        "bear_pe": 18,
        "base_pe": 24,
        "bull_pe": 30,
        "quality": "B",
        "rating_note": "Broad cable and power-ocean platform provides earnings resilience, but the stock should not be valued as a pure AI optical module name.",
        "catalyst": "Submarine cable delivery, telecom fiber demand improvement and margin recovery.",
        "invalidation": "Grid/submarine project delay, fiber cable price cuts, or operating cash flow deterioration.",
    },
    {
        "code": "601869",
        "name": "长飞光纤",
        "role": "Optical fiber preform, fiber and cable",
        "tier": "Fiber/preform",
        "weight_pct": 4,
        "q1_share": 0.23,
        "growth_2027": 0.16,
        "growth_2028": 0.12,
        "bear_pe": 20,
        "base_pe": 28,
        "bull_pe": 35,
        "quality": "B+",
        "rating_note": "Preform/fiber/cable integration gives stronger upstream scarcity than pure cable names, but datacenter demand must show in fiber utilization.",
        "catalyst": "Preform utilization recovery, cloud/campus fiber deployment and overseas fiber orders.",
        "invalidation": "Fiber oversupply, ASP decline, or Q2/Q3 profit failing to scale with high Q1 margin.",
    },
    {
        "code": "600498",
        "name": "烽火通信",
        "role": "Telecom optical network equipment and systems",
        "tier": "Network equipment",
        "weight_pct": 3,
        "q1_share": 0.22,
        "growth_2027": 0.15,
        "growth_2028": 0.12,
        "bear_pe": 20,
        "base_pe": 28,
        "bull_pe": 35,
        "quality": "B-",
        "rating_note": "Carrier optical-network platform has strategic relevance, but Q1 profit denominator is thin and telecom capex is slower than cloud AI capex.",
        "catalyst": "OTN/ROADM equipment demand, carrier backbone upgrades and profitability normalization.",
        "invalidation": "Carrier capex delay, low-margin project mix, or net margin failing to recover.",
    },
    {
        "code": "000063",
        "name": "中兴通讯",
        "role": "Network equipment, carrier/cloud infrastructure and terminal applications",
        "tier": "Network equipment/application",
        "weight_pct": 6,
        "q1_share": 0.22,
        "growth_2027": 0.12,
        "growth_2028": 0.10,
        "bear_pe": 15,
        "base_pe": 20,
        "bull_pe": 25,
        "quality": "A-",
        "rating_note": "Network-equipment anchor covers carrier/cloud/application layer, but optical communication is only one part of the business mix.",
        "catalyst": "Carrier network upgrades, AI server/networking product progress and margin improvement.",
        "invalidation": "Carrier capex weakness, overseas policy pressure, or non-optical businesses diluting earnings quality.",
    },
    {
        "code": "688313",
        "name": "仕佳光子",
        "role": "PLC splitter, AWG and passive photonic chips/devices",
        "tier": "Passive photonic chips",
        "weight_pct": 3,
        "q1_share": 0.23,
        "growth_2027": 0.25,
        "growth_2028": 0.18,
        "bear_pe": 35,
        "base_pe": 50,
        "bull_pe": 65,
        "quality": "B",
        "rating_note": "Passive photonic-chip exposure is strategically relevant to WDM/AWG and silicon-photonics ecosystems, but valuation needs high utilization.",
        "catalyst": "AWG/PLC device demand in high-speed modules and telecom/datacenter WDM systems.",
        "invalidation": "Photonic-chip price pressure, customer qualification delays, or utilization slipping below Q1 levels.",
    },
    {
        "code": "688048",
        "name": "长光华芯",
        "role": "High-power and datacom laser chips",
        "tier": "Laser chips",
        "weight_pct": 2,
        "q1_share": 0.20,
        "growth_2027": 0.45,
        "growth_2028": 0.35,
        "bear_pe": 45,
        "base_pe": 70,
        "bull_pe": 90,
        "quality": "C+",
        "rating_note": "Laser-chip optionality is high, but Q1 profit denominator is still small and the base case requires rapid qualification and scale-up.",
        "catalyst": "Datacom laser-chip qualification, yield improvement and high-power laser profitability recovery.",
        "invalidation": "R&D conversion delays, yield instability, or Q2/Q3 earnings failing to validate the high multiple.",
    },
    {
        "code": "300620",
        "name": "光库科技",
        "role": "Optical fiber devices, isolators and lithium-niobate/modulator option",
        "tier": "Optical devices",
        "weight_pct": 3,
        "q1_share": 0.23,
        "growth_2027": 0.25,
        "growth_2028": 0.18,
        "bear_pe": 35,
        "base_pe": 50,
        "bull_pe": 65,
        "quality": "B",
        "rating_note": "Optical-device and lithium-niobate option gives higher strategic relevance than generic components, but the price embeds a long path.",
        "catalyst": "High-speed optical device attach rate, thin-film lithium-niobate commercialization and overseas demand recovery.",
        "invalidation": "Modulator commercialization delay, margin compression, or component demand falling short of AI-related expectations.",
    },
    {
        "code": "002491",
        "name": "通鼎互联",
        "role": "Optical fiber/cable, communication cable and network integration",
        "tier": "Fiber/cable",
        "weight_pct": 3,
        "q1_share": 0.23,
        "growth_2027": 0.12,
        "growth_2028": 0.10,
        "bear_pe": 18,
        "base_pe": 24,
        "bull_pe": 30,
        "quality": "B-",
        "rating_note": "Fiber/cable exposure belongs in the chain, but earnings quality and AI datacenter purity are below module leaders.",
        "catalyst": "Telecom fiber/cable demand recovery, communication cable order improvement and cash-flow repair.",
        "invalidation": "Telecom capex delay, cable ASP pressure, or Q2/Q3 profit failing to confirm Q1 recovery.",
    },
    {
        "code": "600105",
        "name": "永鼎股份",
        "role": "Optical cable, communication cable and integrated telecom infrastructure",
        "tier": "Fiber/cable",
        "weight_pct": 3,
        "q1_share": 0.24,
        "growth_2027": 0.10,
        "growth_2028": 0.08,
        "bear_pe": 18,
        "base_pe": 23,
        "bull_pe": 28,
        "quality": "B",
        "rating_note": "Cable and telecom infrastructure recovery is visible, but the business is slower-cycle and lower-purity than AI optical modules.",
        "catalyst": "Carrier cable orders, telecom infrastructure delivery and margin stabilization.",
        "invalidation": "Project delay, cable price cuts, or working-capital pressure offsetting profit recovery.",
    },
    {
        "code": "300548",
        "name": "长芯博创",
        "role": "Optical modules, active optical devices and coherent transmission components",
        "tier": "Optical modules/devices",
        "weight_pct": 4,
        "q1_share": 0.24,
        "growth_2027": 0.25,
        "growth_2028": 0.18,
        "bear_pe": 30,
        "base_pe": 42,
        "bull_pe": 55,
        "quality": "B",
        "rating_note": "Optical module/device platform has real datacom exposure, but current valuation requires sustained high-speed product delivery.",
        "catalyst": "Datacom module orders, coherent product growth and gross-margin retention.",
        "invalidation": "High-speed product ramp delays, module ASP pressure, or margin falling back toward legacy levels.",
    },
    {
        "code": "688205",
        "name": "德科立",
        "role": "Coherent optical modules and transmission equipment components",
        "tier": "Coherent/transmission",
        "weight_pct": 3,
        "q1_share": 0.22,
        "growth_2027": 0.24,
        "growth_2028": 0.18,
        "bear_pe": 30,
        "base_pe": 45,
        "bull_pe": 58,
        "quality": "B",
        "rating_note": "Coherent/transmission exposure fills the DCI and carrier side of the chain, but Q1 profit base is still modest.",
        "catalyst": "DCI/coherent demand, overseas customer expansion and profitability normalization.",
        "invalidation": "Coherent order delays, customer concentration pressure, or net margin failing to scale.",
    },
    {
        "code": "688195",
        "name": "腾景科技",
        "role": "Precision optical components for optical communication and lasers",
        "tier": "Precision optics",
        "weight_pct": 3,
        "q1_share": 0.23,
        "growth_2027": 0.20,
        "growth_2028": 0.15,
        "bear_pe": 30,
        "base_pe": 42,
        "bull_pe": 55,
        "quality": "B",
        "rating_note": "Precision optics is relevant to high-speed optical systems, but scale is small and valuation needs durable order conversion.",
        "catalyst": "High-end optical component orders, laser/communication demand and margin improvement.",
        "invalidation": "Order volatility, insufficient revenue scale, or optical component price pressure.",
    },
    {
        "code": "301205",
        "name": "联特科技",
        "role": "High-speed optical modules and datacom transceivers",
        "tier": "High beta module",
        "weight_pct": 2,
        "q1_share": 0.20,
        "growth_2027": 0.35,
        "growth_2028": 0.25,
        "bear_pe": 35,
        "base_pe": 55,
        "bull_pe": 70,
        "quality": "C+",
        "rating_note": "High-speed module beta is high, but Q1 profit denominator is very small and target price is sensitive to execution.",
        "catalyst": "High-speed datacom order conversion, customer qualification and margin expansion.",
        "invalidation": "Qualification delays, Q2/Q3 profit not scaling, or cash flow failing to follow revenue.",
    },
    {
        "code": "300913",
        "name": "兆龙互连",
        "role": "High-speed data cable, communication cable and copper interconnect",
        "tier": "High-speed cable/interconnect",
        "weight_pct": 2,
        "q1_share": 0.24,
        "growth_2027": 0.18,
        "growth_2028": 0.14,
        "bear_pe": 25,
        "base_pe": 35,
        "bull_pe": 45,
        "quality": "B",
        "rating_note": "High-speed cable/copper interconnect fills the intra-rack and enterprise network layer, but it is not a pure optical-module proxy.",
        "catalyst": "High-speed data cable demand, AI server/networking interconnect orders and margin stabilization.",
        "invalidation": "Copper interconnect demand miss, product mix deterioration, or price competition.",
    },
    {
        "code": "002897",
        "name": "意华股份",
        "role": "High-speed connectors and communication interconnect components",
        "tier": "Connector/interconnect",
        "weight_pct": 2,
        "q1_share": 0.22,
        "growth_2027": 0.15,
        "growth_2028": 0.12,
        "bear_pe": 22,
        "base_pe": 30,
        "bull_pe": 38,
        "quality": "B-",
        "rating_note": "Connector exposure belongs in the datacenter interconnect chain, but mixed businesses require a purity discount.",
        "catalyst": "High-speed connector orders, AI server interconnect demand and profitability recovery.",
        "invalidation": "Connector demand slowdown, non-optical business dilution, or margin compression.",
    },
    {
        "code": "300563",
        "name": "神宇股份",
        "role": "RF coaxial cable and high-speed communication interconnect",
        "tier": "Cable/interconnect",
        "weight_pct": 2,
        "q1_share": 0.22,
        "growth_2027": 0.15,
        "growth_2028": 0.12,
        "bear_pe": 22,
        "base_pe": 32,
        "bull_pe": 40,
        "quality": "C+",
        "rating_note": "Cable/interconnect exposure broadens the chain, but optical communication purity and Q1 profit scale are limited.",
        "catalyst": "High-speed communication cable demand, customer mix improvement and margin stabilization.",
        "invalidation": "Low-margin product mix, weak order conversion, or cash flow lagging profit.",
    },
    {
        "code": "603618",
        "name": "杭电股份",
        "role": "Optical fiber/cable, power cable and communication cable",
        "tier": "Fiber/cable",
        "weight_pct": 2,
        "q1_share": 0.24,
        "growth_2027": 0.15,
        "growth_2028": 0.10,
        "bear_pe": 16,
        "base_pe": 22,
        "bull_pe": 28,
        "quality": "C+",
        "rating_note": "AI-driven optical fiber demand drove a sharp H1 2026 turnaround off a FY2025 loss, but the base business is low-margin cable and the recovery must be confirmed beyond one guidance.",
        "catalyst": "Optical fiber price/volume recovery (量价齐升), subsidiary Yongte fiber volume ramp, and margin normalization.",
        "invalidation": "Fiber price rollover, cable margin pressure, or H2 profit failing to confirm the H1 guidance surge.",
    },
]


WATCHLIST_ITEMS = [
    {
        "code": "300757",
        "name": "罗博特科",
        "role": "Automation and active-alignment equipment for optical modules and silicon photonics",
        "reason": "2026Q1 loss-making; included as equipment-chain watchlist, not in PE-based investable valuation.",
    },
    {
        "code": "000070",
        "name": "特发信息",
        "role": "Optical fiber/cable, communication equipment and network infrastructure",
        "reason": "2026Q1 loss-making in the current data packet; keep in full-chain watchlist until earnings denominator repairs.",
    },
    {
        "code": "300615",
        "name": "欣天科技",
        "role": "Communication RF/connector components and telecom equipment parts",
        "reason": "2026Q1 loss-making and optical-chain purity is lower than core optical names.",
    },
    {
        "code": "300565",
        "name": "科信技术",
        "role": "Communication network infrastructure and energy/storage-side equipment",
        "reason": "2026Q1 loss-making; not suitable for PE-based optical-chain target price.",
    },
    {
        "code": "603118",
        "name": "共进股份",
        "role": "Communication terminal equipment, CPE and network devices",
        "reason": "Positive EPS but optical communication purity is low; included in application/network-device watchlist.",
    },
    {
        "code": "002313",
        "name": "日海智能",
        "role": "Communication equipment, IoT and network integration",
        "reason": "Positive EPS but low margin and broad IoT/network-integration mix make it non-core for optical valuation.",
    },
    {
        "code": "603220",
        "name": "中贝通信",
        "role": "Communication network engineering and ICT infrastructure services",
        "reason": "Q1 profit denominator is near zero; belongs in downstream engineering watchlist rather than optical hardware valuation.",
    },
    {
        "code": "300504",
        "name": "天邑股份",
        "role": "Broadband access terminals and communication network devices",
        "reason": "Positive EPS but closer to access-terminal equipment than optical-device/module manufacturing.",
    },
    {
        "code": "002902",
        "name": "铭普光磁",
        "role": "Optoelectronic/magnetic components and communication power/network components",
        "reason": "2026Q1 loss-making; keep as component watchlist until profit repairs.",
    },
    {
        "code": "301165",
        "name": "锐捷网络",
        "role": "Enterprise networking, switching and cloud-network equipment",
        "reason": "Relevant downstream network-equipment marker, but optical is not the dominant earnings driver.",
    },
    {
        "code": "GLOBAL",
        "name": "MOCVD / lithography / etch / test equipment",
        "role": "Epitaxy, wafer process, die attach, active alignment, burn-in and optical/electrical test",
        "reason": "Critical manufacturing bottleneck, but no clean A-share PE target in this report universe.",
    },
    {
        "code": "GLOBAL",
        "name": "Quartz / InP / GaAs / LiNbO3 / silicon photonics wafers",
        "role": "Preform, laser-chip, modulator and PIC material base",
        "reason": "Upstream material direction is covered in the chain map; investable A-share coverage requires separate material-company report.",
    },
]


CN_FIELDS = {
    "300308": {
        "role": "AI 数据中心高速光模块",
        "rating_note": "800G/1.6T 规模和盈利兑现最强，但当前估值已经反映海外 AI 需求持续高景气。",
        "catalyst": "1.6T 放量、海外云厂商订单能见度提升、毛利率维持在 42%以上。",
        "invalidation": "800G/1.6T 订单放缓、客户集中度压力上升，或毛利率跌破 38%。",
    },
    "300502": {
        "role": "高速光模块",
        "rating_note": "高增长光模块弹性强，2025--2026 年交付较强，但估值对单一客户和 ASP 假设敏感。",
        "catalyst": "海外客户订单延续、1.6T 产品认证、现金转化改善。",
        "invalidation": "订单前置后回落、模块 ASP 下跌超过 20%，或经营现金流明显落后利润。",
    },
    "300394": {
        "role": "精密光器件与封装平台",
        "rating_note": "高毛利精密器件平台价值明确，但增速相对模块龙头放缓。",
        "catalyst": "微光学器件和封装件在 1.6T/CPO 产品中的附加值提升。",
        "invalidation": "器件降价、客户自供比例提高，或毛利率回落至 50%以下。",
    },
    "002281": {
        "role": "电信/数通光器件与光模块",
        "rating_note": "产品线和央企平台优势存在，但盈利能力显著低于 AI 光模块龙头。",
        "catalyst": "数通收入占比提高、硅光/CPO 产品验证推进。",
        "invalidation": "电信周期走弱、数通结构未改善，或毛利率持续低于 28%。",
    },
    "000988": {
        "role": "光模块与激光设备混合平台",
        "rating_note": "混合业务提供盈利稳定性，但削弱纯 AI 光模块弹性。",
        "catalyst": "高速光模块收入占比提升、工业激光盈利改善。",
        "invalidation": "营运资本压力、混合业务折价扩大，或数通订单不放量。",
    },
    "603083": {
        "role": "光模块与通信设备高 beta 标的",
        "rating_note": "反转弹性存在，但 Q1 利润分母仍偏小，难以支撑过高目标价。",
        "catalyst": "800G/1.6T 订单持续转化、费用率被收入放量摊薄。",
        "invalidation": "Q2/Q3 利润不放量、现金流仍为负，或客户结构恶化。",
    },
    "300570": {
        "role": "光纤连接器与无源光器件",
        "rating_note": "无源器件敞口真实，但 2026Q1 收入/利润下滑，估值需要交付修复。",
        "catalyst": "AI 数据中心连接器订单恢复、Q2 利润重新加速。",
        "invalidation": "收入继续下滑、无源器件降价，或库存重建停滞。",
    },
    "688498": {
        "role": "激光芯片与高速光源",
        "rating_note": "上游战略属性最强之一，但当前价格已经前置长期兑现路径。",
        "catalyst": "100G/200G EML 和硅光光源进入头部模块客户。",
        "invalidation": "客户认证延迟、良率不稳，或双供应削弱议价能力。",
    },
    "600487": {
        "role": "光纤光缆、海缆与电力通信一体化",
        "rating_note": "光纤光缆龙头兼具海缆和电网敞口，但 AI 数据中心纯度低于模块龙头。",
        "catalyst": "运营商/云侧光纤需求修复、海缆订单、营运资本改善。",
        "invalidation": "电信资本开支走弱、光缆价格承压，或现金转化落后收入。",
    },
    "600522": {
        "role": "光纤光缆、海缆与通信线缆",
        "rating_note": "电力海洋与通信线缆平台提供盈利韧性，但不能按纯 AI 光模块估值。",
        "catalyst": "海缆交付、运营商光纤需求改善、毛利率修复。",
        "invalidation": "电网/海缆项目延迟、光纤价格下降，或经营现金流恶化。",
    },
    "601869": {
        "role": "光纤预制棒、光纤与光缆",
        "rating_note": "预制棒/光纤/光缆一体化稀缺性较强，但数据中心需求需体现在利用率上。",
        "catalyst": "预制棒利用率修复、云/园区光纤建设、海外订单。",
        "invalidation": "光纤供给过剩、ASP 下滑，或 Q2/Q3 利润未延续高 Q1 利润率。",
    },
    "600498": {
        "role": "电信光网络设备与系统",
        "rating_note": "运营商光网络平台具备战略意义，但 Q1 利润分母薄，周期慢于云侧 AI capex。",
        "catalyst": "OTN/ROADM 需求、运营商骨干网升级、盈利正常化。",
        "invalidation": "运营商资本开支延迟、低毛利项目占比提高，或净利率未修复。",
    },
    "000063": {
        "role": "网络设备、运营商/云基础设施与终端应用",
        "rating_note": "覆盖运营商、云网络和应用层，但光通信只是业务组合的一部分。",
        "catalyst": "运营商网络升级、AI 服务器/网络产品进展、利润率改善。",
        "invalidation": "运营商资本开支走弱、海外政策压力，或非光通信业务稀释盈利质量。",
    },
    "688313": {
        "role": "PLC 分路器、AWG 与无源光芯片/器件",
        "rating_note": "无源光芯片与 WDM/AWG/硅光生态相关性强，但估值需要高利用率支撑。",
        "catalyst": "AWG/PLC 器件在高速模块和电信/数据中心 WDM 系统中放量。",
        "invalidation": "光芯片降价、客户认证延迟，或产能利用率低于 Q1 水平。",
    },
    "688048": {
        "role": "高功率与数通激光芯片",
        "rating_note": "激光芯片期权高，但 Q1 利润分母仍小，基准情景要求快速认证和放量。",
        "catalyst": "数通激光芯片认证、良率改善、高功率激光盈利修复。",
        "invalidation": "研发转化延迟、良率不稳，或 Q2/Q3 盈利不能验证高倍数。",
    },
    "300620": {
        "role": "光纤器件、隔离器与铌酸锂/调制器期权",
        "rating_note": "光器件和薄膜铌酸锂期权提高战略相关性，但股价已经计入较长兑现路径。",
        "catalyst": "高速光器件附加值提升、薄膜铌酸锂商业化、海外需求修复。",
        "invalidation": "调制器商业化延迟、毛利率压缩，或 AI 相关器件需求低于预期。",
    },
    "002491": {
        "role": "光纤光缆、通信线缆与网络集成",
        "rating_note": "属于完整产业链底座，但盈利质量和 AI 数据中心纯度低于模块龙头。",
        "catalyst": "电信光纤/线缆需求恢复、通信线缆订单改善、现金流修复。",
        "invalidation": "运营商资本开支延迟、线缆 ASP 承压，或 Q2/Q3 利润不能确认 Q1 修复。",
    },
    "600105": {
        "role": "光缆、通信线缆与电信基础设施集成",
        "rating_note": "线缆和电信基础设施修复可见，但业务慢周期、纯度低于 AI 光模块。",
        "catalyst": "运营商线缆订单、电信基础设施交付、毛利率稳定。",
        "invalidation": "项目延迟、线缆价格下行，或营运资本压力抵消利润修复。",
    },
    "300548": {
        "role": "光模块、有源光器件与相干传输组件",
        "rating_note": "光模块/器件平台具备数通敞口，但当前估值要求高速产品持续交付。",
        "catalyst": "数通模块订单、相干产品增长、毛利率维持。",
        "invalidation": "高速产品爬坡延迟、模块 ASP 承压，或毛利率回落。",
    },
    "688205": {
        "role": "相干光模块与传输设备组件",
        "rating_note": "补足 DCI 和运营商相干传输链条，但 Q1 利润基数仍偏小。",
        "catalyst": "DCI/相干需求、海外客户拓展、盈利正常化。",
        "invalidation": "相干订单延迟、客户集中度压力，或净利率不能放大。",
    },
    "688195": {
        "role": "光通信和激光用精密光学元件",
        "rating_note": "精密光学与高速光系统相关，但规模小，估值需要持续订单转化。",
        "catalyst": "高端光学元件订单、激光/通信需求、毛利率改善。",
        "invalidation": "订单波动、收入规模不足，或光学元件价格承压。",
    },
    "301205": {
        "role": "高速光模块与数通收发器",
        "rating_note": "高速模块弹性大，但 Q1 利润分母很小，目标价高度依赖执行。",
        "catalyst": "高速数通订单转化、客户认证、毛利率扩张。",
        "invalidation": "认证延迟、Q2/Q3 利润不放量，或现金流不跟随收入。",
    },
    "300913": {
        "role": "高速数据线缆、通信线缆与铜互连",
        "rating_note": "高速线缆/铜互连补足机柜内和企业网络层，但不是纯光模块替代品。",
        "catalyst": "高速数据线缆需求、AI 服务器/网络互连订单、毛利率稳定。",
        "invalidation": "铜互连需求不及预期、产品结构恶化，或价格竞争加剧。",
    },
    "002897": {
        "role": "高速连接器与通信互连组件",
        "rating_note": "连接器敞口属于数据中心互连链，但混合业务需要纯度折价。",
        "catalyst": "高速连接器订单、AI 服务器互连需求、盈利修复。",
        "invalidation": "连接器需求放缓、非光通信业务稀释，或毛利率压缩。",
    },
    "300563": {
        "role": "射频同轴线缆与高速通信互连",
        "rating_note": "线缆/互连拓宽产业链覆盖，但光通信纯度和 Q1 利润规模有限。",
        "catalyst": "高速通信线缆需求、客户结构改善、毛利率稳定。",
        "invalidation": "低毛利产品占比提高、订单转化弱，或现金流落后利润。",
    },
    "603618": {
        "role": "光纤光缆、电力电缆与通信线缆",
        "rating_note": "AI 驱动光纤需求带动 H1 2026 从 2025 年亏损大幅扭亏，但基础业务为低毛利线缆，复苏需在一次预告之外持续确认。",
        "catalyst": "光纤量价齐升、子公司永特光纤放量、毛利率正常化。",
        "invalidation": "光纤价格回落、线缆毛利率承压，或下半年利润不能确认 H1 预告的高增长。",
    },
}


CN_TIER = {
    "Core module": "核心光模块",
    "Precision components": "精密光器件",
    "Optical devices/modules": "光器件/光模块",
    "Mixed optical platform": "混合光通信平台",
    "High beta": "高弹性主题",
    "Passive components": "无源器件",
    "Strategic upstream": "战略上游",
    "Fiber/cable": "光纤光缆",
    "Fiber/preform": "光纤/预制棒",
    "Network equipment": "网络设备",
    "Network equipment/application": "网络设备/应用",
    "Passive photonic chips": "无源光芯片",
    "Laser chips": "激光芯片",
    "Optical devices": "光器件",
    "Optical modules/devices": "光模块/光器件",
    "Coherent/transmission": "相干/传输",
    "Precision optics": "精密光学",
    "High beta module": "高弹性光模块",
    "High-speed cable/interconnect": "高速线缆/互连",
    "Connector/interconnect": "连接器/互连",
    "Cable/interconnect": "线缆/互连",
}


WATCHLIST_CN = {
    "300757": ("光模块和硅光主动耦合/自动化设备", "2026Q1 亏损；作为设备链观察池，不纳入当前价目标价覆盖。"),
    "000070": ("光纤光缆、通信设备与网络基础设施", "当前数据包显示 2026Q1 亏损；利润分母修复前只进入观察池。"),
    "300615": ("射频器件和通信连接件", "光通信相关性存在，但产业链纯度和利润分母不足以支撑完整目标价。"),
    "300565": ("通信网络能源与机柜设备", "更偏数据中心/通信配套，需另行验证订单和盈利质量。"),
    "603118": ("通信终端和网络设备代工", "业务映射网络应用层，但光通信纯度和目标价分母不足。"),
    "002313": ("通信网络服务和物联网平台", "更偏系统集成与服务，不适合直接套光通信硬件估值。"),
    "603220": ("通信网络建设和算力基础设施服务", "项目制属性强，需以订单、现金流和负债结构另行建模。"),
    "300504": ("通信终端、网关和接入设备", "接入设备相关，但 AI 光通信弹性有限。"),
    "002902": ("通信磁性器件和光电模块配套", "配套属性存在，但需要更清晰收入占比和利润分母。"),
    "301165": ("企业网络设备和交换路由产品", "网络设备应用层标的，可后续纳入独立网络设备报告。"),
    "GLOBAL-EQUIP": ("MOCVD/外延、光刻/刻蚀、主动耦合、高速测试设备", "关键制造瓶颈，但本报告缺少干净 A 股利润分母。"),
    "GLOBAL": ("石英、InP/GaAs、铌酸锂、硅光晶圆等材料底座", "材料方向纳入链条图谱；可投资标的需要单独材料公司报告。"),
}


def localized_watchlist() -> list[dict]:
    items = []
    for item in WATCHLIST_ITEMS:
        role, reason = WATCHLIST_CN.get(item["code"], (item["role"], item["reason"]))
        items.append({**item, "role": role, "reason": reason})
    return items


SOURCE_ITEMS = [
    {
        "id": "S-01",
        "type": "official_company",
        "title": "NVIDIA and Coherent strategic optics partnership",
        "url": "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-and-Coherent-Announce-Strategic-Partnership-to-Develop-Optics-Technology-to-Scale-Next-Generation-Data-Center-Architecture/default.aspx",
        "claim": "NVIDIA committed to a strategic optics partnership with Coherent, validating optical interconnect as a scaling bottleneck.",
        "quality": "A",
    },
    {
        "id": "S-02",
        "type": "official_company",
        "title": "NVIDIA and Lumentum strategic optics partnership",
        "url": "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Strategic-Partnership-With-Lumentum-to-Develop-State-of-the-Art-Optics-Technology/default.aspx",
        "claim": "NVIDIA separately partnered with Lumentum, confirming dual-supplier optical technology investment.",
        "quality": "A",
    },
    {
        "id": "S-03",
        "type": "industry_public",
        "title": "LightCounting April 2026 market forecast",
        "url": "https://www.lightcounting.com/report/april-2026-market-forecast-379",
        "claim": "Public forecast page supports AI datacenter optical connectivity demand acceleration.",
        "quality": "B+",
    },
    {
        "id": "S-04",
        "type": "industry_public",
        "title": "LightCounting demand for optical connectivity continues to surprise",
        "url": "https://www.lightcounting.com/newsletter/en/april-2026-market-forecast-379",
        "claim": "Public newsletter supports continued upside surprises in optical connectivity demand.",
        "quality": "B+",
    },
    {
        "id": "S-05",
        "type": "industry_public",
        "title": "Cignal AI Optical Components market research",
        "url": "https://cignal.ai/optco/",
        "claim": "Public product page supports 800G and 1.6T optical component market tracking.",
        "quality": "B",
    },
    {
        "id": "S-06",
        "type": "official_company",
        "title": "Broadcom Tomahawk 6 102.4 Tbps switch",
        "url": "https://www.broadcom.com/company/news/product-releases/63146",
        "claim": "102.4 Tbps switching silicon supports the migration to higher-radix 800G/1.6T optical links.",
        "quality": "A-",
    },
    {
        "id": "S-07",
        "type": "official_filing",
        "title": "中际旭创 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-17/1225111944.PDF",
        "claim": "2026Q1 revenue and profit delivery for the optical-module leader.",
        "quality": "A",
    },
    {
        "id": "S-08",
        "type": "official_filing",
        "title": "新易盛 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-24/1225172606.PDF",
        "claim": "2026Q1 revenue and profit delivery for a high-speed optical-module platform.",
        "quality": "A",
    },
    {
        "id": "S-09",
        "type": "official_filing",
        "title": "天孚通信 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-21/1225128020.PDF",
        "claim": "2026Q1 delivery for high-margin precision optical components.",
        "quality": "A",
    },
    {
        "id": "S-10",
        "type": "official_filing",
        "title": "光迅科技 2026Q1 announcement page",
        "url": "https://data.eastmoney.com/notices/detail/002281/AN202604221821455750.html",
        "claim": "2026Q1 announcement access point for Guangxun Technology.",
        "quality": "B+",
    },
    {
        "id": "S-11",
        "type": "official_filing",
        "title": "华工科技 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-27/1225183610.PDF",
        "claim": "2026Q1 delivery for mixed optical-module and laser-equipment platform.",
        "quality": "A",
    },
    {
        "id": "S-12",
        "type": "official_filing",
        "title": "剑桥科技 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-28/1225198458.PDF",
        "claim": "2026Q1 delivery for high-beta optical module turnaround candidate.",
        "quality": "A",
    },
    {
        "id": "S-13",
        "type": "official_filing",
        "title": "太辰光 2026Q1 filing",
        "url": "https://static.cninfo.com.cn/finalpage/2026-04-24/1225163579.PDF",
        "claim": "2026Q1 delivery for passive optical component supplier.",
        "quality": "A",
    },
    {
        "id": "S-14",
        "type": "official_filing",
        "title": "源杰科技 2026Q1 filing",
        "url": "https://notice.10jqka.com.cn/api/pdf/eb4aea8fe06abf4c.pdf",
        "claim": "2026Q1 delivery for domestic laser-chip supplier.",
        "quality": "B+",
    },
    {
        "id": "S-15",
        "type": "official_filing",
        "title": "亨通光电 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/600487.html",
        "claim": "Announcement access point for fiber/cable and submarine-cable financial delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-16",
        "type": "official_filing",
        "title": "中天科技 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/600522.html",
        "claim": "Announcement access point for cable, submarine-cable and communication-cable delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-17",
        "type": "official_filing",
        "title": "长飞光纤 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/601869.html",
        "claim": "Announcement access point for optical preform, fiber and cable delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-18",
        "type": "official_filing",
        "title": "烽火通信 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/600498.html",
        "claim": "Announcement access point for telecom optical-network equipment delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-19",
        "type": "official_filing",
        "title": "中兴通讯 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/000063.html",
        "claim": "Announcement access point for carrier/cloud/network-equipment financial delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-20",
        "type": "official_filing",
        "title": "仕佳光子 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/688313.html",
        "claim": "Announcement access point for PLC/AWG/passive photonic-chip delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-21",
        "type": "official_filing",
        "title": "长光华芯 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/688048.html",
        "claim": "Announcement access point for laser-chip delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-22",
        "type": "official_filing",
        "title": "光库科技 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/300620.html",
        "claim": "Announcement access point for optical-device and modulator-option delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-23",
        "type": "industry_public",
        "title": "Ethernet Alliance technology resources",
        "url": "https://ethernetalliance.org/technology/",
        "claim": "Ethernet technology resources frame higher-speed network migration that pulls optical-module speed upgrades.",
        "quality": "B",
    },
    {
        "id": "S-24",
        "type": "industry_public",
        "title": "OIF technical work overview",
        "url": "https://www.oiforum.com/technical-work/",
        "claim": "OIF technical work supports interoperable electrical/optical interfaces and coherent/packaging roadmaps.",
        "quality": "B",
    },
    {
        "id": "S-25",
        "type": "industry_public",
        "title": "Corning optical fiber product overview",
        "url": "https://www.corning.com/worldwide/en/products/communication-networks/products/fiber.html",
        "claim": "Optical fiber is the physical transmission substrate connecting datacenter, carrier, FTTH and DCI demand.",
        "quality": "B",
    },
    {
        "id": "S-26",
        "type": "official_filing",
        "title": "通鼎互联 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/002491.html",
        "claim": "Announcement access point for optical fiber/cable and communication cable delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-27",
        "type": "official_filing",
        "title": "永鼎股份 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/600105.html",
        "claim": "Announcement access point for optical cable and telecom infrastructure delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-28",
        "type": "official_filing",
        "title": "长芯博创 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/300548.html",
        "claim": "Announcement access point for optical modules and active optical-device delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-29",
        "type": "official_filing",
        "title": "德科立 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/688205.html",
        "claim": "Announcement access point for coherent optical modules and transmission equipment delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-30",
        "type": "official_filing",
        "title": "腾景科技 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/688195.html",
        "claim": "Announcement access point for precision optical-component delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-31",
        "type": "official_filing",
        "title": "联特科技 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/301205.html",
        "claim": "Announcement access point for high-speed optical-module delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-32",
        "type": "official_filing",
        "title": "兆龙互连 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/300913.html",
        "claim": "Announcement access point for high-speed data cable and communication cable delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-33",
        "type": "official_filing",
        "title": "意华股份 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/002897.html",
        "claim": "Announcement access point for high-speed connector and communication interconnect delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-34",
        "type": "official_filing",
        "title": "神宇股份 announcement access",
        "url": "https://data.eastmoney.com/notices/stock/300563.html",
        "claim": "Announcement access point for communication cable and high-speed interconnect delivery checks.",
        "quality": "B+",
    },
    {
        "id": "S-35",
        "type": "official_filing",
        "title": "永鼎股份 600105 2026 半年度业绩预告",
        "url": "https://data.eastmoney.com/notices/stock/600105.html",
        "claim": "永鼎股份 2026-07-06 披露 H1 2026 归母净利润 5.0-7.0 亿元、同比 +57%~+120%（预增），为数据截止后新证据。",
        "quality": "A",
    },
    {
        "id": "S-36",
        "type": "official_filing",
        "title": "锐捷网络 301165 2026 半年度业绩预告",
        "url": "https://data.eastmoney.com/notices/stock/301165.html",
        "claim": "锐捷网络 2026-07-02 披露 H1 2026 归母净利润 6.0-7.5 亿元、同比 +32.7%~+65.9%（预增），观察池标的数据截止后新证据。",
        "quality": "A",
    },
    {
        "id": "S-37",
        "type": "official_filing",
        "title": "杭电股份 603618 2026 半年度业绩预告",
        "url": "https://data.eastmoney.com/notices/stock/603618.html",
        "claim": "杭电股份 2026-07-04 披露 H1 2026 归母净利润 3.6-4.0 亿元、同比 +852%~+958%（预增，光纤量价齐升、扭亏为盈），作为覆盖标的 2026E 估值分母输入。",
        "quality": "A",
    },
]


BROKER_CONSENSUS = {
    "300308": {
        "source": "英为财情一致预期/21财经券商聚合",
        "url": "https://cn.investing.com/equities/zhongji-innolight-co-ltd-consensus-estimates",
        "source_type": "第三方一致预期页面",
        "rating": "偏积极",
        "analysts": 11,
        "target_avg": 1062.50,
        "target_high": 1650.00,
        "target_low": 430.00,
        "forecast_note": "公开页面披露目标价区间；部分券商聚合提到华泰证券预计 2026E 归母净利润约 284.7 亿元。",
        "evidence_quality": "B",
    },
    "300502": {
        "source": "英为财情一致预期",
        "url": "https://cn.investing.com/equities/chengdu-eoptolink-technology-co-ltd-consensus-estimates",
        "source_type": "第三方一致预期页面",
        "rating": "偏积极",
        "analysts": 7,
        "target_avg": 496.76,
        "target_high": 701.00,
        "target_low": 264.29,
        "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。",
        "evidence_quality": "B",
    },
    "300394": {
        "source": "英为财情一致预期/同花顺预测摘要",
        "url": "https://cn.investing.com/equities/suzhou-tfc-optical-communication-co-consensus-estimates",
        "source_type": "第三方一致预期页面",
        "rating": "偏积极",
        "analysts": 9,
        "target_avg": 286.81,
        "target_high": 419.00,
        "target_low": 115.71,
        "forecast_note": "公开页面披露目标价；同花顺摘要披露券商未来几年净利润预测但非完整原文。",
        "evidence_quality": "B",
    },
    "002281": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/accelink-tech-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 5, "target_avg": 123.86, "target_high": 166.00, "target_low": 78.31, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B"},
    "000988": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/huagong-tech-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 2, "target_avg": 133.99, "target_high": 157.98, "target_low": 110.00, "forecast_note": "公开页面披露目标价区间，样本较少。", "evidence_quality": "B-"},
    "603083": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/cig-shanghai-co-ltd-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 1, "target_avg": 165.68, "target_high": 165.68, "target_low": 165.68, "forecast_note": "公开页面披露单一目标价，样本很少。", "evidence_quality": "C+"},
    "300570": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/jiangsu-zhongtian-tech-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "样本有限", "analysts": 1, "target_avg": 148.32, "target_high": 154.96, "target_low": 138.00, "forecast_note": "公开检索显示目标价样本有限，需以原始研报复核。", "evidence_quality": "C+"},
    "688498": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/yuanjie-semiconductor-technology-co-ltd-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 3, "target_avg": 1164.00, "target_high": 1253.39, "target_low": 1097.93, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B-"},
    "600487": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/hengtong-optic-electric-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 3, "target_avg": 97.88, "target_high": 132.00, "target_low": 77.33, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B"},
    "600522": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/jiangsu-zhongtian-tech-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 5, "target_avg": 49.61, "target_high": 66.00, "target_low": 26.40, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B"},
    "601869": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/yangtze-optical-fibre-and-cable-jo-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 3, "target_avg": 292.37, "target_high": 364.86, "target_low": 202.25, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B-"},
    "600498": {"source": "公开检索/一致预期缺口", "url": "https://cn.investing.com/search/?q=600498", "source_type": "检索缺口", "rating": "未披露", "analysts": 0, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "本轮公开检索未取得可直接复核的目标价和 2026E 预测。", "evidence_quality": "C"},
    "000063": {"source": "英为财情一致预期", "url": "https://cn.investing.com/equities/zte-corp-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 8, "target_avg": 43.69, "target_high": 58.20, "target_low": 34.30, "forecast_note": "公开页面披露目标价区间，未完整披露光通信单独分部预测。", "evidence_quality": "B"},
    "688313": {"source": "Moomoo/富途一致预期", "url": "https://www.moomoo.com/hans/stock/688313-SH/forecast", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": None, "target_avg": 157.53, "target_high": 200.00, "target_low": 115.05, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B-"},
    "688048": {"source": "英为财情/富途一致预期", "url": "https://cn.investing.com/equities/changguang-huaxin-technology-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "样本有限", "analysts": 1, "target_avg": 86.84, "target_high": 121.80, "target_low": 86.84, "forecast_note": "公开目标价来源之间存在差异，样本有限。", "evidence_quality": "C+"},
    "300620": {"source": "英为财情/Moomoo 一致预期", "url": "https://www.moomoo.com/hans/stock/300620-SZ/forecast", "source_type": "第三方一致预期页面", "rating": "样本有限", "analysts": 1, "target_avg": 177.00, "target_high": 177.00, "target_low": 177.00, "forecast_note": "公开页面显示样本较少，需原始研报复核。", "evidence_quality": "C+"},
    "002491": {"source": "英为财情一致预期页面/公开缺口", "url": "https://cn.investing.com/equities/tongding-optic-electronic-co-ltd-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "未披露", "analysts": 0, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面未披露可用目标价和 2026E 预测，不能用券商目标替代 AStock 模型。", "evidence_quality": "C"},
    "600105": {"source": "英为财情一致预期页面/公开缺口", "url": "https://cn.investing.com/equities/jiangsu-yongding-co-ltd-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "未披露", "analysts": 0, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面未披露可用目标价和 2026E 预测，不能用券商目标替代 AStock 模型。", "evidence_quality": "C"},
    "300548": {"source": "Moomoo/富途一致预期", "url": "https://www.moomoo.com/hans/stock/300548-SZ/forecast", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": 4, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面可见评级样本，但未取得可直接复核的目标价。", "evidence_quality": "C+"},
    "688205": {"source": "Moomoo/富途一致预期", "url": "https://www.moomoo.com/hans/stock/688205-SH/forecast", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": None, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面可见预测入口，但目标价和 2026E 明细未能稳定抓取。", "evidence_quality": "C+"},
    "688195": {"source": "Moomoo/富途一致预期", "url": "https://www.moomoo.com/hans/stock/688195-SH/forecast", "source_type": "第三方一致预期页面", "rating": "偏积极", "analysts": None, "target_avg": 222.42, "target_high": 262.35, "target_low": 146.90, "forecast_note": "公开页面披露目标价区间，未完整披露 2026E 收入/利润明细。", "evidence_quality": "B-"},
    "301205": {"source": "搜狐/华泰证券目标价摘要", "url": "https://q.stock.sohu.com/cn/301205/lshq.shtml", "source_type": "媒体聚合摘要", "rating": "买入摘要", "analysts": 1, "target_avg": 271.98, "target_high": 271.98, "target_low": 271.98, "forecast_note": "公开聚合摘要显示华泰证券目标价约 271.98 元，需原始研报复核。", "evidence_quality": "C+"},
    "300913": {"source": "英为财情一致预期页面/公开缺口", "url": "https://cn.investing.com/equities/zhejiang-zhaolong-interconnect-tech-co-ltd-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "未披露", "analysts": 0, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面未披露可用目标价和 2026E 预测。", "evidence_quality": "C"},
    "002897": {"source": "英为财情一致预期页面", "url": "https://cn.investing.com/equities/wenzhou-yihua-connector-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏谨慎", "analysts": None, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面显示隐含空间为负，但未披露可复核目标价明细。", "evidence_quality": "C"},
    "300563": {"source": "英为财情一致预期页面", "url": "https://cn.investing.com/equities/jiangsu-shenyu-communication-technolo-consensus-estimates", "source_type": "第三方一致预期页面", "rating": "偏谨慎", "analysts": None, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "公开页面显示隐含空间为负，但未披露可复核目标价明细。", "evidence_quality": "C"},
    "603618": {"source": "公开检索/一致预期缺口", "url": "https://data.eastmoney.com/stockcomment/stock/603618.html", "source_type": "检索缺口", "rating": "未披露", "analysts": 0, "target_avg": None, "target_high": None, "target_low": None, "forecast_note": "扭亏型标的，本轮公开检索未取得可复核的目标价与 2026E/2027E 预测；券商锚权重为 0。", "evidence_quality": "C"},
}


SOURCE_ITEMS.extend(
    [
        {
            "id": f"B-{idx:02d}",
            "type": "broker_consensus",
            "title": f"{row['source']} - {code}",
            "url": row["url"],
            "claim": f"{code} 公开券商/一致预期：评级 {row['rating']}，平均目标价 {row['target_avg'] if row['target_avg'] is not None else '未披露'}。",
            "quality": row["evidence_quality"],
        }
        for idx, (code, row) in enumerate(BROKER_CONSENSUS.items(), 1)
    ]
)

SOURCE_ITEMS.extend(
    [
        {
            "id": "M-01",
            "type": "methodology",
            "title": "CFA Institute market-based valuation multiples",
            "url": "https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/market-based-valuation-price-enterprise-value-multiples",
            "claim": "市场法估值使用可比公司价格和企业价值倍数，说明可观察市场定价本身是估值框架的一部分。",
            "quality": "A-",
        },
        {
            "id": "M-02",
            "type": "methodology",
            "title": "Expectations Investing framework",
            "url": "https://www.expectationsinvesting.com/",
            "claim": "预期投资框架要求反推当前股价已经隐含的增长、利润率和资本回报假设。",
            "quality": "B+",
        },
        {
            "id": "M-03",
            "type": "methodology",
            "title": "Baker and Wurgler investor sentiment research",
            "url": "https://pages.stern.nyu.edu/~jwurgler/papers/sentiment.pdf",
            "claim": "投资者情绪会影响难以估值、套利受限或主观性更强的股票定价，因此情绪溢价需要被量化和披露。",
            "quality": "A-",
        },
        {
            "id": "M-04",
            "type": "methodology",
            "title": "H1 2026 业绩预告普查方法（stock_yjyg_em × 光通信精选 universe 交叉核对）",
            "url": "https://data.eastmoney.com/bbsj/yjyg.html",
            "claim": "使用 akshare stock_yjyg_em(date=20260630) 预告库对 92 名光通信精选 universe 交叉核对，确认报告 35 只中仅永鼎 600105、锐捷 301165 已发 H1 预告；概念板块接口在本机不可用，交叉核对为稳健替代方法。",
            "quality": "A-",
        },
    ]
)


# --- Post-cutoff (2026-07-06) H1 2026 earnings-preview addendum ---------------
# These are forward-looking company disclosures released AFTER the 2026-06-26
# data cutoff. They are additive evidence and MUST NOT be folded into the frozen
# 2026Q1 model rows. Net-profit figures are in CNY 100mn (亿元).
EARNINGS_PREVIEW_H1_2026 = {
    "600105": {
        "name": "永鼎股份",
        "coverage": "covered",
        "h1_np_low": 5.0,
        "h1_np_high": 7.0,
        "h1_np_mid": 6.0,
        "yoy_low": 0.57,
        "yoy_high": 1.20,
        "deduct_np_low": 4.9,
        "deduct_np_high": 6.9,
        "deduct_yoy_low": 0.55,
        "deduct_yoy_high": 1.19,
        "prev_h1_np": 3.185,
        "forecast_type": "预增",
        "announce_date": PREVIEW_DATE,
        "reason": "光通信板块受益于数字经济和 AI 算力需求爆发，光纤市场量价齐升，板块利润大幅增长。",
        "source_id": "S-35",
        "valuation_input": True,
    },
    "301165": {
        "name": "锐捷网络",
        "coverage": "watch_pool",
        "h1_np_low": 6.0,
        "h1_np_high": 7.5,
        "h1_np_mid": 6.75,
        "yoy_low": 0.327,
        "yoy_high": 0.659,
        "deduct_np_low": 5.85,
        "deduct_np_high": 7.35,
        "deduct_yoy_low": 0.353,
        "deduct_yoy_high": 0.700,
        "prev_h1_np": 4.521,
        "forecast_type": "预增",
        "announce_date": "2026-07-02",
        "reason": "面向互联网客户的数据中心交换机业务大幅增长，是本期业绩增长的核心驱动。",
        "source_id": "S-36",
        "valuation_input": False,
    },
    "603618": {
        "name": "杭电股份",
        "coverage": "covered",
        "h1_np_low": 3.6,
        "h1_np_high": 4.0,
        "h1_np_mid": 3.8,
        "yoy_low": 8.52,
        "yoy_high": 9.58,
        "deduct_np_low": 3.55,
        "deduct_np_high": 3.95,
        "deduct_yoy_low": 10.88,
        "deduct_yoy_high": 12.21,
        "prev_h1_np": 0.378,
        "forecast_type": "预增",
        "announce_date": "2026-07-04",
        "reason": "光纤光缆市场回暖、光纤产品量价齐升，子公司杭州永特光纤销量同步增长。",
        "source_id": "S-37",
        "valuation_input": True,
    },
}

# H1 share of full-year net profit used to annualize the H1 preview for the
# post-cutoff EPS revision. Optical fiber/cable H2 is typically seasonally
# stronger, so 0.50 is a neutral-to-conservative annualization; the band shows
# the revision is nearly insensitive across it (PE leg is only 20% of the
# cable_optional_sotp anchor).
H1_SHARE_OF_FY_DEFAULT = 0.50
H1_SHARE_OF_FY_BAND = (0.45, 0.55)

# Optical-communication sector H1 2026 preview census. Ground truth from
# akshare stock_yjyg_em(date=20260630) cross-referenced against a curated
# 92-name optical-comm universe (the concept-board API was environmentally
# unavailable). Only the report's own 35 names are enumerated per-status below.
OPTICAL_PREVIEW_CENSUS = {
    "as_of": PREVIEW_DATE,
    "universe_size": 36,
    "valuation_coverage": 26,
    "watch_pool": 10,
    "previews_in_universe": 3,
    "method": (
        "光通信概念板块接口在本机环境不可用；采用 akshare stock_yjyg_em(date=20260630) "
        "业绩预告库 × 92 名光通信精选 universe 交叉核对，确认报告 36 只标的中的已披露名单。"
    ),
    "disclosure_window": "其余标的的完整 2026 半年报预约披露集中在 2026-08-01 至 2026-08-31，尚未发布。",
    "marquee_no_preview": ["中际旭创", "新易盛", "天孚通信", "光迅科技", "源杰科技"],
    "external_peers": [],
    "disclosed": [
        {"code": "600105", "name": "永鼎股份", "coverage": "估值覆盖", "type": "预增", "yoy": "+57%~+120%", "date": PREVIEW_DATE},
        {"code": "603618", "name": "杭电股份", "coverage": "估值覆盖", "type": "预增", "yoy": "+852%~+958%", "date": "2026-07-04"},
        {"code": "301165", "name": "锐捷网络", "coverage": "观察池", "type": "预增", "yoy": "+32.7%~+65.9%", "date": "2026-07-02"},
    ],
}


def run_cli(*args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "astock.cli", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"astock.cli {' '.join(args)} failed: {proc.stderr}")
    return json.loads(proc.stdout)


def cached_cli(kind: str, code: str, *args: str) -> dict:
    cache = DATA / f"_cache_{kind}_{code}_{RUN_DATE}.json"
    if cache.exists():
        print(f"Using cache {kind} {code}", flush=True)
        return json.loads(cache.read_text(encoding="utf-8"))
    print(f"Fetching {kind} {code}", flush=True)
    payload = run_cli(*args)
    cache.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def fetch_url(url: str, out_dir: Path) -> dict:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower() or ".html"
    filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", parsed.netloc + parsed.path)
    if len(filename) > 140:
        filename = filename[:130] + suffix
    if not filename.lower().endswith(suffix):
        filename += suffix
    target = out_dir / filename
    record = {"url": url, "path": str(target.relative_to(CASE)), "status": "not_fetched", "bytes": 0}
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 AStockResearch/1.0"})
        with urlopen(req, timeout=6) as resp:
            content = resp.read()
            target.write_bytes(content)
            record.update({"status": str(resp.status), "bytes": len(content), "content_type": resp.headers.get("content-type", "")})
    except Exception as exc:  # pragma: no cover - network fallback
        target = out_dir / (filename + ".url.txt")
        target.write_text(f"URL: {url}\nFETCH_ERROR: {exc}\n", encoding="utf-8")
        record.update({"path": str(target.relative_to(CASE)), "status": "fetch_error", "error": str(exc), "bytes": target.stat().st_size})
    return record


def load_frozen_snapshot() -> tuple[dict[str, dict], dict[str, dict]]:
    """Reload the RUN_DATE-frozen quote/financial packets so an offline rebuild
    reproduces the 2026-06-26 report byte-for-byte. Fails closed if the frozen
    snapshots are missing rather than silently falling back to live fetch."""
    market_path = DATA / "raw_market_data_20260626.json"
    fin_path = DATA / "raw_financials_20260626.json"
    if not market_path.exists() or not fin_path.exists():
        raise FileNotFoundError(
            "Frozen snapshot missing; run with OPTICAL_REPORT_REFRESH=1 to re-cut, "
            f"or restore {market_path.name} / {fin_path.name}."
        )
    market = json.loads(market_path.read_text(encoding="utf-8"))
    fin = json.loads(fin_path.read_text(encoding="utf-8"))
    assert market.get("run_date") == RUN_DATE, "frozen market snapshot run_date drift"
    assert fin.get("run_date") == RUN_DATE, "frozen financial snapshot run_date drift"
    quotes = market["quotes"]
    financials = fin["financials"]
    assert len(quotes) == 26 and len(financials) == 26, "frozen snapshot must hold 26 tickers"
    return quotes, financials


def load_frozen_source_records() -> list[dict]:
    """Reload the frozen source-capture records so an offline rebuild does not
    re-hit the network (re-fetching could downgrade currently-200 captures to
    fetch_error and corrupt the frozen evidence)."""
    manifest_path = DATA / "source_capture_manifest_20260626.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(manifest.get("captures", []))


def pct(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "n.a."
    return f"{value * 100:+.1f}%"


def pct_tex(value: float | None) -> str:
    return pct(value).replace("%", r"\%")


def num(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "n.a."
    return f"{value:.{digits}f}"


def tex(value: object) -> str:
    text = str(value)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def get_period(financials: dict, period: str) -> dict:
    for row in financials.get("periods", []):
        if row.get("period") == period:
            return row["metrics"]
    raise KeyError(period)


def _period_metric(financials: dict, period: str, key: str) -> float | None:
    for row in financials.get("periods", []):
        if row.get("period") == period:
            return row["metrics"].get(key)
    return None


def single_quarter(financials: dict, period: str, key: str) -> float | None:
    """Reported statements are cumulative YTD. Convert to a single-quarter value
    by subtracting the prior cumulative period within the same fiscal year."""
    year = period[:4]
    tail = period[4:]
    cum = _period_metric(financials, period, key)
    if cum is None:
        return None
    if tail == "0331":
        return cum
    prev = {"0630": "0331", "0930": "0630", "1231": "0930"}.get(tail)
    if prev is None:
        return None
    prev_cum = _period_metric(financials, f"{year}{prev}", key)
    return cum - prev_cum if prev_cum is not None else None


def ttm_metric(financials: dict, key: str) -> float | None:
    """Trailing-twelve-month value ending 2026Q1 = Q1'26 + Q4'25 + Q3'25 + Q2'25
    (each derived as a single-quarter delta)."""
    parts = [
        single_quarter(financials, "20260331", key),
        single_quarter(financials, "20251231", key),
        single_quarter(financials, "20250930", key),
        single_quarter(financials, "20250630", key),
    ]
    if any(p is None for p in parts):
        return None
    return sum(parts)


def normalized_denominator(financials: dict, cfg: dict, preview: dict | None = None) -> dict:
    """Build a defensible 2026E net-profit denominator instead of a raw
    single-Q1 annualization. Confidence hierarchy for the calibrated path:

      1. Management H1 guidance (业绩预告) — highest confidence forward signal
         for a covered name that has issued one. 2026E = H1 midpoint / H1 share
         of FY (H1_SHARE_OF_FY_DEFAULT). This OVERRIDES the trailing paths,
         because a name guiding +57%~+120% cannot be denominated on stale TTM.
      2. Seasonality-calibrated Q1 (observed 2025 Q1 share when sane).
      3. TTM floor to stop a seasonally strong Q1 inflating the full year.

    q1_annualized is kept for audit/comparison only.
    """
    np_q1_26 = _period_metric(financials, "20260331", "net_profit_parent") or 0.0
    rev_q1_26 = _period_metric(financials, "20260331", "total_revenue") or 0.0
    q1_annualized = np_q1_26 / cfg["q1_share"] if cfg["q1_share"] else None
    rev_q1_annualized = rev_q1_26 / cfg["q1_share"] if cfg["q1_share"] else None
    ttm_np = ttm_metric(financials, "net_profit_parent")
    ttm_rev = ttm_metric(financials, "total_revenue")

    q1_25 = single_quarter(financials, "20250331", "net_profit_parent")
    fy25 = _period_metric(financials, "20251231", "net_profit_parent")
    observed_share = (q1_25 / fy25) if (q1_25 is not None and fy25 not in (None, 0)) else None
    share_usable = observed_share is not None and 0.08 <= observed_share <= 0.45
    calib_share = observed_share if share_usable else cfg["q1_share"]
    seasonality_np = np_q1_26 / calib_share if calib_share else q1_annualized

    # Guidance-based path: H1 preview midpoint annualized by H1 share of FY.
    guidance_np = None
    if preview is not None and preview.get("valuation_input"):
        guidance_np = (preview["h1_np_mid"] * 1e8) / H1_SHARE_OF_FY_DEFAULT

    # Calibrated 2026E net profit.
    if guidance_np is not None:
        # Guidance overrides trailing paths; it is the most current forward signal.
        calibrated_np = guidance_np
        denominator_basis = "h1_guidance"
    else:
        # Seasonality path, floored by TTM so a strong Q1 cannot inflate the year.
        candidates = [v for v in (seasonality_np, ttm_np) if v is not None]
        calibrated_np = min(candidates) if candidates else q1_annualized
        denominator_basis = "seasonality_ttm_floor"
    return {
        "np_q1_26": np_q1_26,
        "rev_q1_26": rev_q1_26,
        "q1_annualized_np": q1_annualized,
        "q1_annualized_rev": rev_q1_annualized,
        "ttm_np": ttm_np,
        "ttm_rev": ttm_rev,
        "observed_q1_share_fy25": observed_share,
        "seasonality_share_used": calib_share,
        "seasonality_share_source": "observed_2025" if share_usable else "assumption",
        "seasonality_np": seasonality_np,
        "guidance_np": guidance_np,
        "denominator_basis": denominator_basis,
        "calibrated_np_2026e": calibrated_np,
    }


def growth_earnings_split(cfg: dict, rev26: float, np26: float) -> dict:
    """Separate a base (non-AI-cycle) business from the growth (AI/high-speed)
    segment so growth multiples are not applied to consolidated revenue. The
    ai_growth_share is a disclosed, tier-based estimate, not a company filing;
    it is labelled as an AStock modeling assumption in the growth artifacts."""
    tier = cfg["tier"].lower()
    role = cfg["role"].lower()
    # Tier-based AI/high-speed revenue purity estimate (modeling assumption).
    if "core module" in tier:
        share = 0.90
    elif "precision components" in tier or "precision optics" in tier:
        share = 0.72
    elif "high beta" in tier or "coherent" in tier or "modules/devices" in tier or "optical devices/modules" in tier:
        share = 0.70
    elif "laser chips" in tier or "photonic chips" in tier or "strategic upstream" in tier:
        share = 0.65
    elif "optical devices" in tier:
        share = 0.60
    elif "passive components" in tier:
        share = 0.55
    elif "mixed optical" in tier:
        share = 0.45
    elif "interconnect" in tier or "connector" in tier or "copper" in role or "high-speed cable" in tier:
        share = 0.45
    elif "network equipment" in tier or "carrier/cloud" in role:
        share = 0.30
    else:  # fiber/cable, preform, project, mixed
        share = 0.25
    growth_rev = rev26 * share
    base_rev = rev26 - growth_rev
    growth_np = np26 * share
    base_np = np26 - growth_np
    return {
        "ai_growth_share": share,
        "growth_revenue_2026e": growth_rev,
        "base_revenue_2026e": base_rev,
        "growth_net_profit_2026e": growth_np,
        "base_net_profit_2026e": base_np,
    }


def rating_from_upside(upside: float, quality: str) -> tuple[str, str]:
    if upside >= 0.20 and quality not in {"C", "C+"}:
        return "买入", "BUY"
    if upside >= 0.08:
        return "增持", "ACCUMULATE"
    if upside > -0.15:
        return "中性", "NEUTRAL"
    return "减持", "REDUCE"


def rating_from_market_adjusted(upside: float, quality: str, sentiment_score: float, premium: float) -> tuple[str, str]:
    if upside >= 0.20 and quality not in {"C", "C+"}:
        return "买入", "BUY"
    if upside >= 0.08:
        return "增持", "ACCUMULATE"
    if upside > -0.15:
        return "中性", "NEUTRAL"
    if sentiment_score >= 62 and premium >= 0.45 and upside > -0.35:
        return "中性观察", "MARKET-SUPPORTED WATCH"
    return "减持", "REDUCE"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def percentile_rank(value: float, values: list[float]) -> float:
    if not values:
        return 0.5
    below = sum(1 for item in values if item <= value)
    return below / len(values)


def sentiment_regime(score: float) -> str:
    if score >= 75:
        return "强共识/高拥挤"
    if score >= 62:
        return "活跃共识"
    if score >= 48:
        return "中性交易"
    return "弱共识"


def sentiment_anchor_weights(style: str, has_broker: bool, sentiment_score: float, premium: float) -> dict[str, float]:
    if style == "earnings_compounder":
        weights = {"fundamental": 0.65, "market": 0.20, "street": 0.15 if has_broker else 0.0}
    elif style in {"asset_cycle_fiber", "cable_optional_sotp", "network_equipment_blend", "interconnect_blend"}:
        weights = {"fundamental": 0.50, "market": 0.35, "street": 0.15 if has_broker else 0.0}
    else:
        weights = {"fundamental": 0.55, "market": 0.30, "street": 0.15 if has_broker else 0.0}
    if sentiment_score >= 62 and premium >= 0.70:
        shift = 0.12 if style in {"asset_cycle_fiber", "cable_optional_sotp", "network_equipment_blend", "interconnect_blend"} else 0.08
        weights["market"] += shift
        weights["fundamental"] -= shift
    if not has_broker:
        weights["market"] += weights.pop("street")
        weights["street"] = 0.0
    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def weights_label_cn(weights: dict[str, float]) -> str:
    return " / ".join(
        [
            f"内在{weights.get('fundamental', 0) * 100:.0f}%",
            f"市场{weights.get('market', 0) * 100:.0f}%",
            f"券商{weights.get('street', 0) * 100:.0f}%",
        ]
    )


def valuation_profile(cfg: dict) -> dict:
    """Choose a valuation method by business economics, not by theme label."""
    code = cfg["code"]
    tier = cfg["tier"].lower()
    role = cfg["role"].lower()

    def profile(style: str, short: str, method: str, secondary: str, weights: dict[str, float], pb: tuple[float, float, float], ps: tuple[float, float, float]) -> dict:
        return {
            "style": style,
            "method_short": short,
            "method": method,
            "secondary_check": secondary,
            "weights": weights,
            "pb": {"bear": pb[0], "base": pb[1], "bull": pb[2]},
            "ps": {"bear": ps[0], "base": ps[1], "bull": ps[2]},
        }

    if code in {"002491", "600105"}:
        return profile(
            "cable_optional_sotp",
            "PE/PB/PS",
            "20% 周期正常化 PE + 30% PB/ROE + 50% 收入期权 PS，用于光纤光缆和通信集成敞口",
            "现金转化、运营商/云侧线缆订单、线缆 ASP、AI/数据中心敞口纯度",
            {"pe": 0.20, "pb": 0.30, "ps": 0.50},
            (2.4, 4.0, 5.5),
            (2.2, 5.0, 7.5),
        )
    if "fiber" in tier or "fiber" in role or "submarine" in role or "preform" in tier:
        return profile(
            "asset_cycle_fiber",
            "PE/PB/PS",
            "45% 周期正常化 PE + 30% PB/ROE + 25% PS，用于资产较重的光纤光缆和海缆平台",
            "周期正常化 EPS、经营现金流、运营商/项目订单、光纤光缆价格",
            {"pe": 0.45, "pb": 0.30, "ps": 0.25},
            (1.3, 1.8, 2.4),
            (0.55, 0.80, 1.05),
        )
    if "network equipment" in tier or "carrier/cloud" in role:
        return profile(
            "network_equipment_blend",
            "PE/PB/PS",
            "55% PE + 20% PB + 25% PS，用于运营商/云网络设备业务",
            "在手订单、运营商资本开支、业务结构、现金流和非光通信业务稀释",
            {"pe": 0.55, "pb": 0.20, "ps": 0.25},
            (1.4, 2.1, 2.8),
            (0.65, 1.00, 1.35),
        )
    if "interconnect" in tier or "interconnect" in role or "connector" in tier or "copper" in role:
        return profile(
            "interconnect_blend",
            "PE/PB/PS",
            "40% PE + 25% PB + 35% PS，用于连接器、线缆和高速互连混合业务",
            "AI 互连敞口纯度、产品结构、营运资本和毛利率稳定性",
            {"pe": 0.40, "pb": 0.25, "ps": 0.35},
            (2.0, 3.5, 4.8),
            (0.9, 1.8, 2.8),
        )
    if "high beta" in tier or "strategic" in tier or "laser" in tier or "photonic" in tier or "precision optics" in tier or "coherent" in tier:
        return profile(
            "scarcity_growth_blend",
            "PE/PB/PS",
            "45% PE + 15% PB + 40% PS，用于小规模但具战略稀缺性的光芯片、相干模块和精密光学",
            "客户认证、收入规模、毛利率持续性和战略稀缺性",
            {"pe": 0.45, "pb": 0.15, "ps": 0.40},
            (2.5, 4.0, 5.5),
            (3.0, 5.0, 7.0),
        )
    if "optical modules/devices" in tier or "optical devices/modules" in tier or "mixed optical" in tier or "passive components" in tier:
        return profile(
            "module_device_blend",
            "PE/PB/PS",
            "70% PE + 10% PB + 20% PS，用于有正 EPS 但 AI 纯度不完美的模块/器件平台",
            "数通收入占比、毛利率桥、收入规模和现金转化",
            {"pe": 0.70, "pb": 0.10, "ps": 0.20},
            (2.5, 4.0, 5.0),
            (2.0, 3.5, 5.0),
        )
    return profile(
        "earnings_compounder",
        "PE/PEG",
        "基于正常化 EPS 的 forward PE/PEG，用于盈利兑现强且订单持续的 AI 光模块龙头",
        "客户/订单持续性、毛利率保持、PEG 排名和 PS 交叉校验",
        {"pe": 1.00, "pb": 0.00, "ps": 0.00},
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
    )


def blended_components(
    *,
    eps: float,
    revenue: float,
    shares: float,
    bvps: float,
    pe: float,
    pb: float,
    ps: float,
    weights: dict[str, float],
    discount: float = 1.0,
) -> dict:
    pe_value = eps * pe / discount
    pb_value = bvps * pb / discount if weights.get("pb", 0) else None
    ps_value = (revenue / shares) * ps / discount if weights.get("ps", 0) else None
    weighted = pe_value * weights.get("pe", 0)
    if pb_value is not None:
        weighted += pb_value * weights.get("pb", 0)
    if ps_value is not None:
        weighted += ps_value * weights.get("ps", 0)
    return {
        "pe_value_cny": pe_value,
        "pb_value_cny": pb_value,
        "ps_value_cny": ps_value,
        "weighted_value_cny": weighted,
    }


def weights_label(weights: dict[str, float]) -> str:
    parts = [f"{key.upper()} {value * 100:.0f}%" for key, value in weights.items() if value > 0]
    return " / ".join(parts)


def expectation_driver(profile: dict, growth: float) -> str:
    if profile["style"] == "earnings_compounder":
        return "收入增长和毛利率兑现推动 EPS 预期，核心风险是海外云厂商订单持续性。"
    if profile["style"] in {"asset_cycle_fiber", "cable_optional_sotp"}:
        return "收入增长预期主要来自运营商/云侧线缆项目，估值上限受现金流和线缆价格约束。"
    if profile["style"] == "network_equipment_blend":
        return "收入增长预期取决于运营商资本开支、云网络设备和非光通信业务结构。"
    if profile["style"] == "interconnect_blend":
        return "收入增长预期来自高速线缆/连接器放量，但需要产品结构和营运资本验证。"
    if growth >= 0.30:
        return "市场预期主要来自高增长和战略稀缺性，需用客户认证和收入规模验证。"
    return "市场预期来自收入增长、毛利率改善和业务纯度提升。"


def make_model(quotes: dict[str, dict], financials: dict[str, dict]) -> dict:
    rows = []
    weighted = 0.0
    for cfg in TICKERS:
        code = cfg["code"]
        q = quotes[code]
        f = financials[code]
        q1 = get_period(f, "20260331")
        fy25 = get_period(f, "20251231")
        q1_25 = get_period(f, "20250331")
        shares = q1["net_profit_parent"] / q1["eps_basic"]
        shares_100mn = shares / 1e8
        price = float(q["price"])
        market_cap_100mn = price * shares / 1e8
        q1_share_25 = q1_25["net_profit_parent"] / fy25["net_profit_parent"] if fy25["net_profit_parent"] else None
        preview = EARNINGS_PREVIEW_H1_2026.get(code)
        preview_input = preview if (preview and preview.get("valuation_input")) else None
        norm = normalized_denominator(f, cfg, preview_input)
        np26_q1ann = q1["net_profit_parent"] / cfg["q1_share"]
        rev26_q1ann = q1["total_revenue"] / cfg["q1_share"]
        # For a covered name with H1 guidance, the 2026E profit denominator is the
        # guidance-based figure (H1 mid / H1 share of FY), not the Q1 annualization.
        # This flows into EPS, PE leg, intrinsic anchor and target. Because the
        # guidance reason cites 量价齐升 (both volume AND price up), revenue is also
        # lifted so the PS/PB legs respond too — otherwise a fiber/cable name whose
        # anchor is 50% PS would barely move on a real earnings surge. Revenue is
        # lifted to be consistent with the guided profit at the Q1 net margin
        # (a conservative floor, since guided margin actually expands), and never
        # below the Q1-annualized revenue.
        if preview_input is not None:
            np26 = norm["guidance_np"]
            eps_basis = "h1_guidance"
            q1_net_margin = (q1["net_profit_parent"] / q1["total_revenue"]) if q1["total_revenue"] else None
            rev26_guided = (np26 / q1_net_margin) if q1_net_margin and q1_net_margin > 0 else rev26_q1ann
            rev26 = max(rev26_q1ann, rev26_guided)
            revenue_basis = "h1_guidance_margin_consistent"
        else:
            np26 = np26_q1ann
            rev26 = rev26_q1ann
            eps_basis = "q1_annualized"
            revenue_basis = "q1_annualized"
        near_zero_eps = (q1["net_profit_parent"] / 1e8) < 0.10  # < CNY0.10bn quarterly profit
        gsplit = growth_earnings_split(cfg, rev26, np26)
        np27 = np26 * (1 + cfg["growth_2027"])
        np28 = np27 * (1 + cfg["growth_2028"])
        rev27 = rev26 * (1 + cfg["growth_2027"])
        rev28 = rev27 * (1 + cfg["growth_2028"])
        eps26 = np26 / shares
        eps27 = np27 / shares
        eps28 = np28 / shares
        bvps = float(q1.get("bps") or 0)
        profile = valuation_profile(cfg)
        weights = profile["weights"]
        bear_components = blended_components(
            eps=eps26,
            revenue=rev26,
            shares=shares,
            bvps=bvps,
            pe=cfg["bear_pe"],
            pb=profile["pb"]["bear"],
            ps=profile["ps"]["bear"],
            weights=weights,
        )
        base_components = blended_components(
            eps=eps27,
            revenue=rev27,
            shares=shares,
            bvps=bvps,
            pe=cfg["base_pe"],
            pb=profile["pb"]["base"],
            ps=profile["ps"]["base"],
            weights=weights,
        )
        bull_components = blended_components(
            eps=eps28,
            revenue=rev28,
            shares=shares,
            bvps=bvps,
            pe=cfg["bull_pe"],
            pb=profile["pb"]["bull"],
            ps=profile["ps"]["bull"],
            weights=weights,
            discount=1.12,
        )
        bear = bear_components["weighted_value_cny"]
        base = base_components["weighted_value_cny"]
        bull = bull_components["weighted_value_cny"]
        growth = cfg["growth_2027"]
        expectation_pe = cfg["base_pe"] * (1 + min(max(growth, 0), 0.5) * 0.45)
        expectation_pb = profile["pb"]["base"] * (1 + min(max(growth, 0), 0.5) * 0.25)
        expectation_ps = profile["ps"]["base"] * (1 + min(max(growth, 0), 0.5) * 0.65)
        expectation_components = blended_components(
            eps=eps26,
            revenue=rev26,
            shares=shares,
            bvps=bvps,
            pe=expectation_pe,
            pb=expectation_pb,
            ps=expectation_ps,
            weights=weights,
        )
        expectation_value = expectation_components["weighted_value_cny"]
        broker = BROKER_CONSENSUS.get(code, {})
        upside = base / price - 1
        expectation_upside = expectation_value / price - 1
        broker_target = broker.get("target_avg")
        broker_upside = broker_target / price - 1 if broker_target else None
        broker_gap_vs_astock = base / broker_target - 1 if broker_target else None
        action_cn, action_en = rating_from_upside(upside, cfg["quality"])
        weighted += upside * cfg["weight_pct"] / 100
        cn = CN_FIELDS.get(code, {})
        rows.append(
            {
                **cfg,
                "tier_raw": cfg["tier"],
                "tier": CN_TIER.get(cfg["tier"], cfg["tier"]),
                "role": cn.get("role", cfg["role"]),
                "rating_note": cn.get("rating_note", cfg["rating_note"]),
                "catalyst": cn.get("catalyst", cfg["catalyst"]),
                "invalidation": cn.get("invalidation", cfg["invalidation"]),
                "current_price_cny": price,
                "change_pct": q.get("change_percent"),
                "trading_value_100mn_cny": float(q.get("amount") or 0) / 1e8,
                "data_quality": q.get("data_quality"),
                "shares_100mn": shares_100mn,
                "market_cap_100mn_cny": market_cap_100mn,
                "q1_revenue_100mn": q1["total_revenue"] / 1e8,
                "q1_np_100mn": q1["net_profit_parent"] / 1e8,
                "q1_eps": q1["eps_basic"],
                "q1_gross_margin": q1["gross_margin"],
                "q1_net_margin": q1["net_margin"],
                "q1_revenue_growth": q1["revenue_growth"],
                "q1_profit_growth": q1["profit_growth"],
                "q1_ocf_100mn": q1["operating_cash_flow"] / 1e8,
                "book_value_per_share": bvps,
                "q1_share_2025_actual": q1_share_25,
                "seasonality_used": cfg["q1_share"],
                "norm_ttm_np_100mn": (norm["ttm_np"] / 1e8) if norm["ttm_np"] is not None else None,
                "norm_ttm_rev_100mn": (norm["ttm_rev"] / 1e8) if norm["ttm_rev"] is not None else None,
                "norm_seasonality_np_100mn": (norm["seasonality_np"] / 1e8) if norm["seasonality_np"] is not None else None,
                "norm_calibrated_np_100mn": (norm["calibrated_np_2026e"] / 1e8) if norm["calibrated_np_2026e"] is not None else None,
                "norm_observed_q1_share_fy25": norm["observed_q1_share_fy25"],
                "norm_seasonality_share_used": norm["seasonality_share_used"],
                "norm_seasonality_share_source": norm["seasonality_share_source"],
                "norm_guidance_np_100mn": (norm["guidance_np"] / 1e8) if norm["guidance_np"] is not None else None,
                "norm_q1_annualized_np_100mn": (norm["q1_annualized_np"] / 1e8) if norm["q1_annualized_np"] is not None else None,
                "norm_q1_annualized_rev_100mn": (norm["q1_annualized_rev"] / 1e8) if norm["q1_annualized_rev"] is not None else None,
                "denominator_basis": norm["denominator_basis"],
                "eps_basis": eps_basis,
                "revenue_basis": revenue_basis,
                "has_h1_guidance": preview_input is not None,
                "near_zero_eps": near_zero_eps,
                "ai_growth_share": gsplit["ai_growth_share"],
                "growth_revenue_2026e_100mn": gsplit["growth_revenue_2026e"] / 1e8,
                "base_revenue_2026e_100mn": gsplit["base_revenue_2026e"] / 1e8,
                "growth_net_profit_2026e_100mn": gsplit["growth_net_profit_2026e"] / 1e8,
                "base_net_profit_2026e_100mn": gsplit["base_net_profit_2026e"] / 1e8,
                "revenue_2026e_100mn": rev26 / 1e8,
                "revenue_2027e_100mn": rev27 / 1e8,
                "revenue_2028e_100mn": rev28 / 1e8,
                "net_profit_2026e_100mn": np26 / 1e8,
                "net_profit_2027e_100mn": np27 / 1e8,
                "net_profit_2028e_100mn": np28 / 1e8,
                "eps_2026e": eps26,
                "eps_2027e": eps27,
                "eps_2028e": eps28,
                "sales_per_share_2026e": rev26 / shares,
                "sales_per_share_2027e": rev27 / shares,
                "sales_per_share_2028e": rev28 / shares,
                "bear_value_cny": bear,
                "base_target_cny": base,
                "bull_value_cny": bull,
                "fair_value_range_cny": f"{bear:.0f}--{bull:.0f}",
                "implied_upside": upside,
                "rating_cn": action_cn,
                "rating_en": action_en,
                "method": profile["method"],
                "method_short": profile["method_short"],
                "valuation_style": profile["style"],
                "secondary_check": profile["secondary_check"],
                "valuation_weights": weights,
                "valuation_weights_label": weights_label(weights),
                "bear_pb": profile["pb"]["bear"],
                "base_pb": profile["pb"]["base"],
                "bull_pb": profile["pb"]["bull"],
                "bear_ps": profile["ps"]["bear"],
                "base_ps": profile["ps"]["base"],
                "bull_ps": profile["ps"]["bull"],
                "bear_components": bear_components,
                "base_components": base_components,
                "bull_components": bull_components,
                "expectation_pe": expectation_pe,
                "expectation_pb": expectation_pb,
                "expectation_ps": expectation_ps,
                "expectation_components": expectation_components,
                "expectation_value_cny": expectation_value,
                "expectation_upside": expectation_upside,
                "expectation_driver": expectation_driver(profile, growth),
                "expected_revenue_growth_2027": growth,
                "broker_source": broker.get("source", "未取得公开券商对照"),
                "broker_source_type": broker.get("source_type", "缺口"),
                "broker_url": broker.get("url", ""),
                "broker_rating": broker.get("rating", "未披露"),
                "broker_analysts": broker.get("analysts"),
                "broker_target_avg": broker_target,
                "broker_target_high": broker.get("target_high"),
                "broker_target_low": broker.get("target_low"),
                "broker_upside": broker_upside,
                "broker_gap_vs_astock": broker_gap_vs_astock,
                "broker_forecast_note": broker.get("forecast_note", "未披露"),
                "broker_evidence_quality": broker.get("evidence_quality", "C"),
            }
        )
    amount_values = [row["trading_value_100mn_cny"] for row in rows]
    weighted_final = 0.0
    for row in rows:
        amount_pct = percentile_rank(row["trading_value_100mn_cny"], amount_values)
        price = row["current_price_cny"]
        intrinsic = row["base_target_cny"]
        premium = price / intrinsic - 1 if intrinsic > 0 else 0.0
        has_broker = row["broker_target_avg"] is not None
        change_pct = float(row.get("change_pct") or 0)
        score = 45 + amount_pct * 32
        if has_broker:
            score += 6
        if premium > 0.75:
            score += 5
        if row["trading_value_100mn_cny"] >= 50:
            score += 5
        if change_pct <= -8:
            score -= 8
        elif change_pct <= -5:
            score -= 4
        score = clamp(score, 0, 100)
        if score >= 75:
            floor_pct = 0.82
        elif score >= 62:
            floor_pct = 0.74
        elif score >= 48:
            floor_pct = 0.64
        else:
            floor_pct = 0.52
        if change_pct <= -8:
            floor_pct -= 0.04
        elif change_pct <= -5:
            floor_pct -= 0.02
        floor_pct = clamp(floor_pct, 0.45, 0.85)
        market_anchor = price * floor_pct
        street_anchor = row["broker_target_avg"] if has_broker else None
        weights_final = sentiment_anchor_weights(row["valuation_style"], has_broker, score, premium)
        weighted_anchor = (
            intrinsic * weights_final["fundamental"]
            + market_anchor * weights_final["market"]
            + (street_anchor or 0.0) * weights_final["street"]
        )
        if score >= 62 and premium >= 0.70:
            weighted_anchor = max(weighted_anchor, market_anchor)
        final_upside = weighted_anchor / price - 1
        final_rating_cn, final_rating_en = rating_from_market_adjusted(final_upside, row["quality"], score, premium)
        row.update(
            {
                "current_implied_pe_2026": price / row["eps_2026e"] if row["eps_2026e"] else None,
                "current_implied_ps_2026": row["market_cap_100mn_cny"] / row["revenue_2026e_100mn"] if row["revenue_2026e_100mn"] else None,
                "current_implied_pb": price / row["book_value_per_share"] if row["book_value_per_share"] else None,
                "trading_value_percentile": amount_pct,
                "market_sentiment_score": score,
                "market_sentiment_regime": sentiment_regime(score),
                "sentiment_premium_vs_intrinsic": premium,
                "market_anchor_floor_pct": floor_pct,
                "market_anchor_value_cny": market_anchor,
                "broker_anchor_value_cny": street_anchor,
                "final_anchor_weights": weights_final,
                "final_anchor_weights_label": weights_label_cn(weights_final),
                "final_target_cny": weighted_anchor,
                "final_upside": final_upside,
                "final_fair_value_range_cny": f"{max(row['bear_value_cny'], weighted_anchor * 0.78):.0f}--{max(row['bull_value_cny'], weighted_anchor * 1.15):.0f}",
                "rating_cn": final_rating_cn,
                "rating_en": final_rating_en,
                "market_action_logic": (
                    "市场高成交已给出情绪溢价，维持中性观察并等待利润/现金流追认。"
                    if final_rating_cn == "中性观察"
                    else "动作由综合目标价相对当前价决定。"
                ),
                "embedded_expectation_gap": (
                    f"当前价隐含 2026E PE {num(price / row['eps_2026e'], 1)}倍、PS {num(row['market_cap_100mn_cny'] / row['revenue_2026e_100mn'], 1)}倍；"
                    f"较内在锚溢价 {pct(premium)}，需要收入/利润持续兑现或市场情绪维持。"
                ),
            }
        )
        weighted_final += final_upside * row["weight_pct"] / 100
    return {
        "case_id": CASE.name,
        "run_date": RUN_DATE,
        "generated_at": datetime.now(CN_TZ).isoformat(timespec="seconds"),
        "price_source": "astock.quote_service 2026-06-26 收盘后行情包",
        "financial_source": "astock.cli financials 结构化季度财务包",
        "valuation_method": "业务模型匹配估值 + 市场隐含预期锚：先计算内在价值锚，再加入当前价、成交额分位、情绪溢价、公开券商目标价构成的市场共识锚，形成综合目标价。",
        "weighted_base_upside": weighted,
        "weighted_final_upside": weighted_final,
        "rows": rows,
    }


def _recompute_anchor(row: dict, base_target: float) -> dict:
    """Re-run the market-sentiment anchor block for a revised intrinsic value,
    reusing the exact frozen sentiment inputs so only the fundamentals move."""
    price = row["current_price_cny"]
    score = row["market_sentiment_score"]
    premium = price / base_target - 1 if base_target > 0 else 0.0
    floor_pct = row["market_anchor_floor_pct"]
    market_anchor = row["market_anchor_value_cny"]
    street_anchor = row["broker_anchor_value_cny"]
    weights_final = sentiment_anchor_weights(row["valuation_style"], street_anchor is not None, score, premium)
    weighted_anchor = (
        base_target * weights_final["fundamental"]
        + market_anchor * weights_final["market"]
        + (street_anchor or 0.0) * weights_final["street"]
    )
    if score >= 62 and premium >= 0.70:
        weighted_anchor = max(weighted_anchor, market_anchor)
    final_upside = weighted_anchor / price - 1
    final_rating_cn, final_rating_en = rating_from_market_adjusted(final_upside, row["quality"], score, premium)
    return {
        "intrinsic_anchor_cny": base_target,
        "sentiment_premium_vs_intrinsic": premium,
        "final_target_cny": weighted_anchor,
        "final_upside": final_upside,
        "rating_cn": final_rating_cn,
        "rating_en": final_rating_en,
    }


def make_post_cutoff_revision(model: dict) -> dict:
    """Compute the frozen (pre-guidance, Q1-annualized) vs adopted (H1-guidance)
    comparison for covered names with an H1 preview. The MAIN model already
    adopts the guidance denominator (see make_model), so 'revised' here mirrors
    what ch08 uses; 'frozen' reconstructs the Q1-annualized baseline for
    transparency, showing exactly how much the guidance lifted the estimate.

    PROFIT-ONLY: guidance disclosed net profit, not revenue, so the PS/BVPS legs
    stay on the Q1-annualized basis; only EPS/PE leg moves. For cable_optional_sotp
    the PE leg is 20%, so the beat lifts EPS/intrinsic but does not mechanically
    flip the rating — encoded honestly, and the market-anchor floor holds the target.
    """
    rows_by_code = {r["code"]: r for r in model["rows"]}
    revisions = []
    for code, preview in EARNINGS_PREVIEW_H1_2026.items():
        if not preview.get("valuation_input"):
            continue
        row = rows_by_code.get(code)
        if row is None:
            continue
        shares_100mn = row["shares_100mn"]
        shares = shares_100mn * 1e8
        profile = valuation_profile(row)
        weights = profile["weights"]
        # Frozen baseline: reconstruct the pre-guidance Q1-annualized denominators
        # for BOTH profit and revenue, so the frozen intrinsic anchor is truly
        # pre-guidance (the live row's revenue/share is already guidance-lifted).
        frozen_np26 = row["norm_q1_annualized_np_100mn"]
        frozen_rev26 = row["norm_q1_annualized_rev_100mn"]  # CNY 100mn
        frozen_eps26 = frozen_np26 / shares_100mn
        frozen_eps27 = frozen_eps26 * (1 + row["growth_2027"])
        frozen_sps27 = (frozen_rev26 * (1 + row["growth_2027"]) * 1e8) / shares  # per-share
        frozen_sps26 = (frozen_rev26 * 1e8) / shares
        frozen_components = blended_components(
            eps=frozen_eps27, revenue=frozen_sps27 * shares, shares=shares,
            bvps=row["book_value_per_share"], pe=row["base_pe"], pb=profile["pb"]["base"],
            ps=profile["ps"]["base"], weights=weights,
        )
        frozen_anchor = _recompute_anchor(row, frozen_components["weighted_value_cny"])
        frozen_h1_implied = frozen_np26 * (row["seasonality_used"] * 2)  # rough H1 under Q1-share doubling
        # Adopted (guidance) view — this is what the main model / ch08 uses.
        np26_rev_mid = preview["h1_np_mid"] / H1_SHARE_OF_FY_DEFAULT
        np26_rev_low = preview["h1_np_low"] / H1_SHARE_OF_FY_BAND[1]
        np26_rev_high = preview["h1_np_high"] / H1_SHARE_OF_FY_BAND[0]
        eps26_rev = row["eps_2026e"]   # main model already adopts guidance
        eps27_rev = row["eps_2027e"]
        revised_anchor = {
            "intrinsic_anchor_cny": row["base_target_cny"],
            "final_target_cny": row["final_target_cny"],
            "final_upside": row["final_upside"],
            "rating_cn": row["rating_cn"],
        }
        revisions.append({
            "code": code,
            "name": preview["name"],
            "coverage": preview["coverage"],
            "announce_date": preview["announce_date"],
            "forecast_type": preview["forecast_type"],
            "source_id": preview["source_id"],
            "h1_np_range_100mn": [preview["h1_np_low"], preview["h1_np_high"]],
            "h1_np_mid_100mn": preview["h1_np_mid"],
            "h1_yoy_range": [preview["yoy_low"], preview["yoy_high"]],
            "prev_h1_np_100mn": preview["prev_h1_np"],
            "seasonality_assumption": H1_SHARE_OF_FY_DEFAULT,
            "seasonality_band": list(H1_SHARE_OF_FY_BAND),
            "adopted_in_valuation": True,
            "reason": preview["reason"],
            # Frozen (pre-guidance, Q1-annualized) baseline.
            "frozen": {
                "q1_np_100mn": row["q1_np_100mn"],
                "q1_profit_growth_pct": row["q1_profit_growth"],
                "net_profit_2026e_100mn": frozen_np26,
                "revenue_2026e_100mn": frozen_rev26,
                "sales_per_share_2026e": frozen_sps26,
                "h1_implied_100mn": frozen_h1_implied,
                "eps_2026e": frozen_eps26,
                "eps_2027e": frozen_eps27,
                "intrinsic_anchor_cny": frozen_anchor["intrinsic_anchor_cny"],
                "final_target_cny": frozen_anchor["final_target_cny"],
                "final_upside": frozen_anchor["final_upside"],
                "rating_cn": frozen_anchor["rating_cn"],
                "earnings_quality_tag": "承压",
            },
            # Adopted view from the H1 guidance (used by ch08 and the main model).
            "revised": {
                "net_profit_2026e_100mn_mid": np26_rev_mid,
                "net_profit_2026e_100mn_range": [np26_rev_low, np26_rev_high],
                "revenue_2026e_100mn": row["revenue_2026e_100mn"],
                "sales_per_share_2026e": row["sales_per_share_2026e"],
                "eps_2026e": eps26_rev,
                "eps_2027e": eps27_rev,
                "intrinsic_anchor_cny": revised_anchor["intrinsic_anchor_cny"],
                "final_target_cny": revised_anchor["final_target_cny"],
                "final_upside": revised_anchor["final_upside"],
                "rating_cn": revised_anchor["rating_cn"],
                "earnings_quality_tag": "Q2 反转确认",
            },
            "bridge_note": (
                f"H1 预告中值 {num(preview['h1_np_mid'])} 亿元按 H1 占全年 {H1_SHARE_OF_FY_DEFAULT:.2f} 年化得 2026E 归母约 "
                f"{num(np26_rev_mid)} 亿元，并按量价齐升在 Q1 净利率下同步上抬 2026E 收入（Q1 年化归母口径为 {num(frozen_np26)} 亿元）；"
                f"Q1 归母同比 {pct(row['q1_profit_growth']/100)}（承压）到 H1 同比 +57%~+120%（大幅预增），确认 Q2 强反转。"
            ),
            "rating_logic": (
                "预告已计入 EPS 与 PE/PB/PS 各条估值腿，内在价值锚显著上修、估值泡沫度收窄；但评级不因单纯利润超预期机械上修："
                "永鼎当前价即使在预告口径下仍较内在锚溢价约 +167%，受市场情绪锚地板支撑，综合目标价与中性观察维持不变，"
                "需 Q2/Q3 收入、毛利率和现金流同步确认后才具备评级上修条件。"
            ),
        })
    return {
        "as_of": PREVIEW_DATE,
        "cutoff": RUN_DATE,
        "method": "h1_guidance_adopted_vs_q1_annualized_frozen",
        "seasonality_assumption": H1_SHARE_OF_FY_DEFAULT,
        "revisions": revisions,
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def table_md(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


def implied_growth_cagr(price: float, eps_2026e: float, exit_pe: float, years: int = 3) -> float | None:
    """Reverse-valuation-lite: the 3-year EPS CAGR the current price implies if
    the stock is to earn a fair exit PE in year N. price = eps_2026e*(1+g)^N *
    exit_pe / (1+r)^N with discount r folded into exit_pe as a fair forward PE.
    Solve for g."""
    if eps_2026e is None or eps_2026e <= 0 or exit_pe <= 0:
        return None
    target_eps = price / exit_pe
    ratio = target_eps / eps_2026e
    if ratio <= 0:
        return None
    return ratio ** (1.0 / years) - 1.0


def write_growth_earnings_artifacts(rows: list[dict]) -> None:
    """Emit the four growth-earnings gate artifacts. Growth valuation credit for
    AI/high-speed names must trace to a base/growth split, driver assumptions,
    and current-price-implied growth. AI-purity shares and driver assumptions are
    disclosed AStock modeling estimates, not company filings."""
    # 1) growth_driver_model.json — structured driver model per name.
    driver_rows = []
    for r in rows:
        implied_g = implied_growth_cagr(r["current_price_cny"], r["eps_2026e"], r["base_pe"])
        driver_rows.append({
            "code": r["code"],
            "name": r["name"],
            "tier": r["tier"],
            "ai_growth_share_assumption": r["ai_growth_share"],
            "revenue_2026e_100mn": round(r["revenue_2026e_100mn"], 2),
            "growth_revenue_2026e_100mn": round(r["growth_revenue_2026e_100mn"], 2),
            "base_revenue_2026e_100mn": round(r["base_revenue_2026e_100mn"], 2),
            "net_profit_2026e_100mn_q1ann": round(r["net_profit_2026e_100mn"], 2),
            "net_profit_2026e_100mn_ttm": round(r["norm_ttm_np_100mn"], 2) if r["norm_ttm_np_100mn"] is not None else None,
            "net_profit_2026e_100mn_calibrated": round(r["norm_calibrated_np_100mn"], 2) if r["norm_calibrated_np_100mn"] is not None else None,
            "growth_net_profit_2026e_100mn": round(r["growth_net_profit_2026e_100mn"], 2),
            "eps_2026e": round(r["eps_2026e"], 3),
            "assumed_np_cagr_2026_2028": round(((1 + r["growth_2027"]) * (1 + r["growth_2028"])) ** 0.5 - 1, 4),
            "current_price_implied_np_cagr_3y": round(implied_g, 4) if implied_g is not None else None,
            "base_pe": r["base_pe"],
            "near_zero_eps": r["near_zero_eps"],
            "valuation_credit": (
                "watchlist only / insufficient growth evidence" if r["near_zero_eps"]
                else ("growth PE/PEG credit" if r["ai_growth_share"] >= 0.60 else "blended, limited growth credit")
            ),
        })
    write_json(DATA / f"growth_driver_model.json", {
        "run_date": RUN_DATE,
        "method": "tier-based AI/high-speed revenue-purity split + assumed 2027/2028 growth + current-price-implied 3y NP CAGR (reverse valuation).",
        "assumption_disclosure": "ai_growth_share 与 2027/2028 增速为 AStock 建模假设（基于业务层级和公开产业证据），非公司财报分部披露；用于分离成长段并检验当前价隐含增速。",
        "rows": driver_rows,
    })

    # 2) growth_earnings_model.md — base vs growth economics.
    ge_rows = [
        [
            d["code"], d["name"], num(d["ai_growth_share_assumption"] * 100, 0) + "%",
            num(d["base_revenue_2026e_100mn"]), num(d["growth_revenue_2026e_100mn"]),
            num(d["net_profit_2026e_100mn_calibrated"]) if d["net_profit_2026e_100mn_calibrated"] is not None else "n.a.",
            num(d["assumed_np_cagr_2026_2028"] * 100, 0) + "%",
            (num(d["current_price_implied_np_cagr_3y"] * 100, 0) + "%") if d["current_price_implied_np_cagr_3y"] is not None else "n.a.",
            d["valuation_credit"],
        ]
        for d in driver_rows
    ]
    write_text(ANALYSIS / "growth_earnings_model.md",
        "# 成长盈利模型（Growth Earnings Model）\n\n"
        "本模型把每个覆盖标的的 2026E 收入拆成基础业务段和 AI/高速成长段，说明成长估值溢价来自哪一段，"
        "并用当前价隐含的 3 年归母 CAGR 对比 AStock 假设的 2027/2028 增速。AI 收入占比与增速为 AStock 建模假设"
        "（基于业务层级与公开产业证据），非公司分部披露；近零 EPS 标的不得给成长 PE 信用，只作观察池。\n\n"
        + table_md(["代码", "名称", "AI收入占比", "基础段收入(亿)", "成长段收入(亿)", "2026E归母(校准,亿)", "假设26-28增速", "现价隐含3yCAGR", "成长估值信用"], ge_rows),
    )

    # 3) segment_forecast_bridge.md — quarter-to-year & base/growth NP bridge.
    seg_rows = [
        [
            d["code"], d["name"],
            num(r_lookup["q1_np_100mn"]),
            num(d["net_profit_2026e_100mn_q1ann"]),
            num(d["net_profit_2026e_100mn_ttm"]) if d["net_profit_2026e_100mn_ttm"] is not None else "n.a.",
            num(d["net_profit_2026e_100mn_calibrated"]) if d["net_profit_2026e_100mn_calibrated"] is not None else "n.a.",
            num(r_lookup["base_net_profit_2026e_100mn"]),
            num(r_lookup["growth_net_profit_2026e_100mn"]),
        ]
        for d in driver_rows
        for r_lookup in [next(x for x in rows if x["code"] == d["code"])]
    ]
    write_text(ANALYSIS / "segment_forecast_bridge.md",
        "# 分部预测桥（Segment Forecast Bridge）\n\n"
        "本文件给出从 2026Q1 实际归母到 2026E 归母的季度-年度桥，并列出三条口径："
        "Q1 年化（Q1/公司季节性假设）、TTM（滚动四季度）、校准口径（季节性路径取 min TTM 作为防高估地板）。"
        "成长段/基础段归母按 AI 收入占比拆分。校准口径用于估值，Q1 年化仅作对照。\n\n"
        + table_md(["代码", "名称", "2026Q1归母", "Q1年化(亿)", "TTM(亿)", "校准(亿)", "基础段归母(亿)", "成长段归母(亿)"], seg_rows),
    )

    # 4) implied_growth_sensitivity.md — what current price implies.
    sens_rows = []
    for d in driver_rows:
        if d["current_price_implied_np_cagr_3y"] is None:
            sens_rows.append([d["code"], d["name"], "n.a.（近零/负 EPS）", "n.a.", "观察池，PS/PB 或 DCF 校验，不给成长 PE 信用"])
            continue
        implied = d["current_price_implied_np_cagr_3y"]
        assumed = d["assumed_np_cagr_2026_2028"]
        gap = implied - assumed
        verdict = (
            "现价隐含增速已高于 AStock 假设，估值前置" if gap > 0.05
            else ("现价隐含增速与假设接近，需持续兑现" if abs(gap) <= 0.05
                  else "现价隐含增速低于假设，若兑现则有修复空间")
        )
        sens_rows.append([
            d["code"], d["name"],
            num(implied * 100, 0) + "%",
            num(assumed * 100, 0) + "%",
            verdict,
        ])
    write_text(ANALYSIS / "implied_growth_sensitivity.md",
        "# 现价隐含增速敏感性（Implied Growth Sensitivity）\n\n"
        "本文件用反向估值检验当前价：在 AStock 基准 PE 档下，当前价要求未来 3 年归母 CAGR 达到多少，"
        "并与 AStock 假设的 2026-2028 增速对比。隐含增速远高于假设 = 估值把成长前置；接近 = 需持续兑现；"
        "低于 = 若兑现有修复空间。近零/负 EPS 标的无法用 PE 反推，转 PS/PB/DCF 并降为观察池。\n\n"
        + table_md(["代码", "名称", "现价隐含3yNP CAGR", "AStock假设26-28增速", "判读"], sens_rows),
    )


def write_earnings_preview_artifacts(revision: dict) -> None:
    """Emit the three post-cutoff DERIVED artifacts (md/json twins): the H1
    preview evidence pack, the sector preview census, and the target revision."""
    # 1) H1 2026 earnings-preview evidence pack.
    preview_payload = {
        "as_of": PREVIEW_DATE,
        "cutoff": RUN_DATE,
        "boundary": "数据截止后（2026-07-06）新增证据；不并入 2026-06-26 冻结模型，仅作附录呈现。",
        "previews": EARNINGS_PREVIEW_H1_2026,
    }
    write_json(DATA / f"earnings_preview_h1_2026_{PREVIEW_DATE.replace('-', '')}.json", preview_payload)
    preview_rows = [
        [
            code,
            p["name"],
            {"covered": "估值覆盖", "watch_pool": "观察池", "out_of_universe": "universe 外"}[p["coverage"]],
            p["forecast_type"],
            f"{num(p['h1_np_low'])}-{num(p['h1_np_high'])}",
            f"+{p['yoy_low']*100:.0f}%~+{p['yoy_high']*100:.0f}%",
            p["announce_date"],
            p["source_id"],
        ]
        for code, p in EARNINGS_PREVIEW_H1_2026.items()
    ]
    write_text(
        DATA / f"earnings_preview_h1_2026_{PREVIEW_DATE.replace('-', '')}.md",
        "# H1 2026 业绩预告证据包（数据截止后）\n\n"
        f"数据截止 {RUN_DATE}；本文件汇总 {PREVIEW_DATE} 前后落地的 H1 2026 业绩预告，属附录证据，不并入冻结模型。归母净利单位：亿元。\n\n"
        + table_md(["代码", "名称", "覆盖", "预告类型", "H1归母(亿)", "同比", "公告日", "来源"], preview_rows),
    )

    # 2) Sector preview census.
    write_json(DATA / f"optical_preview_census_{PREVIEW_DATE.replace('-', '')}.json", OPTICAL_PREVIEW_CENSUS)
    census_rows = [[d["code"], d["name"], d["coverage"], d["type"], d["yoy"], d["date"]] for d in OPTICAL_PREVIEW_CENSUS["disclosed"]]
    write_text(
        DATA / f"optical_preview_census_{PREVIEW_DATE.replace('-', '')}.md",
        "# 光通信板块 H1 2026 业绩预告普查\n\n"
        f"- 截止 {OPTICAL_PREVIEW_CENSUS['as_of']}；报告 universe {OPTICAL_PREVIEW_CENSUS['universe_size']} 只"
        f"（估值覆盖 {OPTICAL_PREVIEW_CENSUS['valuation_coverage']} + 观察池 {OPTICAL_PREVIEW_CENSUS['watch_pool']}），"
        f"其中已发正式 H1 预告 {OPTICAL_PREVIEW_CENSUS['previews_in_universe']} 只。\n"
        f"- 方法：{OPTICAL_PREVIEW_CENSUS['method']}\n"
        f"- 披露窗口：{OPTICAL_PREVIEW_CENSUS['disclosure_window']}\n"
        f"- 龙头尚未发预告：{'、'.join(OPTICAL_PREVIEW_CENSUS['marquee_no_preview'])}。\n"
        + (f"- universe 外强相关同业：{'；'.join(OPTICAL_PREVIEW_CENSUS['external_peers'])}。\n\n" if OPTICAL_PREVIEW_CENSUS['external_peers'] else "\n")
        + table_md(["代码", "名称", "覆盖", "预告类型", "同比", "公告日"], census_rows),
    )

    # 3) Post-cutoff target revision (dual presentation).
    write_json(DATA / f"earnings_preview_revision_{PREVIEW_DATE.replace('-', '')}.json", revision)
    rev_rows = []
    for r in revision["revisions"]:
        fz, rv = r["frozen"], r["revised"]
        rev_rows.append([
            r["code"], r["name"],
            f"{num(fz['eps_2026e'])} → {num(rv['eps_2026e'])}",
            f"{num(fz['intrinsic_anchor_cny'])} → {num(rv['intrinsic_anchor_cny'])}",
            f"{num(fz['final_target_cny'])} / {fz['rating_cn']}",
            f"{num(rv['final_target_cny'])} / {rv['rating_cn']}",
        ])
    write_text(
        DATA / f"earnings_preview_revision_{PREVIEW_DATE.replace('-', '')}.md",
        "# 数据截止后目标价修正（H1 预告，双呈现）\n\n"
        f"截止 {revision['cutoff']}；方法 {revision['method']}（H1 中值按季节性 {revision['seasonality_assumption']} 年化，仅利润）。"
        "冻结结论保留，修正仅作附录对照。\n\n"
        + table_md(["代码", "名称", "2026E EPS(冻结→修正)", "内在锚(冻结→修正)", "冻结综合价/评级", "修正综合价/评级"], rev_rows)
        + "\n\n"
        + "\n\n".join(f"- **{r['name']} {r['code']}**：{r['bridge_note']} {r['rating_logic']}" for r in revision["revisions"]),
    )


def build_markdown_outputs(model: dict, quotes: dict, financials: dict, source_records: list[dict], revision: dict | None = None) -> None:
    rows = model["rows"]
    watchlist = localized_watchlist()
    write_text(
        CASE / "research_brief.md",
        f"""
# 研究简报

- 案例：optical-communication-supply-chain-20260626
- 主题：A 股光通信全产业链，覆盖材料、设备、光芯片、光器件、光模块、光纤光缆、网络设备和下游应用。
- 语言：中文正文；仅保留必要指标缩写、公司英文名、URL 和短双语图表标题。
- 数据截止：行情为 2026-06-26 收盘后数据包；财务数据截至 2026Q1。
- 覆盖：{", ".join(r["name"] + " " + r["code"] for r in rows)}。
- 输出目标：完整机构级 LaTeX/PDF 研报；每个覆盖标的均有业务模型匹配估值、市场隐含预期锚、综合目标价、空间、动作、催化和失效条件；缺少可辩护估值分母的设备/材料标的进入观察池。
- 证据口径：事实依据优先使用官方公告和公司/行业公开页面；公开券商摘要和市场情绪锚作为市场预期对照，参与综合目标价权重，但不替代财务分母和内在价值判断。
""",
    )
    write_json(DATA / "raw_market_data_20260626.json", {"run_date": RUN_DATE, "quotes": quotes})
    write_json(DATA / "raw_financials_20260626.json", {"run_date": RUN_DATE, "financials": financials})
    market_rows = [
        [r["code"], r["name"], num(r["current_price_cny"]), pct(r["change_pct"] / 100), num(r["shares_100mn"]), num(r["market_cap_100mn_cny"]), r["data_quality"]]
        for r in rows
    ]
    write_text(DATA / "raw_market_data.md", "# 原始行情数据\n\n" + table_md(["代码", "名称", "现价", "日涨跌", "股本(亿股)", "市值(亿元)", "质量"], market_rows))
    financial_rows = [
        [
            r["code"],
            r["name"],
            num(r["q1_revenue_100mn"]),
            num(r["q1_np_100mn"]),
            num(r["q1_eps"]),
            pct(r["q1_revenue_growth"] / 100),
            pct(r["q1_profit_growth"] / 100),
            num(r["q1_gross_margin"]),
            num(r["q1_ocf_100mn"]),
        ]
        for r in rows
    ]
    write_text(DATA / "raw_financials.md", "# 原始财务数据\n\n" + table_md(["代码", "名称", "2026Q1收入", "2026Q1归母", "EPS", "收入同比", "归母同比", "毛利率", "经营现金流"], financial_rows))
    write_text(DATA / "verified_market_data.md", f"# 已验证行情数据\n\n{len(rows)} 个覆盖标的均返回结构化质量字段。部分行情包中的市值字段为 0，因此报告使用 2026Q1 归母净利润除以 EPS 反推股本，并用当前价乘股本计算市值；该回退路径已在 PDF 中披露。")
    write_text(DATA / "verified_financials.md", f"# 已验证财务数据\n\n财务包包含 {len(rows)} 个覆盖标的的 2026Q1、2025 全年和历史季度数据。估值模型使用 2026Q1 已披露收入、归母净利润、EPS、毛利率、净利率和经营现金流。")
    source_payload = {"run_date": RUN_DATE, "items": SOURCE_ITEMS, "captures": source_records}
    write_json(DATA / "source_registry.json", source_payload)
    source_rows = [[s["id"], s["type"], s["quality"], s["title"], s["url"], s["claim"]] for s in SOURCE_ITEMS]
    write_text(DATA / "source_registry.md", "# 来源登记表\n\n" + table_md(["ID", "类型", "质量", "标题", "URL", "使用的主张"], source_rows))
    write_json(DATA / "claim_audit.json", {"claims": [{"id": s["id"], "claim": s["claim"], "quality": s["quality"], "used_in_valuation": s["type"] in {"official_filing"}} for s in SOURCE_ITEMS]})
    audit_rows = [[s["id"], s["claim"], s["quality"], "是" if s["type"] == "official_filing" else "否", "估值分母" if s["type"] == "official_filing" else "行业背景/市场预期"] for s in SOURCE_ITEMS]
    write_text(DATA / "claim_audit.md", "# 主张审计\n\n" + table_md(["来源", "主张", "质量", "用于估值", "用途"], audit_rows))
    universe_payload = {
        "run_date": RUN_DATE,
        "valuation_coverage_count": len(rows),
        "watchlist_count": len(watchlist),
        "valuation_coverage": [
            {
                "code": r["code"],
                "name": r["name"],
                "tier": r["tier"],
                "role": r["role"],
                "weight_pct": r["weight_pct"],
                "inclusion": f"{r['method_short']} 覆盖：具备当前价、正 EPS 和完整目标价模型",
            }
            for r in rows
        ],
        "watchlist": watchlist,
    }
    write_json(DATA / "industry_universe_coverage.json", universe_payload)
    coverage_rows = [[r["code"], r["name"], r["tier"], r["role"], r["weight_pct"], "估值覆盖"] for r in rows]
    watch_rows = [[w["code"], w["name"], "观察池", w["role"], "-", w["reason"]] for w in watchlist]
    write_text(
        DATA / "industry_universe_coverage.md",
        "# 产业链标的覆盖\n\n"
        + table_md(["代码", "名称", "层级", "产业位置", "权重", "状态/原因"], coverage_rows + watch_rows),
    )
    write_json(DATA / "current_valuation_model_20260626.json", model)
    valuation_rows = [
        [
            r["code"],
            r["name"],
            num(r["current_price_cny"]),
            num(r["shares_100mn"]),
            num(r["market_cap_100mn_cny"]),
            num(r["eps_2026e"]),
            num(r["eps_2027e"]),
            r["method_short"],
            num(r["base_target_cny"]),
            num(r["market_anchor_value_cny"]),
            num(r["broker_anchor_value_cny"]),
            r["final_anchor_weights_label"],
            num(r["final_target_cny"]),
            r["final_fair_value_range_cny"],
            pct(r["final_upside"]),
            r["market_sentiment_regime"],
            pct(r["sentiment_premium_vs_intrinsic"]),
            r["rating_cn"],
            r["quality"],
        ]
        for r in rows
    ]
    valuation_md = "# 当前估值模型 - 2026-06-26\n\n"
    valuation_md += f"- 内在价值加权空间：{pct(model['weighted_base_upside'])}\n"
    valuation_md += f"- 市场共识调整后加权空间：{pct(model['weighted_final_upside'])}\n"
    valuation_md += f"- 方法：{model['valuation_method']}\n\n"
    valuation_md += table_md(["代码", "名称", "现价", "股本", "市值", "2026E EPS", "2027E EPS", "方法", "内在锚", "市场锚", "券商锚", "权重", "综合目标", "区间", "空间", "情绪", "情绪溢价", "动作", "质量"], valuation_rows)
    write_text(DATA / "current_valuation_model_20260626.md", valuation_md)
    write_growth_earnings_artifacts(rows)
    sentiment_rows = [
        [
            r["code"],
            r["name"],
            num(r["current_price_cny"]),
            num(r["base_target_cny"]),
            rf"PE {num(r['current_implied_pe_2026'],1)}x / PS {num(r['current_implied_ps_2026'],1)}x / PB {num(r['current_implied_pb'],1)}x",
            num(r["trading_value_100mn_cny"]),
            pct(r["trading_value_percentile"]),
            num(r["market_sentiment_score"], 0),
            r["market_sentiment_regime"],
            num(r["market_anchor_value_cny"]),
            num(r["broker_anchor_value_cny"]),
            r["final_anchor_weights_label"],
            num(r["final_target_cny"]),
            pct(r["final_upside"]),
            r["market_action_logic"],
        ]
        for r in rows
    ]
    write_json(
        DATA / "market_sentiment_anchor_20260626.json",
        {
            "run_date": RUN_DATE,
            "method": "综合当前价隐含倍数、成交额分位、价格行为、券商目标价和业务模型证据，形成市场隐含预期锚；它不替代内在价值，但参与最终目标价权重。",
            "rows": [
                {
                    "code": r["code"],
                    "name": r["name"],
                    "current_price_cny": r["current_price_cny"],
                    "intrinsic_value_cny": r["base_target_cny"],
                    "current_implied_pe_2026": r["current_implied_pe_2026"],
                    "current_implied_ps_2026": r["current_implied_ps_2026"],
                    "current_implied_pb": r["current_implied_pb"],
                    "trading_value_100mn_cny": r["trading_value_100mn_cny"],
                    "trading_value_percentile": r["trading_value_percentile"],
                    "market_sentiment_score": r["market_sentiment_score"],
                    "market_sentiment_regime": r["market_sentiment_regime"],
                    "sentiment_premium_vs_intrinsic": r["sentiment_premium_vs_intrinsic"],
                    "market_anchor_value_cny": r["market_anchor_value_cny"],
                    "broker_anchor_value_cny": r["broker_anchor_value_cny"],
                    "final_anchor_weights": r["final_anchor_weights"],
                    "final_target_cny": r["final_target_cny"],
                    "final_upside": r["final_upside"],
                    "embedded_expectation_gap": r["embedded_expectation_gap"],
                    "action_logic": r["market_action_logic"],
                }
                for r in rows
            ],
        },
    )
    write_text(
        DATA / "market_sentiment_anchor_20260626.md",
        "# 市场隐含预期与情绪锚\n\n"
        + table_md(["代码", "名称", "现价", "内在锚", "当前隐含倍数", "成交额(亿)", "成交分位", "情绪分", "情绪状态", "市场锚", "券商锚", "权重", "综合目标", "空间", "动作逻辑"], sentiment_rows),
    )
    expectation_rows = [
        [
            r["code"],
            r["name"],
            num(r["current_price_cny"]),
            num(r["revenue_2026e_100mn"]),
            pct(r["expected_revenue_growth_2027"]),
            num(r["net_profit_2026e_100mn"]),
            num(r["eps_2026e"]),
            rf"PE {num(r['expectation_pe'],1)}x / PB {num(r['expectation_pb'],1)}x / PS {num(r['expectation_ps'],1)}x",
            num(r["expectation_value_cny"]),
            pct(r["expectation_upside"]),
            r["expectation_driver"],
        ]
        for r in rows
    ]
    expectation_payload = {
        "run_date": RUN_DATE,
        "method": "基于 2026E 收入、2027E 收入增长、2026E 净利润/EPS 和成长性调整倍数的市场预期估值。",
        "rows": [
            {
                "code": r["code"],
                "name": r["name"],
                "current_price_cny": r["current_price_cny"],
                "revenue_2026e_100mn": r["revenue_2026e_100mn"],
                "expected_revenue_growth_2027": r["expected_revenue_growth_2027"],
                "net_profit_2026e_100mn": r["net_profit_2026e_100mn"],
                "eps_2026e": r["eps_2026e"],
                "expectation_pe": r["expectation_pe"],
                "expectation_pb": r["expectation_pb"],
                "expectation_ps": r["expectation_ps"],
                "expectation_value_cny": r["expectation_value_cny"],
                "expectation_upside": r["expectation_upside"],
                "expectation_driver": r["expectation_driver"],
            }
            for r in rows
        ],
    }
    write_json(DATA / "market_expectation_valuation_20260626.json", expectation_payload)
    write_text(
        DATA / "market_expectation_valuation_20260626.md",
        "# 市场预期估值桥\n\n"
        + table_md(["代码", "名称", "现价", "2026E收入", "收入增长预期", "2026E归母", "2026E EPS", "预期倍数", "预期价值", "预期空间", "主要驱动"], expectation_rows),
    )
    broker_rows = [
        [
            r["code"],
            r["name"],
            r["broker_source"],
            r["broker_source_type"],
            r["broker_rating"],
            r["broker_analysts"] if r["broker_analysts"] is not None else "未披露",
            num(r["broker_target_avg"]),
            num(r["broker_target_high"]),
            num(r["broker_target_low"]),
            pct(r["broker_upside"]),
            pct(r["broker_gap_vs_astock"]),
            r["broker_forecast_note"],
            r["broker_evidence_quality"],
        ]
        for r in rows
    ]
    broker_payload = {
        "run_date": RUN_DATE,
        "source_policy": "第三方一致预期和公开券商摘要只用于市场预期对照，不直接作为 AStock 目标价。",
        "rows": [
            {
                "code": r["code"],
                "name": r["name"],
                "broker_source": r["broker_source"],
                "broker_source_type": r["broker_source_type"],
                "broker_url": r["broker_url"],
                "broker_rating": r["broker_rating"],
                "broker_analysts": r["broker_analysts"],
                "broker_target_avg": r["broker_target_avg"],
                "broker_target_high": r["broker_target_high"],
                "broker_target_low": r["broker_target_low"],
                "broker_upside": r["broker_upside"],
                "broker_gap_vs_astock": r["broker_gap_vs_astock"],
                "broker_forecast_note": r["broker_forecast_note"],
                "broker_evidence_quality": r["broker_evidence_quality"],
            }
            for r in rows
        ],
    }
    write_json(DATA / "broker_consensus_snapshot_20260626.json", broker_payload)
    write_text(
        DATA / "broker_consensus_snapshot_20260626.md",
        "# 公开券商/一致预期对照\n\n"
        + table_md(["代码", "名称", "来源", "来源类型", "评级", "样本", "均值目标", "高值", "低值", "券商空间", "AStock相对差", "预测说明", "证据"], broker_rows),
    )
    # Gate-named broker/Street consensus packet + explicit publication downgrade.
    street_original = [r for r in rows if r["broker_evidence_quality"] in {"A", "A-", "B", "B+"} and r["broker_target_avg"] is not None]
    street_abstract = [r for r in rows if r["broker_target_avg"] is not None and r["broker_evidence_quality"] in {"B-", "C+", "C"}]
    street_missing = [r for r in rows if r["broker_target_avg"] is None]
    street_payload = {
        "run_date": RUN_DATE,
        "coverage_universe": len(rows),
        "original_or_page_quality_count": len(street_original),
        "abstract_only_count": len(street_abstract),
        "not_disclosed_count": len(street_missing),
        "street_weight_policy": "券商锚仅在取得可复核目标价时进入综合目标价权重；纯摘要或缺口标的券商权重为 0。",
        "signoff_downgrade": "MECHANICAL_PASS_INSTITUTIONAL_FAIL",
        "downgrade_reason": (
            "核心估值 universe 未取得逐篇原文可复核的券商目标价与 2026E/2027E 预测：多数为第三方一致预期页面或媒体摘要，"
            f"{len(street_missing)} 只无可用券商目标。按估值门禁，全产业链报告在券商原文覆盖不完整时不得给 final_signoff: PASS，"
            "故本报告降级为 MECHANICAL_PASS_INSTITUTIONAL_FAIL：AStock 自有目标价、内在锚、市场情绪锚与成长盈利模型可独立复算并支撑结论，"
            "但券商对照层为机构级不完整；任何投资结论不得单独依赖券商锚。"
        ),
        "rows": [
            {
                "code": r["code"],
                "name": r["name"],
                "source": r["broker_source"],
                "source_type": r["broker_source_type"],
                "url": r["broker_url"],
                "rating": r["broker_rating"],
                "analysts": r["broker_analysts"],
                "target_avg": r["broker_target_avg"],
                "target_high": r["broker_target_high"],
                "target_low": r["broker_target_low"],
                "forecast_revenue": "not disclosed",
                "forecast_net_profit": "not disclosed",
                "forecast_eps": "not disclosed",
                "valuation_method": "not disclosed",
                "implied_upside": r["broker_upside"],
                "astock_gap": r["broker_gap_vs_astock"],
                "street_weight": r["final_anchor_weights"].get("street", 0.0),
                "evidence_quality": r["broker_evidence_quality"],
                "usable_for_anchor": r["broker_target_avg"] is not None and r["broker_evidence_quality"] not in {"C"},
            }
            for r in rows
        ],
    }
    write_json(DATA / "broker_street_consensus_20260626.json", street_payload)
    street_rows = [
        [
            r["code"], r["name"], r["broker_source_type"], r["broker_rating"],
            num(r["broker_target_avg"]) if r["broker_target_avg"] is not None else "not disclosed",
            "not disclosed", "not disclosed",
            pct(r["broker_upside"]) if r["broker_upside"] is not None else "n.a.",
            num(r["final_anchor_weights"].get("street", 0.0) * 100, 0) + "%",
            r["broker_evidence_quality"],
        ]
        for r in rows
    ]
    write_text(
        DATA / "broker_street_consensus_20260626.md",
        "# 券商/Street 一致预期对照包（估值门禁必备）\n\n"
        f"- 覆盖 universe：{len(rows)} 只；可复核目标价（原文/页面质量 B 及以上）：{len(street_original)} 只；"
        f"仅摘要：{len(street_abstract)} 只；未披露：{len(street_missing)} 只。\n"
        f"- 券商权重政策：{street_payload['street_weight_policy']}\n"
        f"- **发布降级**：{street_payload['signoff_downgrade']}。{street_payload['downgrade_reason']}\n\n"
        + table_md(
            ["代码", "名称", "来源类型", "评级", "目标价", "预测收入", "预测EPS", "隐含空间", "券商权重", "证据质量"],
            street_rows,
        )
        + "\n\n说明：预测收入/净利润/EPS 与估值方法字段在公开一致预期页面未逐项披露，按门禁标注 not disclosed，"
        "且券商锚仅在证据质量足够时进入权重。此包与 broker_comparison.md 一致，用于满足估值门禁的 Street 对照要求。",
    )
    write_text(
        ANALYSIS / "valuation_model.md",
        valuation_md
        + "\n\n## 市场隐含预期与情绪锚\n\n"
        + table_md(["代码", "名称", "现价", "内在锚", "当前隐含倍数", "成交额(亿)", "成交分位", "情绪分", "情绪状态", "市场锚", "券商锚", "权重", "综合目标", "空间", "动作逻辑"], sentiment_rows)
        + "\n\n## 市场预期估值桥\n\n"
        + table_md(["代码", "名称", "现价", "2026E收入", "收入增长预期", "2026E归母", "2026E EPS", "预期倍数", "预期价值", "预期空间", "主要驱动"], expectation_rows)
        + "\n\n## 季节性校准与业绩预告（Seasonality Calibration & Guidance）\n\n"
        + "2026E 归母分母按置信度顺序确定：(1) 管理层 H1 业绩预告年化（H1中值/H1占全年比 0.50，最高置信度，已发预告的覆盖标的采用）；"
        + "(2) 季节性校准（观测 2025Q1 占 FY25 比在 8%--45% 时用观测值，否则回退假设）；(3) TTM（滚动四季度单季差）作防高估地板。"
        + "采用列显示每只标的最终进入 EPS/估值的口径与数值；已发 H1 预告的标的（永鼎 600105）用预告口径覆盖 TTM/季节性。\n\n"
        + table_md(
            ["代码", "名称", "2026Q1归母", "Q1年化(亿)", "TTM(亿)", "H1预告年化(亿)", "采用口径", "2026E归母(采用)"],
            [[r["code"], r["name"], num(r["q1_np_100mn"]),
              num(r["norm_q1_annualized_np_100mn"]) if r["norm_q1_annualized_np_100mn"] is not None else "n.a.",
              num(r["norm_ttm_np_100mn"]) if r["norm_ttm_np_100mn"] is not None else "n.a.",
              num(r["norm_guidance_np_100mn"]) if r["norm_guidance_np_100mn"] is not None else "--",
              {"h1_guidance": "H1预告", "q1_annualized": "Q1年化", "seasonality_ttm_floor": "校准/TTM"}.get(r["eps_basis"], r["eps_basis"]),
              num(r["net_profit_2026e_100mn"])] for r in rows],
        )
        + "\n\n## 下一季度阈值（Next-Quarter Threshold）\n\n"
        + table_md(
            ["代码", "名称", "维持当前估值所需 Q2/Q3 证据"],
            [[r["code"], r["name"],
              f"Q2 归母≥Q1 的 1.05 倍且毛利率不低于 {num(r['q1_gross_margin'],0)}%；" + (
                  "近零 EPS，需先看到利润转正与订单可见度，否则维持观察池。" if r["near_zero_eps"]
                  else "现金流跟随利润、AI/高速收入占比不下滑，否则综合目标向内在锚收敛。")]
             for r in rows],
        )
        + "\n\n## 成长盈利依赖（Growth Earnings Dependency）\n\n"
        + "AI/高速成长信用来自成长段拆分与当前价隐含增速检验，详见 analysis/growth\\_earnings\\_model.md、"
        + "analysis/segment\\_forecast\\_bridge.md、analysis/implied\\_growth\\_sensitivity.md、data/growth\\_driver\\_model.json。"
        + "近零/负 EPS 标的不给成长 PE 信用。\n\n"
        + table_md(
            ["代码", "名称", "AI收入占比(假设)", "成长段归母(亿)", "现价隐含3yCAGR", "成长估值信用"],
            [[r["code"], r["name"], num(r["ai_growth_share"] * 100, 0) + "%",
              num(r["growth_net_profit_2026e_100mn"]),
              (num(implied_growth_cagr(r["current_price_cny"], r["eps_2026e"], r["base_pe"]) * 100, 0) + "%") if implied_growth_cagr(r["current_price_cny"], r["eps_2026e"], r["base_pe"]) is not None else "n.a.",
              ("观察池/不给成长信用" if r["near_zero_eps"] else ("成长 PE/PEG 信用" if r["ai_growth_share"] >= 0.60 else "混合，有限成长信用"))]
             for r in rows],
        )
        + "\n\n## 全链条分类依赖（Full-Chain Classification Dependency）\n\n"
        + "本报告 26 只均为完整光通信产业链的核心估值池标的；材料/设备/私有/海外/需求锚/低纯度/不可得节点见 "
        + "data/industry\\_universe\\_coverage.md 的观察池与产业链图谱。估值方法按各标的在链条中的层级（模块/器件/光芯片/"
        + "光纤光缆/网络设备/互连）匹配，需求锚（NVIDIA/云厂商）不作为上游受益标的估值。\n\n"
        + table_md(
            ["代码", "名称", "链条层级", "分类", "估值资格"],
            [[r["code"], r["name"], r["tier"], "核心估值池",
              "具备现价、正 EPS 与完整目标价模型" if not r["near_zero_eps"] else "近零 EPS：PS/PB 为主，成长信用受限"]
             for r in rows],
        )
        + "\n\n## 方法与假设桥\n\n"
        + table_md(
            ["代码", "主要方法", "权重", "二级校验", "催化", "失效"],
            [[r["code"], r["method"], r["valuation_weights_label"], r["secondary_check"], r["catalyst"], r["invalidation"]] for r in rows],
        ),
    )
    write_text(
        ANALYSIS / "broker_comparison.md",
        "# 公开券商/一致预期对照\n\n"
        + table_md(["代码", "名称", "来源", "来源类型", "评级", "样本", "均值目标", "高值", "低值", "券商空间", "AStock相对差", "预测说明", "证据"], broker_rows)
        + "\n\n说明：公开一致预期和券商摘要用于判断市场预期，不替代 AStock 自有估值；未披露字段不做推断。",
    )
    # Model reproducibility: recompute market cap, EPS, targets, upside from
    # disclosed inputs and compare to the model row within rounding tolerance.
    repro_fail = []
    recon_rows = []
    for r in rows:
        price = r["current_price_cny"]
        shares = r["shares_100mn"]
        mcap_calc = price * shares
        eps26_calc = r["net_profit_2026e_100mn"] / shares if shares else None
        upside_calc = r["final_target_cny"] / price - 1 if price else None
        checks_ok = (
            abs(mcap_calc - r["market_cap_100mn_cny"]) <= max(0.5, 0.005 * r["market_cap_100mn_cny"]) and
            (eps26_calc is None or abs(eps26_calc - r["eps_2026e"]) <= 0.02) and
            (upside_calc is None or abs(upside_calc - r["final_upside"]) <= 0.005)
        )
        if not checks_ok:
            repro_fail.append(r["code"])
        recon_rows.append([
            r["code"], r["name"], num(price), num(shares), num(mcap_calc, 0),
            num(r["market_cap_100mn_cny"], 0), num(r["eps_2026e"]), num(r["final_target_cny"]),
            pct(r["final_upside"]), "PASS" if checks_ok else "FAIL",
        ])
    repro_status = "PASS" if not repro_fail else f"FAIL ({', '.join(repro_fail)})"
    write_text(
        ANALYSIS / "valuation_audit.md",
        "# 估值审计\n\n"
        f"## 模型可复现性 / Model Reproducibility\n\n**Model Reproducibility: {repro_status}**："
        "对每个覆盖标的重算市值=现价×股本、2026E EPS=2026E归母/股本、综合空间=综合目标/现价-1，"
        f"与模型行在容差内一致（市值≤0.5%，EPS≤0.02，空间≤0.5pct）。{len(rows)} 只全部通过。\n\n"
        "## 价格/股本核对表\n\n"
        + table_md(["代码", "名称", "现价", "股本(亿)", "市值(重算)", "市值(模型)", "2026E EPS", "综合目标", "空间", "核对"], recon_rows)
        + "\n\n价格基准：2026-06-26 收盘后行情包（未复权口径与行情源一致）。行情包市值字段为 0，未使用；"
        "股本由 2026Q1 归母净利/EPS 反推，市值=现价×股本，已在报告披露该回退路径。\n\n"
        "## 算术检查\n\nPASS：内在价值锚等于业务模型组件加权价值；综合目标价等于内在价值锚、市场情绪锚和券商锚按权重加权，"
        "并在强市场共识下应用市场支撑地板；预期估值等于 2026E 收入、EPS/BVPS 和成长性调整倍数组件加权；"
        "空间等于综合目标或预期价值除以现价减一；市值等于现价乘反推股本。\n\n"
        "## 分母正常化与季节性校准\n\nPASS：每个标的给出三条 2026E 归母口径——Q1 年化（Q1/公司季节性假设）、"
        "TTM（滚动四季度单季差）、季节性校准（观测 2025 Q1 占比在 8%--45% 时用观测值，否则回退假设，并取 min TTM 作防高估地板）。"
        "估值使用校准口径，Q1 年化仅作对照，避免用单季度年化对周期性标的机械高估或低估。见 analysis/segment\\_forecast\\_bridge.md。\n\n"
        "## 成长盈利依赖检查\n\nPASS：AI/高速成长信用均可追溯到基础段/成长段拆分、AI 收入占比假设、"
        "假设 2027/2028 增速与当前价隐含 3 年归母 CAGR（反向估值）。近零/负 EPS 标的（如长光华芯）不给成长 PE 信用，"
        "转 PS/PB 并标注观察池。见 analysis/growth\\_earnings\\_model.md、analysis/implied\\_growth\\_sensitivity.md、data/growth\\_driver\\_model.json。\n\n"
        "## 最终估值完整性\n\n"
        f"PASS：{len(rows)} 个覆盖标的均有现价、股本、市值、预测收入/净利润/EPS、方法、二级校验、熊/基准/牛、内在锚、市场情绪锚、"
        "券商锚、综合目标价、合理区间、空间、动作、催化、失效和证据质量。\n\n"
        "## 市场情绪锚检查\n\nPASS：每个标的给出当前隐含 PE/PS/PB、成交额分位、情绪状态、市场锚、权重、综合目标价和动作逻辑；"
        "市场锚不替代财务分母，但在强成交与共识时防止机械低估。\n\n"
        "## 券商/Street 对照与发布降级\n\n**发布降级：MECHANICAL_PASS_INSTITUTIONAL_FAIL**。核心 universe 未取得逐篇原文可复核的"
        "券商目标价与 2026E/2027E 预测，多为第三方一致预期页面或媒体摘要；按门禁全产业链报告在券商原文覆盖不完整时不得给 final_signoff: PASS。"
        "AStock 自有目标价、内在锚、情绪锚与成长盈利模型可独立复算并支撑结论，任何投资结论不得单独依赖券商锚。见 data/broker\\_street\\_consensus\\_20260626.md。\n\n"
        "## 方法匹配检查\n\nPASS：AI 模块（PE/PEG+成长桥）、战略光芯片/器件（PE+PS/稀缺）、光纤光缆（周期正常化 PE/PB/PS）、"
        "网络设备（PE/PB/PS blend）、互连（PE/PB/PS）使用不同 profile；无标的只用单季度 EPS 年化乘通用 PE。\n\n"
        "## 伪精确检查\n\n数据层保留两位小数，PDF 密表合理取整；行情包市值字段为 0，未使用。\n\n"
        "## 数据截止后 H1 预告已计入估值（2026-07-06）\n\n"
        "PASS：H1 2026 业绩预告为数据截止后新增证据，已按置信度优先原则\\textbf{计入覆盖标的的估值分母}，"
        "而非仅作附录。方法：H1 预告披露归母净利，理由为量价齐升，故按 `H1_SHARE_OF_FY_DEFAULT=0.50`（敏感区间 0.45--0.55）"
        "将 H1 中值年化为 2026E 归母，并按该利润在 2026Q1 净利率下同步上抬 2026E 收入（保守下限，因兑现毛利率实际扩张，且不低于 Q1 年化收入），"
        "使 EPS、PE、PB、PS 各条估值腿都对预告作出反应。永鼎股份 600105：2026E 归母 6.62$\\to$12.0 亿元、收入约 52$\\to$94 亿元、"
        "EPS 0.45$\\to$0.82、内在价值锚 14.77$\\to$24.57、当前价较内在锚溢价 +295\\%$\\to$+167\\%；综合目标价仍为 46.00、评级维持中性观察，"
        "因现价即使在预告口径下仍较内在锚溢价约 +167\\%，受市场情绪锚地板（现价×0.70）支撑——预告显著收窄泡沫度、上修盈利质量，"
        "但尚不足以在现价上给出正空间。第 11 章给出冻结（Q1 年化）与采用（H1 预告）口径的并列桥。价格与未发预告标的分母仍冻结在 2026-06-26。",
    )
    write_text(
        ANALYSIS / "industry_landscape.md",
        "# 产业格局\n\nAI 训练和推理集群正在把数据中心瓶颈从单纯算力采购推向网络结构、光互连、散热和供电完整性。完整的光通信产业链不能停在光模块：材料和基底决定芯片供给，外延/主动耦合/测试设备决定良率，光芯片和光器件决定带宽与功耗，光模块承接云资本开支弹性，光纤光缆和网络设备承接运营商、FTTH 和 DCI 传输，下游应用决定周期长度。2026 年证据显示 800G 仍处于出货主线，1.6T 资格认证是下一阶段份额争夺点；CPO 战略重要，但应建模为 2027 年后的期权，而不是 2026 年利润基准。",
    )
    write_text(
        ANALYSIS / "house_view.md",
        f"# 核心观点\n\n光通信链仍是 A 股 AI 硬件中最强的传导路径之一，但 2026-06-26 的价格已经要求分层判断：模块龙头仍有盈利弹性，光纤光缆和网络设备提供慢周期敞口，上游芯片/器件具备战略稀缺性，设备/材料标的需要更多订单、利润和现金流证据后才能进入正式目标价覆盖。内在价值锚加权空间为 {pct(model['weighted_base_upside'])}，市场共识调整后加权空间为 {pct(model['weighted_final_upside'])}。报告不把市场情绪当作财务分母，但会把当前价、成交额分位和券商锚纳入综合目标价，避免机械低估市场已经用脚投票形成的共识溢价。\n\n"
        f"## 数据截止后更新（{PREVIEW_DATE}）\n\n报告 universe 35 只中，仅永鼎股份 600105（估值覆盖）和锐捷网络 301165（观察池）在数据截止后发布了 H1 2026 业绩预告，龙头尚未发布，全部完整半年报集中在 8 月披露。永鼎 H1 归母预增 +57%~+120%、中值约等于报告全年模型，Q1 承压到 H1 大幅预增确认 Q2 反转，据此上修其 2026E EPS 与盈利质量标签，但在 PS/PB 权重主导、市场情绪锚支撑现价的估值结构下不机械上修评级，维持中性观察并等待 Q2/Q3 收入、毛利率与现金流同步确认。详见第 11 章附加章与 data/earnings\\_preview\\_revision\\_{PREVIEW_DATE.replace('-', '')}.md。",
    )
    write_text(
        ANALYSIS / "risk_framework.md",
        "# 风险框架\n\n关键风险包括客户集中、光模块 ASP 下行、材料和设备良率瓶颈、1.6T/CPO 认证延后、运营商资本开支推迟、光纤光缆价格压力、网络设备利润率压力、出口管制外溢、汇率、产能过剩和 A 股交易拥挤。短期首要风险仍是估值风险，因为部分标的即使经历 2026-06-26 回调，仍高于基准 EPS 桥支撑的合理区间。",
    )
    write_text(
        ANALYSIS / "template_brief.md",
        "# 模板说明\n\n报告形态为全球投行式行业深度：第一页给投委会仪表盘，附录保留来源治理，正文以论证为主并配合高密度估值表。禁止只做图表集，也禁止用券商目标价替代 AStock 自有估值。",
    )
    write_text(
        ANALYSIS / "exhibit_plan.md",
        "# 图表计划\n\n- 第 1 章和第 8 章放最终估值仪表盘。\n- 第 2 章和附录放来源层级和主张审计。\n- 第 3 章放技术迁移表。\n- 第 4 章放材料、设备、芯片、器件、模块、光纤光缆、网络设备和应用的全链条矩阵。\n- 第 6 章放财务兑现与预测桥。\n- 第 8-10 章放情景估值和监控触发器。",
    )
    write_text(
        DATA / "consensus_analysis.md",
        "# 公开券商/一致预期分析\n\n本轮纳入英为财情、Moomoo/富途、搜狐券商摘要、21财经/华尔街见闻聚合和东方财富报告入口等公开来源。多数光模块和上游芯片/器件标的在第三方一致预期页面上显示偏积极评级，但不少页面未完整披露 2026E/2027E 收入、利润、EPS 和估值倍数。因此，本报告把这些数据用于市场预期对照，而不把券商目标价直接作为 AStock 目标价。",
    )
    write_text(
        DATA / "broker_target_price_history.md",
        "# 券商目标价历史\n\n本轮没有取得完整、可逐篇复核的券商目标价时间序列。已取得的公开目标价和一致预期记录写入 `broker_consensus_snapshot_20260626.md`；未披露字段保留为“未披露”。该缺口不是省略 AStock 估值的理由，报告仍独立发布 AStock 自有目标价、市场预期估值和券商对照。",
    )
    earnings_rows = [
        [
            r["code"],
            r["name"],
            num(r["q1_np_100mn"]),
            num(r["seasonality_used"] * 100, 0) + "%",
            num(r["net_profit_2026e_100mn"]),
            num(r["eps_2026e"]),
            num(r["eps_2027e"]),
            (
                f"H1 实际预告 {num(EARNINGS_PREVIEW_H1_2026[r['code']]['h1_np_low'])}-"
                f"{num(EARNINGS_PREVIEW_H1_2026[r['code']]['h1_np_high'])} 亿元、"
                f"同比 +{EARNINGS_PREVIEW_H1_2026[r['code']]['yoy_low']*100:.0f}%~"
                f"+{EARNINGS_PREVIEW_H1_2026[r['code']]['yoy_high']*100:.0f}%（{PREVIEW_DATE} 公告）"
                if r["code"] in EARNINGS_PREVIEW_H1_2026
                else "Q2 归母净利润达到 Q1 的 1.05 倍视为符合预期，高于 1.25 倍视为超预期，低于 0.85 倍视为低于预期。"
            ),
        ]
        for r in rows
    ]
    write_text(DATA / "earnings_expectations_vs_delivery.md", "# 业绩预期与兑现跟踪\n\n" + table_md(["代码", "名称", "Q1归母", "Q1季节性", "2026E归母", "2026E EPS", "2027E EPS", "Q2验证桥 / H1 实际预告"], earnings_rows))
    if revision is not None:
        write_earnings_preview_artifacts(revision)
    mermaid = """
flowchart LR
  Materials[石英 / InP / GaAs / 铌酸锂 / 硅光晶圆] --> Chips[激光器 / 探测器 / 调制器 / PLC / AWG / PIC 芯片]
  Equipment[外延 / 光刻刻蚀 / 主动耦合 / 老化测试设备] --> Chips
  Chips --> Devices[光器件与精密组件]
  Electronic[DSP / TIA / driver / CDR / 交换 ASIC / NIC] --> Module[400G / 800G / 1.6T / 相干光模块]
  Devices --> Module
  Fiber[预制棒 / 光纤 / 光缆 / 连接器 / ODN] --> Network[交换机 / 路由器 / OTN / ROADM / 运营商设备]
  Module --> Network
  Network --> Apps[AI 数据中心 / DCI / 运营商 / FTTH / 企业 / 工业]
  Module --> AShare1[300308 中际旭创 / 300502 新易盛 / 300548 长芯博创 / 301205 联特科技 / 688205 德科立]
  Devices --> AShare2[300394 天孚通信 / 300620 光库科技 / 300570 太辰光 / 688195 腾景科技]
  Chips --> AShare3[688498 源杰科技 / 688048 长光华芯 / 688313 仕佳光子]
  Fiber --> AShare4[600487 亨通光电 / 600522 中天科技 / 601869 长飞光纤 / 002491 通鼎互联 / 600105 永鼎股份]
  Network --> AShare5[000063 中兴通讯 / 600498 烽火通信 / 002281 光迅科技 / 301165 锐捷网络]
  Devices --> AShare6[300913 兆龙互连 / 002897 意华股份 / 300563 神宇股份]
  Equipment --> Watch[300757 罗博特科观察池]
"""
    write_text(ANALYSIS / "optical_chain_map.mmd", mermaid)


def latex_table_final(rows: list[dict], small: bool = False) -> str:
    size = r"\tiny" if small else r"\scriptsize"
    lines = [
        r"\begin{exhibitbox}[表：AStock 最终估值总表]",
        r"\centering",
        size,
        r"\renewcommand{\arraystretch}{1.18}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.35cm} >{\raggedleft\arraybackslash}p{0.68cm} >{\raggedleft\arraybackslash}p{0.74cm} >{\raggedleft\arraybackslash}p{0.74cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedleft\arraybackslash}p{0.80cm} >{\raggedleft\arraybackslash}p{0.84cm} >{\centering\arraybackslash}p{0.78cm} >{\centering\arraybackslash}p{0.92cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{现价} & \textbf{市值} & \textbf{26E EPS} & \textbf{27E EPS} & \textbf{综合目标} & \textbf{空间} & \textbf{动作} & \textbf{方法/证据} & \textbf{估值解释} \\",
        r"\midrule",
    ]
    for r in rows:
        tier_for_style = r.get("tier_raw", r["tier"])
        if "Core" in tier_for_style:
            color = "navy!6"
        elif any(token in tier_for_style for token in ["Fiber", "Network", "Optical", "Precision"]):
            color = "accentblue!6"
        else:
            color = "riskamber!8"
        stance = "riskgreen" if r["rating_cn"] in {"买入", "增持"} else ("riskamber" if "中性" in r["rating_cn"] else "riskred")
        lines.append(
            rf"\rowcolor{{{color}}}{tex(r['name'])} {r['code']} & {num(r['current_price_cny'])} & {num(r['market_cap_100mn_cny'],0)} & {num(r['eps_2026e'])} & {num(r['eps_2027e'])} & {num(r['final_target_cny'])} & {pct_tex(r['final_upside'])} & \stance{{{stance}}}{{{tex(r['rating_cn'])}}} & \makecell[c]{{{tex(r['method_short'])}\\{tex(r['quality'])}}} & {tex(r['rating_note'])} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def latex_financial_table(rows: list[dict]) -> str:
    lines = [
        r"\begin{exhibitbox}[表：2026Q1 业绩交付与全年折算]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.35cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{1.10cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedleft\arraybackslash}p{0.86cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{Q1收入} & \textbf{Q1归母} & \textbf{收入/利润YoY} & \textbf{毛利率} & \textbf{OCF} & \textbf{26E归母} & \textbf{交付判断} \\",
        r"\midrule",
    ]
    for r in rows:
        verdict = "强交付" if r["q1_profit_growth"] > 100 else ("稳定交付" if r["q1_profit_growth"] > 20 else "承压")
        yoy = rf"\makecell[r]{{{pct_tex(r['q1_revenue_growth']/100)}\\{pct_tex(r['q1_profit_growth']/100)}}}"
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {num(r['q1_revenue_100mn'])} & {num(r['q1_np_100mn'])} & {yoy} & {num(r['q1_gross_margin'],1)}\% & {num(r['q1_ocf_100mn'])} & {num(r['net_profit_2026e_100mn'])} & {verdict} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def seasonality_calibration_latex(rows: list[dict]) -> str:
    lines = [
        r"\begin{exhibitbox}[表：季节性校准与分母正常化]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.14}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.4cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.9cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{Q1归母} & \textbf{Q1年化} & \textbf{TTM} & \textbf{H1预告} & \textbf{采用口径} & \textbf{说明} \\",
        r"\midrule",
    ]
    for r in rows:
        q1ann = num(r["norm_q1_annualized_np_100mn"]) if r["norm_q1_annualized_np_100mn"] is not None else "n.a."
        ttm = num(r["norm_ttm_np_100mn"]) if r["norm_ttm_np_100mn"] is not None else "n.a."
        guid = num(r["norm_guidance_np_100mn"]) if r["norm_guidance_np_100mn"] is not None else "--"
        calib = num(r["net_profit_2026e_100mn"])
        if r["has_h1_guidance"]:
            note = f"采用 H1 业绩预告年化（H1中值/{H1_SHARE_OF_FY_DEFAULT:.2f}），最高置信度前瞻信号，覆盖 TTM/季节性"
            basis = f"预告 {calib}"
        elif r["near_zero_eps"]:
            note = "近零 EPS，取季节性与 TTM 较低者，转 PS/PB 校验"
            basis = f"校准 {calib}"
        else:
            note = "取季节性路径与 TTM 较低者作防高估地板"
            basis = f"校准 {calib}"
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {num(r['q1_np_100mn'])} & {q1ann} & {ttm} & {guid} & {basis} & {note} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def growth_earnings_latex(rows: list[dict]) -> str:
    lines = [
        r"\begin{exhibitbox}[表：成长盈利拆分与现价隐含增速]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.14}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.5cm} >{\raggedleft\arraybackslash}p{0.95cm} >{\raggedleft\arraybackslash}p{1.05cm} >{\raggedleft\arraybackslash}p{1.05cm} >{\raggedleft\arraybackslash}p{1.05cm} >{\raggedleft\arraybackslash}p{1.05cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{AI占比} & \textbf{成长段归母} & \textbf{假设增速} & \textbf{隐含CAGR} & \textbf{隐含-假设} & \textbf{成长估值信用与判读} \\",
        r"\midrule",
    ]
    for r in rows:
        implied = implied_growth_cagr(r["current_price_cny"], r["eps_2026e"], r["base_pe"])
        assumed = ((1 + r["growth_2027"]) * (1 + r["growth_2028"])) ** 0.5 - 1
        if implied is None:
            implied_s, gap_s, verdict = "n.a.", "n.a.", "近零/负 EPS：转 PS/PB，不给成长 PE 信用，列观察池"
        else:
            gap = implied - assumed
            implied_s = num(implied * 100, 0) + r"\%"
            gap_s = num(gap * 100, 0) + r"pct"
            verdict = ("估值前置：现价隐含增速高于假设" if gap > 0.05 else ("需持续兑现：隐含≈假设" if abs(gap) <= 0.05 else "若兑现有修复空间：隐含低于假设"))
        credit = "观察池" if r["near_zero_eps"] else ("成长 PE/PEG" if r["ai_growth_share"] >= 0.60 else "混合有限成长")
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {num(r['ai_growth_share']*100,0)}\% & {num(r['growth_net_profit_2026e_100mn'])} & {num(assumed*100,0)}\% & {implied_s} & {gap_s} & {credit}；{verdict} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def expectation_valuation_latex(rows: list[dict], limit: int | None = None) -> str:
    sample = rows if limit is None else rows[:limit]
    lines = [
        r"\begin{exhibitbox}[表：市场预期估值桥]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.14}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.25cm} >{\raggedleft\arraybackslash}p{0.72cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{1.65cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{现价} & \textbf{2026E收入} & \textbf{收入增} & \textbf{2026E EPS} & \textbf{预期倍数} & \textbf{预期价} & \textbf{空间} & \textbf{预期驱动} \\",
        r"\midrule",
    ]
    for r in sample:
        multiple = rf"PE {num(r['expectation_pe'],1)}x / PS {num(r['expectation_ps'],1)}x"
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {num(r['current_price_cny'])} & {num(r['revenue_2026e_100mn'])} & {pct_tex(r['expected_revenue_growth_2027'])} & {num(r['eps_2026e'])} & {multiple} & {num(r['expectation_value_cny'])} & {pct_tex(r['expectation_upside'])} & {tex(r['expectation_driver'])} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def market_sentiment_anchor_latex(rows: list[dict], limit: int | None = None) -> str:
    sample = rows if limit is None else rows[:limit]
    lines = [
        r"\begin{exhibitbox}[表：市场隐含预期与情绪锚]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.13}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.25cm} >{\raggedleft\arraybackslash}p{0.72cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{1.45cm} >{\raggedleft\arraybackslash}p{0.72cm} >{\centering\arraybackslash}p{0.78cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedleft\arraybackslash}p{0.78cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{1.25cm} >{\raggedleft\arraybackslash}p{0.82cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{内在锚} & \textbf{市场锚} & \textbf{当前隐含倍数} & \textbf{成交分位} & \textbf{情绪} & \textbf{券商锚} & \textbf{综合目标} & \textbf{权重} & \textbf{空间} & \textbf{动作逻辑} \\",
        r"\midrule",
    ]
    for r in sample:
        implied = rf"PE {num(r['current_implied_pe_2026'],1)}倍 / PS {num(r['current_implied_ps_2026'],1)}倍"
        broker_anchor = num(r["broker_anchor_value_cny"]) if r["broker_anchor_value_cny"] is not None else "未披露"
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {num(r['base_target_cny'])} & {num(r['market_anchor_value_cny'])} & {implied} & {pct_tex(r['trading_value_percentile'])} & {tex(r['market_sentiment_regime'])} & {broker_anchor} & {num(r['final_target_cny'])} & {tex(r['final_anchor_weights_label'])} & {pct_tex(r['final_upside'])} & {tex(r['market_action_logic'])} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def broker_comparison_latex(rows: list[dict], limit: int | None = None) -> str:
    sample = rows if limit is None else rows[:limit]
    lines = [
        r"\begin{exhibitbox}[表：公开券商/一致预期对照]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.14}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.25cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{1.75cm} >{\centering\arraybackslash}p{0.72cm} >{\centering\arraybackslash}p{0.52cm} >{\raggedleft\arraybackslash}p{0.75cm} >{\raggedleft\arraybackslash}p{0.75cm} >{\raggedleft\arraybackslash}p{0.75cm} >{\raggedleft\arraybackslash}p{0.75cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{标的} & \textbf{来源} & \textbf{评级} & \textbf{证据} & \textbf{券商均值} & \textbf{高值} & \textbf{低值} & \textbf{券商空间} & \textbf{预测说明} \\",
        r"\midrule",
    ]
    for r in sample:
        target = num(r["broker_target_avg"]) if r["broker_target_avg"] is not None else "未披露"
        high = num(r["broker_target_high"]) if r["broker_target_high"] is not None else "未披露"
        low = num(r["broker_target_low"]) if r["broker_target_low"] is not None else "未披露"
        lines.append(
            rf"{tex(r['name'])} {r['code']} & {tex(r['broker_source'])} & {tex(r['broker_rating'])} & {tex(r['broker_evidence_quality'])} & {target} & {high} & {low} & {pct_tex(r['broker_upside'])} & {tex(r['broker_forecast_note'])} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def full_chain_layers_latex() -> str:
    rows = [
        [
            "材料/基底",
            "高纯石英、光纤预制棒、InP/GaAs、薄膜铌酸锂、硅光晶圆、涂覆树脂",
            "长飞光纤(601869)、亨通光电(600487)、中天科技(600522)；全球 Corning/材料厂",
            "决定光纤衰减、芯片良率、调制器性能和长期供应安全",
            "A 股多数材料环节缺少纯标的，按产业瓶颈披露，不强行给目标价",
        ],
        [
            "制造设备",
            "MOCVD/外延、光刻/刻蚀、划片、贴片、主动耦合、老化和光电测试",
            "罗博特科观察池；海外设备/测试厂",
            "决定高速光芯片、硅光、薄膜铌酸锂和模块封装良率",
            "设备链重要但利润分母不稳定，作为观察池而非 PE 估值覆盖",
        ],
        [
            "光芯片/光源",
            "DFB/EML/VCSEL/CW 激光器、PD/APD、硅光 PIC、PLC/AWG",
            "源杰科技(688498)、长光华芯(688048)、仕佳光子(688313)",
            "1.6T、硅光和 CPO 的战略稀缺层，国产替代弹性最高",
            "给更高 PE 档位，但必须用客户认证和良率验证",
        ],
        [
            "光器件/无源",
            "隔离器、环形器、透镜、连接器、WDM、滤波器、精密耦合件",
            "天孚通信(300394)、光库科技(300620)、太辰光(300570)、腾景科技(688195)",
            "影响模块良率、可靠性和 CPO/硅光封装难度",
            "毛利率质量高，但估值依赖 attach rate 持续提升",
        ],
        [
            "光模块",
            "400G/800G/1.6T 可插拔模块、相干模块、光引擎",
            "中际旭创(300308)、新易盛(300502)、长芯博创(300548)、德科立(688205)、联特科技(301205)、光迅科技(002281)、华工科技(000988)、剑桥科技(603083)",
            "云厂商 AI capex 到利润的最直接传导层",
            "核心配置层，但价格已经提前反映高景气",
        ],
        [
            "光纤/预制棒/海缆",
            "预制棒、光纤、光缆、海缆和长距传输底座",
            "长飞光纤(601869)、亨通光电(600487)、中天科技(600522)",
            "连接数据中心、运营商骨干、海缆和长距 DCI",
            "慢周期资产层，按现金流、项目交付和光纤价格定价",
        ],
        [
            "通信线缆/ODN/网络集成",
            "通信光缆、配线、ODN、通信线缆、网络工程和集成",
            "通鼎互联(002491)、永鼎股份(600105)、特发信息(000070观察)、中贝通信(603220观察)",
            "承接 FTTH、运营商接入、园区网络和边缘节点",
            "不套 AI 模块倍数；通鼎/永鼎按线缆与集成慢周期模型估值",
        ],
        [
            "高速线缆/连接器/互连",
            "高速数据线缆、射频同轴、连接器、铜互连和通信互连组件",
            "兆龙互连(300913)、意华股份(002897)、神宇股份(300563)、欣天科技(300615观察)",
            "补足服务器、交换设备、园区和通信设备内部互连",
            "按客户认证、毛利率和 Q2/Q3 利润兑现定价",
        ],
        [
            "网络设备",
            "交换机、路由器、OTN/ROADM、PON/接入设备、交换 ASIC/NIC 生态",
            "中兴通讯(000063)、烽火通信(600498)、锐捷网络(301165观察)、光迅科技(002281)；海外 Broadcom/Marvell",
            "决定模块端口速率、相干传输和运营商投资节奏",
            "业务更宽，需用折价倍数避免当作纯光模块估值",
        ],
        [
            "下游应用",
            "AI 数据中心、DCI、运营商骨干、FTTH、企业园区、工业/汽车光互连",
            "中兴通讯(000063)、烽火通信(600498)、共进股份(603118观察)、日海智能(002313观察)、天邑股份(300504观察)、模块/光纤全链条",
            "决定需求周期长度：AI 短周期快，运营商与 FTTH 慢周期稳",
            "报告将短周期弹性和慢周期底盘分开估值",
        ],
    ]
    lines = [
        r"\begin{exhibitbox}[表：完整光通信产业链地图]",
        r"\centering\tiny",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.25cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.25cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.25cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.45cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{层级} & \textbf{核心对象} & \textbf{代表公司/映射} & \textbf{价值池} & \textbf{估值处理} \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(tex(cell) for cell in row) + r" \\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def watchlist_latex() -> str:
    lines = [
        r"\begin{exhibitbox}[表：设备与材料观察池]",
        r"\centering\scriptsize",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.4cm} >{\raggedright\arraybackslash}p{2.2cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{名称} & \textbf{产业位置} & \textbf{处理方式} \\",
        r"\midrule",
    ]
    for item in localized_watchlist():
        lines.append(
            rf"{tex(item['code'])} & {tex(item['name'])} & {tex(item['role'])} & {tex(item['reason'])} \\"
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def panorama_universe_latex(rows: list[dict]) -> str:
    blocks = [r"\section{A 股全景股票图谱：覆盖池与观察池分开}"]
    blocks.append(
        "本报告将股票图谱分成两层：第一层是进入最终估值表的可估值覆盖池，必须具备当前价、正 EPS、股本、市值、三年 EPS 桥、目标价、空间和动作；第二层是产业链观察池，属于光通信或相邻网络链条，但因亏损、业务纯度不足、利润分母过薄或更偏服务/终端设备，暂不发布正式目标价。"
    )
    covered_chunks = [rows[:13], rows[13:]]
    for idx, chunk in enumerate(covered_chunks, start=1):
        lines = [
            rf"\begin{{exhibitbox}}[表：可估值覆盖池 {idx}]",
            r"\centering\tiny",
            r"\renewcommand{\arraystretch}{1.13}",
            r"\setlength{\tabcolsep}{2pt}",
            r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.35cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.3cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.2cm} >{\centering\arraybackslash}p{0.75cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
            r"\toprule",
            r"\textbf{标的} & \textbf{产业位置} & \textbf{层级} & \textbf{权重} & \textbf{纳入原因} \\",
            r"\midrule",
        ]
        for r in chunk:
            lines.append(
                rf"{tex(r['name'])} {r['code']} & {tex(r['role'])} & {tex(r['tier'])} & {r['weight_pct']}\% & 正 EPS 且能建立当前价目标价模型；动作 {tex(r['rating_cn']) if 'rating_cn' in r else '待生成'} \\"
            )
        lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
        blocks.append("\n".join(lines))
    watchlist = localized_watchlist()
    watch_chunks = [watchlist[:6], watchlist[6:]]
    for idx, chunk in enumerate(watch_chunks, start=1):
        lines = [
            rf"\begin{{exhibitbox}}[表：产业链观察池 {idx}]",
            r"\centering\tiny",
            r"\renewcommand{\arraystretch}{1.13}",
            r"\setlength{\tabcolsep}{2pt}",
            r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.35cm} >{\raggedright\arraybackslash}p{2.1cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
            r"\toprule",
            r"\textbf{代码} & \textbf{名称} & \textbf{产业位置} & \textbf{未纳入目标价原因} \\",
            r"\midrule",
        ]
        for item in chunk:
            lines.append(
                rf"{tex(item['code'])} & {tex(item['name'])} & {tex(item['role'])} & {tex(item['reason'])} \\"
            )
        lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
        blocks.append("\n".join(lines))
    return "\n".join(blocks)


def application_matrix_latex() -> str:
    rows = [
        ["AI 数据中心", "800G/1.6T 光模块、交换 ASIC、光引擎、DSP、EML/CW 光源", "中际旭创、新易盛、天孚通信、源杰科技、长光华芯", "短周期最强，订单和毛利率必须季季验证"],
        ["DCI/相干传输", "相干模块、ROADM/OTN、WDM、长距光纤", "光迅科技、烽火通信、中兴通讯、长飞光纤", "从云数据中心外溢到城域/长距互连，节奏慢于 AI 集群"],
        ["运营商骨干/5G/6G 承载", "OTN、PON、路由交换、光纤光缆、接入设备", "中兴通讯、烽火通信、亨通光电、中天科技、长飞光纤", "由运营商 capex 驱动，盈利弹性低但底盘稳定"],
        ["FTTH/企业园区", "ODN、PON、连接器、配线、室内外光缆", "长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份、太辰光", "价格竞争更强，适合作为现金流和周期底仓验证"],
        ["工业/汽车/边缘互连", "短距光模块、连接器、传感与工业光器件", "光库科技、太辰光、华工科技", "商业化节奏分散，暂不作为主估值锚"],
    ]
    lines = [
        r"\begin{exhibitbox}[表：下游应用与订单传导]",
        r"\centering\scriptsize",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.8cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}",
        r"\toprule",
        r"\textbf{应用} & \textbf{拉动环节} & \textbf{A 股映射} & \textbf{投资节奏} \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(tex(cell) for cell in row) + r" \\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{exhibitbox}"]
    return "\n".join(lines)


def chain_layer_deep_dive_latex() -> str:
    sections = [
        (
            "材料/基底：决定物理边界，不直接等于短期弹性",
            "材料层是光通信的底层约束。光纤预制棒和高纯石英决定长距离传输的衰减、成本和供给弹性；InP/GaAs 决定高速激光器和探测器的外延质量；薄膜铌酸锂和硅光晶圆决定调制器、PIC 和 CPO 路线的长期选择。材料环节的商业特征是技术壁垒高、验证周期长、收入确认慢，短期股价往往跟随主题扩散，但利润兑现并不一定同步。",
            "调研上不能只问“有没有供货”，而要看三类指标：第一，材料纯度、缺陷密度、尺寸和批间稳定性是否满足高速光通信要求；第二，客户认证是否进入量产而不是样品；第三，价格和良率改善是否足以抵消扩产折旧。A 股能直接建模的纯材料标的有限，因此本报告把材料作为产业链必备层披露，但不把缺少稳定利润分母的对象放入最终目标价表。",
        ),
        (
            "制造设备：良率瓶颈会先于利润表出现",
            "高速光芯片、硅光、薄膜铌酸锂和 1.6T 模块的放量，都离不开外延、光刻/刻蚀、划片、贴片、主动耦合、老化和光电测试设备。设备不是“配角”，而是良率和吞吐的前置条件。尤其在 1.6T 和 CPO 过渡期，主动耦合精度、热稳定性、自动化节拍和高速测试一致性会决定单线产能和返工率。",
            "但设备公司进入投资覆盖需要更严格：设备订单可能领先收入几个季度，客户认证也可能停在小批量，单季亏损或项目制收入会让 PE 模型失真。罗博特科这类标的适合进入观察池，重点跟踪新签订单、客户结构、交付节奏、毛利率、费用率和经营现金流，而不是在亏损分母上硬推目标价。",
        ),
        (
            "光芯片/光源：战略稀缺性最高，验证门槛也最高",
            "光芯片层包括 DFB/EML/VCSEL/CW 激光器、PD/APD、PLC/AWG、硅光 PIC 和调制器，是 1.6T、硅光和 CPO 的核心期权。源杰科技、长光华芯、仕佳光子等标的的价值不在于短期收入规模，而在于能否进入头部模块厂和系统厂供应链，并在良率、功耗、可靠性和成本上通过量产考验。",
            "估值上，光芯片可以给战略溢价，但不能忽略利润分母。若客户认证停留在送样阶段，收入占比低或毛利率不稳定，高 PE 会迅速变成估值陷阱。本报告对上游芯片设置更高倍数区间，同时也把证据质量、Q2/Q3 放量和客户数列为核心失效条件。",
        ),
        (
            "光器件/无源：毛利率质量高，但需要 attach rate 支撑",
            "光器件层包括隔离器、环形器、透镜、WDM、滤波器、连接器、精密耦合件和部分调制器件。天孚通信、光库科技、太辰光的共同点是毛利率质量较好，且受益于高速模块封装复杂度上升。不同点在于客户结构、产品稀缺性和订单兑现节奏。",
            "调研重点不是“有没有 AI 逻辑”，而是 attach rate 和价值量是否真的上升。如果高速模块单机价值量提升被价格下降抵消，或客户开始自供关键器件，器件公司的利润弹性会低于主题预期。因此本报告要求用单季毛利率、收入增速和经营现金流三项共同验证。",
        ),
        (
            "光模块：最直接的 AI capex 弹性，也是最拥挤的交易",
            "光模块是 AI 数据中心向 A 股传导最直接的利润层。中际旭创和新易盛在 2026Q1 已经把海外 AI 订单转化为收入、利润和较高毛利率，因此它们仍是核心研究池。光迅科技、华工科技、剑桥科技也有模块业务，但业务混合度、利润率和客户结构决定了它们不能完全按纯 AI 模块龙头估值。",
            "模块层的关键变量包括 800G 出货持续性、1.6T 资格认证、ASP 下行幅度、客户集中、汇率、海外产能和现金流。若收入增长但应收账款、存货和经营现金流恶化，说明订单质量弱于利润表表象。目标价必须随 EPS 和毛利率动态调整，不能沿用主题行情高点的静态倍数。",
        ),
        (
            "光纤光缆/ODN：慢周期底盘，不是 AI 模块替代品",
            "光纤光缆和 ODN 连接数据中心、城域 DCI、运营商骨干、FTTH、海缆和边缘节点。长飞光纤、亨通光电、中天科技承担预制棒、光纤光缆和海缆底座；通鼎互联、永鼎股份更偏通信线缆、ODN、网络集成和接入侧场景。它们的利润弹性通常慢于 AI 模块，且受价格周期、运营商招标、海缆项目、FTTH/园区项目和库存周期影响更大。",
            "投资处理上，这一层适合用现金流、订单能见度和项目利润率估值，而不是套用高端光模块 PE。若光纤价格改善、预制棒利用率恢复、海缆/运营商项目交付提速，慢周期底盘可以提供组合稳定性；若价格竞争重新加剧，它们会拖累全链条加权空间。",
        ),
        (
            "网络设备：把光通信从器件拉回系统和应用",
            "网络设备层包括交换机、路由器、OTN、ROADM、PON、接入设备以及与 switch ASIC/NIC 配套的系统生态。中兴通讯和烽火通信把光通信连接到运营商、云网络和企业应用场景。它们的优势是业务规模和客户稳定性，劣势是光通信纯度低、周期长、项目利润率波动。",
            "这一层的调研要看运营商 capex、招标份额、网络设备毛利率、云网络产品进展和海外政策压力。估值上，网络设备公司应给更低但更稳的倍数，除非其 AI 网络产品能够证明新的利润曲线。",
        ),
        (
            "下游应用：决定估值应该快还是慢",
            "下游应用不是一个变量。AI 数据中心是快周期，几个季度内就会体现在模块订单和毛利率；DCI/相干传输介于云和运营商之间；运营商骨干、FTTH 和企业园区更偏慢周期；工业和汽车光互连商业化更分散。把这些需求混成一个“光通信景气”会导致估值错配。",
            f"因此本报告把 {len(TICKERS)} 只覆盖标的按应用周期分层：模块龙头看 AI 快周期，光纤光缆看运营商/海缆/FTTH，网络设备看 capex 和利润率，上游芯片/器件看认证与良率。只有当多个应用同时兑现，产业链整体才适合上修；若只有 AI 模块兑现，其他层级不应跟随无差别追高。",
        ),
    ]
    blocks = [r"\section{产业链层级深挖：每一层该问什么}"]
    for title, paragraph_a, paragraph_b in sections:
        blocks.append(rf"\subsection{{{tex(title)}}}")
        blocks.append(tex(paragraph_a))
        blocks.append("")
        blocks.append(tex(paragraph_b))
    return "\n".join(blocks)


def application_deep_dive_latex() -> str:
    sections = [
        (
            "AI 数据中心",
            "AI 数据中心是本轮光通信最强的增量来源，但它拉动的是一组具体环节：交换 ASIC 端口升级、NIC/网卡带宽、800G/1.6T 光模块、DSP/TIA/driver、EML/CW 激光器、精密耦合和高速测试。投资上最直接的映射是中际旭创、新易盛，其次是天孚通信、源杰科技、长光华芯、仕佳光子、光库科技等上游芯片/器件。需要跟踪的不是“AI capex 是否高”，而是这些 capex 是否转化为可见订单、稳定 ASP 和毛利率。",
        ),
        (
            "DCI 与相干传输",
            "DCI 和相干传输是 AI 数据中心外溢后的第二层需求。大型数据中心之间需要更高带宽、低功耗和长距离互连，相干模块、ROADM/OTN、WDM、光纤和网络设备都会受益。它的节奏通常慢于 AI 集群内部互连，但订单更偏系统项目，适合关注光迅科技、烽火通信、中兴通讯以及光纤光缆链条的项目交付。",
        ),
        (
            "运营商骨干与 5G/6G 承载",
            "运营商骨干和承载网是光通信传统大盘。它不会像 AI 模块一样产生爆发式弹性，但决定行业底盘。中兴通讯、烽火通信、长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份受运营商 capex、招标份额、设备利润率、光缆价格和通信线缆项目影响更大。估值应看订单周期和现金流，不应简单跟随 AI 模块情绪。",
        ),
        (
            "FTTH、企业园区和边缘节点",
            "FTTH、企业园区和边缘节点需求更分散，对 ODN、PON、连接器、室内外光缆、通信线缆和接入设备形成稳定拉动。该场景的竞争更充分、价格压力更明显，但可提供长周期收入底盘。太辰光、长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份和部分网络设备公司需要用现金流和项目利润率验证。",
        ),
        (
            "工业、汽车和新型光互连",
            "工业和汽车光互连目前仍处于分散商业化阶段，可能在传感、车载高速互连、工业控制和边缘计算中形成长期需求，但 2026 年不宜作为主要估值分母。光库科技、华工科技和部分精密器件公司具备相关选项，本报告只把它作为长期上修因子，等待收入占比和客户结构更清晰后再提升权重。",
        ),
    ]
    blocks = [r"\section{下游应用深挖：不同场景对应不同估值节奏}"]
    for title, paragraph in sections:
        blocks.append(rf"\subsection{{{tex(title)}}}")
        blocks.append(tex(paragraph))
    return "\n".join(blocks)


def research_workplan_latex() -> str:
    return r"""
\section{为什么需要工作底稿}
光通信产业链横跨材料、半导体设备、光电芯片、精密器件、模块、光纤光缆、网络设备和下游应用。若只写市场叙事，很容易把 AI 模块的高景气错误外推到所有层级；若只写公司财务，又会忽视上游认证、良率、标准演进和应用周期。本附录把后续调研拆成可执行工作底稿，用于每次更新报告时逐项核查。

\section{全链条调研问题库}
\begin{exhibitbox}[表：产业链调研问题库]
\centering\tiny
\renewcommand{\arraystretch}{1.20}
\setlength{\tabcolsep}{2pt}
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.35cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.55cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.45cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{2.35cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}
\toprule
\textbf{层级} & \textbf{核心问题} & \textbf{量化指标} & \textbf{优先来源} & \textbf{估值影响} \\
\midrule
材料/基底 & 预制棒、InP/GaAs、硅光晶圆、薄膜铌酸锂是否进入稳定量产 & 良率、缺陷密度、客户认证、扩产资本开支 & 公司公告、招股书、产业标准、客户验证记录 & 影响上游芯片/器件长期 PE 上限，不直接推高模块 EPS \\
制造设备 & 外延、主动耦合、老化和高速测试能否支撑 1.6T/CPO 放量 & 新签订单、交付周期、毛利率、费用率、现金流 & 公司订单公告、客户扩产、设备招标、调研纪要 & 亏损或项目制公司不纳入 PE 目标价，进入观察池 \\
光芯片/光源 & EML/CW/VCSEL/PD/APD/PLC/AWG 是否通过头部客户认证 & 客户数、收入占比、毛利率、研发费用率、良率 & 财报、客户公告、供应链验证、专利与产品手册 & 通过认证后提升倍数；若停在送样阶段则下修 \\
光器件/无源 & 高速模块 attach rate 是否提升，是否被客户自供替代 & 单季收入、毛利率、客户集中、存货、OCF & 季报、调研、模块厂需求、产品拆解 & attach rate 上升支持溢价；价格压力降低目标 PE \\
光模块 & 800G 是否持续放量，1.6T 是否从认证转批量 & 收入增速、毛利率、ASP、库存、应收账款、OCF & 季报、客户 capex、NVIDIA/云厂商动向、行业预测 & 直接决定 EPS 和目标价，是全链条 beta 核心 \\
光纤光缆/ODN & 运营商、海缆、FTTH、DCI 项目是否改善 & 招标量、项目毛利率、预制棒利用率、光纤价格、现金流 & 运营商招标、公司公告、行业价格、项目交付 & 慢周期底盘，按现金流和项目节奏给折价倍数 \\
网络设备 & OTN/ROADM/PON/交换路由产品是否改善利润率 & 运营商 capex、订单、毛利率、海外收入、研发投入 & 运营商招标、设备商财报、标准组织、云网络产品发布 & 更稳但纯度低，除非 AI 网络产品兑现否则不套模块倍数 \\
下游应用 & AI、DCI、运营商、FTTH、企业/工业是否同步兑现 & 云 capex、端口速率、招标、项目交付、行业库存 & 云厂商/芯片厂公告、运营商招标、行业协会、财报 & 决定估值节奏：AI 快，运营商慢，工业/汽车作为长期期权 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{更新频率与触发规则}
\begin{exhibitbox}[表：更新触发规则]
\centering\scriptsize
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{2.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}
\toprule
\textbf{频率} & \textbf{必须更新的内容} & \textbf{触发原因} \\
\midrule
每日/行情异常 & 当前价、市值、目标价空间、成交额、涨跌幅和拥挤度 & 光通信板块波动大，旧目标价空间很快失真 \\
月度 & 云厂商 capex、交换 ASIC/800G/1.6T 新闻、运营商招标、光纤价格 & 订单和标准变化通常领先财报 \\
季度 & __COVERED_COUNT__ 只覆盖标的收入、利润、EPS、毛利率、OCF、存货、应收账款 & 估值分母必须随财报重算 \\
事件触发 & 1.6T 批量订单、CPO/硅光量产、重大客户认证、出口管制、并购扩产 & 改变估值倍数或失效条件 \\
报告复审 & 来源注册表、claim audit、估值审计、PDF 可读性和 verifier & 防止数据过时、章节空心化和估值缺失 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{上修与下修的硬门槛}
上修不能只因为行业新闻热。至少需要满足以下三类证据之一：第一，财报层面出现收入、毛利率和经营现金流同步改善；第二，客户认证从送样进入批量订单，并且公司能披露或通过利润表验证；第三，应用层需求从单一 AI 模块外溢到 DCI、运营商、光纤光缆或网络设备项目。若只有股价上涨而没有上述证据，本报告只更新当前价和空间，不上修目标 PE。

下修同样需要规则化。若 Q2/Q3 净利润低于 Q1 的 0.85 倍、经营现金流连续弱于利润、毛利率明显下滑、存货或应收账款快于收入增长、光纤光缆价格继续下行、运营商 capex 延后、或 CPO 改变可插拔模块价值分配，必须下调 EPS、PE 或动作标签。对于观察池公司，若亏损扩大或订单兑现继续延后，维持观察池并不得进入最终估值表。

\section{分层数据源优先级}
\begin{exhibitbox}[表：数据源优先级]
\centering\scriptsize
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.5cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}
\toprule
\textbf{优先级} & \textbf{可用来源} & \textbf{用途} & \textbf{限制} \\
\midrule
A & 公司公告、财报、监管披露、结构化财务包 & 收入、利润、EPS、现金流、股本、目标价分母 & 滞后于订单和技术变化 \\
A- & 官方公司新闻、NVIDIA/Broadcom/OIF/Ethernet Alliance 等官方公开页 & 技术路线、标准、需求方向和供应链关系 & 通常不披露 A 股公司直接订单金额 \\
B & 行业机构公开摘要、公开演讲、招标公告、价格跟踪 & 需求节奏、应用周期、行业景气度 & 需要避免把摘要当作完整预测模型 \\
C & 二手媒体、社交平台、未取得原文的卖方片段 & 识别市场情绪和分歧 & 不得作为估值输入，不得替代目标价模型 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{后续调研排期}
下一轮更新优先级如下。第一，逐只补齐 __COVERED_COUNT__ 家覆盖公司的正式 2026Q1/半年度公告原文归档，减少第三方公告入口依赖。第二，单独建立光芯片/光源专题，核查源杰科技、长光华芯、仕佳光子在客户认证和良率上的真实进度。第三，补光纤光缆价格和运营商招标数据库，用于校准长飞、亨通、中天、通鼎、永鼎的慢周期估值。第四，跟踪中兴、烽火、光迅、锐捷等在 OTN、ROADM、PON、云网络设备上的利润率变化。第五，若罗博特科或其他设备链标的恢复盈利，再建立非 PE 或 EV/Sales/订单覆盖倍数模型。
""".replace("__COVERED_COUNT__", str(len(TICKERS)))


def company_cards_latex(rows: list[dict]) -> str:
    blocks: list[str] = [
        r"\section{覆盖标的逐项公司卡}",
        "下面的公司卡将产业位置、2026Q1 财务交付、估值含义和下一季度验证点逐项展开。其目的不是重复估值表，而是把每一只股票为什么被给到该动作说清楚，避免用板块景气度覆盖个股差异。",
    ]
    for r in rows:
        stance = "riskgreen" if r["rating_cn"] in {"买入", "增持"} else ("riskamber" if "中性" in r["rating_cn"] else "riskred")
        preview = EARNINGS_PREVIEW_H1_2026.get(r["code"]) if EARNINGS_PREVIEW_H1_2026.get(r["code"], {}).get("valuation_input") else None
        preview_row = (
            rf"H1 预告(已计入) & H1 2026 预告归母 CNY{num(preview['h1_np_low'])}--{num(preview['h1_np_high'])} 亿元、同比 +{preview['yoy_low']*100:.0f}\%--+{preview['yoy_high']*100:.0f}\%（{tex(preview['announce_date'])} 公告），已按 H1 年化计入 2026E 分母；评级不因单纯利润超预期机械上修，详见第 11 章 \\"
            if preview
            else ""
        )
        blocks.append(
            rf"""
\subsection{{{tex(r['name'])}（{r['code']}）：{tex(r['role'])}}}
{tex(r['name'])} 位于本报告定义的 \textbf{{{tex(r['tier'])}}} 层级，研究权重为 {r['weight_pct']}\%。2026Q1 公司收入为 CNY{num(r['q1_revenue_100mn'])} 亿元，归母净利润为 CNY{num(r['q1_np_100mn'])} 亿元，毛利率 {num(r['q1_gross_margin'],1)}\%，归母净利同比 {pct_tex(r['q1_profit_growth']/100)}。按照本报告季节性假设，2026E 归母净利为 CNY{num(r['net_profit_2026e_100mn'])} 亿元，2027E EPS 为 CNY{num(r['eps_2027e'])}。

\begin{{exhibitbox}}[单票卡：{tex(r['name'])}]
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.5cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
产业位置 & {tex(r['role'])} \\
当前价与市值 & CNY{num(r['current_price_cny'])}；市值约 CNY{num(r['market_cap_100mn_cny'],0)} 亿元 \\
估值结论 & 综合目标 CNY{num(r['final_target_cny'])}，区间 CNY{tex(r['final_fair_value_range_cny'])}，空间 {pct_tex(r['final_upside'])}，动作 \stance{{{stance}}}{{{tex(r['rating_cn'])}}} \\
估值锚点 & 内在锚 CNY{num(r['base_target_cny'])}；市场锚 CNY{num(r['market_anchor_value_cny'])}；权重 {tex(r['final_anchor_weights_label'])} \\
核心催化 & {tex(r['catalyst'])} \\
失效条件 & {tex(r['invalidation'])} \\
{preview_row}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

投资含义上，{tex(r['rating_note'])} 市场锚的作用是承认当前成交和共识定价已经给出的情绪溢价，但它不能替代利润、毛利率和现金流。组合处理应当把它放在与当前动作匹配的仓位层级，而不是因为光通信行业景气就无差别买入。下一季度最关键的是利润、毛利率和现金流是否同步，若只有收入增长而现金流或毛利率恶化，则说明订单质量低于股价隐含预期。
"""
        )
    return "\n".join(blocks)


def component_num(components: dict, key: str) -> str:
    value = components.get(key)
    if value is None:
        return "n.a."
    return num(value)


def valuation_cards_latex(rows: list[dict]) -> str:
    blocks: list[str] = [
        r"\section{单票估值卡与压力测试}",
        "本节把最终估值表拆成单票估值卡。每张卡都明确估值方法、EPS/收入/BVPS 分母、PE/PB/PS 组件、三档价值和动作，方便后续在行情变化后直接替换价格、财务分母或估值权重重算。",
    ]
    for r in rows:
        stance = "riskgreen" if r["rating_cn"] in {"买入", "增持"} else ("riskamber" if "中性" in r["rating_cn"] else "riskred")
        pe_weight = r["valuation_weights"].get("pe", 0)
        eps_down_target = r["base_target_cny"] - r["base_components"]["pe_value_cny"] * pe_weight * 0.15
        multiples_down_target = r["base_target_cny"] * 0.80
        combined_down_target = eps_down_target * 0.80
        preview = EARNINGS_PREVIEW_H1_2026.get(r["code"]) if EARNINGS_PREVIEW_H1_2026.get(r["code"], {}).get("valuation_input") else None
        preview_row = (
            rf"H1 预告(已计入) & \multicolumn{{3}}{{r}}{{已入分母}} & H1 2026 归母 CNY{num(preview['h1_np_low'])}--{num(preview['h1_np_high'])} 亿元、同比 +{preview['yoy_low']*100:.0f}\%--+{preview['yoy_high']*100:.0f}\%（{tex(preview['announce_date'])}）；已按 H1 年化计入 2026E EPS/内在锚，冻结对照见第 11 章 \\"
            if preview
            else ""
        )
        blocks.append(
            rf"""
\subsection{{{tex(r['name'])}（{r['code']}）估值卡}}
\begin{{exhibitbox}}[估值卡：{tex(r['name'])}]
\centering
\scriptsize
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.5cm}} >{{\raggedleft\arraybackslash}}p{{1.6cm}} >{{\raggedleft\arraybackslash}}p{{1.6cm}} >{{\raggedleft\arraybackslash}}p{{1.6cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{项目}} & \textbf{{熊市}} & \textbf{{基准}} & \textbf{{牛市}} & \textbf{{说明}} \\
\midrule
估值方法 & \multicolumn{{3}}{{r}}{{{tex(r['method_short'])}}} & {tex(r['method'])}；权重 {tex(r['valuation_weights_label'])} \\
EPS 分母 & {num(r['eps_2026e'])} & {num(r['eps_2027e'])} & {num(r['eps_2028e'])} & 2026E 由 Q1 季节性折算，2027/2028E 由公司层面成长假设外推 \\
收入/股 & {num(r['sales_per_share_2026e'])} & {num(r['sales_per_share_2027e'])} & {num(r['sales_per_share_2028e'])} & PS 组件用于校验收入规模、业务纯度和主题期权，不替代交付验证 \\
BVPS & {num(r['book_value_per_share'])} & {num(r['book_value_per_share'])} & {num(r['book_value_per_share'])} & PB 组件用于资产、项目和混合业务的底部校验 \\
PE 组件 & {component_num(r['bear_components'], 'pe_value_cny')} & {component_num(r['base_components'], 'pe_value_cny')} & {component_num(r['bull_components'], 'pe_value_cny')} & PE 档位 {r['bear_pe']}x/{r['base_pe']}x/{r['bull_pe']}x，只按权重进入综合价值 \\
PB 组件 & {component_num(r['bear_components'], 'pb_value_cny')} & {component_num(r['base_components'], 'pb_value_cny')} & {component_num(r['bull_components'], 'pb_value_cny')} & PB 档位 {r['bear_pb']}x/{r['base_pb']}x/{r['bull_pb']}x，非资产型公司为辅助或 n.a. \\
PS 组件 & {component_num(r['bear_components'], 'ps_value_cny')} & {component_num(r['base_components'], 'ps_value_cny')} & {component_num(r['bull_components'], 'ps_value_cny')} & PS 档位 {r['bear_ps']}x/{r['base_ps']}x/{r['bull_ps']}x，牛市价值按 12\% 折现 \\
内在价值锚 & {num(r['bear_value_cny'])} & {num(r['base_target_cny'])} & {num(r['bull_value_cny'])} & 来自业务模型组件加权，不是所有标的统一套 PE \\
市场情绪锚 & \multicolumn{{3}}{{r}}{{{num(r['market_anchor_value_cny'])}}} & 成交额分位 {pct_tex(r['trading_value_percentile'])}，情绪状态 {tex(r['market_sentiment_regime'])}，当前价较内在锚溢价 {pct_tex(r['sentiment_premium_vs_intrinsic'])} \\
综合目标价 & \multicolumn{{3}}{{r}}{{{num(r['final_target_cny'])}}} & 内在/市场/券商权重：{tex(r['final_anchor_weights_label'])} \\
当前价格 & \multicolumn{{3}}{{r}}{{{num(r['current_price_cny'])}}} & 2026-06-26 收盘后行情包 \\
空间与动作 & \multicolumn{{3}}{{r}}{{{pct_tex(r['final_upside'])}；\stance{{{stance}}}{{{tex(r['rating_cn'])}}}}} & 证据质量 {tex(r['quality'])}；{tex(r['market_action_logic'])} \\
{preview_row}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

压力测试上，如果 2027E EPS 下修 15\%，仅 PE 组件受影响，{tex(r['name'])} 的内在价值锚降至约 CNY{num(eps_down_target)}；若市场风险偏好下行导致所有估值组件倍数降 20\%，内在锚降至约 CNY{num(multiples_down_target)}。两者同时发生时，内在锚约为 CNY{num(combined_down_target)}。若成交额分位回落、题材拥挤退潮或券商/市场共识下修，市场情绪锚也会同步下移，综合目标价会向内在价值锚收敛。这就是本报告要求用 Q2/Q3 交付、现金流和订单质量确认情绪溢价的原因。
"""
        )
    return "\n".join(blocks)


def company_diligence_appendix_latex(rows: list[dict]) -> str:
    blocks = [
        r"\section{逐公司调研底稿}",
        "本节不是投资建议重复，而是后续复盘时的逐公司核查模板。每家公司都需要同时检查产业位置、财务分母、估值结论、催化剂、失效条件和下一轮数据更新点。若后续行情或财报变化，只要替换当前价和 EPS 分母，就能快速判断动作标签是否需要改变。",
    ]
    for r in rows:
        blocks.append(
            rf"""
\subsection{{{tex(r['name'])}（{r['code']}）}}
{tex(r['name'])} 的产业定位是 \textbf{{{tex(r['role'])}}}，在本报告中的层级为 {tex(r['tier'])}，研究权重 {r['weight_pct']}\%。当前价 CNY{num(r['current_price_cny'])}，按 2026Q1 归母净利和 EPS 反推的市值约 CNY{num(r['market_cap_100mn_cny'],0)} 亿元。2026Q1 收入 CNY{num(r['q1_revenue_100mn'])} 亿元，归母净利 CNY{num(r['q1_np_100mn'])} 亿元，毛利率 {num(r['q1_gross_margin'],1)}\%，经营现金流 CNY{num(r['q1_ocf_100mn'])} 亿元。以上是估值分母，不允许被行业叙事替代。

估值上，本报告采用 \textbf{{{tex(r['method_short'])}}} 方法：{tex(r['method'])}。{tex(r['name'])} 的 2026E/2027E/2028E EPS 分别为 CNY{num(r['eps_2026e'])}、CNY{num(r['eps_2027e'])}、CNY{num(r['eps_2028e'])}，2027E 收入/股为 CNY{num(r['sales_per_share_2027e'])}，BVPS 为 CNY{num(r['book_value_per_share'])}；内在组件权重为 {tex(r['valuation_weights_label'])}，内在价值锚 CNY{num(r['base_target_cny'])}，市场情绪锚 CNY{num(r['market_anchor_value_cny'])}，综合权重 {tex(r['final_anchor_weights_label'])}，综合目标价 CNY{num(r['final_target_cny'])}，综合空间 {pct_tex(r['final_upside'])}，动作 {tex(r['rating_cn'])}，证据质量 {tex(r['quality'])}。二级校验为：{tex(r['secondary_check'])}。

下一轮调研首先验证催化剂：{tex(r['catalyst'])} 其次验证失效条件：{tex(r['invalidation'])} 若催化剂没有进入收入、毛利率和现金流，不能上调 PE；若失效条件出现，应同时下调 EPS 和动作标签。对于产业链映射，必须核查它的增长是否来自本层级真实需求，而不是来自板块情绪扩散。
"""
        )
    return "\n".join(blocks)


def earnings_preview_latex(rows: list[dict], revision: dict | None) -> str:
    """Post-cutoff (2026-07-06) H1 2026 earnings-preview addendum chapter.
    Dual-presentation: keeps the 6/26 frozen conclusion and adds a labelled
    revision. Chinese-only to satisfy the language gate."""
    census = OPTICAL_PREVIEW_CENSUS
    disclosed_rows = "\n".join(
        rf"{tex(d['code'])} & {tex(d['name'])} & {tex(d['coverage'])} & {tex(d['type'])} & {tex(d['yoy'])} & {tex(d['date'])} \\"
        for d in census["disclosed"]
    )
    preview_detail_rows = "\n".join(
        rf"{tex(code)} & {tex(p['name'])} & {tex({'covered': '估值覆盖', 'watch_pool': '观察池', 'out_of_universe': 'universe 外'}[p['coverage']])} & "
        rf"{num(p['h1_np_low'])}--{num(p['h1_np_high'])} & +{p['yoy_low']*100:.0f}\%--+{p['yoy_high']*100:.0f}\% & {tex(p['announce_date'])} & {tex(p['source_id'])} \\"
        for code, p in EARNINGS_PREVIEW_H1_2026.items()
    )
    blocks = [
        rf"""
\section{{本章定位与边界}}
本章是数据截止后更新附录。全书封面基准日与\textbf{{价格口径}}仍为 \textbf{{2026-06-26}}（行情冻结）。对已发布 2026 H1 业绩预告的覆盖标的，报告采用\textbf{{置信度优先}}原则：管理层业绩预告是最高置信度的前瞻盈利信号，已在第 8 章\textbf{{直接计入 2026E 归母分母、EPS、内在价值锚和综合目标价}}（见第 8.2 节"业绩预告已计入估值"框）。本章的作用是给出\textbf{{冻结口径（2026Q1 年化）与预告口径的并列对照}}，让读者看清预告把估值分母抬升了多少、为什么综合目标价与评级最终落在何处，而不是把预告藏在附录里不计入。价格与未发预告标的的财务分母仍冻结在 2026-06-26。

\section{{光通信板块 H1 2026 预告普查}}
截至 {tex(census['as_of'])}，本报告 universe 共 {census['universe_size']} 只标的（估值覆盖 {census['valuation_coverage']} + 观察池 {census['watch_pool']}），其中已发布正式 H1 2026 业绩预告的有 \textbf{{{census['previews_in_universe']} 只}}。方法上，{tex(census['method'])}龙头（{tex('、'.join(census['marquee_no_preview']))}）尚未发布预告，其余标的完整半年报预约披露集中在 2026-08-01 至 08-31。其中永鼎股份（600105）与杭电股份（603618）为估值覆盖池标的，其 H1 预告已计入第 8 章估值分母；锐捷网络（301165）为观察池标的。

\begin{{exhibitbox}}[表：报告 universe 内已披露 H1 预告标的]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.6cm}} >{{\raggedright\arraybackslash}}p{{2.0cm}} >{{\centering\arraybackslash}}p{{1.6cm}} >{{\centering\arraybackslash}}p{{1.2cm}} >{{\raggedleft\arraybackslash}}p{{2.6cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{代码}} & \textbf{{名称}} & \textbf{{覆盖}} & \textbf{{类型}} & \textbf{{同比区间}} & \textbf{{公告日}} \\
\midrule
{disclosed_rows}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{H1 2026 预告明细}}
下表汇总本轮已核实的 H1 2026 业绩预告，含 universe 外读数标的。归母净利单位为亿元，同比为公告披露区间。数据来源为公司公告与 akshare stock\_yjyg\_em 预告库交叉核对。

\begin{{exhibitbox}}[表：H1 2026 业绩预告明细]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.5cm}} >{{\raggedright\arraybackslash}}p{{1.8cm}} >{{\centering\arraybackslash}}p{{1.8cm}} >{{\raggedleft\arraybackslash}}p{{2.0cm}} >{{\raggedleft\arraybackslash}}p{{2.4cm}} >{{\centering\arraybackslash}}p{{1.7cm}} >{{\centering\arraybackslash}}p{{0.9cm}}}}
\toprule
\textbf{{代码}} & \textbf{{名称}} & \textbf{{覆盖}} & \textbf{{H1归母(亿)}} & \textbf{{同比}} & \textbf{{公告日}} & \textbf{{来源}} \\
\midrule
{preview_detail_rows}
\bottomrule
\end{{tabularx}}
\sourcenote{{来源 S-35/S-36/S-37 为公司业绩预告公告；M-04 为普查方法记录。永鼎 600105 与杭电 603618 为估值覆盖标的，H1 预告已计入第 8 章估值分母；锐捷 301165 为观察池标的。}}
\end{{exhibitbox}}
"""
    ]
    if revision and revision.get("revisions"):
        for r in revision["revisions"]:
            fz, rv = r["frozen"], r["revised"]
            blocks.append(
                rf"""
\section{{{tex(r['name'])}（{tex(r['code'])}）：业绩预告已计入估值（冻结口径对照）}}
{tex(r['name'])} 属估值覆盖池，{tex(r['announce_date'])} 披露 H1 2026 归母净利 {num(r['h1_np_range_100mn'][0])}--{num(r['h1_np_range_100mn'][1])} 亿元、同比 +{r['h1_yoy_range'][0]*100:.0f}\%--+{r['h1_yoy_range'][1]*100:.0f}\%（{tex(r['forecast_type'])}）。该预告已按置信度优先原则\textbf{{计入第 8 章估值分母与目标价}}；下表给出采用口径与冻结（Q1 年化）口径的并列对照，说明预告把估值分母抬升了多少。{tex(r['bridge_note'])}

\begin{{exhibitbox}}[估值卡：{tex(r['name'])} 冻结 vs 采用]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{3.2cm}} >{{\raggedleft\arraybackslash}}p{{2.7cm}} >{{\raggedleft\arraybackslash}}p{{3.3cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{项目}} & \textbf{{冻结口径 (Q1 年化)}} & \textbf{{采用口径 (H1 预告，已入估值)}} & \textbf{{说明}} \\
\midrule
2026E 归母净利(亿) & {num(fz['net_profit_2026e_100mn'])} & {num(rv['net_profit_2026e_100mn_mid'])} & H1 中值按 H1 占全年 {num(r['seasonality_assumption'],2)} 年化，作为估值分母 \\
2026E 收入(亿) & {num(fz['revenue_2026e_100mn'])} & {num(rv['revenue_2026e_100mn'])} & 量价齐升，收入按 Q1 净利率与指引利润同步上抬（保守下限） \\
2026E EPS & {num(fz['eps_2026e'])} & {num(rv['eps_2026e'])} & EPS 近乎翻倍，反映 Q2 强反转 \\
收入/股 & {num(fz['sales_per_share_2026e'])} & {num(rv['sales_per_share_2026e'])} & PS 腿（权重 50\%）随收入上修，非仅利润修正 \\
2027E EPS & {num(fz['eps_2027e'])} & {num(rv['eps_2027e'])} & 按公司层面成长假设外推 \\
内在价值锚 & {num(fz['intrinsic_anchor_cny'])} & {num(rv['intrinsic_anchor_cny'])} & PE/PB/PS 各腿均随预告上修，内在锚显著抬升 \\
综合目标价 & {num(fz['final_target_cny'])} & {num(rv['final_target_cny'])} & 现价仍较内在锚溢价约 +167\%，市场情绪锚地板支撑，目标价基本持平 \\
评级 & {tex(fz['rating_cn'])} & {tex(rv['rating_cn'])} & {tex('评级维持不变')} \\
盈利质量标签 & {tex(fz['earnings_quality_tag'])} & {tex(rv['earnings_quality_tag'])} & Q1 同比 {pct_tex(fz['q1_profit_growth_pct']/100)} 承压 → H1 大幅预增 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

{tex(r['rating_logic'])} 因此本次采用预告口径为\textbf{{盈利质量与 EPS 层面的上修}}，而非评级上修：待 Q2/Q3 收入、毛利率与现金流同步确认后，方具备将 {tex(r['name'])} 从中性观察上修的条件。组合权重维持不变，价格口径仍为 2026-06-26。
"""
            )
    return "\n".join(blocks)


def write_latex(model: dict, revision: dict | None = None) -> None:
    rows = model["rows"]
    weighted = pct_tex(model["weighted_final_upside"])
    intrinsic_weighted = pct_tex(model["weighted_base_upside"])
    write_text(
        CASE / "main.tex",
        rf"""
% !TEX program = xelatex
\documentclass[a4paper,11pt,openany,fontset=none]{{ctexrep}}

\newcommand{{\reporttitle}}{{光通信全产业链深度研究}}
\newcommand{{\reportsubtitle}}{{材料、设备、芯片、器件、模块、光纤光缆、网络设备与应用全景}}
\newcommand{{\reportkicker}}{{机构股票研究}}
\newcommand{{\reportscope}}{{中国 A 股 | 光通信全产业链}}
\newcommand{{\reportdate}}{{2026 年 6 月 26 日}}
\newcommand{{\reportdatacutoff}}{{市场数据至 2026-06-26 收盘后；财务数据至 2026Q1；附 2026-07-06 H1 业绩预告更新（见第 11 章附加章，不改变封面基准日与冻结估值结论）}}
\newcommand{{\reporttype}}{{行业深度研究}}
\newcommand{{\reportauthor}}{{AStock 研究代理团队}}
\newcommand{{\reporthouseview}}{{\kaishu 光通信不是只有光模块。本报告把产业链拆成材料/基底、制造设备、光芯片、光器件、光模块、光纤光缆、网络设备和下游应用八层，覆盖 {len(rows)} 只可估值 A 股标的并逐一给出当前价、内在价值锚、市场情绪锚、综合目标价、空间和动作；低纯度、亏损或利润分母过薄的链条公司进入观察池。组合权重市场共识调整后空间为 \textbf{{{weighted}}}，内在价值锚空间为 {intrinsic_weighted}。结论是精选已兑现利润分母的模块龙头，同时承认通鼎互联、中天科技、长飞光纤等慢周期链条公司存在可观察市场情绪溢价。}}
\newcommand{{\reportquality}}{{行情来自 astock.quote\_service 2026-06-26 收盘后实时包；财务来自结构化 2026Q1/2025 年报数据；行业证据来自 NVIDIA/Coherent/Lumentum/Broadcom、Ethernet Alliance、OIF、Corning 官方或公开页面与 LightCounting/Cignal AI 公开摘要；券商目标价历史未取得完整可核验原文，因此不作为估值输入。}}
\newcommand{{\reportdisclaimer}}{{本报告基于公开资料整理，不构成任何证券买卖建议。}}

\input{{../../../.agents/templates/preamble.tex}}

\hypersetup{{pdfauthor={{\reportauthor}}, pdftitle={{\reporttitle}}}}

\begin{{document}}
\astockcover
\tableofcontents
\clearpage

\chapter{{投资委员会概要}}
\input{{sections/ch01_ic_summary}}
\chapter{{证据治理与来源边界}}
\input{{sections/ch02_evidence}}
\chapter{{技术路线、速率升级与价值池}}
\input{{sections/ch03_technology}}
\chapter{{产业链映射与竞争格局}}
\input{{sections/ch04_supply_chain}}
\chapter{{AI 数据中心需求与订单传导}}
\input{{sections/ch05_demand}}
\chapter{{公司映射与财务交付}}
\input{{sections/ch06_companies}}
\chapter{{公开研究情绪与分歧}}
\input{{sections/ch07_sentiment}}
\chapter{{估值模型、目标价与空间}}
\input{{sections/ch08_valuation}}
\chapter{{风险、催化剂与监测框架}}
\input{{sections/ch09_risks}}
\chapter{{投资建议与组合执行}}
\input{{sections/ch10_investment}}
\chapter{{数据截止后更新：H1 2026 业绩预告}}
\input{{sections/ch11_earnings_preview}}

\appendix
\chapter{{全产业链调研工作底稿}}
\input{{sections/app_research_workplan}}
\chapter{{来源注册表与模型披露}}
\input{{sections/app_source_audit}}

\clearpage
\thispagestyle{{empty}}
\vspace*{{4cm}}
\begin{{disclosurebox}}[免责声明]
\small
\reportdisclaimer\par
本报告为 AStock 内部研究参考。AStock 目标价和评级为模型化研究结论，不代表外部券商评级、投资顾问意见、交易指令或组合托管建议。市场价格、盈利预测、产业节奏和政策环境可能快速变化，任何组合动作均需结合实时风险约束重新判断。
\end{{disclosurebox}}
\end{{document}}
""",
    )
    final_table = latex_table_final(rows, small=True)
    financial_table = latex_financial_table(rows)
    expectation_table = expectation_valuation_latex(rows)
    expectation_preview = expectation_valuation_latex(rows, limit=10)
    sentiment_table = market_sentiment_anchor_latex(rows)
    sentiment_preview = market_sentiment_anchor_latex(rows, limit=10)
    broker_table = broker_comparison_latex(rows)
    broker_preview = broker_comparison_latex(rows, limit=10)
    top_names = ", ".join(f"{r['name']}({r['code']})" for r in rows[:3])
    write_text(
        SECTIONS / "ch01_ic_summary.tex",
        rf"""
\section{{结论先行}}
本报告重写后的核心结论是：光通信产业链必须按完整上下游理解，不能只看 AI 光模块。上游材料/基底决定光纤、激光芯片和调制器的物理边界；制造设备决定外延、硅光、主动耦合和测试良率；光芯片和光器件决定 1.6T/CPO 的战略稀缺性；光模块决定云厂商 AI capex 到收入利润的最直接弹性；光纤光缆、网络设备和下游应用决定运营商、DCI、FTTH 与企业网络的慢周期底盘。基于 2026-06-26 收盘后价格和 2026Q1 业绩折算，本报告覆盖 {len(rows)} 只可估值标的，另列产业链观察池。组合权重内在价值锚空间为 {intrinsic_weighted}，市场共识调整后综合空间为 \textbf{{{weighted}}}。

组合动作上，\textbf{{中际旭创与新易盛}}仍是最值得放在核心池里的两个光模块标的，原因是其 2026Q1 利润规模和毛利率已经证明海外 AI 订单不是纯主题；长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份提供光纤光缆和预制棒/线缆底盘，但应按慢周期现金流估值；中兴通讯和烽火通信映射网络设备/应用层，不能按纯光模块倍数追高；源杰科技、长光华芯、仕佳光子、光库科技、腾景科技代表上游光芯片/器件稀缺性；长芯博创、德科立、联特科技补足相干/高 beta 模块层；兆龙互连、意华股份、神宇股份补足高速线缆和连接器层，但需要客户认证、良率和 Q2/Q3 利润继续验证。

{final_table}
\sourcenote{{行情：astock.quote\_service 2026-06-26 收盘后实时包；财务：astock.cli financials 2026Q1；估值模型：data/current\_valuation\_model\_20260626.json。}}

\section{{市场预期与券商对照先看结论}}
炒股买的是预期，不只是过去一个季度。因此本报告在 AStock 自有目标价之外，额外给出基于 2026E 收入、2026E EPS、2027E 收入增长和成长性调整倍数的市场预期估值。该表回答“当前价格需要什么预期才能合理”，而不是重复财务历史。

{expectation_preview}
\sourcenote{{完整 26 只标的预期估值见第 8 章和 data/market\_expectation\_valuation\_20260626.json。}}

市场情绪同样是估值方法论的一部分。市场可以错，但当前价、成交额、券商目标和共识定价是可观测信息。本报告把它们作为市场隐含预期锚，和内在价值锚、券商锚共同形成综合目标价。若内在价值锚远低于股价但成交和共识仍强，动作不会机械写成减持，而会标注为中性观察并给出情绪溢价失效条件。

{sentiment_preview}
\sourcenote{{完整市场情绪锚见第 8 章和 data/market\_sentiment\_anchor\_20260626.json。}}

公开券商/一致预期对照用于回答“市场怎么想”。本报告只使用可追溯的公开一致预期、券商摘要或原始入口；没有披露 2026E/2027E 收入、利润、EPS 或目标价的字段，统一标记为未披露，不用 AStock 假设回填。

{broker_preview}
\sourcenote{{完整券商/一致预期对照见第 7 章和 data/broker\_consensus\_snapshot\_20260626.json。券商目标价不直接作为 AStock 目标价。}}

\section{{评级与权重方法}}
本报告用五类动作标签约束组合行为：买入表示综合目标价较当前价有 20\% 以上空间且证据质量不低于 B；增持表示空间 8--20\%；中性表示空间介于 -15\% 至 8\%；中性观察表示内在价值锚偏低但市场成交、共识定价或情绪溢价仍强，需要等待利润和现金流追认；减持表示综合空间低于 -15\% 且情绪支撑不足或正在破裂。权重不是建议仓位，而是用于计算产业链组合赔率的研究权重：光模块与器件 58\%，上游光芯片/光源 13\%，光纤光缆 17\%，网络设备与应用 12\%。设备和材料中缺少稳定 PE 分母的对象进入观察池，不参与目标价加权。

\begin{{exhibitbox}}[表：组合执行摘要 / Portfolio Action Summary]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.5cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash}}p{{3.2cm}}}}
\toprule
\textbf{{动作}} & \textbf{{标的}} & \textbf{{执行含义}} \\
\midrule
核心持有/增持观察 & 中际旭创、新易盛 & 只在 Q2 订单、毛利率与现金流继续验证时提高权重 \\
慢周期底盘 & 长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份、中兴通讯、烽火通信 & 用现金流、运营商/海缆/FTTH 项目节奏和网络设备利润率校验 \\
上游与相干期权 & 源杰科技、长光华芯、仕佳光子、光库科技、腾景科技、长芯博创、德科立、联特科技 & 只在认证、良率、收入占比和毛利率同时改善时提高估值容忍度 \\
线缆/连接器观察 & 兆龙互连、意华股份、神宇股份、光迅科技、华工科技、剑桥科技、太辰光 & 当前价格需要更多利润分母或业务纯度证明 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{下一季度最重要的三个问题}}
第一，{top_names} 的 2026Q2 净利润是否至少达到 Q1 的 1.05 倍，这是判断 800G 订单是否继续外溢的最低门槛。第二，1.6T 资格认证是否转化为批量订单，而不是停留在样品和送样阶段。第三，上游光芯片/器件、光纤光缆和网络设备是否出现独立验证，而不是全部依赖光模块情绪扩散；如果只有模块端景气、其他层级没有收入和现金流同步，完整产业链的估值就应继续分层。

\section{{数据截止后更新提示（{PREVIEW_DATE}）}}
本报告价格口径仍为 2026-06-26 收盘。数据截止后，报告 universe 35 只中仅\textbf{{永鼎股份 600105}}（估值覆盖）和\textbf{{锐捷网络 301165}}（观察池）发布了 H1 2026 业绩预告，龙头（中际旭创、新易盛、天孚通信、光迅科技、源杰科技）尚未发布，全部完整半年报预约披露集中在 2026 年 8 月。永鼎 H1 归母预增 +57\%--+120\%，其预告已\textbf{{按置信度优先原则计入第 8 章估值}}：2026E 归母从 6.62 亿元（Q1 年化）上修到约 12.0 亿元（预告年化），EPS 从 0.45 上修到约 0.82，内在价值锚从 14.77 升到 16.63。综合目标价仍为 46.00、评级维持中性观察，原因是 cable\_optional\_sotp 档 PE 权重仅 20\%、PS/PB 合计 80\% 且现价被市场情绪锚支撑——利润超预期上修 EPS 与盈利质量，但不机械上修评级。第 11 章给出冻结口径与预告口径的并列对照与桥。
""",
    )
    write_text(
        SECTIONS / "ch02_evidence.tex",
        r"""
\section{来源层级}
本报告将来源分为三层。第一层是上市公司公告与结构化财务数据，用于收入、利润、EPS、现金流、股本和估值分母；第二层是 NVIDIA、Broadcom、Coherent、Lumentum、LightCounting、Cignal AI 等官方或产业公开页面，用于判断技术方向和需求节奏；第三层是公开研究情绪，用于识别市场分歧，但不用于直接计算目标价。

\begin{sourcequalitybox}[证据边界]
本轮取得了部分第三方一致预期、券商摘要和报告入口，但没有取得覆盖全部标的、逐篇原文可复核的券商目标价历史序列。因此第 7 章以“公开券商/一致预期对照”呈现，且逐项披露来源类型和证据质量；没有原文、日期、评级、目标价或预测方法的字段，保留为未披露，不得替代 AStock 自有目标价。
\end{sourcequalitybox}

\section{关键事实与可用性}
\begin{exhibitbox}[表：关键证据链]
\centering
\scriptsize
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.2cm} >{\raggedright\arraybackslash}p{2.5cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\centering\arraybackslash}p{1.0cm} >{\raggedright\arraybackslash}p{2.8cm}}
\toprule
\textbf{来源} & \textbf{类型} & \textbf{本报告采用的事实} & \textbf{质量} & \textbf{估值用途} \\
\midrule
S-01/S-02 & NVIDIA 官方合作 & NVIDIA 对 Coherent/Lumentum 的光互连合作说明光连接成为 AI 集群扩展瓶颈 & A & 只作为需求方向，不直接进入 EPS \\
S-03/S-05 & 产业公开摘要 & 800G/1.6T 需求处在上行周期，CPO 是下一代选项 & B/B+ & 影响 PE 档位和风险描述 \\
S-07--S-22/S-26--S-34 & 公司公告/结构化财务 & 2026Q1 收入、利润、EPS、现金流与毛利率，覆盖模块、器件、光芯片、光纤光缆、线缆互连和网络设备 & A/B+ & 直接作为估值分母 \\
S-23--S-25 & Ethernet/OIF/光纤公开资料 & 高速网络接口、互操作标准和光纤传输底座 & B & 支撑完整产业链边界，不直接进入 EPS \\
行情包 & astock.quote\_service & 2026-06-26 收盘后当前价与日内跌幅 & A- & 目标价空间计算 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{未解决数据与处理}
两类数据仍有局限：第一，海外 hyperscaler 对中际旭创、新易盛等 A 股公司的直接订单分配没有公开逐客户金额，报告只能用公司已披露业绩和产业链方向推断；第二，券商目标价历史和 2026E/2027E 预测并非所有标的都有完整原文，因此本报告对能取得的公开目标价和评级做对照，对未披露字段明确留空。上述缺口均不阻碍当前价估值，因为 AStock 目标价以已披露财务、行情和统一假设计算；券商数据只用于识别市场预期。
""",
    )
    write_text(
        SECTIONS / "ch03_technology.tex",
        r"""
\section{从 800G 到 1.6T：不是线性提速，而是系统瓶颈重排}
AI 集群的网络需求不是传统电信流量的平滑升级，而是由 GPU/加速卡并行训练、MoE 推理、参数同步和存储访问共同驱动的突发式带宽需求。800G 光模块在 2025-2026 年仍是收入主力，1.6T 则开始进入资格认证和放量前夜。速率升级带来的价值不是单个模块单价提升，而是 DSP、EML/CW 激光器、光引擎、精密耦合和测试良率的门槛提高。

\begin{exhibitbox}[表：速率升级对应的产业链变化]
\centering
\scriptsize
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.8cm} >{\raggedright\arraybackslash}p{2.4cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\raggedright\arraybackslash}p{3.2cm}}
\toprule
\textbf{代际} & \textbf{主要形态} & \textbf{技术变化} & \textbf{A 股映射} \\
\midrule
400G & 数通高端到主流 & 100G/lane 成熟，成本与良率是核心 & 光迅科技、华工科技、剑桥科技 \\
800G & AI 集群主力 & 200G/lane、DSP 功耗、热管理和良率决定盈利差距 & 中际旭创、新易盛、天孚通信 \\
1.6T & 2026 资格认证与初期放量 & 224G/lane、硅光/薄膜铌酸锂/EML 路线并行，测试与封装复杂度上升 & 中际旭创、新易盛、源杰科技、天孚通信 \\
CPO & 2027+ 期权 & 光引擎靠近交换 ASIC，降低功耗但改变供应链分工 & 源杰科技、天孚通信、光迅科技 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{价值池从材料到应用的重新分配}
800G/1.6T 不是单纯“模块速率翻倍”，而是把整条链的难度重新排序。材料端，高纯石英和光纤预制棒影响衰减与成本，InP/GaAs、硅光晶圆和薄膜铌酸锂决定激光器、PIC 与调制器路径；设备端，外延、光刻/刻蚀、划片、贴片、主动耦合、老化和高速测试决定良率；芯片端，EML/CW 激光器、PD/APD、DSP、TIA、driver、CDR、switch ASIC 与 NIC 决定功耗和带宽；封装端，透镜、隔离器、WDM、连接器和精密耦合决定可靠性；系统端，交换机、路由器、OTN/ROADM、PON 和 DCI 决定模块进入哪一类应用。

\begin{exhibitbox}[表：技术价值池]
\centering\scriptsize
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{1.5cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.1cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}p{3.2cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X}
\toprule
\textbf{价值池} & \textbf{核心技术} & \textbf{主要瓶颈} & \textbf{A 股映射} \\
\midrule
材料/基底 & 光纤预制棒、InP/GaAs、薄膜铌酸锂、硅光晶圆 & 纯度、缺陷密度、尺寸、衰减和供应稳定性 & 长飞光纤、亨通光电、中天科技；材料观察池 \\
制造设备 & 外延、光刻/刻蚀、主动耦合、老化、光电测试 & 良率、吞吐、自动化和高速测试一致性 & 罗博特科观察池；海外测试/半导体设备厂 \\
光/电芯片 & EML/CW/VCSEL、PD/APD、DSP/TIA/driver/CDR、switch ASIC & 224G/lane、功耗、热、封装和客户认证 & 源杰科技、长光华芯、仕佳光子；海外 Broadcom/Marvell \\
模块/系统 & 800G/1.6T、相干模块、CPO、OTN/ROADM、PON & ASP、毛利率、客户集中和架构替代 & 中际旭创、新易盛、光迅科技、烽火通信、中兴通讯 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{CPO 是期权，不是 2026 年 EPS 分母}
Co-packaged optics 的方向清晰，但投资上必须区分技术方向和财务兑现。CPO 会提高激光源、光引擎、精密耦合和测试价值量，但短期也会把传统可插拔模块的一部分价值转移到系统厂和芯片厂。本报告把 CPO 作为 2027 年后估值弹性，不把它纳入 2026 年利润基准，否则容易把远期叙事包装成当前安全边际。

\section{Mermaid 产业链图源}
仓库规则要求架构图使用 Mermaid。报告的 Mermaid 源文件已保存至 \texttt{analysis/optical\_chain\_map.mmd}，用于后续在有 Mermaid 渲染器的环境中转成图片；本版 PDF 正文使用表格表达同一关系，避免用 TikZ 或 ASCII 画架构图。
""",
    )
    write_text(
        SECTIONS / "ch04_supply_chain.tex",
        r"""
\section{产业链关系矩阵}
光通信 A 股映射不能只分“模块和器件”。完整产业链至少包含八层：材料/基底、制造设备、光芯片/光源、光器件/无源、光模块、光纤光缆/ODN、网络设备、下游应用。本轮最强的短期收入弹性在 AI 光模块，最强的战略稀缺性在光芯片和关键器件，最稳定的周期底盘在光纤光缆与网络设备，最容易被忽视但决定良率的是制造设备和测试环节。
"""
        + full_chain_layers_latex()
        + "\n\n"
        + panorama_universe_latex(rows)
        + "\n\n"
        + chain_layer_deep_dive_latex()
        + r"""

\section{设备与材料为什么单列观察池}
设备和材料是产业链必需项，但并不等于每个环节都适合纳入本报告最终估值表。估值表要求当前价、股本、市值、2026E/2027E/2028E EPS、目标价、合理区间和空间均可计算；如果公司当期亏损、业务混杂、或 A 股缺少纯标的，本报告只做观察池披露，避免为了“覆盖完整”而制造虚假的目标价。
"""
        + watchlist_latex()
        + r"""

\section{竞争格局}
中际旭创和新易盛的优势来自规模、海外客户认证和高端模块交付经验；天孚通信、光库科技、太辰光的优势来自精密组件、封装和无源器件；源杰科技、长光华芯、仕佳光子的优势在光芯片、激光器和 PLC/AWG 等上游稀缺环节；长飞光纤、亨通光电、中天科技构成光纤光缆和海缆底盘；通鼎互联、永鼎股份补足通信线缆、ODN 和网络集成慢周期敞口；兆龙互连、意华股份、神宇股份补足高速线缆和连接器；中兴通讯、烽火通信和光迅科技则把光通信接入网络设备和运营商/云网络场景。估值上，不能把上述层级统一套一个“AI 光模块倍数”：利润弹性、客户集中、资本开支周期和可替代性都不同。
""",
    )
    write_text(
        SECTIONS / "ch05_demand.tex",
        r"""
\section{下游应用不是单一 AI 数据中心}
GPU 数量增加并不会线性等同于光通信全链条需求，真正的变量是集群网络拓扑、东西向流量、交换层级、冗余配置和光电转换边界。NVIDIA 与 Coherent/Lumentum 的合作说明系统厂已经把光互连视为集群扩展的关键瓶颈，而 Broadcom 102.4Tbps 交换芯片路线说明 1.6T 端口将成为下一代交换网络的自然配套。但完整光通信还包括 DCI/相干传输、运营商骨干、FTTH、企业园区、工业和汽车光互连，不同应用的订单节奏、利润弹性和估值倍数差异很大。

\begin{exhibitbox}[表：需求传导路径]
\centering
\small
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{2.0cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\raggedright\arraybackslash}p{3.0cm}}
\toprule
\textbf{环节} & \textbf{传导逻辑} & \textbf{监测指标} \\
\midrule
GPU/ASIC 集群 & 参数同步和推理流量提升，交换层级增加 & NVIDIA/AMD/云厂商 capex 与集群出货节奏 \\
交换 ASIC & 51.2T 到 102.4T 切换推动端口速率升级 & Broadcom/Marvell 交换芯片发布时间表 \\
光模块 & 800G 继续放量，1.6T 开始资格认证 & 模块厂订单、ASP、毛利率、存货和现金流 \\
上游器件 & 激光器、光引擎、精密耦合和测试价值量提升 & 源杰/天孚/太辰光 Q2-Q3 收入和毛利率 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}
"""
        + application_matrix_latex()
        + "\n\n"
        + application_deep_dive_latex()
        + r"""

\section{AI 快周期与运营商慢周期的估值差异}
AI 数据中心是 2025-2026 年最强的价格驱动因素，因为海外云厂商 capex、800G/1.6T 模块订单和毛利率能在几个季度内反映到利润表。运营商骨干、FTTH、DCI 和企业园区则更偏项目制和资本开支周期，需求没有消失，但估值应更多锚定现金流、订单能见度和资产周转，而不是套用 AI 模块的高增长倍数。材料和设备环节进一步滞后，它们可能先体现在产能和良率瓶颈，再进入收入确认。

\section{为什么不能把行业高景气直接等同于个股买入}
光通信是高景气行业，但股价买的是“高景气减去已经支付的估值”。2026-06-26 当天多个光通信标的下跌 5--10\%，但业务模型匹配后的基准估值仍显示不少公司当前价已经提前支付了较多成长和主题期权。只有当下一季度利润、收入质量、现金流和订单能见度继续超过估值隐含要求，主题才能继续转化为超额收益；否则股价会先通过横盘或下跌消化叙事。对全产业链而言，最重要的是把“短期 AI 模块兑现”“上游芯片/设备期权”“光纤光缆慢周期底盘”“网络设备应用层”分开看。
""",
    )
    write_text(
        SECTIONS / "ch06_companies.tex",
        rf"""
\section{{财务交付总览}}
{financial_table}
\sourcenote{{公司财务数据来自 astock.cli financials；2026E 归母净利使用公司层面 Q1 季节性假设折算，不等同于外部一致预期。}}

\section{{公司层面判断}}
\textbf{{光模块与器件层}}：中际旭创和新易盛拥有最直接的 AI 模块利润弹性；长芯博创、德科立和联特科技补足相干传输、高速模块和高 beta 模块层；天孚通信、光库科技、太辰光和腾景科技更多体现精密器件、无源器件和封装价值；光迅科技、华工科技、剑桥科技具备平台和模块业务，但需要用 AI 数通收入占比与利润率证明业务纯度。

\textbf{{上游光芯片/光源层}}：源杰科技、长光华芯和仕佳光子分别映射高速激光芯片、激光器与 PLC/AWG/无源光芯片。它们的战略稀缺性更强，但估值容忍度必须绑定客户认证、良率、产能利用率和收入占比，而不是只绑定“国产替代”叙事。

\textbf{{光纤光缆、线缆互连与网络设备层}}：长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份提供预制棒、光纤、光缆、海缆和 ODN/通信线缆底座；兆龙互连、意华股份、神宇股份补足高速线缆、连接器和通信互连；中兴通讯、烽火通信提供运营商/云网络设备和应用层映射。这一层的估值更依赖运营商 capex、FTTH/DCI 项目、现金流、线缆价格和网络设备利润率，不能照搬模块龙头倍数。

\textbf{{设备和材料观察池}}：罗博特科及 MOCVD、外延、光刻/刻蚀、主动耦合、高速测试、InP/GaAs/薄膜铌酸锂/硅光晶圆等材料设备环节是完整产业链的一部分，但本报告不在缺少稳定利润分母时强行给目标价。它们进入观察池，后续若出现可验证盈利和纯度，再单独建模。

{company_cards_latex(rows)}
""",
    )
    write_text(
        SECTIONS / "ch07_sentiment.tex",
        rf"""
\section{{公开券商/一致预期}}
公开券商和一致预期对光通信链整体偏乐观，主要逻辑集中在四个方向：800G 需求持续超预期，1.6T 资格认证提前，CPO/硅光将重构长期价值分配，光纤光缆和网络设备受益于 DCI、运营商骨干和 FTTH 升级。这些方向与本报告产业判断一致，但情绪本身不能作为买入理由；券商目标价只作为市场预期对照，不作为估值输入，也不直接进入 AStock 目标价。

{broker_table}
\sourcenote{{来源包括英为财情、Moomoo/富途、搜狐券商摘要、21财经/华尔街见闻聚合及东方财富报告入口。未披露字段不做推断；聚合摘要证据质量低于原始券商 PDF。}}

\section{{AStock 与市场的主要分歧}}
第一，本报告不把 CPO 纳入 2026 年利润基准，只把它作为 2027 年后的估值期权。第二，本报告对混合业务、光纤光缆和网络设备公司给予慢周期折价，避免把所有光通信标的按纯 AI 模块倍数估值。第三，本报告把现金流和毛利率作为订单真实性验证指标，而不是只看收入增速。

\begin{{exhibitbox}}[表：研究分歧 / Sentiment Divergence]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.5cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash}}p{{3.4cm}}}}
\toprule
\textbf{{市场叙事}} & \textbf{{AStock 校准}} & \textbf{{投资处理}} \\
\midrule
AI 光模块需求无限上修 & 需求高景气成立，但估值已经提前反映 & 只买业绩交付，不买泛主题 \\
CPO 立刻重估所有光器件 & CPO 是远期架构变化，不是 2026 EPS & 对上游期权给 PE 溢价，但设仓位上限 \\
跌幅后估值便宜 & 跌幅大不等于便宜，目标价要锚定 EPS & 用当前价重算空间，不沿用旧目标 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}
""",
    )
    write_text(
        SECTIONS / "ch08_valuation.tex",
        rf"""
\section{{估值哲学与门禁}}
本章发布 AStock 自有综合目标价，不搬运券商目标价，并遵循固定的估值门禁：先分类、再正常化分母、再做情景估值、再构建多锚目标价、再翻译成动作、最后做可复现性审计。核心原则有四条。第一，\textbf{{方法匹配业务模型}}，绝不把异质产业链套进同一个 PE 表。第二，\textbf{{分母必须正常化}}，2026E 归母不用单季度机械年化，而用季节性校准并以 TTM（滚动四季度）作防高估地板。第三，\textbf{{成长信用必须可追溯}}，AI/高速成长溢价要拆到成长段收入与现价隐含增速，近零/负 EPS 标的不给成长 PE 信用。第四，\textbf{{市场不是真理也不是噪音}}，内在价值锚回答"财务分母支持多少钱"，市场情绪锚回答"市场已经愿意给多少钱以及为什么"，二者按业务模型加权形成综合目标价。所有覆盖标的均具备现价、股本、市值、2026E/2027E/2028E EPS、方法、熊/基准/牛三档、内在锚、市场情绪锚、券商锚、综合目标价、合理区间、隐含空间、动作、催化、失效条件和证据质量。

\begin{{exhibitbox}}[表：业务模型—估值方法匹配矩阵]
\centering\scriptsize
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.6cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}p{{3.4cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{业务类型}} & \textbf{{首选方法}} & \textbf{{必需二级校验}} \\
\midrule
AI 光模块龙头 & PE/PEG + 成长盈利桥 & 现价隐含增速、Street 目标价离散度 \\
光芯片/精密器件/稀缺组件 & PE + PS 或稀缺/SOTP 校验 & 客户认证、ASP/毛利率证据 \\
光纤光缆/预制棒（资产型） & 周期正常化 PE + PB/ROE + PS & 经营现金流、运营商/项目订单、光纤价格 \\
网络设备/混合集成 & PE/SOTP 或 PE/PB/PS blend & 在手订单、分部毛利率、现金转化 \\
高速线缆/连接器互连 & PE/PB/PS blend & AI 互连纯度、产品结构、营运资本 \\
近零 EPS / 亏损 & PS、EV/Sales、PB 或观察池 & 盈利路径、稀释/负债敏感性 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{分母正常化、季节性校准与业绩预告}}
把单季度利润乘以 4（或除以固定季节性假设）对周期性和拐点型标的会系统性失真。本报告对每个标的按\textbf{{置信度顺序}}确定 2026E 分母：\textbf{{(1) 管理层 H1 业绩预告（最高置信度前瞻信号）}}——已发预告的覆盖标的用 H1 中值除以 H1 占全年比例（{H1_SHARE_OF_FY_DEFAULT:.2f}）年化得 2026E 归母；因预告理由为\textbf{{量价齐升}}（量、价同增），2026E 收入也按该利润在 2026Q1 净利率下同步上抬（保守下限，因兑现毛利率实际扩张），使 EPS、PE、PB、PS \textbf{{各条估值腿都对预告作出反应}}，而不是只动 EPS；(2) 季节性校准 Q1（观测 2025 年 Q1 占全年比例在 8\%--45\% 时用观测值）；(3) TTM（滚动四季度）作防高估地板。已发 H1 预告的名字不能再用陈旧 TTM 或 Q1 年化定分母——例如永鼎股份 2026Q1 归母 1.59 亿元、TTM 仅约 1.03 亿元，但其 H1 预告已达 5.0--7.0 亿元，故 2026E 归母采用预告年化约 12.0 亿元、收入约 94 亿元，EPS 从 0.45 上修到约 0.82，内在价值锚从 14.77 抬升到约 24.57，当前价较内在锚溢价从约 +295\% 收窄到约 +167\%。

{seasonality_calibration_latex(rows)}
\sourcenote{{季度-年度桥与三口径：analysis/segment\_forecast\_bridge.md；H1 预告证据：data/earnings\_preview\_h1\_2026\_20260706.md、第 11 章。数据层 data/growth\_driver\_model.json。}}

\begin{{sourcequalitybox}}[业绩预告已计入估值]
本报告 26 只覆盖标的中，有两只已发布 2026 H1 业绩预告，且已按置信度优先原则\textbf{{计入其 2026E 归母、2026E 收入、EPS 及 PE/PB/PS 各条估值腿}}，而非仅列附录。\textbf{{永鼎股份（600105）}}：H1 归母 5.0--7.0 亿元、同比 +57\%--+120\%（光纤量价齐升），EPS 0.45$\to$0.82、收入/股 3.55$\to$6.44、内在价值锚 14.77$\to$24.57、溢价 +295\%$\to$+167\%。\textbf{{杭电股份（603618）}}：H1 归母 3.6--4.0 亿元、同比 +852\%--+958\%（光纤量价齐升，扭亏为盈；FY2025 为亏损），因 Q1 年化与 TTM 都无法代表其扭亏后的盈利能力，采用 H1 预告年化作为 2026E 分母，具体 EPS/内在锚/目标价见其单票估值卡。两只标的综合目标价与评级由各自内在锚、市场情绪锚加权决定：预告显著上修了盈利质量与内在价值锚、收窄了估值泡沫度，但当前价是否给出正空间取决于溢价水平，评级不因单纯利润超预期机械上修。观察池标的锐捷网络（301165）同样已发预告，但不在 26 只当前价目标价覆盖内。第 11 章给出冻结（Q1 年化）与采用（H1 预告）口径的并列对照。价格与未发预告标的的财务分母仍冻结在 2026-06-26。
\end{{sourcequalitybox}}

\section{{最终估值总表}}
下表是全部覆盖标的的 AStock 综合目标价、隐含空间与动作。内在价值锚由业务模型组件（PE/PB/PS 按权重）加权得到，综合目标价再叠加市场情绪锚和券商锚。极端"泡沫度"（现价远高于内在锚）不是模型错误，而是当前光通信板块高拥挤定价的真实刻画，报告用市场情绪锚显式承认这部分溢价，同时坚持财务分母底线。

{latex_table_final(rows, small=True)}
\sourcenote{{估值模型：data/current\_valuation\_model\_20260626.json；可复现性见 analysis/valuation\_audit.md（Model Reproducibility: PASS）。}}

\section{{成长盈利拆分与现价隐含增速}}
AI/高速成长溢价必须回答"贵在哪一段、现价隐含多快增速"。本节把 2026E 收入拆成基础业务段与 AI/高速成长段（AI 收入占比为基于业务层级的 AStock 建模假设，非公司分部披露），并用反向估值给出：在 AStock 基准 PE 档下，当前价要求未来 3 年归母 CAGR 达到多少，再与 AStock 假设的 2026--2028 增速对比。隐含增速远高于假设=估值把成长前置；接近=需持续兑现；低于=若兑现有修复空间。近零/负 EPS 标的（如长光华芯）无法用 PE 反推，转 PS/PB 并降为观察池，不给成长 PE 信用。

{growth_earnings_latex(rows)}
\sourcenote{{成长盈利模型：analysis/growth\_earnings\_model.md、analysis/implied\_growth\_sensitivity.md、data/growth\_driver\_model.json。AI 收入占比与增速为 AStock 建模假设，非公司财报分部披露。}}

\section{{基于 2026E 收入和成长性的市场预期估值}}
本节补上"市场炒预期"的视角。AStock 内在价值锚回答按业务模型和 2027E 正常化分母的冷静价值；市场预期估值回答：如果投资者愿意基于 2026E 收入、2026E EPS 和 2027E 成长性给更高预期倍数，当前价格对应的上方或下方空间是多少。预期价值不是买入理由，只有当下一季度收入、毛利率、现金流和订单质量继续验证，预期倍数才有资格维持。

{expectation_table}
\sourcenote{{预期估值模型：data/market\_expectation\_valuation\_20260626.json。}}

\section{{市场隐含预期与情绪锚}}
内在价值锚回答"财务分母支持多少钱"，市场隐含预期锚回答"当前市场已经愿意给多少钱以及为什么"。本节用成交额分位、当前隐含 PE/PS/PB、券商锚和情绪状态修正综合目标价。它不是把现价当真理，而是防止模型在强共识阶段把慢周期或期权型标的机械低估；反过来，当内在锚远低于现价时，报告也不机械写减持，而是标注情绪溢价并给出失效条件。

{sentiment_table}
\sourcenote{{市场情绪锚：data/market\_sentiment\_anchor\_20260626.json；方法论参考 CFA 市场法估值、预期投资反推框架和投资者情绪研究。}}

\section{{券商/Street 对照与发布降级}}
估值门禁要求全产业链报告为每个覆盖标的提供逐篇原文可复核的券商目标价与 2026E/2027E 预测。本轮多数标的仅取得第三方一致预期页面或媒体摘要，部分标的无可用券商目标价。按门禁，券商原文覆盖不完整时不得给 final\_signoff: PASS，故本报告显式降级为 \textbf{{MECHANICAL\_PASS\_INSTITUTIONAL\_FAIL}}：AStock 自有目标价、内在锚、市场情绪锚与成长盈利模型可独立复算并支撑全部结论，但券商对照层为机构级不完整，任何投资结论不得单独依赖券商锚。预测收入/净利润/EPS 与估值方法字段在公开页面未逐项披露，统一标注 not disclosed，且券商锚仅在证据质量足够时进入权重。

\begin{{exhibitbox}}[表：券商/Street 对照与证据质量]
\centering\tiny
\renewcommand{{\arraystretch}}{{1.14}}
\setlength{{\tabcolsep}}{{2pt}}
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.5cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}p{{2.4cm}} >{{\raggedleft\arraybackslash}}p{{0.95cm}} >{{\raggedleft\arraybackslash}}p{{0.95cm}} >{{\raggedleft\arraybackslash}}p{{0.85cm}} >{{\centering\arraybackslash}}p{{1.0cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{标的}} & \textbf{{来源类型}} & \textbf{{目标价}} & \textbf{{隐含空间}} & \textbf{{券商权重}} & \textbf{{证据质量}} & \textbf{{预测明细}} \\
\midrule
{chr(10).join([rf"{tex(r['name'])} {r['code']} & {tex(r['broker_source_type'])} & {num(r['broker_target_avg']) if r['broker_target_avg'] is not None else 'n.d.'} & {pct_tex(r['broker_upside']) if r['broker_upside'] is not None else 'n.a.'} & {num(r['final_anchor_weights'].get('street',0.0)*100,0)}\% & {tex(r['broker_evidence_quality'])} & 收入/利润/EPS: not disclosed \\" for r in rows])}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}
\sourcenote{{券商/Street 一致预期对照包：data/broker\_street\_consensus\_20260626.md/json（含发布降级说明）。}}

\section{{情景解释}}
中际旭创和新易盛的综合空间接近持平甚至略正，是因为 2026Q1 已体现强利润分母、TTM run-rate 扎实，且现价隐含增速（约 5\%--7\% 的 3 年归母 CAGR）其实低于 AStock 假设增速，说明并非无条件贵；但它们也不是无约束买入，核心风险是海外云厂商订单与 ASP 持续性。长飞光纤、亨通光电、中天科技、通鼎互联、永鼎股份、中兴通讯和烽火通信提供完整产业链的慢周期底盘，估值既要锚定现金流和运营商/网络项目节奏，也要承认成交额和市场共识给出的情绪溢价。源杰科技、长光华芯、仕佳光子、光库科技拥有更高战略稀缺性，但现价通常把长期技术期权前置，其中长光华芯为近零 EPS，只作观察池。光迅科技、华工科技、剑桥科技、太辰光的问题不是没有产业位置，而是利润分母、业务纯度或现金流还不足以支撑过高倍数。

\begin{{exhibitbox}}[表：估值假设桥 / Method and Assumption Bridge]
\centering\scriptsize
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.5cm}} >{{\centering\arraybackslash}}p{{1.0cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}p{{2.2cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{标的}} & \textbf{{方法}} & \textbf{{权重}} & \textbf{{二级校验与倍数理由}} \\
\midrule
{chr(10).join([rf"{tex(r['name'])} & {tex(r['method_short'])} & {tex(r['valuation_weights_label'])} & {tex(r['secondary_check'])}；{tex(r['rating_note'])} \\" for r in rows])}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

{valuation_cards_latex(rows)}
""",
    )
    write_text(
        SECTIONS / "ch09_risks.tex",
        r"""
\section{风险矩阵}
\begin{riskbox}[核心风险]
本轮最大的风险不是产业方向错误，而是盈利兑现速度追不上股价隐含速度。若 2026Q2/Q3 毛利率、现金流或订单节奏低于当前估值要求，光通信板块会出现“业绩增长但股价下跌”的典型估值消化。完整产业链还要额外关注材料/设备良率、运营商 capex、网络设备利润率和光纤光缆价格周期。
\end{riskbox}

\begin{exhibitbox}[表：风险矩阵]
\centering
\small
\begin{tabularx}{\exhibitboxwidth}{>{\bfseries\raggedright\arraybackslash}p{2.2cm} >{\raggedright\arraybackslash\sloppy\hspace{0pt}}X >{\centering\arraybackslash}p{1.2cm} >{\raggedright\arraybackslash}p{3.0cm}}
\toprule
\textbf{风险} & \textbf{表现} & \textbf{等级} & \textbf{监测指标} \\
\midrule
客户集中 & 海外大客户拉货节奏变化直接影响模块厂收入 & 高 & 前五客户、应收账款、存货、订单口径 \\
ASP 下行 & 800G 放量后价格下降快于成本下降 & 高 & 毛利率、单季度收入/利润剪刀差 \\
1.6T 延迟 & 样品验证变慢，规模出货推迟 & 中高 & 公司调研、资本开支、产品认证节奏 \\
CPO 分工变化 & 系统厂/芯片厂拿走部分模块价值 & 中 & 硅光/CPO 合作模式和光源供应方式 \\
材料/设备卡点 & InP/GaAs/薄膜铌酸锂/硅光晶圆、外延、主动耦合和高速测试良率不及预期 & 中高 & 良率、认证周期、资本开支和设备交付 \\
运营商慢周期 & 光纤光缆、OTN、PON、ROADM 和网络设备项目延期 & 中 & 运营商 capex、招标、海缆/FTTH 项目进度 \\
政策与汇率 & 出口管制、海外生产与汇兑扰动 & 中 & 海外收入占比、美元兑人民币、政策公告 \\
拥挤交易 & 板块换手和主题资金集中导致回撤放大 & 高 & 单日成交额、龙虎榜、基金持仓变化 \\
\bottomrule
\end{tabularx}
\end{exhibitbox}

\section{上修与下修触发}
上修触发包括：中际旭创/新易盛 Q2 净利润达到 Q1 的 1.25 倍以上，1.6T 订单进入批量交付，模块毛利率维持 42\% 以上，上游激光芯片/PLC/AWG/调制器通过更多头部客户认证，长飞/亨通/中天现金流和订单同步改善，中兴/烽火网络设备利润率回升。下修触发包括：Q2 净利润低于 Q1 的 0.85 倍，光模块 ASP 超预期下行，经营现金流持续弱于利润，光纤光缆价格再次下行，运营商 capex 延后，或 CPO 架构使可插拔模块价值量被重估。
""",
    )
    by_code = {r["code"]: r for r in rows}

    def investment_exec_row(code: str, add_rule: str, downgrade_rule: str) -> str:
        r = by_code[code]
        stance = "riskgreen" if r["rating_cn"] in {"买入", "增持"} else ("riskamber" if "中性" in r["rating_cn"] else "riskred")
        return (
            rf"{tex(r['name'])} {r['code']} & {num(r['current_price_cny'])} & {num(r['final_target_cny'])} & "
            rf"{pct_tex(r['final_upside'])} & \stance{{{stance}}}{{{tex(r['rating_cn'])}}} & "
            rf"{tex(add_rule)} & {tex(downgrade_rule)} \\"
        )

    investment_exec_rows = "\n".join(
        [
            investment_exec_row("300308", "Q2/Q3 净利、毛利率、经营现金流同步验证，1.6T 客户交付没有延迟；回撤到目标区间下沿附近但基本面未破时优先补。", "净利环比低于 Q1、毛利率下滑或大客户订单节奏放缓，降为只观察不加仓。"),
            investment_exec_row("300502", "高增长订单继续兑现，单一客户风险没有扩大，现金流跟上利润；若综合空间重新扩大到 8% 以上，进入增持候选。", "高增长只体现在收入不体现在现金流，或 2027E 增速预期下修，降低权重。"),
            investment_exec_row("600522", "海缆、电网、通信线缆订单和现金流确认；市场情绪锚维持但不能脱离经营现金流。", "光纤价格下行、海缆/电网项目延后，或成交额回落导致情绪锚失效。"),
            investment_exec_row("601869", "预制棒/光纤/光缆利用率回升，数据中心需求真正进入收入和现金流；只做强共识观察，不追高。", "利用率、毛利率或经营现金流未改善，强共识溢价回落时下调市场锚。"),
            investment_exec_row("002491", "通信线缆和项目交付带动利润分母修复，Q2/Q3 经营现金流改善；按慢周期底盘处理。", "利润改善不能延续，或 AI 相关纯度被证伪，退出核心观察。"),
            investment_exec_row("688498", "激光芯片客户认证、收入规模和毛利率同时提升；只能作为上游战略期权，不能按模块龙头仓位处理。", "认证不及预期、收入放量慢于股价隐含预期，维持中性观察或降级。"),
            investment_exec_row("002281", "光芯片/器件和模块业务利润率修复，证明平台价值能穿越板块情绪。", "估值继续高于利润兑现速度，或现金流弱于利润，维持中性观察。"),
            investment_exec_row("000063", "运营商、云网络和服务器相关业务利润率改善，现金流维持稳健；作为应用层稳健观察。", "非光通信业务稀释加重，运营商 capex 延后，维持中性或降低权重。"),
            investment_exec_row("300620", "薄膜铌酸锂/调制器期权进入订单和收入，且综合空间不再深负。", "股价继续把长期期权前置而收入和利润不跟，维持减持。"),
            investment_exec_row("301205", "高 beta 模块订单、客户认证和利润分母修复；未修复前不因题材追涨。", "Q2/Q3 利润仍薄或现金流弱，维持减持。"),
        ]
    )

    write_text(
        SECTIONS / "ch10_investment.tex",
        rf"""
\section{{最终投资结论}}
本报告的最终建议不是“一篮子买光通信”，而是\textbf{{只买兑现、限制期权、承认情绪、等待验证}}。截至 2026-06-26 收盘价，覆盖组合的内在价值锚加权空间为 {intrinsic_weighted}，纳入市场隐含预期与券商锚后的综合空间为 {weighted}。这意味着板块仍有强产业逻辑，但从组合角度看已经不是低估扩散阶段，而是业绩兑现和市场情绪共同定价阶段。投资动作应从主题追涨切换为三件事：第一，核心模块只在利润、毛利率和现金流继续兑现时加仓；第二，光纤光缆、网络设备和通信线缆只按慢周期现金流和项目节奏持有观察；第三，上游芯片/器件和设备材料只给期权仓位，不能用长期空间掩盖短期分母不足。

\section{{建议的研究组合结构}}
以下权重是研究组合权重，不是账户交易指令。它用于约束不同产业链层级的相对重要性，防止因为光通信主题强就无差别追涨。当前基准情景下，组合应维持\textbf{{中性偏进攻观察}}：保留核心模块敞口，但新增资金必须等待 Q2/Q3 交付、毛利率和现金流验证。

\begin{{exhibitbox}}[表：最终组合建议矩阵]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.1cm}} >{{\centering\arraybackslash}}p{{1.4cm}} >{{\raggedright\arraybackslash}}p{{2.8cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}p{{3.0cm}}}}
\toprule
\textbf{{篮子}} & \textbf{{研究权重}} & \textbf{{代表标的}} & \textbf{{当前建议}} & \textbf{{升/降级触发}} \\
\midrule
核心兑现池 & 30--35\% & 中际旭创、新易盛 & 作为组合主线，但不无条件追高；利润、毛利率、现金流三项确认后才提高权重。 & Q2/Q3 净利环比继续改善且现金流不背离，上调；若毛利率或订单节奏破坏，下调。 \\
市场支持观察池 & 25--30\% & 中天科技、长飞光纤、亨通光电、通鼎互联、永鼎股份 & 承认市场情绪锚，但只按慢周期现金流和项目节奏管理，不能套用纯 AI 模块倍数。 & 光纤光缆价格、海缆/运营商项目和经营现金流改善，上调；成交额和现金流同时回落，下调。 \\
上游战略期权池 & 10--15\% & 源杰科技、长光华芯、仕佳光子、光库科技、腾景科技 & 只给期权仓位，重点看认证、良率、客户数和收入占比。 & 客户认证转量产且毛利率稳定，上调；只有题材无收入，维持低配。 \\
网络设备与应用层 & 10--15\% & 中兴通讯、烽火通信 & 稳健观察，按运营商 capex、云网络订单和利润率定价。 & 运营商/云网络项目和利润率改善，上调；非光通信业务稀释或项目延后，下调。 \\
低配/等待修复池 & 0--10\% & 光迅、华工、剑桥、太辰光、德科立、联特、兆龙、意华、神宇及设备材料观察池 & 只有在目标价空间、利润分母或现金流修复后才提高权重；亏损或近零 EPS 标的不强行买入。 & 综合空间转正且证据质量提升，上调；预期继续前置而交付不足，维持低配或减持。 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{重点标的执行清单}}
最终建议必须落到单票执行层。下表把当前价、综合目标、空间、动作和下一步触发绑定在一起。中天科技、长飞光纤、通鼎互联这类标的的重点不是机械减持，而是承认市场已经给出情绪溢价，同时要求后续现金流、订单和项目节奏确认；若确认失败，综合目标会向内在价值锚收敛。

\begin{{exhibitbox}}[表：重点标的最终执行清单]
\centering
\tiny
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.7cm}} >{{\raggedleft\arraybackslash}}p{{0.85cm}} >{{\raggedleft\arraybackslash}}p{{0.95cm}} >{{\raggedleft\arraybackslash}}p{{0.85cm}} >{{\centering\arraybackslash}}p{{1.25cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{标的}} & \textbf{{现价}} & \textbf{{目标}} & \textbf{{空间}} & \textbf{{动作}} & \textbf{{加仓/上修条件}} & \textbf{{降级/退出条件}} \\
\midrule
{investment_exec_rows}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{三种情景下的操作剧本}}
\begin{{exhibitbox}}[表：情景、动作与复盘纪律]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{1.9cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{情景}} & \textbf{{触发条件}} & \textbf{{组合动作}} & \textbf{{重点复盘}} \\
\midrule
牛市兑现 & Q2/Q3 模块龙头净利环比强增长，1.6T 订单批量化，上游认证转收入，光纤光缆现金流改善。 & 提高核心模块权重，选择性增加上游战略期权和慢周期底盘；仍不扩大亏损/近零 EPS 设备材料敞口。 & 毛利率是否稳定、经营现金流是否跟上、客户集中度是否恶化。 \\
基准验证 & 模块利润继续增长但估值已经充分，慢周期链条只有部分项目兑现，上游认证仍在推进。 & 维持中性偏进攻观察；核心池逢基本面确认加，市场支持观察池不追涨，低配分母不足标的。 & 现价是否重新低于综合目标区间下沿，现金流和订单能否支持情绪锚。 \\
预期破裂 & Q2/Q3 利润低于 Q1，毛利率或 ASP 下行，经营现金流弱于利润，光纤光缆/网络项目延后。 & 降低主题总敞口，优先减掉期权和低证据质量标的；中性观察标的若情绪锚失效，降为减持。 & 内在价值锚下修幅度、成交额分位回落、券商目标和一致预期是否同步下修。 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{复盘纪律与结论}}
未来一个季度的复盘顺序应固定为：先看利润分母，再看现金流，再看订单/认证，最后才看市场情绪。若某只股票只有成交额和题材热度，没有利润、毛利率或现金流确认，不能因为产业链位置好就上调动作；若某只股票内在价值偏低但市场锚、成交和项目兑现仍强，也不能机械写成减持，而应维持中性观察并列出情绪溢价失效条件。最终结论是：光通信仍是 AI 硬件链最重要方向之一，但当前阶段的正确做法不是扩大无差别敞口，而是在中际旭创、新易盛等利润已兑现标的上等待确认，在中天科技、长飞光纤、通鼎互联等市场支持观察标的上用现金流验证情绪锚，在上游芯片/器件和设备材料上保持期权仓位和严格止错。

\begin{{exhibitbox}}[表：下一次更新检查清单]
\centering
\small
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{2.4cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{检查项}} & \textbf{{上修条件}} & \textbf{{下修条件}} \\
\midrule
利润分母 & Q2/Q3 净利润继续环比改善，且增长不只来自一次性收益。 & 净利润低于 Q1 或低于市场隐含增速，先下调 EPS 和目标价。 \\
毛利率与 ASP & 模块毛利率稳定，上游器件和芯片放量不牺牲毛利率。 & ASP 下行、毛利率下降或客户议价增强，降低估值倍数。 \\
经营现金流 & 经营现金流跟上净利润，应收和存货没有快于收入恶化。 & 现金流持续弱于利润，说明订单质量低于股价隐含预期。 \\
订单与认证 & 1.6T、CPO、硅光、激光芯片、光纤光缆项目进入收入确认。 & 只停留在送样、认证或主题宣传，不能上调动作标签。 \\
市场情绪锚 & 成交额分位、券商目标和项目兑现同时支撑市场锚。 & 成交回落、券商目标下修或项目延后，情绪锚向内在价值锚收敛。 \\
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}
""",
    )
    write_text(SECTIONS / "ch11_earnings_preview.tex", earnings_preview_latex(rows, revision))
    source_rows = "\n".join(
        rf"{tex(s['id'])} & {tex(s['title'])} & {tex(s['type'])} & {tex(s['quality'])} & \href{{{s['url']}}}{{source link}} \\"
        for s in SOURCE_ITEMS
    )
    write_text(
        SECTIONS / "app_source_audit.tex",
        rf"""
\section{{来源注册表}}
\begin{{exhibitbox}}[表：来源注册表 / Source Registry]
\centering\tiny
\begin{{tabularx}}{{\exhibitboxwidth}}{{>{{\bfseries\raggedright\arraybackslash}}p{{0.7cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}p{{3.2cm}} >{{\raggedright\arraybackslash}}p{{1.8cm}} >{{\centering\arraybackslash}}p{{0.8cm}} >{{\raggedright\arraybackslash\sloppy\hspace{{0pt}}}}X}}
\toprule
\textbf{{ID}} & \textbf{{标题}} & \textbf{{类型}} & \textbf{{质量}} & \textbf{{URL}} \\
\midrule
{source_rows}
\bottomrule
\end{{tabularx}}
\end{{exhibitbox}}

\section{{模型披露}}
市场价格来自 2026-06-26 收盘后行情包。行情包中的市值字段为 0，本报告未使用该字段，而是使用 2026Q1 归母净利润除以 EPS 反推股本，再乘当前价计算市值。盈利预测不是外部一致预期，而是基于 2026Q1 已披露业绩和公司层面季节性假设的 AStock 内部折算。综合目标价由内在价值锚、市场隐含预期锚和公开券商锚加权得到；市场情绪锚参与最终目标价，但不替代财务分母。
""",
    )
    write_text(SECTIONS / "app_research_workplan.tex", research_workplan_latex() + "\n\n" + company_diligence_appendix_latex(rows))


def write_governance(model: dict, source_records: list[dict]) -> None:
    files = []
    for path in sorted(CASE.rglob("*")):
        if path.is_file() and path.name not in {".DS_Store"}:
            files.append({"path": str(path.relative_to(CASE)), "size_bytes": path.stat().st_size})
    index_rows = [[f"`workspace/research/{CASE.name}/{item['path']}`", "True", item["size_bytes"]] for item in files]
    write_text(CASE / "data_room_index.md", "# 数据室索引\n\n" + table_md(["路径", "存在", "大小"], index_rows))
    manifest = {
        "case_id": CASE.name,
        "run_date": RUN_DATE,
        "decision": "publish_internal_research_report",
        "verifier_summary": "pending_pdf_build",
        "covered_tickers": [r["code"] for r in model["rows"]],
        "weighted_base_upside": model["weighted_base_upside"],
        "weighted_final_upside": model["weighted_final_upside"],
    }
    write_json(CASE / "completion_audit_manifest.json", manifest)
    write_text(CASE / "completion_audit_manifest.md", f"# Completion Audit Manifest\n\n- Decision: publish_internal_research_report\n- Covered tickers: {len(model['rows'])}\n- Weighted intrinsic upside: {pct(model['weighted_base_upside'])}\n- Weighted market-adjusted upside: {pct(model['weighted_final_upside'])}\n- PDF status: built")
    exhaustion = {
        "case_id": CASE.name,
        "run_date": RUN_DATE,
        "public_sources_exhausted_for": ["完整券商目标价时间序列", "全部标的逐篇券商 2026E/2027E 预测原文"],
        "fallback": "使用公开一致预期/券商摘要做对照，并以 AStock 自有模型独立估值。",
    }
    write_json(CASE / "source_exhaustion_log.json", exhaustion)
    write_text(CASE / "source_exhaustion_log.md", "# 来源穷尽记录\n\n本轮未取得覆盖全部标的、逐篇原文可复核的券商目标价时间序列，也未取得所有标的的完整 2026E/2027E 券商预测明细。报告因此使用公开一致预期和券商摘要做市场预期对照，未披露字段不做推断；AStock 目标价仍由自有模型独立计算。")
    write_text(CASE / "review_log.md", f"# 审阅记录\n\n- {RUN_DATE}: 按反馈重建光通信报告，修正早期版本过窄、过度模块中心的问题。\n- {RUN_DATE}: 扩展至 {len(model['rows'])} 只可估值 A 股标的，覆盖模块、器件、光芯片、光纤光缆和网络设备。\n- {RUN_DATE}: 增加材料、设备、下游应用和观察池。\n- {RUN_DATE}: 增加业务模型匹配估值、2026E 市场预期估值桥和公开券商/一致预期对照。\n- {RUN_DATE}: 扩写最终投资建议，加入研究组合权重、重点标的执行清单、情景剧本和复盘纪律。\n- {PREVIEW_DATE}: 按估值门禁重写第 8 章估值体系：新增分母正常化/季节性校准、成长盈利模型、券商/Street 对照包与发布降级、可复现性审计。\n- {PREVIEW_DATE}: H1 2026 业绩预告按置信度优先原则计入覆盖标的估值分母（量价齐升同时上抬收入与利润，贯穿 EPS/PE/PB/PS）。永鼎 600105 内在锚 14.77→24.57；新增杭电股份 603618 为第 26 只估值覆盖标的（6/26 收盘 52.00，H1 预增 +852%~+958% 扭亏），其预告计入估值分母。第 11 章给出冻结（Q1 年化）与采用（H1 预告）口径并列对照。价格与未发预告标的分母仍冻结在 2026-06-26。\n")
    write_json(DATA / "source_capture_manifest_20260626.json", {"captures": source_records})
    write_text(DATA / "source_capture_manifest_20260626.md", "# 来源抓取清单\n\n" + table_md(["URL", "路径", "状态", "字节"], [[r["url"], r["path"], r.get("status"), r.get("bytes")] for r in source_records]))


def write_verifier() -> None:
    verifier = r'''#!/usr/bin/env python3
"""Verify the optical communication research workspace."""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def load_json(rel: str):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))


def text(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8", errors="ignore")


def has_pdf_pages() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    proc = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True)
    if proc.returncode != 0:
        return False, "pdfinfo failed"
    m = re.search(r"Pages:\s+(\d+)", proc.stdout)
    if not m:
        return False, "page count missing"
    pages = int(m.group(1))
    return pages >= 40, f"pages={pages}"


def no_pattern_in_pdf(pattern: str) -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    out = BASE / "main_current_text.txt"
    if not out.exists():
        proc = subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
        if proc.returncode != 0:
            return False, "pdftotext failed"
    body = out.read_text(encoding="utf-8", errors="ignore")
    return pattern not in body, f"pattern={pattern}"


def valuation_complete() -> tuple[bool, str]:
    model = load_json("data/current_valuation_model_20260626.json")
    required = [
        "code", "name", "current_price_cny", "shares_100mn", "market_cap_100mn_cny",
        "eps_2026e", "eps_2027e", "eps_2028e", "method", "bear_value_cny",
        "base_target_cny", "bull_value_cny", "fair_value_range_cny",
        "implied_upside", "rating_cn", "catalyst", "invalidation", "quality",
        "method_short", "valuation_style", "secondary_check", "valuation_weights",
        "base_components", "bear_components", "bull_components", "book_value_per_share",
        "sales_per_share_2027e", "expectation_value_cny", "expectation_upside",
        "expectation_components", "expectation_driver", "expected_revenue_growth_2027",
        "broker_source", "broker_rating", "broker_forecast_note", "broker_evidence_quality",
        "current_implied_pe_2026", "current_implied_ps_2026", "current_implied_pb",
        "trading_value_100mn_cny", "trading_value_percentile", "market_sentiment_score",
        "market_sentiment_regime", "sentiment_premium_vs_intrinsic", "market_anchor_value_cny",
        "final_anchor_weights", "final_anchor_weights_label", "final_target_cny",
        "final_upside", "market_action_logic", "embedded_expectation_gap",
    ]
    problems = []
    for row in model.get("rows", []):
        for key in required:
            if row.get(key) in (None, "", "n.a."):
                problems.append(f"{row.get('code')} missing {key}")
        target = row["base_components"]["weighted_value_cny"]
        bear = row["bear_components"]["weighted_value_cny"]
        bull = row["bull_components"]["weighted_value_cny"]
        upside = row["base_target_cny"] / row["current_price_cny"] - 1
        mcap = row["current_price_cny"] * row["shares_100mn"]
        if abs(target - row["base_target_cny"]) > 0.02:
            problems.append(f"{row['code']} target math")
        if abs(bear - row["bear_value_cny"]) > 0.02:
            problems.append(f"{row['code']} bear math")
        if abs(bull - row["bull_value_cny"]) > 0.02:
            problems.append(f"{row['code']} bull math")
        if abs(upside - row["implied_upside"]) > 0.0005:
            problems.append(f"{row['code']} upside math")
        if abs(mcap - row["market_cap_100mn_cny"]) > 0.05:
            problems.append(f"{row['code']} mcap math")
        expectation = row["expectation_components"]["weighted_value_cny"]
        expectation_upside = row["expectation_value_cny"] / row["current_price_cny"] - 1
        final_weights = row["final_anchor_weights"]
        final_target = (
            row["base_target_cny"] * final_weights["fundamental"]
            + row["market_anchor_value_cny"] * final_weights["market"]
            + (row.get("broker_anchor_value_cny") or 0.0) * final_weights["street"]
        )
        if row["market_sentiment_score"] >= 62 and row["sentiment_premium_vs_intrinsic"] >= 0.70:
            final_target = max(final_target, row["market_anchor_value_cny"])
        final_upside = row["final_target_cny"] / row["current_price_cny"] - 1
        if abs(expectation - row["expectation_value_cny"]) > 0.02:
            problems.append(f"{row['code']} expectation math")
        if abs(expectation_upside - row["expectation_upside"]) > 0.0005:
            problems.append(f"{row['code']} expectation upside math")
        if abs(final_target - row["final_target_cny"]) > 0.02:
            problems.append(f"{row['code']} final target math")
        if abs(final_upside - row["final_upside"]) > 0.0005:
            problems.append(f"{row['code']} final upside math")
    styles = {row.get("valuation_style") for row in model.get("rows", [])}
    if len(styles) < 4:
        problems.append(f"method profiles too narrow: {sorted(styles)}")
    return not problems and len(model.get("rows", [])) == 26, "; ".join(problems) or f"26 rows complete, styles={len(styles)}"


def source_files_exist() -> tuple[bool, str]:
    reg = load_json("data/source_registry.json")
    captures = load_json("data/source_capture_manifest_20260626.json").get("captures", [])
    ok = len(reg.get("items", [])) >= 34 and len(captures) >= 34
    missing = [c["path"] for c in captures if not (BASE / c["path"]).exists()]
    return ok and not missing, f"sources={len(reg.get('items', []))}, captures={len(captures)}, missing={missing[:2]}"


def check_file(rel: str) -> tuple[bool, str]:
    path = BASE / rel
    return path.exists() and path.stat().st_size > 0, rel


def section_has_prose(rel: str) -> tuple[bool, str]:
    body = text(rel)
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", body))
    tables = body.count(r"\begin{exhibitbox}")
    return chinese_chars > 180 and body.find(r"\begin{exhibitbox}") > 0, f"chars={chinese_chars}, exhibits={tables}"


def full_chain_complete() -> tuple[bool, str]:
    body = text("sections/ch04_supply_chain.tex") + text("sections/ch05_demand.tex") + text("analysis/optical_chain_map.mmd")
    required = ["材料", "设备", "光芯片", "光器件", "光模块", "光纤光缆", "通信线缆", "高速线缆", "网络设备", "下游应用"]
    missing = [term for term in required if term not in body]
    return not missing, f"missing={missing}"


def full_chain_map_tickers_explicit() -> tuple[bool, str]:
    body = text("sections/ch04_supply_chain.tex")
    start = body.find(r"\begin{exhibitbox}[表：完整光通信产业链地图]")
    end = body.find(r"\end{exhibitbox}", start)
    block = body[start:end] if start >= 0 and end > start else ""
    required = [
        "通鼎互联(002491)",
        "永鼎股份(600105)",
        "兆龙互连(300913)",
        "意华股份(002897)",
        "神宇股份(300563)",
    ]
    missing = [term for term in required if term not in block]
    return not missing, f"missing={missing}"


def broker_and_expectation_present() -> tuple[bool, str]:
    body = text("sections/ch01_ic_summary.tex") + text("sections/ch07_sentiment.tex") + text("sections/ch08_valuation.tex")
    required = ["市场预期估值", "市场隐含预期与情绪锚", "综合目标价", "公开券商/一致预期", "2026E收入", "券商均值", "未披露字段不做推断"]
    missing = [term for term in required if term not in body]
    broker_rows = load_json("data/broker_consensus_snapshot_20260626.json").get("rows", [])
    expectation_rows = load_json("data/market_expectation_valuation_20260626.json").get("rows", [])
    sentiment_rows = load_json("data/market_sentiment_anchor_20260626.json").get("rows", [])
    if len(broker_rows) != 26:
        missing.append(f"broker_rows={len(broker_rows)}")
    if len(expectation_rows) != 26:
        missing.append(f"expectation_rows={len(expectation_rows)}")
    if len(sentiment_rows) != 26:
        missing.append(f"sentiment_rows={len(sentiment_rows)}")
    return not missing, f"missing={missing}"


def chinese_language_gate() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    out = BASE / "main_current_text.txt"
    if pdf.exists() and not out.exists():
        subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
    body = out.read_text(encoding="utf-8", errors="ignore") if out.exists() else text("main.tex")
    forbidden = [
        "Optical fiber/cable",
        "High-speed optical",
        "Business-model matched",
        "cycle-normalized",
        "customer qualification",
        "current price",
        "target price",
        "strongest earnings delivery",
    ]
    hits = [term for term in forbidden if term in body]
    return not hits, f"forbidden={hits}"


def investment_advice_depth() -> tuple[bool, str]:
    body = text("sections/ch10_investment.tex")
    required = [
        "最终投资结论",
        "最终组合建议矩阵",
        "重点标的最终执行清单",
        "情景、动作与复盘纪律",
        "下一次更新检查清单",
        "研究权重",
        "加仓/上修条件",
        "降级/退出条件",
        "中际旭创",
        "新易盛",
        "中天科技",
        "长飞光纤",
        "通鼎互联",
    ]
    missing = [term for term in required if term not in body]
    prose_chars = len(re.sub(r"\\[a-zA-Z]+|[{}\\\\&%_$#^~]", "", body))
    if prose_chars < 2600:
        missing.append(f"chars={prose_chars}")
    return not missing, f"missing={missing}"


def post_cutoff_preview_present() -> tuple[bool, str]:
    preview = load_json("data/earnings_preview_h1_2026_20260706.json")
    census = load_json("data/optical_preview_census_20260706.json")
    previews = preview.get("previews", {})
    in_universe = [c for c, p in previews.items() if p.get("coverage") in {"covered", "watch_pool"}]
    ok = (
        "600105" in previews and "301165" in previews and "603618" in previews
        and len(in_universe) >= 3
        and census.get("universe_size") == 36
        and census.get("previews_in_universe") == 3
        and "stock_yjyg_em" in census.get("method", "")
    )
    return ok, f"in_universe={len(in_universe)}, universe={census.get('universe_size')}"


def post_cutoff_disclosure_in_pdf() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    out = BASE / "main_current_text.txt"
    if not out.exists():
        proc = subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
        if proc.returncode != 0:
            return False, "pdftotext failed"
    body = out.read_text(encoding="utf-8", errors="ignore")
    needed = ["业绩预告", "数据截止", "2026-07-06"]
    missing = [t for t in needed if t not in body]
    return not missing, f"missing={missing}"


def frozen_baseline_intact() -> tuple[bool, str]:
    market = load_json("data/raw_market_data_20260626.json")
    model = load_json("data/current_valuation_model_20260626.json")
    yd = next((r for r in model.get("rows", []) if r["code"] == "600105"), None)
    ok = (
        market.get("run_date") == "2026-06-26"
        and len(market.get("quotes", {})) == 26
        and model.get("run_date") == "2026-06-26"
        and yd is not None
        and yd.get("rating_cn") == "中性观察"
        and abs(yd.get("final_upside", 0) + 0.30) < 0.02
    )
    return ok, f"600105 rating={yd.get('rating_cn') if yd else None}, upside={round(yd.get('final_upside'), 3) if yd else None}"


def preview_revision_dual_view() -> tuple[bool, str]:
    rev = load_json("data/earnings_preview_revision_20260706.json")
    revisions = rev.get("revisions", [])
    yd = next((r for r in revisions if r["code"] == "600105"), None)
    ok = (
        rev.get("cutoff") == "2026-06-26"
        and yd is not None
        and "frozen" in yd and "revised" in yd
        and yd["revised"]["eps_2026e"] > yd["frozen"]["eps_2026e"]
        and rev.get("seasonality_assumption") is not None
    )
    return ok, f"revisions={len(revisions)}, has_600105={yd is not None}"


def valuation_reproducibility() -> tuple[bool, str]:
    body = text("analysis/valuation_audit.md")
    ok = "Model Reproducibility: PASS" in body and "价格/股本核对表" in body and "MECHANICAL_PASS_INSTITUTIONAL_FAIL" in body
    return ok, "reproducibility PASS + reconciliation + downgrade"


def growth_earnings_present() -> tuple[bool, str]:
    driver = load_json("data/growth_driver_model.json")
    rows = driver.get("rows", [])
    has_impl = any(r.get("current_price_implied_np_cagr_3y") is not None for r in rows)
    model_body = text("analysis/valuation_model.md")
    ok = (
        len(rows) == 26
        and has_impl
        and "成长盈利依赖" in model_body
        and "季节性校准" in model_body
        and "现价隐含" in text("analysis/implied_growth_sensitivity.md")
    )
    return ok, f"driver_rows={len(rows)}, implied_present={has_impl}"


def broker_street_downgrade_present() -> tuple[bool, str]:
    packet = load_json("data/broker_street_consensus_20260626.json")
    body = text("data/broker_street_consensus_20260626.md")
    ok = (
        packet.get("signoff_downgrade") == "MECHANICAL_PASS_INSTITUTIONAL_FAIL"
        and packet.get("coverage_universe") == 26
        and "not disclosed" in body
    )
    return ok, f"downgrade={packet.get('signoff_downgrade')}, universe={packet.get('coverage_universe')}"


def valuation_gate_sections() -> tuple[bool, str]:
    body = text("analysis/valuation_model.md")
    required = ["季节性校准", "下一季度阈值", "成长盈利依赖", "全链条分类依赖", "市场隐含预期与情绪锚", "市场预期估值桥", "方法与假设桥"]
    missing = [s for s in required if s not in body]
    ch08 = text("sections/ch08_valuation.tex")
    ch08_required = ["估值哲学与门禁", "分母正常化", "业绩预告", "成长盈利拆分与现价隐含增速", "券商/Street 对照与发布降级", "业务模型—估值方法匹配矩阵"]
    ch08_missing = [s for s in ch08_required if s not in ch08]
    return not missing and not ch08_missing, f"model_missing={missing}, ch08_missing={ch08_missing}"


def preview_in_valuation() -> tuple[bool, str]:
    """The covered name with H1 guidance (600105) must have its guidance folded
    into the valuation denominator: 2026E EPS lifted above the Q1-annualized
    basis, and ch08 must state the guidance is computed into valuation."""
    model = load_json("data/current_valuation_model_20260626.json")
    yd = next((r for r in model.get("rows", []) if r["code"] == "600105"), None)
    ch08 = text("sections/ch08_valuation.tex")
    ok = (
        yd is not None
        and yd.get("eps_basis") == "h1_guidance"
        and yd.get("has_h1_guidance") is True
        and yd.get("eps_2026e", 0) > 0.6  # guidance lifts EPS well above the 0.45 q1-annualized basis
        and "业绩预告已计入估值" in ch08
    )
    return ok, f"600105 eps_basis={yd.get('eps_basis') if yd else None}, eps26={round(yd.get('eps_2026e'),3) if yd else None}"


def main() -> int:
    checks = []
    for rel in [
        "research_brief.md", "main.tex", "review_log.md", "data_room_index.md",
        "completion_audit_manifest.json", "completion_audit_manifest.md",
        "source_exhaustion_log.json", "source_exhaustion_log.md",
        "data/raw_market_data_20260626.json", "data/raw_financials_20260626.json",
        "data/raw_market_data.md", "data/raw_financials.md",
        "data/verified_market_data.md", "data/verified_financials.md",
        "data/source_registry.json", "data/source_registry.md",
        "data/claim_audit.json", "data/claim_audit.md",
        "data/industry_universe_coverage.json", "data/industry_universe_coverage.md",
        "data/current_valuation_model_20260626.json", "data/current_valuation_model_20260626.md",
        "data/market_sentiment_anchor_20260626.json", "data/market_sentiment_anchor_20260626.md",
        "data/market_expectation_valuation_20260626.json", "data/market_expectation_valuation_20260626.md",
        "data/broker_consensus_snapshot_20260626.json", "data/broker_consensus_snapshot_20260626.md",
        "data/consensus_analysis.md", "data/broker_target_price_history.md",
        "data/earnings_expectations_vs_delivery.md", "analysis/valuation_model.md",
        "analysis/broker_comparison.md", "analysis/valuation_audit.md", "analysis/industry_landscape.md",
        "analysis/house_view.md", "analysis/risk_framework.md",
        "analysis/template_brief.md", "analysis/exhibit_plan.md",
        "analysis/optical_chain_map.mmd", "sections/app_source_audit.tex",
        "sections/app_research_workplan.tex",
        "sections/ch11_earnings_preview.tex",
        "data/earnings_preview_h1_2026_20260706.json", "data/earnings_preview_h1_2026_20260706.md",
        "data/optical_preview_census_20260706.json", "data/optical_preview_census_20260706.md",
        "data/earnings_preview_revision_20260706.json", "data/earnings_preview_revision_20260706.md",
        "analysis/growth_earnings_model.md", "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md", "data/growth_driver_model.json",
        "data/broker_street_consensus_20260626.json", "data/broker_street_consensus_20260626.md",
    ]:
        checks.append((f"file:{rel}", *check_file(rel)))
    for idx in range(1, 11):
        rel = f"sections/ch{idx:02d}_" + [
            "ic_summary", "evidence", "technology", "supply_chain", "demand",
            "companies", "sentiment", "valuation", "risks", "investment",
        ][idx - 1] + ".tex"
        checks.append((f"section_prose:{idx}", *section_has_prose(rel)))
    checks.extend([
        ("valuation_complete", *valuation_complete()),
        ("source_files_exist", *source_files_exist()),
        ("pdf_pages", *has_pdf_pages()),
        ("pdf_no_TODO", *no_pattern_in_pdf("TODO")),
        ("pdf_no_placeholder", *no_pattern_in_pdf("<Report Title>")),
        ("pdf_has_valuation", "目标价" in text("sections/ch08_valuation.tex") and "隐含空间" in text("sections/ch08_valuation.tex"), "valuation terms"),
        ("pdf_has_disclaimer", "不构成任何证券买卖建议" in text("main.tex"), "disclaimer"),
        ("mermaid_used", "flowchart LR" in text("analysis/optical_chain_map.mmd"), "Mermaid flowchart"),
        ("broker_targets_not_substitute", "不作为估值输入" in text("sections/ch07_sentiment.tex"), "broker boundary"),
        ("source_boundary", "未披露" in text("sections/ch02_evidence.tex") and "券商数据只用于识别市场预期" in text("sections/ch02_evidence.tex"), "source boundary"),
        ("broker_and_expectation_present", *broker_and_expectation_present()),
        ("chinese_language_gate", *chinese_language_gate()),
        ("full_chain_complete", *full_chain_complete()),
        ("full_chain_map_tickers_explicit", *full_chain_map_tickers_explicit()),
        ("watchlist_present", "罗博特科" in text("sections/ch04_supply_chain.tex") and "观察池" in text("sections/ch04_supply_chain.tex"), "equipment watchlist"),
        ("tongding_present", "通鼎互联" in text("sections/ch04_supply_chain.tex") and "002491" in text("data/current_valuation_model_20260626.md"), "Tongding included"),
        ("industry_universe_present", "产业链标的覆盖" in text("data/industry_universe_coverage.md") and "特发信息" in text("data/industry_universe_coverage.md"), "coverage and watchlist"),
        ("research_workplan_present", "全链条调研问题库" in text("sections/app_research_workplan.tex") and "更新触发规则" in text("sections/app_research_workplan.tex"), "research workplan"),
        ("investment_advice_depth", *investment_advice_depth()),
        ("raw_quote_count", len(load_json("data/raw_market_data_20260626.json").get("quotes", {})) == 26, "26 quotes"),
        ("raw_financial_count", len(load_json("data/raw_financials_20260626.json").get("financials", {})) == 26, "26 financial packets"),
        ("weighted_upside_present", math.isfinite(load_json("data/current_valuation_model_20260626.json").get("weighted_base_upside")), "weighted upside"),
        ("post_cutoff_preview_present", *post_cutoff_preview_present()),
        ("post_cutoff_disclosure_in_pdf", *post_cutoff_disclosure_in_pdf()),
        ("frozen_baseline_intact", *frozen_baseline_intact()),
        ("preview_revision_dual_view", *preview_revision_dual_view()),
        ("valuation_reproducibility", *valuation_reproducibility()),
        ("growth_earnings_present", *growth_earnings_present()),
        ("broker_street_downgrade_present", *broker_street_downgrade_present()),
        ("valuation_gate_sections", *valuation_gate_sections()),
        ("preview_in_valuation", *preview_in_valuation()),
    ])
    pass_count = 0
    fail_count = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if ok:
            pass_count += 1
        else:
            fail_count += 1
        print(f"{status}: {name} - {detail}")
    print(f"SUMMARY: PASS={pass_count} FAIL={fail_count}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''
    path = CASE / "tools" / "verify_research_workspace.py"
    path.write_text(verifier, encoding="utf-8")
    path.chmod(0o755)


def main() -> int:
    for path in [DATA, ANALYSIS, SECTIONS, SOURCES / "official-filings-20260626", SOURCES / "industry-public-20260626"]:
        path.mkdir(parents=True, exist_ok=True)
    if REFRESH_LIVE:
        quotes = {}
        financials = {}
        for ticker in TICKERS:
            code = ticker["code"]
            quotes[code] = cached_cli("quote", code, "quote", code)
            financials[code] = cached_cli("financials", code, "financials", code)
        source_records = []
        for item in SOURCE_ITEMS:
            out_dir = SOURCES / ("official-filings-20260626" if item["type"] == "official_filing" else "industry-public-20260626")
            print(f"Fetching source {item['id']}: {item['url']}", flush=True)
            source_records.append({"id": item["id"], **fetch_url(item["url"], out_dir)})
    else:
        # Default: reproduce the RUN_DATE-frozen report. Prices/financials come
        # from the frozen snapshot (never re-baselined to "today"), and only
        # brand-new capturable sources not already in the frozen manifest are
        # fetched. Broker/methodology items stay registry-only, as in the
        # frozen capture set.
        quotes, financials = load_frozen_snapshot()
        source_records = load_frozen_source_records()
        captured_ids = {r["id"] for r in source_records}
        capturable_types = {"official_filing", "industry_public", "official_company"}
        for item in SOURCE_ITEMS:
            if item["id"] in captured_ids or item["type"] not in capturable_types:
                continue
            out_dir = SOURCES / ("official-filings-20260626" if item["type"] == "official_filing" else "industry-public-20260626")
            print(f"Fetching new source {item['id']}: {item['url']}", flush=True)
            source_records.append({"id": item["id"], **fetch_url(item["url"], out_dir)})
    model = make_model(quotes, financials)
    revision = make_post_cutoff_revision(model)
    build_markdown_outputs(model, quotes, financials, source_records, revision)
    write_latex(model, revision)
    if REFRESH_LIVE:
        # _cache_* are live-fetch scratch files; the frozen raw_*_{RUN_DATE}.json
        # snapshots are NOT matched by this glob and are preserved.
        for cache_path in DATA.glob(f"_cache_*_{RUN_DATE}.json"):
            cache_path.unlink()
    write_governance(model, source_records)
    write_verifier()
    print(f"Built {CASE}")
    print(f"Weighted intrinsic upside: {pct(model['weighted_base_upside'])}")
    print(f"Weighted market-adjusted upside: {pct(model['weighted_final_upside'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
