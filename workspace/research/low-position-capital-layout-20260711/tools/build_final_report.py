#!/usr/bin/env python3
"""Generate the final full-market LaTeX report from repaired artifacts."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SECTIONS_DIR = CASE_DIR / "sections"


STAGE_LABELS = {
    "silent_accumulation": "静默吸纳",
    "launch_confirmation": "启动确认",
    "flow_watch": "资金观察",
    "one_day_rebound": "单日反弹",
    "low_price_no_flow": "低位无资金",
    "no_signal": "无信号",
}

DISPOSITION_LABELS = {
    "quiet_accumulation_priority": "静默验证",
    "low_position_earnings_priority": "低位盈利优先",
    "launched_with_runway_candidate": "启动后空间候选",
    "earnings_validation_watch": "盈利验证观察",
    "earnings_delivered_price_advanced": "业绩兑现但价格先行",
    "watch_insufficient_price_history": "历史不足观察",
    "earnings_decline_watch": "盈利下滑观察",
    "exclude_nonrecurring_dominated": "一次性主导排除",
    "exclude_deducted_profit_nonpositive": "扣非不正排除",
}

ACTION_LABELS = {
    "core review / pullback entry": "核心复核／回撤进入",
    "pullback entry / earnings validation": "回撤进入／业绩验证",
    "income-oriented market-supported watch": "收益型观察",
    "trend pullback core / milestone validation": "趋势回撤核心／里程碑验证",
    "earnings-delivery pullback / market-supported watch": "兑现后回撤／市场支持观察",
}

CONDITIONAL_LABELS = {
    "watchlist_only_insufficient_segment_economics": "分部证据不足",
    "watchlist_only_formally_bounded_segment_economics": "分部边界已降权",
    "watchlist_only_cycle_model_unresolved": "周期模型未闭合",
    "sector_validation_market_supported_watch": "行业验证观察",
}

THEME_DISPOSITION_LABELS = {
    "current_price_core_model": "正式模型",
    "conditional_watch_insufficient_segment_economics": "分部证据不足",
    "conditional_watch_cycle_model_unresolved": "周期模型未闭合",
    "post_preview_model_refresh": "预告后重估",
    "earnings_delivered_wait_pullback": "兑现待回撤",
    "price_above_broker_anchor": "价格超外部锚",
    "oneoff_discount_watch": "一次性折价",
    "exclude_nonrecurring_dominated": "一次性主导排除",
    "price_advanced_wait_earnings": "价格先行",
    "broker_supported_no_preview": "研报支持待中报",
    "cycle_watch_price_demanding": "周期估值偏高",
    "cycle_watch_q2_deceleration": "Q2减速观察",
    "cycle_watch_working_capital": "营运资金观察",
    "no_preview_fundamental_watch": "基本面观察",
    "no_preview_cycle_watch": "周期观察",
    "no_preview_storage_watch": "存储观察",
    "no_preview_pipeline_watch": "管线观察",
    "no_preview_order_watch": "订单观察",
}

EXPANDED_ACTION_LABELS = {
    "high-upside model candidate / validate before entry": "高空间模型候选／先验证",
    "selective pullback entry / earnings validation": "选择性回撤／业绩验证",
    "market-supported watch / wait for margin of safety": "市场支持观察／等安全边际",
    "valuation full / watch only": "估值已满／仅观察",
    "high valuation risk / avoid chasing": "高估值风险／勿追",
    "avoid / insufficient valuation quality": "模型质量未过关／排除",
    "not priceable": "不可定价",
    "not priceable / wait for positive denominator": "不可定价／等待正分母",
    "IPO watch / wait for issue price and trading history": "IPO待定价／等待交易历史",
    "watchlist only / probability value below current price": "概率价值低于现价／仅观察",
}

MODEL_TIER_LABELS = {
    "linked_full_priority_model": "优先池完整模型",
    "linked_formal_valuation_model": "高置信正式模型",
    "linked_conditional_watch_model": "条件观察模型",
    "screening_house_range": "H1筛选区间",
    "theme_screening_house_range": "主题筛选区间",
    "ipo_prepricing_boundary": "IPO定价边界",
    "not_priceable": "不可定价",
}

PRIORITY_READER_TEXT = {
    "601225": ("周期调整PE与股息底部交叉验证", "煤价企稳、2026E EPS高于2.08元且分红稳定", "煤价下跌、扣非利润走弱或分红下降"),
    "002379": ("扣非EPS周期PE，并以原始券商目标交叉验证", "铝价成本差与高分红延续，H2扣非利润保持强势", "铝价成本差收窄，或分红及现金转化恶化"),
    "600346": ("预告后正常化PE，并对一次性收益折价", "炼化价差稳定且H2经营现金流为正", "一次性收益占比上升、价差收窄或H2利润低于基准桥"),
    "002738": ("锂周期PE，并以资源产量和现金流验证", "锂价、资源产量与H2现金转化共同支撑EPS", "锂价反转、产量不及预期或经营现金流持续偏弱"),
    "002048": ("汽车零部件正常化PE，并对陈旧预测折价", "欧洲业务修复和机器人增量推升扣非利润", "H2扣非利润低于H1节奏或海外亏损再次扩大"),
    "002532": ("电解铝周期PE，并验证产能释放与分红", "低成本产能释放且分红支撑约1.9元EPS桥", "铝价差、产量或现金流显著走弱"),
    "600595": ("周期PE并计入现金流折价", "电解铝与加工业务单位利润稳定、经营现金流转正", "经营现金流继续为负或单位盈利快速正常化"),
    "601360": ("收入倍数与盈利路径交叉验证", "安全与AI收入提速、经营现金流转正", "收入停滞、现金流持续为负或AI商业化贡献不显著"),
    "600918": ("PB-ROE与盈利情景混合估值", "资本市场活跃度和财富管理收入支撑H2利润", "自营收益反转，或ROE、手续费收入低于基准"),
    "300014": ("预告后PE，并验证储能出货与现金流", "储能出货、毛利率和H2现金转化验证EPS", "经营现金流持续为负，或储能价格与毛利低于预期"),
    "000987": ("PB-ROE与盈利分部混合估值", "投资与租赁盈利强劲、账面价值稳定增长", "投资收益反转或ROE低于基准"),
    "600120": ("PB-ROE与盈利分部混合估值", "金融持股与经营利润转化为持续ROE", "H2利润减速或金融资产收益反转"),
    "000703": ("预告后炼化周期PE，并使用券商合理价值区间", "文莱炼化盈利和H2现金流验证预告后区间", "炼化价差收窄或经营现金流持续为负"),
    "000301": ("石化与新材料结构的预告后重置PE", "H2新材料占比和正现金流支撑新盈利分母", "价差正常化或H2扣非利润低于基准桥"),
    "002414": ("军工预告后重置PE，并验证订单与现金流", "订单、合同负债和H2现金流支撑预告后重置", "订单转化减速或经营现金流持续为负"),
    "002558": ("预告后游戏PE，并验证新品与出海", "新品和海外收入支撑H2扣非利润", "产品管线或商业化低于预期，H2利润低于基准桥"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def tex(value: Any) -> str:
    text = str(value if value is not None else "---")
    replacements = {
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
    return "".join(replacements.get(char, char) for char in text)


def num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "---"
    return f"{float(value):.{digits}f}"


def pct(value: Any, digits: int = 1, signed: bool = False) -> str:
    if value is None:
        return "---"
    prefix = "+" if signed and float(value) > 0 else ""
    return f"{prefix}{float(value):.{digits}f}\\%"


def stage_label(value: str) -> str:
    return STAGE_LABELS.get(value, value)


def disposition_label(value: str) -> str:
    return DISPOSITION_LABELS.get(value, value)


def dashboard_section(
    valuation_rows: list[dict[str, Any]],
    conditional_rows: list[dict[str, Any]],
    priority_rows: list[dict[str, Any]],
    priority_valuations: list[dict[str, Any]],
    candidate_valuation: dict[str, Any],
    report_wide_ledger: dict[str, Any],
    evidence_closure: dict[str, Any],
    preview_screen: dict[str, Any],
) -> str:
    formal = sorted(valuation_rows, key=lambda row: row["upside"], reverse=True)
    formal_map = {row["ticker"]: row for row in valuation_rows}
    hengrui_upside = formal_map["600276"]["upside"] * 100
    fii_upside = formal_map["601138"]["upside"] * 100
    quiet = [
        row
        for row in priority_rows
        if row["full_market_disposition"]
        in {"quiet_accumulation_priority", "low_position_earnings_priority"}
    ]
    launched = [
        row
        for row in priority_rows
        if row["full_market_disposition"] == "launched_with_runway_candidate"
    ]
    lines = [
        r"\section{投资委员会结论}",
        "",
        (
            r"本轮重建后的结论比旧稿更克制：全市场业绩预告母池不是54只，而是"
            f"\\textbf{{{preview_screen['preview_company_count']}家A股公司、"
            f"{preview_screen['eligible_a_share_metric_row_count']}条合格指标记录}}；"
            f"统一规则筛出{preview_screen['high_impact_candidate_count']}只高影响候选，"
            r"再经价格位置、扣非纯度、Q1现金流和研报时效过滤为16只优先证据池。"
            r"本次估值扩展后，16只优先股全部建立公司级熊／基准／牛模型；"
            f"{candidate_valuation['priceable_count']}只H1候选有公平价值区间，"
            f"{candidate_valuation['not_priceable_count']}只因无有效现价不可定价；"
            f"报告117只去重标的中{report_wide_ledger['priceable_count']}只可定价，"
            f"{report_wide_ledger['not_priceable_count']}只为IPO定价时间边界。"
            f"证据闭环总账覆盖{evidence_closure['row_count']}只："
            f"{evidence_closure['closed_count']}只直接关闭、"
            f"{evidence_closure['downgraded_count']}只以估值降权关闭、"
            f"{evidence_closure['formal_boundary_count']}只为正式时间边界，"
            f"开放实质缺口{evidence_closure['unresolved_material_gap_count']}只。"
        ),
        "",
        r"\begin{houseviewbox}[AStock House View]",
        (
            r"\textbf{左侧机会}主要集中在有色金属、石油石化、非银金融、汽车、"
            r"计算机与电力设备中的低位盈利个股，但行业资金确认普遍不足；煤炭是唯一"
            r"“静默吸纳”且出现高影响预告标的的行业，陕西煤业却因概率价值低于现价"
            r"只能做行业验证。"
            r"\textbf{右侧机会}包括石化、军工、传媒以及旧主题池中的创新药和AI基础设施；"
            f"正式模型中恒瑞医药仍有约{hengrui_upside:.1f}\\%概率加权空间，"
            f"工业富联约{fii_upside:.1f}\\%，"
            r"但后者已是业绩兑现后的市场支持观察，而非低位配置。"
        ),
        r"\end{houseviewbox}",
        "",
        r"\section{五只正式估值结论}",
        "",
        r"\begin{exhibitbox}[Exhibit 1：正式估值池]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{1.25cm}L{1.75cm}R{1.10cm}R{1.10cm}R{1.10cm}R{1.15cm}R{1.05cm}X}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{概率值} & "
            r"\textbf{最终目标} & \textbf{空间} & \textbf{熊市} & \textbf{动作} \\"
        ),
        r"\midrule",
    ]
    for row in formal:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{num(row['current_price'])} & {num(row['scenario_expected_value'])} & "
            f"{num(row['final_target'])} & {pct(row['upside'] * 100, 1, True)} & "
            f"{num(row['bear'])} & {tex(ACTION_LABELS.get(row['action'], row['action']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{data/current\_valuation\_model\_20260711.json；现价截至2026-07-10。}",
        r"\end{exhibitbox}",
        "",
        (
            r"恒瑞医药是正式池中唯一概率加权上行超过20\%的标的；渝农商行与徐工机械"
            r"处于14\%--15\%区间，属于有安全边际但需要催化验证的回撤配置；工业富联"
            r"约11.8\%，要求H2净利润至少321.1亿元；沪农商行仅约5.5\%，更适合作为"
            r"收益型观察。所有熊市值均低于现价，避免旧稿“熊市仍上涨”的伪情景。"
        ),
        "",
        r"\section{全市场16只优先目标排序}",
        "",
        r"\begin{exhibitbox}[Exhibit 2：16只优先池概率目标]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.05cm}L{1.45cm}R{0.9cm}R{0.9cm}R{0.9cm}R{0.9cm}R{0.9cm}X}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{熊} & "
            r"\textbf{概率目标} & \textbf{牛} & \textbf{空间} & \textbf{动作} \\"
        ),
        r"\midrule",
    ]
    for row in sorted(
        priority_valuations, key=lambda item: item["upside"], reverse=True
    ):
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {num(row['current_price'])} & "
            f"{num(row['bear'])} & {num(row['probability_target'])} & "
            f"{num(row['bull'])} & {pct(row['upside'] * 100, 1, True)} & "
            f"{tex(EXPANDED_ACTION_LABELS.get(row['action'], row['action']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        (
            f"静默／低位盈利篮子共{len(quiet)}只，已启动仍有空间篮子共{len(launched)}只。"
            r"宏桥控股、天山铝业、东方盛虹、中孚实业和高德红外的模型空间居前，"
            r"但均需分别验证周期价差、产能、H2扣非、现金流或订单；"
            r"三六零的概率目标显著低于现价，说明“低位”不等于“低估”。"
        ),
        "",
        r"\begin{exhibitbox}[Exhibit 3：估值覆盖闭环]",
        r"\begin{tabularx}{\textwidth}{L{3.2cm}R{1.5cm}R{1.5cm}X}",
        r"\toprule",
        r"\textbf{估值层} & \textbf{总数} & \textbf{可定价} & \textbf{模型边界} \\",
        r"\midrule",
        r"16只优先池 & 16 & 16 & 公司级熊／基准／牛、概率目标、催化与失效 \\",
        (
            f"73只H1候选 & {candidate_valuation['row_count']} & "
            f"{candidate_valuation['priceable_count']} & "
            r"优先／正式模型链接；其余为H1扣非与行业适配筛选区间 \\"
        ),
        (
            f"117只报告总账 & {report_wide_ledger['row_count']} & "
            f"{report_wide_ledger['priceable_count']} & "
            r"73只H1候选与54只主题池去重；长鑫为IPO定价时间边界 \\"
        ),
        (
            f"117只证据闭环 & {evidence_closure['row_count']} & "
            f"{evidence_closure['row_count'] - evidence_closure['unresolved_material_gap_count']} & "
            r"逐票记录检查来源、代理、正式边界与估值后果 \\"
        ),
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{exhibitbox}",
    ]
    return "\n".join(lines)


def methodology_section(
    preview_screen: dict[str, Any],
    candidates: dict[str, Any],
    priority_evidence: dict[str, Any],
) -> str:
    distribution = Counter(
        row["full_market_disposition"] for row in candidates["rows"]
    )
    return "\n".join(
        [
            r"\section{母池、筛选与证据层级}",
            "",
            (
                r"全市场研究采用五层漏斗。第一层是申万31个一级行业；第二层是原始预告表"
            f"{preview_screen['source_preview_row_count']}条记录；按A股范围排除"
            f"{preview_screen['scope_excluded_security_count']}只B股的"
            f"{preview_screen['scope_excluded_metric_row_count']}条指标后，保留"
            f"{preview_screen['eligible_a_share_metric_row_count']}条合格输入；第三层将归母预告"
            f"透视为{preview_screen['preview_company_count']}家A股公司并完成31行业映射；"
            f"第四层按统一高影响规则筛出{preview_screen['high_impact_candidate_count']}只；"
            r"第五层结合一年位置、"
                r"20/60日趋势、扣非纯度、Q1财务和券商时效形成16只优先证据池。"
            ),
            "",
            r"\begin{exhibitbox}[Exhibit 4：全市场研究漏斗]",
            r"\begin{tabularx}{\textwidth}{L{2.2cm}R{1.5cm}X}",
            r"\toprule",
            r"\textbf{层级} & \textbf{数量} & \textbf{规则与用途} \\",
            r"\midrule",
            r"申万行业 & 31 & 行业位置、资金阶段与预告密度全覆盖 \\",
            (
                f"预告公司 & {preview_screen['preview_company_count']} & "
                r"以归母净利润预告为公司主键，扣非、EPS和营收作为质量字段 \\"
            ),
            (
                f"高影响候选 & {preview_screen['high_impact_candidate_count']} & "
                r"利润规模、同比、扣非纯度与行业阶段统一评分；不先手工挑主题 \\"
            ),
            (
                f"优先证据池 & {priority_evidence['row_count']} & "
                r"价格位置、完整历史、正增长、Q1财务与最新研报二次过滤 \\"
            ),
            r"正式估值池 & 5 & 当前价、股本、2026E分母、三情景、原始PDF Street锚全部可复算 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            r"\section{高影响与优先池规则}",
            "",
            (
                r"高影响定义为：H1归母净利至少20亿元；或至少5亿元、同比至少100\%、"
                r"扣非占比至少70\%；或至少2亿元、同比至少150\%，且行业属于静默、"
                r"启动确认或资金观察。高影响只代表值得研究，不代表可买。"
            ),
            "",
            (
                r"进入优先池还需满足正增长和完整一年价格历史。静默行业且位置不高者归"
                r"“静默吸纳”；一年位置不高、盈利质量过关者归“低位盈利”；行业处于"
                r"启动／资金观察且20日或60日涨幅达到5\%者归“已启动仍有空间”。"
                r"负增长、历史不足、扣非不正或一次性收益超过40\%者降级或排除。"
            ),
            "",
            f"\\begin{{exhibitbox}}[Exhibit 5：{candidates['row_count']}只候选最终处置]",
            r"\begin{tabularx}{\textwidth}{L{4.5cm}R{1.5cm}X}",
            r"\toprule",
            r"\textbf{处置} & \textbf{数量} & \textbf{含义} \\",
            r"\midrule",
            (
                f"静默吸纳优先 & {distribution['quiet_accumulation_priority']} & "
                r"行业和位置满足静默条件，仍需估值验证 \\"
            ),
            (
                f"低位盈利优先 & {distribution['low_position_earnings_priority']} & "
                r"价格位置低且预告质量较好，资金确认可能不足 \\"
            ),
            (
                f"已启动仍有空间 & {distribution['launched_with_runway_candidate']} & "
                r"价格启动且盈利证据较强，需约束追涨与H2兑现 \\"
            ),
            (
                f"盈利验证观察 & {distribution['earnings_validation_watch']} & "
                r"高影响但位置、行业阶段或现金流尚未同时通过 \\"
            ),
            (
                f"价格先行 & {distribution['earnings_delivered_price_advanced']} & "
                r"业绩兑现但一年位置或涨幅偏高，等待回撤 \\"
            ),
            (
                f"负增长／历史不足／一次性排除 & "
                f"{distribution['earnings_decline_watch'] + distribution['watch_insufficient_price_history'] + distribution['exclude_nonrecurring_dominated']} & "
                r"不进入优先池 \\"
            ),
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            r"\section{数据质量与边界}",
            "",
            (
                r"申万分类使用官方历史分类文件并按2026-07-11之前的最新生效记录映射。"
                r"本机证书链无法验证上游HTTPS证书，下载过程使用\texttt{verify=False}，"
                r"但归档文件大小1,161,216字节、SHA-256为"
                r"\texttt{8da3f757}\allowbreak\texttt{895a6d77}\allowbreak"
                r"\texttt{a19d8f69}\allowbreak\texttt{0cca3b30}\allowbreak"
                r"\texttt{22fa0da5}\allowbreak\texttt{6533cdb4}\allowbreak"
                r"\texttt{769f5939}\allowbreak\texttt{b4bc49d2}。"
                r"这是传输验证降级，不是内容缺失。4只B股已从A股母池排除；1只北交所A股"
                r"公司使用明确手工映射并保留。"
            ),
            "",
            (
                r"“主力资金”仍是按成交单大小划分的公开统计，不等于机构身份穿透。"
                r"浙江东方券商元数据接口返回\texttt{KeyError('infoCode')}，其Q1财务和预告"
                r"完整保留；进一步检查官方H1预告、Q1财务和公开检索后，仍未取得可核验的"
                r"当前原始券商PDF，因此Street目标权重为0，House PB-ROE／盈利桥不受影响。"
                r"16只优先池财务成功16只，当前原始PDF覆盖15只；第16只以正式回退路径闭环。"
            ),
        ]
    )


def industry_section(industry_rows: list[dict[str, Any]]) -> str:
    lines = [
        r"\section{31行业预告与阶段全景}",
        "",
        (
            r"行业表先回答“哪里有盈利变化”，再回答“价格和资金是否已经确认”。有色金属、"
            r"电子、非银金融、基础化工和电力设备是预告密度最高的五个行业，但高影响"
            r"数量多并不等于低位布局：电子和基础化工在本轮行业资金模型中仍是无信号，"
            r"有色金属多数只是单日反弹。"
        ),
        "",
        r"\small",
        r"\begin{longtable}{L{1.8cm}L{1.55cm}R{1.05cm}R{1.05cm}R{1.05cm}R{1.25cm}L{4.1cm}}",
        r"\toprule",
        (
            r"\textbf{行业} & \textbf{阶段} & \textbf{预告数} & \textbf{正利润} & "
            r"\textbf{高影响} & \textbf{H1净利和} & \textbf{代表公司} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{行业} & \textbf{阶段} & \textbf{预告数} & \textbf{正利润} & "
            r"\textbf{高影响} & \textbf{H1净利和} & \textbf{代表公司} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    for row in industry_rows:
        top = "、".join(item["company"] for item in row["top_candidates"][:3]) or "---"
        lines.append(
            f"{tex(row['industry'])} & {tex(stage_label(row.get('sector_stage')))} & "
            f"{row['preview_company_count']} & {row['positive_parent_profit_count']} & "
            f"{row['high_impact_candidate_count']} & {num(row['h1_parent_np_sum_100mn'], 1)} & "
            f"{tex(top)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        r"\sourcenote{data/full\_market\_preview\_screen\_20260712.json；利润单位为亿元。}",
        "",
        r"\section{板块判断：静默、低位与已启动}",
        "",
        r"\begin{exhibitbox}[Exhibit 6：板块机会地图]",
        r"\begin{tabularx}{\textwidth}{L{2.2cm}L{3.0cm}L{3.4cm}X}",
        r"\toprule",
        r"\textbf{类型} & \textbf{行业} & \textbf{核心证据} & \textbf{投资含义} \\",
        r"\midrule",
        (
            r"静默吸纳 & 煤炭、银行、房地产 & "
            r"行业阶段低，煤炭出现陕西煤业高影响预告 & "
            r"行业方向成立，但正式目标仍需逐票通过现价估值 \\"
        ),
        (
            r"低位盈利 & 有色、石化、非银、汽车、电力设备、计算机 & "
            r"11只优先股位于一年区间约9\%--33\% & "
            r"赔率来自位置与盈利改善，主要风险是缺少持续资金确认 \\"
        ),
        (
            r"已启动仍有空间 & 石化、军工、传媒、创新药、AI基础设施 & "
            r"趋势确认与盈利桥并存 & "
            r"只做回撤和业绩确认，不能把同比高增线性外推 \\"
        ),
        (
            r"业绩兑现但价格先行 & 电子、计算机、军工等 & "
            r"江波龙、兆易创新、香农芯创等涨幅或位置较高 & "
            r"等待新分母、现金流和回撤，不追逐旧目标价 \\"
        ),
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{exhibitbox}",
        "",
        (
            r"差异化结论是：本轮最广泛的盈利改善来自有色、电子和非银金融，但真正符合"
            r"“尚未充分启动”的是个股而非整板块；石油石化同时拥有低位的恒力石化和"
            r"已启动的恒逸石化、东方盛虹，最适合用左右两侧篮子拆分，而不是统一看多。"
        ),
    ]
    return "\n".join(lines)


def candidate_section(
    candidate_rows: list[dict[str, Any]],
    candidate_valuation_rows: list[dict[str, Any]],
    preview_screen: dict[str, Any],
) -> str:
    valuation_map = {row["ticker"]: row for row in candidate_valuation_rows}
    lines = [
        f"\\section{{{len(candidate_rows)}只统一规则候选}}",
        "",
        (
            r"下表保留全部高影响候选，目的是让读者看到哪些公司被筛入、哪些被降级，"
            r"而不是只展示最终赢家。扣非占比高于100\%表示非经常损益为负，不应误读为"
            r"数据错误；一次性收益超过40\%的标的被明确排除。"
        ),
        "",
        r"\scriptsize",
        r"\begin{longtable}{L{1.05cm}L{1.55cm}L{1.45cm}L{1.25cm}R{0.90cm}R{0.90cm}R{0.90cm}R{0.95cm}R{0.95cm}L{2.05cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{阶段} & "
            r"\textbf{H1净利} & \textbf{同比} & \textbf{扣非占} & \textbf{一年位} & "
            r"\textbf{20日} & \textbf{处置} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{阶段} & "
            r"\textbf{H1净利} & \textbf{同比} & \textbf{扣非占} & \textbf{一年位} & "
            r"\textbf{20日} & \textbf{处置} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    for row in candidate_rows:
        yoy = row["parent_np_yoy_midpoint_pct"]
        yoy_text = (
            f"{float(yoy) / 1000:.0f}k\\%"
            if yoy is not None and abs(float(yoy)) >= 10000
            else pct(yoy, 0)
        )
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['sws_industry'])} & "
            f"{tex(stage_label(row['sector_stage']))} & "
            f"{num(row['h1_parent_np_midpoint_100mn'], 1)} & "
            f"{yoy_text} & "
            f"{pct(row['deducted_profit_share_pct'], 0)} & "
            f"{pct(row.get('position_1y_pct'), 0)} & "
            f"{pct(row.get('return_20d_pct'), 0, True)} & "
            f"{tex(disposition_label(row['full_market_disposition']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        r"\sourcenote{data/full\_market\_preview\_candidates\_20260712.json。}",
        "",
        r"\section{73只候选估值区间与概率目标}",
        "",
        (
            r"本表不再让备选池停留在“观察”标签：72只有有效市场价格的候选均给出"
            r"熊市下沿、概率目标和牛市上沿；长鑫科技截至数据截点仍处IPO初步询价，"
            r"发行公告计划于2026-07-15刊登，尚不存在二级市场价格历史，因此明确标记为"
            r"IPO定价时间边界而非伪造二级目标。优先池和正式池链接公司级模型，其余标的使用H1扣非利润、"
            r"H2行业/阶段校准和行业适配方法生成筛选区间。"
        ),
        "",
        r"\scriptsize",
        r"\begin{longtable}{L{1.05cm}L{1.55cm}R{0.95cm}R{0.95cm}R{1.05cm}R{0.95cm}R{0.95cm}L{2.15cm}L{2.55cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{下沿} & "
            r"\textbf{概率目标} & \textbf{上沿} & \textbf{空间} & "
            r"\textbf{模型层级} & \textbf{动作} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{下沿} & "
            r"\textbf{概率目标} & \textbf{上沿} & \textbf{空间} & "
            r"\textbf{模型层级} & \textbf{动作} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    for candidate in candidate_rows:
        row = valuation_map[candidate["ticker"]]
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{num(row.get('current_price'))} & {num(row.get('target_low'))} & "
            f"{num(row.get('probability_target'))} & {num(row.get('target_high'))} & "
            f"{pct(row['upside'] * 100, 0, True) if row.get('upside') is not None else '---'} & "
            f"{tex(MODEL_TIER_LABELS.get(row['model_tier'], row['model_tier']))} & "
            f"{tex(EXPANDED_ACTION_LABELS.get(row['action'], row['action']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        r"\sourcenote{data/full\_market\_candidate\_valuation\_20260712.json；House筛选区间不冒充券商目标。}",
        "",
        r"\section{旧54只名单的漏选审计}",
        "",
        (
            f"统一规则筛出的{len(candidate_rows)}只高影响候选中，"
            f"{preview_screen['high_impact_omitted_from_prior_54_count']}只不在旧54只主题池。"
            r"旧名单的价值是"
            r"对AI网络、存储、创新药、军工、封装、传媒、银行和工程机械做深度穿透，"
            f"但它不能代表全市场。新报告将其降级为主题研究附录，并以"
            f"{preview_screen['preview_company_count']}家A股公司母池"
            r"作为全市场结论的唯一入口。"
        ),
        "",
        r"\begin{riskbox}[为什么不能把高同比直接变成买入]",
        (
            r"江波龙同比高增但当前价格高于概率价值；东方精工归母利润大增但扣非占比"
            r"仅约2.7\%；华润新能源利润规模大但同比下降且上市历史不足；高德红外预告"
            r"纯度高但旧券商分母过时、Q1经营现金流为负。盈利同比只是筛选入口，"
            r"不是投资结论。"
        ),
        r"\end{riskbox}",
    ]
    return "\n".join(lines)


def priority_section(
    priority_rows: list[dict[str, Any]],
    priority_valuation_rows: list[dict[str, Any]],
) -> str:
    valuation_map = {row["ticker"]: row for row in priority_valuation_rows}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in priority_rows:
        grouped[row["full_market_disposition"]].append(row)
    order = [
        "quiet_accumulation_priority",
        "low_position_earnings_priority",
        "launched_with_runway_candidate",
    ]
    titles = {
        "quiet_accumulation_priority": "静默行业验证",
        "low_position_earnings_priority": "低位盈利优先池",
        "launched_with_runway_candidate": "已启动仍有空间候选",
    }
    lines = [
        r"\section{优先池总览}",
        "",
        (
            r"16只优先股全部具备Q1结构化财务并建立公司级熊／基准／牛模型；"
            r"15只归档最新原始券商PDF，浙江东方研报接口失败但仍以官方预告、Q1财务"
            r"和PB-ROE/盈利桥建立House区间。对浙江东方已检查结构化研报接口、"
            r"官方H1预告、Q1财务和公开检索；无法取得可核验的当前原始券商PDF，"
            r"因此Street权重为0，但House模型仍可由公告分母复算。外部目标与"
            r"AStock House目标严格分列。"
        ),
    ]
    exhibit = 7
    for disposition in order:
        rows = grouped[disposition]
        lines += [
            "",
            f"\\section{{{titles[disposition]}：{len(rows)}只}}",
            "",
            f"\\begin{{exhibitbox}}[Exhibit {exhibit}：{titles[disposition]}]",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{L{1.0cm}L{1.45cm}R{0.85cm}R{0.85cm}R{0.95cm}R{0.85cm}R{0.85cm}R{0.85cm}X}",
            r"\toprule",
            (
                r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{下沿} & "
                r"\textbf{概率目标} & \textbf{上沿} & \textbf{空间} & "
                r"\textbf{H1扣非} & \textbf{动作} \\"
            ),
            r"\midrule",
        ]
        exhibit += 1
        for row in rows:
            valuation = valuation_map[row["ticker"]]
            lines.append(
                f"{tex(row['ticker'])} & {tex(row['company'])} & "
                f"{num(valuation['current_price'])} & {num(valuation['target_low'])} & "
                f"{num(valuation['probability_target'])} & {num(valuation['target_high'])} & "
                f"{pct(valuation['upside'] * 100, 0, True)} & "
                f"{num(row['h1_deducted_np_midpoint_100mn'], 1)} & "
                f"{tex(EXPANDED_ACTION_LABELS.get(valuation['action'], valuation['action']))} \\\\"
            )
        lines += [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\normalsize",
            r"\end{exhibitbox}",
            "",
        ]
        for row in rows:
            valuation = valuation_map[row["ticker"]]
            reader_method, reader_catalyst, reader_invalidation = PRIORITY_READER_TEXT[
                row["ticker"]
            ]
            lines.append(
                f"\\paragraph{{{tex(row['company'])}（{tex(row['ticker'])}）}}"
            )
            report_text = (
                f"最新研报为{row['latest_broker']} {row['latest_report_date']}《{row['latest_title']}》，"
                f"2026E EPS {num(row.get('latest_2026e_eps'))}元、PE "
                f"{num(row.get('latest_2026e_pe'), 1)}倍，状态为{row['report_status']}"
                if row.get("latest_broker")
                else (
                    "已检查结构化研报接口、官方公告与公开检索；当前原始券商"
                    "PDF未获得，外部目标权重为0，House分母来自H1预告与Q1财务"
                )
            )
            lines += [
                (
                    f"现价{num(row['current_price'])}元，一年位置"
                    f"{pct(row['position_1y_pct'])}；H1归母／扣非净利中值"
                    f"{num(row['h1_parent_np_midpoint_100mn'], 1)}/"
                    f"{num(row['h1_deducted_np_midpoint_100mn'], 1)}亿元；Q1归母净利／"
                    f"经营现金流{num(row.get('q1_parent_np_100mn'), 1)}/"
                    f"{num(row.get('q1_ocf_100mn'), 1)}亿元。{tex(report_text)}。"
                    f"估值采用{reader_method}，熊／基准／牛为"
                    f"{num(valuation['bear'])}/{num(valuation['base'])}/"
                    f"{num(valuation['bull'])}元，概率目标"
                    f"{num(valuation['probability_target'])}元，相对现价"
                    f"{pct(valuation['upside'] * 100, 1, True)}。"
                ),
                (
                    f"\\textbf{{催化}}：{reader_catalyst}；"
                    f"\\textbf{{失效}}：{reader_invalidation}。"
                    f"证据等级{tex(valuation['evidence_quality'])}，外部目标权重"
                    f"{pct(valuation['external_weight'] * 100, 0)}；未引用外部目标时，"
                    r"概率目标明确为AStock House模型。"
                ),
                "",
            ]
    lines += [
        r"\begin{keyinsight}[优先池的真正排序]",
        (
            r"按概率目标空间排序，宏桥控股、天山铝业、东方盛虹、中孚实业、高德红外"
            r"和中泰证券居前；但它们分别受铝价差、产能释放、石化价差、负现金流、"
            r"订单兑现和资本市场波动约束。三六零、陕西煤业、越秀资本与浙江东方的"
            r"概率目标不高于现价，说明低位置或高同比并不自动等于低估。"
        ),
        r"\end{keyinsight}",
    ]
    return "\n".join(lines)


def valuation_section(
    valuation_rows: list[dict[str, Any]],
    broker_rows: list[dict[str, Any]],
) -> str:
    broker_map = {row["ticker"]: row for row in broker_rows}
    lines = [
        r"\section{正式估值方法与概率框架}",
        "",
        (
            r"正式目标不再使用无来源市场锚。每只公司先按业务模式建立熊／基准／牛三情景，"
            r"概率统一为30\%／50\%／20\%；再将概率价值与同票、同源、原始PDF的Street"
            r"目标做5\%--10\%加权。现价只作为隐含预期参照，权重为零。陈旧Street锚"
            r"降至5\%，最新详细转载目标仅作方向验证、权重为零。"
        ),
        "",
        r"\begin{exhibitbox}[Exhibit 10：五只正式模型全表]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.0cm}L{1.5cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}L{1.8cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{现价} & \textbf{熊} & "
            r"\textbf{基准} & \textbf{牛} & \textbf{概率值} & \textbf{Street} & "
            r"\textbf{权重} & \textbf{目标} & \textbf{动作} \\"
        ),
        r"\midrule",
    ]
    for row in valuation_rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {num(row['current_price'])} & "
            f"{num(row['bear'])} & {num(row['base'])} & {num(row['bull'])} & "
            f"{num(row['scenario_expected_value'])} & {num(row['broker_anchor'])} & "
            f"{pct(row['broker_weight'] * 100, 0)} & {num(row['final_target'])} & "
            f"{tex(ACTION_LABELS.get(row['action'], row['action']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        r"\section{逐票模型与外部锚}",
        "",
    ]
    for row in valuation_rows:
        broker = broker_map[row["ticker"]]
        assumptions = row["scenario_assumptions"]
        lines += [
            f"\\subsection{{{tex(row['company'])}（{tex(row['ticker'])}）}}",
            "",
            (
                f"现价{num(row['current_price'])}元、2026E收入{num(row['revenue_2026e_100mn'], 1)}亿元、"
                f"归母净利{num(row['np_2026e_100mn'], 1)}亿元、EPS {num(row['eps_2026e'])}元。"
                f"熊市{num(row['bear'])}元、基准{num(row['base'])}元、牛市{num(row['bull'])}元，"
                f"概率价值{num(row['scenario_expected_value'])}元。{broker['broker']} "
                f"{broker['report_date']}原始PDF目标{num(broker['target_price'])}元，权重"
                f"{pct(broker['valuation_weight'] * 100, 0)}；最终目标{num(row['final_target'])}元，"
                f"相对现价{pct(row['upside'] * 100, 1, True)}。"
            ),
            "",
            r"\begin{itemize}",
            f"  \\item \\textbf{{熊市}}：{tex(assumptions['bear'])}。",
            f"  \\item \\textbf{{基准}}：{tex(assumptions['base'])}。",
            f"  \\item \\textbf{{牛市}}：{tex(assumptions['bull'])}。",
            f"  \\item \\textbf{{催化}}：{tex(row['catalyst'])}。",
            f"  \\item \\textbf{{失效}}：{tex(row['invalidation'])}。",
            f"  \\item \\textbf{{下季门槛}}：{tex(row['next_quarter_threshold'])}。",
            r"\end{itemize}",
            "",
        ]
    lines += [
        r"\section{Street来源治理}",
        "",
        r"\begin{exhibitbox}[Exhibit 11：同票同源原始PDF锚]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{1.1cm}L{1.7cm}L{1.4cm}R{1.0cm}L{2.7cm}R{0.9cm}X}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{券商} & \textbf{日期} & \textbf{目标} & "
            r"\textbf{方法} & \textbf{权重} & \textbf{时效} \\"
        ),
        r"\midrule",
    ]
    for row in broker_rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['broker'])} & {tex(row['report_date'])} & "
            f"{num(row['target_price'])} & {tex(row['method'])} & "
            f"{pct(row['valuation_weight'] * 100, 0)} & {tex(row['anchor_freshness'])} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        (
            r"徐工和沪农商行的原始目标明显陈旧，因此只给5\%权重；工业富联原始目标"
            r"也早于最新H1预告，给5\%。华创、华泰等最新详细转载页仍用于核对目标调整"
            r"方向，但不再被标记为原始报告，也不进入最终权重。"
        ),
    ]
    return "\n".join(lines)


def growth_section(
    growth_drivers: list[dict[str, Any]],
    sotp: dict[str, Any],
) -> str:
    hengrui = next(row for row in growth_drivers if row["ticker"] == "600276")
    fii = next(row for row in growth_drivers if row["ticker"] == "601138")
    zte = next(row for row in growth_drivers if row["ticker"] == "000063")
    jiang = next(row for row in growth_drivers if row["ticker"] == "301308")
    hs = hengrui["scenario_earnings_bridge"]
    fs = fii["scenario_earnings_bridge"]
    lines = [
        r"\section{恒瑞医药：收入、利润与SOTP闭环}",
        "",
        (
            r"恒瑞2025年收入316.29亿元，其中创新药销售163.42亿元、对外许可33.92亿元，"
            r"成熟与其他业务代理约118.95亿元。2026Q1创新药销售45.26亿元、许可收入"
            r"7.87亿元、归母净利22.82亿元。模型不再把全公司统一套创新药倍数，而是"
            r"分别估算创新药、成熟业务与许可价值。"
        ),
        "",
        r"\begin{exhibitbox}[Exhibit 12：恒瑞收入—利润—SOTP桥]",
        r"\begin{tabularx}{\textwidth}{L{1.4cm}R{1.35cm}R{1.35cm}R{1.35cm}R{1.25cm}R{1.25cm}R{1.25cm}X}",
        r"\toprule",
        (
            r"\textbf{情景} & \textbf{创新销售} & \textbf{许可收入} & \textbf{成熟其他} & "
            r"\textbf{总收入} & \textbf{净利润} & \textbf{EPS} & \textbf{SOTP/股} \\"
        ),
        r"\midrule",
    ]
    for name, label in (("bear", "熊"), ("base", "基准"), ("bull", "牛")):
        row = hs[name]
        lines.append(
            f"{label} & {num(row['innovative_sales_100mn'], 1)} & "
            f"{num(row['licensing_revenue_100mn'], 1)} & "
            f"{num(row['mature_and_other_revenue_100mn'], 1)} & "
            f"{num(row['revenue_100mn'], 1)} & {num(row['net_profit_100mn'], 1)} & "
            f"{num(row['eps'])} & {num(row['sotp_per_share'])} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\sourcenote{data/growth\_driver\_model.json与data/hengrui\_sotp\_model\_20260712.json。}",
        r"\end{exhibitbox}",
        "",
        (
            r"华泰2026-03-26原始PDF的未折价SOTP为5918亿元：创新药DCF 5408亿元、"
            r"仿制药及其他192亿元、对外授权317亿元，WACC 7.4\%、永续增长2.5\%，"
            r"对应89.16元。AStock牛市SOTP仍折价至5256亿元／79.19元，华泰89.16元"
            r"只作为独立10\%Street锚，避免在基本面情景与外部锚中重复计价。"
        ),
        "",
        (
            r"现价55.75元若按40倍PE，隐含EPS约1.39元、净利润约92.5亿元，已计入大部分"
            r"基准盈利但未计入完整SOTP。已核验公司Q1证据、华源2026-05-07、西南"
            r"2026-07-01与华泰2026-03-25原始PDF；组合层面已有创新药收入、BD确认、"
            r"NDA／III期进展和分部SOTP闭环。产品级峰值销售、分阶段PoS与未来BD确认日"
            r"属于正式披露边界，因此AStock对创新药DCF折价并对许可收入概率加权，不向"
            r"任何单品补入未经披露的峰值销售。"
        ),
        "",
        r"\section{工业富联：H1预告到H2利润门槛}",
        "",
        (
            r"工业富联H1归母净利中值239亿元、扣非232亿元；Q1归母105.95亿元，隐含Q2"
            r"约133.05亿元。公司披露AI服务器收入同比增长超过230\%、800G以上交换机"
            r"出货增长140\%，构成比泛AI叙事更直接的经营证据。"
        ),
        "",
        r"\begin{exhibitbox}[Exhibit 13：工业富联盈利敏感度]",
        r"\begin{tabularx}{\textwidth}{L{1.4cm}R{1.55cm}R{1.55cm}R{1.25cm}R{1.15cm}R{1.35cm}X}",
        r"\toprule",
        (
            r"\textbf{情景} & \textbf{收入} & \textbf{净利润} & \textbf{EPS} & "
            r"\textbf{PE} & \textbf{价值} & \textbf{验证} \\"
        ),
        r"\midrule",
    ]
    for name, label in (("bear", "熊"), ("base", "基准"), ("bull", "牛")):
        row = fs[name]
        validation = (
            "H2净利321.1亿元"
            if name == "base"
            else ("平台放缓/毛利承压" if name == "bear" else "平台与利润超预期")
        )
        lines.append(
            f"{label} & {num(row['revenue_100mn'], 1)} & {num(row['net_profit_100mn'], 1)} & "
            f"{num(row['eps'])} & {num(row['multiple'], 0)}x & {num(row['value'])} & "
            f"{tex(validation)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{exhibitbox}",
        "",
        (
            r"现价66.27元对应基准EPS约23.5倍PE；若按27倍基准倍数，现价隐含净利润约"
            r"488亿元，低于基准560.1亿元，但安全垫不厚。正式目标74.06元要求H2净利润"
            r"至少321.1亿元、AI服务器增速保持100\%以上、毛利率不低于7\%。已核验官方"
            r"H1预告、金元原始PDF、华泰平台报告和预告后完整研报页：除AI服务器收入"
            r"+230\%、800G出货+140\%外，公司还披露主要客户份额提升、联合研发的下一代"
            r"产品H2量产；CPO样机生产、上万台指引与Rubin爬坡提供代理。客户名称分配、"
            r"单品ASP、精确利用率与AI分部毛利属于正式边界，因此只用合并PE，不给AI"
            r"分部单独高倍数。"
        ),
        "",
        r"\section{四只高增长核心的证据闭环}",
        "",
        (
            r"高增长估值必须同时连接收入代理、毛利、费用、净利润、EPS和当前价格隐含"
            r"门槛。以下四只均已完成来源检查与代理证据闭环；差别不是“有没有证据”，"
            r"而是证据能支持合并估值、分部SOTP，还是只能支持降权后的条件情景。"
        ),
        "",
        r"\fontsize{7.5pt}{10pt}\selectfont",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{L{1.35cm}L{5.10cm}L{4.00cm}X}",
        r"\toprule",
        r"\textbf{公司} & \textbf{直接／代理证据} & \textbf{正式披露边界} & \textbf{估值后果} \\",
        r"\midrule",
        (
            r"恒瑞医药 & 创新药收入、BD确认、NDA／III期进展、12笔BD与组合SOTP & "
            r"单品峰值、阶段PoS、未来BD确认日 & 创新药DCF折价，许可收入概率加权 \\"
        ),
        (
            r"工业富联 & AI服务器+230\%、800G+140\%、大客户联合研发、CPO／Rubin代理 & "
            r"客户分配、单品ASP、利用率、AI分部毛利 & 只用合并PE，不给AI分部额外倍数 \\"
        ),
        (
            f"中兴通讯 & 算力收入+150\\%、占比24.6\\%，服务器存储+200\\%、"
            r"Q1占比27\%；头部互联网、运营商、政务金融客户类别；国金2026E收入"
            r"1728.08亿元、净利73.73亿元、EPS 1.541元 & "
            r"具名客户、设备量、合同ASP、算力分部毛利 & 仅合并PE；概率值低于现价，条件观察 \\"
        ),
        (
            r"江波龙 & LTA／MOU、自研SPU／HLC、自有封测、AMD联合调优；"
            r"NAND／DRAM价格、平台认证、企业级存储及客户行业代理 & "
            r"合同价、库存成本层、H2具名客户订单额 & 11x／14x／17x周期PE与35\%熊市概率 \\"
        ),
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{data/growth\_driver\_model.json；每行均保存检查来源、正式边界和估值后果。}",
    ]
    return "\n".join(lines)


def conditional_section(conditional_rows: list[dict[str, Any]]) -> str:
    row_map = {row["ticker"]: row for row in conditional_rows}
    zte = row_map["000063"]
    jiang = row_map["301308"]
    shaanxi = row_map["601225"]
    return "\n".join(
        [
            r"\section{中兴通讯：经营证据已闭环，但赔率未过关}",
            "",
            (
                f"现价{num(zte['current_price'])}元，熊／基准／牛情景为"
                f"{num(zte['bear'])}/{num(zte['base'])}/{num(zte['bull'])}元，"
                f"35\\%／45\\%／20\\%概率值{num(zte['probability_expected_value'])}元，"
                f"相对现价{pct(zte['expected_upside'] * 100, 1, True)}。"
                r"2025年算力相关收入同比约+150\%、占营收24.6\%，服务器及存储收入"
                r"+200\%以上、数据中心产品+50\%；2026Q1算力占比升至27\%。国金原始"
                r"PDF明确把头部互联网、运营商、政务与金融智算项目列为需求来源，并给出"
                r"2026E收入1728.08亿元、净利73.73亿元、EPS 1.541元、经营现金流／股"
                r"1.80元与毛利率31.3\%。具名终端客户、设备量、合同ASP和算力分部毛利"
                r"在已检查季报及两份原始PDF中没有单独披露，所以不使用算力分部高倍数；"
                r"旧48.75元目标撤销，当前只用合并EPS情景，且概率值低于现价。"
            ),
            "",
            r"\section{江波龙：上半年兑现不等于周期永久化}",
            "",
            (
                r"江波龙H1归母净利中值101亿元、扣非97.5亿元，Q1归母38.62亿元，隐含Q2"
                r"62.38亿元，主营兑现强；但Q1经营现金流为-28.75亿元，一年位置约79\%，"
                r"当前587.60元已包含相当多周期持续性假设。"
            ),
            "",
            r"\begin{exhibitbox}[Exhibit 14：江波龙周期敏感度]",
            r"\begin{tabularx}{\textwidth}{L{1.6cm}R{1.5cm}R{1.4cm}R{1.3cm}R{1.4cm}X}",
            r"\toprule",
            r"\textbf{情景} & \textbf{全年净利} & \textbf{EPS} & \textbf{PE} & \textbf{价值} & \textbf{含义} \\",
            r"\midrule",
            r"熊 & 131亿元 & 约31元 & 11x & 341元 & 库存红利消退、价格回落 \\",
            r"基准 & 161亿元 & 约38元 & 14x & 532元 & H2仍盈利但不继续加速 \\",
            r"牛 & 191亿元 & 约45元 & 17x & 765元 & 合同价、供给与订单延续 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            (
                f"概率值{num(jiang['probability_expected_value'])}元，相对现价"
                f"{pct(jiang['expected_upside'] * 100, 1, True)}；旧802.30元目标撤销。"
                r"官方预告明确披露与多家全球存储晶圆原厂续签LTA／MOU、自研SPU／HLC、"
                r"自有高端封测以及与AMD联合调优，后者令端侧AI产品DRAM使用量下降约40\%。"
                r"国信与爱建原始PDF补充企业级存储+93.3\%、平台认证、通信／金融／互联网"
                r"客户链和NAND／DRAM价格指数。合同价、库存成本层和H2具名订单额属于正式"
                r"披露边界，因此模型使用11x／14x／17x周期PE并保留35\%熊市概率；升级要求"
                r"H2扣非、现金流和存货减值共同验证，而不是等待一个可能永不公开的客户名称。"
            ),
            "",
            r"\section{陕西煤业：行业静默成立，个股赔率未过关}",
            "",
            (
                f"陕西煤业H1归母／扣非净利中值114.58／97.46亿元，行业阶段为静默吸纳，"
                f"但现价{num(shaanxi['current_price'])}元高于概率值"
                f"{num(shaanxi['probability_expected_value'])}元。熊／基准／牛为"
                f"{num(shaanxi['bear'])}/{num(shaanxi['base'])}/{num(shaanxi['bull'])}元。"
                r"股息提供下行支撑，但只有煤价、2026E EPS和分红持续性同时高于当前券商"
                r"基准，才可从行业验证升级为正式配置。"
            ),
            "",
            r"\begin{riskbox}[降级原则]",
            (
                r"条件观察并非“没有证据”：中兴和江波龙都已完成直接披露、代理证据和"
                r"正式边界记录。但只要概率值低于现价，或现金流／库存／利润门槛尚未"
                r"兑现，就不能用牛市目标替代正式目标。"
            ),
            r"\end{riskbox}",
        ]
    )


def risk_section(
    valuation_rows: list[dict[str, Any]],
    priority_rows: list[dict[str, Any]],
) -> str:
    return "\n".join(
        [
            r"\section{组合与执行纪律}",
            "",
            r"\begin{exhibitbox}[Exhibit 15：行为框架]",
            r"\begin{tabularx}{\textwidth}{L{2.4cm}L{3.3cm}L{3.2cm}X}",
            r"\toprule",
            r"\textbf{类别} & \textbf{进入条件} & \textbf{加仓／升级} & \textbf{退出／降级} \\",
            r"\midrule",
            (
                r"正式核心 & 概率目标高于现价且模型可复算 & "
                r"下季门槛兑现、回撤承接稳定 & 触发失效条件或概率价值跌破现价 \\"
            ),
            (
                r"低位盈利 & 一年位置低、扣非为正、增长为正 & "
                r"资金由单日变连续、现金流与新研报确认 & Q2恶化、一次性上升、资金继续缺席 \\"
            ),
            (
                r"已启动候选 & 价格启动、行业阶段确认、盈利桥有效 & "
                r"H2利润、现金流、订单继续兑现 & 追高后估值超阈值或旧分母失效 \\"
            ),
            (
                r"条件观察 & 产业方向对但证据或赔率不足 & "
                r"补齐ASP／客户／分部毛利／现金流 & 只剩主题热度、牛市情景成为唯一依据 \\"
            ),
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            r"\section{关键风险}",
            "",
            r"\begin{itemize}",
            r"  \item \textbf{预告风险}：业绩预告未经审计，H1不能机械年化；正式中报可能改变扣非、现金流与分部口径。",
            r"  \item \textbf{周期风险}：有色、石化、存储和煤炭的高利润可能来自价格、库存或价差，倍数会随周期迅速压缩。",
            r"  \item \textbf{资金口径风险}：公开“主力资金”无法穿透最终受益人，静默标签只是价格—资金结构描述。",
            r"  \item \textbf{Street时效风险}：徐工、沪农商行和工业富联的正权重原始目标存在时效折价；最新转载页只作零权重核对。",
            r"  \item \textbf{高增长边界风险}：恒瑞单品PoS、工业富联客户分配、江波龙合同价、中兴分部毛利属于已检查后的正式披露边界；模型分别以SOTP折价、合并PE、周期PE和条件观察处理。",
            r"  \item \textbf{数据传输风险}：申万分类文件下载使用证书校验降级；浙江东方研报接口失败后已回退至官方预告、Q1财务和公开检索，Street权重为0。",
            r"\end{itemize}",
            "",
            r"\section{监控触发器}",
            "",
            r"\begin{exhibitbox}[Exhibit 16：未来一个季度监控]",
            r"\begin{tabularx}{\textwidth}{L{2.1cm}L{3.5cm}L{3.4cm}X}",
            r"\toprule",
            r"\textbf{对象} & \textbf{升级触发} & \textbf{降级触发} & \textbf{对应动作} \\",
            r"\midrule",
            r"低位有色／石化 & 现金流转正、价格与资金同步 & 价差回落、库存或现金流恶化 & 从观察升级为分批配置，或退出 \\",
            r"非银金融 & 新研报分母、成交与资金持续确认 & 只有低位、没有业务或资金验证 & 保持小权重观察 \\",
            r"恒瑞医药 & 创新药增长30\%+、里程碑按期 & 增长低于20\%、EPS低于1.25元 & 回撤核心或下修SOTP \\",
            r"工业富联 & H2净利321.1亿元+、毛利率7\%+ & 平台延迟、净利低于516亿元 & 回撤观察或降级 \\",
            r"江波龙 & H2现金流转正、合同价与订单延续 & 库存减值、价格回落、现金流继续负 & 重新评估周期情景 \\",
            r"中兴通讯 & H2利润正增、算力分部证据出现 & 现金流和利润继续弱 & 维持条件观察 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            r"\section{最终配置判断}",
            "",
            (
                r"当前最值得进入正式决策的是恒瑞医药；渝农商行与徐工机械适合在回撤中"
                r"复核，工业富联适合等H2兑现，沪农商行偏收益型。全市场低位优先池中，"
                r"宏桥控股、天山铝业、恒力石化、中孚实业和中矿资源具有明显位置与盈利"
                r"弹性，但仍需用现金流和行业资金确认。右侧候选中巨人网络质量最好，"
                r"恒逸石化、东方盛虹与高德红外分别受现金流、估值或旧分母约束。"
            ),
            "",
            (
                r"这不是“所有高增长都买”，而是把全市场机会拆成：正式估值通过、低位盈利"
                r"待资金确认、已启动待H2兑现、证据已闭环但赔率／现金流未过关四种行为。"
            ),
        ]
    )


def theme_appendix(
    company_rows: list[dict[str, Any]],
    broker_catalog: dict[str, Any],
    report_wide_rows: list[dict[str, Any]],
    evidence_closure_rows: list[dict[str, Any]],
) -> str:
    valuation_map = {row["ticker"]: row for row in report_wide_rows}
    lines = [
        r"\section{旧54只主题池的正确定位}",
        "",
        (
            r"旧主题池覆盖银行、工程机械、AI网络与算力设备、AI存储、创新药、军工与"
            r"商业航天、先进封装、传媒与AI应用、业绩预告雷达九组，共54只。其研报"
            r"元数据与28只优先主题标的的56份原始PDF仍有研究价值，但本报告不再把它"
            r"称为全市场母池。"
        ),
        "",
        r"\scriptsize",
        r"\begin{longtable}{L{1.05cm}L{1.55cm}L{1.75cm}R{0.90cm}R{1.05cm}R{0.90cm}L{1.75cm}L{2.45cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{主题} & \textbf{现价} & "
            r"\textbf{概率目标} & \textbf{空间} & \textbf{模型层级} & \textbf{动作} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{主题} & \textbf{现价} & "
            r"\textbf{概率目标} & \textbf{空间} & \textbf{模型层级} & \textbf{动作} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    for row in company_rows:
        valuation = valuation_map[row["ticker"]]
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['sector'])} & "
            f"{num(valuation.get('current_price'))} & "
            f"{num(valuation.get('probability_target'))} & "
            f"{pct(valuation['upside'] * 100, 0, True) if valuation.get('upside') is not None else '---'} & "
            f"{tex(MODEL_TIER_LABELS.get(valuation['model_tier'], valuation['model_tier']))} & "
            f"{tex(EXPANDED_ACTION_LABELS.get(valuation['action'], valuation['action']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        (
            f"研报目录记录54只元数据、{broker_catalog['priority_count']}只主题优先标的和"
            f"{sum(row['status'] == 'downloaded' for row in broker_catalog['download_rows'])}份"
            r"原始PDF。54只主题标的全部进入117只去重估值总账。常熟银行已由东海证券"
            r"2026-04-28原始PDF的2026E EPS 1.40元和Q1 BPS 9.66元建立PB-ROE区间；"
            r"深科技使用国泰海通完整转载正文的2026E EPS 0.89元，但因不是原始PDF，"
            r"Street目标权重为0；汤姆猫只用官方Q1 EPS、扣非与现金流做低置信筛选；"
            r"长鑫科技截至数据截点仍处IPO初询价，不伪造二级市场目标。"
        ),
        "",
        r"\section{117只逐票证据闭环总账}",
        "",
        (
            r"下表逐票给出直接证据、检查来源、代理、"
            r"正式边界与估值后果。114只直接关闭、2只以估值降权关闭、1只为IPO正式"
            r"时间边界；开放实质缺口为0。"
        ),
        "",
        r"\scriptsize",
        r"\begin{longtable}{L{1.00cm}L{1.40cm}L{1.45cm}L{2.85cm}L{2.50cm}L{3.05cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{闭环} & \textbf{直接／代理证据} & "
            r"\textbf{正式边界} & \textbf{估值后果} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{闭环} & \textbf{直接／代理证据} & "
            r"\textbf{正式边界} & \textbf{估值后果} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    closure_labels = {
        "closed": "已关闭",
        "closed_with_valuation_downgrade": "降权关闭",
        "formal_timing_boundary": "时间边界",
    }
    for row in evidence_closure_rows:
        checked_count = len(row.get("source_paths", []))
        evidence_text = (
            f"{row['direct_evidence']}；{row.get('proxy_evidence') or '无需额外代理'}；"
            f"归档路径{checked_count}个"
        )
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(closure_labels.get(row['closure_status'], row['closure_status']))} & "
            f"{tex(evidence_text)} & {tex(row.get('formal_boundary') or '无重大未决边界')} & "
            f"{tex(row.get('valuation_consequence') or '按已披露分母生成筛选区间')} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        r"\sourcenote{data/report\_wide\_evidence\_closure\_20260713.json；完整117行亦保存在结构化工件中。}",
    ]
    return "\n".join(lines)


def source_appendix(evidence_closure: dict[str, Any]) -> str:
    return "\n".join(
        [
            r"\section{关键工件索引}",
            "",
            r"\begin{itemize}",
            r"  \item 全市场预告：\texttt{data/full\_market\_preview\_screen\_20260712.json}",
            r"  \item 73只候选：\texttt{data/full\_market\_preview\_candidates\_20260712.json}",
            r"  \item 16只优先池：\texttt{data/full\_market\_priority\_evidence\_20260712.json}",
            r"  \item 16只完整估值：\texttt{data/full\_market\_priority\_valuation\_20260712.json}",
            r"  \item 73只候选估值：\texttt{data/full\_market\_candidate\_valuation\_20260712.json}",
            r"  \item 117只去重总账：\texttt{data/report\_wide\_valuation\_ledger\_20260712.json}",
            r"  \item 117只证据闭环：\texttt{data/report\_wide\_evidence\_closure\_20260713.json}",
            r"  \item 44只主题独有证据：\texttt{data/theme\_only\_evidence\_20260713.json}",
            r"  \item 全候选估值证据：\texttt{data/full\_market\_valuation\_evidence\_20260712.json}",
            r"  \item 公告EPS／扣非质量：\texttt{data/earnings\_preview\_quality\_20260711.json}",
            r"  \item 7月15日预告增量：\texttt{data/earnings\_preview\_update\_20260715.json}",
            r"  \item 7月15日公告原件：\texttt{sources/earnings-previews-20260715/}",
            r"  \item 五只正式估值：\texttt{data/current\_valuation\_model\_20260711.json}",
            r"  \item Street锚：\texttt{data/broker\_street\_consensus\_20260711.json}",
            r"  \item 恒瑞SOTP：\texttt{data/hengrui\_sotp\_model\_20260712.json}",
            r"  \item 条件观察：\texttt{data/conditional\_watch\_models\_20260712.json}",
            r"  \item 高增长桥：\texttt{data/growth\_driver\_model.json}",
            r"  \item 旧主题池：\texttt{data/company\_cards\_20260711.json}",
            r"  \item 旧主题研报目录：\texttt{data/core\_broker\_report\_catalog\_20260711.json}",
            r"\end{itemize}",
            "",
            r"\section{来源层级}",
            "",
            r"\begin{exhibitbox}[Exhibit A1：来源与用途]",
            r"\begin{tabularx}{\textwidth}{L{2.1cm}L{2.4cm}L{3.4cm}X}",
            r"\toprule",
            r"\textbf{来源} & \textbf{质量} & \textbf{用途} & \textbf{边界} \\",
            r"\midrule",
            r"公司公告／财报 & L1 & H1预告、Q1财务、扣非与EPS & 预告未经审计，不机械年化 \\",
            r"申万官方分类 & L1传输降级 & 364家A股公司映射31行业 & HTTPS证书校验失败，文件已归档校验 \\",
            r"交易行情与历史K线 & L1--L2 & 现价、20/60日、一年位置 & 不证明机构身份或未来趋势 \\",
            r"原始券商PDF & L2 & 盈利分母、目标、方法、风险 & 需要时效折价，不能替代AStock判断 \\",
            r"详细转载页 & L3 & 最新目标方向与预测交叉验证 & 目标权重为0，不冒充原始报告 \\",
            r"结构化资金表 & L2 & 行业与个股资金阶段 & 按成交单分类，无法穿透受益人 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{exhibitbox}",
            "",
            r"\section{模型复现声明}",
            "",
            (
                r"五只正式模型的现价、股本、市值、2026E收入／净利／EPS、三情景、概率、"
                r"Street权重、最终目标和空间均可由结构化JSON复算。所有熊市值低于现价，"
                r"概率和为100\%，市场锚权重为0，同票同源原始PDF覆盖5/5。"
                r"\textbf{Model Reproducibility: PASS}。"
            ),
            (
                r"估值覆盖层另包含16只优先股公司级模型、73只H1候选估值行和117只报告全标的"
                r"去重总账。73只候选中72只可定价、1只因无有效二级市场价格不可定价；"
                r"117只总账中116只可定价、1只为IPO定价时间边界。"
                r"\textbf{Full-Market Valuation Coverage Reproducibility: PASS}。"
            ),
            "",
            r"\section{证据闭环与正式边界}",
            "",
            (
                f"117只证据闭环总账中，{evidence_closure['closed_count']}只直接关闭、"
                f"{evidence_closure['downgraded_count']}只通过估值降权关闭、"
                f"{evidence_closure['formal_boundary_count']}只为正式时间边界，"
                f"开放实质缺口{evidence_closure['unresolved_material_gap_count']}只。"
                r"正式边界不是空白：每项均列明检查来源、代理证据及估值后果。"
            ),
            r"\begin{itemize}",
            r"  \item 浙江东方：已检查研报接口、官方H1预告、Q1财务与公开检索；当前原始券商PDF未取得，Street权重为0，House PB-ROE／盈利桥仍可复算。",
            r"  \item 恒瑞／工业富联：组合或合并盈利证据完整；产品PoS、客户分配等边界分别通过SOTP折价或只用合并PE处理。",
            r"  \item 中兴／江波龙：直接披露和代理证据已闭环，但概率值低于现价；分别只用合并PE或周期PE，维持条件观察。",
            r"  \item 长鑫科技：官方IPO公告显示2026-07-15才刊登发行公告；数据截点没有发行价和二级历史，因此不给二级目标。",
            r"  \item 资金表不能穿透到具体机构、量化策略或最终受益人。",
            r"\end{itemize}",
        ]
    )


def preview_update_section(update: dict[str, Any]) -> str:
    rows = update["rows"]
    lines = [
        r"\section{截至2026年7月15日的半年报预告增量}",
        "",
        (
            r"本节是对7月11日基线的增量更新，不重写原有364家A股预告母池和117只估值总账。"
            f"通过东方财富官方公告接口及公司公告附件，新增归档{len(rows)}只原此前未命中的"
            r"主题池公司；每只均完成代码、公司名、标题、金额字段和PDF文本校验。"
            r"由于AkShare的同类端点本轮返回异常结构，采集切换至官方公告接口，"
            r"该降级路径已写入结构化数据包。"
        ),
        "",
        r"\noindent",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.00cm}L{1.25cm}L{0.95cm}R{0.75cm}R{0.75cm}R{0.70cm}R{0.75cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{公告日} & \textbf{归母中值} & \textbf{扣非中值} & \textbf{H1 EPS} & \textbf{隐含Q2} & \textbf{处置} \\",
        r"\midrule",
    ]
    disposition_labels = {
        "earnings_validation_watch": "验证观察",
        "exclude_nonrecurring_dominated": "一次性排除",
        "broker_supported_no_preview": "研报待验证",
        "earnings_delivered_price_advanced": "兑现待回撤",
        "price_advanced_wait_earnings": "价格先行",
        "earnings_decline_watch": "预减观察",
    }
    for row in rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['announcement_date'])} & "
            f"{num(row['h1_parent_np_midpoint_100mn'], 1)} & "
            f"{num(row['h1_deducted_np_midpoint_100mn'], 1)} & "
            f"{num(row.get('h1_eps_midpoint'), 2)} & "
            f"{num(row.get('q2_implied_net_profit_100mn'), 1)} & "
            f"{tex(disposition_labels.get(row['disposition'], row['disposition']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        "",
        (
            r"\textit{注：}归母和扣非净利润单位为人民币亿元；隐含Q2为H1归母净利中值减"
            r"2026Q1归母净利，不是公司正式季度指引。预告未经审计，不能机械年化；"
            r"H1 EPS优先使用公司公告，未披露者由H1归母中值除以Q1股本推算。"
        ),
        "",
        r"\subsection{本轮最重要的估值含义}",
        "",
        (
            r"\textbf{北京君正、德明利}补齐了存储观察池的预告缺口。北京君正H1归母中值"
            r"约11.8亿元、扣非中值约11.5亿元，隐含Q2约8.6亿元，主营改善较清晰，但"
            r"现价仍处高位，先做业绩验证；德明利H1归母中值约61.0亿元、扣非约60.5亿元，"
            r"H1 EPS约27.13元，业绩已经兑现但价格先行，不能沿用预告前的旧分母直接追价。"
        ),
        (
            r"\textbf{长电科技}是本轮先进封装中最干净的增量：归母与扣非中值分别约8.6和"
            r"8.25亿元，非经常性占比约4.1\%，公司明确提到AI基础设施需求、订单和产能利用率。"
            r"但一年位置和前期涨幅已经较高，结论是等待中报毛利率、资本开支回报和现金流，"
            r"而不是把预告直接转化为新目标价。"
        ),
        (
            r"\textbf{华天科技、通富微电}的归母利润不能直接当作主营分母。华天科技H1归母"
            r"中值约8.0亿元、扣非约2.4亿元，非经常性占比约70\%；通富微电归母约17.0亿元、"
            r"扣非约7.5亿元，非经常性占比约55.9\%。两者保留为产业趋势观察，正式估值必须"
            r"等待中报解释公允价值、投资收益、毛利率和现金流。"
        ),
        (
            r"\textbf{中航沈飞}的新增预告改变了原先“等待订单修复”的风险等级：H1归母约"
            r"4.75亿元，同比预减约58.2\%，扣非约4.04亿元，同比预减约62.4\%。交付节奏和"
            r"新型装备生产组织仍是约束，原先正向EPS分母不得继续作为升级依据。"
            r"\textbf{航发动力}虽预增，但归母中值仅约1.48亿元、扣非约2.03亿元，绝对利润"
            r"基数仍低，预告只支持订单交付验证，不支持估值重估。"
        ),
        (
            r"\textbf{恺英网络、中国卫星}分别属于游戏经营改善和卫星型号验收进度改善。"
            r"前者扣非中值约11.7亿元，仍有传奇IP和新品贡献，但非经常性占比约18.2\%；"
            r"后者由亏转盈，扣非中值仅约0.29亿元，须观察H2合同履约和利润确认。两者均"
            r"更新为“预告后验证”，不自动升级为正式核心。"
        ),
        "",
        r"\begin{riskbox}[增量数据边界]",
        (
            r"本轮只补齐已被官方公告确认的9只标的；“未在新增清单”不代表公司没有预告。"
            r"主报告的全市场母池仍以7月11日结构化普查为基线，后续若要把所有364家公司"
            r"完全滚动到7月15日，需要重新抓取全量公告并重建行业/候选/估值矩阵。"
        ),
        r"\end{riskbox}",
        r"\sourcenote{data/earnings\_preview\_update\_20260715.json；sources/earnings-previews-20260715/。}",
    ]
    return "\n".join(lines)


def main_tex() -> str:
    return r"""% !TEX program = xelatex
