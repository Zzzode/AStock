#!/usr/bin/env python3
"""Build C51, a bounded SSE ETF-collar option-family screen.

This artifact distinguishes a genuinely different payoff family from the
previous covered-call route.  It deliberately stops before product, series,
strike, expiry, account, cost, fill or return selection.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c51-sse-etf-option-collar-scope-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.md"
EXPECTED_SOURCE_IDS = {"C51-S01", "C51-S02", "C51-S03", "C51-S04", "C51-S05"}
EXPECTED_MANIFEST_SHA256 = "993e481ff1f04a03e1f1e02c2ed1253dd64f5a31e32a15c2df4cebd8c2934914"
EXPECTED_SOURCES = {
    "C51-S01": {
        "filename": "sse_option_investor_suitability_page.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781453.shtml",
        "sha256": "e79cda6747d18ae145fbb2de8e6dd0bbc909969c2af4717976d7a6644c53a5c0",
    },
    "C51-S02": {
        "filename": "sse_option_investor_suitability_guideline.docx",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781453/files/733e45a7625f460facc66cff7ddcfc8b.docx",
        "sha256": "81992a8ec243c6829fbc43f194836d05277905cda551dbaccab961e4447a28a0",
    },
    "C51-S03": {
        "filename": "sse_stock_option_trading_rule_page.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781448.shtml",
        "sha256": "ddafdc569fe845cfb5e612e07006288629680433d9dd72bdb4e5ff5a2956b540",
    },
    "C51-S04": {
        "filename": "sse_stock_option_trading_rule.docx",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781448/files/0c0f89e74e9c4a5b9aa3a7acafdf5119.docx",
        "sha256": "fff3aaeb338da5d1e1a5892ab7601d79393dd33659b01cb0595b214e2df4a8a9",
    },
    "C51-S05": {
        "filename": "sse_market_data_file_exchange_specification.pdf",
        "url": "https://www.sse.com.cn/services/tradingtech/development/c/10810429/files/ca36291a287242698ad505bce1a7efcc.pdf",
        "sha256": "233d98bdc1faf26cd3940495bac37f6603b6b328e049a2e81244efc394a154c2",
    },
}
REPO_ROOT = CASE_DIR.parents[2]
PREDECESSOR_C13 = REPO_ROOT / "workspace" / "research" / "domestic-personal-securities-futures-strategy-20260814" / "analysis" / "c13_etf_option_covered_call_feasibility_20260815.json"
EXPECTED_PREDECESSOR_C13_SHA256 = "f2859c71d8cbd57eeb6eee211a1e3700c7d16e3694ed3127ce12c07931ada434"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8")
    text = re.sub(r"<[^>]+>", " ", xml)
    return re.sub(r"\s+", " ", html.unescape(text))


def read_pdf_text(path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(completed.returncode == 0, "C51 market-data PDF text extraction failed")
    return completed.stdout


def write_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def build() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest.get("artifact_id") == "D5PT-C51-SOURCES-v1", "C51 source manifest identity mismatch")
    require(sha256(MANIFEST_PATH) == EXPECTED_MANIFEST_SHA256, "C51 source manifest digest mismatch")
    entries = manifest.get("entries")
    require(isinstance(entries, list), "C51 source manifest entries missing")
    by_id = {str(entry.get("source_id")): entry for entry in entries if isinstance(entry, dict)}
    require(set(by_id) == EXPECTED_SOURCE_IDS, "C51 source manifest coverage mismatch")
    for source_id, expected in EXPECTED_SOURCES.items():
        entry = by_id[source_id]
        for field, expected_value in expected.items():
            require(entry.get(field) == expected_value, f"C51 manifest {source_id} {field} mismatch")
        path = SOURCE_DIR / expected["filename"]
        require(path.is_file(), f"C51 source missing: {source_id}")
        require(sha256(path) == expected["sha256"], f"C51 source digest mismatch: {source_id}")

    suitability_page = (SOURCE_DIR / str(by_id["C51-S01"]["filename"])).read_text(encoding="utf-8")
    trading_page = (SOURCE_DIR / str(by_id["C51-S03"]["filename"])).read_text(encoding="utf-8")
    suitability_text = read_docx_text(SOURCE_DIR / str(by_id["C51-S02"]["filename"]))
    trading_text = read_docx_text(SOURCE_DIR / str(by_id["C51-S04"]["filename"]))
    market_data_pdf = SOURCE_DIR / str(by_id["C51-S05"]["filename"])
    market_data_text = read_pdf_text(market_data_pdf)
    require(PREDECESSOR_C13.is_file(), "C51 predecessor C13 missing")
    require(sha256(PREDECESSOR_C13) == EXPECTED_PREDECESSOR_C13_SHA256, "C51 predecessor C13 digest mismatch")
    predecessor_c13 = json.loads(PREDECESSOR_C13.read_text(encoding="utf-8"))

    require("现行有效" in suitability_page, "C51 suitability current-effectiveness marker absent")
    require("现行有效" in trading_page, "C51 trading-rule current-effectiveness marker absent")
    for token in ("个人投资者", "备兑开仓", "认沽期权买入开仓"):
        require(token in suitability_text, f"C51 suitability token missing: {token}")
    for token in ("备兑开仓", "备兑证券", "无效"):
        require(token in trading_text, f"C51 trading-rule token missing: {token}")
    require(market_data_pdf.read_bytes().startswith(b"%PDF"), "C51 market-data file is not a PDF")
    for token in ("期权基础信息文件", "期权交易系统行情文件", "期权收盘价格文件", "期权组合策略文件"):
        require(token in market_data_text, f"C51 market-data interface token missing: {token}")
    require(predecessor_c13.get("status") == "RESEARCH_CANDIDATE_NOT_ACTION_READY", "C51 predecessor C13 status mismatch")
    require(
        predecessor_c13.get("strict_5pct_test", {}).get("status") == "NOT_FEASIBLE_FOR_RETURN_CLAIM",
        "C51 predecessor C13 strict-test status mismatch",
    )

    return {
        "schema_version": "c51_sse_etf_option_collar_scope_screen.v1",
        "artifact_id": "D5PT-C51-v1",
        "as_of": "2026-08-15",
        "status": "NOT_ADMITTED_OPTIONS_FAMILY_NO_NEW_USABLE_ROUTE",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "portfolio_q": 0,
        "scope": "A rule-level, no-selection screen of whether an SSE ETF collar is economically distinct from the previously reviewed covered-call route. It is not a product choice, option-series selection, historical test, account decision or action instruction.",
        "taxonomy": {
            "existing_covered_call_C13": {
                "relationship": "The prior 510300 plus covered call family is the same economic structure. Changing ETF, strike, expiry or venue does not create a new route.",
                "current_disposition": "RETAIN_CLOSED_NOT_TESTABLE_FOR_RETURN_CLAIM",
                "no_reopen_rule": "Do not rename, retune or substitute the covered-call structure into a new candidate."
            },
            "sse_etf_collar": {
                "economic_structure": "Long a single ETF, sell a covered call and buy a put on the same normalized option exposure and expiry. No ETF, option contract, strike, expiry, size, weight or roll calendar is selected here.",
                "distinctness": "A collar changes the payoff by paying for downside protection; it is economically distinct from a covered call, but it still depends on the same option-chain, eligibility, quotation, adjustment, settlement and execution infrastructure.",
                "rule_level_feasibility": "The retained SSE suitability guideline contains covered-opening and corresponding put-buying permission categories, while the trading rule contains covered-security locking and order-validity mechanics. Neither establishes any particular person's eligibility, broker workflow, collar-combination availability or simultaneous-combination execution path."
            },
            "short_option_premium": {
                "current_disposition": "NOT_A_STABLE_FIVE_PERCENT_CANDIDATE",
                "reason": "Premium income is compensation for nonlinear downside and assignment risk rather than a contractual positive return floor. No naked or cash-secured short-option structure is selected, tested or made actionable."
            },
            "cffex_index_option_overlay": {
                "current_disposition": "UNREGISTERED_FUTURE_CLASS_NO_ACTION",
                "boundary": "A possible index-option overlay is not treated as an ETF covered position and is not developed here. It would require separately retained rule evidence and a complete point-in-time contract, quote, execution and account data package before any new protocol could be registered."
            }
        },
        "payoff_boundary": {
            "covered_call_terminal_value": "min(S_T, K_C) + C",
            "collar_terminal_value": "min(S_T, K_C) + max(K_P - S_T, 0) + C - P",
            "collar_compact_terminal_value_only_when_K_P_le_K_C": "max(K_P, min(S_T, K_C)) + C - P",
            "formula_provenance": "Generic derivative payoff algebra only; it is not an SSE rule, market-data-interface or exchange formula.",
            "interpretation": "For normalized same-expiry legs, the general collar formula creates a bounded terminal payoff but does not impose a positive five-percent return floor. The compact max(K_P, min(S_T, K_C)) expression is equivalent only when K_P <= K_C; C51 selects no strikes and therefore uses the general formula. Without a pre-frozen K_P, K_C, C, P and S_0 relationship, no 5% conclusion can be made; even a selected formula would require complete execution and cost accounting.",
            "not_a_return_result": True
        },
        "rule_evidence": {
            "sse_suitability": "The current SSE guideline contains individual-investor conditions and first-level permission categories for covered opening with the underlying held and for corresponding put-buying opening with the underlying held. This is a category-level rule fact only, not an account entitlement.",
            "sse_trading": "The current SSE trading rule contains covered-security lock and order-validity mechanics, and the retained text contains corporate-action adjustment terminology. This does not establish a selected contract, fill, cost, exercise or settlement outcome.",
            "sse_market_data_interface": "The retained SSE interface specification presents option reference, real-time, closing-price and combination-strategy data-file categories. A technical specification neither establishes that a collar is a currently enabled formal combination strategy nor provides a rights-cleared point-in-time historical option chain, bid/ask/depth tape, order/fill record or replay right."
        },
        "strict_hurdle_screen": {
            "hurdle": "Long-run annualized return above 5% as a research objective only, not a promise or guarantee.",
            "contractual_or_rule_based_positive_five_percent_floor_evidenced": False,
            "historical_full_year_or_rolling_five_year_test_performed": False,
            "pre_frozen_contract_selection_and_roll_rule_present": False,
            "admission_result": "fail",
            "reason": "The rule evidence allows a bounded collar definition but supplies neither a five-percent floor nor the complete, rights-cleared historical and execution inputs required to test net outcomes."
        },
        "required_but_missing_before_any_formal_test": [
            "逐日点时点完整的实际 ETF 期权合约主表，包括上市、摘牌、行权价、合约单位、除权调整、停复牌、到期和行权/交收状态。",
            "每个冻结决策时点的逐合约双边报价、五档深度、成交、拒单、部分成交、未成交和官方结算记录。",
            "标的 ETF 的总回报、分配、公司行动、交易状态及与期权调整的可审计映射。",
            "带日期的交易所费率、券商佣金、保证金或备兑锁定、行权与交收成本及账户流程证据。",
            "在查看结果前冻结的标的、到期、行权价、保护腿、换月、无成交和成本规则，以及独立重建全部年度和滚动五年端点。",
            "匿名但可审计的账户权限、券商路由、备兑锁定、组合处理和结算可行性证据；公开规则不能替代这些记录。",
            "若未来主张正式组合策略或同步组合委托，还需保留对应的交易所实施通知、实际可用性和券商工作流证据；本工件不作此主张。"
        ],
        "relationship_to_c48": {
            "c48_status": "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT",
            "effect": "C51 maps a distinct payoff family but does not close C48's point-in-time, total-return/event, availability/version, execution or rights gates."
        },
        "decision": {
            "action": "NO_ACTION",
            "reason": "Do not select an ETF, option contract, strike, expiry, size, broker, calendar or threshold. C51 does not admit a stable-five-percent strategy or any personal execution path."
        },
        "source_control": {
            "manifest": str(MANIFEST_PATH.relative_to(CASE_DIR.parent.parent.parent)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "source_ids": sorted(EXPECTED_SOURCE_IDS),
            "source_hashes": {source_id: EXPECTED_SOURCES[source_id]["sha256"] for source_id in sorted(EXPECTED_SOURCE_IDS)},
            "predecessor_c13": {
                "path": str(PREDECESSOR_C13.relative_to(REPO_ROOT)),
                "sha256": EXPECTED_PREDECESSOR_C13_SHA256,
                "status": predecessor_c13["status"],
                "strict_5pct_test_status": predecessor_c13["strict_5pct_test"]["status"],
            },
        },
        "boundary": "This evidence-bound screen is not a recommendation, return forecast, account-suitability conclusion, portfolio allocation or order instruction."
    }


def markdown(result: dict[str, Any]) -> str:
    missing = "\n".join(f"{index}. {item}" for index, item in enumerate(result["required_but_missing_before_any_formal_test"], start=1))
    return f"""# C51 场内 ETF collar 期权路线：非重复性与数据契约预审

