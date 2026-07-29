#!/usr/bin/env python3
"""Render deterministic LaTeX appendix tables from structured case data."""

from __future__ import annotations

import json
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]

BLOCKS = {
    "Compute platform and accelerator demand anchors": "算力与需求锚",
    "Server, OEM, ODM and rack integration": "服务器/整柜",
    "Power, UPS, transformer and electrical infrastructure": "供配电",
    "Thermal management and liquid cooling": "液冷/热管理",
    "Optical, networking and interconnect": "光网络/互联",
    "Storage, memory and HBM": "存储/内存",
    "PCB, CCL, connectors, cables and precision components": "PCB/连接",
    "IDC, cloud, operator and downstream applications": "IDC/应用",
}

CLASSES = {
    "core_valuation": "核心估值",
    "satellite_watch": "卫星观察",
    "watchlist": "观察",
    "demand_anchor": "需求锚",
    "excluded": "排除",
    "unavailable": "不可得",
    "out_of_scope": "范围外参照",
}

STATUS = {
    "official roadmap": "官方路线图",
    "official product capability": "官方产品能力",
    "official filing evidence": "公司公告",
    "official relationship evidence": "官方关系",
    "official policy context": "官方政策",
    "negative official response": "官方否认",
    "relationship unconfirmed": "关系未确认",
    "not disclosed": "未披露",
    "global reference": "海外参照",
    "official physical disclosure": "官方实物披露",
    "official benchmark context": "官方竞品参照",
    "official ecosystem context": "官方生态参照",
    "official product context": "官方产品参照",
    "official-disclosed": "官方披露",
    "official denial": "官方否认",
    "official demand anchor": "官方需求锚",
    "official capacity context": "官方产能参照",
    "official-disclosed at architecture level": "官方架构披露",
    "official-disclosed product and delivery": "官方产品/交付",
    "company capability context": "公司能力",
    "company did not confirm": "公司未确认",
    "industry context": "行业参照",
    "inferred from system ownership": "仅系统归属推断",
    "not found": "未找到",
    "rumor / not confirmed": "传闻/未确认",
}

SUBSEGMENTS = {
    "AI accelerator": "AI 加速器", "SuperPoD platform": "超节点平台",
    "AI accelerator competitor": "加速器竞品", "Model training application": "模型训练应用",
    "Domestic accelerator competitors": "国产加速器竞品", "SuperPoD system integration": "超节点集成",
    "Server ecosystem": "服务器生态", "Server OEM": "服务器 OEM", "Server OEM competitor": "服务器 OEM 竞品",
    "Rumored ODM mapping": "传闻 ODM 映射", "Integrated power": "综合供电",
    "UPS and integrated infrastructure": "UPS/基础设施", "HVDC power": "HVDC 供电",
    "Transformer and magnetic components": "变压器/磁性元件", "UPS": "UPS",
    "Busway / transformer / backup power": "母线/变压器/备电", "End-to-end liquid cooling": "端到端液冷",
    "Industrial liquid cooling": "工业液冷", "Liquid-cooling system": "液冷系统",
    "Liquid-cooling connectors": "液冷连接器", "Coolant, pumps and valves": "冷却液/泵阀",
    "Scale-up interconnect": "Scale-up 互联", "Optical switching / OCS": "光交换/OCS",
    "Optical modules and engines": "光模块/光引擎", "Optical modules": "光模块",
    "Optical components": "光器件", "High-speed copper cable": "高速铜缆",
    "High-speed connector": "高速连接器", "Switch/NIC silicon": "交换/NIC 芯片",
    "HBM-like memory": "类 HBM 内存", "DRAM wafer manufacturing": "DRAM 晶圆制造",
    "Memory interface": "内存接口", "SPD / EEPROM": "SPD/EEPROM", "Enterprise SSD": "企业级 SSD",
    "High-speed CCL": "高速 CCL", "High-speed PCB": "高速 PCB", "High-density PCB": "高密度 PCB",
    "ABF substrate / PCB": "ABF 载板/PCB", "Probe card": "探针卡", "Cloud platform": "云平台",
    "Telecom operator": "电信运营商", "Model application": "模型应用", "IDC / colocation": "IDC/托管",
    "Policy and public compute": "政策/公共算力",
}

