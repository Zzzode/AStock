#!/usr/bin/env python3
"""Build reader-facing LaTeX sections for the expanded 54-name research report."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SECTIONS_DIR = CASE_DIR / "sections"


SECTOR_ORDER = [
    "银行",
    "工程机械",
    "AI网络与算力设备",
    "AI存储",
    "创新药",
    "国防军工与商业航天",
    "先进封装",
    "传媒与AI应用",
    "业绩预告新雷达",
]

SECTOR_VIEWS = {
    "银行": (
        "银行是当前唯一同时通过低位置、周度资金净流入和可复算估值的一级行业。"
        "渝农商行与沪农商行进入正式估值池；宁波银行、南京银行、常熟银行和建设银行"
        "用于比较成长、股息、区域信用与大行防御属性。银行没有H1预告并非信息缺失，"
        "而是披露制度差异；核心门槛仍是净息差、不良率、拨备和分红。"
    ),
    "工程机械": (
        "工程机械并未通过行业周度净流入门槛，但徐工机械出现连续资金吸纳、低价格位置"
        "和经营现金流改善，因此是个股岛而非行业普涨。三一重工与中联重科代表主机厂"
        "周期，恒立液压和浙江鼎力代表零部件及高端装备，估值必须分别验证海外、矿机、"
        "液压件和高空作业平台的订单与现金转化。"
    ),
    "AI网络与算力设备": (
        "该板块是本轮预告密度最高的方向，7只中6只披露H1预告。工业富联已具备预告后"
        "盈利预测与公开目标价，升级为正式核心；浪潮信息和锐捷网络已有预告后研报，"
        "但价格已接近或达到外部目标；紫光股份、智微智能和星网锐捷必须扣除结构性或"
        "一次性因素。中兴通讯未披露预告，但算力收入占比和公司级估值桥已完整。"
    ),
    "AI存储": (
        "AI存储同时具备最强盈利弹性和最高周期风险。江波龙用官方H1预告重建全年模型；"
        "香农芯创H1预告EPS已是旧全年EPS的3.4倍，兆易创新H1预告EPS也超过旧全年EPS，"
        "说明旧券商分母失效。德明利、北京君正和佰维存储价格位置均偏高，需等待实际"
        "库存成本、合同价、现金流和减值风险验证。"
    ),
    "创新药": (
        "创新药核心不是是否有AI或政策主题，而是产品销售、BD里程碑、临床概率和费用率"
        "能否进入公司EPS。恒瑞医药用SOTP进入正式核心；百济神州、甘李药业、科伦药业、"
        "贝达药业和神州细胞分别承担全球化、胰岛素、创新药平台、肿瘤管线和生物药弹性，"
        "但本轮未捕获H1预告，继续等待中报和管线事件。"
    ),
    "国防军工与商业航天": (
        "军工板块已经启动，但公司利润修复并不均匀。中船防务的造船订单与效率改善得到"
        "预告验证，但联营和分红收益也有贡献；星网宇达扣非仍亏、约1.4亿元投资收益主导"
        "扭亏，明确排除。中航光电、中航沈飞、航发动力、中国卫星和紫光国微仍需订单、"
        "交付和现金流共同确认。"
    ),
    "先进封装": (
        "先进封装产业趋势明确，但本轮6只均未捕获H1预告，且华天科技、长电科技、通富"
        "微电、甬矽电子和芯碁微装多处于一年高位。原始研报支持资本开支、2.5D/3D和大"
        "客户成长叙事，但没有新预告分母时，不把产业空间直接转换成当前价格目标。"
    ),
    "传媒与AI应用": (
        "传媒与AI应用的分化在盈利模型而非主题标签。恺英网络、三七互娱有成熟游戏现金流"
        "和新品周期；芒果超媒、浙数文化有内容与数据资产；昆仑万维和汤姆猫的AI期权更"
        "高但盈利可见度较弱。本轮6只均未捕获H1预告，因此仅保留券商支持的观察池。"
    ),
    "业绩预告新雷达": (
        "该组5只全部披露H1预告，用于捕捉原板块之外的新盈利拐点。方正科技主营PCB兑现"
        "最干净但旧EPS已失效；风华高科和翔鹭钨业属于量价周期；多氟多Q2隐含利润较Q1"
        "下降；亿道信息一次性投资收益占比较高。全部先进入重估或周期观察，不因高同比"
        "自动给目标价。"
    ),
}

DISPOSITION_LABELS = {
    "current_price_core_model": "正式核心模型",
    "post_preview_model_refresh": "预告后重估池",
    "earnings_delivered_wait_pullback": "业绩兑现、等待回撤",
    "price_above_broker_anchor": "价格高于旧外部锚",
    "oneoff_discount_watch": "扣除一次性后观察",
    "exclude_nonrecurring_dominated": "非经常主导、排除",
    "cycle_watch_price_demanding": "周期兑现但价格要求高",
    "cycle_watch_q2_deceleration": "周期观察、Q2减速",
    "cycle_watch_working_capital": "周期观察、现金流门槛",
    "price_advanced_wait_earnings": "价格先行、等待业绩",
    "broker_supported_no_preview": "券商支持、等待中报",
    "no_preview_fundamental_watch": "基本面观察、等待中报",
    "no_preview_cycle_watch": "周期观察、等待中报",
    "no_preview_compute_watch": "算力观察、等待中报",
    "no_preview_storage_watch": "存储观察、等待中报",
    "no_preview_pipeline_watch": "管线观察、等待中报",
    "no_preview_order_watch": "订单观察、等待中报",
    "preview_radar_watch": "预告雷达观察",
}

QUALITY_LABELS = {
    "core_operating_delivery": "主营真兑现",
    "core_operating_cycle_and_mix": "周期/结构真兑现",
    "core_operating_cycle_and_price": "周期/价格兑现",
    "core_operating_plus_investment_income": "主营改善+投资收益",
    "operating_plus_structural_and_oneoff": "主营+结构变化+一次性",
    "operating_plus_fair_value": "主营+公允价值收益",
    "operating_plus_oneoff": "主营+一次性",
    "nonrecurring_dominated": "非经常损益主导",
    "not applicable": "未披露预告",
}

RELATION_LABELS = {
    "post_preview": "预告后",
    "same_day_as_preview": "预告同日",
    "pre_preview_forecast_may_be_stale": "预告前，分母可能失效",
    "no_preview_date": "无预告时序",
    "not found": "未找到",
}

TIER_LABELS = {
    "core": "核心",
    "core_candidate": "候选",
    "preview_candidate": "预告",
    "satellite": "卫星",
    "demand_anchor": "核心",
    "equipment_satellite": "设备",
}

TICKER_TRIGGERS = {
    "601077": "净息差不低于1.60%、不良率不高于1.10%，营收维持正增长。",
    "601825": "营收维持正增长、拨备覆盖率不低于300%，分红率稳定。",
    "000425": "海外和矿机收入双位数增长、经营现金流持续为正、EPS不低于0.60元。",
    "000063": "算力收入占比不低于25%、H2利润恢复正增长、经营现金流改善。",
    "301308": "H2归母净利不低于80亿元、经营现金流改善、无重大存货减值。",
    "600276": "创新药销售增速不低于30%、EPS不低于1.35元、关键BD/临床里程碑兑现。",
    "601138": "H2归母净利不低于321亿元、AI服务器增速高于100%、毛利率不低于7%。",
    "000938": "扣除2.5--3.5亿元一次性收益，重建新华三持股比例与利息费用后的全年EPS。",
    "000977": "预告后EPS已刷新，但现价接近群益90元目标；等待毛利率和营运资金确认。",
    "301165": "数据中心交换机增长延续，且回撤后估值不再透支预告后EPS。",
    "001339": "AI算力/ICT出货兑现，同时当前价格回到新盈利预测可解释区间。",
    "002396": "剔除约1.0--1.2亿元非经常收益后，交换机主营利润仍持续增长。",
    "300475": "重建全年毛利、海普存储收入与现金流；旧全年EPS 2.36元不得继续使用。",
    "603986": "拆分证券公允价值收益与扣非利润，重建存储和MCU全年量价假设。",
    "600685": "拆分造船主营、联营收益和分红收益，获取预告后2026E分母。",
    "002829": "扣非转正前不升级；投资收益不能替代订单、收入和经营现金流。",
    "600601": "重建高端PCB收入、毛利、客户订单和资本开支，旧EPS 0.11元作废。",
    "000636": "Q2利润加速同时MLCC价格、产品结构和现金流持续改善。",
    "001314": "剔除约0.86亿元投资收益，单独验证AI终端主营利润。",
    "002407": "六氟磷酸锂价格与销量继续改善，且Q2减速不延续、现金流转正。",
    "002842": "钨价可顺利传导，下游需求不被高价压制，经营现金流覆盖利润。",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def tex(value: Any) -> str:
    text = str(value)
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
    return "".join(replacements.get(character, character) for character in text)


def num(value: Any, digits: int = 2, missing: str = "---") -> str:
    return f"{float(value):.{digits}f}" if value is not None else missing


def pct(value: Any, digits: int = 1, missing: str = "---") -> str:
    return f"{float(value):.{digits}f}\\%" if value is not None else missing


def compact_excerpt(value: str, limit: int) -> str:
    if not value or value == "not extracted":
        return "原文未形成可稳定抽取的连续段落，保留标题、预测表与PDF路径供复核。"
    text = re.sub(r"\[[^\]]+\]", " ", value)
    text = text.replace("\\", "/")
    text = text.replace("/", " / ")
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", " ", text)
    text = re.sub(r"\bS\d{9,}\b", " ", text)
    text = re.sub(r"[▌◼⚫]", " ", text)
    text = re.sub(r"\.{5,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(分析师|联系人|基本数据|当前股价).{0,80}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if (
        "相对估值" in text
        and "风险提示" in text
        and not any(token in text for token in ("预计", "净利润", "营业收入", "EPS"))
    ):
        return "原文目录未形成可稳定抽取的盈利段，保留EPS元数据与PDF路径供复核。"
    return text[:limit].rstrip(" ，；。") + ("……" if len(text) > limit else "。")


def build_industrial_fulian_section() -> str:
    return r"""