- 截止日：2026-08-15
- 状态：`{result['status']}`；`portfolio_q=0`；当前动作：`NO_ACTION`。
- 范围：本工件只判断 ETF collar 是否与已审备兑认购在经济上不同，并冻结其证据缺口；不选择 ETF、期权合约、行权价、到期日、权重、券商或任何操作。

## 为什么这不是对 C13 的改名

已审的 ETF 备兑认购属于“持有 ETF、卖出相应备兑认购”的同一收益曲线。仅更换 ETF、行权价、到期日或场所，不能成为新的研究路线，也不能重开 C13。

ETF collar 则在持有 ETF 和卖出备兑认购之外，增加同到期的买入认沽保护腿。它改变了风险曲线，因而可以在未来作为独立假设；但目前没有选择任何实际合约或参数。上交所适当性指引保留了备兑开仓和对应数量认沽期权买入开仓的规则类别，上交所交易规则保留了备兑证券锁定、委托有效性和合约调整机制。这些只是规则层面的可定义性，**不能**推定任何个人账户已具备权限、经纪流程可用或委托可以成交。

## 为什么 collar 也不能被称为稳定 5%

对同到期、同单位的抽象腿，备兑认购到期价值可写为 `min(S_T, K_C) + C`，collar 的通用到期价值为 `min(S_T, K_C) + max(K_P - S_T, 0) + C - P`。其中 `S_T` 是到期标的价格，`K_C`、`K_P` 为认购/认沽行权价，`C`、`P` 为相应权利金。只有在 `K_P <= K_C` 时，collar 才可简写为 `max(K_P, min(S_T, K_C)) + C - P`；本工件没有选择任何行权价，因此不采用该带条件的简写作为通用公式。这是通用衍生品到期收益代数，不是上交所规则、市场数据接口或交易所公式。

该结构可以约束到期区间，却不会自动产生正的 5% 回报下限：规则没有预先规定 `K_P`、`K_C`、权利金、成本与初始标的价格之间的关系；保护腿成本、未成交、调整、换月和结算也会改变净结果。短期权收取的权利金同样不是利息或已锁定收益，而是对非线性风险的补偿。因此没有合同或规则层面的 5% 下限，也没有年度或滚动五年净结果测试。

## 数据与执行缺口

{missing}

上交所市场数据接口说明书显示期权基础信息、实时行情、收盘价格和组合策略等字段类别，但该技术说明书不证明 collar 是当前可用的正式组合策略或可同步执行的组合委托，也不是历史数据授权、可回放完整期权链或订单与成交账本。当前 C48 仍是 `NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT`，C51 不改变这一结论。

## 结论

ETF collar 是与备兑认购不同的未来研究族，但目前仅有规则层面的定义，**不具备稳定 5% 的证据，也不具备可用策略准入条件**。C13 不重开；不选择任何 collar 或短期权结构，不产生任何外部操作。
"""


def main() -> int:
    result = build()
    write_atomic(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_atomic(OUTPUT_MD, markdown(result))
    print("C51 artifact build: PASS; route_admission=fail; action=NO_ACTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
