#!/usr/bin/env python3
"""Build C50, a bounded SSE general-repo yield-floor research screen.

The screen verifies product mechanics and one dated public fixing.  It is not
a historical performance test, a personal-account entitlement decision, or a
trade instruction.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c50-sse-general-repo-screen-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c50_sse_general_repo_yield_floor_screen_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c50_sse_general_repo_yield_floor_screen_20260815.md"

EXPECTED_SOURCES = {
    "C50-S01": {
        "filename": "sse_general_repo_personal_inverse_participation.html",
        "sha256": "c88c6551cf434da52382c322ce96e1c880c9e74be595ac8e36fe86fbef0fb4d5",
    },
    "C50-S02": {
        "filename": "sse_general_repo_trading_guideline.html",
        "sha256": "b5a14f9d76076a8c03538f9a6df935c60d081ef9ae4737d0dc633cd09fa14380",
    },
    "C50-S03": {
        "filename": "sse_204001_curve_page_20260814.html",
        "sha256": "ceae0b84f02283dab66f16ab6855154d6f1e6c27505123ce1013efd28b20f19a",
    },
    "C50-S04": {
        "filename": "sse_204001_fixing_query_20260814.jsonp",
        "sha256": "74d55edad71e976d01cdd7891844fe2f4bc1e37602457ee08b5f70726cdf62a0",
    },
    "C50-S05": {
        "filename": "sse_general_repo_trading_guideline.docx",
        "sha256": "b148bd3ce4e9fae7bce6d4328cfa4caf95999e068fa29f03d9a65f74550d1844",
    },
}


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


def parse_jsonp(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    match = re.fullmatch(r"callback\((.*)\)", raw, flags=re.DOTALL)
    require(match is not None, "C50 fixing response is not expected JSONP")
    payload = json.loads(match.group(1))
    require(isinstance(payload, dict), "C50 fixing response is not an object")
    return payload


def write_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def build() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest.get("artifact_id") == "D5PT-C50-SOURCES-v1", "C50 source manifest identity mismatch")
    entries = manifest.get("entries")
    require(isinstance(entries, list), "C50 source manifest entries missing")
    by_id = {str(entry.get("source_id")): entry for entry in entries if isinstance(entry, dict)}
    require(set(by_id) == set(EXPECTED_SOURCES), "C50 source manifest coverage mismatch")
    for source_id, expected in EXPECTED_SOURCES.items():
        entry = by_id[source_id]
        path = SOURCE_DIR / expected["filename"]
        require(entry.get("filename") == expected["filename"], f"C50 source filename mismatch: {source_id}")
        require(path.is_file(), f"C50 source missing: {source_id}")
        require(entry.get("sha256") == expected["sha256"], f"C50 manifest digest mismatch: {source_id}")
        require(sha256(path) == expected["sha256"], f"C50 raw digest mismatch: {source_id}")

    participation_text = (SOURCE_DIR / EXPECTED_SOURCES["C50-S01"]["filename"]).read_text(encoding="utf-8")
    guideline_text = read_docx_text(SOURCE_DIR / EXPECTED_SOURCES["C50-S05"]["filename"])
    query = parse_jsonp(SOURCE_DIR / EXPECTED_SOURCES["C50-S04"]["filename"])
    result = query.get("result")
    require(isinstance(result, list) and len(result) == 5, "C50 expected five SSE fixing observations")
    latest = result[0]
    require(isinstance(latest, dict), "C50 latest fixing is malformed")
    require(latest.get("TRADE_DATE") == "2026-08-14", "C50 latest fixing date mismatch")
    rate_1day_pct = float(latest["RATE_1DAY"])
    rate_7day_pct = float(latest["RATE_7DAY"])
    require(rate_1day_pct == 1.391 and rate_7day_pct == 1.414, "C50 latest fixing value mismatch")
    require("个人投资者可以作为逆回购方" in participation_text, "C50 personal inverse-repo wording absent")
    require("本所暂免债券通用质押式回购交易费用" in participation_text, "C50 exchange-fee wording absent")
    for token in (
        "通用回购的期限分为",
        "204***",
        "一次成交、两次结算",
        "购回价=100元",
        "实际占款天数",
        "逐日发布相关通用回购品种的定盘利率",
    ):
        require(token in guideline_text, f"C50 guideline token missing: {token}")

    one_day_fraction = rate_1day_pct / 100 / 365
    return {
        "schema_version": "c50_sse_general_repo_yield_floor_screen.v1",
        "artifact_id": "D5PT-C50-v1",
        "as_of": "2026-08-15",
        "status": "NOT_ADMITTED_NO_STABLE_5PCT_YIELD_FLOOR",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "portfolio_q": 0,
        "scope": "A primary-source mechanism and dated-yield-floor pre-screen for SSE general pledged reverse repo. It does not compute a multi-year result, select a broker, verify an account, or authorize an external action.",
        "economic_mechanism": {
            "route": "SSE general pledged reverse repo as the funding side",
            "distinct_from_prior_routes": "A short-term collateralized funding-rate mechanism, not an ETF allocation, direct-credit ladder, commodity trend, commodity calendar curve, Treasury cash-futures basis, or covered-call route.",
            "official_mechanics_verified": [
                "SSE states that an individual investor may participate as the reverse-repo funding side.",
                "SSE describes matching and multilateral net settlement for the general-repo mechanism.",
                "SSE states that its general-repo transaction fee is temporarily waived.",
                "The current guideline lists standardized terms including one day and identifies general-repo codes with the 204 prefix.",
                "The guideline describes one trade with two settlement legs and a maturity amount based on the quoted annual rate and actual days.",
                "SSE publishes a daily fixing calculated from transaction prices and volumes; a no-trade fixing carries forward the prior trading day's fixing."
            ],
            "personal_access_boundary": "The exchange-level statement that individuals may participate does not verify any particular brokerage account, permission, route, fee schedule, order acceptance, fill, or settlement outcome."
        },
        "dated_official_observation": {
            "source_date": "2026-08-14",
            "source_displayed_timestamp": "2026-08-14 22:30:00",
            "instrument": "204001 / one-day general repo fixing",
            "quoted_annualized_rate_pct": rate_1day_pct,
            "same_response_rate_7day_pct": rate_7day_pct,
            "same_response_rate_7day_label": "The separate RATE_7DAY field returned by the same SSE public query; it is not labeled as an 204001 quote.",
            "one_day_interest_fraction_before_broker_specific_costs": one_day_fraction,
            "one_day_interest_pct_before_broker_specific_costs": one_day_fraction * 100,
            "interpretation": "The 1.391% figure is an annualized quote for a one-day term, not a one-year realized portfolio return."
        },
        "strict_hurdle_screen": {
            "hurdle": "A research target above 5% annualized, not a promised or guaranteed outcome.",
            "current_official_one_day_quote_below_5pct": rate_1day_pct < 5.0,
            "current_official_same_response_rate_7day_below_5pct": rate_7day_pct < 5.0,
            "contractual_or_rule_based_5pct_floor_evidenced": False,
            "historical_full_year_or_rolling_five_year_test_performed": False,
            "admission_result": "fail",
            "reason": "A market-determined daily fixing below 5% at the dated observation and the absence of any evidenced yield floor mean this route cannot be presented as a stable 5% yield-floor strategy. The limited public observation also cannot establish a formal historical return test."
        },
        "required_but_missing_before_any_formal_test": [
            "每个决策日均有完整、权利明确的逐时点定盘利率、报价、委托状态与结算历史。",
            "在查看利率前冻结期限、日历或阈值规则，并明确闲置资金、节假日、未成交和结算处理。",
            "带日期的券商路径、账户权限、费税、委托受理、成交与结算记录；交易所费率暂免说明不是完整的个人成本账本。",
            "每项历史输入均有发布时间、可得时间、版本/修订、原始哈希和字段字典证据。",
            "独立重建完整自然年和滚动五年窗口，并完成连续的前瞻纸面观察。"
        ],
        "relationship_to_c48": {
            "c48_status": "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT",
            "effect": "C50 adds a distinct mechanism screen but does not close C48's point-in-time, availability/version, execution, and rights gates."
        },
        "decision": {
            "action": "NO_ACTION",
            "reason": "Do not select a repo code, broker, term, schedule, or transaction. C50 is not admitted as a usable strategy and cannot satisfy the requested stable-5% characterization."
        },
        "source_control": {
            "manifest": str(MANIFEST_PATH.relative_to(CASE_DIR.parent.parent.parent)),
            "source_ids": list(EXPECTED_SOURCES),
            "source_hashes": {source_id: item["sha256"] for source_id, item in EXPECTED_SOURCES.items()},
        },
        "boundary": "This screen is an evidence-bound research artifact. It does not provide a yield promise, allocation, account recommendation, personal suitability conclusion, or order instruction."
    }


def markdown(result: dict[str, Any]) -> str:
    observation = result["dated_official_observation"]
    screen = result["strict_hurdle_screen"]
    missing = "\n".join(f"{index}. {item}" for index, item in enumerate(result["required_but_missing_before_any_formal_test"], start=1))
    return f"""# C50 上交所债券通用质押式逆回购：收益下限路线预审

