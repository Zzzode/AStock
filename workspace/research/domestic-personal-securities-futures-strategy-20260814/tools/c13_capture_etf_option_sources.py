#!/usr/bin/env python3
"""Capture primary C13 ETF-option material and build a feasibility record.

The C13 candidate is deliberately a research-only covered-call protocol.  The
tool does not reach an account, seek trading permission, submit an instruction,
or create a position.  Its output records why rules alone cannot establish a
strict annual-return result without actual-contract and execution evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c13-sse-etf-option-rules-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
OUTPUT_JSON = CASE_DIR / "analysis" / f"c13_etf_option_covered_call_feasibility_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"c13_etf_option_covered_call_feasibility_{DATE_TAG}.md"
SOURCE_FREEZE_SCHEMA = "research_source_freeze_control.v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (C13 research evidence capture; read-only)",
    "Accept": "text/html,application/pdf,*/*;q=0.8",
}

DOCUMENTS: tuple[dict[str, str], ...] = (
    {
        "filename": "sse_300etf_option_listing_terms_20191217.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "Notice on listing SSE CSI 300 ETF options and contract terms",
        "document_date": "2019-12-17",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250611_10781547.shtml",
        "format": "html",
        "purpose": "Underlying identification, contract multiplier, expiry and physical-delivery mechanics.",
    },
    {
        "filename": "sse_stock_option_investor_suitability_20170628.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE stock option pilot investor-suitability guidance",
        "document_date": "2017-06-28",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781453.shtml",
        "format": "html",
        "purpose": "Account-specific suitability, assessment and permission boundary.",
    },
    {
        "filename": "sse_stock_option_trial_trading_rules_20150109.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE stock option pilot trading rules",
        "document_date": "2015-01-09",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781448.shtml",
        "format": "html",
        "purpose": "Current legal and exchange-rule framework for option dealing and investor access.",
    },
    {
        "filename": "sse_300etf_option_adjustment_20260116.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE CSI 300 ETF option contract-adjustment notice",
        "document_date": "2026-01-16",
        "url": "https://www.sse.com.cn/assortment/options/disclo/update/c/c_20260116_10805396.shtml",
        "format": "html",
        "purpose": "Dated example of corporate-action adjustment and covered-reserve operational risk.",
    },
    {
        "filename": "sse_option_market_data_file_spec_202601.pdf",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE market-data file exchange interface specification",
        "document_date": "2026-01-01",
        "url": "https://www.sse.com.cn/services/tradingtech/development/c/10805084/files/fca415e1f54944db9bd41b6d7ed3fb62.pdf",
        "format": "pdf",
        "purpose": "Evidence that actual-option data must preserve contract lifecycle, adjustment, status, price, settlement and quote fields.",
    },
    {
        "filename": "sse_option_price_page_20260815.html",
        "publisher": "Shanghai Stock Exchange",
        "title": "SSE option price page",
        "document_date": "2026-08-15",
        "url": "https://www.sse.com.cn/assortment/options/price/",
        "format": "html",
        "purpose": "Current public-page route observation, not an entitled actual-contract historical package.",
    },
    {
        "filename": "510300_product_summary_20251124.pdf",
        "publisher": "Shanghai Stock Exchange / Huatai-PineBridge Fund Management",
        "title": "Huatai-PineBridge CSI 300 ETF product summary",
        "document_date": "2025-11-24",
        "url": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2025-11-24/510300_20251124_9WR7.pdf",
        "format": "pdf",
        "purpose": "Dated underlying-ETF identity and product-document boundary.",
    },
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _record(path: Path) -> dict[str, Any]:
    return {"path": _repo_relative(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == content:
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_text(path: Path, value: str) -> None:
    _atomic_write(path, value.encode("utf-8"))


def _validate(content: bytes, descriptor: dict[str, str]) -> None:
    if len(content) < 500:
        raise ValueError(f"source unexpectedly short: {descriptor['filename']}")
    if descriptor["format"] == "pdf" and not content.startswith(b"%PDF"):
        raise ValueError(f"source is not a PDF: {descriptor['filename']}")
    if descriptor["format"] == "html":
        head = content[:5000].decode("utf-8", errors="ignore").lower()
        if "safeline_bot_challenge" in head or "<title>web 应用防火墙" in head:
            raise ValueError(f"WAF response cannot be retained: {descriptor['filename']}")


def _runtime_provenance() -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, capture_output=True, check=True
        )
        commit = result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "not_available"
    return {
        "git_commit_at_runtime": commit,
        "script_path": _repo_relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _capture() -> None:
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C13 source batch already exists; use --rebuild-derived or --verify-only")
    staged: list[tuple[Path, bytes, dict[str, Any]]] = []
    times: list[str] = []
    for descriptor in DOCUMENTS:
        response = requests.get(descriptor["url"], headers=HEADERS, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"source download failed {response.status_code}: {descriptor['url']}")
        _validate(response.content, descriptor)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        staged.append(
            (
                RAW_DIR / descriptor["filename"],
                response.content,
                {
                    **descriptor,
                    "retrieved_at": retrieved_at,
                    "http_status": response.status_code,
                    "content_type": response.headers.get("content-type", "not_reported"),
                },
            )
        )
        times.append(retrieved_at)
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    for path, content, _ in staged:
        _atomic_write(path, content)
    files = [
        {
            **_record(path),
            **metadata,
            "capture_note": (
                "Read-only current official documentation capture. It does not establish historic availability, "
                "an entitled actual-contract archive, bid/ask history, fill, account permission, allocation, holding, or action."
            ),
        }
        for path, _, metadata in staged
    ]
    manifest = {
        "schema_version": "c13_sse_etf_option_source_manifest.v1",
        "case_id": CASE_DIR.name,
        "capture_batch": RAW_DIR.name,
        "captured_at": min(times),
        "protocol_status": "research_candidate_not_action_ready",
        "source_quality": "primary_official_option_rules_and_market_data_interface_documentation",
        "purpose": "C13 first-party option contract/rule/data-interface evidence. It supports a feasibility review only; no return replay or action is generated.",
        "files": files,
        "limitations": [
            "The captured contract and rule documents are dated rules, not an individual account eligibility decision or an execution record.",
            "The market-data interface specification documents fields and delivery mechanics; it does not make this capture an entitled historical actual-contract package.",
            "The current public price-page observation does not establish a complete point-in-time history of every listed/adjusted contract, bid/ask, depth, settlement, fee, tax, or fill.",
            "No return, allocation, holding, external instruction, or guarantee is created from this batch.",
        ],
        "source_freeze": {
            "schema_version": SOURCE_FREEZE_SCHEMA,
            "seal_status": "case_local_hash_control",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_files": [_record(path) for path, _, _ in staged],
            "runtime_provenance": _runtime_provenance(),
            "boundary": "Local file hashes reveal mismatch only; they do not establish external notarization, historic publication timing, entitlement, personal permission, holder outcome, or execution validation.",
        },
    }
    _write_json(MANIFEST_JSON, manifest)
    rows = [
        "# C13 SSE ETF Option Source Manifest",
        "",
        f"- Batch: `{manifest['capture_batch']}`",
        f"- Capture time: `{manifest['captured_at']}`",
        "- Method: anonymous, read-only HTTPS requests to named SSE option and fund documents.",
        "- Boundary: this documents rules and data-field requirements, not historical actual-contract access or an execution result.",
        "",
        "| File | Date | SHA-256 |",
        "|---|---|---|",
    ]
    for item in files:
        rows.append(f"| {Path(item['path']).name} | {item['document_date']} | `{item['sha256']}` |")
    rows.extend(
        [
            "",
            "`tools/verify_source_manifests.py` verifies every retained raw-file hash. The frozen material cannot validate an individual account, a full historical contract chain, bid/ask availability, a fill, or a return result.",
            "",
        ]
    )
    _write_text(MANIFEST_MD, "\n".join(rows))


def _verify_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.is_file():
        raise FileNotFoundError(f"C13 source manifest is absent: {MANIFEST_JSON}")
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    files = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(files, list) or len(files) != len(DOCUMENTS) or not isinstance(frozen, list):
        raise ValueError("C13 manifest does not have the expected file/freeze records")
    names = {Path(str(item.get("path"))).name for item in files}
    if names != {item["filename"] for item in DOCUMENTS}:
        raise ValueError("C13 source names differ from capture definition")
    frozen_by_path = {str(item.get("path")): item for item in frozen}
    if set(frozen_by_path) != {str(item.get("path")) for item in files}:
        raise ValueError("C13 source-freeze paths differ from manifest paths")
    for item in files:
        path = (REPO_ROOT / str(item["path"])).resolve()
        if not path.is_file() or path.stat().st_size != int(item["bytes"]) or _sha256(path) != item["sha256"]:
            raise ValueError(f"C13 raw source mismatch: {path}")
        frozen_item = frozen_by_path[str(item["path"])]
        if {key: item.get(key) for key in ("path", "bytes", "sha256")} != {key: frozen_item.get(key) for key in ("path", "bytes", "sha256")}:
            raise ValueError(f"C13 frozen record mismatch: {path}")
    return manifest


def _build() -> dict[str, Any]:
    manifest = _verify_manifest()
    payload = {
        "artifact_id": "DPSFS-C13-ETF-OPTION-CC-v1",
        "as_of": "2026-08-15",
        "status": "RESEARCH_CANDIDATE_NOT_ACTION_READY",
        "portfolio_q": 0,
        "candidate": {
            "underlying_etf": {"code": "510300", "name": "Huatai-PineBridge CSI 300 ETF"},
            "option_product": "SSE CSI 300 ETF call options",
            "mechanism": "备兑认购研究协议：只能以经纪商确认的备兑开仓方式、针对当期精确可交割 ETF 数量卖出认购；不得卖出裸认购或认沽。",
            "exchange_terms_from_frozen_listing_notice": {
                "contract_multiplier": "公司行动调整前为 10,000 份 ETF",
                "expiry_months": "当月、下月及随后两个季月",
                "exercise": "欧式，到期日行权",
                "settlement": "实物交割，除非交易所规则另有规定",
                "standard_expiry": "到期月份第四个星期三；遇休市按规则顺延",
            },
        },
        "fixed_research_protocol": {
            "selection": "固定标的仅为 510300，期权仅限上交所挂钩该 ETF 的沪深300ETF认购期权；不得事后在 ETF、行权价、到期日、交易所或期权品种之间替换。",
            "formation_gate": [
                "操作者独立确认当前适当性、权限等级、账户路由和经纪商备兑开仓功能；公开规则不能替代账户确认。",
                "当期交易所合约记录须证明精确合约、调整后单位、行权价、到期日、交易状态与交割条款。",
                "经纪商能够锁定精确的可交割 ETF 数量作为备兑备用证券；不允许裸卖或以保证金替代备兑。",
                "留存带时间戳的买卖报价、深度、交易状态、经纪商费税表和结算日历；任一字段缺失即 NO_ACTION。",
            ],
            "series_rule": "上一标准到期日完成结算后，检查当期交易所合约清单；在未调整的下月认购中，选择行权价不低于前一日 ETF 收盘价的最低挂牌行权价。没有合格存续合约，或公司行动改变交割物时，记录 NO_ACTION，不得改用其他规则。",
            "quantity_rule": "经纪商锁定的每一份当前精确合约单位的可交割 ETF，仅对应一张备兑认购；不得超过经纪商确认的备兑数量。",
            "order_rule": "仅在备兑锁定和报价质量门槛通过后使用限价委托。部分成交或未成交均保留为未完成状态，不得在研究中视为完成卖出。",
            "expiry_and_adjustment_rule": "在交易所最后交易／到期日前，以及每次标的分配或合约调整公告后，逐项核对合约代码、单位、行权价、交割物锁定、交收日和经纪商持仓状态。核对失败即停止该候选，不得虚构换月。",
            "forbidden": [
                "uncovered_call",
                "short_put",
                "assumed_broker_permission",
                "assumed_fill_or_quote",
                "synthetic_continuous_option_chain",
                "post_hoc_contract_or_strike_selection",
                "external_order_or_action",
            ],
        },
        "strict_5pct_test": {
            "status": "NOT_FEASIBLE_FOR_RETURN_CLAIM",
            "hurdle": 0.05,
            "definition": "每个完整自然年的净结果及每个滚动五年的年化净结果均须不低于 5%；任一实际合约或执行输入缺失即不通过准入门槛。",
            "required_input": [
                "point_in_time_actual_contract_master_with_adjustments_and_lifecycle",
                "historical_option_bid_ask_depth_trades_and_official_settlement_by_contract",
                "underlying_total_return_distribution_and_trading_status_history",
                "dated_exchange_and_broker_fee_tax_margin_and_covered_reservation_rules",
                "execution_state_and_partial_fill_evidence",
                "account_permission_and_settlement_feasibility_evidence",
                "pre_frozen_replay_protocol_and_independent_audit",
            ],
            "observed_source_scope": "冻结的上交所材料确立了合约／规则机制与数据字段要求，但未提供所需的完整时点正确实际合约和执行数据包。",
            "decision": "不计算年度或滚动收益。按当前证据，该候选不能进入严格 5% 策略或个人操作。",
        },
        "risk_register": [
            "underlying_equity_drawdown",
            "upside_cap_and_opportunity_cost",
            "option_assignment_and_physical_delivery",
            "contract_adjustment_and_changed_multiplier",
            "liquidity_spread_depth_and_no_fill",
            "account_permission_and_broker_process",
            "settlement_and_corporate_action_timing",
            "model_selection_and_backtest_data_gap",
        ],
        "source_manifest": {
            "path": _repo_relative(MANIFEST_JSON),
            "sha256": _sha256(MANIFEST_JSON),
            "capture_batch": manifest["capture_batch"],
        },
        "allowed_interpretation": "这是受来源约束的可行性与规则设计记录，不能证明稳定收益、预测、适当性、配置、持有、经纪商指令或外部行动。",
    }
    _write_json(OUTPUT_JSON, payload)
    _write_text(OUTPUT_MD, _render(payload))
    return payload


def _render(payload: dict[str, Any]) -> str:
    candidate = payload["candidate"]
    protocol = payload["fixed_research_protocol"]
    test = payload["strict_5pct_test"]
    gates = "\n".join(f"{index}. {item}" for index, item in enumerate(protocol["formation_gate"], start=1))
    needed = "\n".join(f"- `{item}`" for item in test["required_input"])
    return f"""# C13 沪深300 ETF 备兑认购期权：可行性与固定规则 — 2026-08-15

