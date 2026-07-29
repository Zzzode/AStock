#!/usr/bin/env python3
"""Build the full core universe and 2026H1 earnings-preview census."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
SOURCE_DIR = CASE_DIR / "sources" / "earnings-previews-20260711"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)


UNIVERSE: list[dict[str, str]] = [
    # Quiet accumulation / banks
    {"sector": "银行", "ticker": "601077", "company": "渝农商行", "tier": "core"},
    {"sector": "银行", "ticker": "601825", "company": "沪农商行", "tier": "core"},
    {"sector": "银行", "ticker": "601009", "company": "南京银行", "tier": "satellite"},
    {"sector": "银行", "ticker": "601128", "company": "常熟银行", "tier": "satellite"},
    {"sector": "银行", "ticker": "002142", "company": "宁波银行", "tier": "satellite"},
    {"sector": "银行", "ticker": "601939", "company": "建设银行", "tier": "satellite"},
    # Quiet accumulation / machinery
    {"sector": "工程机械", "ticker": "000425", "company": "徐工机械", "tier": "core"},
    {"sector": "工程机械", "ticker": "600031", "company": "三一重工", "tier": "satellite"},
    {"sector": "工程机械", "ticker": "000157", "company": "中联重科", "tier": "satellite"},
    {"sector": "工程机械", "ticker": "601100", "company": "恒立液压", "tier": "satellite"},
    {"sector": "工程机械", "ticker": "603338", "company": "浙江鼎力", "tier": "satellite"},
    # Launched / AI network and compute infrastructure
    {"sector": "AI网络与算力设备", "ticker": "000063", "company": "中兴通讯", "tier": "core"},
    {"sector": "AI网络与算力设备", "ticker": "000938", "company": "紫光股份", "tier": "core_candidate"},
    {"sector": "AI网络与算力设备", "ticker": "000977", "company": "浪潮信息", "tier": "core_candidate"},
    {"sector": "AI网络与算力设备", "ticker": "002396", "company": "星网锐捷", "tier": "satellite"},
    {"sector": "AI网络与算力设备", "ticker": "301165", "company": "锐捷网络", "tier": "satellite"},
    {"sector": "AI网络与算力设备", "ticker": "601138", "company": "工业富联", "tier": "demand_anchor"},
    {"sector": "AI网络与算力设备", "ticker": "001339", "company": "智微智能", "tier": "preview_candidate"},
    # Launched / AI storage
    {"sector": "AI存储", "ticker": "301308", "company": "江波龙", "tier": "core"},
    {"sector": "AI存储", "ticker": "300475", "company": "香农芯创", "tier": "core_candidate"},
    {"sector": "AI存储", "ticker": "603986", "company": "兆易创新", "tier": "core_candidate"},
    {"sector": "AI存储", "ticker": "300223", "company": "北京君正", "tier": "satellite"},
    {"sector": "AI存储", "ticker": "001309", "company": "德明利", "tier": "satellite"},
    {"sector": "AI存储", "ticker": "688525", "company": "佰维存储", "tier": "satellite"},
    # Launched / innovative drugs
    {"sector": "创新药", "ticker": "600276", "company": "恒瑞医药", "tier": "core"},
    {"sector": "创新药", "ticker": "688235", "company": "百济神州-U", "tier": "core_candidate"},
    {"sector": "创新药", "ticker": "603087", "company": "甘李药业", "tier": "core_candidate"},
    {"sector": "创新药", "ticker": "002422", "company": "科伦药业", "tier": "satellite"},
    {"sector": "创新药", "ticker": "300558", "company": "贝达药业", "tier": "satellite"},
    {"sector": "创新药", "ticker": "688520", "company": "神州细胞-U", "tier": "satellite"},
    # Launched / defense and commercial aerospace
    {"sector": "国防军工与商业航天", "ticker": "002179", "company": "中航光电", "tier": "core_candidate"},
    {"sector": "国防军工与商业航天", "ticker": "600893", "company": "航发动力", "tier": "core_candidate"},
    {"sector": "国防军工与商业航天", "ticker": "600760", "company": "中航沈飞", "tier": "core_candidate"},
    {"sector": "国防军工与商业航天", "ticker": "600685", "company": "中船防务", "tier": "preview_candidate"},
    {"sector": "国防军工与商业航天", "ticker": "002829", "company": "星网宇达", "tier": "preview_candidate"},
    {"sector": "国防军工与商业航天", "ticker": "600118", "company": "中国卫星", "tier": "satellite"},
    {"sector": "国防军工与商业航天", "ticker": "002049", "company": "紫光国微", "tier": "satellite"},
    # Launched / advanced packaging
    {"sector": "先进封装", "ticker": "002185", "company": "华天科技", "tier": "core_candidate"},
    {"sector": "先进封装", "ticker": "600584", "company": "长电科技", "tier": "core_candidate"},
    {"sector": "先进封装", "ticker": "002156", "company": "通富微电", "tier": "core_candidate"},
    {"sector": "先进封装", "ticker": "000021", "company": "深科技", "tier": "satellite"},
    {"sector": "先进封装", "ticker": "688362", "company": "甬矽电子", "tier": "satellite"},
    {"sector": "先进封装", "ticker": "688630", "company": "芯碁微装", "tier": "equipment_satellite"},
    # Launched / media and AI applications
    {"sector": "传媒与AI应用", "ticker": "002517", "company": "恺英网络", "tier": "core_candidate"},
    {"sector": "传媒与AI应用", "ticker": "002555", "company": "三七互娱", "tier": "core_candidate"},
    {"sector": "传媒与AI应用", "ticker": "300418", "company": "昆仑万维", "tier": "satellite"},
    {"sector": "传媒与AI应用", "ticker": "300413", "company": "芒果超媒", "tier": "satellite"},
    {"sector": "传媒与AI应用", "ticker": "600633", "company": "浙数文化", "tier": "satellite"},
    {"sector": "传媒与AI应用", "ticker": "300459", "company": "汤姆猫", "tier": "satellite"},
    # Newly disclosed preview radar
    {"sector": "业绩预告新雷达", "ticker": "600601", "company": "方正科技", "tier": "preview_candidate"},
    {"sector": "业绩预告新雷达", "ticker": "000636", "company": "风华高科", "tier": "preview_candidate"},
    {"sector": "业绩预告新雷达", "ticker": "001314", "company": "亿道信息", "tier": "preview_candidate"},
    {"sector": "业绩预告新雷达", "ticker": "002407", "company": "多氟多", "tier": "preview_candidate"},
    {"sector": "业绩预告新雷达", "ticker": "002842", "company": "翔鹭钨业", "tier": "preview_candidate"},
]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def normalize_code(value: Any) -> str:
    text = str(value).strip()
    return text.zfill(6) if text.isdigit() else text


def format_date(value: Any) -> str:
    if value is None or pd.isna(value):
        return "not disclosed"
    if isinstance(value, (int, float)) and value > 10_000_000_000:
        return pd.to_datetime(value, unit="ms").strftime("%Y-%m-%d")
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def main() -> None:
    preview_df = ak.stock_yjyg_em(date="20260630")
    raw_records = json.loads(
        preview_df.to_json(orient="records", force_ascii=False, date_format="iso")
    )
    write_json(
        DATA_DIR / "raw_a_share_h1_2026_preview_20260711.json",
        {
            "data_cutoff": "2026-07-11 collection; report period 2026H1",
            "source": "akshare.stock_yjyg_em(date=20260630) / Eastmoney earnings preview",
            "row_count": len(raw_records),
            "rows": raw_records,
        },
    )

    profit_rows = preview_df[
        preview_df["预测指标"].astype(str).eq("归属于上市公司股东的净利润")
    ].copy()
    profit_rows["股票代码"] = profit_rows["股票代码"].map(normalize_code)
    profit_by_code = {
        row["股票代码"]: row for row in profit_rows.to_dict(orient="records")
    }

    matched: list[dict[str, Any]] = []
    for item in UNIVERSE:
        preview = profit_by_code.get(item["ticker"])
        row: dict[str, Any] = {
            **item,
            "preview_status": "disclosed" if preview else "not_found_in_preview_table",
            "preview_type": preview.get("预告类型") if preview else "not disclosed",
            "forecast_metric": preview.get("预测指标") if preview else "not disclosed",
            "forecast_text": preview.get("业绩变动") if preview else "not disclosed",
            "forecast_midpoint_cny": float(preview["预测数值"])
            if preview and pd.notna(preview.get("预测数值"))
            else None,
            "yoy_midpoint_pct": float(preview["业绩变动幅度"])
            if preview and pd.notna(preview.get("业绩变动幅度"))
            else None,
            "reason": preview.get("业绩变动原因") if preview else "not disclosed",
            "prior_period_cny": float(preview["上年同期值"])
            if preview and pd.notna(preview.get("上年同期值"))
            else None,
            "announcement_date": format_date(preview.get("公告日期"))
            if preview
            else "not disclosed",
        }
        matched.append(row)

    sector_counts: dict[str, dict[str, int]] = {}
    for sector in sorted({row["sector"] for row in matched}):
        sector_rows = [row for row in matched if row["sector"] == sector]
        sector_counts[sector] = {
            "universe_count": len(sector_rows),
            "preview_disclosed_count": sum(
                row["preview_status"] == "disclosed" for row in sector_rows
            ),
            "preview_not_found_count": sum(
                row["preview_status"] != "disclosed" for row in sector_rows
            ),
        }

    preview_types = Counter(
        row["preview_type"] for row in matched if row["preview_status"] == "disclosed"
    )
    payload = {
        "schema_version": "astock.core_universe_preview_census.v1",
        "data_cutoff": "2026-07-11 collection; 2026H1 report period",
        "method": "Curated full core/satellite universe cross-referenced against akshare stock_yjyg_em(date=20260630); missing means not found in the captured preview table, not proof that no later filing exists.",
        "universe_count": len(matched),
        "preview_disclosed_count": sum(
            row["preview_status"] == "disclosed" for row in matched
        ),
        "preview_not_found_count": sum(
            row["preview_status"] != "disclosed" for row in matched
        ),
        "sector_counts": sector_counts,
        "preview_type_counts": dict(preview_types),
        "rows": matched,
    }
    write_json(DATA_DIR / "core_universe_preview_census_20260711.json", payload)

    lines = [
        "# Core Universe and 2026H1 Earnings Preview Census",
        "",
        f"- Universe: {payload['universe_count']} names",
        f"- Preview disclosed: {payload['preview_disclosed_count']}",
        f"- Not found in captured preview table: {payload['preview_not_found_count']}",
        f"- Method: {payload['method']}",
        "",
        "## Sector Coverage",
        "",
        "| Sector | Universe | Preview disclosed | Not found |",
        "|---|---:|---:|---:|",
    ]
    for sector, counts in sector_counts.items():
        lines.append(
            f"| {sector} | {counts['universe_count']} | "
            f"{counts['preview_disclosed_count']} | {counts['preview_not_found_count']} |"
        )
    lines += [
        "",
        "## Company Matrix",
        "",
        "| Sector | Tier | Ticker | Company | Status | Type | H1 NP midpoint (CNY100mn) | YoY midpoint | Announcement |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for row in matched:
        midpoint = (
            f"{row['forecast_midpoint_cny'] / 1e8:.2f}"
            if row["forecast_midpoint_cny"] is not None
            else "-"
        )
        yoy = (
            f"{row['yoy_midpoint_pct']:.1f}%"
            if row["yoy_midpoint_pct"] is not None
            else "-"
        )
        lines.append(
            f"| {row['sector']} | {row['tier']} | {row['ticker']} | "
            f"{row['company']} | {row['preview_status']} | {row['preview_type']} | "
            f"{midpoint} | {yoy} | {row['announcement_date']} |"
        )
    lines += [
        "",
        "## Evidence Boundary",
        "",
        "A preview validates company-level earnings direction and refresh timing. It does not prove segment revenue, product ASP, customer allocation, order durability or cash conversion. Rows not found in the captured table must be rechecked against exchange announcements before publication.",
    ]
    write_text(DATA_DIR / "core_universe_preview_census_20260711.md", "\n".join(lines))

    analysis_lines = [
        "# Core Universe Coverage Audit",
        "",
        "This artifact prevents a small hand-picked list from masquerading as sector research.",
        "",
    ]
    for sector, counts in sector_counts.items():
        names = "、".join(
            f"{row['company']}({row['ticker']})"
            for row in matched
            if row["sector"] == sector
        )
        analysis_lines.append(
            f"- **{sector}**: {counts['universe_count']} names; "
            f"{counts['preview_disclosed_count']} previews found. Universe: {names}."
        )
    write_text(
        ANALYSIS_DIR / "core_universe_coverage_audit.md",
        "\n".join(analysis_lines),
    )
    print(
        json.dumps(
            {
                "universe_count": payload["universe_count"],
                "preview_disclosed_count": payload["preview_disclosed_count"],
                "preview_not_found_count": payload["preview_not_found_count"],
                "preview_type_counts": payload["preview_type_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