\documentclass[a4paper,11pt,openany,fontset=none]{ctexrep}

\newcommand{\reporttitle}{A股全市场双机会曲线研究}
\newcommand{\reportsubtitle}{31行业、364家A股公司基线预告、7月15日增量与117只估值总账}
\newcommand{\reportkicker}{ASTOCK FULL-MARKET STRATEGY}
\newcommand{\reportscope}{中国A股 | 31行业 | 73只H1候选 | 16只完整模型 | 117只估值总账}
\newcommand{\reportdate}{2026年7月15日}
\newcommand{\reportdatacutoff}{行情基线截至2026年7月10日；全市场预告基线截至7月11日；增量预告截至7月15日}
\newcommand{\reporttype}{全市场板块轮动与核心标的研究}
\newcommand{\reportauthor}{AStock研究代理}
\newcommand{\reporthouseview}{全市场机会必须拆成两条曲线：左侧寻找位置低、盈利改善但尚未获得持续资金确认的公司；右侧寻找价格已经启动、但H2利润和现金流仍能覆盖现价的公司。7月15日增量预告显示，长电科技和德明利业绩兑现但价格先行，华天科技、通富微电受非经常性收益干扰，中航沈飞预减，预告数据强化了分层而不是统一追涨。}
\newcommand{\reportquality}{全市场基线原始预告表949条，排除4只B股的12条指标后保留937条合格A股输入；母池覆盖364家公司并映射31个申万一级行业。另归档9只截至7月15日新增官方半年报预告，均完成PDF字段校验；原117只估值总账保留为7月11日基线，新增预告不自动生成目标价。}
\newcommand{\reportdisclaimer}{本报告基于公开资料整理，不构成任何证券买卖建议。}