- 截止日：2026-08-15
- 状态：`{result['status']}`；`portfolio_q=0`；当前动作：`NO_ACTION`。
- 范围：这是一个机制与收益下限预审，不是历史回测、账户核验、产品选择或外部操作指令。

## 已核实的机制

该路线以个人作为通用质押式逆回购的资金融出方为研究对象。上交所页面明确说明个人可作为逆回购方参与，并说明通用回购采用匹配成交和多边净额结算；交易所层面的通用回购交易费暂免。现行指引列出 1 天等标准期限、`204***` 通用回购代码、一次成交两次结算，以及按年收益率与实际占款天数计算到期结算金额的框架；上交所逐日发布由当日成交价格与成交量计算的定盘利率。

这些事实只说明一种不同于 ETF、股票、期货趋势、期限结构、现券—期货基差和备兑期权的短期资金利率机制。交易所层面的个人参与说明**不等于**任何券商账户已经开通、可接受委托、可成交或已完成结算。

## 带日期的收益下限检查

上交所公开查询对 2026-08-14 返回的 204001 一天期定盘利率为 **{observation['quoted_annualized_rate_pct']:.3f}%**。同一公开响应中的独立 `RATE_7DAY` 字段为 **{observation['same_response_rate_7day_pct']:.3f}%**，但该响应并未将其标注为 204001 报价。一天期数字是年化报价，不是一年的已实现组合回报；按指引的天数框架，它对应一天约 **{observation['one_day_interest_pct_before_broker_specific_costs']:.6f}%** 的单位资金利息，尚未纳入任何券商特定成本。

研究目标是长期年化高于 5%，并非收益承诺。该观察日 204001 一天期官方年化报价低于 5%，同一响应的独立 `RATE_7DAY` 字段也低于 5%，且现有规则材料没有提供 5% 的合同或规则下限。因此，不能把逆回购表述为“稳定 5%”的收益下限策略；更不能把单日年化报价写成年度结果。

## 为什么不能进入正式策略测试

{missing}

当前环境的 C48 仍是 `NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT`。C50 没有改变这一结论：它只增加了一个独立机制的公开一手预审，并未补齐逐时点、版本、完整成交与个人执行证据。

## 结论

该路线具备可继续尽调的机制事实，但**不具备稳定 5% 收益下限，也没有通过可用策略准入**。不选择回购代码、期限、券商、日历或阈值，不生成任何外部操作。
"""


def main() -> int:
    result = build()
    write_atomic(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_atomic(OUTPUT_MD, markdown(result))
    print("C50 artifact build: PASS; route_admission=fail; action=NO_ACTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