- 工件：`{payload['artifact_id']}`；状态：**`{payload['status']}`**；`portfolio_q=0`。
- 标的：`{candidate['underlying_etf']['code']}` {candidate['underlying_etf']['name']}，对应上交所沪深300 ETF 认购期权。
- 这是一条备兑认购期权的研究路径，不是现在的交易指令，也不是稳定 5% 回报的证明。

## 经一手规则确认的机械约束

- 上市通知列明标准合约单位为 `{candidate['exchange_terms_from_frozen_listing_notice']['contract_multiplier']}`，到期月份为 `{candidate['exchange_terms_from_frozen_listing_notice']['expiry_months']}`，采用 `{candidate['exchange_terms_from_frozen_listing_notice']['exercise']}` 与 `{candidate['exchange_terms_from_frozen_listing_notice']['settlement']}`。
- 除息等公司行动会调整未到期合约的代码、行权价和合约单位；被冻结的 2026-01-16 公告说明，备兑持仓也可能需要补足调整后的交割备用证券，否则有强行平仓风险。
- 期权权限、适当性、账户路由、交易状态和经纪商的备兑流程均是逐账户条件，不能从公开规则推定。

## 冻结的研究操作逻辑

{gates}

- 系列选择：{protocol['series_rule']}
- 数量：{protocol['quantity_rule']}
- 委托：{protocol['order_rule']}
- 到期与调整：{protocol['expiry_and_adjustment_rule']}

