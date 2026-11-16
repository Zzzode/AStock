#!/usr/bin/env python3
"""Build a bounded cross-candidate disposition from frozen case artifacts.

This tool does not calculate an investable result.  It preserves the distinction
between a negative diagnostic and an unclosed data/operability gate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = CASE_ROOT / "analysis"
OUTPUT_JSON = ANALYSIS / "r11_open_universe_candidate_disposition_20260815.json"
OUTPUT_MD = ANALYSIS / "r11_open_universe_candidate_disposition_20260815.md"


def read_json(filename: str) -> dict[str, Any]:
    with (ANALYSIS / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def ratio(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%"


def expect(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def add_c14_row() -> dict[str, Any]:
    candidates = sorted(ANALYSIS.glob("c14_public_reit_feasibility_*.json"))
    if not candidates:
        return {
            "candidate_id": "C14",
            "route": "公开募集基础设施 REIT",
            "representative_objects": [],
            "evidence_class": "研究进行中；不构成经济排除",
            "strict_hurdle_test": "待 C14 统一复核",
            "observed_evidence": "正在以一手产品、价格和分派资料建立有界诊断。",
            "admission_decision": "未进入结论或行动范围",
            "why_not_admitted": ["C14 工件尚未生成。"],
            "reopen_or_completion_gate": ["完成产品尽调、历史口径与个人交易可行性审计。"],
            "source_artifacts": [],
            "independent_check": "待完成",
            "portfolio_q": 0,
        }

    source = candidates[-1]
    payload = json.loads(source.read_text(encoding="utf-8"))
    gross = payload["strict_5pct_test"]["gross_cost_free_diagnostic"]
    failures = "、".join(
        f"{row['year']} 年 {row['gross_cost_free_cash_return'] * 100:.2f}%"
        for row in gross["annual_failures"]
    )
    product = payload["representative_product_diligence"]["product"]
    return {
        "candidate_id": "C14",
        "route": "公开募集基础设施 REIT",
        "representative_objects": [product["code"]],
        "evidence_class": "一手规则、产品/年报/分派披露与上交所事后价格、分派行诊断；非个人净后成本总回报",
        "strict_hurdle_test": (
            f"零成本现金诊断中 {failures} 低于 5%；"
            f"{gross['rolling_five_year_failure_count']}/{gross['rolling_five_year_window_count']} 个可得滚动五年窗口低于 5%；"
            "严格个人净后成本结果未建立"
        ),
        "observed_evidence": (
            f"代表品种 {product['code']}（{product['name']}）的公开价格加现金分配诊断，"
            "不把分派率、净值或零成本结果当作个人总回报。"
        ),
        "admission_decision": "不准入",
        "why_not_admitted": payload["blocking_requirements"],
        "reopen_or_completion_gate": payload["next_research_gate"],
        "source_artifacts": [
            str(source.relative_to(CASE_ROOT)),
            "analysis/c14_public_reit_rulebook_20260815.json",
        ],
        "independent_check": "C14 源文件哈希与输出状态校验通过；尚无独立净后成本回放",
        "portfolio_q": payload["portfolio_q"],
        "completed": True,
    }


def build_payload() -> dict[str, Any]:
    c7 = read_json("c7_static_core_satellite_price_diagnostic_20260815.json")
    c8 = read_json("c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json")
    c9 = read_json("c9_commodity_actual_contract_feasibility_20260815.json")
    c10 = read_json("c10_direct_equity_quality_distribution_candidate_20260815.json")
    c11 = read_json("c11_market_neutral_fund_nav_proxy_20260815.json")
    c12 = read_json("c12_cash_futures_basis_feasibility_20260815.json")
    c13 = read_json("c13_etf_option_covered_call_feasibility_20260815.json")
    r8 = read_json("r8_c11_independent_audit_20260815.json")
    r9 = read_json("r9_c10_independent_diagnostic_audit_20260815.json")
    r10 = read_json("r10_c12_independent_route_audit_20260815.json")

    expect(c7["portfolio_q"], 0, "C7 q")
    expect(c8["result"]["status"], "PRICE_PROXY_HURDLE_FALSIFIED", "C8 status")
    expect(c9["status"], "NOT_FEASIBLE_FOR_RETURN_CLAIM_OR_PERSONAL_ACTION_YET", "C9 status")
    expect(r9["audit_status"], "PASS", "R9 audit")
    expect(c11["result"]["status"], "OFFICIAL_NAV_PROXY_HURDLE_FALSIFIED", "C11 status")
    expect(r8["audit_status"], "PASS", "R8 audit")
    expect(c12["status"], "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION", "C12 status")
    expect(r10["audit_status"], "PASS", "R10 audit")
    expect(c13["strict_5pct_test"]["status"], "NOT_FEASIBLE_FOR_RETURN_CLAIM", "C13 status")

    c7_stats = c7["arithmetic_output"]
    c8_result = c8["result"]
    c11_result = c11["result"]
    c10_years = r9["independent_result"]
    c10_failures = [row for row in c10_years if row["year"] in r9["below_5pct_years"]]

    c14 = add_c14_row()
    rows = [
        {
            "candidate_id": "C7",
            "route": "多资产 ETF 静态核心—卫星组合",
            "representative_objects": ["510300", "510500", "510880", "511010", "511990", "518880"],
            "evidence_class": "上交所事后市场价格诊断；非总回报、非执行结果",
            "strict_hurdle_test": "12 个完整年度中 5 个低于 5%；1,952 个滚动五年端点中 1,428 个低于 5%",
            "observed_evidence": {
                "annualized_market_price_unitized_change": c7_stats["annualized_market_price_unitized_change"],
                "maximum_drawdown": c7_stats["maximum_drawdown"],
                "complete_year_below_5pct": c7_stats["complete_calendar_year_summary"]["below_5pct_count"],
                "rolling_below_5pct": c7_stats["rolling_five_year"]["below_5pct_count"],
                "rolling_total": len(c7_stats["rolling_five_year"]["rows"]),
            },
            "admission_decision": "不准入",
            "why_not_admitted": [
                "即使仅作为市场价格诊断，固定组合已出现多年度与大量滚动窗口低于门槛。",
                "价格调整口径、分派/事件、成本和成交记录未闭合，不能升级为投资者总回报。",
            ],
            "reopen_or_completion_gate": [
                "独立、获授权的点时点总回报与执行数据包。",
                "在看结果前冻结全资产的回放和成本规则。",
            ],
            "source_artifacts": [
                "analysis/c7_static_core_satellite_price_diagnostic_20260815.json",
                "analysis/r7_c7_c8_independent_audit_20260815.json",
            ],
            "independent_check": "R7 已复核共享公共行情输入的算术；不改变总回报/执行边界",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C8",
            "route": "可转债 ETF 固定配置",
            "representative_objects": ["511180", "511380", "511010"],
            "evidence_class": "冻结的公开市场价格算术代理；非正式总回报或执行结果",
            "strict_hurdle_test": "完整年度 2022 与 2023 低于 5%；187 个滚动五年端点中 123 个低于 5%",
            "observed_evidence": {
                "annualized_net_unitized_change": c8_result["annualized_net_unitized_change"],
                "maximum_drawdown": c8_result["max_drawdown"],
                "complete_year_failures": [
                    {"year": row["year"], "net_unitized_change": row["net_unitized_change"]}
                    for row in c8_result["complete_year_failures"]
                ],
                "rolling_below_5pct": c8_result["rolling_failure_count"],
                "rolling_total": c8_result["rolling_window_count"],
            },
            "admission_decision": "不准入",
            "why_not_admitted": [
                "固定规则的价格代理已被自身的完整年度和滚动端点否证。",
                "仍缺分派、事件、实际成交和个人交易路径，不能把代理称为净总回报。",
            ],
            "reopen_or_completion_gate": [
                "仅能以全新、预冻结的产品和总回报/执行研究重新提出假设。",
            ],
            "source_artifacts": [
                "analysis/c8_convertible_bond_etf_fixed_allocation_price_proxy_20260815.json",
                "analysis/r7_c7_c8_independent_audit_20260815.json",
            ],
            "independent_check": "R7 独立重算公共行情算术；不升级证据等级",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C9",
            "route": "商品期货实际合约趋势",
            "representative_objects": ["CU", "AU", "RU"],
            "evidence_class": "交易所规则与六个事后实际合约样本",
            "strict_hurdle_test": "未测试；没有完整、点时点实际合约和执行账本",
            "observed_evidence": "交易所层面的合约和风控规则已核验；六个日期的实际合约文件仅证明有限来源路径。",
            "admission_decision": "不准入",
            "why_not_admitted": [
                "没有完整合约生命周期、滚动、保证金、限额、费用、流动性和成交状态。",
                "不能以连续合约替代实际合约损益。",
            ],
            "reopen_or_completion_gate": [
                "取得具有合法权利、可保留且带来源时间戳的全量实际合约数据；不得以匿名连续合约替代。",
                "冻结逐合约的上市、到期、交易日历、交割和交易状态主表。",
                "归档逐日交易所保证金、限额、费用及经纪端规则，并预先写明无成交/部分成交处理。",
                "在不记录个人信息的前提下，独立确认账户可达性。",
                "在计算前冻结逐日盯市、换月、成本、风险事件和端点总体规则，并由独立人员复核。",
            ],
            "source_artifacts": ["analysis/c9_commodity_actual_contract_feasibility_20260815.json"],
            "independent_check": "来源哈希和案例控制已验证；未产生收益回放",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C10",
            "route": "直接股票质量与分派研究篮子",
            "representative_objects": ["600519", "600900", "601398", "601088"],
            "evidence_class": "发行人尽调加事后四股票价/税前现金分派诊断；非 PIT 总回报",
            "strict_hurdle_test": "2022 为 -0.15%，2025 为 2.05%，均低于 5%；滚动五年因样本长度及口径不可裁决",
            "observed_evidence": {
                "complete_years": c10_years,
                "below_5pct_years": r9["below_5pct_years"],
                "failing_rows": c10_failures,
            },
            "admission_decision": "不准入",
            "why_not_admitted": [
                "即使对分派采取宽松的税前现金口径，固定事后篮子仍在两个完整年度低于门槛。",
                "不是全市场点时点筛选、企业行为全账本、税费与成交回放。",
            ],
            "reopen_or_completion_gate": [
                "对完整 A 股母体使用预冻结的点时点状态、总回报、成本和成交数据。",
                "把未来观察作为新假设，而不是修复既有事后篮子。",
            ],
            "source_artifacts": [
                "analysis/c10_direct_equity_quality_distribution_candidate_20260815.json",
                "analysis/r9_c10_independent_diagnostic_audit_20260815.json",
            ],
            "independent_check": "R9 直接解析冻结原始文件并复算通过",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C11",
            "route": "市场中性公募基金 NAV 代理",
            "representative_objects": ["008856"],
            "evidence_class": "管理人披露累计净值代理；非持有人申赎结果",
            "strict_hurdle_test": "2022、2024、2025 低于 5%；204/204 可用滚动 1260 观察端点低于 5%",
            "observed_evidence": {
                "annualized_cumulative_nav_change": c11_result["annualized_cumulative_nav_change"],
                "maximum_drawdown": c11_result["maximum_drawdown_from_published_cumulative_nav"],
                "complete_year_failures": c11_result["complete_year_failures"],
                "rolling_below_5pct": c11_result["rolling_failure_count"],
                "rolling_total": c11_result["rolling_failure_count"],
            },
            "admission_decision": "不准入",
            "why_not_admitted": [
                "固定管理人披露净值代理未通过年度和全部可用滚动端点。",
                "开放期、渠道、费用和持有人实际成交没有被替代为可执行结果。",
            ],
            "reopen_or_completion_gate": ["不同产品须以独立预冻结方案另立假设并复核。"],
            "source_artifacts": [
                "analysis/c11_market_neutral_fund_nav_proxy_20260815.json",
                "analysis/r8_c11_independent_audit_20260815.json",
            ],
            "independent_check": "R8 直接解析冻结管理人净值文件并复算通过",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C12",
            "route": "国债现货—期货基差",
            "representative_objects": ["T", "TF", "511260"],
            "evidence_class": "CFFEX/SSE 规则、产品披露与六个实际合约来源样本",
            "strict_hurdle_test": "不可测试；没有完整匹配的现券、交割、融资、成本和双腿成交账本",
            "observed_evidence": "R10 独立核验实际 T/TF 合约来源样本与 2026-08-14 的 T2612 研究筛选观察。",
            "admission_decision": "不准入",
            "why_not_admitted": [
                "ETF 不是可交割债券，不能把 ETF/期货关系误写为无风险收敛。",
                "缺交割券、转换因子、融资、托管、两腿成交、个人路径以及完整端点。",
            ],
            "reopen_or_completion_gate": [
                "取得带权利证明的点时点 T 合约、生命周期、交割券/转换因子、现券价格/应计利息/票息数据。",
                "获得带日期的经纪佣金、保证金、现券/ETF 路径、托管和交割操作文件。",
                "在看到结果前冻结双腿、无成交、成本、换月和盯市规则，并独立重算全部年度和滚动五年端点。",
                "任一字段缺失时保留“不可测且不可行动”，不得用连续合约、通用 ETF 收益或虚构成交替代。",
            ],
            "source_artifacts": [
                "analysis/c12_cash_futures_basis_feasibility_20260815.json",
                "analysis/r10_c12_independent_route_audit_20260815.json",
            ],
            "independent_check": "R10 直接解析冻结 CFFEX CSV 并通过",
            "portfolio_q": 0,
        },
        {
            "candidate_id": "C13",
            "route": "沪深 300 ETF 备兑认购期权",
            "representative_objects": ["510300", "上交所沪深300ETF认购期权"],
            "evidence_class": "上交所规则和产品文件；非实际合约执行样本",
            "strict_hurdle_test": "不可测试；实际合约生命周期、报价、费用、成交与账户证据未闭合",
            "observed_evidence": "交易所已披露合约、适当性、调整和数据字段边界；规则本身不产生收益记录。",
            "admission_decision": "不准入",
            "why_not_admitted": [
                "备兑机制不消除标的下跌和调整风险。",
                "没有点时点实际合约、买卖价/深度/成交、费用、结算和个人账户证据。",
            ],
            "reopen_or_completion_gate": [
                "带调整与生命周期的点时点实际合约主表。",
                "逐合约历史买卖价、深度、成交与官方结算数据。",
                "标的总回报、分派和交易状态历史。",
                "带日期的交易所/经纪费用、税费、保证金和备兑保留规则。",
                "成交状态、部分成交与账户/结算可行性证据，以及预冻结的独立复核方案。",
            ],
            "source_artifacts": ["analysis/c13_etf_option_covered_call_feasibility_20260815.json"],
            "independent_check": "规则来源哈希已验证；没有收益回放",
            "portfolio_q": 0,
        },
        c14,
    ]

    return {
        "artifact_id": "DPSFS-R11-OPEN-UNIVERSE-DISPOSITION-v1",
        "as_of": "2026-08-15",
        "scope": "The listed tracks are representative, bounded research routes. The disposition does not prove that no future domestic strategy can meet the target.",
        "strict_research_hurdle": {
            "complete_calendar_year_net_return": ">= 5%",
            "rolling_five_year_annualized_net_return": ">= 5%",
            "boundary": "A research admission test only; not a guarantee, forecast, allocation, holding or external-action authorization.",
        },
        "rows": rows,
        "portfolio_q": 0,
        "formal_decision_eligible": False,
        "usable_candidate_count": 0,
        "disposition": "NO_CURRENT_CANDIDATE_CLEARS_THE_STRICT_RESEARCH_ADMISSION_GATE",
        "synthesis": [
            "C7, C8, C10 and C11 contain observed negative diagnostic evidence under their stated, non-executable boundaries.",
            "C9, C12 and C13 have documented mechanics but lack the data and operational package required to calculate the strict net-return endpoints.",
            "C14 的单一代表品种在宽松诊断下也出现年度与全部可得滚动五年失败；这不是对整个公募 REIT 类别的否定。",
            "No mixture of an invalidated diagnostic and an untested route may be represented as a usable strategy.",
        ],
        "next_case_gate": [
            "如继续研究公募 REIT，先取得覆盖全体候选的点时点价格/净值/分配/公司行动总体，而不是从单一代表品种推及全类别。",
            "对任何重启路线，在冻结新方案前取得带权利证明的点时点总回报/实际合约、事件、成本、成交和账户路径数据。",
            "在考虑决策范围前，独立计算全部端点，并完成前瞻性纸面核对。",
        ],
        "no_action_statement": "本处置表不授权申购、赎回、买入、卖出、期货或期权交易、回购、交割、开户、配置或任何外部动作。",
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# 开放资产池候选路线统一处置表",
        "",
        "- 截止日：2026-08-15",
        "- 状态：`q=0`；没有候选被认定为可用策略。",
        "- 严格研究门槛：每个完整自然年经成本后净回报率不低于 5%，且每个滚动五年区间年化净回报率不低于 5%。这是准入测试，不是收益承诺、预测或操作指令。",
        "",
        "## 结论",
        "",
        "当前已完成的代表性路线没有任何一条可以诚实地写成满足严格门槛、且能够由个人执行的策略。这个结论只覆盖下表的已研究路线；它不推出国内未来不存在其他可研究的方案。公募 REIT 已完成一个代表品种的研究，但单一品种的结果不能外推为整个类别的经济性结论。",
        "",
        "## 路线处置",
        "",
        "| 路线 | 实际测试或已核验内容 | 处置 | 不能准入的直接原因 | 重新打开的门槛 |",
        "|---|---|---|---|---|",
    ]
    for row in payload["rows"]:
        observed = row["observed_evidence"]
        if isinstance(observed, dict):
            if row["candidate_id"] == "C7":
                observed_text = (
                    f"市场价格年化变动 {ratio(observed['annualized_market_price_unitized_change'])}，"
                    f"最大回撤 {ratio(observed['maximum_drawdown'])}"
                )
            elif row["candidate_id"] == "C8":
                observed_text = (
                    f"价格代理年化变动 {ratio(observed['annualized_net_unitized_change'])}，"
                    f"最大回撤 {ratio(observed['maximum_drawdown'])}"
                )
            elif row["candidate_id"] == "C10":
                observed_text = "独立复算的年度结果为 2022 年 -0.15%、2023 年 13.02%、2024 年 26.15%、2025 年 2.05%"
            elif row["candidate_id"] == "C11":
                observed_text = (
                    f"累计净值代理年化变动 {ratio(observed['annualized_cumulative_nav_change'])}，"
                    f"最大回撤 {ratio(observed['maximum_drawdown'])}"
                )
            else:
                observed_text = "见机器可读工件"
        else:
            observed_text = str(observed)
        why = row["why_not_admitted"]
        if isinstance(why, list):
            why_items = [
                str(item.get("impact", item)) if isinstance(item, dict) else str(item)
                for item in why
            ]
            why = "；".join(item.rstrip("。；") for item in why_items) + "。"
        gate = row["reopen_or_completion_gate"]
        if isinstance(gate, list):
            gate = "；".join(str(item).rstrip("。；") for item in gate) + "。"
        lines.append(
            f"| {row['candidate_id']}：{row['route']} | {row['strict_hurdle_test']}；{observed_text} | {row['admission_decision']} | {why} | {gate} |"
        )

    lines.extend(
        [
            "",
            "## 不能跨越的推理边界",
            "",
            "1. 市场价格、税前现金分派或管理人累计净值代理都不是个人经成本后总回报，更不是未来收益。",
            "2. 交易所规则、产品说明和少量实际合约样本可以说明机制或数据路径，不能替代完整历史、双腿成交、费用、账户与托管证据。",
            "3. 不能将一条被否证的静态组合和一条尚不可测的衍生品路线拼接为“已验证的策略”。",
            "4. 任何新候选必须先以点时点数据、事件、成本、成交与账户路径冻结规则，再计算全部年度和滚动窗口；若任一门槛未闭合，仍维持 `q=0`。",
            "",
            "## 下一研究门槛",
            "",
        ]
    )
    for index, item in enumerate(payload["next_case_gate"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(["", payload["no_action_statement"], ""])
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(markdown(payload), encoding="utf-8")
    print("R11 OPEN-UNIVERSE CANDIDATE DISPOSITION: PASS")


if __name__ == "__main__":
    main()
