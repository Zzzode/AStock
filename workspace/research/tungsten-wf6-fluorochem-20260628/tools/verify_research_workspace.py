#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EXPECTED_CODES = {"600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020", "002407", "600378", "300037", "688146", "688549", "688268", "300346", "688106", "002549", "002971"}

def ok_file(rel: str) -> tuple[bool, str]:
    p = BASE / rel
    return p.exists() and p.stat().st_size > 0, rel

def load_json(rel: str):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))

def pdf_pages() -> tuple[bool, str]:
    p = BASE / "main.pdf"
    if not p.exists():
        return False, "main.pdf missing"
    proc = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True)
    if proc.returncode != 0:
        return False, "pdfinfo failed"
    pages = 0
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
    return pages >= 15, f"pages={pages}"

def template_exhibit_quality() -> tuple[bool, str]:
    template = (BASE / "analysis/template_brief.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    visual = (BASE / "analysis/visual_review.md").read_text(encoding="utf-8")
    template_ok = all(s in template for s in ["主题型产业链深度", "BlackRock", "Vanguard", "J.P. Morgan", "模板验收表"])
    exhibit_count = sum(1 for line in exhibit.splitlines() if line.startswith("| ") and "Exhibit" not in line and "---" not in line)
    exhibit_ok = exhibit_count >= 25 and all(s in exhibit for s in ["投资含义", "增长业绩门禁", "数据完整性审计总览", "业绩披露日历与验证窗口", "业绩预告/快报公告证据", "问询/审核回复公告证据", "完整估值总表", "股本与市值口径审计", "官方股本重算审计", "客户链高影响声明审计", "客户侧验证探针", "下游客户公开文件探针", "公告/互动/研报补证结果", "公开价格/成本代理边界", "中船特气招股书价格/毛利边界", "公司级制冷剂配额证据", "上游资源安全与基准现金流证据", "公开个股研报快照", "公开券商覆盖历史质量", "公开券商预测分歧与本报告差异", "公开券商全文PDF证据", "公开券商全文模型表字段", "公开券商全文硬字段关键词", "主营构成与产品毛利率", "下游行业与区域结构", "下游需求锚行情与财务", "AI平台/HBM/网络需求锚", "公司澄清/风险提示证据", "投资者关系互动问答补证", "投关调研记录标题索引与正文关键词探针", "合同/中标/供货协议公告全文扫描", "合同金额经济性约束", "订单持续性与收入确认耐久性证据", "价格与毛利入模门禁", "官方单品收入/订单金额边界", "半导体高纯钨材边界", "含氟电子材料边界", "市场盘口与日内风险", "官方市值与流动性口径", "股东结构与机构持仓拥挤度", "融资融券杠杆拥挤度", "龙虎榜席位异常与机构交易", "龙虎榜席位快照", "交易风险公告与估值热度", "制程/材料功能证据", "政策/出口管制官方证据", "公司产品能力官方证据", "项目/产能建设官方证据", "年报客户/供应商集中度", "年报客户/供应商明细可得性", "年报主题证据扫描", "年报原文证据短摘", "年报管理层讨论与业绩归因", "产销量/库存/产能利用证据", "成本结构/毛利/价格传导证据", "竞争格局/行业地位证据", "单品转化约束", "隐含增长反推门槛", "证据成熟度与下一季验证", "单季财务趋势与拐点", "资本开支与营运资本信号", "研发与技术资产强度", "字段级证据矩阵", "硬缺口行动清单", "全覆盖催化与失效条件", "反方证据与看错情形", "逐标的风险监测触发器"])
    visual_ok = all(s in visual for s in ["门禁状态：通过", "五项硬门禁", "Overfull hbox", "中文可读性"])
    return template_ok and exhibit_ok and visual_ok, f"template={template_ok}, exhibits={exhibit_count}, visual={visual_ok}"

def fundamental_quality_complete() -> tuple[bool, str]:
    packet = load_json("data/fundamental_quality_snapshot.json")
    rows = packet.get("rows", [])
    gaps = load_json("data/data_gap_matrix.json").get("rows", [])
    required = [
        "q1_operating_cash_flow",
        "q1_cash_conversion",
        "q1_net_margin",
        "q1_debt_ratio",
        "q1_quick_ratio",
        "q1_revenue_growth",
        "q1_profit_growth",
        "cash_conversion_label",
        "balance_sheet_label",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    gap_ok = len(gaps) == 18 and all(r.get("remaining_gaps") for r in gaps)
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    md = (BASE / "data/verified_financials.md").read_text(encoding="utf-8")
    text_ok = all(s in main_text for s in ["财务质量与资产负债表信号", "经营现金流", "现金转化", "数据补齐与剩余缺口"]) and all(s in md for s in ["经营现金流", "负债率", "速动比率"])
    return len(rows) == 18 and not missing and gap_ok and text_ok, f"rows={len(rows)}, missing={missing[:3]}, gap_ok={gap_ok}, text_ok={text_ok}"

def quarterly_financial_trend_complete() -> tuple[bool, str]:
    packet = load_json("data/quarterly_financial_trend_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required = [
        "latest_period",
        "latest_single_revenue",
        "latest_single_net_profit_parent",
        "latest_single_gross_margin",
        "latest_single_operating_cash_flow",
        "latest_single_revenue_yoy",
        "latest_single_net_profit_yoy",
        "trend_signal",
    ]
    missing = []
    short = []
    for r in rows:
        if len(r.get("quarters", [])) < 5:
            short.append(f"{r.get('ticker')}:{len(r.get('quarters', []))}")
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    text = (BASE / "analysis/quarterly_financial_trend_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["单季财务趋势与拐点快照", "单季收入", "单季经营现金流"]) and "单季财务趋势与拐点" in main_text and "单季趋势" in cards
    return len(covered) == 18 and not missing and not short and text_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, short={short[:3]}, text_ok={text_ok}"

def market_tape_complete() -> tuple[bool, str]:
    packet = load_json("data/market_tape_snapshot.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "price",
        "change_percent",
        "intraday_range_pct",
        "turnover_amount",
        "market_tape_status",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/market_tape_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/market_tape_snapshot.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch06_sentiment.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["市场盘口与日内风险快照", "涨跌幅", "日内振幅", "成交额"]) and "市场盘口与日内风险快照" in analysis
    section_ok = "市场盘口与日内风险" in section and "盘口、涨跌幅、日内振幅和成交额只用于二级市场拥挤度" in section
    field_ok = "市场盘口与日内风险" in field and "市场盘口证据不得替代客户订单" in field
    main_ok = "市场盘口与日内风险" in main_text and "涨跌幅" in main_text and "日内振幅" in main_text
    boundary_ok = packet.get("gate_status") == "PASS" and "不得替代基本面目标价" in packet.get("use_boundary", "")
    return len(codes) == 18 and not missing and text_ok and section_ok and field_ok and main_ok and boundary_ok, f"rows={len(rows)}, covered={len(codes)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def official_market_liquidity_complete() -> tuple[bool, str]:
    packet = load_json("data/official_market_liquidity_snapshot.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "quote_time",
        "official_price",
        "official_turnover_rate_pct",
        "official_volume_ratio",
        "official_turnover_amount",
        "official_total_market_cap",
        "official_float_market_cap",
        "float_market_cap_ratio",
        "liquidity_signal",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/official_market_liquidity_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/official_market_liquidity_snapshot.md").read_text(encoding="utf-8")
    section6 = (BASE / "sections/ch06_sentiment.tex").read_text(encoding="utf-8")
    section7 = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["官方市值与流动性口径快照", "官方价", "官方总市值", "官方流通市值", "换手率", "量比", "估值现价"]) and "官方市值与流动性口径快照" in analysis
    section_ok = "官方市值与流动性口径" in section6 and "东方财富官方市值与流动性快照" in section7
    field_ok = "官方市值与流动性口径" in field and "不得替代客户订单" in field
    provenance_ok = "官方市值与流动性口径" in provenance and "东方财富push2" in provenance
    catalog_ok = "东方财富官方市值与流动性快照" in catalog
    main_ok = "官方市值与流动性口径" in main_text and "官方现价" in main_text and "流通市值" in main_text and "换手率" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "估值现价" in packet.get("use_boundary", "") and "不替代客户订单" in packet.get("use_boundary", "")
    return len(codes) == 18 and not missing and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and main_ok and boundary_ok, f"rows={len(rows)}, covered={len(codes)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def shareholder_crowding_complete() -> tuple[bool, str]:
    packet = load_json("data/shareholder_crowding_snapshot.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "theme",
        "top_holder_date",
        "top1_holder",
        "top1_share_pct",
        "main_top10_share_pct",
        "ownership_structure",
        "circulate_holder_date",
        "circulate_top10_float_share_pct",
        "fund_holder_date",
        "fund_holder_count",
        "fund_float_share_pct",
        "fund_market_value",
        "official_float_market_cap",
        "float_market_cap_ratio",
        "official_turnover_rate_pct",
        "official_turnover_amount",
        "current_price",
        "final_target",
        "valuation_use",
        "evidence_boundary",
        "crowding_signal",
        "model_action",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/shareholder_crowding_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/shareholder_crowding_snapshot.md").read_text(encoding="utf-8")
    section6 = (BASE / "sections/ch06_sentiment.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["股东结构与机构持仓拥挤度快照", "第一大股东", "基金持仓", "拥挤信号"]) and "股东结构与机构持仓拥挤度快照" in analysis
    section_ok = "股东结构与机构持仓拥挤度" in section6 and "只用于二级市场拥挤度" in section6 and "不替代客户订单" in section6
    field_ok = "股东结构与机构持仓拥挤度" in field and "股东结构与机构持仓证据不得替代客户订单" in field
    provenance_ok = "股东结构与机构持仓拥挤度" in provenance and "AkShare" in provenance
    catalog_ok = "AkShare股东结构与机构持仓快照" in catalog
    audit_ok = "股东结构与机构持仓拥挤度" in audit and "不替代订单金额" in audit
    main_ok = "股东结构与机构持仓拥挤度" in main_text and "不替代客户订单" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代客户订单" in packet.get("use_boundary", "")
    signal_ok = any("高拥挤" in str(r.get("crowding_signal")) or "中拥挤" in str(r.get("crowding_signal")) for r in rows)
    return (
        packet.get("covered_tickers") == 18
        and codes == EXPECTED_CODES
        and not missing
        and text_ok
        and section_ok
        and field_ok
        and provenance_ok
        and catalog_ok
        and audit_ok
        and main_ok
        and boundary_ok
        and signal_ok
    ), f"rows={len(rows)}, covered={len(codes)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, audit_ok={audit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, signal_ok={signal_ok}"

def margin_leverage_complete() -> tuple[bool, str]:
    packet = load_json("data/margin_leverage_snapshot.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "exchange",
        "margin_date",
        "margin_status",
        "margin_eligible",
        "margin_balance",
        "margin_buy",
        "margin_balance_to_float_cap",
        "margin_buy_to_turnover",
        "valuation_use",
        "evidence_boundary",
        "leverage_signal",
        "model_action",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/margin_leverage_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/margin_leverage_snapshot.md").read_text(encoding="utf-8")
    section6 = (BASE / "sections/ch06_sentiment.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["融资融券杠杆拥挤度快照", "融资余额", "融资买入", "杠杆信号"]) and "融资融券杠杆拥挤度快照" in analysis
    section_ok = "融资融券杠杆拥挤度" in section6 and "只用于杠杆资金参与度" in section6 and "不替代客户订单" in section6
    field_ok = "融资融券杠杆拥挤度" in field and "融资融券证据不得替代客户订单" in field
    provenance_ok = "融资融券杠杆拥挤度" in provenance and "上交所融资融券明细" in provenance
    catalog_ok = "交易所融资融券杠杆快照" in catalog
    audit_ok = "融资融券杠杆拥挤度" in audit and "融资融券证据不替代订单金额" in audit
    gap_ok = "融资融券杠杆拥挤度" in gaps
    main_ok = "融资融券杠杆拥挤度" in main_text and "不替代客户订单" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代客户订单" in packet.get("use_boundary", "")
    eligible_ok = packet.get("margin_eligible_tickers", 0) >= 10
    signal_ok = any("高杠杆" in str(r.get("leverage_signal")) or "中杠杆" in str(r.get("leverage_signal")) for r in rows)
    return (
        packet.get("covered_tickers") == 18
        and codes == EXPECTED_CODES
        and not missing
        and text_ok
        and section_ok
        and field_ok
        and provenance_ok
        and catalog_ok
        and audit_ok
        and gap_ok
        and main_ok
        and boundary_ok
        and eligible_ok
        and signal_ok
    ), f"rows={len(rows)}, covered={len(codes)}, eligible={packet.get('margin_eligible_tickers')}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, eligible_ok={eligible_ok}, signal_ok={signal_ok}"

def dragon_tiger_complete() -> tuple[bool, str]:
    packet = load_json("data/dragon_tiger_seat_snapshot.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "month_status",
        "latest_lhb_date",
        "month_list_count",
        "month_lhb_net_buy",
        "month_lhb_turnover",
        "month_institution_net_buy",
        "june_detail_count",
        "valuation_use",
        "evidence_boundary",
        "seat_signal",
        "model_action",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/dragon_tiger_seat_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/dragon_tiger_seat_snapshot.md").read_text(encoding="utf-8")
    section6 = (BASE / "sections/ch06_sentiment.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["龙虎榜席位异常与机构交易快照", "上榜次数", "机构净买额", "席位信号"]) and "龙虎榜席位异常与机构交易快照" in analysis
    section_ok = "龙虎榜席位异常与机构交易" in section6 and "公开异常交易席位" in section6 and "不替代客户订单" in section6
    field_ok = "龙虎榜席位异常与机构交易" in field and "龙虎榜席位证据不得替代客户订单" in field
    provenance_ok = "龙虎榜席位异常与机构交易" in provenance and "东方财富龙虎榜" in provenance
    catalog_ok = "龙虎榜席位异常与机构交易" in catalog or "龙虎榜席位快照" in catalog
    audit_ok = "龙虎榜席位异常与机构交易" in audit and ("不得作为基本面目标价上修依据" in audit or "不替代订单金额" in audit)
    gap_ok = "龙虎榜席位异常" in gaps
    main_ok = "龙虎榜席位异常与机构交易" in main_text and "不替代客户订单" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代客户订单" in packet.get("use_boundary", "")
    listed_ok = packet.get("recent_listed_tickers", 0) >= 8
    detail_ok = packet.get("june_detail_records", 0) >= 20
    signal_ok = any("高席位" in str(r.get("seat_signal")) or "中席位" in str(r.get("seat_signal")) for r in rows)
    return (
        packet.get("covered_tickers") == 18
        and codes == EXPECTED_CODES
        and not missing
        and text_ok
        and section_ok
        and field_ok
        and provenance_ok
        and catalog_ok
        and audit_ok
        and gap_ok
        and main_ok
        and boundary_ok
        and listed_ok
        and detail_ok
        and signal_ok
    ), f"rows={len(rows)}, covered={len(codes)}, listed={packet.get('recent_listed_tickers')}, details={packet.get('june_detail_records')}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, listed_ok={listed_ok}, detail_ok={detail_ok}, signal_ok={signal_ok}"

def capitalization_audit_complete() -> tuple[bool, str]:
    packet = load_json("data/capitalization_audit.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "price_date",
        "price",
        "bps",
        "derived_shares",
        "used_market_cap",
        "raw_market_cap_status",
        "market_cap_source",
        "valuation_use",
        "evidence_boundary",
        "refresh_trigger",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/capitalization_audit.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/capitalization_audit.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["股本与市值口径审计", "使用股本", "估值市值", "原始行情市值字段"]) and "股本与市值口径审计" in analysis
    section_ok = "股本与市值口径审计" in section and "东方财富官方总市值/官方价倒算" in section and "官方倒算股本不替代交易所正式股本公告" in section
    field_ok = "股本与市值口径" in field and "估值市值使用东方财富官方总市值" in field
    provenance_ok = "股本与市值口径审计" in provenance and "东方财富官方价/官方总市值" in provenance
    main_ok = "股本与市值口径审计" in main_text and "使用股本" in main_text and "估值市值" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代交易所正式股本公告" in packet.get("use_boundary", "")
    return len(codes) == 18 and not missing and text_ok and section_ok and field_ok and provenance_ok and main_ok and boundary_ok, f"rows={len(rows)}, covered={len(codes)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def share_count_reconciliation_complete() -> tuple[bool, str]:
    packet = load_json("data/share_count_reconciliation.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "price_date",
        "official_share_quote_time",
        "used_total_shares",
        "used_share_count_source",
        "financial_derived_shares",
        "official_implied_total_shares",
        "official_implied_float_shares",
        "financial_vs_official_delta_pct",
        "used_market_cap",
        "used_float_market_cap",
        "valuation_use",
        "evidence_boundary",
        "refresh_trigger",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/share_count_reconciliation.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/share_count_reconciliation.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    valuation = (BASE / "data/current_valuation_model_20260628.json").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in data_md for s in ["官方股本重算审计", "官方总股本", "官方流通股本", "旧/官方差异", "估值市值"]) and "官方股本重算审计" in analysis
    section_ok = "官方股本重算审计" in section and "官方总股本=东方财富官方总市值/官方价" in section and "不替代客户订单、合同平均售价、收入确认比例或单品毛利" in section
    field_ok = "官方股本重算审计" in field and "不得替代客户订单" in field
    provenance_ok = "官方股本重算审计" in provenance and "官方总市值/价格" in provenance
    catalog_ok = "官方股本重算审计" in catalog
    valuation_ok = "official_implied_total_shares" in valuation and "share_count_source" in valuation
    main_ok = "官方股本重算审计" in main_text and "官方总股本" in main_text and "旧/官方" in main_text and "差异" in main_text
    boundary_ok = packet.get("schema") == "astock.share_count_reconciliation.v1" and packet.get("gate_status") == "CONDITIONAL" and "不替代客户订单" in packet.get("use_boundary", "")
    return len(codes) == 18 and packet.get("covered_tickers") == 18 and not missing and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and valuation_ok and main_ok and boundary_ok, f"rows={len(rows)}, covered={len(codes)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, valuation_ok={valuation_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def public_price_proxy_complete() -> tuple[bool, str]:
    packet = load_json("data/public_price_proxy_snapshot.json")
    rows = packet.get("rows", [])
    themes = {r.get("theme") for r in rows}
    required_keys = ["theme", "proxy_item", "proxy_type", "as_of", "value", "trend", "valuation_use", "remaining_gap"]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('proxy_item')}:{k}")
    text = (BASE / "analysis/public_price_proxy_snapshot.md").read_text(encoding="utf-8")
    sensitivity = (BASE / "analysis/implied_growth_sensitivity.md").read_text(encoding="utf-8")
    valuation = (BASE / "analysis/valuation_model.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["公开价格代理边界包", "行业价格不等于公司合同平均售价", "公开价格代理不能直接进入增长每股收益"])
    downstream_ok = "公开价格代理边界" in sensitivity and "公开价格代理边界" in valuation
    asp_boundary_ok = any(
        s in main_text
        for s in [
            "行业价格不等于公司合同ASP",
            "行业价格不等于公司合同 ASP",
            "行业价格不等于公司合同平均售价",
        ]
    )
    main_ok = all(s in main_text for s in ["公开价格/成本代理边界", "公开价格代理进入估值的边界"]) and asp_boundary_ok
    return len(rows) >= 8 and {"钨", "电子特气", "氟化工"} <= themes and not missing and text_ok and downstream_ok and main_ok, f"rows={len(rows)}, themes={len(themes)}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, main_ok={main_ok}"

def prospectus_price_boundary_complete() -> tuple[bool, str]:
    packet = load_json("data/prospectus_price_boundary_evidence.json")
    rows = packet.get("rows", [])
    required_keys = ["evidence_layer", "official_evidence", "model_use", "valuation_boundary"]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('evidence_layer')}:{k}")
    data_md = (BASE / "data/prospectus_price_boundary_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/prospectus_price_boundary_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch02_evidence.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    source_pdf = BASE / "sources/official-prospectus-2023/688146-中船特气-ipo-prospectus-20230417.pdf"
    text_ok = all(s in data_md for s in ["招股书价格/毛利披露边界", "平均单价", "豁免披露", "六氟化钨", "8.27%", "5.76%", "5.16%", "不得替代当前合同平均售价"]) and "招股书价格/毛利披露边界" in analysis
    section_ok = all(s in section for s in ["中船特气招股书价格/毛利边界", "平均单价", "豁免披露", "不得把六氟化钨价格叙事转成增长每股收益"])
    field_ok = "招股书价格/毛利披露边界" in field and "不得替代当前合同平均售价" in field
    hard_gap_ok = "招股书披露平均单价计算口径并申请豁免披露" in hard_gap and "公开价格代理不能替代公司合同平均售价" in hard_gap
    source_ok = "S35" in source and "首次公开发行股票并在科创板上市招股说明书" in source and source_pdf.exists() and source_pdf.stat().st_size > 1_000_000
    claim_ok = "平均单价已申请豁免披露" in claim and "S35" in claim
    main_ok = all(s in main_text for s in ["中船特气招股书价格/毛利边界", "平均单价", "豁免披露", "阻断增长每股收益"])
    boundary_ok = packet.get("schema") == "astock.prospectus_price_boundary.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("source_id") == "S35" and "不得替代当前合同平均售价" in packet.get("use_boundary", "")
    return len(rows) >= 4 and not missing and text_ok and section_ok and field_ok and hard_gap_ok and source_ok and claim_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, hard_gap_ok={hard_gap_ok}, source_ok={source_ok}, claim_ok={claim_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def hfc_quota_allocation_complete() -> tuple[bool, str]:
    packet = load_json("data/hfc_quota_allocation_evidence.json")
    rows = packet.get("rows", [])
    by_code = {r.get("ticker"): r for r in rows}
    required_codes = {"600160", "603379", "605020", "002407"}
    required_keys = [
        "ticker",
        "company",
        "mapped_entities",
        "production_quota_tons",
        "internal_use_quota_tons",
        "import_quota_co2e_tons",
        "national_production_share_pct",
        "national_internal_use_share_pct",
        "national_import_share_pct",
        "hfc_species",
        "main_species_share_summary",
        "official_evidence",
        "valuation_use",
        "evidence_boundary",
        "source_id",
        "status",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/hfc_quota_allocation_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/hfc_quota_allocation_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch02_evidence.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    source_pdf = BASE / "sources/official-policy-hfc-quota-2026/mee-2026-hfc-quota-attachment2.pdf"
    quota_values_ok = (
        by_code.get("600160", {}).get("production_quota_tons") == 240826
        and by_code.get("600160", {}).get("national_production_share_pct") == 30.18
        and by_code.get("603379", {}).get("import_quota_co2e_tons") == 8451
        and by_code.get("603379", {}).get("national_production_share_pct") == 9.64
        and by_code.get("605020", {}).get("production_quota_tons") == 60281
        and by_code.get("605020", {}).get("main_species_share_summary") == "HFC-143a 28.57%；HFC-134a 6.10%；HFC-152a 31.59%；HFC-125 5.37%"
        and by_code.get("002407", {}).get("status") == "not_found_in_quota_attachment"
    )
    national_totals_ok = packet.get("national_totals", {}).get("production_quota_tons") == 797845 and packet.get("national_totals", {}).get("import_quota_co2e_tons") == 5992594
    text_ok = all(s in data_md for s in ["公司级制冷剂配额证据", "生态环境部", "巨化股份", "三美股份", "永和股份", "多氟多", "全国生产份额", "重点品种份额", "不得替代含氟电子材料"]) and "公司级制冷剂配额证据" in analysis
    section_ok = all(s in section for s in ["公司级制冷剂配额证据", "生态环境部2026年度氢氟碳化物", r"全国生产配额份额约30.18\%", "多氟多", "不替代含氟电子材料"])
    field_ok = "公司级制冷剂配额证据" in field and "全国生产份额" in field and "公司级HFC配额证据不得替代含氟电子材料" in field
    provenance_ok = "公司级制冷剂配额证据" in provenance and "生态环境部2026年度氢氟碳化物" in provenance and "重点品种份额" in provenance
    hard_gap_ok = "生态环境部2026年度HFC配额附件" in hard_gap and "制冷剂配额和份额已官方补证" in hard_gap
    source_ok = "S36" in source and "氢氟碳化物生产、进口配额核发表" in source and source_pdf.exists() and source_pdf.stat().st_size > 100_000
    claim_ok = "生态环境部2026年度氢氟碳化物配额附件" in claim and "S36" in claim
    audit_ok = "公司级制冷剂配额证据" in audit and "不得替代含氟电子材料客户" in audit
    main_ok = "公司级制冷剂配额证据" in main_text and "多氟多" in main_text and "不替代含氟电子材料" in main_text
    boundary_ok = packet.get("schema") == "astock.hfc_quota_allocation.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("source_id") == "S36" and "不得替代含氟电子材料" in packet.get("use_boundary", "") and "全国分母" in packet.get("share_method", "")
    return required_codes <= set(by_code) and not missing and quota_values_ok and national_totals_ok and text_ok and section_ok and field_ok and provenance_ok and hard_gap_ok and source_ok and claim_ok and audit_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, quota_values_ok={quota_values_ok}, national_totals_ok={national_totals_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, hard_gap_ok={hard_gap_ok}, source_ok={source_ok}, claim_ok={claim_ok}, audit_ok={audit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def resource_security_evidence_complete() -> tuple[bool, str]:
    packet = load_json("data/resource_security_evidence.json")
    rows = packet.get("rows", [])
    by_code = {r.get("ticker"): r for r in rows}
    required_codes = {"600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020"}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "resource_layer",
        "resource_or_quota_anchor",
        "production_sales_anchor",
        "cost_or_margin_anchor",
        "valuation_use",
        "model_gate",
        "remaining_gap",
        "source_artifacts",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/resource_security_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/resource_security_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    source = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    gap = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    completion = (BASE / "completion_audit_manifest.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    value_ok = (
        packet.get("schema") == "astock.resource_security_evidence.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 8
        and packet.get("resource_base_allowed_count") == 7
        and packet.get("growth_eps_allowed_count") == 0
        and by_code.get("600549", {}).get("model_gate") == "RESOURCE_BASE_CASHFLOW_ALLOWED"
        and by_code.get("002842", {}).get("model_gate") == "PROCESSING_OPTIONALITY_ONLY"
        and by_code.get("603505", {}).get("model_gate") == "FLUORITE_AHF_BASE_CASHFLOW_ALLOWED"
        and "240,826吨" in by_code.get("600160", {}).get("resource_or_quota_anchor", "")
    )
    text_ok = all(s in data_md for s in ["上游资源安全与基准现金流证据", "资源/配额基准现金流", "0/8", "钨矿山/钨精矿", "萤石/AHF", "不得替代半导体高纯钨材"]) and "上游资源安全与基准现金流证据" in analysis
    section_ok = "上游资源安全与基准现金流证据" in section and "资源或配额可进入基准业务现金流" in section and "不替代半导体高纯钨材" in section
    field_ok = "上游资源安全与基准现金流证据" in field and "资源/配额基准现金流允许" in field and "不得替代半导体高纯钨材" in field
    provenance_ok = "上游资源安全与基准现金流证据" in provenance and "L1年报原文+L1官方配额+L2派生门禁" in provenance
    catalog_ok = "上游资源安全与基准现金流证据" in catalog and "增长每股收益 0/8" in catalog
    claim_ok = "上游资源安全与基准现金流证据显示8只" in claim and "0/8可进入成长每股收益" in claim
    audit_ok = "上游资源安全与基准现金流证据" in audit and "0/8可进入半导体或电子材料增长每股收益" in audit
    source_ok = "上游资源安全证据" in source and "资源/配额基准现金流允许" in source
    exhibit_ok = "上游资源安全与基准现金流证据" in exhibit and "资源/配额基准现金流门禁" in exhibit
    gap_ok = "上游资源安全/基准现金流证据" in gap and "资源/配额可以进入基准现金流" in gap
    completion_ok = "上游资源安全与基准现金流证据" in completion and "0/8可进入半导体或电子材料增长每股收益" in completion
    main_ok = "上游资源安全与基准现金流证据" in main_text and "资源或配额可进入基准业务现金流" in main_compact and "不替代半导体高纯钨材" in main_text
    boundary_ok = "不关闭半导体高纯钨材" in packet.get("use_boundary", "") and all("不替代" in r.get("evidence_boundary", "") for r in rows)
    return required_codes <= set(by_code) and not missing and value_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and claim_ok and audit_ok and source_ok and exhibit_ok and gap_ok and completion_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, value_ok={value_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, claim_ok={claim_ok}, audit_ok={audit_ok}, source_ok={source_ok}, exhibit_ok={exhibit_ok}, gap_ok={gap_ok}, completion_ok={completion_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def downstream_demand_complete() -> tuple[bool, str]:
    packet = load_json("data/downstream_demand_anchor_snapshot.json")
    rows = packet.get("rows", [])
    required_codes = {"688981", "688347", "688012", "002371", "688126"}
    codes = {r.get("code") for r in rows}
    required_keys = [
        "code",
        "name",
        "layer",
        "material_link",
        "quote_price",
        "turnover_amount",
        "q1_revenue",
        "q1_net_profit_parent",
        "q1_revenue_growth",
        "demand_signal",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('code')}:{k}")
    md = (BASE / "data/downstream_demand_anchor_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/downstream_demand_anchor_snapshot.md").read_text(encoding="utf-8")
    supply = (BASE / "analysis/supply_chain_model.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["下游需求锚快照", "不能证明上游", "覆盖需求锚"]) and "下游需求锚快照" in analysis
    main_ok = "下游需求锚行情与财务" in main_text and ("不是确认任何单一上游公司的收入" in main_text or "下游需求锚不等于上游公司" in main_text)
    supply_ok = "下游晶圆/设备需求" in supply and "需求锚" in supply
    boundary_ok = "不替代上游公司客户" in packet.get("use_boundary", "") or "不替代上游公司" in md
    return required_codes <= codes and len(rows) == 5 and not missing and text_ok and main_ok and supply_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, supply_ok={supply_ok}, boundary_ok={boundary_ok}"

def ai_platform_demand_complete() -> tuple[bool, str]:
    packet = load_json("data/ai_platform_demand_anchor_snapshot.json")
    rows = packet.get("rows", [])
    vendors = {r.get("vendor") for r in rows}
    required_vendors = {"NVIDIA", "SK hynix", "Google Cloud", "AWS", "Intel", "Huawei"}
    required_keys = [
        "platform_group",
        "vendor",
        "platform",
        "public_evidence",
        "material_chain_link",
        "watch_items",
        "source_url",
        "corpus_gap",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('vendor')}:{k}")
    md = (BASE / "data/ai_platform_demand_anchor_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/ai_platform_demand_anchor_snapshot.md").read_text(encoding="utf-8")
    supply = (BASE / "analysis/supply_chain_model.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["AI平台/HBM/网络需求锚", "不能把平台需求直接折成A股上游公司每股收益", "语料缺口"]) and "AI平台/HBM/网络需求锚" in analysis
    supply_ok = "AI平台/HBM/网络需求锚" in supply and "NVIDIA" in supply and "华为" in supply
    main_compact = "".join(main_text.split())
    main_ok = "AI平台需求锚" in main_compact and "HBM" in main_compact and ("不能替代供应商认证" in main_compact or "不能直接上调目标价" in main_compact)
    boundary_ok = "不证明A股上游订单" in packet.get("use_boundary", "") or "不替代A股订单" in md
    return len(rows) >= 7 and required_vendors <= vendors and not missing and text_ok and supply_ok and main_ok and boundary_ok, f"rows={len(rows)}, vendors={len(vendors)}, missing={missing[:3]}, text_ok={text_ok}, supply_ok={supply_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def company_clarification_complete() -> tuple[bool, str]:
    packet = load_json("data/company_clarification_snapshot.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"688146", "688549", "600378", "688268", "002971"}
    required_keys = [
        "ticker",
        "company",
        "clarification_date",
        "topic",
        "evidence_type",
        "clarified_fact",
        "production_status",
        "order_status",
        "revenue_status",
        "pricing_status",
        "source_ids",
        "valuation_effect",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    md = (BASE / "data/company_clarification_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/company_clarification_snapshot.md").read_text(encoding="utf-8")
    supply = (BASE / "analysis/supply_chain_model.md").read_text(encoding="utf-8")
    audit = (BASE / "data/customer_chain_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["公司澄清/风险提示证据快照", "合同平均售价", "单品毛利"]) and "公司澄清/风险提示证据快照" in analysis
    supply_ok = "公司澄清/风险提示证据" in supply and "和远气体" in supply and "中巨芯-U" in supply
    audit_ok = "和远气体WF6尚处试生产" in audit and "中巨芯高纯WF6产能600吨" in audit
    main_ok = "公司澄清/风险提示证据" in main_text and "负面门禁" in main_text and ("长期或大额订单" in main_text or "实质性订单" in main_text)
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代客户侧认证" in packet.get("use_boundary", "")
    return len(rows) >= 5 and required_tickers <= tickers and not missing and text_ok and supply_ok and audit_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}, supply_ok={supply_ok}, audit_ok={audit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def investor_relations_qa_complete() -> tuple[bool, str]:
    packet = load_json("data/investor_relations_qa_evidence.json")
    rows = packet.get("rows", [])
    summaries = packet.get("ticker_summaries", [])
    summary_codes = {str(r.get("ticker")) for r in summaries}
    required_keys = [
        "ticker",
        "company",
        "source_platform",
        "question",
        "answer",
        "answer_status",
        "topic_tags",
        "evidence_effect",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/investor_relations_qa_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/investor_relations_qa_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join([r.get("company", "") + r.get("question", "") + r.get("answer", "") for r in rows])
    text_ok = all(s in data_md for s in ["投资者关系互动问答补证", "证据作用", "覆盖摘要"]) and "投资者关系互动问答补证" in analysis
    section_ok = "投资者关系互动问答补证" in section and "不替代具体订单金额" in section
    field_ok = "投资者关系互动问答补证" in field and "互动问答不得替代具体订单金额" in field
    provenance_ok = "投资者关系互动问答补证" in provenance and "巨潮互动易" in provenance
    catalog_ok = "投资者关系互动问答补证" in catalog
    audit_ok = "投资者关系互动问答补证" in audit and "不得直接进入增长每股收益" in audit
    gap_ok = "投资者关系互动问答补证/否证" in gaps
    hard_gap_ok = "投资者关系互动问答" in hard_gap
    source_log_ok = "投资者关系互动问答补证" in source_log
    main_ok = "投资者关系互动问答补证" in main_text and "传闻否证" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and ("不替代这些硬字段" in packet.get("use_boundary", "") or "不得替代这些硬字段" in packet.get("use_boundary", ""))
    coverage_ok = packet.get("covered_tickers") == 18 and packet.get("source_tickers", 0) >= 8 and packet.get("relevant_tickers", 0) >= 8 and packet.get("high_impact_rows", 0) >= 15 and packet.get("selected_rows", 0) >= 25 and EXPECTED_CODES <= summary_codes
    error_ok = any(e.get("error") == "sseinfo_403_or_non_json_response" for e in packet.get("errors", []))
    evidence_ok = all(s in combined for s in ["和远气体", "试生产", "凯美特气", "未生产六氟化钨", "中钨高新", "钨粉", "多氟多", "南大光电"])
    passed = not missing and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and audit_ok and gap_ok and hard_gap_ok and source_log_ok and main_ok and boundary_ok and coverage_ok and error_ok and evidence_ok
    return passed, f"rows={len(rows)}, covered={packet.get('covered_tickers')}, source_tickers={packet.get('source_tickers')}, relevant={packet.get('relevant_tickers')}, high_impact={packet.get('high_impact_rows')}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, coverage_ok={coverage_ok}, error_ok={error_ok}, evidence_ok={evidence_ok}"

def ir_activity_record_complete() -> tuple[bool, str]:
    packet = load_json("data/ir_activity_record_evidence.json")
    rows = packet.get("rows", [])
    summaries = packet.get("ticker_summaries", [])
    summary_codes = {str(r.get("ticker")) for r in summaries}
    required_keys = [
        "ticker",
        "company",
        "source_platform",
        "announcement_date",
        "announcement_title",
        "activity_type",
        "content_parse_status",
        "p0_field_status",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/ir_activity_record_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/ir_activity_record_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join([r.get("company", "") + r.get("announcement_title", "") + r.get("activity_type", "") for r in rows])
    text_ok = all(s in data_md for s in ["投关调研记录标题索引与正文关键词探针补证", "覆盖摘要", "P0字段状态"]) and "投关调研记录标题索引与正文关键词探针补证" in analysis
    section_ok = "投关调研记录标题索引与正文关键词探针" in section and "正文关键词探针" in section and "不替代订单金额" in section
    field_ok = "投关调研记录标题索引与正文关键词探针" in field and "投关调研标题索引和正文关键词探针不得替代订单金额" in field
    provenance_ok = "投关调研记录标题索引与正文关键词探针" in provenance and "东方财富公告索引" in provenance
    catalog_ok = "投关调研记录标题索引与正文关键词探针" in catalog
    gap_ok = "投关调研记录标题索引与正文关键词探针" in gaps
    hard_gap_ok = "投关调研记录标题索引与正文关键词探针" in hard_gap
    source_log_ok = "投关调研记录标题索引与正文关键词探针" in source_log
    main_ok = "投关调研记录标题索引与正文关键词探针" in main_text and "正文关键词探针" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and packet.get("p0_closed_count") == 0 and "关键词语境" in packet.get("use_boundary", "")
    coverage_ok = packet.get("covered_tickers") == 18 and packet.get("title_source_tickers") == 18 and packet.get("cninfo_relation_tickers", 0) >= 8 and packet.get("selected_rows", 0) >= 80 and packet.get("content_probe_tickers", 0) >= 1 and packet.get("content_probe_records", 0) >= 1 and EXPECTED_CODES <= summary_codes
    evidence_ok = all(s in combined for s in ["中船特气", "投资者关系活动记录表", "昊华科技", "机构投资者调研", "华特气体", "凯美特气", "和远气体"])
    error_ok = any(e.get("source") == "cninfo_relation" for e in packet.get("errors", []))
    passed = not missing and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and source_log_ok and main_ok and boundary_ok and coverage_ok and evidence_ok and error_ok
    return passed, f"rows={len(rows)}, covered={packet.get('covered_tickers')}, title_source={packet.get('title_source_tickers')}, cninfo={packet.get('cninfo_relation_tickers')}, selected={packet.get('selected_rows')}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, coverage_ok={coverage_ok}, evidence_ok={evidence_ok}, error_ok={error_ok}"

def contract_order_announcement_complete() -> tuple[bool, str]:
    packet = load_json("data/contract_order_announcement_evidence.json")
    rows = packet.get("rows", [])
    summaries = packet.get("ticker_summaries", [])
    summary_codes = {str(r.get("ticker")) for r in summaries}
    required_keys = [
        "ticker",
        "company",
        "announcement_date",
        "announcement_type",
        "announcement_title",
        "contract_scope",
        "matched_field_groups",
        "snippets",
        "p0_disclosure_status",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/contract_order_announcement_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/contract_order_announcement_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join(
        [
            r.get("company", "")
            + r.get("announcement_title", "")
            + r.get("contract_scope", "")
            + "；".join(r.get("snippets", []))
            for r in rows
        ]
    )
    text_ok = all(s in data_md for s in ["合同/中标/供货协议公告全文扫描", "P0字段状态", "1.1904亿元", "1.1508亿元", "1.4822亿元", "电子气体平台订单金额样本"]) and "合同/中标/供货协议公告全文扫描" in analysis
    section_ok = "合同/中标/供货协议公告全文扫描" in section and "1.1904亿元" in section and "1.1508亿元" in section and "1.4822亿元" in section
    field_ok = "合同/中标/供货协议公告全文扫描" in field and "合同公告扫描不得把工业气体" in field
    provenance_ok = "合同/中标/供货协议公告全文扫描" in provenance and "东方财富公告索引" in provenance
    catalog_ok = "合同/中标/供货协议公告全文扫描" in catalog
    gap_ok = "合同/中标/供货协议公告全文扫描" in gaps
    hard_gap_ok = "合同/中标/供货协议公告全文扫描" in hard_gap and "六氟化钨采购合同约1.1904亿元" in hard_gap and "11种电子气体产品采购合同约1.4822亿元" in hard_gap
    source_log_ok = "合同/中标/供货协议公告全文扫描" in source_log
    audit_ok = "合同/中标/供货协议公告全文扫描" in audit and "六氟化钨采购合同约1.1904亿元" in audit and "HF/HCL/D2" in audit
    main_ok = "合同/中标/供货协议公告全文扫描" in main_text and "六氟化钨采购合同" in main_text and "三氟化氮销售合同" in main_text and "1.1904" in main_text and "1.1508" in main_text and "1.4822" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and packet.get("p0_closed_count") == 0 and "工业气体" in packet.get("use_boundary", "") and "平台订单可见度" in packet.get("use_boundary", "")
    coverage_ok = packet.get("covered_tickers") == 18 and packet.get("matched_tickers", 0) >= 1 and packet.get("selected_rows", 0) >= 1 and packet.get("theme_order_amount_rows", 0) >= 1 and packet.get("platform_order_amount_rows", 0) >= 1 and EXPECTED_CODES <= summary_codes
    evidence_ok = all(s in combined for s in ["中船特气", "WF6/NF3正式合同", "六氟化钨", "三氟化氮", "电子气体平台合同", "氟化氢", "氯化氢", "氘气", "新宙邦", "电解液"])
    passed = not missing and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and source_log_ok and audit_ok and main_ok and boundary_ok and coverage_ok and evidence_ok
    return passed, f"rows={len(rows)}, covered={packet.get('covered_tickers')}, matched={packet.get('matched_tickers')}, selected={packet.get('selected_rows')}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, audit_ok={audit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}, coverage_ok={coverage_ok}, evidence_ok={evidence_ok}"

def contract_economics_constraint_complete() -> tuple[bool, str]:
    packet = load_json("data/contract_economics_constraint.json")
    rows = packet.get("rows", [])
    required_keys = [
        "ticker",
        "company",
        "announcement_date",
        "product_scope",
        "amount_yuan",
        "tax_basis",
        "company_revenue_2025",
        "electronic_segment_revenue_2025",
        "amount_to_company_revenue",
        "amount_to_electronic_segment_revenue",
        "evidence_grade",
        "model_use",
        "blocked_fields",
        "ratio_note",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('product_scope')}:{k}")
    data_md = (BASE / "data/contract_economics_constraint.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/contract_economics_constraint.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    def has_amount(product: str, amount: float) -> bool:
        return any(product in r.get("product_scope", "") and abs(float(r.get("amount_yuan") or 0) - amount) < 1.0 for r in rows)
    values_ok = has_amount("六氟化钨", 119040600.0) and has_amount("三氟化氮", 115079200.0) and has_amount("电子气体平台", 148216408.0)
    ratios_ok = all((r.get("amount_to_company_revenue") or 0) > 0 and (r.get("amount_to_electronic_segment_revenue") or 0) > 0 for r in rows)
    counts_ok = packet.get("schema") == "astock.contract_economics_constraint.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("sample_rows") == 3 and packet.get("theme_single_product_order_rows") == 2 and packet.get("platform_order_rows") == 1 and packet.get("p0_economics_closed_count") == 0
    text_ok = all(s in data_md for s in ["合同金额经济性约束", "1.1904亿元", "1.1508亿元", "1.4822亿元", "金额/电子特气分部", "完整P0经济性关闭"]) and "合同金额经济性约束" in analysis
    section_ok = "合同金额经济性约束" in section and "金额/电子特气" in section and "19.27亿元" in section and "22.60亿元" in section
    field_ok = "合同金额经济性约束" in field and ("不得替代合同ASP" in field or "不得替代合同平均售价" in field)
    provenance_ok = "合同金额经济性约束" in provenance and "2025年电子特气分部收入" in provenance
    catalog_ok = "合同金额经济性约束" in catalog
    source_ok = "合同金额经济性约束" in source_log and "比例桥" in source_log
    hard_gap_ok = "合同金额经济性约束" in hard_gap and "收入上限" in hard_gap
    claim_ok = "合同金额经济性约束" in claim
    review_ok = "合同金额经济性约束补充" in review and "无缺失合同金额经济性约束包" in review
    main_ok = "合同金额经济性约束" in main_text and "电子特气分部收入" in main_text and "历史订单强度" in main_text and "收入桥上限" in main_text
    boundary_ok = "不关闭合同ASP" in packet.get("use_boundary", "") or "不替代合同ASP" in data_md or "不关闭合同平均售价" in data_md
    passed = not missing and values_ok and ratios_ok and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and source_ok and hard_gap_ok and claim_ok and review_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, missing={missing[:3]}, values_ok={values_ok}, ratios_ok={ratios_ok}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, source_ok={source_ok}, hard_gap_ok={hard_gap_ok}, claim_ok={claim_ok}, review_ok={review_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def order_durability_evidence_complete() -> tuple[bool, str]:
    packet = load_json("data/order_durability_evidence.json")
    rows = packet.get("rows", [])
    by_code = {str(r.get("ticker")): r for r in rows}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "order_evidence_stage",
        "latest_order_evidence_date",
        "order_evidence_summary",
        "contract_amount_evidence",
        "single_product_boundary",
        "revenue_recognition_gate",
        "next_validation_window",
        "durability_gate",
        "durable_order_allowed",
        "growth_eps_allowed",
        "valuation_use",
        "remaining_gap",
        "source_artifacts",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/order_durability_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/order_durability_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    completion = (BASE / "completion_audit_manifest.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    cssc = by_code.get("688146", {})
    codes_ok = EXPECTED_CODES <= set(by_code)
    counts_ok = (
        packet.get("schema") == "astock.order_durability_evidence.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 18
        and packet.get("growth_eps_allowed_count") == 0
        and packet.get("historical_theme_order_tickers", 0) >= 1
        and packet.get("platform_order_tickers", 0) >= 1
    )
    cssc_ok = cssc.get("order_evidence_stage") == "历史主题订单金额样本" and cssc.get("durability_gate") == "EVENT_VALIDATION_ONLY" and cssc.get("growth_eps_allowed") is False
    zero_growth_text_ok = "持续订单增长每股收益允许入模0/18" in data_md or "可直接进入持续订单增长每股收益：0/18" in data_md
    text_ok = all(s in data_md for s in ["订单持续性与收入确认耐久性证据", "历史主题订单金额样本"]) and zero_growth_text_ok and "必须等待持续订单" in data_md and "订单持续性与收入确认耐久性证据" in analysis
    section_ok = "订单持续性与收入确认耐久性证据" in section and "订单耐久性门禁" in section and "持续增长每股收益" in section
    field_ok = "订单持续性与收入确认耐久性证据" in field and "订单耐久性证据不得把历史订单" in field
    provenance_ok = "订单持续性与收入确认耐久性证据" in provenance and "持续订单增长每股收益" in provenance
    catalog_ok = "订单持续性与收入确认耐久性证据" in catalog
    gap_ok = "订单持续性与收入确认耐久性证据" in gaps and "持续订单增长每股收益允许入模0/18" in gaps
    hard_gap_ok = "订单持续性与收入确认耐久性证据" in hard_gap and "持续订单增长每股收益允许入模0/18" in hard_gap
    source_ok = "订单持续性与收入确认耐久性证据" in source_log and "持续订单增长每股收益允许入模0/18" in source_log
    audit_ok = "订单持续性与收入确认耐久性证据" in audit and "0/18" in audit
    claim_ok = "订单持续性与收入确认耐久性证据" in claim and "0/18" in claim
    review_ok = "订单持续性与收入确认耐久性补充" in review and "无缺失订单持续性与收入确认耐久性证据包" in review
    exhibit_ok = "订单持续性与收入确认耐久性证据" in exhibit
    completion_ok = "订单持续性与收入确认耐久性证据" in completion and "0/18可直接进入持续订单增长每股收益" in completion
    main_ok = "订单持续性与收入确认耐久性证据" in main_text and "订单耐久性门禁" in main_text and "持续订单增长每股收益" in main_text
    boundary_ok = "持续订单" in packet.get("use_boundary", "") and all("不得把" in r.get("evidence_boundary", "") for r in rows) and all((r.get("growth_eps_allowed") is False) for r in rows)
    passed = not missing and codes_ok and counts_ok and cssc_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and source_ok and audit_ok and claim_ok and review_ok and exhibit_ok and completion_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, missing={missing[:3]}, codes_ok={codes_ok}, counts_ok={counts_ok}, cssc_ok={cssc_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_ok={source_ok}, audit_ok={audit_ok}, claim_ok={claim_ok}, review_ok={review_ok}, exhibit_ok={exhibit_ok}, completion_ok={completion_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def price_margin_valuation_gate_complete() -> tuple[bool, str]:
    packet = load_json("data/price_margin_valuation_gate.json")
    rows = packet.get("rows", [])
    by_code = {str(r.get("ticker")): r for r in rows}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "price_proxy_layer",
        "company_price_evidence",
        "company_margin_evidence",
        "pass_through_evidence",
        "official_segment_margin",
        "single_product_boundary",
        "order_durability_gate",
        "price_margin_gate",
        "contract_average_price_allowed",
        "single_product_margin_allowed",
        "growth_eps_allowed",
        "valuation_use",
        "remaining_gap",
        "source_artifacts",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/price_margin_valuation_gate.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/price_margin_valuation_gate.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    completion = (BASE / "completion_audit_manifest.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    cssc = by_code.get("688146", {})
    counts_ok = (
        packet.get("schema") == "astock.price_margin_valuation_gate.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 18
        and packet.get("contract_average_price_allowed_count") == 0
        and packet.get("single_product_margin_allowed_count") == 0
        and packet.get("growth_eps_allowed_count") == 0
        and packet.get("official_segment_margin_tickers", 0) >= 4
        and packet.get("cost_margin_proxy_tickers", 0) == 18
        and packet.get("public_price_proxy_theme_count", 0) >= 3
    )
    codes_ok = EXPECTED_CODES <= set(by_code)
    cssc_ok = "招股书" in str(cssc.get("company_price_evidence", "")) and cssc.get("growth_eps_allowed") is False and ("当前合同" in str(cssc.get("price_margin_gate", "")) or "阻断" in str(cssc.get("price_margin_gate", "")))
    text_ok = all(s in data_md for s in ["价格与毛利入模门禁", "合同平均售价允许入模：0/18", "单品毛利允许入模：0/18", "增长每股收益允许入模：0/18"]) and "价格与毛利入模门禁" in analysis
    section_ok = "价格与毛利入模门禁" in section and "合同平均售价和单品毛利允许入模均为0/18" in section
    field_ok = "价格与毛利入模门禁" in field and "不得把公开价格" in field
    provenance_ok = "价格与毛利入模门禁" in provenance and "合同平均售价允许入模0/18" in provenance
    catalog_ok = "价格与毛利入模门禁" in catalog and "单品毛利入模0/18" in catalog
    gap_ok = "价格与毛利入模门禁" in gaps and "合同平均售价允许入模0/18" in gaps and "单品毛利允许入模0/18" in gaps
    hard_gap_ok = "价格与毛利入模门禁" in hard_gap and "单品毛利允许入模0/18" in hard_gap
    source_ok = "价格与毛利入模门禁" in source_log and "合同平均售价允许入模0/18" in source_log
    audit_ok = "价格与毛利入模门禁" in audit and "单品毛利允许入模0/18" in audit
    claim_ok = "价格与毛利入模门禁" in claim and "增长每股收益" in claim
    review_ok = "价格与毛利入模门禁补充" in review and "无缺失价格与毛利入模门禁包" in review
    exhibit_ok = "价格与毛利入模门禁" in exhibit
    completion_ok = "价格与毛利入模门禁" in completion and "合同平均售价允许入模0/18" in completion
    main_ok = "价格与毛利入模门禁" in main_text and "公司合同平均售价和当前单品毛利" in main_text
    boundary_ok = "当前0/18" in packet.get("use_boundary", "") and all("不得把" in r.get("evidence_boundary", "") for r in rows) and all((r.get("contract_average_price_allowed") is False and r.get("single_product_margin_allowed") is False and r.get("growth_eps_allowed") is False) for r in rows)
    passed = not missing and codes_ok and counts_ok and cssc_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and source_ok and audit_ok and claim_ok and review_ok and exhibit_ok and completion_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, missing={missing[:3]}, codes_ok={codes_ok}, counts_ok={counts_ok}, cssc_ok={cssc_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_ok={source_ok}, audit_ok={audit_ok}, claim_ok={claim_ok}, review_ok={review_ok}, exhibit_ok={exhibit_ok}, completion_ok={completion_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def earnings_disclosure_calendar_complete() -> tuple[bool, str]:
    packet = load_json("data/earnings_disclosure_calendar.json")
    rows = packet.get("rows", [])
    codes = {r.get("ticker") for r in rows}
    required_keys = [
        "ticker",
        "company",
        "next_report_type",
        "report_period",
        "appointment_date",
        "actual_publish_date",
        "disclosure_status",
        "next_quarter_validation",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/earnings_disclosure_calendar.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/earnings_disclosure_calendar.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch01_dashboard.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    cssc_ok = any(r.get("ticker") == "688146" and r.get("appointment_date") == "2026-07-18" and "半年报" in r.get("next_report_type", "") for r in rows)
    counts_ok = packet.get("schema") == "astock.earnings_disclosure_calendar.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 18 and packet.get("next_report_rows") == 18 and packet.get("upcoming_with_appointment_rows", 0) >= 18
    text_ok = all(s in data_md for s in ["业绩披露日历与验证窗口", "2026-07-18", "预约披露日", "不得替代实际财报结果"]) and "业绩披露日历与验证窗口" in analysis
    section_ok = "业绩披露日历与验证窗口" in section and "2026-07-18" in section and "预约披露日只触发模型刷新" in section
    field_ok = "业绩披露日历与验证窗口" in field and "业绩披露日历不得替代实际财报结果" in field
    provenance_ok = "业绩披露日历与验证窗口" in provenance and "东方财富业绩预约披露日历接口" in provenance
    catalog_ok = "东方财富业绩预约披露日历" in catalog and "2026-07-18" in catalog
    gap_ok = "业绩披露日历与验证窗口" in gaps and "预约披露日不得替代实际财报结果" in gaps
    hard_gap_ok = "业绩披露日历与验证窗口" in hard_gap and "预约披露日之后必须用实际财报" in hard_gap
    audit_ok = "业绩披露日历与验证窗口" in audit and "2026-07-18" in audit
    claim_ok = "2026年半年报预约披露日" in claim and "2026-07-18" in claim
    review_ok = "业绩披露日历与验证窗口补充" in review
    exhibit_ok = "业绩披露日历与验证窗口" in exhibit
    main_ok = "业绩披露日历与验证窗口" in main_text and "2026-07-18" in main_text and "预约披露日" in main_text
    boundary_ok = "不得替代实际财报结果" in packet.get("use_boundary", "") and all("不证明订单" in r.get("evidence_boundary", "") or "不得替代" in r.get("evidence_boundary", "") for r in rows)
    passed = EXPECTED_CODES <= codes and not missing and cssc_ok and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and audit_ok and claim_ok and review_ok and exhibit_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, covered={packet.get('covered_tickers')}, missing={missing[:3]}, cssc_ok={cssc_ok}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, audit_ok={audit_ok}, claim_ok={claim_ok}, review_ok={review_ok}, exhibit_ok={exhibit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def performance_forecast_complete() -> tuple[bool, str]:
    packet = load_json("data/performance_forecast_evidence.json")
    rows = packet.get("rows", [])
    summaries = packet.get("ticker_summaries", [])
    codes = {r.get("ticker") for r in summaries}
    required_row_keys = [
        "ticker",
        "company",
        "announcement_date",
        "announcement_type",
        "announcement_title",
        "metric_status",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_row_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    required_summary_keys = [
        "ticker",
        "company",
        "matched_performance_titles",
        "parsed_performance_records",
        "latest_performance_date",
        "latest_performance_type",
        "evidence_status",
        "valuation_use",
    ]
    for r in summaries:
        for k in required_summary_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:summary:{k}")
    data_md = (BASE / "data/performance_forecast_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/performance_forecast_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch01_dashboard.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    counts_ok = packet.get("schema") == "astock.performance_forecast_evidence.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 18 and packet.get("matched_tickers", 0) >= 1 and packet.get("selected_rows", 0) >= 1
    text_ok = all(s in data_md for s in ["业绩预告/快报公告证据", "排除业绩说明会", "不能替代单品订单"]) and "业绩预告/快报公告证据" in analysis
    section_ok = "业绩预告/快报公告证据" in section and "业绩预告和快报证据进一步回答" in section and "排除业绩说明会" in section
    field_ok = "业绩预告/快报公告证据" in field and "业绩预告/快报不得替代单品订单" in field
    provenance_ok = "业绩预告/快报公告证据" in provenance and "东方财富公告索引与公告正文接口" in provenance
    catalog_ok = "东方财富业绩预告/快报公告扫描" in catalog
    gap_ok = "业绩预告/快报公告证据" in gaps and "业绩预告/快报只能验证公司层" in gaps
    hard_gap_ok = "业绩预告/快报公告只验证公司层利润预警" in hard_gap
    audit_ok = "业绩预告/快报公告证据" in audit and "不得单独上修增长每股收益" in audit
    claim_ok = "业绩预告/快报公告可用于验证公司层利润预警" in claim
    review_ok = "业绩预告/快报公告证据补充" in review
    exhibit_ok = "业绩预告/快报公告证据" in exhibit
    main_ok = "业绩预告/快报公告证据" in main_text and "业绩预告和快报证据进一步回答" in main_text
    boundary_ok = "不得替代WF6/NF3/电子材料/高纯钨材单品订单" in packet.get("use_boundary", "") and all("不得替代" in r.get("evidence_boundary", "") for r in rows)
    passed = EXPECTED_CODES <= codes and len(summaries) == 18 and not missing and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and audit_ok and claim_ok and review_ok and exhibit_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, summaries={len(summaries)}, matched={packet.get('matched_tickers')}, selected={packet.get('selected_rows')}, missing={missing[:3]}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, audit_ok={audit_ok}, claim_ok={claim_ok}, review_ok={review_ok}, exhibit_ok={exhibit_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def regulatory_inquiry_complete() -> tuple[bool, str]:
    packet = load_json("data/regulatory_inquiry_evidence.json")
    rows = packet.get("rows", [])
    summaries = packet.get("ticker_summaries", [])
    codes = {r.get("ticker") for r in summaries}
    required_row_keys = [
        "ticker",
        "company",
        "announcement_date",
        "inquiry_type",
        "announcement_title",
        "field_status",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_row_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    required_summary_keys = [
        "ticker",
        "company",
        "matched_inquiry_titles",
        "parsed_inquiry_records",
        "latest_inquiry_date",
        "latest_inquiry_type",
        "evidence_status",
        "valuation_use",
    ]
    for r in summaries:
        for k in required_summary_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:summary:{k}")
    data_md = (BASE / "data/regulatory_inquiry_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/regulatory_inquiry_evidence.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    claim = (BASE / "data/claim_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    counts_ok = packet.get("schema") == "astock.regulatory_inquiry_evidence.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 18 and packet.get("matched_tickers", 0) >= 1 and packet.get("selected_rows", 0) >= 1
    text_ok = all(s in data_md for s in ["问询/审核回复公告证据", "不能把问询标题", "合同平均售价"]) and "问询/审核回复公告证据" in analysis
    section_ok = "问询/审核回复公告证据" in section and "问询/审核回复层比投关记录更正式" in section and "不改变增长每股收益信用" in section
    field_ok = "问询/审核回复公告证据" in field and "问询/审核回复证据不得把问询标题" in field
    provenance_ok = "问询/审核回复公告证据" in provenance and "东方财富公告索引与公告正文接口" in provenance
    catalog_ok = "东方财富问询/审核回复公告扫描" in catalog
    gap_ok = "问询/审核回复公告证据" in gaps and "问询标题、募投说明或泛化回复不得替代单品订单" in gaps
    hard_gap_ok = "问询/审核回复公告只提供交易所或监管层硬字段复核入口" in hard_gap
    audit_ok = "问询/审核回复公告证据" in audit and "只有回复正文披露可量化单品订单" in audit
    claim_ok = "问询/审核回复公告可用于补强交易所或监管层硬字段复核" in claim
    review_ok = "问询/审核回复公告证据补充" in review
    exhibit_ok = "问询/审核回复公告证据" in exhibit
    source_log_ok = "问询/审核回复公告证据" in source_log and "可量化单品订单" in source_log
    main_ok = "问询/审核回复公告证据" in main_text and "不改变增长每股收益信用" in main_text
    boundary_ok = "不得替代单品订单" in packet.get("use_boundary", "") and all("不得把问询标题" in r.get("evidence_boundary", "") or "不得替代" in r.get("evidence_boundary", "") for r in rows)
    passed = EXPECTED_CODES <= codes and len(summaries) == 18 and not missing and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and audit_ok and claim_ok and review_ok and exhibit_ok and source_log_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, summaries={len(summaries)}, matched={packet.get('matched_tickers')}, selected={packet.get('selected_rows')}, missing={missing[:3]}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, audit_ok={audit_ok}, claim_ok={claim_ok}, review_ok={review_ok}, exhibit_ok={exhibit_ok}, source_log_ok={source_log_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def official_single_product_revenue_boundary_complete() -> tuple[bool, str]:
    packet = load_json("data/official_single_product_revenue_boundary.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"600378", "688146", "688549", "688268", "002971"}
    required_keys = [
        "ticker",
        "company",
        "product_scope",
        "official_metric",
        "quantified_value",
        "source_basis",
        "what_it_proves",
        "valuation_use",
        "still_missing",
        "p0_status",
        "source_ids",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/official_single_product_revenue_boundary.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/official_single_product_revenue_boundary.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    dashboard = (BASE / "data/data_completeness_dashboard.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join(
        [
            r.get("company", "")
            + r.get("product_scope", "")
            + r.get("official_metric", "")
            + r.get("quantified_value", "")
            + r.get("p0_status", "")
            for r in rows
        ]
    )
    values_ok = all(
        s in combined
        for s in [
            "0.13%",
            "1.1904亿元",
            "1.1508亿元",
            "1.4822亿元",
            "269.19/533.75/838.27/550.15吨",
            "8.27%/5.76%/5.16%",
            "600吨",
            "未披露占比",
            "0业绩贡献/无实质性订单",
        ]
    )
    counts_ok = (
        packet.get("schema") == "astock.official_single_product_revenue_boundary.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 5
        and packet.get("quantified_rows", 0) >= 8
        and packet.get("single_product_amount_rows") == 2
        and packet.get("revenue_ratio_rows") == 1
        and packet.get("negative_boundary_rows") == 3
    )
    text_ok = all(s in data_md for s in ["官方单品收入/订单金额边界证据", "0.13%", "1.1904亿元", "1.1508亿元", "1.4822亿元", "负面边界", "合同平均售价"]) and "官方单品收入/订单金额边界证据" in analysis
    section_ok = "官方单品收入/订单金额边界" in section and "0.13" in section and "1.1904" in section and "1.1508" in section and "合同平均售价" in section
    field_ok = "官方单品收入/订单金额边界" in field and "不得替代合同平均售价" in field
    provenance_ok = "官方单品收入/订单金额边界" in provenance and "公司澄清" in provenance and "招股说明书" in provenance
    catalog_ok = "官方单品收入/订单金额边界" in catalog
    gap_ok = "官方单品收入/订单金额边界证据" in gaps and "昊华科技WF6收入占比0.13%" in gaps
    hard_gap_ok = "官方单品收入/订单金额边界包" in hard_gap and "昊华科技WF6收入占比0.13%" in hard_gap
    dashboard_ok = "官方单品收入/订单金额边界" in dashboard
    audit_ok = "官方单品收入/订单金额边界" in audit and "不得替代合同平均售价" in audit
    review_ok = "官方单品收入/订单金额边界补充" in review and "无缺失官方单品收入/订单金额边界包" in review
    main_ok = "官方单品收入/订单金额边界" in main_text and "0.13" in main_text and "1.1904" in main_text and "1.1508" in main_text and "负面边界" in main_text
    boundary_ok = "不关闭合同ASP" in packet.get("use_boundary", "") or "不关闭合同平均售价" in data_md or "不得替代合同平均售价" in data_md
    passed = required_tickers <= tickers and len(rows) >= 9 and not missing and values_ok and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and dashboard_ok and audit_ok and review_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, values_ok={values_ok}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, dashboard_ok={dashboard_ok}, audit_ok={audit_ok}, review_ok={review_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def semiconductor_tungsten_material_boundary_complete() -> tuple[bool, str]:
    packet = load_json("data/semiconductor_tungsten_material_boundary.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"600549", "000657", "002378", "002842"}
    required_keys = [
        "ticker",
        "company",
        "annual_report_anchor",
        "semiconductor_relevance",
        "customer_order_status",
        "revenue_margin_status",
        "valuation_use",
        "model_gate",
        "source_artifacts",
        "source_ids",
        "remaining_gap",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/semiconductor_tungsten_material_boundary.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/semiconductor_tungsten_material_boundary.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    dashboard = (BASE / "data/data_completeness_dashboard.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join(
        [
            r.get("company", "")
            + r.get("annual_report_anchor", "")
            + r.get("semiconductor_relevance", "")
            + r.get("customer_order_status", "")
            + r.get("model_gate", "")
            for r in rows
        ]
    )
    values_ok = all(
        s in combined
        for s in [
            "厦门钨业",
            "中钨高新",
            "章源钨业",
            "翔鹭钨业",
            "细钨丝销量1,292亿米",
            "硬质合金销售10,756吨",
            "钨粉销量4,928吨",
            "粉末制品收入占比66.9%",
        ]
    )
    counts_ok = (
        packet.get("schema") == "astock.semiconductor_tungsten_material_boundary.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 4
        and packet.get("growth_eps_allowed_count") == 0
        and "0/4" in packet.get("use_boundary", "")
    )
    text_ok = all(s in data_md for s in ["半导体高纯钨材边界证据", "0/4", "厦门钨业", "中钨高新", "章源钨业", "翔鹭钨业", "不得替代"]) and "半导体高纯钨材边界证据" in analysis
    section_ok = "半导体高纯钨材边界" in section and "0/4" in section and "光伏钨丝" in section and "半导体客户" in section and "订单金额" in section
    field_ok = "半导体高纯钨材边界证据" in field and "不得替代半导体客户" in field
    provenance_ok = "半导体高纯钨材边界证据" in provenance and "2025年报主营构成" in provenance
    catalog_ok = "半导体高纯钨材边界证据" in catalog
    gap_ok = "半导体高纯钨材边界证据" in gaps and "0/4可进入半导体高纯钨材增长每股收益" in gaps
    hard_gap_ok = "半导体高纯钨材边界证据包" in hard_gap and "0/4可进入半导体高纯钨材增长每股收益" in hard_gap
    dashboard_ok = "半导体高纯钨材边界" in dashboard
    audit_ok = "半导体高纯钨材边界证据" in audit and "0/4可进入半导体高纯钨材增长每股收益" in audit
    review_ok = "半导体高纯钨材边界补充" in review and "无缺失半导体高纯钨材边界包" in review
    source_ok = "半导体高纯钨材客户、订单和收入" in source_log and "0/4可进入半导体高纯钨材增长每股收益" in source_log
    main_ok = "半导体高纯钨材边界" in main_text and "0/4" in main_text and "高纯钨材增长每股收益" in main_text
    boundary_ok = "不得替代半导体客户、订单、合同ASP、收入占比或单品毛利" in packet.get("use_boundary", "") or "不得替代半导体客户" in data_md
    passed = required_tickers <= tickers and len(rows) == 4 and not missing and values_ok and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and dashboard_ok and audit_ok and review_ok and source_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, values_ok={values_ok}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, dashboard_ok={dashboard_ok}, audit_ok={audit_ok}, review_ok={review_ok}, source_ok={source_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def fluorinated_electronic_material_boundary_complete() -> tuple[bool, str]:
    packet = load_json("data/fluorinated_electronic_material_boundary.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"600160", "603379", "605020", "002407", "300037", "603505"}
    required_keys = [
        "ticker",
        "company",
        "base_cashflow_anchor",
        "electronic_material_relevance",
        "customer_order_status",
        "spread_revenue_margin_status",
        "valuation_use",
        "model_gate",
        "source_artifacts",
        "source_ids",
        "remaining_gap",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/fluorinated_electronic_material_boundary.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/fluorinated_electronic_material_boundary.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    dashboard = (BASE / "data/data_completeness_dashboard.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    review = (BASE / "review_log.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    combined = "\n".join(
        [
            r.get("company", "")
            + r.get("base_cashflow_anchor", "")
            + r.get("electronic_material_relevance", "")
            + r.get("customer_order_status", "")
            + r.get("model_gate", "")
            for r in rows
        ]
    )
    values_ok = all(
        s in combined
        for s in [
            "巨化股份",
            "三美股份",
            "永和股份",
            "多氟多",
            "新宙邦",
            "金石资源",
            "240,826",
            "76,910",
            "60,281",
        ]
    )
    counts_ok = (
        packet.get("schema") == "astock.fluorinated_electronic_material_boundary.v1"
        and packet.get("gate_status") == "CONDITIONAL"
        and packet.get("covered_tickers") == 6
        and packet.get("growth_eps_allowed_count") == 0
        and packet.get("refrigerant_base_cashflow_allowed_count") == 3
        and "0/6" in packet.get("use_boundary", "")
    )
    text_ok = all(s in data_md for s in ["含氟电子材料边界证据", "0/6", "巨化股份", "三美股份", "永和股份", "多氟多", "新宙邦", "金石资源", "不得替代"]) and "含氟电子材料边界证据" in analysis
    section_ok = "含氟电子材料边界" in section and "0/6" in section and "制冷剂配额" in section and "单品价差" in section and "电子材料客户" in section
    field_ok = "含氟电子材料边界证据" in field and "不得替代电子材料客户" in field
    provenance_ok = "含氟电子材料边界证据" in provenance and "HFC配额" in provenance
    catalog_ok = "含氟电子材料边界证据" in catalog
    gap_ok = "含氟电子材料边界证据" in gaps and "0/6可进入含氟电子材料增长" in gaps
    hard_gap_ok = "含氟电子材料边界证据包" in hard_gap and "0/6进入含氟电子材料增长每股收益" in hard_gap
    dashboard_ok = "含氟电子材料边界" in dashboard
    audit_ok = "含氟电子材料边界证据" in audit and "0/6可进入含氟电子材料增长每股收益" in audit
    review_ok = "含氟电子材料边界补充" in review and "无缺失含氟电子材料边界包" in review
    source_ok = "含氟电子材料客户、订单和单品价差" in source_log and "0/6可进入含氟电子材料增长每股收益" in source_log
    main_ok = "含氟电子材料边界" in main_text and "0/6" in main_text and "含氟电子材料增长每股收益" in main_text
    boundary_ok = "不得替代电子材料客户、订单、单品价差、收入占比或单品毛利" in packet.get("use_boundary", "") or "不得替代含氟电子材料客户" in data_md
    passed = required_tickers <= tickers and len(rows) == 6 and not missing and values_ok and counts_ok and text_ok and section_ok and field_ok and provenance_ok and catalog_ok and gap_ok and hard_gap_ok and dashboard_ok and audit_ok and review_ok and source_ok and main_ok and boundary_ok
    return passed, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, values_ok={values_ok}, counts_ok={counts_ok}, text_ok={text_ok}, section_ok={section_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, dashboard_ok={dashboard_ok}, audit_ok={audit_ok}, review_ok={review_ok}, source_ok={source_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def trading_risk_complete() -> tuple[bool, str]:
    packet = load_json("data/trading_risk_announcement_snapshot.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"688146", "688549", "600378", "002971"}
    required_keys = [
        "ticker",
        "company",
        "announcement_date",
        "risk_event",
        "price_move",
        "index_comparison",
        "company_pe",
        "industry_pe",
        "official_boundary",
        "source_ids",
        "valuation_use",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    md = (BASE / "data/trading_risk_announcement_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/trading_risk_announcement_snapshot.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["交易风险公告与估值热度快照", "573.30", "388.77", "180.63", "21.42"]) and "交易风险公告与估值热度快照" in analysis
    main_ok = "交易风险公告与估值热度" in main_text and "市场锚" in main_text and ("573.30" in main_text or "388.77" in main_text)
    field_ok = "交易风险公告与估值热度" in field and "交易风险公告不得替代订单" in field
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不能替代基本面目标价" in packet.get("use_boundary", "")
    return len(rows) >= 4 and required_tickers <= tickers and not missing and text_ok and main_ok and field_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, field_ok={field_ok}, boundary_ok={boundary_ok}"

def technical_process_complete() -> tuple[bool, str]:
    packet = load_json("data/technical_process_evidence.json")
    rows = packet.get("rows", [])
    layers = {r.get("process_layer") for r in rows}
    required_layers = {"前道钨源", "钨连接/金属化", "接触孔/通孔填充", "供应规格/纯度控制"}
    source_ids = {sid for r in rows for sid in r.get("source_ids", [])}
    required_sources = {"S20", "S21", "S22", "S23"}
    required_keys = [
        "process_layer",
        "evidence_point",
        "semiconductor_relevance",
        "demand_link",
        "source_ids",
        "valuation_use",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('process_layer')}:{k}")
    md = (BASE / "data/technical_process_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/technical_process_evidence.md").read_text(encoding="utf-8")
    tech = (BASE / "analysis/technology_architecture.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    source_md = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["制程/材料功能证据包", "CVD", "ALD", "接触孔", "痕量金属"]) and "制程/材料功能证据包" in analysis and "制程/材料功能证据" in tech
    main_compact = "".join(main_text.split())
    main_ok = "制程/材料功能证据" in main_text and "钨金属化" in main_compact and "不替代A股公司客户认证" in main_compact
    field_ok = "制程/材料功能证据" in field and "制程功能证据不得替代客户认证" in field
    source_ok = all(s in source_md for s in ["Linde Electronics", "Lam Research", "Applied Materials", "Air Products"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不能替代A股公司客户认证" in packet.get("use_boundary", "")
    return len(rows) >= 4 and required_layers <= layers and required_sources <= source_ids and not missing and text_ok and main_ok and field_ok and source_ok and boundary_ok, f"rows={len(rows)}, sources={sorted(source_ids)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, field_ok={field_ok}, source_ok={source_ok}, boundary_ok={boundary_ok}"

def policy_export_control_complete() -> tuple[bool, str]:
    packet = load_json("data/policy_export_control_evidence.json")
    rows = packet.get("rows", [])
    layers = {r.get("policy_layer") for r in rows}
    required_layers = {"实施时点与法律框架", "钨相关材料", "固态钨与高密度合金", "技术与资料", "政策目的与许可边界"}
    source_ids = {sid for r in rows for sid in r.get("source_ids", [])}
    required_sources = {"S24", "S25"}
    required_keys = [
        "policy_layer",
        "official_evidence",
        "covered_items",
        "market_relevance",
        "source_ids",
        "valuation_use",
        "monitoring_item",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('policy_layer')}:{k}")
    md = (BASE / "data/policy_export_control_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/policy_export_control_evidence.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    source_md = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["政策/出口管制官方证据包", "仲钨酸铵", "氧化钨", "碳化钨", "出口许可"]) and "政策/出口管制官方证据包" in analysis
    main_ok = "政策/出口管制官方证据" in main_text and "仲钨酸铵" in main_text and "资源安全溢价" in main_text
    field_ok = "政策/出口管制官方证据" in field and "政策管制证据不得替代公司实际销售价格" in field
    source_ok = all(s in source_md for s in ["商务部政策摘要", "商务部新闻发言人"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代公司实际销售价格" in packet.get("use_boundary", "")
    return len(rows) >= 5 and required_layers <= layers and required_sources <= source_ids and not missing and text_ok and main_ok and field_ok and source_ok and boundary_ok, f"rows={len(rows)}, sources={sorted(source_ids)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, field_ok={field_ok}, source_ok={source_ok}, boundary_ok={boundary_ok}"

def company_product_capability_complete() -> tuple[bool, str]:
    packet = load_json("data/company_product_capability_evidence.json")
    rows = packet.get("rows", [])
    entities = {r.get("ticker") for r in rows}
    required_entities = {"688146", "688549", "600378", "002971", "标准化层"}
    source_ids = {sid for r in rows for sid in r.get("source_ids", [])}
    required_sources = {"S2", "S15", "S16", "S26", "S27", "S28"}
    required_keys = [
        "ticker",
        "company",
        "capability_layer",
        "official_evidence",
        "product_or_standard_detail",
        "source_ids",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    md = (BASE / "data/company_product_capability_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/company_product_capability_evidence.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    source_md = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["公司产品能力官方证据包", "中船特气", "中巨芯-U", "6N", "国家标准项目"]) and "公司产品能力官方证据包" in analysis
    main_compact = "".join(main_text.split())
    main_ok = "公司产品能力官方证据" in main_text and "产品能力证据" in main_text and ("不能替代客户认证" in main_compact or "不替代客户认证" in main_compact)
    field_ok = "公司产品能力官方证据" in field and "公司产品能力证据不得替代客户认证" in field
    source_ok = all(s in source_md for s in ["中船特气官网", "中巨芯官网", "全国标准信息公共服务平台"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代客户认证" in packet.get("use_boundary", "")
    return len(rows) >= 5 and required_entities <= entities and required_sources <= source_ids and not missing and text_ok and main_ok and field_ok and source_ok and boundary_ok, f"rows={len(rows)}, sources={sorted(source_ids)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, field_ok={field_ok}, source_ok={source_ok}, boundary_ok={boundary_ok}"

def capacity_project_evidence_complete() -> tuple[bool, str]:
    packet = load_json("data/capacity_project_evidence.json")
    rows = packet.get("rows", [])
    layers = {r.get("project_layer") for r in rows}
    required_layers = {"投资公告", "环评分期与总产能", "工艺装置/车间范围", "现有工程/环保手续"}
    source_ids = {sid for r in rows for sid in r.get("source_ids", [])}
    required_sources = {"S29", "S30", "S31"}
    required_keys = [
        "ticker",
        "company",
        "project_layer",
        "official_evidence",
        "capacity_or_scope",
        "source_ids",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('project_layer')}:{k}")
    md = (BASE / "data/capacity_project_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/capacity_project_evidence.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    source_md = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in md for s in ["项目/产能建设官方证据包", "3383", "91305", "六氟化钨六氟化钼车间"]) and "项目/产能建设官方证据包" in analysis
    main_ok = "项目/产能建设官方证据" in main_text and "不替代WF6单品产能拆分" in main_compact and "六氟化钨六氟化钼车间" in main_compact
    field_ok = "项目/产能建设官方证据" in field and "项目产能证据不得替代WF6单品产能拆分" in field
    source_ok = all(s in source_md for s in ["年产3383吨高纯硫化氢", "环评征求意见稿", "环评第一次公示"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代WF6单品产能拆分" in packet.get("use_boundary", "")
    return len(rows) >= 4 and required_layers <= layers and required_sources <= source_ids and not missing and text_ok and main_ok and field_ok and source_ok and boundary_ok, f"rows={len(rows)}, sources={sorted(source_ids)}, missing={missing[:3]}, text_ok={text_ok}, main_ok={main_ok}, field_ok={field_ok}, source_ok={source_ok}, boundary_ok={boundary_ok}"

def external_evidence_complete() -> tuple[bool, str]:
    probe = load_json("data/external_evidence_probe.json")
    rows = probe.get("rows", [])
    required_tickers = {"688146", "688549", "600378", "688268", "主题层"}
    tickers = {r.get("ticker") for r in rows}
    missing = []
    for r in rows:
        for k in ["evidence_area", "evidence_found", "source_ids", "still_missing", "valuation_gate"]:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in main_text for s in ["公告/互动/研报补证结果", "外部补证摘要", "公开个股研报快照"])
    return required_tickers <= tickers and not missing and text_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}"

def broker_research_complete() -> tuple[bool, str]:
    packet = load_json("data/broker_research_snapshot.json")
    rows = packet.get("rows", [])
    covered = packet.get("covered_tickers", 0)
    real_covered = packet.get("real_covered_tickers", 0)
    recent_covered = packet.get("recent_covered_tickers", 0)
    forecast_covered = packet.get("forecast_covered_tickers", 0)
    gap_count = packet.get("gap_ticker_count", 0)
    text = (BASE / "analysis/broker_research_snapshot.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    rows_ok = len(rows) >= 18 and covered >= 18 and real_covered >= 16 and recent_covered >= 14 and forecast_covered >= 12 and gap_count <= 4
    text_ok = all(s in text for s in ["公开个股研报快照", "不是付费Wind/Choice一致预期", "缺口行不参与券商锚估值权重", "样本陈旧", "缺少2026E每股收益/市盈率"]) and all(s in main_text for s in ["公开个股研报快照（1）", "公开个股研报快照（2）"])
    return rows_ok and text_ok, f"rows={len(rows)}, covered={covered}, real_covered={real_covered}, recent_covered={recent_covered}, forecast_covered={forecast_covered}, gap_count={gap_count}, text_ok={text_ok}"


def public_broker_coverage_complete() -> tuple[bool, str]:
    packet = load_json("data/public_broker_coverage_history.json")
    rows = packet.get("rows", [])
    coverage = packet.get("coverage", {})
    required_keys = [
        "ticker",
        "company",
        "total_sample_count",
        "recent_sample_count",
        "forecast_sample_count",
        "institution_count",
        "institutions",
        "rating_mix",
        "latest_report_date",
        "latest_institution",
        "eps_2026_range",
        "eps_2027_range",
        "coverage_quality",
        "anchor_eligibility",
        "target_price_history_status",
        "evidence_boundary",
        "sample_details",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    qualities = {r.get("coverage_quality") for r in rows}
    md = (BASE / "data/public_broker_coverage_history.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/public_broker_coverage_history.md").read_text(encoding="utf-8")
    valuation = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    rows_ok = (
        len(rows) == 18
        and coverage.get("public_sample_tickers", 0) == 18
        and coverage.get("recent_sample_tickers", 0) >= 16
        and coverage.get("forecast_sample_tickers", 0) >= 16
    )
    text_ok = all(s in md for s in ["公开券商覆盖历史质量", "53条样本", "目标价历史继续标记为未披露", "使用边界"]) and "公开券商覆盖历史质量" in analysis
    downstream_ok = "公开券商覆盖历史质量" in valuation and "公开券商覆盖历史质量" in field and "公开券商覆盖历史质量" in provenance and "公开券商覆盖历史质量包" in catalog and "公开券商覆盖历史质量包已补充" in hard_gap and "公开券商覆盖历史质量" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代券商全文模型" in packet.get("use_boundary", "") and "目标价历史" in main_compact
    return rows_ok and not missing and {"近期多样本多年度", "样本陈旧"} <= qualities and text_ok and downstream_ok and boundary_ok, f"rows={len(rows)}, coverage={coverage}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, boundary_ok={boundary_ok}"


def public_broker_forecast_complete() -> tuple[bool, str]:
    packet = load_json("data/public_broker_forecast_evidence.json")
    rows = packet.get("rows", [])
    coverage = packet.get("coverage", {})
    required_keys = [
        "ticker",
        "company",
        "sample_count",
        "forecast_sample_count",
        "institutions",
        "eps_2026_range",
        "eps_2026_avg",
        "pe_2026_avg",
        "astock_eps_2026e",
        "astock_vs_public_broker_eps_pct",
        "forecast_quality",
        "external_anchor_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if k in {"eps_2026_avg", "pe_2026_avg", "astock_vs_public_broker_eps_pct"} and r.get("forecast_sample_count") == 0:
                continue
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    qualities = {r.get("forecast_quality") for r in rows}
    md = (BASE / "data/public_broker_forecast_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/public_broker_forecast_evidence.md").read_text(encoding="utf-8")
    valuation = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    rows_ok = len(rows) == 18 and coverage.get("forecast_tickers", 0) >= 12 and coverage.get("multi_sample_forecast_tickers", 0) >= 8
    text_ok = all(s in md for s in ["公开券商预测分歧与本报告差异", "不是Wind/Choice一致预期", "本报告每股收益", "使用边界"]) and "公开券商预测分歧与本报告差异" in analysis
    downstream_ok = "公开券商预测分歧" in valuation and "公开券商预测分歧" in field and "公开券商预测分歧与本报告差异" in main_compact
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代付费一致预期" in packet.get("use_boundary", "")
    return rows_ok and not missing and {"多样本可用", "样本陈旧"} <= qualities and text_ok and downstream_ok and boundary_ok, f"rows={len(rows)}, forecast={coverage.get('forecast_tickers')}, multi={coverage.get('multi_sample_forecast_tickers')}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, boundary_ok={boundary_ok}"

def public_broker_fulltext_complete() -> tuple[bool, str]:
    packet = load_json("data/public_broker_fulltext_evidence.json")
    rows = packet.get("rows", [])
    coverage = packet.get("coverage", {})
    required_keys = [
        "ticker",
        "company",
        "theme",
        "report_date",
        "report_name",
        "rating",
        "pages",
        "source_file",
        "text_file",
        "text_chars",
        "fulltext_status",
        "target_price_signal",
        "assumption_signal",
        "forecast_signal",
        "product_terms",
        "customer_certification_terms",
        "order_delivery_terms",
        "price_margin_terms",
        "risk_terms",
        "p0_evidence_signal",
        "fulltext_review_use",
        "broker_revenue_2026e_source",
        "broker_net_profit_2026e_source",
        "broker_forecast_model_parse_status",
        "broker_forecast_model_quality",
        "broker_forecast_model_use",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        if r.get("pages", 0) <= 0 or r.get("text_chars", 0) <= 0:
            missing.append(f"{r.get('ticker')}:pages_or_text")
        for k in ["source_file", "text_file"]:
            rel = r.get(k)
            if rel and not (BASE / rel).exists():
                missing_sources.append(f"{r.get('ticker')}:{rel}")
    md = (BASE / "data/public_broker_fulltext_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/public_broker_fulltext_evidence.md").read_text(encoding="utf-8")
    valuation = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    rows_ok = (
        len(rows) == 18
        and coverage.get("covered_tickers", 0) == 18
        and coverage.get("archived_pdf_count", 0) == 18
        and coverage.get("extracted_text_count", 0) == 18
        and coverage.get("forecast_table_count", 0) >= 10
        and coverage.get("model_revenue_2026e_tickers", 0) >= 12
        and coverage.get("model_net_profit_2026e_tickers", 0) >= 12
        and coverage.get("model_revenue_and_profit_2026e_tickers", 0) >= 10
        and coverage.get("product_term_tickers", 0) >= 12
        and coverage.get("price_margin_term_tickers", 0) >= 8
    )
    keyword_ok = any("人工复核入口" in str(r.get("p0_evidence_signal", "")) for r in rows) and all("fulltext_review_use" in r for r in rows)
    model_ok = any(r.get("broker_revenue_2026e_cny_billion") is not None and r.get("broker_net_profit_2026e_cny_billion") is not None for r in rows) and all("broker_forecast_model_use" in r for r in rows)
    text_ok = all(s in md for s in ["公开券商全文PDF证据", "18篇", "不是付费一致预期", "来源清单", "全文预测模型表字段", "2026E营收", "全文关键词证据矩阵", "P0复核结论"]) and "公开券商全文PDF证据" in analysis and "全文预测模型表字段" in analysis and "全文关键词证据矩阵" in analysis
    downstream_ok = all("公开券商全文PDF证据" in text for text in [valuation, audit, field, provenance, catalog, hard_gap]) and "公开券商全文" in main_text
    source_ok = (BASE / str(packet.get("source_manifest", ""))).exists() and not missing_sources
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代付费一致预期" in packet.get("use_boundary", "")
    return rows_ok and not missing and source_ok and keyword_ok and model_ok and text_ok and downstream_ok and boundary_ok, f"rows={len(rows)}, coverage={coverage}, missing={missing[:3]}, missing_sources={missing_sources[:3]}, keyword_ok={keyword_ok}, model_ok={model_ok}, text_ok={text_ok}, downstream_ok={downstream_ok}, boundary_ok={boundary_ok}"


def business_segment_complete() -> tuple[bool, str]:
    packet = load_json("data/business_segment_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required = {"segment", "revenue", "revenue_share"}
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    has_margin = {
        code
        for code in covered
        if any(r.get("ticker") == code and r.get("gross_margin") is not None for r in rows)
    }
    text = (BASE / "analysis/business_segment_snapshot.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = "主营构成" in text and "产品收入占比" in text and "主营构成与产品毛利率" in main_text
    return len(covered) == 18 and len(has_margin) == 18 and len(rows) >= 50 and not missing and text_ok, f"rows={len(rows)}, covered={len(covered)}, margin_covered={len(has_margin)}, missing={missing[:3]}, text_ok={text_ok}"

def official_segment_table_complete() -> tuple[bool, str]:
    packet = load_json("data/official_segment_table_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"688146", "688549", "600378", "688268"}
    segments = {r.get("segment") for r in rows}
    required_segments = {"电子特种气体", "电子特种气体及前驱体", "电子化学品", "光刻及其他混合气体"}
    required_keys = [
        "ticker",
        "company",
        "segment",
        "revenue",
        "cost",
        "gross_margin_pct",
        "revenue_yoy_pct",
        "report_path",
        "line_reference",
        "official_evidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{r.get('segment')}:{k}")
        rel = r.get("report_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/official_segment_table_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/official_segment_table_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["官方年报分产品/分部证据", "电子特种气体", "电子化学品", "光刻及其他混合气体", "不替代WF6"]) and "官方年报分产品/分部证据" in analysis
    main_ok = "官方年报分产品/分部证据：电子特气核心公司" in main_text and "不替代WF6/NF3单品订单" in main_compact
    matrix_ok = "官方年报分产品/分部证据" in matrix and "官方分产品/分部证据不得替代WF6/NF3" in matrix
    provenance_ok = "官方年报分产品/分部证据" in provenance
    audit_ok = "官方年报分产品/分部证据" in audit and "不得替代WF6/NF3单品收入" in audit
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代WF6/NF3单品收入" in packet.get("use_boundary", "")
    return len(rows) >= 8 and required_tickers <= tickers and required_segments <= segments and not missing and not missing_sources and text_ok and main_ok and matrix_ok and provenance_ok and audit_ok and boundary_ok, f"rows={len(rows)}, tickers={sorted(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, boundary_ok={boundary_ok}"

def order_revenue_recognition_complete() -> tuple[bool, str]:
    packet = load_json("data/order_revenue_recognition_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"688146", "688549", "600378", "688268", "002971", "300346", "688106"}
    required_keys = [
        "ticker",
        "company",
        "production_order_evidence",
        "revenue_recognition_evidence",
        "remaining_performance_obligation",
        "q_contract_liab",
        "q_contract_liab_to_revenue",
        "recognition_gate",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
        "source_path",
        "line_reference",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("source_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/order_revenue_recognition_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/order_revenue_recognition_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["订单与收入确认代理证据", "收入确认门槛", "合同负债/收入", "剩余履约义务"]) and "订单与收入确认代理证据" in analysis
    main_ok = "订单与收入确认代理证据" in main_text and "不替代单品订单金额" in main_compact
    matrix_ok = "订单与收入确认代理证据" in matrix and "不得替代单品订单金额" in matrix
    provenance_ok = "订单与收入确认代理证据" in provenance
    audit_ok = "订单与收入确认代理证据" in audit and "不得替代单品订单金额" in audit
    hard_gap_ok = "订单与收入确认代理证据包已补充" in hard_gap
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代单品订单金额" in packet.get("use_boundary", "")
    return len(rows) >= 7 and required_tickers <= tickers and not missing and not missing_sources and text_ok and main_ok and matrix_ok and provenance_ok and audit_ok and hard_gap_ok and boundary_ok, f"rows={len(rows)}, tickers={sorted(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, hard_gap_ok={hard_gap_ok}, boundary_ok={boundary_ok}"

def product_conversion_constraint_complete() -> tuple[bool, str]:
    packet = load_json("data/product_conversion_constraint.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"603379", "300037", "605020", "600160", "002407", "603505", "300346", "600378", "688549", "688146", "688268", "002971", "002549", "688106"}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "growth_scope",
        "disclosed_product_volume_or_capacity",
        "segment_revenue_ceiling",
        "order_or_contract_proxy",
        "customer_or_certification_proxy",
        "company_clarification_boundary",
        "conversion_gate",
        "growth_eps_allowed",
        "conversion_blocker",
        "model_conclusion",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
        "source_artifacts",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if k == "growth_eps_allowed":
                if r.get(k) is None:
                    missing.append(f"{r.get('ticker')}:{k}")
            elif r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    gates = {r.get("conversion_gate") for r in rows}
    required_gates = {"BASE_BUSINESS_ONLY", "VOLUME_ONLY_BLOCKED", "CATEGORY_VOLUME_BLOCKED", "LOW_EXPOSURE_BOUND", "LOW_DIRECTNESS_BOUND", "PLATFORM_ONLY_BLOCKED"}
    data_md = (BASE / "data/product_conversion_constraint.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/product_conversion_constraint.md").read_text(encoding="utf-8")
    growth = (BASE / "analysis/growth_earnings_model.md").read_text(encoding="utf-8")
    bridge = (BASE / "analysis/segment_forecast_bridge.md").read_text(encoding="utf-8")
    valuation = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    company = (BASE / "sections/ch05_companies.tex").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in data_md for s in ["单品转化约束", "增长每股收益是否允许入模", "14只高成长", "增长每股收益入模"]) and "单品转化约束" in analysis
    downstream_ok = "单品转化约束" in growth and "单品转化约束" in bridge and "单品转化约束进入估值" in valuation and "单品转化约束" in company
    matrix_ok = "单品转化约束" in matrix and "增长每股收益入模为否" in matrix
    provenance_ok = "单品转化约束" in provenance and "证据派生门禁" in provenance
    catalog_ok = "单品转化约束" in catalog
    main_ok = "单品转化约束" in main_text and ("增长EPS入模" in main_text or "增长每股收益入模" in main_text) and not any(s in main_compact for s in ["BASE_BUSINESS_ONLY", "VOLUME_ONLY_BLOCKED", "CATEGORY_VOLUME_BLOCKED", "LOW_EXPOSURE_BOUND", "LOW_DIRECTNESS_BOUND", "PLATFORM_ONLY_BLOCKED"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 14 and packet.get("growth_eps_allowed_count") == 0 and all(r.get("growth_eps_allowed") is False for r in rows) and "不得进入基本面目标价上修" in packet.get("use_boundary", "")
    return len(rows) == 14 and required_tickers == tickers and required_gates <= gates and not missing and text_ok and downstream_ok and matrix_ok and provenance_ok and catalog_ok and main_ok and boundary_ok, f"rows={len(rows)}, tickers={sorted(tickers)}, gates={sorted(gates)}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def implied_growth_requirement_complete() -> tuple[bool, str]:
    packet = load_json("data/implied_growth_requirement.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"603379", "300037", "605020", "600160", "002407", "603505", "300346", "600378", "688549", "688146", "688268", "002971", "002549", "688106"}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "method",
        "current_price",
        "base_target",
        "price_premium_pct",
        "market_cap",
        "base_market_cap",
        "premium_market_cap",
        "calculation_mode",
        "valuation_multiple",
        "required_growth_revenue_base_margin_30pct",
        "required_growth_net_profit_base_margin_30pct",
        "required_revenue_vs_2026e_pct",
        "required_net_profit_vs_2026e_pct",
        "growth_driver",
        "sensitivity_key",
        "evidence_gap",
        "valuation_gate",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if k in {"price_premium_pct", "required_revenue_vs_2026e_pct", "required_net_profit_vs_2026e_pct"}:
                if r.get(k) is None:
                    missing.append(f"{r.get('ticker')}:{k}")
            elif r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    positive = packet.get("coverage", {}).get("positive_premium_tickers", 0)
    data_md = (BASE / "data/implied_growth_requirement.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/implied_growth_requirement.md").read_text(encoding="utf-8")
    sensitivity = (BASE / "analysis/implied_growth_sensitivity.md").read_text(encoding="utf-8")
    valuation_md = (BASE / "analysis/valuation_model.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    valuation_tex = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in data_md for s in ["隐含增长反推门槛", "所需增量净利", "所需增长收入", "使用边界"]) and "隐含增长反推门槛" in analysis
    downstream_ok = all(
        "隐含增长反推门槛" in text
        for text in [sensitivity, valuation_md, audit, valuation_tex, matrix, provenance, main_text]
    ) and "隐含增长反推门槛" in catalog
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不是公司预测" in packet.get("use_boundary", "") and "不替代订单" in packet.get("use_boundary", "") and "不是公司预测" in main_compact
    return len(rows) == 14 and required_tickers == tickers and positive >= 10 and not missing and text_ok and downstream_ok and boundary_ok, f"rows={len(rows)}, positive={positive}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, boundary_ok={boundary_ok}"

def evidence_maturity_monitor_complete() -> tuple[bool, str]:
    packet = load_json("data/evidence_maturity_monitor.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020", "002407", "600378", "300037", "688146", "688549", "688268", "300346", "688106", "002549", "002971"}
    required_keys = [
        "ticker",
        "company",
        "theme",
        "evidence_score",
        "maturity_stage",
        "p0_closure_status",
        "available_evidence",
        "blocking_gap",
        "next_quarter_validation",
        "upgrade_trigger",
        "downgrade_trigger",
        "model_action",
        "source_artifacts",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if k == "evidence_score":
                if r.get(k) is None:
                    missing.append(f"{r.get('ticker')}:{k}")
            elif r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    stages = {r.get("maturity_stage") for r in rows}
    p0_statuses = {r.get("p0_closure_status") for r in rows}
    data_md = (BASE / "data/evidence_maturity_monitor.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/evidence_maturity_monitor.md").read_text(encoding="utf-8")
    valuation_tex = (BASE / "sections/ch07_valuation.tex").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in data_md for s in ["证据成熟度与下一季验证", "P0闭合状态", "下一季验证", "使用边界"]) and "证据成熟度与下一季验证" in analysis
    downstream_ok = all("证据成熟度与下一季验证" in text for text in [valuation_tex, matrix, provenance, catalog, audit, main_text])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 18 and "不得替代订单金额" in packet.get("use_boundary", "") and "不替代订单" in main_compact
    p0_ok = any("部分证据" in str(x) for x in p0_statuses) and "无P0闭合" in p0_statuses
    stage_ok = bool(stages & {"事件验证池", "强观察池"})
    return len(rows) == 18 and required_tickers == tickers and not missing and text_ok and downstream_ok and boundary_ok and p0_ok and stage_ok, f"rows={len(rows)}, stages={sorted(stages)}, missing={missing[:3]}, text_ok={text_ok}, downstream_ok={downstream_ok}, boundary_ok={boundary_ok}, p0_ok={p0_ok}"

def customer_qualification_evidence_complete() -> tuple[bool, str]:
    packet = load_json("data/customer_qualification_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {"688146", "688549", "688268", "600378", "688106", "002549", "002971", "300346"}
    required_keys = [
        "ticker",
        "company",
        "evidence_layer",
        "named_customer_evidence",
        "certification_or_supply_evidence",
        "customer_share_or_scope",
        "line_reference",
        "source_path",
        "source_id",
        "confidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("source_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/customer_qualification_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/customer_qualification_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    customer_audit = (BASE / "data/customer_chain_audit.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["客户认证/具名客户披露证据", "中船特气", "中巨芯-U", "ASML", "不替代单品客户份额"]) and "客户认证/具名客户披露证据" in analysis
    main_ok = "客户认证/具名客户披露证据" in main_text and "不替代单品客户份额" in main_compact
    matrix_ok = "客户认证/具名客户披露证据" in matrix and "不得替代单品客户份额" in matrix
    provenance_ok = "客户认证/具名客户披露证据" in provenance
    audit_ok = "客户认证/具名客户披露证据" in audit and "不得替代单品客户份额" in audit
    hard_gap_ok = "客户认证/具名客户披露证据包已补充" in hard_gap
    customer_audit_ok = "客户认证/具名客户披露证据" in customer_audit and "不替代单品客户份额" in customer_audit
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代单品客户份额" in packet.get("use_boundary", "")
    return len(rows) >= 8 and required_tickers <= tickers and not missing and not missing_sources and text_ok and main_ok and matrix_ok and provenance_ok and audit_ok and hard_gap_ok and customer_audit_ok and boundary_ok, f"rows={len(rows)}, tickers={sorted(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, hard_gap_ok={hard_gap_ok}, customer_audit_ok={customer_audit_ok}, boundary_ok={boundary_ok}"

def customer_side_verification_probe_complete() -> tuple[bool, str]:
    packet = load_json("data/customer_side_verification_probe.json")
    rows = packet.get("rows", [])
    required_keys = [
        "anchor_group",
        "linked_a_share_names",
        "supplier_side_evidence",
        "customer_side_public_evidence",
        "checked_artifacts",
        "found_status",
        "valuation_use",
        "remaining_gap",
        "evidence_boundary",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('anchor_group')}:{k}")
    data_md = (BASE / "data/customer_side_verification_probe.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/customer_side_verification_probe.md").read_text(encoding="utf-8")
    supply = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    source = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in data_md for s in ["客户侧验证探针", "反向验证为0/8", "供应商侧具名客户", "客户侧订单/采购/份额反向验证"]) and "客户侧验证探针" in analysis
    supply_ok = "客户侧验证探针" in supply and "客户侧反向验证为0/8" in supply and "供应商年报自述" in supply
    source_ok = "客户侧验证探针" in source and "反向验证为0/8" in source and "客户侧采购文件" in source
    field_ok = "客户侧验证探针" in field and "不得把供应商年报自述" in field
    provenance_ok = "客户侧验证探针" in provenance and "反向验证" in provenance
    audit_ok = "客户侧验证探针" in audit and "反向验证为0/8" in audit
    hard_gap_ok = "客户侧验证探针" in hard_gap and "反向验证为0/8" in hard_gap
    catalog_ok = "客户侧验证探针" in catalog and "反向验证0/8" in catalog
    main_ok = "客户侧验证探针" in main_text and "反向验证为0/8" in main_compact and "客户侧采购文件" in main_text
    boundary_ok = packet.get("schema") == "astock.customer_side_verification_probe.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_anchor_groups") == 8 and packet.get("customer_side_order_confirmed_count") == 0 and "反向验证为0/8" in packet.get("use_boundary", "") and "不得替代订单金额" in packet.get("use_boundary", "")
    return len(rows) == 8 and not missing and text_ok and supply_ok and source_ok and field_ok and provenance_ok and audit_ok and hard_gap_ok and catalog_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}, supply_ok={supply_ok}, source_ok={source_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, hard_gap_ok={hard_gap_ok}, catalog_ok={catalog_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def downstream_customer_public_file_probe_complete() -> tuple[bool, str]:
    packet = load_json("data/downstream_customer_public_file_probe.json")
    rows = packet.get("rows", [])
    required_codes = {"688981", "688347", "600460", "688012", "002371", "688126", "000725", "000100"}
    codes = {str(r.get("ticker")) for r in rows}
    required_keys = [
        "ticker",
        "company",
        "customer_role",
        "annual_report_status",
        "supplier_name_hit_status",
        "product_procurement_hit_status",
        "reverse_confirmation_status",
        "valuation_use",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("annual_report_text_path")
        if r.get("annual_report_status") == "公开年报已检查" and rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/downstream_customer_public_file_probe.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/downstream_customer_public_file_probe.md").read_text(encoding="utf-8")
    supply = (BASE / "sections/ch04_supply_chain.tex").read_text(encoding="utf-8")
    source = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    field = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    text_ok = all(s in data_md for s in ["下游客户公开文件探针", "客户侧公开年报", "产品级采购订单/份额/价格反向验证", "使用边界"]) and "下游客户公开文件探针" in analysis
    supply_ok = "下游客户公开文件探针" in supply and "产品级采购订单" in supply and "不能写成订单和利润" in supply
    source_ok = "下游客户公开文件探针" in source and "产品级采购订单/份额/价格反向验证仍为0" in source
    field_ok = "下游客户公开文件探针" in field and "不得把客户侧年报中的供应商名或产品词候选" in field
    provenance_ok = "下游客户公开文件探针" in provenance and "客户侧公开年报" in provenance and "产品级采购订单" in provenance
    audit_ok = "下游客户公开文件探针" in audit and "产品级采购订单/采购份额/合同价格反向验证" in audit
    hard_gap_ok = "下游客户公开文件探针" in hard_gap and "产品级采购订单/份额/价格反向验证仍为0" in hard_gap
    catalog_ok = "下游客户公开文件探针" in catalog and "客户侧采购订单/份额/价格反向验证" in catalog
    main_ok = "下游客户公开文件探针" in main_text and "产品级采购订单" in main_text and ("不替代采购文件" in main_text or "不能写成订单和利润" in main_text) and "反向验证仍为0/8" in main_compact
    boundary_ok = packet.get("schema") == "astock.downstream_customer_public_file_probe.v1" and packet.get("gate_status") == "CONDITIONAL" and packet.get("checked_customer_files", 0) >= 7 and packet.get("reverse_confirmation_count") == 0 and "采购订单/份额/价格反向验证为0" in packet.get("use_boundary", "")
    return len(rows) == 8 and required_codes <= codes and not missing and not missing_sources and text_ok and supply_ok and source_ok and field_ok and provenance_ok and audit_ok and hard_gap_ok and catalog_ok and main_ok and boundary_ok, f"rows={len(rows)}, codes={sorted(codes)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, supply_ok={supply_ok}, source_ok={source_ok}, field_ok={field_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, hard_gap_ok={hard_gap_ok}, catalog_ok={catalog_ok}, main_ok={main_ok}, boundary_ok={boundary_ok}"

def production_sales_inventory_complete() -> tuple[bool, str]:
    packet = load_json("data/production_sales_inventory_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {
        "600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020", "002407", "300037",
        "600378", "688146", "688549", "688268", "300346", "688106", "002549", "002971",
    }
    required_keys = [
        "ticker",
        "company",
        "evidence_layer",
        "product_or_segment",
        "production_evidence",
        "sales_evidence",
        "inventory_evidence",
        "capacity_or_utilization_evidence",
        "conversion_signal",
        "report_summary",
        "source_path",
        "line_reference",
        "confidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("source_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/production_sales_inventory_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/production_sales_inventory_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["产销量/库存/产能利用证据包", "六氟化钨", "电子级氢氟酸", "细钨丝", "不替代单品客户"]) and "产销量/库存/产能利用证据包" in analysis
    main_ok = "产销库存与产能利用" in main_text and "产销量/库存/产能利用证据" in main_text and "不替代单品客户份额" in main_compact
    cards_ok = "产销量/库存/产能利用" in cards
    matrix_ok = "产销量/库存/产能利用证据" in matrix and "不得替代单品客户份额" in matrix
    provenance_ok = "产销量/库存/产能利用证据" in provenance
    audit_ok = "产销量/库存/产能利用证据" in audit and "不得替代WF6/NF3" in audit
    gap_ok = "产销量/库存/产能利用公开证据" in gaps
    hard_gap_ok = "产销量/库存/产能利用证据包已补充" in hard_gap
    source_log_ok = "产销量/库存/产能利用证据包" in source_log
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不得替代WF6/NF3" in packet.get("use_boundary", "")
    return len(rows) == 18 and required_tickers <= tickers and not missing and not missing_sources and text_ok and main_ok and cards_ok and matrix_ok and provenance_ok and audit_ok and gap_ok and hard_gap_ok and source_log_ok and boundary_ok, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, cards_ok={cards_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, boundary_ok={boundary_ok}"

def cost_margin_pass_through_complete() -> tuple[bool, str]:
    packet = load_json("data/cost_margin_pass_through_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {
        "600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020", "002407", "300037",
        "600378", "688146", "688549", "688268", "300346", "688106", "002549", "002971",
    }
    required_keys = [
        "ticker",
        "company",
        "evidence_layer",
        "product_or_segment",
        "gross_margin_or_profit_evidence",
        "cost_structure_evidence",
        "price_pass_through_evidence",
        "raw_material_or_energy_risk",
        "margin_signal",
        "report_summary",
        "source_path",
        "line_reference",
        "confidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("source_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/cost_margin_pass_through_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/cost_margin_pass_through_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["成本结构/毛利/价格传导证据包", "翔鹭钨业", "中船特气", "三美股份", "不替代WF6/NF3"]) and "成本结构/毛利/价格传导证据包" in analysis
    main_ok = "成本毛利与价格传导" in main_text and "成本结构/毛利/价格传导证据" in main_compact and "不替代单品毛利" in main_compact
    cards_ok = "成本毛利/价格传导" in cards
    matrix_ok = "成本结构/毛利/价格传导证据" in matrix and "不得替代单品毛利率" in matrix
    provenance_ok = "成本结构/毛利/价格传导证据" in provenance
    audit_ok = "成本结构/毛利/价格传导证据" in audit and "不得替代单品毛利" in audit
    gap_ok = "成本结构/毛利/价格传导公开证据" in gaps
    hard_gap_ok = "成本结构/毛利/价格传导证据包已补充" in hard_gap
    source_log_ok = "成本结构/毛利/价格传导证据包" in source_log
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代WF6/NF3" in packet.get("use_boundary", "")
    return len(rows) == 18 and required_tickers <= tickers and not missing and not missing_sources and text_ok and main_ok and cards_ok and matrix_ok and provenance_ok and audit_ok and gap_ok and hard_gap_ok and source_log_ok and boundary_ok, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, cards_ok={cards_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, boundary_ok={boundary_ok}"

def competitive_position_complete() -> tuple[bool, str]:
    packet = load_json("data/competitive_position_evidence.json")
    rows = packet.get("rows", [])
    tickers = {r.get("ticker") for r in rows}
    required_tickers = {
        "600549", "000657", "002378", "002842", "603505", "600160", "603379", "605020", "002407", "300037",
        "600378", "688146", "688549", "688268", "300346", "688106", "002549", "002971",
    }
    required_keys = [
        "ticker",
        "company",
        "evidence_layer",
        "competitive_position",
        "market_share_or_rank_evidence",
        "barrier_or_moat_evidence",
        "customer_or_certification_evidence",
        "competitive_risk",
        "report_summary",
        "source_path",
        "line_reference",
        "confidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("source_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:{rel}")
    data_md = (BASE / "data/competitive_position_evidence.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/competitive_position_evidence.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    hard_gap = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    source_log = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["竞争格局/行业地位证据包", "厦门钨业", "中船特气", "中巨芯-U", "不替代单品收入"]) and "竞争格局/行业地位证据包" in analysis
    main_ok = "竞争格局与行业地位" in main_text and "竞争格局/行业地位证据" in main_text and "不替代单品收入" in main_compact
    cards_ok = "竞争格局/行业地位" in cards
    matrix_ok = "竞争格局/行业地位证据" in matrix and "不得替代单品收入" in matrix
    provenance_ok = "竞争格局/行业地位证据" in provenance
    audit_ok = "竞争格局/行业地位证据" in audit and "不得替代单品收入" in audit
    gap_ok = "竞争格局/行业地位/壁垒公开证据" in gaps
    hard_gap_ok = "竞争格局/行业地位证据包已补充" in hard_gap
    source_log_ok = "竞争格局/行业地位证据包" in source_log
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不替代单品收入" in packet.get("use_boundary", "")
    return len(rows) == 18 and required_tickers <= tickers and not missing and not missing_sources and text_ok and main_ok and cards_ok and matrix_ok and provenance_ok and audit_ok and gap_ok and hard_gap_ok and source_log_ok and boundary_ok, f"rows={len(rows)}, tickers={len(tickers)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, main_ok={main_ok}, cards_ok={cards_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, audit_ok={audit_ok}, gap_ok={gap_ok}, hard_gap_ok={hard_gap_ok}, source_log_ok={source_log_ok}, boundary_ok={boundary_ok}"

def industry_region_segment_complete() -> tuple[bool, str]:
    packet = load_json("data/industry_region_segment_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    industry_covered = {r.get("ticker") for r in rows if r.get("classification") == "industry"}
    region_covered = {r.get("ticker") for r in rows if r.get("classification") == "region"}
    required_keys = ["segment", "revenue", "revenue_share", "classification"]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    text = (BASE / "analysis/industry_region_segment_snapshot.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["下游行业与区域收入结构快照", "按行业", "按地区"]) and "下游行业与区域结构" in main_text
    return len(covered) == 18 and len(industry_covered) == 18 and len(region_covered) == 18 and not missing and text_ok, f"rows={len(rows)}, covered={len(covered)}, industry={len(industry_covered)}, region={len(region_covered)}, missing={missing[:3]}, text_ok={text_ok}"

def capital_working_capital_complete() -> tuple[bool, str]:
    packet = load_json("data/capital_working_capital_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required = ["q_period", "q_cip", "q_inventory", "q_research_expense", "q_capex_cash", "capital_signal"]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    text = (BASE / "analysis/capital_working_capital_snapshot.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["资本开支与营运资本快照", "在建工程", "合同负债"]) and "资本开支与营运资本信号" in main_text
    return len(covered) == 18 and not missing and text_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, text_ok={text_ok}"

def rd_technology_intensity_complete() -> tuple[bool, str]:
    packet = load_json("data/rd_technology_intensity_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required = [
        "ticker",
        "company",
        "theme",
        "q_research_expense",
        "fy_research_expense",
        "q_research_to_revenue",
        "rd_intensity_label",
        "technology_asset_evidence",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/rd_technology_intensity_snapshot.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/rd_technology_intensity_snapshot.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch05_companies.tex").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    provenance = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    catalog = (BASE / "data/report_catalog.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["研发与技术资产强度快照", "研发/收入", "技术资产证据"]) and "研发与技术资产强度快照" in analysis
    section_ok = "研发与技术资产强度" in section and "研发强度高只能说明平台有持续投入" in section
    main_ok = "研发与技术资产强度" in main_text and "研发/收入" in main_text
    matrix_ok = "研发与技术资产强度" in matrix and "不得替代客户认证" in matrix
    provenance_ok = "研发与技术资产强度" in provenance
    catalog_ok = "研发与技术资产强度快照" in catalog
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不直接进入增长EPS" in packet.get("use_boundary", "")
    return len(covered) == 18 and not missing and text_ok and section_ok and main_ok and matrix_ok and provenance_ok and catalog_ok and boundary_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, text_ok={text_ok}, section_ok={section_ok}, main_ok={main_ok}, matrix_ok={matrix_ok}, provenance_ok={provenance_ok}, catalog_ok={catalog_ok}, boundary_ok={boundary_ok}"

def customer_supplier_concentration_complete() -> tuple[bool, str]:
    packet = load_json("data/customer_supplier_concentration_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required_keys = [
        "annual_report_pdf_path",
        "annual_report_text_path",
        "customer_top5_sales_share",
        "customer_related_sales_share",
        "customer_disclosure_type",
        "supplier_top5_purchase_share",
        "supplier_related_purchase_share",
        "supplier_disclosure_type",
        "concentration_signal",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        for path_key in ["annual_report_pdf_path", "annual_report_text_path"]:
            rel = r.get(path_key)
            if rel and not (BASE / rel).exists():
                missing_sources.append(f"{r.get('ticker')}:{path_key}")
    text = (BASE / "analysis/customer_supplier_concentration_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["年报前五客户/供应商集中度快照", "前五客户占比", "前五供应商占比"]) and "客户/供应商集中度" in main_text and "年报客户/供应商集中度" in cards
    return len(covered) == 18 and not missing and not missing_sources and text_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}"

def customer_supplier_detail_complete() -> tuple[bool, str]:
    packet = load_json("data/customer_supplier_detail_snapshot.json")
    summary_rows = packet.get("summary_rows", [])
    detail_rows = packet.get("detail_rows", [])
    covered = {r.get("ticker") for r in summary_rows}
    required_summary = [
        "ticker",
        "company",
        "customer_top5_sales_share",
        "customer_detail_status",
        "customer_named_sample",
        "supplier_top5_purchase_share",
        "supplier_detail_status",
        "supplier_named_sample",
        "valuation_gate",
        "evidence_boundary",
    ]
    required_detail = ["ticker", "company", "counterparty_type", "name", "source"]
    missing = []
    for r in summary_rows:
        for k in required_summary:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    for r in detail_rows:
        for k in required_detail:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
    data_md = (BASE / "data/customer_supplier_detail_snapshot.md").read_text(encoding="utf-8")
    analysis_md = (BASE / "analysis/customer_supplier_detail_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = (
        all(s in data_md for s in ["年报前五客户/供应商明细", "可解析逐项/合并口径明细", "使用边界"])
        and all(s in analysis_md for s in ["年报前五客户/供应商明细", "可解析逐项/合并口径明细", "使用边界"])
        and "客户/供应商明细可得性" in main_text
        and "年报客户/供应商明细" in cards
        and "年报客户/供应商明细" in matrix
        and "年报客户/供应商明细" in audit
    )
    boundary_ok = "不替代单品客户份额" in main_text and ("不等于单品客户份额" in matrix or "不替代单品客户份额" in data_md)
    use_ok = "不进入单品订单、ASP或增长EPS" in packet.get("use_boundary", "")
    return len(covered) == 18 and len(detail_rows) >= 20 and not missing and text_ok and boundary_ok and use_ok, f"summary={len(summary_rows)}, covered={len(covered)}, details={len(detail_rows)}, missing={missing[:3]}, text_ok={text_ok}, boundary_ok={boundary_ok}, use_ok={use_ok}"

def annual_report_theme_evidence_complete() -> tuple[bool, str]:
    packet = load_json("data/annual_report_theme_evidence_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required_keys = [
        "annual_report_text_path",
        "product_terms",
        "theme_evidence_status",
        "valuation_gate",
        "evidence_gap",
    ]
    missing = []
    missing_sources = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        rel = r.get("annual_report_text_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:annual_report_text_path")
    text = (BASE / "analysis/annual_report_theme_evidence_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in text for s in ["年报主题证据扫描", "产品词", "客户/平台词", "估值门禁"]) and "年报主题证据" in main_text and "年报主题证据" in cards
    return len(covered) == 18 and not missing and not missing_sources and text_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}"

def annual_report_evidence_snippet_complete() -> tuple[bool, str]:
    packet = load_json("data/annual_report_evidence_snippet_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required_keys = [
        "annual_report_text_path",
        "snippet_count",
        "product_excerpt",
        "valuation_gate",
        "evidence_boundary",
    ]
    missing = []
    missing_sources = []
    product_missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        product = r.get("product_excerpt", {})
        if not isinstance(product, dict) or product.get("excerpt") in (None, "", "未找到"):
            product_missing.append(str(r.get("ticker")))
        rel = r.get("annual_report_text_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:annual_report_text_path")
    text = (BASE / "analysis/annual_report_evidence_snippet_snapshot.md").read_text(encoding="utf-8")
    data_md = (BASE / "data/annual_report_evidence_snippet_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    text_ok = all(s in text for s in ["年报原文证据短摘", "产品/工艺短摘", "使用边界"]) and all(s in data_md for s in ["年报原文证据短摘", "短摘不进入增长每股收益"]) and "年报原文短摘" in main_text and "年报原文短摘" in cards and "年报原文证据短摘" in matrix
    boundary_ok = "短摘不替代单品订单或合同ASP" in main_text or "短摘不等于单品订单" in matrix
    return len(covered) == 18 and not missing and not missing_sources and not product_missing and text_ok and boundary_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, product_missing={product_missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, boundary_ok={boundary_ok}"

def annual_report_mdna_complete() -> tuple[bool, str]:
    packet = load_json("data/annual_report_mdna_snapshot.json")
    rows = packet.get("rows", [])
    covered = {r.get("ticker") for r in rows}
    required_keys = [
        "annual_report_text_path",
        "snippet_count",
        "performance_excerpt",
        "margin_cost_excerpt",
        "cash_working_capital_excerpt",
        "risk_excerpt",
        "valuation_gate",
        "evidence_boundary",
    ]
    missing = []
    missing_sources = []
    short = []
    performance_missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('ticker')}:{k}")
        if int(r.get("snippet_count") or 0) < 3:
            short.append(f"{r.get('ticker')}:{r.get('snippet_count')}")
        perf = r.get("performance_excerpt", {})
        if not isinstance(perf, dict) or perf.get("excerpt") in (None, "", "未找到"):
            performance_missing.append(str(r.get("ticker")))
        rel = r.get("annual_report_text_path")
        if rel and not (BASE / rel).exists():
            missing_sources.append(f"{r.get('ticker')}:annual_report_text_path")
    text = (BASE / "analysis/annual_report_mdna_snapshot.md").read_text(encoding="utf-8")
    data_md = (BASE / "data/annual_report_mdna_snapshot.md").read_text(encoding="utf-8")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    matrix = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    text_ok = (
        all(s in text for s in ["年报管理层讨论与业绩归因摘录", "业绩归因", "现金流/营运资本", "使用边界"])
        and all(s in data_md for s in ["年报管理层讨论与业绩归因摘录", "管理层讨论只解释公司整体业绩"])
        and "年报管理层讨论与业绩归因" in main_text
        and "年报业绩归因" in cards
        and "年报管理层讨论与业绩归因" in matrix
        and "年报管理层讨论与业绩归因" in audit
    )
    boundary_ok = "不替代单品订单" in main_text and ("管理层讨论不等于单品订单" in matrix or "不进入单品订单、ASP或增长EPS" in packet.get("use_boundary", ""))
    return len(covered) == 18 and not missing and not missing_sources and not short and not performance_missing and text_ok and boundary_ok, f"rows={len(rows)}, covered={len(covered)}, missing={missing[:3]}, short={short[:3]}, performance_missing={performance_missing[:3]}, source_missing={missing_sources[:3]}, text_ok={text_ok}, boundary_ok={boundary_ok}"

def valuation_complete() -> tuple[bool, str]:
    rows = load_json("data/current_valuation_model_20260628.json").get("rows", [])
    missing = []
    for r in rows:
        for k in [
            "code",
            "name",
            "price",
            "official_price",
            "astock_quote_price",
            "price_source",
            "price_source_time",
            "price_warning",
            "shares",
            "market_cap",
            "official_total_market_cap",
            "revenue_2026e",
            "np_2026e",
            "eps_2026e",
            "bear_target",
            "base_target",
            "bull_target",
            "market_anchor",
            "weights_text",
            "final_target",
            "final_upside",
            "action",
            "next_quarter_threshold",
            "catalyst",
            "invalidation",
            "risk_monitor_signal",
            "risk_downgrade_trigger",
            "risk_model_action",
        ]:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('code')}:{k}")
    def as_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    price_mismatch = []
    market_cap_mismatch = []
    price_date_mismatch = []
    price_source_mismatch = []
    for r in rows:
        code = r.get("code")
        price = as_float(r.get("price"))
        official_price = as_float(r.get("official_price"))
        market_cap = as_float(r.get("market_cap"))
        official_market_cap = as_float(r.get("official_total_market_cap"))
        quote_date = str(r.get("official_share_quote_time") or "")[:10]
        if price is None or official_price is None or abs(price - official_price) > 0.011:
            price_mismatch.append(code)
        if market_cap is None or official_market_cap is None or abs(market_cap - official_market_cap) > max(100000.0, official_market_cap * 0.00001):
            market_cap_mismatch.append(code)
        if quote_date and str(r.get("price_date")) != quote_date:
            price_date_mismatch.append(code)
        if "东方财富官方行情快照" not in str(r.get("price_source", "")):
            price_source_mismatch.append(code)
    official_price_ok = not price_mismatch and not market_cap_mismatch and not price_date_mismatch and not price_source_mismatch
    text = (BASE / "analysis/valuation_model.md").read_text(encoding="utf-8")
    required_sections = [
        "最终估值总表",
        "三情景目标",
        "相对估值与增长/收入增速校验对比",
        "季节性校准",
        "下一季度验证门槛",
        "方法与假设桥",
        "市场预期估值桥",
        "高成长业绩依赖",
        "公开价格代理边界",
        "券商/公开外部锚对比",
        "公开个股研报快照",
        "市场隐含情绪锚",
    ]
    missing_sections = [s for s in required_sections if s not in text]
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    audit_ok = all(s in audit for s in ["算术校验", "预测数据可用性", "市场隐含情绪锚", "高成长业绩依赖", "投关调研记录标题索引与正文关键词探针", "合同/中标/供货协议公告全文扫描", "订单持续性与收入确认耐久性证据", "价格与毛利入模门禁", "公开价格代理边界", "公开券商全文PDF证据", "硬缺口行动清单", "字段级证据矩阵", "后续必需更新"])
    text_price_ok = "东方财富官方行情快照" in text and "官方现价" in text and "官方总市值" in text
    return len(rows) == 18 and not missing and not missing_sections and audit_ok and official_price_ok and text_price_ok, f"rows={len(rows)}, missing={missing[:3]}, sections={missing_sections}, audit={audit_ok}, official_price_ok={official_price_ok}, price_mismatch={price_mismatch[:3]}, cap_mismatch={market_cap_mismatch[:3]}, price_date_mismatch={price_date_mismatch[:3]}, source_mismatch={price_source_mismatch[:3]}, text_price_ok={text_price_ok}"

def risk_framework_complete() -> tuple[bool, str]:
    rows = load_json("data/current_valuation_model_20260628.json").get("rows", [])
    codes = {r.get("code") for r in rows}
    missing = []
    for r in rows:
        for k in ["risk_monitor_signal", "risk_downgrade_trigger", "risk_model_action", "catalyst", "invalidation"]:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('code')}:{k}")
    risk_md = (BASE / "analysis/risk_framework.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch08_risks.tex").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    coverage_ok = len(codes) == 18 and all(code in section for code in codes)
    text_ok = all(s in risk_md for s in ["门禁状态：通过", "反方证据与看错情形", "看错情形", "逐标的风险监测触发器", "监测信号", "降级触发", "模型动作"])
    section_ok = all(s in section for s in ["反方证据与看错情形", "反方框架", "看错情形", "全覆盖催化与失效条件", "逐标的风险监测触发器", "订单、合同价格、单品收入和单品毛利"])
    main_ok = all(s in main_text for s in ["反方证据与看错情形", "看错情形", "逐标的风险监测触发器", "全覆盖催化与失效条件"])
    return not missing and coverage_ok and text_ok and section_ok and main_ok, f"rows={len(rows)}, missing={missing[:3]}, coverage={coverage_ok}, text={text_ok}, section={section_ok}, main={main_ok}"

def supply_chain_complete() -> tuple[bool, str]:
    valuation_rows = load_json("data/current_valuation_model_20260628.json").get("rows", [])
    codes = {r.get("code") for r in valuation_rows}
    rels = load_json("data/supply_chain_relationships.json").get("relationships", [])
    rel_codes = {r.get("ticker") for r in rels}
    required_keys = [
        "ticker",
        "company",
        "chain_layer",
        "upstream_input",
        "product_or_process",
        "downstream_customer_or_platform",
        "relationship_type",
        "confidence",
        "revenue_exposure",
        "capacity_or_certification",
        "order_visibility",
        "margin_or_earnings_impact",
        "source",
        "evidence_gap",
        "used_in_valuation",
    ]
    missing = []
    for r in rels:
        for k in required_keys:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    cards = (BASE / "analysis/company_fundamental_cards.md").read_text(encoding="utf-8")
    bridge = (BASE / "analysis/chain_earnings_bridge.md").read_text(encoding="utf-8")
    model = (BASE / "analysis/supply_chain_model.md").read_text(encoding="utf-8")
    rel_md = (BASE / "data/supply_chain_relationships.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    main_compact = "".join(main_text.split())
    audit = load_json("data/customer_chain_audit.json").get("claims", [])
    audit_text = json.dumps(audit, ensure_ascii=False)
    card_ok = all(code in cards for code in codes if code)
    text_ok = all(s in model for s in ["门禁状态：有条件通过", "利润池分层"]) and "下一季验证" in bridge
    contract_ok = "688146" in rel_md and "历史订单金额样本" in rel_md and "合同平均售价" in rel_md and "历史订单金额样本" in cards
    platform_contract_audit_ok = all(s in audit_text for s in ["S34", "电子气体平台合同金额样本", "1.4822亿元", "HF/HCL/D2", "不得替代WF6/NF3单品订单"])
    rel_by_code = {str(r.get("ticker")): r for r in rels}
    customer_chain_tickers = {"688146", "688549", "688268", "600378", "688106", "002549", "002971", "300346"}
    customer_rel_ok = all(
        code in rel_by_code
        and "官方年报客户链" in str(rel_by_code[code].get("downstream_customer_or_platform", ""))
        and "具名客户未找到" not in str(rel_by_code[code].get("downstream_customer_or_platform", ""))
        and "AR" in str(rel_by_code[code].get("source", ""))
        and "不替代单品订单金额" in str(rel_by_code[code].get("order_visibility", ""))
        for code in customer_chain_tickers
    )
    customer_main_ok = all(s in main_compact for s in ["官方年报客户链", "台积电、美光、海力士", "中芯国际、华虹集团", "不得替代WF6/NF3"])
    tungsten_tickers = {"600549", "000657", "002378", "002842"}
    tungsten_rel_ok = all(
        code in rel_by_code
        and "年报产销/产能证据" in str(rel_by_code[code].get("capacity_or_certification", ""))
        and "年报成本/传导证据" in str(rel_by_code[code].get("margin_or_earnings_impact", ""))
        and "矿山/冶炼/加工产能需逐家公司年报补充" not in str(rel_by_code[code].get("capacity_or_certification", ""))
        and "AR" in str(rel_by_code[code].get("source", ""))
        and "高纯钨材" in str(rel_by_code[code].get("evidence_gap", ""))
        for code in tungsten_tickers
    )
    tungsten_main_ok = all(s in main_compact for s in ["钨链年报证据", "细钨丝销量1,292亿米", "硬质合金销售10,756吨", "不得替代半导体高纯钨材客户"])
    return len(rels) == 18 and codes <= rel_codes and not missing and len(audit) >= 5 and card_ok and text_ok and contract_ok and platform_contract_audit_ok and customer_rel_ok and customer_main_ok and tungsten_rel_ok and tungsten_main_ok, f"relationships={len(rels)}, missing={missing[:3]}, audit={len(audit)}, card_ok={card_ok}, text_ok={text_ok}, contract_ok={contract_ok}, platform_contract_audit_ok={platform_contract_audit_ok}, customer_rel_ok={customer_rel_ok}, customer_main_ok={customer_main_ok}, tungsten_rel_ok={tungsten_rel_ok}, tungsten_main_ok={tungsten_main_ok}"

def growth_earnings_complete() -> tuple[bool, str]:
    valuation_rows = load_json("data/current_valuation_model_20260628.json").get("rows", [])
    codes = {r.get("code") for r in valuation_rows}
    rows = load_json("data/growth_driver_model.json").get("rows", [])
    row_codes = {r.get("ticker") for r in rows}
    required_keys = [
        "ticker",
        "company",
        "applies",
        "growth_driver",
        "base_business_revenue",
        "growth_segment_revenue",
        "unit_volume_or_proxy",
        "ASP_or_price",
        "recognized_revenue_ratio",
        "growth_gross_margin",
        "incremental_opex",
        "growth_net_profit",
        "growth_EPS",
        "evidence_type",
        "source",
        "evidence_gap",
        "valuation_credit",
        "bear",
        "base",
        "bull",
        "current_price_implied_growth",
        "sensitivity_key",
    ]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, ""):
                missing.append(f"{r.get('ticker')}:{k}")
    model = (BASE / "analysis/growth_earnings_model.md").read_text(encoding="utf-8")
    bridge = (BASE / "analysis/segment_forecast_bridge.md").read_text(encoding="utf-8")
    sensitivity = (BASE / "analysis/implied_growth_sensitivity.md").read_text(encoding="utf-8")
    text_ok = all(s in model for s in ["门禁状态：有条件通过", "增长每股收益", "估值信用"]) and "增长分部收入" in bridge and "当前股价隐含增长要求" in sensitivity and "隐含增长反推门槛" in sensitivity and "公开价格代理边界" in sensitivity
    applicable = [r for r in rows if r.get("applies")]
    blocked_ok = all("证据不足" in r.get("growth_EPS", "") or "不适用" in r.get("growth_segment_revenue", "") or "未披露" in r.get("growth_segment_revenue", "") or "不直接给增长盈利信用" in r.get("growth_segment_revenue", "") for r in applicable)
    contract_row_ok = any(
        r.get("ticker") == "688146"
        and "历史官方订单金额样本" in str(r.get("unit_volume_or_proxy", ""))
        and "订单金额部分补证" in str(r.get("valuation_credit", ""))
        for r in rows
    )
    contract_text_ok = "历史合同金额样本" in model and "合同平均售价" in model
    return len(rows) == 18 and codes <= row_codes and not missing and text_ok and blocked_ok and contract_row_ok and contract_text_ok, f"rows={len(rows)}, applicable={len(applicable)}, missing={missing[:3]}, text_ok={text_ok}, blocked_ok={blocked_ok}, contract_row_ok={contract_row_ok}, contract_text_ok={contract_text_ok}"

def structured_data_provenance_complete() -> tuple[bool, str]:
    packet = load_json("data/structured_data_provenance.json")
    rows = packet.get("rows", [])
    datasets = {r.get("dataset") for r in rows}
    required = {
        "行情与基础财务",
        "东方财富公开个股研报样本",
        "公开券商覆盖历史质量",
        "公开券商预测分歧与AStock差异",
        "公开券商全文PDF证据",
        "主营构成与产品毛利率",
        "官方年报分产品/分部证据",
        "订单与收入确认代理证据",
        "客户认证/具名客户披露证据",
        "客户侧验证探针",
        "下游客户公开文件探针",
        "产销量/库存/产能利用证据",
        "成本结构/毛利/价格传导证据",
        "竞争格局/行业地位证据",
        "2025年报客户/供应商集中度",
        "2025年报主题证据扫描",
        "2025年报原文证据短摘",
        "2025年报管理层讨论与业绩归因",
        "下游需求锚行情与财务",
        "AI平台/HBM/网络需求锚",
        "公司澄清/风险提示证据",
        "投资者关系互动问答补证",
        "投关调研记录标题索引与正文关键词探针",
        "合同/中标/供货协议公告全文扫描",
        "合同金额经济性约束",
        "订单持续性与收入确认耐久性证据",
        "价格与毛利入模门禁",
        "业绩披露日历与验证窗口",
        "业绩预告/快报公告证据",
        "问询/审核回复公告证据",
        "官方单品收入/订单金额边界",
        "半导体高纯钨材边界证据",
        "含氟电子材料边界证据",
        "交易风险公告与估值热度",
        "股东结构与机构持仓拥挤度",
        "融资融券杠杆拥挤度",
        "龙虎榜席位异常与机构交易",
        "制程/材料功能证据",
        "政策/出口管制官方证据",
        "公司产品能力官方证据",
        "项目/产能建设官方证据",
        "招股书价格/毛利披露边界",
        "上游资源安全与基准现金流证据",
        "公开价格/成本/配额代理",
        "2025年报客户/供应商明细",
        "隐含增长反推门槛",
        "证据成熟度与下一季验证",
    }
    missing = []
    for r in rows:
        for k in ["dataset", "source_type", "source_name", "artifact", "coverage", "material_fields", "quality_tier", "limitations", "downstream_use"]:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('dataset')}:{k}")
    md = (BASE / "data/structured_data_provenance.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/structured_data_provenance.md").read_text(encoding="utf-8")
    source_md = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["结构化数据来源覆盖与健康", "硬缺口仍为公司合同平均售价"]) and "结构化数据源摘要" in source_md and "结构化数据源健康" in main_text and "结构化数据来源覆盖与健康" in analysis
    return required <= datasets and len(rows) >= 9 and not missing and text_ok, f"rows={len(rows)}, missing={missing[:3]}, text_ok={text_ok}"

def hard_gap_action_plan_complete() -> tuple[bool, str]:
    packet = load_json("data/hard_gap_action_plan.json")
    rows = packet.get("rows", [])
    priorities = {r.get("priority") for r in rows}
    required_fields = [
        "priority",
        "missing_field",
        "affected_tickers",
        "required_source",
        "current_proxy",
        "valuation_effect_if_obtained",
        "monitoring_trigger",
        "current_status",
        "owner_gate",
    ]
    missing = []
    for r in rows:
        for k in required_fields:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('missing_field')}:{k}")
    md = (BASE / "data/hard_gap_action_plan.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/hard_gap_action_plan.md").read_text(encoding="utf-8")
    gaps = (BASE / "data/data_gap_matrix.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    must_have = ["公司合同平均售价", "订单金额", "单品收入", "单品毛利", "具名晶圆厂客户", "半导体高纯钨材客户", "含氟电子材料客户"]
    text_ok = all(s in md for s in ["硬数据缺口行动清单", "使用纪律"] + must_have) and "硬数据缺口行动清单" in analysis and "data/hard_gap_action_plan.md" in gaps and "硬缺口行动清单" in audit and "硬缺口行动清单" in main_text
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and "不是缺口关闭证明" in packet.get("completion_boundary", "")
    return len(rows) >= 7 and {"P0", "P1", "P2"} <= priorities and not missing and text_ok and boundary_ok, f"rows={len(rows)}, priorities={sorted(priorities)}, missing={missing[:3]}, text_ok={text_ok}, boundary_ok={boundary_ok}"

def field_evidence_matrix_complete() -> tuple[bool, str]:
    packet = load_json("data/field_evidence_matrix.json")
    rows = packet.get("rows", [])
    groups = {r.get("field_group") for r in rows}
    required_groups = {
        "行情与交易锚",
        "基础财务与2026E桥",
        "主营构成与产品毛利率",
        "官方年报分产品/分部证据",
        "订单与收入确认代理证据",
        "客户认证/具名客户披露证据",
        "客户侧验证探针",
        "下游客户公开文件探针",
        "产销量/库存/产能利用证据",
        "成本结构/毛利/价格传导证据",
        "竞争格局/行业地位证据",
        "年报原文证据短摘",
        "年报客户/供应商明细",
        "年报管理层讨论与业绩归因",
        "下游需求锚行情与财务",
        "AI平台/HBM/网络需求锚",
        "公司澄清/风险提示证据",
        "投资者关系互动问答补证",
        "投关调研记录标题索引与正文关键词探针",
        "合同/中标/供货协议公告全文扫描",
        "合同金额经济性约束",
        "订单持续性与收入确认耐久性证据",
        "价格与毛利入模门禁",
        "业绩披露日历与验证窗口",
        "业绩预告/快报公告证据",
        "问询/审核回复公告证据",
        "官方单品收入/订单金额边界",
        "半导体高纯钨材边界证据",
        "含氟电子材料边界证据",
        "交易风险公告与估值热度",
        "股东结构与机构持仓拥挤度",
        "融资融券杠杆拥挤度",
        "龙虎榜席位异常与机构交易",
        "制程/材料功能证据",
        "政策/出口管制官方证据",
        "公司产品能力官方证据",
        "项目/产能建设官方证据",
        "招股书价格/毛利披露边界",
        "公司级制冷剂配额证据",
        "上游资源安全与基准现金流证据",
        "供应链关系",
        "增长业绩精算",
        "隐含增长反推门槛",
        "证据成熟度与下一季验证",
        "公开价格/成本/配额代理",
        "公开券商覆盖历史质量",
        "公开券商预测分歧与AStock差异",
        "公开券商全文PDF证据",
        "估值模型",
        "硬缺口行动清单",
    }
    required_fields = [
        "field_group",
        "covered_fields",
        "coverage",
        "evidence_artifact",
        "source_tier",
        "proof_strength",
        "report_use",
        "valuation_use",
        "evidence_boundary",
        "remaining_gap",
    ]
    missing = []
    for r in rows:
        for k in required_fields:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('field_group')}:{k}")
    md = (BASE / "data/field_evidence_matrix.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/field_evidence_matrix.md").read_text(encoding="utf-8")
    audit = (BASE / "analysis/valuation_audit.md").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    text_ok = all(s in md for s in ["字段级证据矩阵", "估值使用纪律", "公开价格", "合同平均售价"]) and "字段级证据矩阵" in analysis and "字段级证据矩阵" in audit and "字段级证据矩阵" in main_text
    boundaries = packet.get("coverage_summary", {}).get("valuation_blocking_boundaries", [])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and any(("公开价格代理不得替代公司合同ASP" in x or "公开价格代理不得替代公司合同平均售价" in x) for x in boundaries) and any("官方分产品/分部证据不得替代WF6/NF3" in x for x in boundaries) and any("订单与收入确认代理证据不得替代单品订单金额" in x for x in boundaries) and any("客户认证/具名客户披露证据不得替代单品客户份额" in x for x in boundaries) and any("客户侧验证探针不得把供应商年报自述" in x for x in boundaries) and any("下游客户公开文件探针不得把客户侧年报中的供应商名" in x for x in boundaries) and any("产销量/库存/产能利用证据不得替代单品客户份额" in x for x in boundaries) and any("成本结构/毛利/价格传导证据不得替代单品毛利率" in x for x in boundaries) and any("竞争格局/行业地位证据不得替代单品收入" in x for x in boundaries) and any("年报短摘不得替代单品订单" in x for x in boundaries) and any("年报前五明细" in x and "单品客户份额" in x for x in boundaries) and any("管理层讨论不得替代单品订单" in x for x in boundaries) and any("下游需求锚不得替代上游公司客户" in x for x in boundaries) and any("AI平台需求锚不得替代A股上游客户" in x for x in boundaries) and any("公司澄清不得替代客户侧认证" in x for x in boundaries) and any("互动问答不得替代具体订单金额" in x for x in boundaries) and any("投关调研标题索引和正文关键词探针不得替代订单金额" in x for x in boundaries) and any("合同公告扫描不得把工业气体" in x and "电子材料单品订单" in x for x in boundaries) and any(("合同金额经济性约束不得替代合同ASP" in x or "合同金额经济性约束不得替代合同平均售价" in x) for x in boundaries) and any("订单耐久性证据不得把历史订单" in x and "持续订单" in x for x in boundaries) and any("价格与毛利入模门禁不得把公开价格" in x and "当前单品毛利" in x for x in boundaries) and any("业绩预告/快报不得替代单品订单" in x for x in boundaries) and any("问询/审核回复证据不得把问询标题" in x for x in boundaries) and any(("官方单品收入/订单金额边界不得替代合同ASP" in x or "官方单品收入/订单金额边界不得替代合同平均售价" in x) for x in boundaries) and any("半导体高纯钨材边界证据不得替代半导体客户" in x for x in boundaries) and any("含氟电子材料边界证据不得替代电子材料客户" in x for x in boundaries) and any("资源、配额和一体化证据不得替代半导体高纯钨材" in x for x in boundaries) and any("交易风险公告不得替代订单" in x for x in boundaries) and any("股东结构与机构持仓证据不得替代客户订单" in x for x in boundaries) and any("融资融券证据不得替代客户订单" in x for x in boundaries) and any("龙虎榜席位证据不得替代客户订单" in x for x in boundaries) and any("制程功能证据不得替代客户认证" in x for x in boundaries) and any("政策管制证据不得替代公司实际销售价格" in x for x in boundaries) and any("公司产品能力证据不得替代客户认证" in x for x in boundaries) and any("项目产能证据不得替代WF6单品产能拆分" in x for x in boundaries) and any("招股书价格/毛利披露边界不得替代当前合同平均售价" in x for x in boundaries) and any("公司级HFC配额证据不得替代含氟电子材料" in x for x in boundaries) and any("隐含增长反推不得替代订单金额" in x for x in boundaries) and any("证据成熟度不得替代订单金额" in x for x in boundaries) and any("公开券商覆盖历史质量不得替代券商全文模型" in x for x in boundaries) and any("公开券商预测分歧不得替代Wind/Choice一致预期" in x for x in boundaries) and any("公开券商全文PDF证据不得替代付费一致预期" in x for x in boundaries)
    return len(rows) >= 23 and required_groups <= groups and not missing and text_ok and boundary_ok, f"rows={len(rows)}, missing_groups={sorted(required_groups - groups)}, missing={missing[:3]}, text_ok={text_ok}, boundary_ok={boundary_ok}"

def data_completeness_dashboard_complete() -> tuple[bool, str]:
    packet = load_json("data/data_completeness_dashboard.json")
    rows = packet.get("rows", [])
    domains = {r.get("domain") for r in rows}
    required_domains = {
        "价格、股本、市值和流动性",
        "基础财务、单季趋势和现金流质量",
        "主营构成、官方分部和产品毛利",
        "产销量、库存、产能利用和项目建设",
        "客户链、认证、前五客户和公司沟通",
        "合同、订单、收入确认和履约代理",
        "公开价格、下游需求、AI平台和政策锚",
        "高成长业绩、单品转化和隐含增长",
        "外部券商、来源治理和字段矩阵",
    }
    required_keys = ["domain", "coverage", "completion_status", "core_evidence", "valuation_use", "remaining_gap", "model_rule"]
    missing = []
    for r in rows:
        for k in required_keys:
            if r.get(k) in (None, "", []):
                missing.append(f"{r.get('domain')}:{k}")
    data_md = (BASE / "data/data_completeness_dashboard.md").read_text(encoding="utf-8")
    analysis = (BASE / "analysis/data_completeness_dashboard.md").read_text(encoding="utf-8")
    section = (BASE / "sections/ch01_dashboard.tex").read_text(encoding="utf-8")
    main_text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    exhibit = (BASE / "analysis/exhibit_plan.md").read_text(encoding="utf-8")
    text_ok = all(s in data_md for s in ["数据完整性审计总览", "完整字段", "代理", "阻断增长每股收益"]) and "数据完整性审计总览" in analysis
    section_ok = all(s in section for s in ["数据补齐到了哪一步", "数据完整性审计总览", "完整字段进估值", "硬缺口阻断上修"])
    main_ok = all(s in main_text for s in ["数据完整性审计总览", "完整字段进估值", "代理字段进监测", "硬缺口阻断上修"])
    boundary_ok = packet.get("gate_status") == "CONDITIONAL" and packet.get("covered_tickers") == 18 and packet.get("domain_count") == 9 and "不是P0硬缺口关闭证明" in packet.get("use_boundary", "") and "数据完整性审计总览" in exhibit
    return len(rows) == 9 and required_domains <= domains and not missing and text_ok and section_ok and main_ok and boundary_ok, f"rows={len(rows)}, missing_domains={sorted(required_domains - domains)}, missing={missing[:3]}, text={text_ok}, section={section_ok}, main={main_ok}, boundary={boundary_ok}"

def source_registry() -> tuple[bool, str]:
    j = load_json("data/source_registry.json")
    failed = j.get("failed_count", 0)
    captured = j.get("captured_count", 0)
    sources = len(j.get("sources", []))
    return sources >= 8 and failed == 0 and captured == sources, f"sources={sources}, captured={captured}, failed={failed}"

def source_exhaustion_complete() -> tuple[bool, str]:
    j = load_json("source_exhaustion_log.json")
    probes = j.get("hard_gap_probes", [])
    contract_scan_errors = j.get("contract_announcement_scan_errors", [])
    gaps = {p.get("gap") for p in probes}
    required = {
        "公司合同ASP或销售价格区间",
        "订单金额、长单条款、交付节奏和收入确认比例",
        "WF6/NF3/电子特气单品收入拆分",
        "单品毛利率和成本传导机制",
        "具名晶圆厂客户、客户份额和认证阶段",
        "半导体高纯钨材客户、订单和收入",
        "含氟电子材料客户、订单和单品价差",
    }
    missing = []
    for p in probes:
        for k in ["gap", "checked_sources", "found", "not_found", "valuation_boundary", "next_required_source"]:
            if p.get(k) in (None, "", []):
                missing.append(f"{p.get('gap')}:{k}")
    md = (BASE / "source_exhaustion_log.md").read_text(encoding="utf-8")
    text_ok = all(s in md for s in ["硬缺口来源穷尽", "公司合同平均售价", "订单金额", "单品毛利", "具名晶圆厂客户", "客户侧验证探针", "下游客户公开文件探针", "反向验证为0/8", "产品级采购订单", "半导体高纯钨材客户", "含氟电子材料客户", "合同/中标/供货协议公告全文扫描", "问询/审核回复公告证据", "不得进入增长每股收益"])
    contract_partial_ok = "中船特气2025年六氟化钨采购合同约1.1904亿元" in md and "11种电子气体产品采购合同约1.4822亿元" in md and "订单金额为历史部分补证" in md and "多数标的也缺主题单品订单金额" in md
    prospectus_ok = "招股说明书" in md and "平均单价" in md and "豁免披露" in md and "历史产销" in md
    if contract_scan_errors:
        scan_error_ok = (
            "分项公告扫描降级" in md
            and j.get("contract_announcement_scan_error_count") == len(contract_scan_errors)
            and all(str(e.get("ticker", "")) in md and "不得据此认定该标的没有主题订单" in md for e in contract_scan_errors)
        )
    else:
        scan_error_ok = j.get("contract_announcement_scan_error_count") == 0 and "无逐标的合同公告扫描失败" in md
    boundary_ok = j.get("gate_status") == "CONDITIONAL" and "公开来源抓取成功不等于硬缺口关闭" in j.get("summary", "") and "订单金额已有历史部分补证" in j.get("summary", "") and "平台订单可见度提高" in j.get("summary", "") and "问询/审核回复公告扫描" in j.get("summary", "") and "未披露可量化单品字段前不改变增长每股收益信用" in j.get("summary", "") and "招股书已证明平均单价豁免披露" in j.get("summary", "") and "客户侧验证探针已确认8个客户链锚点" in j.get("summary", "") and "反向验证0/8" in j.get("summary", "") and "下游客户公开文件探针进一步检查客户侧公开年报" in j.get("summary", "") and "产品级采购订单/份额/价格反向验证仍为0" in j.get("summary", "") and "半导体高纯钨材边界证据" in j.get("summary", "") and "含氟电子材料边界证据" in j.get("summary", "") and "生态环境部HFC配额" in j.get("summary", "")
    return len(probes) >= 5 and required <= gaps and not missing and text_ok and contract_partial_ok and prospectus_ok and scan_error_ok and boundary_ok, f"probes={len(probes)}, missing={missing[:3]}, text_ok={text_ok}, contract_partial_ok={contract_partial_ok}, prospectus_ok={prospectus_ok}, scan_errors={len(contract_scan_errors)}, scan_error_ok={scan_error_ok}, boundary_ok={boundary_ok}"

def mermaid_exists() -> tuple[bool, str]:
    text = (BASE / "analysis/wf6_chain_map.mmd").read_text(encoding="utf-8")
    return text.startswith("flowchart"), "Mermaid flowchart"

def json_valid() -> tuple[bool, str]:
    total = 0
    for p in list((BASE / "data").glob("*.json")) + list(BASE.glob("*.json")):
        total += 1
        json.loads(p.read_text(encoding="utf-8"))
    return total >= 5, f"json={total}"

def no_placeholders() -> tuple[bool, str]:
    text = (BASE / "main_current_text.txt").read_text(encoding="utf-8", errors="ignore")
    bad = ["<Report Title>", "TODO", "PLACEHOLDER"]
    hits = [b for b in bad if b in text]
    return not hits, f"hits={hits}"

def main() -> int:
    checks = []
    for rel in [
        "research_brief.md",
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
        "data/raw_market_data.md",
        "data/raw_financials.md",
        "data/verified_market_data.md",
        "data/verified_financials.md",
        "data/source_registry.md",
        "data/claim_audit.md",
        "data/supply_chain_relationships.md",
        "data/customer_chain_audit.md",
        "data/growth_driver_model.json",
        "data/fundamental_quality_snapshot.json",
        "data/fundamental_quality_snapshot.md",
        "data/data_gap_matrix.json",
        "data/data_gap_matrix.md",
        "data/external_evidence_probe.json",
        "data/external_evidence_probe.md",
        "data/broker_research_snapshot.json",
        "data/broker_research_snapshot.md",
        "data/public_broker_coverage_history.json",
        "data/public_broker_coverage_history.md",
        "data/public_broker_forecast_evidence.json",
        "data/public_broker_forecast_evidence.md",
        "data/public_broker_fulltext_evidence.json",
        "data/public_broker_fulltext_evidence.md",
        "data/business_segment_snapshot.json",
        "data/business_segment_snapshot.md",
        "data/official_segment_table_evidence.json",
        "data/official_segment_table_evidence.md",
        "data/order_revenue_recognition_evidence.json",
        "data/order_revenue_recognition_evidence.md",
        "data/product_conversion_constraint.json",
        "data/product_conversion_constraint.md",
        "data/implied_growth_requirement.json",
        "data/implied_growth_requirement.md",
        "data/evidence_maturity_monitor.json",
        "data/evidence_maturity_monitor.md",
        "data/customer_qualification_evidence.json",
        "data/customer_qualification_evidence.md",
        "data/customer_side_verification_probe.json",
        "data/customer_side_verification_probe.md",
        "data/downstream_customer_public_file_probe.json",
        "data/downstream_customer_public_file_probe.md",
        "data/production_sales_inventory_evidence.json",
        "data/production_sales_inventory_evidence.md",
        "data/cost_margin_pass_through_evidence.json",
        "data/cost_margin_pass_through_evidence.md",
        "data/competitive_position_evidence.json",
        "data/competitive_position_evidence.md",
        "data/industry_region_segment_snapshot.json",
        "data/industry_region_segment_snapshot.md",
        "data/capital_working_capital_snapshot.json",
        "data/capital_working_capital_snapshot.md",
        "data/rd_technology_intensity_snapshot.json",
        "data/rd_technology_intensity_snapshot.md",
        "data/customer_supplier_concentration_snapshot.json",
        "data/customer_supplier_concentration_snapshot.md",
        "data/customer_supplier_detail_snapshot.json",
        "data/customer_supplier_detail_snapshot.md",
        "data/annual_report_theme_evidence_snapshot.json",
        "data/annual_report_theme_evidence_snapshot.md",
        "data/annual_report_evidence_snippet_snapshot.json",
        "data/annual_report_evidence_snippet_snapshot.md",
        "data/annual_report_mdna_snapshot.json",
        "data/annual_report_mdna_snapshot.md",
        "data/quarterly_financial_trend_snapshot.json",
        "data/quarterly_financial_trend_snapshot.md",
        "data/market_tape_snapshot.json",
        "data/market_tape_snapshot.md",
        "data/official_market_liquidity_snapshot.json",
        "data/official_market_liquidity_snapshot.md",
        "data/shareholder_crowding_snapshot.json",
        "data/shareholder_crowding_snapshot.md",
        "data/margin_leverage_snapshot.json",
        "data/margin_leverage_snapshot.md",
        "data/dragon_tiger_seat_snapshot.json",
        "data/dragon_tiger_seat_snapshot.md",
        "data/capitalization_audit.json",
        "data/capitalization_audit.md",
        "data/share_count_reconciliation.json",
        "data/share_count_reconciliation.md",
        "data/public_price_proxy_snapshot.json",
        "data/public_price_proxy_snapshot.md",
        "data/downstream_demand_anchor_snapshot.json",
        "data/downstream_demand_anchor_snapshot.md",
        "data/ai_platform_demand_anchor_snapshot.json",
        "data/ai_platform_demand_anchor_snapshot.md",
        "data/company_clarification_snapshot.json",
        "data/company_clarification_snapshot.md",
        "data/investor_relations_qa_evidence.json",
        "data/investor_relations_qa_evidence.md",
        "data/ir_activity_record_evidence.json",
        "data/ir_activity_record_evidence.md",
        "data/contract_order_announcement_evidence.json",
        "data/contract_order_announcement_evidence.md",
        "data/contract_economics_constraint.json",
        "data/contract_economics_constraint.md",
        "data/order_durability_evidence.json",
        "data/order_durability_evidence.md",
        "data/price_margin_valuation_gate.json",
        "data/price_margin_valuation_gate.md",
        "data/earnings_disclosure_calendar.json",
        "data/earnings_disclosure_calendar.md",
        "data/performance_forecast_evidence.json",
        "data/performance_forecast_evidence.md",
        "data/regulatory_inquiry_evidence.json",
        "data/regulatory_inquiry_evidence.md",
        "data/official_single_product_revenue_boundary.json",
        "data/official_single_product_revenue_boundary.md",
        "data/semiconductor_tungsten_material_boundary.json",
        "data/semiconductor_tungsten_material_boundary.md",
        "data/fluorinated_electronic_material_boundary.json",
        "data/fluorinated_electronic_material_boundary.md",
        "data/trading_risk_announcement_snapshot.json",
        "data/trading_risk_announcement_snapshot.md",
        "data/technical_process_evidence.json",
        "data/technical_process_evidence.md",
        "data/policy_export_control_evidence.json",
        "data/policy_export_control_evidence.md",
        "data/company_product_capability_evidence.json",
        "data/company_product_capability_evidence.md",
        "data/capacity_project_evidence.json",
        "data/capacity_project_evidence.md",
        "data/prospectus_price_boundary_evidence.json",
        "data/prospectus_price_boundary_evidence.md",
        "data/hfc_quota_allocation_evidence.json",
        "data/hfc_quota_allocation_evidence.md",
        "data/resource_security_evidence.json",
        "data/resource_security_evidence.md",
        "data/structured_data_provenance.json",
        "data/structured_data_provenance.md",
        "data/hard_gap_action_plan.json",
        "data/hard_gap_action_plan.md",
        "data/field_evidence_matrix.json",
        "data/field_evidence_matrix.md",
        "data/data_completeness_dashboard.json",
        "data/data_completeness_dashboard.md",
        "analysis/template_brief.md",
        "analysis/industry_landscape.md",
        "analysis/house_view.md",
        "analysis/exhibit_plan.md",
        "analysis/visual_review.md",
        "analysis/supply_chain_model.md",
        "analysis/external_evidence_probe.md",
        "analysis/broker_research_snapshot.md",
        "analysis/public_broker_coverage_history.md",
        "analysis/public_broker_forecast_evidence.md",
        "analysis/public_broker_fulltext_evidence.md",
        "analysis/business_segment_snapshot.md",
        "analysis/official_segment_table_evidence.md",
        "analysis/order_revenue_recognition_evidence.md",
        "analysis/product_conversion_constraint.md",
        "analysis/implied_growth_requirement.md",
        "analysis/evidence_maturity_monitor.md",
        "analysis/customer_qualification_evidence.md",
        "analysis/customer_side_verification_probe.md",
        "analysis/downstream_customer_public_file_probe.md",
        "analysis/production_sales_inventory_evidence.md",
        "analysis/cost_margin_pass_through_evidence.md",
        "analysis/competitive_position_evidence.md",
        "analysis/industry_region_segment_snapshot.md",
        "analysis/capital_working_capital_snapshot.md",
        "analysis/rd_technology_intensity_snapshot.md",
        "analysis/customer_supplier_concentration_snapshot.md",
        "analysis/customer_supplier_detail_snapshot.md",
        "analysis/annual_report_theme_evidence_snapshot.md",
        "analysis/annual_report_evidence_snippet_snapshot.md",
        "analysis/annual_report_mdna_snapshot.md",
        "analysis/quarterly_financial_trend_snapshot.md",
        "analysis/market_tape_snapshot.md",
        "analysis/official_market_liquidity_snapshot.md",
        "analysis/shareholder_crowding_snapshot.md",
        "analysis/margin_leverage_snapshot.md",
        "analysis/dragon_tiger_seat_snapshot.md",
        "analysis/capitalization_audit.md",
        "analysis/share_count_reconciliation.md",
        "analysis/public_price_proxy_snapshot.md",
        "analysis/downstream_demand_anchor_snapshot.md",
        "analysis/ai_platform_demand_anchor_snapshot.md",
        "analysis/company_clarification_snapshot.md",
        "analysis/investor_relations_qa_evidence.md",
        "analysis/ir_activity_record_evidence.md",
        "analysis/contract_order_announcement_evidence.md",
        "analysis/contract_economics_constraint.md",
        "analysis/order_durability_evidence.md",
        "analysis/price_margin_valuation_gate.md",
        "analysis/earnings_disclosure_calendar.md",
        "analysis/performance_forecast_evidence.md",
        "analysis/regulatory_inquiry_evidence.md",
        "analysis/official_single_product_revenue_boundary.md",
        "analysis/semiconductor_tungsten_material_boundary.md",
        "analysis/fluorinated_electronic_material_boundary.md",
        "analysis/trading_risk_announcement_snapshot.md",
        "analysis/technical_process_evidence.md",
        "analysis/policy_export_control_evidence.md",
        "analysis/company_product_capability_evidence.md",
        "analysis/capacity_project_evidence.md",
        "analysis/prospectus_price_boundary_evidence.md",
        "analysis/hfc_quota_allocation_evidence.md",
        "analysis/resource_security_evidence.md",
        "analysis/structured_data_provenance.md",
        "analysis/hard_gap_action_plan.md",
        "analysis/field_evidence_matrix.md",
        "analysis/data_completeness_dashboard.md",
        "analysis/company_fundamental_cards.md",
        "analysis/chain_earnings_bridge.md",
        "analysis/fundamental_quality_model.md",
        "analysis/growth_earnings_model.md",
        "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/risk_framework.md",
        "review_log.md",
        "completion_audit_manifest.json",
        "completion_audit_manifest.md",
        "source_exhaustion_log.json",
        "source_exhaustion_log.md",
        "data_room_index.md",
    ]:
        passed, detail = ok_file(rel)
        checks.append((f"file:{rel}", passed, detail))
    for name, fn in [
        ("pdf_pages", pdf_pages),
        ("template_exhibit_quality", template_exhibit_quality),
        ("fundamental_quality_complete", fundamental_quality_complete),
        ("quarterly_financial_trend_complete", quarterly_financial_trend_complete),
        ("market_tape_complete", market_tape_complete),
        ("official_market_liquidity_complete", official_market_liquidity_complete),
        ("shareholder_crowding_complete", shareholder_crowding_complete),
        ("margin_leverage_complete", margin_leverage_complete),
        ("dragon_tiger_complete", dragon_tiger_complete),
        ("capitalization_audit_complete", capitalization_audit_complete),
        ("share_count_reconciliation_complete", share_count_reconciliation_complete),
        ("public_price_proxy_complete", public_price_proxy_complete),
        ("prospectus_price_boundary_complete", prospectus_price_boundary_complete),
        ("hfc_quota_allocation_complete", hfc_quota_allocation_complete),
        ("resource_security_evidence_complete", resource_security_evidence_complete),
        ("downstream_demand_complete", downstream_demand_complete),
        ("ai_platform_demand_complete", ai_platform_demand_complete),
        ("company_clarification_complete", company_clarification_complete),
        ("investor_relations_qa_complete", investor_relations_qa_complete),
        ("ir_activity_record_complete", ir_activity_record_complete),
        ("contract_order_announcement_complete", contract_order_announcement_complete),
        ("contract_economics_constraint_complete", contract_economics_constraint_complete),
        ("order_durability_evidence_complete", order_durability_evidence_complete),
        ("price_margin_valuation_gate_complete", price_margin_valuation_gate_complete),
        ("earnings_disclosure_calendar_complete", earnings_disclosure_calendar_complete),
        ("performance_forecast_complete", performance_forecast_complete),
        ("regulatory_inquiry_complete", regulatory_inquiry_complete),
        ("official_single_product_revenue_boundary_complete", official_single_product_revenue_boundary_complete),
        ("semiconductor_tungsten_material_boundary_complete", semiconductor_tungsten_material_boundary_complete),
        ("fluorinated_electronic_material_boundary_complete", fluorinated_electronic_material_boundary_complete),
        ("trading_risk_complete", trading_risk_complete),
        ("technical_process_complete", technical_process_complete),
        ("policy_export_control_complete", policy_export_control_complete),
        ("company_product_capability_complete", company_product_capability_complete),
        ("capacity_project_evidence_complete", capacity_project_evidence_complete),
        ("external_evidence_complete", external_evidence_complete),
        ("broker_research_complete", broker_research_complete),
        ("public_broker_coverage_complete", public_broker_coverage_complete),
        ("public_broker_forecast_complete", public_broker_forecast_complete),
        ("public_broker_fulltext_complete", public_broker_fulltext_complete),
        ("business_segment_complete", business_segment_complete),
        ("official_segment_table_complete", official_segment_table_complete),
        ("order_revenue_recognition_complete", order_revenue_recognition_complete),
        ("product_conversion_constraint_complete", product_conversion_constraint_complete),
        ("implied_growth_requirement_complete", implied_growth_requirement_complete),
        ("evidence_maturity_monitor_complete", evidence_maturity_monitor_complete),
        ("customer_qualification_evidence_complete", customer_qualification_evidence_complete),
        ("customer_side_verification_probe_complete", customer_side_verification_probe_complete),
        ("downstream_customer_public_file_probe_complete", downstream_customer_public_file_probe_complete),
        ("production_sales_inventory_complete", production_sales_inventory_complete),
        ("cost_margin_pass_through_complete", cost_margin_pass_through_complete),
        ("competitive_position_complete", competitive_position_complete),
        ("industry_region_segment_complete", industry_region_segment_complete),
        ("capital_working_capital_complete", capital_working_capital_complete),
        ("rd_technology_intensity_complete", rd_technology_intensity_complete),
        ("customer_supplier_concentration_complete", customer_supplier_concentration_complete),
        ("customer_supplier_detail_complete", customer_supplier_detail_complete),
        ("annual_report_theme_evidence_complete", annual_report_theme_evidence_complete),
        ("annual_report_evidence_snippet_complete", annual_report_evidence_snippet_complete),
        ("annual_report_mdna_complete", annual_report_mdna_complete),
        ("valuation_complete", valuation_complete),
        ("risk_framework_complete", risk_framework_complete),
        ("supply_chain_complete", supply_chain_complete),
        ("growth_earnings_complete", growth_earnings_complete),
        ("structured_data_provenance_complete", structured_data_provenance_complete),
        ("hard_gap_action_plan_complete", hard_gap_action_plan_complete),
        ("field_evidence_matrix_complete", field_evidence_matrix_complete),
        ("data_completeness_dashboard_complete", data_completeness_dashboard_complete),
        ("source_registry", source_registry),
        ("source_exhaustion_complete", source_exhaustion_complete),
        ("mermaid_exists", mermaid_exists),
        ("json_valid", json_valid),
        ("no_placeholders", no_placeholders),
    ]:
        passed, detail = fn()
        checks.append((name, passed, detail))
    fail = 0
    for name, passed, detail in checks:
        print(("PASS" if passed else "FAIL") + f": {name} - {detail}")
        fail += 0 if passed else 1
    print(f"SUMMARY: PASS={len(checks)-fail} FAIL={fail}")
    return 1 if fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