\section{结论：预告后盈利桥已经闭合}

工业富联不再只是AI算力需求锚，而是本报告第七只正式估值标的。公司预计
2026H1归母净利润234--244亿元，中值239亿元、同比约+97\%；其中Q1为
105.95亿元，隐含Q2约133.05亿元、环比+25.6\%。更重要的是，公司同时披露
云服务商AI服务器收入同比增长超过230\%、800G以上数据中心交换机出货量
同比增长1.4倍，盈利增长有直接业务代理，而不是单纯依靠估值扩张。

\begin{dashboardbox}[工业富联：预告后当前价格估值]
\begin{tabularx}{\textwidth}{L{2.4cm}R{1.7cm}R{1.7cm}R{1.7cm}R{1.7cm}R{1.8cm}X}
\toprule
\textbf{现价} & \textbf{H1净利} & \textbf{2026E净利} & \textbf{EPS} &
\textbf{基准价值} & \textbf{最终目标} & \textbf{空间/动作} \\
\midrule
66.27元 & 239亿元 & 560.1亿元 & 2.82元 & 84.60元 & 82.29元 &
+24.2\%；业绩兑现后的回撤配置 \\
\bottomrule
\end{tabularx}
\end{dashboardbox}

\section{预告质量：Q2继续加速，主营证据最完整}

