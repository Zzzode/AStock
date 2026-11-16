#!/usr/bin/env python3
"""Build C52, a bounded public-SSE option-history coverage screen.

C52 tests whether publicly accessible SSE materials close the historical data
contract that C51 would require. It intentionally does not test a collar,
select any instrument, or infer a replay right from a public webpage.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c52-sse-etf-option-history-route-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c52_sse_etf_option_history_route_screen_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c52_sse_etf_option_history_route_screen_20260815.md"
EXPECTED_MANIFEST_SHA256 = "92fdb7356454e21c203ea88baf6d3a7fee1d03e7fde576901d2e1ccc50de0c76"
EXPECTED_SOURCES = {
    "C52-S01": {
        "filename": "sse_option_daily_contract_page.html",
        "url": "https://www.sse.com.cn/assortment/options/disclo/preinfo/",
        "sha256": "174776f4d6a0c205565d540b747fca6058a9717753588cd35564eb799c7072e1",
    },
    "C52-S02": {
        "filename": "sse_option_listing_adjustment_page.html",
        "url": "https://www.sse.com.cn/assortment/options/disclo/info/",
        "sha256": "e8d9755ee343ab44724ecfa95a681216a8f564b6e1c2b20a3d369b0a604912cb",
    },
    "C52-S03": {
        "filename": "sse_option_market_price_page.html",
        "url": "https://www.sse.com.cn/assortment/options/price/",
        "sha256": "5b7f88565d943aa1503811b774b98e9d82815e67dc0be0f79669e2fe1b04091e",
    },
    "C52-S04": {
        "filename": "sse_option_information_query_script.js",
        "url": "https://www.sse.com.cn/xhtml/home/2021public/querySearch/search_stockOptionInformation_2021.js",
        "sha256": "d3fe735a30cad061375ce03441522dcbe48b32a899b67b09fee08412a6452eb7",
    },
    "C52-S05": {
        "filename": "sse_20161128_50etf_dividend_option_adjustment_notice.html",
        "url": "https://www.sse.com.cn/assortment/options/guide/c/c_20161128_4207559.shtml",
        "sha256": "a968a1a9a30897a5a1e7c796d3e8a3357c672f694004cd1a047bc88668a1e38d",
    },
    "C52-S06": {
        "filename": "sseinfo_historical_data_product_page.html",
        "url": "https://www.sseinfo.com/services/assortment/historical/",
        "sha256": "dbae0135ca890931f4161f0b9c239029096dddb55015738f0c988fd92005a85f",
    },
}
EXPECTED_SOURCE_IDS = set(EXPECTED_SOURCES)
C48_PATH = CASE_DIR / "analysis" / "c48_current_environment_data_capability_audit_20260815.json"
C49_PATH = CASE_DIR / "analysis" / "c49_official_authorized_data_route_recheck_20260815.json"
C51_PATH = CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.json"
EXPECTED_C48_SHA256 = "dd61020103246458545b3bf1367115529c9285c4a80c07c853f3a3706731f4ce"
EXPECTED_C49_SHA256 = "990a20b9ab5a8d855656b3e642848d55f17b4394f28c07568cdbedfc9f5317b3"
EXPECTED_C51_SHA256 = "114d4ee9795ba94f50a23b3aecd321fe15b8ebdc2decacfb6dc5d1023ff86f1c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_source(source_id: str) -> str:
    return (SOURCE_DIR / EXPECTED_SOURCES[source_id]["filename"]).read_text(encoding="utf-8")


def write_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def build() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest.get("artifact_id") == "D5PT-C52-SOURCES-v1", "C52 source manifest identity mismatch")
    require(sha256(MANIFEST_PATH) == EXPECTED_MANIFEST_SHA256, "C52 source manifest digest mismatch")
    entries = manifest.get("entries")
    require(isinstance(entries, list), "C52 source manifest entries missing")
    by_id = {str(entry.get("source_id")): entry for entry in entries if isinstance(entry, dict)}
    require(set(by_id) == EXPECTED_SOURCE_IDS, "C52 source manifest coverage mismatch")
    for source_id, expected in EXPECTED_SOURCES.items():
        entry = by_id[source_id]
        for field, expected_value in expected.items():
            require(entry.get(field) == expected_value, f"C52 manifest {source_id} {field} mismatch")
        path = SOURCE_DIR / expected["filename"]
        require(path.is_file(), f"C52 source missing: {source_id}")
        require(sha256(path) == expected["sha256"], f"C52 source digest mismatch: {source_id}")

    for path, expected_hash, label in (
        (C48_PATH, EXPECTED_C48_SHA256, "C48"),
        (C49_PATH, EXPECTED_C49_SHA256, "C49"),
        (C51_PATH, EXPECTED_C51_SHA256, "C51"),
    ):
        require(path.is_file(), f"C52 {label} dependency missing")
        require(sha256(path) == expected_hash, f"C52 {label} dependency digest mismatch")
    c48 = json.loads(C48_PATH.read_text(encoding="utf-8"))
    c49 = json.loads(C49_PATH.read_text(encoding="utf-8"))
    c51 = json.loads(C51_PATH.read_text(encoding="utf-8"))

    daily_page = read_source("C52-S01")
    listing_page = read_source("C52-S02")
    market_page = read_source("C52-S03")
    query_script = read_source("C52-S04")
    adjustment_notice = read_source("C52-S05")
    historical_product = read_source("C52-S06")
    day_contract = re.search(r"dayContractParam\s*:\s*\{(?P<body>.*?)\n\s*\},", query_script, re.DOTALL)
    require(day_contract is not None, "C52 daily-contract query object missing")
    day_contract_body = day_contract.group("body")

    for token in ('content="当日合约"', 'pageTitle ="当日合约"'):
        require(token in daily_page, f"C52 daily-contract page marker missing: {token}")
    for token in ("expireDate", "securityId", "SSE_ZQPZ_YSP_GGQQZSXT_XXPL_DRHY_SEARCH_L", "SETTL_PRICE"):
        require(token in query_script, f"C52 daily-contract query token missing: {token}")
    require("adjustDate" not in day_contract_body, "C52 daily-contract query unexpectedly includes adjustDate")
    require("tradeDate" not in day_contract_body, "C52 daily-contract query unexpectedly includes tradeDate")
    for token in ('content="挂牌信息"', "合约新挂、摘牌、调整"):
        require(token in listing_page, f"C52 listing page marker missing: {token}")
    for token in ("adjustDate", "SSE_ZQPZ_YSP_OPTZSXT_ADJUST_INFO_HYXG_SEARCH_L", "SSE_ZQPZ_YSP_OPTZSXT_ADJUST_INFO_HYZP_SEARCH_L", "SSE_ZQPZ_YSP_OPTZSXT_ADJUST_INFO_HYTZ_SEARCH_L"):
        require(token in query_script, f"C52 listing/adjustment query token missing: {token}")
    for token in ('content="行情"', 'pageTitle ="行情"'):
        require(token in market_page, f"C52 market page marker missing: {token}")
    for token in ("2016-11-28", "将于2016年11月29日分红", "所有未到期合约进行相应调整", "合约单位", "合约前结算价", "重新挂牌新的上证50ETF期权合约"):
        require(token in adjustment_notice, f"C52 adjustment-notice token missing: {token}")
    for token in ("股票期权", "快照数据", "逐笔成交", "日K线", "分钟K线", "证券基本信息文件", "业务申请"):
        require(token in historical_product, f"C52 historical-product token missing: {token}")
    require(c48.get("status") == "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT", "C52 C48 status mismatch")
    require(c49.get("status") == "CONDITIONAL_AUTHORIZED_DATA_ROUTE_DISCOVERY_NO_CURRENT_ACCEPTED_DELIVERY", "C52 C49 status mismatch")
    require(c51.get("status") == "NOT_ADMITTED_OPTIONS_FAMILY_NO_NEW_USABLE_ROUTE", "C52 C51 status mismatch")

    return {
        "schema_version": "c52_sse_etf_option_history_route_screen.v1",
        "artifact_id": "D5PT-C52-v1",
        "as_of": "2026-08-15",
        "status": "PUBLIC_SSE_OPTION_SOURCE_ROUTE_INSUFFICIENT_FOR_C51_REPLAY",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "portfolio_q": 0,
        "scope": "A read-only coverage screen of retained public SSE pages and their client-side query implementation. It asks whether those pages close C51's historical data contract; it does not test, select or operate a collar or any other option position.",
        "public_source_findings": {
            "daily_contract_display": {
                "what_is_evidenced": "The SSE page is explicitly labelled '当日合约'. Its retained client query renders contract code, trading code, name, underlying, call/put, exercise price, unit, exercise/delivery/expiry dates, new-listing flag, price limits, prior settlement, adjustment and delisting fields.",
                "captured_query_parameters": ["expireDate", "securityId", "pagination"],
                "historical_as_of_parameter_in_captured_daily_query": False,
                "bounded_interpretation": "The retained public implementation supports a current-day contract view filtered by expiry and underlying. It is not evidence of a complete, immutable historical as-of contract-master archive. This is a statement about the captured query only; it does not claim that no other SSE route could exist."
            },
            "listing_delisting_adjustment_disclosures": {
                "what_is_evidenced": "The SSE '挂牌信息' page presents new-listing, delisting and adjustment sections, and its retained query implementation accepts adjustDate for each of those categories.",
                "usable_for": "Dated, contract-event cross-checks and selected adjustment-event reconstruction.",
                "not_established": "A normalized, complete point-in-time master; immutable versions or available-at history; full lifecycle completeness across every contract and date."
            },
            "current_market_display": {
                "what_is_evidenced": "The retained SSE page is labelled '行情'.",
                "not_established": "A public, date-queryable historical close or settlement panel, a historical bid/ask/depth tape, or an order/fill record."
            },
            "adjustment_event_example": {
                "what_is_evidenced": "The 2016-11-28 SSE notice says a 50ETF distribution would trigger adjustment of unexpired option contracts, including contract unit and prior-settlement adjustments and relisting of new contracts.",
                "usable_for": "An example that corporate-action mapping is economically material and must be retained in any later option lifecycle ledger.",
                "not_established": "A normalized ETF distribution, cash-flow, total-return or investor-settlement ledger."
            },
            "historical_data_product_page": {
                "what_is_evidenced": "The SSE information operator describes a historical-data product covering stock options and categories including snapshots, trades, daily/minute bars and reference files, with a business-application link.",
                "bounded_interpretation": "This identifies a possible future licensed-data category only. It does not prove current written rights, a delivered field set, point-in-time version/available-at coverage, replay rights, account records or C48 closure."
            }
        },
        "coverage_matrix": [
            {
                "required_component": "Point-in-time actual option contract master",
                "public_coverage": "partial_event_evidence_only",
                "finding": "Current daily-contract fields plus dated listing/delisting/adjustment queries can support limited checks, but not a demonstrated complete historical as-of master.",
                "formal_gate_closed": False
            },
            {
                "required_component": "Historical option close/settlement and decision-time bid/ask/depth panel",
                "public_coverage": "not_demonstrated",
                "finding": "The retained public market page is current-market labelled; the retained daily-contract query has no captured historical as-of parameter. No complete historical quote/depth/fill panel is evidenced.",
                "formal_gate_closed": False
            },
            {
                "required_component": "ETF distribution, option-adjustment and lifecycle mapping",
                "public_coverage": "partial_event_evidence_only",
                "finding": "Dated adjustment records can inform a manual cross-check, but they are not a normalized total-return, cash-flow or immutable timing ledger.",
                "formal_gate_closed": False
            },
            {
                "required_component": "Historical data rights, available-at/version chain and independent replay rights",
                "public_coverage": "conditional_future_product_category_only",
                "finding": "The historical-data product page is not a written delivery, usage right or accepted data contract.",
                "formal_gate_closed": False
            },
            {
                "required_component": "Broker/account eligibility, order state, fills, fees, settlement and cash movements",
                "public_coverage": "absent",
                "finding": "None of the retained public sources is an account, broker-routing, execution-cost or settlement record.",
                "formal_gate_closed": False
            }
        ],
        "strict_hurdle_boundary": {
            "hurdle": "Long-run annualized return above 5% is a research objective only, not a promise or guarantee.",
            "historical_net_total_return_test_performed": False,
            "contractual_or_rule_based_positive_five_percent_floor_evidenced": False,
            "reason": "Public source coverage does not establish the history, total-return/event, execution/cost, account or rights inputs needed to calculate a net collar outcome."
        },
        "relationship_to_existing_controls": {
            "c48_status": c48["status"],
            "c49_status": c49["status"],
            "c51_status": c51["status"],
            "effect": "C52 adds source-level precision to C51's historical-data gap. It does not close C48, alter C49's conditional future-route conclusion, reopen C13, or admit C51."
        },
        "decision": {
            "state": "NO_PUBLIC_REPLAY_OR_ADMISSION_PATH",
            "action": "NO_ACTION",
            "reason": "Do not select an ETF, contract, strike, expiry, size, broker, calendar or threshold. Any future formal C51 study still requires a user-authorized, written-rights delivery plus accepted point-in-time, total-return/event and execution evidence."
        },
        "source_control": {
            "manifest": str(MANIFEST_PATH.relative_to(CASE_DIR.parent.parent.parent)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "source_ids": sorted(EXPECTED_SOURCE_IDS),
            "source_hashes": {source_id: EXPECTED_SOURCES[source_id]["sha256"] for source_id in sorted(EXPECTED_SOURCE_IDS)},
            "dependencies": {
                "c48": {"path": str(C48_PATH.relative_to(CASE_DIR.parent.parent.parent)), "sha256": EXPECTED_C48_SHA256, "status": c48["status"]},
                "c49": {"path": str(C49_PATH.relative_to(CASE_DIR.parent.parent.parent)), "sha256": EXPECTED_C49_SHA256, "status": c49["status"]},
                "c51": {"path": str(C51_PATH.relative_to(CASE_DIR.parent.parent.parent)), "sha256": EXPECTED_C51_SHA256, "status": c51["status"]},
            },
        },
        "boundary": "This is a public-source coverage assessment, not a product recommendation, return forecast, historical-performance result, account-suitability conclusion, portfolio allocation or order instruction."
    }


def markdown(result: dict[str, Any]) -> str:
    component_labels = {
        "Point-in-time actual option contract master": "逐时点实际期权合约主表",
        "Historical option close/settlement and decision-time bid/ask/depth panel": "历史收盘/结算及决策时点双边报价/深度面板",
        "ETF distribution, option-adjustment and lifecycle mapping": "ETF 分配、期权调整与生命周期映射",
        "Historical data rights, available-at/version chain and independent replay rights": "历史数据权利、可得时点/版本链与独立回放权利",
        "Broker/account eligibility, order state, fills, fees, settlement and cash movements": "券商/账户资格、委托状态、成交、费用、结算与现金流",
    }
    coverage_labels = {
        "partial_event_evidence_only": "仅有部分事件证据",
        "not_demonstrated": "未被证明",
        "conditional_future_product_category_only": "仅为条件性的未来产品类别",
        "absent": "缺失",
    }
    finding_labels = {
        "Current daily-contract fields plus dated listing/delisting/adjustment queries can support limited checks, but not a demonstrated complete historical as-of master.": "当日合约字段与带日期的挂牌、摘牌、调整查询可支持有限核对，但不能证明完整的历史时点主表。",
        "The retained public market page is current-market labelled; the retained daily-contract query has no captured historical as-of parameter. No complete historical quote/depth/fill panel is evidenced.": "已归档行情页标示为当前行情，已捕获的当日合约查询没有历史时点参数；没有完整的历史报价、深度或成交面板证据。",
        "Dated adjustment records can inform a manual cross-check, but they are not a normalized total-return, cash-flow or immutable timing ledger.": "带日期调整记录可用于人工勾稽，但不是标准化的总回报、现金流或不可变时点账本。",
        "The historical-data product page is not a written delivery, usage right or accepted data contract.": "历史数据产品页面不是书面交付、使用权利或已验收的数据契约。",
        "None of the retained public sources is an account, broker-routing, execution-cost or settlement record.": "已归档的公开来源都不是账户、券商路由、执行成本或结算记录。",
    }
    rows = "\n".join(
        f"| {component_labels[row['required_component']]} | {coverage_labels[row['public_coverage']]} | {finding_labels[row['finding']]} | {'否' if not row['formal_gate_closed'] else '是'} |"
        for row in result["coverage_matrix"]
    )
    return f"""# C52 上交所 ETF 期权公开历史数据路线复核

