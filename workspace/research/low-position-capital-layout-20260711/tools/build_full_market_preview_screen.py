#!/usr/bin/env python3
"""Build a full-A-share 2026H1 preview screen mapped to 31 SWS industries."""

from __future__ import annotations

import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
SOURCES_DIR = CASE_DIR / "sources" / "full-market-preview-20260712"
CLASSIFICATION_URL = (
    "https://www.swsresearch.com/swindex/pdf/SwClass2021/"
    "StockClassifyUse_stock.xls"
)

SWS_LEVEL1 = {
    "11": "农林牧渔",
    "22": "基础化工",
    "23": "钢铁",
    "24": "有色金属",
    "27": "电子",
    "28": "汽车",
    "33": "家用电器",
    "34": "食品饮料",
    "35": "纺织服饰",
    "36": "轻工制造",
    "37": "医药生物",
    "41": "公用事业",
    "42": "交通运输",
    "43": "房地产",
    "45": "商贸零售",
    "46": "社会服务",
    "48": "银行",
    "49": "非银金融",
    "51": "综合",
    "61": "建筑材料",
    "62": "建筑装饰",
    "63": "电力设备",
    "64": "机械设备",
    "65": "国防军工",
    "71": "计算机",
    "72": "传媒",
    "73": "通信",
    "74": "煤炭",
    "75": "石油石化",
    "76": "环保",
    "77": "美容护理",
}

MANUAL_INDUSTRY = {
    "920176": ("医药生物", "Beijing Stock Exchange medical-device issuer"),
}

B_SHARE_PREFIXES = ("200", "900")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def parse_bounds(text: str) -> tuple[float | None, float | None]:
    numbers = [
        float(value.replace(",", ""))
        for value in re.findall(r"(-?[\d,]+(?:\.\d+)?)\s*万元", text or "")
    ]
    if not numbers:
        return None, None
    low, high = min(numbers), max(numbers)
    return low / 10000, high / 10000


def optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_metric_map(raw_rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    metrics: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in raw_rows:
        code = str(row.get("股票代码", "")).zfill(6)
        metric = str(row.get("预测指标", ""))
        metrics[code][metric] = row
    return metrics


def fetch_sws_classification() -> dict[str, dict[str, Any]]:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    source_path = SOURCES_DIR / "StockClassifyUse_stock_20260712.xls"
    if source_path.exists() and source_path.stat().st_size:
        content = source_path.read_bytes()
    else:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            CLASSIFICATION_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            verify=False,
            timeout=60,
        )
        response.raise_for_status()
        content = response.content
        source_path.write_bytes(content)
    frame = pd.read_excel(
        io.BytesIO(content),
        dtype={"股票代码": str, "行业代码": str},
    )
    frame["股票代码"] = frame["股票代码"].str.zfill(6)
    frame["计入日期"] = pd.to_datetime(frame["计入日期"], errors="coerce")
    frame = frame[frame["计入日期"] <= pd.Timestamp("2026-07-11")]
    frame = (
        frame.sort_values(["股票代码", "计入日期"])
        .groupby("股票代码", as_index=False)
        .tail(1)
    )
    result: dict[str, dict[str, Any]] = {}
    for record in frame.to_dict("records"):
        industry_code = str(record["行业代码"])
        result[record["股票代码"]] = {
            "sws_industry_code": industry_code,
            "sws_industry": SWS_LEVEL1.get(industry_code[:2], "unmapped"),
            "industry_mapping_source": "official_sws_classification_history",
            "industry_effective_date": str(record["计入日期"].date()),
        }
    return result


def impact_score(
    h1_np: float | None,
    yoy: float | None,
    deducted_share: float | None,
    preview_type: str,
    sector_stage: str,
) -> float:
    profit_points = min(max(h1_np or 0, 0), 100) / 5
    growth_points = min(max(yoy or 0, 0), 300) / 20
    quality_points = min(max(deducted_share or 0, 0), 1) * 10
    stage_points = {
        "silent_accumulation": 8,
        "launch_confirmation": 7,
        "flow_watch": 5,
        "one_day_rebound": 3,
        "low_price_no_flow": 1,
        "no_signal": 0,
    }.get(sector_stage, 0)
    turnaround_points = 3 if preview_type in {"扭亏", "预增"} else 0
    return round(profit_points + growth_points + quality_points + stage_points + turnaround_points, 2)