H1预告EPS中值约1.20元，相当于华泰预告后2026E EPS 2.82元的42.4\%。
这一进度略快于简单时间进度，但本报告没有把H1机械翻倍。华泰维持2026E
营收14,803.7亿元、归母净利润560.1亿元；华创给出更高的645.97亿元净利
预测。AStock采用华泰作为基准分母，将华创仅作为牛市盈利交叉验证。

\begin{exhibitbox}[Exhibit 11：收入代理到EPS的闭环]
\begin{tabularx}{\textwidth}{L{3.0cm}L{3.0cm}L{3.2cm}X}
\toprule
\textbf{驱动} & \textbf{已披露证据} & \textbf{盈利转换} & \textbf{仍缺字段} \\
\midrule
AI服务器 & H1云服务商收入同比+230\%以上 & 产品结构和系统价值量提升，推升收入与净利 &
客户分配、单机ASP和分部毛利率未披露 \\
高速网络 & 800G以上交换机出货同比+140\% & 高速互联占比提升改善通信业务质量 &
具体收入占比与价格未披露 \\
下一代平台 & 与大客户联合研发，H2逐步量产 & 支撑H2收入和利润继续增长 &
量产爬坡节奏与良率未披露 \\
现金转换 & Q1经营现金流250.24亿元 & 当前现金流覆盖利润，降低纯账面增长风险 &
H2营运资金仍受大客户和备货影响 \\
\bottomrule
\end{tabularx}
\sourcenote{公司2026H1预告、2026Q1财务包、华泰和华创2026-07-10预告点评。}
\end{exhibitbox}