\input{../../../.agents/templates/preamble.tex}

\hypersetup{
  pdfauthor={\reportauthor},
  pdftitle={\reporttitle}
}

\begin{document}

\astockcover

\tableofcontents
\clearpage

\chapter{决策摘要：全市场双机会曲线}
\input{sections/final_ch01_dashboard}

\chapter{方法、母池与证据边界}
\input{sections/final_ch02_methodology}

\chapter{申万31行业全景}
\input{sections/final_ch03_industries}

\chapter{73只高影响候选全量审计}
\input{sections/final_ch04_candidates}

\chapter{16只优先证据池逐股研究}
\input{sections/final_ch05_priority}

\chapter{五只正式估值与Street穿透}
\input{sections/final_ch06_valuation}

\chapter{四只高增长核心的盈利桥与证据边界}
\input{sections/final_ch07_growth}

\chapter{中兴、江波龙与陕西煤业条件观察}
\input{sections/final_ch08_conditional}

\chapter{风险、组合与监控纪律}
\input{sections/final_ch09_risk}

\chapter{7月15日半年报预告增量更新}
\input{sections/final_ch10_preview_update}

\appendix
\chapter{54只主题深挖池与56份研报归档}
\input{sections/final_app_theme}

\chapter{来源、模型与审计索引}
\input{sections/final_app_sources}

