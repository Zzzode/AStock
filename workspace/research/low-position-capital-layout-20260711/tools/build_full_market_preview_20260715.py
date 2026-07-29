#!/usr/bin/env python3
"""Build the full A-share 2026H1 preview universe through 2026-07-15."""

from __future__ import annotations

import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd
import requests


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "refresh-20260715" / "data"
SOURCE_DIR = CASE_DIR / "refresh-20260715" / "sources" / "full-market-preview-20260715"
CLASSIFICATION_URL = (
    "https://www.swsresearch.com/swindex/pdf/SwClass2021/"
    "StockClassifyUse_stock.xls"
)
DATA_CUTOFF = "2026-07-15"
B_SHARE_PREFIXES = ("200", "900")
SWS_LEVEL1 = {
    "11": "农林牧渔", "22": "基础化工", "23": "钢铁", "24": "有色金属",
    "27": "电子", "28": "汽车", "33": "家用电器", "34": "食品饮料",
    "35": "纺织服饰", "36": "轻工制造", "37": "医药生物", "41": "公用事业",
    "42": "交通运输", "43": "房地产", "45": "商贸零售", "46": "社会服务",
    "48": "银行", "49": "非银金融", "51": "综合", "61": "建筑材料",
    "62": "建筑装饰", "63": "电力设备", "64": "机械设备", "65": "国防军工",
    "71": "计算机", "72": "传媒", "73": "通信", "74": "煤炭",
    "75": "石油石化", "76": "环保", "77": "美容护理",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def normalize_code(value: Any) -> str:
    text = str(value).strip()
    return text.zfill(6) if text.isdigit() else text


def optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_classification() -> dict[str, dict[str, Any]]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = SOURCE_DIR / "StockClassifyUse_stock_20260715.xls"
    response = requests.get(CLASSIFICATION_URL, headers={"User-Agent": "Mozilla/5.0"},
                            verify=False, timeout=60)
    response.raise_for_status()
    path.write_bytes(response.content)
    frame = pd.read_excel(io.BytesIO(response.content), dtype={"股票代码": str, "行业代码": str})
    frame["股票代码"] = frame["股票代码"].str.zfill(6)
    frame["计入日期"] = pd.to_datetime(frame["计入日期"], errors="coerce")
    frame = frame[frame["计入日期"] <= pd.Timestamp(DATA_CUTOFF)]
    frame = frame.sort_values(["股票代码", "计入日期"]).groupby("股票代码", as_index=False).tail(1)
    result = {}
    for row in frame.to_dict("records"):
        industry_code = str(row["行业代码"])
        result[row["股票代码"]] = {
            "sws_industry_code": industry_code,
            "sws_industry": SWS_LEVEL1.get(industry_code[:2], "unmapped"),
            "industry_mapping_source": "official_sws_classification_history",
            "industry_effective_date": str(row["计入日期"].date()),
        }
    return result


def build_metric_map(frame: pd.DataFrame) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in frame.to_dict("records"):
        result[normalize_code(row.get("股票代码"))][str(row.get("预测指标"))] = row
    return result


def load_sector_stage() -> dict[str, dict[str, Any]]:
    refresh_path = CASE_DIR / "refresh-20260715" / "data" / "sector_scan_20260715.json"
    path = refresh_path if refresh_path.exists() else CASE_DIR / "data" / "sector_scan_20260710.json"
    if not path.exists():
        return {}
    return {row["industry"]: row for row in json.loads(path.read_text())["rows"]}


def impact_score(h1_np: float | None, yoy: float | None, deducted_share: float | None,
                 preview_type: str, stage: str) -> float:
    profit_points = min(max(h1_np or 0, 0), 100) / 5
    growth_points = min(max(yoy or 0, 0), 300) / 20
    quality_points = min(max(deducted_share or 0, 0), 1) * 10
    stage_points = {"silent_accumulation": 8, "launch_confirmation": 7,
                    "flow_watch": 5, "one_day_rebound": 3,
                    "low_price_no_flow": 1, "no_signal": 0}.get(stage, 0)
    turnaround_points = 3 if preview_type in {"扭亏", "预增"} else 0
    return round(profit_points + growth_points + quality_points +
                 stage_points + turnaround_points, 2)


def main() -> None:
    frame = ak.stock_yjyg_em(date="20260630")
    raw_records = json.loads(frame.to_json(orient="records", force_ascii=False,
                                            date_format="iso"))
    write_json(DATA_DIR / "raw_a_share_h1_2026_preview_20260715.json", {
        "schema_version": "astock.raw_a_share_h1_preview.v2",
        "data_cutoff": DATA_CUTOFF,
        "report_period": "2026H1",
        "source": "akshare.stock_yjyg_em(date=20260630) / Eastmoney datacenter paginated API",
        "row_count": len(raw_records),
        "rows": raw_records,
    })
    eligible = [row for row in raw_records
                if not normalize_code(row.get("股票代码")).startswith(B_SHARE_PREFIXES)]
    parent_rows = [row for row in eligible
                   if str(row.get("预测指标")) == "归属于上市公司股东的净利润"]
    metrics = build_metric_map(pd.DataFrame(eligible))
    classification = fetch_classification()
    sector_stage = load_sector_stage()
    rows: list[dict[str, Any]] = []
    for code, company_metrics in metrics.items():
        parent = company_metrics.get("归属于上市公司股东的净利润")
        if parent is None:
            continue
        deducted = company_metrics.get("扣除非经常性损益后的净利润")
        eps = company_metrics.get("每股收益")
        revenue = company_metrics.get("营业收入")
        industry = classification.get(code, {
            "sws_industry_code": "unmapped",
            "sws_industry": "unmapped",
            "industry_mapping_source": "not_found",
            "industry_effective_date": "not_found",
        })
        h1_np_raw = optional_float(parent.get("预测数值"))
        h1_deducted_raw = optional_float(deducted.get("预测数值")) if deducted else None
        h1_np = h1_np_raw / 1e8 if h1_np_raw is not None else None
        h1_deducted = h1_deducted_raw / 1e8 if h1_deducted_raw is not None else None
        yoy = optional_float(parent.get("业绩变动幅度"))
        nonrecurring = ((h1_np - h1_deducted) / h1_np * 100
                        if h1_np and h1_deducted is not None else None)
        deducted_share = (h1_deducted / h1_np
                          if h1_np and h1_deducted is not None else None)
        stage = sector_stage.get(industry["sws_industry"], {}).get("stage", "unmapped")
        preview_type = str(parent.get("预告类型") or "")
        high_impact = (
            h1_np is not None
            and (h1_np >= 20
                 or (h1_np >= 5 and (yoy or 0) >= 100 and (deducted_share or 0) >= 0.7)
                 or (h1_np >= 2 and (yoy or 0) >= 150 and
                     stage in {"silent_accumulation", "launch_confirmation", "flow_watch"}))
        )
        exclusion_reasons = []
        if h1_np is None or h1_np <= 0:
            exclusion_reasons.append("parent_net_profit_not_positive_or_missing")
        if h1_deducted is not None and h1_deducted <= 0:
            exclusion_reasons.append("deducted_profit_not_positive")
        if nonrecurring is not None and nonrecurring > 40:
            exclusion_reasons.append("nonrecurring_share_above_40pct")
        if not high_impact:
            exclusion_reasons.append("below_full_market_impact_threshold")
        rows.append({
            "ticker": code,
            "company": parent.get("股票简称"),
            **industry,
            "sector_stage": stage,
            "preview_type": preview_type,
            "announcement_date": str(parent.get("公告日期") or "")[:10],
            "h1_parent_np_midpoint_100mn": round(h1_np, 4) if h1_np is not None else None,
            "h1_deducted_np_midpoint_100mn": round(h1_deducted, 4) if h1_deducted is not None else None,
            "official_h1_eps_midpoint": optional_float(eps.get("预测数值")) if eps else None,
            "h1_revenue_midpoint_100mn": optional_float(revenue.get("预测数值")) / 1e8
            if revenue and optional_float(revenue.get("预测数值")) is not None else None,
            "parent_np_yoy_midpoint_pct": yoy,
            "deducted_profit_share_pct": round(deducted_share * 100, 2)
            if deducted_share is not None else None,
            "nonrecurring_share_pct": round(nonrecurring, 2)
            if nonrecurring is not None else None,
            "impact_score": impact_score(h1_np, yoy, deducted_share, preview_type, stage),
            "high_impact_candidate": high_impact,
            "exclusion_reasons": exclusion_reasons,
            "parent_forecast_text": parent.get("业绩变动"),
            "deducted_forecast_text": deducted.get("业绩变动") if deducted else "not disclosed",
            "data_quality": "official_structured_preview",
        })
    rows.sort(key=lambda row: (not row["high_impact_candidate"],
                               -row["impact_score"],
                               -(row["h1_parent_np_midpoint_100mn"] or -1e12)))
    candidates = [row for row in rows if row["high_impact_candidate"]]
    summary = []
    for industry in SWS_LEVEL1.values():
        group = [row for row in rows if row["sws_industry"] == industry]
        high = [row for row in group if row["high_impact_candidate"]]
        summary.append({
            "industry": industry,
            "sector_stage": sector_stage.get(industry, {}).get("stage", "unmapped"),
            "preview_company_count": len(group),
            "positive_parent_profit_count": sum((row["h1_parent_np_midpoint_100mn"] or 0) > 0
                                                for row in group),
            "high_impact_candidate_count": len(high),
            "h1_parent_np_sum_100mn": round(sum(row["h1_parent_np_midpoint_100mn"] or 0
                                                for row in group), 2),
            "top_candidates": [{"ticker": row["ticker"], "company": row["company"],
                                "h1_parent_np_midpoint_100mn": row["h1_parent_np_midpoint_100mn"],
                                "parent_np_yoy_midpoint_pct": row["parent_np_yoy_midpoint_pct"],
                                "nonrecurring_share_pct": row["nonrecurring_share_pct"],
                                "impact_score": row["impact_score"]}
                               for row in high[:5]],
        })
    write_json(DATA_DIR / "full_market_preview_screen_20260715.json", {
        "schema_version": "astock.full_market_preview_screen.v3",
        "data_cutoff": DATA_CUTOFF,
        "source_preview_row_count": len(raw_records),
        "eligible_a_share_metric_row_count": len(eligible),
        "scope_excluded_metric_row_count": len(raw_records) - len(eligible),
        "scope_excluded_security_count": len({normalize_code(r.get("股票代码"))
                                             for r in raw_records
                                             if normalize_code(r.get("股票代码")).startswith(B_SHARE_PREFIXES)}),
        "preview_company_count": len(rows),
        "mapped_company_count": sum(row["sws_industry"] != "unmapped" for row in rows),
        "high_impact_candidate_count": len(candidates),
        "screen_definition": {
            "high_impact": "H1 parent NP >= CNY2bn; or >= CNY0.5bn with YoY >=100% and deducted share >=70%; or >= CNY0.2bn with YoY >=150% in silent/launch/flow-watch industries",
            "quality_flags": ["deducted profit <= 0", "non-recurring share > 40%", "missing deducted-profit disclosure"],
        },
        "industry_summary": sorted(summary, key=lambda x: (-x["high_impact_candidate_count"],
                                                           -x["h1_parent_np_sum_100mn"])),
        "rows": rows,
    })
    write_json(DATA_DIR / "full_market_preview_candidates_20260715.json", {
        "schema_version": "astock.full_market_preview_candidates.v3",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(candidates),
        "rows": candidates,
    })
    lines = [
        "# Full-Market 2026H1 Preview Screen Through 2026-07-15", "",
        f"- Raw metric rows: {len(raw_records)}",
        f"- Eligible A-share metric rows: {len(eligible)}",
        f"- Preview companies: {len(rows)}",
        f"- Mapped companies: {sum(row['sws_industry'] != 'unmapped' for row in rows)}",
        f"- High-impact candidates: {len(candidates)}", "",
        "| Industry | Stage | Preview companies | Positive | High impact | H1 parent NP sum |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for item in sorted(summary, key=lambda x: x["industry"]):
        lines.append(f"| {item['industry']} | {item['sector_stage']} | "
                     f"{item['preview_company_count']} | {item['positive_parent_profit_count']} | "
                     f"{item['high_impact_candidate_count']} | {item['h1_parent_np_sum_100mn']:.2f} |")
    lines += ["", "## Evidence Boundary", "",
              "This is the full official structured 2026H1 preview table through 2026-07-15. "
              "It validates company-level forecast direction, not segment ASP, customer allocation, "
              "order durability, cash conversion or investable valuation."]
    write_text(DATA_DIR / "full_market_preview_screen_20260715.md", "\n".join(lines))
    print(json.dumps({"raw_rows": len(raw_records), "eligible_rows": len(eligible),
                      "companies": len(rows), "mapped": sum(row["sws_industry"] != "unmapped" for row in rows),
                      "candidates": len(candidates),
                      "stage_counts": Counter(row["sector_stage"] for row in rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