\section{券商原文穿透与AStock冷判断}

\textbf{华泰证券}在预告后维持“买入”和93元目标，预测2026--2028营收
14,803.7/18,837.1/21,890.3亿元，归母净利润560.1/674.9/779.6亿元，
给予2026E 33倍PE。其核心假设是GB300/Rubin平台放量、单机价值量提升、
Hyperscaler资本开支延续以及液冷自供比例提高。

\textbf{华创证券}同日维持“强推”，预测2026--2028归母净利润
645.97/868.66/1,094.91亿元。归档页面没有披露点目标，因此该行只用于
盈利牛市情景，不进入Street目标权重；这避免把“强推”评级伪造成目标价。

AStock基准只给30倍PE而非华泰33倍，得到84.60元基本面价值；再按65\%
基本面、25\%市场锚72元、10\%华泰目标93元加权，最终目标82.29元。现价
对应华泰EPS约23.5倍PE，仍有空间，但已经不是低位静默布局。

\section{催化、风险与失效条件}

\begin{itemize}
  \item \textbf{升级催化}：H2下一代AI服务器进入稳定量产；AI服务器收入增速仍高于100\%；
  800G以上交换机维持增长；毛利率持续高于7\%并改善。
  \item \textbf{基准门槛}：华泰全年560.1亿元意味着H2至少贡献约321.1亿元净利；
  若H2显著低于该水平，30倍基准PE不成立。
  \item \textbf{主要风险}：北美云厂资本开支下修、GPU平台量产延期、客户集中、贸易摩擦、
  低毛利制造属性重新主导估值，以及营运资金波动。
  \item \textbf{动作纪律}：62--66元为第一观察区；72--76元进入前高压力区；未出现H2
  盈利与毛利验证前，不以93元券商目标作为无条件追涨理由。