NODE_NAMES = {
    "FC001": "华为昇腾 950DT", "FC002": "华为 Atlas 950 SuperPoD", "FC003": "英伟达 Rubin NVL 平台",
    "FC004": "AMD Instinct/UALink 生态", "FC005": "科大讯飞", "FC006": "寒武纪/海光/摩尔线程",
    "FC007": "华为计算产品线", "FC008": "拓维信息/兆瀚", "FC009": "神州数码/鲲泰",
    "FC010": "超聚变", "FC011": "浪潮信息", "FC012": "四川长虹",
    "FC013": "华为数字能源", "FC014": "科华数据", "FC015": "中恒电气", "FC016": "伊戈尔",
    "FC017": "科士达", "FC018": "Atlas 专属电气 BOM", "FC019": "申菱环境", "FC020": "英维克",
    "FC021": "同飞股份", "FC022": "高澜股份", "FC023": "航天电器", "FC024": "Atlas 专属流体子系统",
    "FC025": "华为 UnifiedBus/灵衢", "FC026": "华为跨柜光互联", "FC027": "华工科技",
    "FC028": "光迅科技", "FC029": "天孚通信/光库科技", "FC030": "沃尔核材/兆龙互连",
    "FC031": "鼎通科技", "FC032": "华为自研交换/NIC 栈", "FC033": "华为 HiZQ 2.0",
    "FC034": "国产 DRAM 制造映射", "FC035": "澜起科技", "FC036": "聚辰股份",
    "FC037": "佰维存储/江波龙/德明利", "FC038": "生益科技", "FC039": "深南电路",
    "FC040": "沪电股份", "FC041": "胜宏科技", "FC042": "广合科技", "FC043": "强一股份",
    "FC044": "华为云", "FC045": "中国移动", "FC046": "中国电信", "FC047": "中国联通",
    "FC048": "科大讯飞", "FC049": "国内 IDC 运营商", "FC050": "国家及地方智算项目",
}

ACTION = {
    "watch": "观察", "avoid_chasing": "避免追高", "selective_watch": "选择性观察",
    "wait_for_q2_margin": "等待毛利恢复", "highest_linkage_watch": "最高关系观察",
    "value_watch": "等待估值回落", "value_satellite": "低纯度价值卫星",
    "downstream_event_watch": "下游事件验证", "unconfirmed_linkage_watch": "关系未确认观察",
}

TRIGGERS = {
    "000034": ("自有品牌毛利/现金转化", "分销利润或现金继续落后"),
    "000988": ("800G+交付与光连接毛利", "交付或毛利低于预期"),
    "600183": ("高端 CCL 结构/利用率", "产能爬坡或原料价差恶化"),
    "002916": ("AI PCB 良率/新线利用率", "高层板良率与毛利不达标"),
    "002463": ("AI PCB 出货/客户结构", "利用率或客户集中恶化"),
    "300476": ("海外产能良率/AI 产品结构", "高增长和毛利不可持续"),
    "002837": ("Q2/H1 利润与毛利恢复", "利润恢复失败或订单弱"),
    "301018": ("数据服务订单转收入/现金", "订单不转收入或应收恶化"),
    "002335": ("项目验收/扣非利润", "非经常收益主导或回款弱"),
    "002130": ("高速线缆利用率/利润", "认证、产能或铜价传导失效"),
    "002230": ("10 月模型性能/付费转化", "发布延期或现金转化弱"),
    "002025": ("平台认证/连接器收入", "关系仍未确认或军品周期下行"),
}


