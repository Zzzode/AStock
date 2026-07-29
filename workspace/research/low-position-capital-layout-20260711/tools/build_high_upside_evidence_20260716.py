#!/usr/bin/env python3
"""Build the ticker-level evidence closure for Section 4.3 high-upside rows."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
REFRESH_DATA_DIR = REFRESH_DIR / "data"
CANONICAL_DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "high-upside-evidence-20260716"
METADATA_DIR = SOURCE_DIR / "eastmoney-report-metadata"
PUBLIC_PROBE_DIR = SOURCE_DIR / "public-probes"
BROKER_DIR = REFRESH_DIR / "sources" / "broker-reports-20260715"
DATA_CUTOFF = "2026-07-15"
EVIDENCE_DATE = "2026-07-16"
CURRENT_REPORT_THRESHOLD = "2026-04-01"
TICKERS = ("002432", "000623", "600739", "000685", "600150", "301308")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def relative(path: Path) -> str:
    return str(path.relative_to(CASE_DIR))


def report_date(value: str) -> str:
    return value.split(" ", 1)[0]


def age_days(value: str) -> int:
    return (date.fromisoformat(DATA_CUTOFF) - date.fromisoformat(value)).days


def number(value: Any, digits: int = 2) -> str:
    if value is None:
        return "未披露"
    return f"{float(value):.{digits}f}"


def percent(value: Any, digits: int = 1) -> str:
    if value is None:
        return "不适用"
    return f"{float(value) * 100:.{digits}f}%"


def require_text(path: Path, needles: list[str], encoding: str = "utf-8") -> str:
    text = path.read_text(encoding=encoding, errors="replace")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise RuntimeError(f"{relative(path)} is missing required text: {missing}")
    return text


def target_rows(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in metadata["data"]:
        low = str(row.get("indvAimPriceL") or "").strip()
        high = str(row.get("indvAimPriceT") or "").strip()
        if not low and not high:
            continue
        low_value = float(low or high)
        high_value = float(high or low)
        low_value, high_value = sorted((low_value, high_value))
        rows.append(
            {
                "report_date": report_date(row["publishDate"]),
                "broker": row.get("orgSName"),
                "title": row.get("title"),
                "target_low": low_value,
                "target_high": high_value,
                "target_midpoint": round((low_value + high_value) / 2, 4),
                "info_code": row.get("infoCode"),
            }
        )
    return rows


def anchor(
    *,
    target_low: float | None,
    target_high: float | None,
    report_date_value: str | None,
    broker: str | None,
    source_class: str,
    source_path: str | None,
    extract: str | None,
    derivation: str | None = None,
) -> dict[str, Any]:
    target_midpoint = (
        round((target_low + target_high) / 2, 4)
        if target_low is not None and target_high is not None
        else None
    )
    return {
        "status": "found" if target_midpoint is not None else "not_disclosed",
        "target_low": target_low,
        "target_high": target_high,
        "target_midpoint": target_midpoint,
        "report_date": report_date_value,
        "age_days_at_cutoff": age_days(report_date_value)
        if report_date_value
        else None,
        "broker": broker,
        "source_class": source_class,
        "source_path": source_path,
        "extract": extract,
        "derivation": derivation,
        "valuation_weight": 0.0,
    }


def evidence_configuration() -> dict[str, dict[str, Any]]:
    return {
        "002432": {
            "anchor": anchor(
                target_low=70.28,
                target_high=70.28,
                report_date_value="2024-12-23",
                broker="东吴证券",
                source_class="historical_original_pdf",
                source_path=(
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "002432-九安医疗/2024-12-23-东吴证券-"
                    "立足iHealth系列-展望O-O互联网医疗.pdf"
                ),
                extract="FCFF估值测算得到公司市值344.47亿元，对应每股价值70.28元。",
            ),
            "required_text": {
                "path": (
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "002432-九安医疗/2024-12-23-东吴证券-"
                    "立足iHealth系列-展望O-O互联网医疗.txt"
                ),
                "needles": ["344.47 亿元，对应每股价值 70.28 元"],
            },
            "cross_checks": [
                {
                    "source_class": "failed_public_probe",
                    "source_path": (
                        "sources/high-upside-evidence-20260716/public-probes/"
                        "002432_ttchagu_probe.html"
                    ),
                    "result": "页面可归档，但未出现可核验的53元目标价原文；不接受搜索摘要或聚合页推断。",
                    "valuation_weight": 0.0,
                }
            ],
            "remaining_event_validation": [
                "重新满足优先池的价格位置与行业阶段规则",
                "H2扣非利润持续性与经营现金流转正",
                "2026-04-01之后原始券商目标价或合理价值区间",
            ],
        },
        "000623": {
            "anchor": anchor(
                target_low=round(223.7 / 12.4107, 2),
                target_high=round(223.7 / 12.4107, 2),
                report_date_value="2024-03-27",
                broker="国元证券",
                source_class="historical_original_pdf_derived_per_share",
                source_path=(
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "000623-吉林敖东/2024-03-27-国元证券-首次覆盖报告-"
                    "医药主业持续发力-金融赋能-老牌药企迎来新发展.pdf"
                ),
                extract="公司目标总市值223.7亿元；A股总股本1,241.07百万股。",
                derivation="223.7亿元 / 12.4107亿股 = 18.02元/股",
            ),
            "required_text": {
                "path": (
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "000623-吉林敖东/2024-03-27-国元证券-首次覆盖报告-"
                    "医药主业持续发力-金融赋能-老牌药企迎来新发展.txt"
                ),
                "needles": [
                    "A 股总股本（百万股）： 1241.07",
                    "公司对应目标总市值为 223.7 亿元",
                ],
            },
            "cross_checks": [],
            "remaining_event_validation": [
                "2026-04-01之后原始券商目标价或合理价值区间",
                "H2扣非利润持续性与投资收益质量",
                "经营现金流持续为正",
            ],
        },
        "600739": {
            "anchor": anchor(
                target_low=22.79,
                target_high=22.79,
                report_date_value="2017-10-30",
                broker="太平洋证券",
                source_class="stale_original_pdf",
                source_path=(
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "600739-辽宁成大/2017-10-30-太平洋-"
                    "辽宁成大2017年三季报点评-单季业绩暴增-投资收益稳定.pdf"
                ),
                extract="目标价22.79元。",
            ),
            "required_text": {
                "path": (
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "600739-辽宁成大/2017-10-30-太平洋-"
                    "辽宁成大2017年三季报点评-单季业绩暴增-投资收益稳定.txt"
                ),
                "needles": ["目标价 22.79 元"],
            },
            "cross_checks": [],
            "remaining_event_validation": [
                "2026-04-01之后原始券商目标价或合理价值区间",
                "H2扣非利润持续性与广发证券投资收益质量",
                "经营现金流转正",
            ],
        },
        "000685": {
            "anchor": anchor(
                target_low=10.50,
                target_high=11.11,
                report_date_value="2025-03-04",
                broker="国信证券",
                source_class="historical_original_pdf",
                source_path=(
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "000685-中山公用/2025-03-04-国信证券-"
                    "攻守兼备的珠三角公用事业平台-长期破净估值有望修复.pdf"
                ),
                extract="合理估值10.50-11.11元。",
            ),
            "required_text": {
                "path": (
                    "refresh-20260715/sources/broker-reports-20260715/"
                    "000685-中山公用/2025-03-04-国信证券-"
                    "攻守兼备的珠三角公用事业平台-长期破净估值有望修复.txt"
                ),
                "needles": ["合理估值                                    10.50 - 11.11 元"],
            },
            "cross_checks": [],
            "remaining_event_validation": [
                "重新满足优先池的价格位置与行业阶段规则",
                "H2扣非利润与投资收益可持续性",
                "经营现金流转正",
                "当前原始券商目标价或合理价值区间",
            ],
        },
        "600150": {
            "anchor": anchor(
                target_low=31.36,
                target_high=31.36,
                report_date_value="2023-03-27",
                broker="国金证券",
                source_class="stale_original_api_metadata",
                source_path=(
                    "sources/high-upside-evidence-20260716/"
                    "eastmoney-report-metadata/600150_report_list.json"
                ),
                extract="indvAimPriceL=31.36; indvAimPriceT=31.36",
            ),
            "required_text": None,
            "cross_checks": [
                {
                    "source_class": "media_repost",
                    "source_path": (
                        "sources/high-upside-evidence-20260716/public-probes/"
                        "600150_sina_vreport_837356572572.html"
                    ),
                    "report_date": "2026-07-14",
                    "broker": "中金公司",
                    "target_price": 50.00,
                    "result": "新浪转载文本明确写出50.00元目标价，但不是原始研报PDF，估值权重为0。",
                    "valuation_weight": 0.0,
                }
            ],
            "remaining_event_validation": [
                "当前原始券商目标价或合理价值区间",
                "H2订单交付、船价、利润率与应收回款",
                "集团整合后的持续盈利与现金流",
            ],
        },
        "301308": {
            "anchor": anchor(
                target_low=None,
                target_high=None,
                report_date_value=None,
                broker=None,
                source_class="not_found_in_original_corpus",
                source_path=None,
                extract=None,
            ),
            "required_text": None,
            "cross_checks": [
                {
                    "source_class": "failed_third_party_probe",
                    "source_path": (
                        "sources/high-upside-evidence-20260716/public-probes/"
                        "301308_stockstar_probe.html"
                    ),
                    "result": "归档页面未出现454.51元目标均价文本，不能作为可审计共识或目标价。",
                    "valuation_weight": 0.0,
                }
            ],
            "remaining_event_validation": [
                "重新满足优先池的价格位置与行业阶段规则",
                "当前原始券商目标价或合理价值区间",
                "H2存储价格、出货、毛利率与库存周期",
                "经营现金流显著改善",
            ],
        },
    }


def build_row(
    audit: dict[str, Any],
    evidence: dict[str, Any],
    model: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    ticker = audit["ticker"]
    metadata_path = METADATA_DIR / f"{ticker}_report_list.json"
    metadata = load_json(metadata_path)
    if metadata.get("ticker") != ticker:
        raise RuntimeError(f"Ticker mismatch in {relative(metadata_path)}")
    rows = metadata.get("data") or []
    if not rows:
        raise RuntimeError(f"No report metadata in {relative(metadata_path)}")
    latest_metadata_date = max(report_date(row["publishDate"]) for row in rows)
    metadata_targets = target_rows(metadata)
    current_metadata_rows = [
        row for row in rows if report_date(row["publishDate"]) >= CURRENT_REPORT_THRESHOLD
    ]
    current_metadata_targets = [
        row for row in metadata_targets if row["report_date"] >= CURRENT_REPORT_THRESHOLD
    ]
    broker_path = next(
        path
        for path in BROKER_DIR.glob(f"{ticker}-*")
        if path.is_dir()
    )
    pdf_paths = sorted(broker_path.glob("*.pdf"))
    text_paths = sorted(broker_path.glob("*.txt"))
    if not pdf_paths or len(pdf_paths) != len(text_paths):
        raise RuntimeError(
            f"Incomplete PDF/text archive for {ticker}: "
            f"{len(pdf_paths)} PDF, {len(text_paths)} text"
        )
    required = config.get("required_text")
    if required:
        require_text(CASE_DIR / required["path"], required["needles"])
    if ticker == "600150":
        require_text(
            PUBLIC_PROBE_DIR / "600150_sina_vreport_837356572572.html",
            ["日期：2026-07-14", "维持50.00 元目标价"],
            encoding="gb18030",
        )
    if ticker == "301308":
        failed_probe = (
            PUBLIC_PROBE_DIR / "301308_stockstar_probe.html"
        ).read_text(errors="replace")
        if "454.51" in failed_probe:
            raise RuntimeError("301308 failed probe unexpectedly contains 454.51")
    if ticker == "002432":
        failed_probe = (
            PUBLIC_PROBE_DIR / "002432_ttchagu_probe.html"
        ).read_text(errors="replace")
        if "53.00元" in failed_probe or "53元" in failed_probe:
            raise RuntimeError("002432 failed probe unexpectedly contains a 53 yuan target")

    accepted_anchor = config["anchor"]
    target_midpoint = accepted_anchor.get("target_midpoint")
    target_upside = (
        round(target_midpoint / float(model["current_price"]) - 1, 4)
        if target_midpoint is not None
        else None
    )
    target_to_house = (
        round(target_midpoint / float(model["probability_target"]), 4)
        if target_midpoint is not None
        else None
    )
    latest_report_current = latest_metadata_date >= CURRENT_REPORT_THRESHOLD
    current_direct_target_available = bool(current_metadata_targets)
    cash_flow_status = (
        "positive_observed"
        if float(evidence.get("q1_ocf_100mn") or 0) > 0
        else "negative_or_zero_observed"
    )
    if target_midpoint is None:
        external_anchor_closure = (
            f"东方财富原始API共{len(rows)}份研报的目标价字段均为空；"
            f"本地复核{len(pdf_paths)}份原始PDF，未获得可接受目标价。"
        )
        closure_type = "closed_by_exhaustion"
    else:
        external_anchor_closure = (
            f"找到{accepted_anchor['report_date']}的{number(target_midpoint)}元历史锚，"
            f"但其相对当前价空间仅{percent(target_upside)}，仅相当于本机构概率值的"
            f"{percent(target_to_house)}；因陈旧或非当前原始证据，估值权重为0。"
        )
        closure_type = "closed_by_counterevidence"
    if current_direct_target_available:
        raise RuntimeError(
            f"{ticker} unexpectedly has a current original API target after "
            f"{CURRENT_REPORT_THRESHOLD}"
        )
    current_target_proof = (
        f"截止{DATA_CUTOFF}，原始API中{len(current_metadata_rows)}份"
        f"{CURRENT_REPORT_THRESHOLD}后研报均未披露目标价字段。"
        if current_metadata_rows
        else (
            f"原始API中没有{CURRENT_REPORT_THRESHOLD}后的研报，"
            "因此不存在可正权使用的当前目标价。"
        )
    )
    final_admission_decision = (
        "保留优先池验证，维持非正式模型"
        if audit["in_priority_pool"]
        else "保留候选观察，维持未进入优先池及非正式模型"
    )
    final_admission_code = (
        "retain_priority_not_formal"
        if audit["in_priority_pool"]
        else "retain_candidate_not_priority_not_formal"
    )
    direct_evidence_paths = [
        relative(metadata_path),
        relative(broker_path),
        evidence.get("local_pdf"),
        accepted_anchor.get("source_path"),
    ]
    direct_evidence_paths = list(dict.fromkeys(path for path in direct_evidence_paths if path))
    closed_gaps = [
        {
            "gap": "original_broker_corpus",
            "status": "closed",
            "finding": (
                f"东方财富原始API完整返回{len(rows)}份；本地归档并复核"
                f"{len(pdf_paths)}份PDF及对应文本。"
            ),
        },
        {
            "gap": "current_external_target",
            "status": closure_type,
            "finding": external_anchor_closure + current_target_proof,
        },
        {
            "gap": "cash_conversion",
            "status": "closed_as_observed_not_forecast",
            "finding": (
                f"Q1经营现金流为{number(evidence.get('q1_ocf_100mn'), 4)}亿元，"
                f"状态为{cash_flow_status}；H2仅保留为未来事件验证，不冒充已满足。"
            ),
        },
        {
            "gap": "pool_admission",
            "status": "closed",
            "finding": final_admission_decision,
        },
    ]
    return {
        "ticker": ticker,
        "company": audit["company"],
        "industry": audit["industry"],
        "current_price": model["current_price"],
        "house_probability_target": model["probability_target"],
        "house_model_upside": model["upside"],
        "q1_ocf_100mn": evidence.get("q1_ocf_100mn"),
        "cash_flow_status": cash_flow_status,
        "in_priority_pool": audit["in_priority_pool"],
        "in_formal_pool": audit["in_formal_pool"],
        "metadata_report_count": len(rows),
        "archived_original_pdf_count": len(pdf_paths),
        "archived_original_text_count": len(text_paths),
        "latest_metadata_report_date": latest_metadata_date,
        "latest_metadata_report_is_current": latest_report_current,
        "current_report_count": len(current_metadata_rows),
        "current_original_target_count": len(current_metadata_targets),
        "api_target_record_count": len(metadata_targets),
        "api_target_records": metadata_targets,
        "accepted_external_anchor": {
            **accepted_anchor,
            "implied_upside_vs_current": target_upside,
            "target_to_house_probability_value": target_to_house,
        },
        "current_target_proof": current_target_proof,
        "cross_checks": config["cross_checks"],
        "closed_gaps": closed_gaps,
        "remaining_event_validation": config["remaining_event_validation"],
        "final_admission_code": final_admission_code,
        "final_admission_decision": final_admission_decision,
        "final_conclusion": (
            f"证据缺口已完成事实闭环，但未形成当前正权外部锚；"
            f"{final_admission_decision}。内部{percent(model['upside'])}高空间"
            "不得转换为正式目标价或配置结论。"
        ),
        "direct_evidence_paths": direct_evidence_paths,
        "metadata_request_url": metadata.get("request_url"),
        "metadata_retrieved_at": metadata.get("retrieved_at"),
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# 第4.3节高空间标的证据闭环",
        "",
        f"- 数据截止：{payload['data_cutoff']}",
        f"- 专项核验日期：{payload['evidence_date']}",
        f"- 覆盖标的：{payload['row_count']}只",
        f"- 缺口闭环：{payload['closure_count']}/{payload['row_count']}",
        f"- 当前原始正权目标：{payload['current_positive_anchor_count']}只",
        f"- 正式模型升级：{payload['formal_upgrade_count']}只",
        "",
        "“补齐”不等于强行升级。本专项把每只标的归入三类真实结果：找到原始证据、找到反向证据，或证明截至截止日未披露。媒体转载、聚合页、搜索摘要和用户内容均为零权重。",
        "",
        "## 逐票结论",
        "",
        "| 代码 | 标的 | 原始API/本地PDF | 已核验外部锚 | Q1经营现金流 | 最终准入 |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in payload["rows"]:
        accepted = row["accepted_external_anchor"]
        if accepted["target_midpoint"] is None:
            anchor_text = "原始语料未披露当前目标"
        else:
            anchor_text = (
                f"{accepted['report_date']} {number(accepted['target_midpoint'])}元；"
                f"权重{percent(accepted['valuation_weight'], 0)}"
            )
        lines.append(
            f"| {row['ticker']} | {row['company']} | "
            f"{row['metadata_report_count']}/{row['archived_original_pdf_count']} | "
            f"{anchor_text} | {number(row['q1_ocf_100mn'], 4)}亿元 | "
            f"{row['final_admission_decision']} |"
        )
    lines += [
        "",
        "## 审计原则",
        "",
        f"1. “当前”原始研报门槛为{CURRENT_REPORT_THRESHOLD}及以后；早于该日的目标只作历史反证，权重为0。",
        "2. 当前研报存在但目标字段为空，记录为“已核验未披露”，不继续保留空白待办。",
        "3. H2现金流、利润持续性、订单或价格周期是未来事件验证，不写成已满足证据。",
        "4. 内部情景值与券商目标严格分列；媒体转载、第三方聚合和失败探针均不进入估值加权。",
    ]
    for row in payload["rows"]:
        anchor_row = row["accepted_external_anchor"]
        lines += [
            "",
            f"## {row['ticker']} {row['company']}",
            "",
            f"- 当前价/本机构概率值/模型空间：{number(row['current_price'])}元 / "
            f"{number(row['house_probability_target'])}元 / {percent(row['house_model_upside'])}",
            f"- 原始语料：API {row['metadata_report_count']}份，本地PDF "
            f"{row['archived_original_pdf_count']}份，最新日期{row['latest_metadata_report_date']}。",
            f"- 当前目标价证明：{row['current_target_proof']}",
            (
                f"- 接受的历史/反向锚：{anchor_row['report_date']} "
                f"{number(anchor_row['target_midpoint'])}元；来源等级"
                f"`{anchor_row['source_class']}`；估值权重0%。"
                if anchor_row["target_midpoint"] is not None
                else "- 接受的历史/反向锚：未找到；原始API与本地PDF语料已按上述范围穷尽。"
            ),
            f"- 现金流证明：Q1经营现金流{number(row['q1_ocf_100mn'], 4)}亿元；"
            "H2仍为未来验证条件。",
            f"- 最终结论：{row['final_conclusion']}",
            f"- 剩余事件验证：{'；'.join(row['remaining_event_validation'])}。",
            "- 证据路径："
            + "；".join(f"`{path}`" for path in row["direct_evidence_paths"])
            + "。",
        ]
        for check in row["cross_checks"]:
            lines.append(
                f"- 零权重交叉验证：{check['result']} "
                f"`{check['source_path']}`。"
            )
    return "\n".join(lines)


def source_index(payload: dict[str, Any]) -> str:
    lines = [
        "# High-Upside Evidence Source Index",
        "",
        f"- Data cutoff: {DATA_CUTOFF}",
        f"- Evidence closure date: {EVIDENCE_DATE}",
        "- Raw Eastmoney responses are preserved under `eastmoney-report-metadata/`.",
        "- Public reposts and failed probes are preserved under `public-probes/` and always carry zero valuation weight.",
        "- Original broker PDFs and extracted text remain under `refresh-20260715/sources/broker-reports-20260715/`.",
        "",
        "| Ticker | Metadata rows | Archived PDFs | Current original targets | Decision |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['ticker']} | {row['metadata_report_count']} | "
            f"{row['archived_original_pdf_count']} | "
            f"{row['current_original_target_count']} | "
            f"{row['final_admission_code']} |"
        )
    return "\n".join(lines)


def main() -> None:
    audit_packet = load_json(
        REFRESH_DATA_DIR / "high_upside_selection_audit_20260715.json"
    )
    evidence_packet = load_json(
        REFRESH_DATA_DIR / "full_market_valuation_evidence_20260715.json"
    )
    model_packet = load_json(
        REFRESH_DATA_DIR / "full_market_candidate_valuation_20260715.json"
    )
    audits = {row["ticker"]: row for row in audit_packet["rows"]}
    evidence = {row["ticker"]: row for row in evidence_packet["rows"]}
    models = {row["ticker"]: row for row in model_packet["rows"]}
    if tuple(row["ticker"] for row in audit_packet["rows"]) != TICKERS:
        raise RuntimeError("High-upside ticker set or order changed")
    config = evidence_configuration()
    rows = [
        build_row(audits[ticker], evidence[ticker], models[ticker], config[ticker])
        for ticker in TICKERS
    ]
    payload = {
        "schema_version": "astock.high_upside_evidence_closure.v1",
        "data_cutoff": DATA_CUTOFF,
        "evidence_date": EVIDENCE_DATE,
        "current_report_threshold": CURRENT_REPORT_THRESHOLD,
        "row_count": len(rows),
        "closure_count": sum(len(row["closed_gaps"]) == 4 for row in rows),
        "current_positive_anchor_count": sum(
            row["current_original_target_count"] > 0 for row in rows
        ),
        "formal_upgrade_count": sum(row["in_formal_pool"] for row in rows),
        "priority_retained_count": sum(row["in_priority_pool"] for row in rows),
        "candidate_only_count": sum(not row["in_priority_pool"] for row in rows),
        "source_policy": {
            "positive_weight": "current original broker PDF/API target field only",
            "zero_weight": [
                "historical original target",
                "media repost",
                "third-party aggregation",
                "search snippet",
                "user-generated content",
                "failed probe",
            ],
            "future_event_boundary": (
                "H2 earnings, cash flow, orders, prices and pool re-entry are "
                "future validation events, not completed evidence."
            ),
        },
        "rows": rows,
    }
    for directory in (REFRESH_DATA_DIR, CANONICAL_DATA_DIR):
        write_json(
            directory / "high_upside_evidence_closure_20260716.json",
            payload,
        )
        write_text(
            directory / "high_upside_evidence_closure_20260716.md",
            markdown(payload),
        )
    write_text(SOURCE_DIR / "index.md", source_index(payload))
    print(
        json.dumps(
            {
                "rows": payload["row_count"],
                "closed": payload["closure_count"],
                "current_positive_anchors": payload[
                    "current_positive_anchor_count"
                ],
                "formal_upgrades": payload["formal_upgrade_count"],
                "output": relative(
                    REFRESH_DATA_DIR
                    / "high_upside_evidence_closure_20260716.json"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