\end{itemize}
"""


def build_preview_section(preview_rows: list[dict[str, Any]]) -> str:
    lines = [
        r"\section{预告普查结论：16只不是同一种高增长}",
        "",
        (
            "54只核心/卫星池中，16只在截至7月11日捕获的H1预告表中披露业绩，"
            "其中15只预增、1只扭亏。判断顺序是：先看H1利润和隐含Q2，再看扣非与"
            "一次性，最后比较H1预告EPS与最新券商全年EPS。若H1已经超过旧全年分母，"
            "旧PE立即失效，必须进入预告后重估池。"
        ),
        "",
        r"\small",
        r"\begin{longtable}{L{1.35cm}L{1.75cm}R{1.05cm}R{1.05cm}R{1.10cm}R{1.15cm}R{1.10cm}L{2.45cm}}",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{H1净利} & "
            r"\textbf{隐含Q2} & \textbf{Q2/Q1} & \textbf{H1 EPS} & "
            r"\textbf{占旧全年} & \textbf{质量结论} \\"
        ),
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        (
            r"\textbf{代码} & \textbf{公司} & \textbf{H1净利} & "
            r"\textbf{隐含Q2} & \textbf{Q2/Q1} & \textbf{H1 EPS} & "
            r"\textbf{占旧全年} & \textbf{质量结论} \\"
        ),
        r"\midrule",
        r"\endhead",
    ]
    for row in preview_rows:
        ratio = (
            f"{row['h1_eps_to_latest_2026e_eps_ratio'] * 100:.1f}\\%"
            if row.get("h1_eps_to_latest_2026e_eps_ratio") is not None
            else "---"
        )
        qoq = pct(row.get("q2_vs_q1_pct"))
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{num(row.get('h1_net_profit_midpoint_100mn'))} & "
            f"{num(row.get('q2_implied_net_profit_100mn'))} & {qoq} & "
            f"{num(row.get('h1_eps_midpoint'))} & {ratio} & "
            f"{tex(QUALITY_LABELS.get(row['quality_class'], row['quality_class']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        r"\sourcenote{16份公司正式业绩预告PDF、2026Q1财务包、最新券商预测元数据；利润单位为亿元。}",
        "",
        r"\section{第一组：主营真兑现，可进入正式模型或回撤观察}",
        "",
        (
            r"\textbf{工业富联}的AI服务器收入、800G以上交换机出货和Q2利润均有直接证据，"
            r"且已有华泰/华创预告后预测，因此进入正式估值。"
            r"\textbf{浪潮信息}H1净利中值28.5亿元、隐含Q2约22.45亿元，Q2较Q1增长271\%；"
            r"群益预告同日给出56.67亿元2026E净利和90元目标，中邮预告后EPS 2.53元。"
            r"但7月10日现价89.52元几乎到达90元目标，结论是业绩兑现、等待回撤，而非继续追高。"
        ),
        "",
        (
            r"\textbf{锐捷网络}隐含Q2净利5.52亿元、较Q1增长349\%，非经常损益占H1约2.2\%，"
            r"数据中心交换机是清晰主营驱动；但20日涨幅超过80\%、一年位置约92\%，"
            r"预告后开源EPS 1.87元对应现价估值仍高，只进入回撤观察。"
            r"\textbf{方正科技}H1净利5.7亿元、扣非方向与归母一致，高端PCB产品结构改善；"
            r"但H1 EPS约0.12元已超过旧全年0.11元，必须重建全年分母。"
            r"\textbf{智微智能}H1净利3.84亿元、Q2明显加速，但股价已在一年高位，"
            r"先等待预告后研报与现金流。"
        ),
        "",
        r"\section{第二组：周期与产品结构兑现，但不能把高景气线性外推}",
        "",
        (
            r"\textbf{江波龙}H1净利中值101亿元，H1 EPS约24.08元，已完成旧国信全年EPS"
            r"26.47元的91\%；本报告使用预告后自行重建的200亿元全年净利，而非旧预测。"
            r"\textbf{香农芯创}H1 EPS约8.08元，是旧全年2.36元的342\%，旧PE完全失效；"
            r"企业级存储和海普存储商业化是真增长，但分销毛利、存货和现金流必须重做。"
        ),
        "",
        (
            r"\textbf{风华高科}Q2隐含利润较Q1增长121\%，MLCC、电阻、电感量价和降本共同驱动；"
            r"现价和周期位置要求持续改善。"
            r"\textbf{多氟多}H1 EPS约0.43元已超过旧全年0.36元，但隐含Q2利润较Q1下降65.7\%，"
            r"不能只看同比高增；需验证六氟磷酸锂价格、销量和现金流。"
            r"\textbf{翔鹭钨业}受益钨价传导，Q2继续增长，但缺少有效2026E券商分母，"
            r"高钨价能否顺利向下游转嫁是核心风险。"
        ),
        "",
        r"\section{第三组：主营改善中混入结构性或一次性收益}",
        "",
        (
            r"\textbf{紫光股份}H1净利中值21.15亿元，AI/ICT增长和新华三持股提升均为正面，"
            r"但约2.5--3.5亿元非经常收益不可持续；H1 EPS约0.74元已达到旧全年0.85元的87\%，"
            r"旧模型必须同时更新持股比例、利息费用和一次性收益。"
            r"\textbf{兆易创新}H1净利69亿元、隐含Q2约54.39亿元，但包含证券公允价值收益；"
            r"H1 EPS约10.34元已超过旧全年8.35元，重估必须使用扣非利润。"
        ),
        "",
        (
            r"\textbf{星网锐捷}数据中心交换机是真驱动，但约1.0--1.2亿元非经常收益占H1"
            r"中值约29.7\%；\textbf{亿道信息}约0.86亿元投资收益占H1中值约43.9\%，"
            r"均需把主营与一次性分开。"
            r"\textbf{中船防务}造船订单、生产效率和毛利改善是真实主线，但联营企业与分红"
            r"收益也推高利润，因此进入预告后重估池而非直接给目标。"
        ),
        "",
        r"\section{明确排除：星网宇达}",
        "",
        (
            r"星网宇达H1预计扭亏至约1.05亿元，但扣非仍亏，约1.4亿元投资收益是扭亏主因，"
            r"一次性占报告利润中值超过100\%。在主营收入下降、扣非未转正前，"
            r"该预告不能获得盈利信用，明确排除出核心和重估池。"
        ),
        "",
        r"\begin{riskbox}[预告使用边界]",
        (
            r"业绩预告未经审计；H1利润不是全年利润的简单一半。未披露扣非、现金流、"
            r"存货和客户订单的标的，只能得到方向性信用。预告后没有新研报或公司级模型时，"
            r"本报告只给“重估池/等待模型刷新”，不伪造点目标。"
        ),
        r"\end{riskbox}",
    ]
    return "\n".join(lines)


def company_monitor(row: dict[str, Any]) -> str:
    if row["ticker"] in TICKER_TRIGGERS:
        return TICKER_TRIGGERS[row["ticker"]]
    sector = row["sector"]
    if sector == "银行":
        return "等待中报净息差、资产质量、拨备与分红更新。"
    if sector == "工程机械":
        return "等待海外/国内收入、毛利率、应收账款和经营现金流更新。"
    if sector == "创新药":
        return "等待产品销售、临床/获批、BD里程碑和费用率更新。"
    if sector == "先进封装":
        return "等待H1实际利润、先进封装收入、产能利用率和资本开支回报。"
    if sector == "传媒与AI应用":
        return "等待新品流水、用户付费、内容成本和AI收入对EPS的贡献。"
    if sector == "国防军工与商业航天":
        return "等待订单、收入确认、合同负债和经营现金流同步改善。"
    if sector == "AI存储":
        return "等待存储价格、库存成本、客户认证和经营现金流更新。"
    return "等待H1正式报告与预告后盈利预测更新。"


def build_universe_section(company_rows: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in company_rows:
        grouped[row["sector"]].append(row)
    lines = [
        r"\section{覆盖原则：板块研究不能由少数样本代替}",
        "",
        (
            "本章把9个机会板块拆成54只核心、候选与卫星标的。每只至少给出价格位置、"
            "Q1利润/现金流、H1预告、最新券商预测时序、当前处置和升级条件。正式点目标"
            "只属于7只通过当前价格估值门槛的标的；其余公司即使主题正确，也必须说明"
            "缺少什么证据，不能用“受益者”标签替代盈利模型。"
        ),
    ]
    exhibit_index = 12
    for sector in SECTOR_ORDER:
        rows = grouped[sector]
        lines += [
            "",
            f"\\section{{{tex(sector)}：{len(rows)}只完整公司池}}",
            "",
            SECTOR_VIEWS[sector],
            "",
            f"\\begin{{exhibitbox}}[Exhibit {exhibit_index}：{tex(sector)}核心池快照]",
            r"\small",
            r"\begin{tabularx}{\textwidth}{L{1.25cm}L{1.65cm}L{1.35cm}R{1.05cm}R{1.05cm}R{1.15cm}L{2.45cm}X}",
            r"\toprule",
            (
                r"\textbf{代码} & \textbf{公司} & \textbf{层级} & \textbf{现价} & "
                r"\textbf{一年位} & \textbf{H1净利} & \textbf{研报时序} & \textbf{处置} \\"
            ),
            r"\midrule",
        ]
        exhibit_index += 1
        for row in rows:
            h1 = num(row.get("h1_preview_midpoint_100mn"))
            relation = RELATION_LABELS.get(
                row.get("report_vs_preview"), row.get("report_vs_preview", "---")
            )
            disposition = DISPOSITION_LABELS.get(
                row["valuation_disposition"], row["valuation_disposition"]
            )
            lines.append(
                f"{tex(row['ticker'])} & {tex(row['company'])} & "
                f"{tex(TIER_LABELS.get(row['tier'], row['tier']))} & "
                f"{num(row.get('current_price'))} & {pct(row.get('position_1y_pct'), 0)} & "
                f"{h1} & {tex(relation)} & {tex(disposition)} \\\\"
            )
        lines += [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\normalsize",
            r"\end{exhibitbox}",
            "",
            r"\subsection{逐股研究卡}",
            "",
        ]
        for row in rows:
            preview_text = (
                f"H1预告净利中值{num(row.get('h1_preview_midpoint_100mn'))}亿元，"
                f"隐含Q2为{num(row.get('q2_implied_net_profit_100mn'))}亿元，"
                f"质量归类为{QUALITY_LABELS.get(row.get('preview_quality_class'), '未分类')}"
                if row.get("h1_preview_midpoint_100mn") is not None
                else "截至本轮捕获表未见H1预告，等待正式中报"
            )
            q1_text = (
                f"Q1归母净利{num(row.get('q1_net_profit_100mn'))}亿元、"
                f"经营现金流{num(row.get('q1_ocf_100mn'))}亿元"
                if row.get("q1_net_profit_100mn") is not None
                else "Q1结构化财务包缺失或未稳定返回，报告不填造数字"
            )
            broker_text = (
                f"最新券商元数据为{row.get('latest_broker', '未找到')} "
                f"{row.get('latest_report_date', '未找到')}，2026E EPS "
                f"{num(row.get('latest_2026e_eps'))}元，"
                f"与预告关系为{RELATION_LABELS.get(row.get('report_vs_preview'), row.get('report_vs_preview', '未找到'))}"
            )
            disposition = DISPOSITION_LABELS.get(
                row["valuation_disposition"], row["valuation_disposition"]
            )
            lines += [
                f"\\paragraph{{{tex(row['company'])}（{tex(row['ticker'])}）}}",
                (
                    f"现价{num(row.get('current_price'))}元，位于一年价格区间"
                    f"{pct(row.get('position_1y_pct'))}；{q1_text}。{preview_text}。"
                    f"{broker_text}。\\textbf{{当前处置：{tex(disposition)}。}}"
                    f"升级或降级门槛：{tex(company_monitor(row))}"
                ),
                "",
            ]
    lines += [
        r"\begin{sourcequalitybox}[54只公司池的数据边界]",
        (
            r"南京银行、常熟银行等少数结构化财务包为空时，本报告明确保留缺口，不用同业"
            r"或旧年度数字代填。38只未在捕获预告表命中的公司被标为“等待中报”，"
            r"这不等同于公司确认没有预告；后续更新仍需复查交易所公告。"
        ),
        r"\end{sourcequalitybox}",
    ]
    return "\n".join(lines)


def build_broker_section(digest_rows: list[dict[str, Any]]) -> str:
    lines = [
        r"\section{穿透结果：54只元数据、28只优先池、56份原始PDF}",
        "",
        (
            "本轮对54只公司逐一检查券商研报元数据，并对28只核心、核心候选和预告候选"
            "各归档最近两份原始PDF及文本，共56份、下载失败0份。以下不是标题目录，"
            "而是逐票比较两份报告的预测分母、核心主线、风险与预告时序。若报告早于"
            "最新预告，原预测只作为“旧市场预期”，不得继续作为当前估值分母。"
        ),
        "",
        r"\begin{exhibitbox}[Exhibit 21：研报时序审计]",
        r"\begin{tabularx}{\textwidth}{L{3.2cm}R{2.0cm}R{2.0cm}X}",
        r"\toprule",
        r"\textbf{类型} & \textbf{标的数} & \textbf{PDF数} & \textbf{估值后果} \\",
        r"\midrule",
        r"完整优先池 & 28 & 56 & 每只两份原始PDF，保留预测、风险与本地路径 \\",
        r"预告后新研报 & 3 & 4+2页 & 浪潮信息、锐捷网络、工业富联可使用新分母；工业富联另有两份完整报告页 \\",
        r"预告前旧研报 & 其余预告公司 & 已归档 & 只作旧预期对照，必须进入重估或等待池 \\",
        r"无公开点目标 & 若干 & --- & 不以评级或内部计算冒充Street目标，目标权重为0 \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{exhibitbox}",
    ]
    for row in digest_rows:
        lines += [
            "",
            f"\\section{{{tex(row['company'])}（{tex(row['ticker'])}）：两份原始研报对照}}",
            "",
        ]
        for report in row["reports"]:
            eps = num(report.get("eps_2026e"))
            pe = num(report.get("pe_2026e"), 1)
            relation = RELATION_LABELS.get(
                report.get("report_vs_preview"), report.get("report_vs_preview", "---")
            )
            forecast = compact_excerpt(report.get("forecast_excerpt", ""), 230)
            risk = compact_excerpt(report.get("risk_excerpt", ""), 145)
            lines += [
                (
                    f"\\textbf{{{tex(report['broker'])}，{tex(report['report_date'])}，"
                    f"《{tex(report['title'])}》}}"
                ),
                (
                    f"元数据给出2026E EPS {eps}元、PE {pe}倍；时序为"
                    f"\\textbf{{{tex(relation)}}}。原文盈利段摘要：{tex(forecast)}"
                    f"风险段摘要：{tex(risk)}"
                ),
                "",
            ]
        disposition = DISPOSITION_LABELS.get(row["disposition"], row["disposition"])
        if row["report_vs_preview"] in {"post_preview", "same_day_as_preview"}:
            timing_judgment = (
                "报告预测晚于或同步于预告，可用于更新分母，但仍需按7月10日现价重算空间。"
            )
        elif row["report_vs_preview"] == "pre_preview_forecast_may_be_stale":
            timing_judgment = (
                "两份报告均早于最新预告，只能作为旧市场预期；旧EPS不得继续直接入模。"
            )
        else:
            timing_judgment = (
                "公司未形成H1预告时序，本轮报告用于Q1和全年预测对照，仍需按当前价格重算。"
            )
        lines += [
            r"\begin{keyinsight}[AStock处理]",
            (
                f"处置为\\textbf{{{tex(disposition)}}}。{tex(timing_judgment)}"
                f"下一步门槛：{tex(company_monitor({'ticker': row['ticker'], 'sector': row['sector']}))}"
            ),
            r"\end{keyinsight}",
        ]
    lines += [
        r"\begin{riskbox}[研报使用边界]",
        (
            r"券商EPS、PE和目标价是市场预期锚，不是AStock的事实判断。预告前报告可以证明"
            r"市场此前预期有多低，但不能在预告后继续充当当前分母。仅有“买入/强推”而无"
            r"公开目标价时，Street目标权重必须为0。"
        ),
        r"\end{riskbox}",
    ]
    return "\n".join(lines)


def main() -> None:
    preview_rows = load_json(DATA_DIR / "earnings_preview_quality_20260711.json")["rows"]
    company_rows = load_json(DATA_DIR / "company_cards_20260711.json")["rows"]
    digest_rows = load_json(DATA_DIR / "core_broker_report_digests_20260711.json")[
        "rows"
    ]
    write_text(SECTIONS_DIR / "ch10_industrial_fulian.tex", build_industrial_fulian_section())
    write_text(SECTIONS_DIR / "ch11_earnings_previews.tex", build_preview_section(preview_rows))
    write_text(SECTIONS_DIR / "ch12_core_universe.tex", build_universe_section(company_rows))
    write_text(SECTIONS_DIR / "ch13_broker_penetration.tex", build_broker_section(digest_rows))
    print(
        json.dumps(
            {
                "preview_rows": len(preview_rows),
                "company_rows": len(company_rows),
                "broker_tickers": len(digest_rows),
                "sections": [
                    "ch10_industrial_fulian.tex",
                    "ch11_earnings_previews.tex",
                    "ch12_core_universe.tex",
                    "ch13_broker_penetration.tex",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