def main() -> None:
    raw_packet = load_json(DATA_DIR / "raw_a_share_h1_2026_preview_20260711.json")
    scope_excluded_rows = [
        row
        for row in raw_packet["rows"]
        if str(row.get("股票代码", "")).zfill(6).startswith(B_SHARE_PREFIXES)
    ]
    eligible_raw_rows = [
        row
        for row in raw_packet["rows"]
        if not str(row.get("股票代码", "")).zfill(6).startswith(B_SHARE_PREFIXES)
    ]
    scope_excluded_tickers = sorted(
        {str(row.get("股票代码", "")).zfill(6) for row in scope_excluded_rows}
    )
    metrics = build_metric_map(eligible_raw_rows)
    classification = fetch_sws_classification()
    sector_stage = {
        row["industry"]: row for row in load_json(DATA_DIR / "sector_scan_20260710.json")["rows"]
    }
    old_universe = {
        row["ticker"]
        for row in load_json(DATA_DIR / "company_cards_20260711.json")["rows"]
    }

    rows: list[dict[str, Any]] = []
    for code, company_metrics in metrics.items():
        parent = company_metrics.get("归属于上市公司股东的净利润")
        if parent is None:
            continue
        deducted = company_metrics.get("扣除非经常性损益后的净利润")
        eps = company_metrics.get("每股收益")
        revenue = company_metrics.get("营业收入")
        industry = classification.get(code)
        if industry is None and code in MANUAL_INDUSTRY:
            industry_name, note = MANUAL_INDUSTRY[code]
            industry = {
                "sws_industry_code": "manual",
                "sws_industry": industry_name,
                "industry_mapping_source": note,
                "industry_effective_date": "2026-07-11",
            }
        industry = industry or {
            "sws_industry_code": "unmapped",
            "sws_industry": "unmapped",
            "industry_mapping_source": "not_found",
            "industry_effective_date": "not_found",
        }
        parent_value = optional_float(parent.get("预测数值"))
        h1_np = parent_value / 1e8 if parent_value is not None else None
        deducted_value = (
            optional_float(deducted.get("预测数值")) if deducted is not None else None
        )
        h1_deducted = (
            deducted_value / 1e8 if deducted_value is not None else None
        )
        official_eps = (
            optional_float(eps.get("预测数值")) if eps is not None else None
        )
        revenue_value = (
            optional_float(revenue.get("预测数值")) if revenue is not None else None
        )
        revenue_mid = revenue_value / 1e8 if revenue_value is not None else None
        yoy = (
            optional_float(parent.get("业绩变动幅度"))
        )
        deducted_share = (
            h1_deducted / h1_np
            if h1_np is not None and h1_np > 0 and h1_deducted is not None
            else None
        )
        nonrecurring_share = (
            (h1_np - h1_deducted) / h1_np * 100
            if h1_np is not None and h1_np > 0 and h1_deducted is not None
            else None
        )
        stage = sector_stage.get(industry["sws_industry"], {}).get("stage", "unmapped")
        score = impact_score(
            h1_np,
            yoy,
            deducted_share,
            str(parent.get("预告类型", "")),
            stage,
        )
        high_impact = (
            h1_np is not None
            and (
                h1_np >= 20
                or (
                    h1_np >= 5
                    and (yoy or 0) >= 100
                    and (deducted_share or 0) >= 0.7
                )
                or (
                    h1_np >= 2
                    and (yoy or 0) >= 150
                    and stage
                    in {"silent_accumulation", "launch_confirmation", "flow_watch"}
                )
            )
        )
        exclusion_reasons: list[str] = []
        if h1_np is None:
            exclusion_reasons.append("forecast_value_missing")
        elif h1_np <= 0:
            exclusion_reasons.append("parent_net_profit_not_positive")
        if h1_deducted is not None and h1_deducted <= 0:
            exclusion_reasons.append("deducted_profit_not_positive")
        if nonrecurring_share is not None and nonrecurring_share > 40:
            exclusion_reasons.append("nonrecurring_share_above_40pct")
        if not high_impact:
            exclusion_reasons.append("below_full_market_impact_threshold")
        row = {
            "ticker": code,
            "company": parent.get("股票简称"),
            **industry,
            "sector_stage": stage,
            "preview_type": parent.get("预告类型"),
            "announcement_date": str(parent.get("公告日期", ""))[:10],
            "h1_parent_np_midpoint_100mn": (
                round(h1_np, 4) if h1_np is not None else None
            ),
            "h1_deducted_np_midpoint_100mn": (
                round(h1_deducted, 4) if h1_deducted is not None else None
            ),
            "official_h1_eps_midpoint": official_eps,
            "h1_revenue_midpoint_100mn": (
                round(revenue_mid, 4) if revenue_mid is not None else None
            ),
            "parent_np_yoy_midpoint_pct": yoy,
            "deducted_profit_share_pct": (
                round(deducted_share * 100, 2) if deducted_share is not None else None
            ),
            "nonrecurring_share_pct": (
                round(nonrecurring_share, 2)
                if nonrecurring_share is not None
                else None
            ),
            "impact_score": score,
            "high_impact_candidate": high_impact,
            "in_prior_54_name_universe": code in old_universe,
            "exclusion_reasons": exclusion_reasons,
            "parent_forecast_text": parent.get("业绩变动"),
            "deducted_forecast_text": (
                deducted.get("业绩变动") if deducted is not None else "not disclosed"
            ),
        }
        rows.append(row)

    rows.sort(
        key=lambda row: (
            not row["high_impact_candidate"],
            -row["impact_score"],
            -(row["h1_parent_np_midpoint_100mn"] or -1e12),
        )
    )
    candidates = [row for row in rows if row["high_impact_candidate"]]
    omitted = [
        row
        for row in candidates
        if not row["in_prior_54_name_universe"]
    ]
    industry_summary: list[dict[str, Any]] = []
    for industry_name in SWS_LEVEL1.values():
        industry_rows = [row for row in rows if row["sws_industry"] == industry_name]
        industry_candidates = [
            row for row in industry_rows if row["high_impact_candidate"]
        ]
        industry_summary.append(
            {
                "industry": industry_name,
                "sector_stage": sector_stage.get(industry_name, {}).get("stage"),
                "preview_company_count": len(industry_rows),
                "positive_parent_profit_count": sum(
                    (row["h1_parent_np_midpoint_100mn"] or 0) > 0
                    for row in industry_rows
                ),
                "high_impact_candidate_count": len(industry_candidates),
                "h1_parent_np_sum_100mn": round(
                    sum(
                        row["h1_parent_np_midpoint_100mn"]
                        for row in industry_rows
                        if (row["h1_parent_np_midpoint_100mn"] or 0) > 0
                    ),
                    2,
                ),
                "top_candidates": [
                    {
                        "ticker": row["ticker"],
                        "company": row["company"],
                        "h1_parent_np_midpoint_100mn": row[
                            "h1_parent_np_midpoint_100mn"
                        ],
                        "parent_np_yoy_midpoint_pct": row[
                            "parent_np_yoy_midpoint_pct"
                        ],
                        "nonrecurring_share_pct": row["nonrecurring_share_pct"],
                        "impact_score": row["impact_score"],
                    }
                    for row in industry_candidates[:5]
                ],
            }
        )
    industry_summary.sort(
        key=lambda row: (
            -row["high_impact_candidate_count"],
            -row["h1_parent_np_sum_100mn"],
        )
    )

    packet = {
        "schema_version": "astock.full_market_preview_screen.v2",
        "data_cutoff": "2026-07-12 review; preview announcements through 2026-07-11",
        "source_preview_row_count": raw_packet["row_count"],
        "eligible_a_share_metric_row_count": len(eligible_raw_rows),
        "scope_excluded_metric_row_count": len(scope_excluded_rows),
        "scope_excluded_security_count": len(scope_excluded_tickers),
        "scope_excluded_tickers": scope_excluded_tickers,
        "scope_rule": "exclude Shenzhen/Shanghai B-share codes; retain Shanghai, Shenzhen, Beijing Stock Exchange A-share issuers",
        "preview_company_count": len(rows),
        "mapped_company_count": sum(row["sws_industry"] != "unmapped" for row in rows),
        "high_impact_candidate_count": len(candidates),
        "high_impact_omitted_from_prior_54_count": len(omitted),
        "screen_definition": {
            "high_impact": (
                "H1 parent NP >= CNY2bn; or H1 parent NP >= CNY0.5bn with "
                "YoY >=100% and deducted share >=70%; or H1 parent NP >= "
                "CNY0.2bn with YoY >=150% in silent/launch/flow-watch industries"
            ),
            "quality_flags": [
                "deducted profit <= 0",
                "non-recurring share > 40%",
                "missing deducted-profit disclosure",
            ],
        },
        "industry_summary": industry_summary,
        "rows": rows,
    }
    write_json(DATA_DIR / "full_market_preview_screen_20260712.json", packet)
    write_json(
        DATA_DIR / "full_market_preview_candidates_20260712.json",
        {
            "schema_version": "astock.full_market_preview_candidates.v1",
            "row_count": len(candidates),
            "rows": candidates,
        },
    )
    write_json(
        DATA_DIR / "prior_universe_omission_audit_20260712.json",
        {
            "schema_version": "astock.prior_universe_omission_audit.v1",
            "omitted_high_impact_count": len(omitted),
            "rows": omitted,
        },
    )

    lines = [
        "# Full-Market 2026H1 Preview Screen",
        "",
        f"- Raw metric rows: {raw_packet['row_count']}",
        f"- Eligible A-share metric rows: {len(eligible_raw_rows)}",
        f"- Scope-excluded B-share metric rows: {len(scope_excluded_rows)} across {len(scope_excluded_tickers)} securities",
        f"- Preview companies: {len(rows)}",
        f"- Mapped to 31 SWS industries: {packet['mapped_company_count']}",
        f"- High-impact candidates: {len(candidates)}",
        f"- High-impact candidates omitted from prior 54-name universe: {len(omitted)}",
        "",
        "## Industry Summary",
        "",
        "| Industry | Stage | Preview companies | Positive | High impact | Positive H1 NP sum | Top candidates |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in industry_summary:
        top = "、".join(
            f"{item['company']}({item['ticker']})"
            for item in row["top_candidates"][:3]
        ) or "-"
        lines.append(
            f"| {row['industry']} | {row['sector_stage']} | "
            f"{row['preview_company_count']} | {row['positive_parent_profit_count']} | "
            f"{row['high_impact_candidate_count']} | {row['h1_parent_np_sum_100mn']:.1f} | {top} |"
        )
    lines += [
        "",
        "## High-Impact Candidates",
        "",
        "| Industry | Stage | Ticker | Company | H1 parent NP | H1 deducted NP | YoY | Non-recurring | Score | Prior universe |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in candidates:
        lines.append(
            f"| {row['sws_industry']} | {row['sector_stage']} | {row['ticker']} | "
            f"{row['company']} | {row['h1_parent_np_midpoint_100mn']:.2f} | "
            f"{row['h1_deducted_np_midpoint_100mn'] if row['h1_deducted_np_midpoint_100mn'] is not None else '-'} | "
            f"{row['parent_np_yoy_midpoint_pct'] if row['parent_np_yoy_midpoint_pct'] is not None else '-'}% | "
            f"{row['nonrecurring_share_pct'] if row['nonrecurring_share_pct'] is not None else '-'}% | "
            f"{row['impact_score']:.2f} | {row['in_prior_54_name_universe']} |"
        )
    write_text(DATA_DIR / "full_market_preview_screen_20260712.md", "\n".join(lines))
    write_text(ANALYSIS_DIR / "full_market_preview_screen.md", "\n".join(lines))
    print(
        json.dumps(
            {
                "companies": len(rows),
                "mapped": packet["mapped_company_count"],
                "high_impact": len(candidates),
                "omitted_high_impact": len(omitted),
                "industry_counts": Counter(row["sws_industry"] for row in candidates),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