def esc(value: object) -> str:
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
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def main() -> None:
    payload = json.loads((CASE / "data/full_chain_universe_20260718.json").read_text(encoding="utf-8"))
    rows = payload["rows"]
    lines = [
        r"\begin{exhibitbox}[Atlas 950/AIDC 相关节点全景表（50 个节点）]",
        r"\scriptsize",
        r"\begin{longtable}{L{1.0cm}L{2.2cm}L{2.5cm}L{3.0cm}L{2.2cm}L{2.0cm}L{1.8cm}}",
        r"\toprule",
        r"\textbf{ID} & \textbf{模块} & \textbf{子环节} & \textbf{节点/公司} & \textbf{代码/市场} & \textbf{分类} & \textbf{证据状态}\\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        block = BLOCKS.get(row["chain_block"], row["chain_block"])
        classification = CLASSES.get(row["classification"], row["classification"])
        status = STATUS.get(row["evidence_status"], row["evidence_status"])
        ticker = row.get("listed_ticker") or row.get("market")
        subsegment = SUBSEGMENTS.get(row["subsegment"], row["subsegment"])
        node_name = NODE_NAMES.get(row["node_id"], row["node_name"])
        lines.append(
            f"{esc(row['node_id'])} & {esc(block)} & {esc(subsegment)} & "
            f"{esc(node_name)} & {esc(ticker)} & {esc(classification)} & {esc(status)}\\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\sourcenote{50 节点全链条证据池。分类只表示研究处置，不表示 Atlas 950 供货或投资评级。}",
        r"\end{exhibitbox}",
    ]
    out = CASE / "sections/generated_full_chain_table.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    valuation = json.loads((CASE / "data/current_valuation_model_20260718.json").read_text(encoding="utf-8"))["rows"]
    v = [
        r"\begin{exhibitbox}[完整最终估值矩阵：财务、方法与权重]", r"\scriptsize", r"\setlength{\tabcolsep}{2.2pt}",
        r"\begin{longtable}{L{1.0cm}R{1.25cm}R{1.25cm}R{1.05cm}R{1.0cm}R{1.15cm}R{1.15cm}L{1.25cm}R{1.15cm}R{1.1cm}L{1.7cm}}",
        r"\toprule", r"\textbf{代码} & \textbf{市值} & \textbf{26E收入} & \textbf{26E净利} & \textbf{EPS} & \textbf{PE目标} & \textbf{P/B目标} & \textbf{F/M/B} & \textbf{综合目标} & \textbf{空间} & \textbf{动作}\\", r"\midrule", r"\endhead",
    ]
    for row in valuation:
        weights = f"{row['fundamental_weight']:.0%}/{row['market_weight']:.0%}/{row['broker_weight']:.0%}"
        upside_text = esc(f"{row['upside']:.1%}")
        v.append(
            f"{esc(row['ticker'])} & {row['market_cap_100mn_cny']:.0f} & {row['revenue_2026e_100mn']:.1f} & {row['np_2026e_100mn']:.2f} & {row['eps_2026e']:.3f} & "
            f"{row['primary_base_target']:.2f} & {row['secondary_base_target']:.2f} & {esc(weights)} & {row['final_target']:.2f} & {upside_text} & {esc(ACTION[row['action']])}\\\\"
        )
    v += [r"\bottomrule", r"\end{longtable}", r"\sourcenote{单位：亿元、元。F/M/B 为基本面/市场/外部明示目标权重；PE 使用现股本重算 EPS，独立 P/B 锚使用交易所 FY2025 归母净资产、现股本、标准化 ROE、权益成本与永续增速，Atlas 专属收入、净利与 EPS 为 0。}", r"\end{exhibitbox}", ""]
    v += [
        r"\begin{exhibitbox}[完整最终估值矩阵：证据、催化与失效]", r"\scriptsize",
        r"\begin{longtable}{L{1.1cm}L{2.0cm}L{3.5cm}L{3.7cm}L{3.7cm}}",
        r"\toprule", r"\textbf{代码} & \textbf{证据等级} & \textbf{估值边界} & \textbf{下一验证/催化} & \textbf{失效/下调条件}\\", r"\midrule", r"\endhead",
    ]
    for row in valuation:
        trigger, invalidation = TRIGGERS[row["ticker"]]
        relationship = "关系较强/专属订单未证实" if row["ticker"] in {"301018", "002230"} else "广义业务可核验/Atlas 关系弱或未确认"
        v.append(f"{esc(row['ticker'])} & {esc(relationship)} & 已披露更广义业务；Atlas 信用为零 & {esc(trigger)}；平台订单为额外升级项 & {esc(invalidation)}；路线图延期或无订单\\\\")
    v += [r"\bottomrule", r"\end{longtable}", r"\sourcenote{交易所年报原件、客户链审计、原始卖方盈利预测与风险矩阵。动作均为研究监测处置，不构成交易建议。}", r"\end{exhibitbox}"]
    vout = CASE / "sections/generated_valuation_matrix.tex"
    vout.write_text("\n".join(v) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(out), "valuation_rows": len(valuation), "valuation_output": str(vout)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