\clearpage
\thispagestyle{empty}
\vspace*{4cm}
\begin{disclosurebox}[免责声明]
\small
本报告中的“主力资金”沿用公开数据源按成交单大小分类的统计口径，不代表对资金最终受益人、机构身份或一致行动关系的确认。“静默吸纳”“启动确认”等标签仅用于研究价格与资金结构。所有目标价均为概率情景研究框架，不构成收益承诺或证券买卖建议。
\end{disclosurebox}

\end{document}
"""


def main() -> None:
    SECTIONS_DIR.mkdir(exist_ok=True)
    preview_screen = load_json(DATA_DIR / "full_market_preview_screen_20260712.json")
    candidates = load_json(DATA_DIR / "full_market_preview_candidates_20260712.json")
    priority_evidence = load_json(DATA_DIR / "full_market_priority_evidence_20260712.json")
    valuations = load_json(DATA_DIR / "current_valuation_model_20260711.json")["rows"]
    brokers = load_json(DATA_DIR / "broker_street_consensus_20260711.json")["rows"]
    preview_update = load_json(DATA_DIR / "earnings_preview_update_20260715.json")
    conditionals = load_json(DATA_DIR / "conditional_watch_models_20260712.json")["rows"]
    growth = load_json(DATA_DIR / "growth_driver_model.json")["drivers"]
    sotp = load_json(DATA_DIR / "hengrui_sotp_model_20260712.json")
    priority_valuations = load_json(
        DATA_DIR / "full_market_priority_valuation_20260712.json"
    )["rows"]
    candidate_valuation = load_json(
        DATA_DIR / "full_market_candidate_valuation_20260712.json"
    )
    report_wide_ledger = load_json(
        DATA_DIR / "report_wide_valuation_ledger_20260712.json"
    )
    evidence_closure = load_json(
        DATA_DIR / "report_wide_evidence_closure_20260713.json"
    )
    company_cards = load_json(DATA_DIR / "company_cards_20260711.json")["rows"]
    broker_catalog = load_json(DATA_DIR / "core_broker_report_catalog_20260711.json")

    write_text(
        SECTIONS_DIR / "final_ch01_dashboard.tex",
        dashboard_section(
            valuations,
            conditionals,
            priority_evidence["rows"],
            priority_valuations,
            candidate_valuation,
            report_wide_ledger,
            evidence_closure,
            preview_screen,
        ),
    )
    write_text(
        SECTIONS_DIR / "final_ch02_methodology.tex",
        methodology_section(preview_screen, candidates, priority_evidence),
    )
    write_text(
        SECTIONS_DIR / "final_ch03_industries.tex",
        industry_section(preview_screen["industry_summary"]),
    )
    write_text(
        SECTIONS_DIR / "final_ch04_candidates.tex",
        candidate_section(
            candidates["rows"],
            candidate_valuation["rows"],
            preview_screen,
        ),
    )
    write_text(
        SECTIONS_DIR / "final_ch05_priority.tex",
        priority_section(priority_evidence["rows"], priority_valuations),
    )
    write_text(
        SECTIONS_DIR / "final_ch06_valuation.tex",
        valuation_section(valuations, brokers),
    )
    write_text(
        SECTIONS_DIR / "final_ch07_growth.tex",
        growth_section(growth, sotp),
    )
    write_text(
        SECTIONS_DIR / "final_ch08_conditional.tex",
        conditional_section(conditionals),
    )
    write_text(
        SECTIONS_DIR / "final_ch09_risk.tex",
        risk_section(valuations, priority_evidence["rows"]),
    )
    write_text(
        SECTIONS_DIR / "final_ch10_preview_update.tex",
        preview_update_section(preview_update),
    )
    write_text(
        SECTIONS_DIR / "final_app_theme.tex",
        theme_appendix(
            company_cards,
            broker_catalog,
            report_wide_ledger["rows"],
            evidence_closure["rows"],
        ),
    )
    write_text(
        SECTIONS_DIR / "final_app_sources.tex",
        source_appendix(evidence_closure),
    )
    write_text(CASE_DIR / "main.tex", main_tex())
    print(
        json.dumps(
            {
                "industry_rows": len(preview_screen["industry_summary"]),
                "preview_companies": preview_screen["preview_company_count"],
                "candidate_rows": candidates["row_count"],
                "priority_rows": priority_evidence["row_count"],
                "valuation_rows": len(valuations),
                "conditional_rows": len(conditionals),
                "theme_rows": len(company_cards),
                "priority_valuation_rows": len(priority_valuations),
                "candidate_valuation_rows": candidate_valuation["row_count"],
                "report_wide_valuation_rows": report_wide_ledger["row_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