- 截止日：2026-08-15
- 状态：`{result['status']}`；`portfolio_q=0`；当前动作：`NO_ACTION`。
- 范围：只核对已归档的上交所公开页面和其客户端查询实现，判断它们能否补齐 C51 的历史数据契约；不测试、不选择也不操作任何 collar 或期权头寸。

## 公开页面实际能证明什么

1. **当日合约。** 页面明确标示“当日合约”。已归档客户端查询可展示合约编码、交易代码、标的、认购/认沽、行权价、合约单位、行权/交收/到期日、价格限制、前结算价、调整与摘牌等字段；其已捕获的查询参数是 `expireDate`、`securityId` 和分页，没有历史 `as_of`、`adjustDate` 或 `tradeDate` 参数。因此它能支持当前页面字段核对，**不能**证明存在完整、不可变的历史时点合约主表。本结论仅针对本次保留的公开查询，不声称不存在任何其他交易所渠道。
2. **挂牌、摘牌和调整。** “挂牌信息”页面显示合约新挂、摘牌、调整；其查询实现对三个类别均接受 `adjustDate`。这可用于有日期的合约事件勾稽，但不能构成全覆盖的时点主表、版本链或可得时点记录。
3. **行情。** 已归档页面标示为“行情”，但本批公开来源没有证明可按日期查询的历史收盘/结算面板，也没有历史双边报价、深度、委托状态或成交记录。
4. **调整事件。** 2016-11-28 的 50ETF 期权调整公告说明，ETF 分红会影响未到期期权合约、合约单位、前结算价及重新挂牌。这证明事件映射必须进入未来账本；它不是 ETF 总回报、现金流、投资者结算或版本化事件库。
5. **历史数据产品。** 上证所信息的产品页列出股票期权、快照、逐笔成交、日/分钟 K 线和基础信息文件，并提供业务申请入口。它只定位了未来可能的受权数据类别，不能推定当前已获书面权利、已交付字段、可回放权利或账户执行记录。

## C51 数据契约覆盖矩阵

| 所需组成 | 公开覆盖 | 本次结论 | 正式闸门闭合 |
|---|---|---|---|
{rows}

## 对 5% 研究目标与 C51 的含义

没有执行任何净总回报计算，也没有规则或合同层面的正 5% 下限。即使公开页面可核验部分合约字段或调整事件，也不能替代带权利的历史期权链、ETF 总回报/事件账本、决策时点报价与未成交处理、成本/结算和账户记录。故 C52 不改变 C48：当前环境仍没有正式历史研究路径；也不改变 C49 或 C51 的 `NO_ACTION` 结论。

## 结论

公开上交所材料适合做合同字段和个别事件的来源核对，**不足以重建 C51 的可执行历史表现，更不足以准入策略**。不选择 ETF、合约、行权价、到期日、规模、券商、日历或阈值。只有用户授权的书面数据交付通过独立来源验收后，才可另行讨论冻结新的正式研究协议。
"""


def main() -> int:
    result = build()
    write_atomic(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_atomic(OUTPUT_MD, markdown(result))
    print("C52 artifact build: PASS; public-replay-route=fail; action=NO_ACTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