## 严格 5% 检验为何不能开展

当前结论为 **`{test['status']}`**。要计算每个完整年度和滚动五年的净结果，至少需要：

{needed}

上交所冻结材料解释了期权数据应有的合约、调整、状态、报价和结算字段，却没有在本研究中形成完整、时点正确且可审计的实际合约与成交包。因此不能把卖出期权收取的权利金误读成每年稳定的净收益，也不能生成任何回测数字或个人操作。

## 风险与结论

备兑认购仍承担 ETF 下跌；权利金会限制上行但不能消除下跌、流动性、调整、交割、账户和成交风险。C13 当前只保留为规则完整但数据与个人执行尚未闭合的研究候选；在严格 5% 目标下不具备可用性。来源与哈希见 [C13 source manifest](../sources/c13-sse-etf-option-rules-20260815/manifest.md)，机器副本见 [c13_etf_option_covered_call_feasibility_20260815.json](c13_etf_option_covered_call_feasibility_20260815.json)。
"""


def _verify_output() -> None:
    _verify_manifest()
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        raise FileNotFoundError("C13 derived output is absent")
    saved = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    if saved.get("source_manifest", {}).get("sha256") != _sha256(MANIFEST_JSON):
        raise ValueError("C13 output source-manifest hash differs")
    if saved.get("status") != "RESEARCH_CANDIDATE_NOT_ACTION_READY" or saved.get("portfolio_q") != 0:
        raise ValueError("C13 output status differs")
    if saved.get("strict_5pct_test", {}).get("status") != "NOT_FEASIBLE_FOR_RETURN_CLAIM":
        raise ValueError("C13 output must retain the strict-test non-feasible state")
    prohibited = ("本金", "初始资金", "initial capital", "initial_capital", "starting amount")
    for path in (OUTPUT_JSON, OUTPUT_MD):
        text = path.read_text(encoding="utf-8").lower()
        for term in prohibited:
            if term.lower() in text:
                raise ValueError(f"forbidden monetary-scope phrase {term!r} in {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--capture", action="store_true")
    modes.add_argument("--rebuild-derived", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
        payload = _build()
        print(f"C13 CAPTURE + FEASIBILITY: {payload['strict_5pct_test']['status']}")
    elif arguments.rebuild_derived:
        payload = _build()
        print(f"C13 FEASIBILITY: {payload['strict_5pct_test']['status']}")
    else:
        _verify_output()
        print("C13 CAPTURE/FEASIBILITY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
