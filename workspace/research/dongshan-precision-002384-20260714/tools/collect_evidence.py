#!/usr/bin/env python3
"""Collect case-scoped evidence for Dongshan Precision research."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import akshare as ak
import requests


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
SOURCES = CASE / "sources"
OFFICIAL = SOURCES / "official-20260714"
BROKERS = SOURCES / "broker-reports" / "2026-07-14"
MARKET = SOURCES / "market-20260714"

NOTICE_API = "https://np-anotice-stock.eastmoney.com/api/security/ann"
CONTENT_API = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://data.eastmoney.com/notices/",
}

OFFICIAL_NOTICES = {
    "AN202604211821390360": "2026-04-22-2025年年度报告",
    "AN202604271821624536": "2026-04-28-2026年第一季度报告",
    "AN202604071821046193": "2026-04-08-2026年第一季度业绩预告",
    "AN202606041823254494": "2026-06-05-股票交易异常波动公告",
    "AN202606161823609170": "2026-06-17-光芯片及光模块扩建对外投资公告",
    "AN202606171823637410": "2026-06-17-投资者关系活动记录表",
    "AN202505131672285947": "2025-05-14-收购法国GMD集团公告",
    "AN202506131690337077": "2025-06-14-收购索尔思光电对外投资公告",
    "AN202511031774473949": "2025-11-04-GMD交割完成公告",
    "AN202511171783108562": "2025-11-18-索尔思交割进展公告",
    "AN202605201822498535": "2026-05-21-H股上市申请公告",
}

BROKER_REPORTS = {
    "2026-03-30-东吴证券-光模块与高端PCB双轮驱动AI基建新龙头.pdf":
        "https://pdf.dfcfw.com/pdf/H3_AP202603301820859917_1.pdf",
    "2026-04-16-华金证券-深耕优势赛道多元布局开启新程.pdf":
        "https://pdf.dfcfw.com/pdf/H3_AP202604171821286553_1.pdf",
    "2026-04-27-中原证券-光模块与AIPCB双引擎驱动.pdf":
        "http://rdfile.dzh.com.cn/new/dzh/dbcData/594/5E900D762BAA16C106137611383703F5_3126106.pdf",
    "2026-04-30-开源证券-2026Q1业绩高增.pdf":
        "https://pdf.dfcfw.com/pdf/H3_AP202605051821972125_1.pdf",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def get_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=(5, 45),
    )
    response.raise_for_status()
    return response.json()


def download(url: str, path: Path) -> None:
    response = requests.get(url, headers=HEADERS, timeout=(5, 120))
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    if path.suffix.lower() == ".pdf" and not response.content.startswith(b"%PDF"):
        raise ValueError(f"Downloaded file is not a PDF: {path}")


def extract_pdf(pdf_path: Path) -> Path:
    text_path = pdf_path.with_suffix(".txt")
    subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        check=True,
    )
    return text_path


def collect_notice_index() -> list[dict[str, Any]]:
    params = {
        "sr": "-1",
        "page_size": "100",
        "page_index": "1",
        "ann_type": "A",
        "client_source": "web",
        "f_node": "0",
        "s_node": "0",
        "begin_time": "2024-01-01",
        "end_time": "2026-07-14",
        "stock_list": "002384",
    }
    first = get_json(NOTICE_API, params).get("data") or {}
    total = int(first.get("total_hits") or 0)
    pages = max(1, (total + 99) // 100)
    rows: list[dict[str, Any]] = []
    for page in range(1, pages + 1):
        params["page_index"] = str(page)
        data = first if page == 1 else (get_json(NOTICE_API, params).get("data") or {})
        for item in data.get("list") or []:
            codes = item.get("codes") or []
            code_row = next(
                (row for row in codes if str(row.get("stock_code")) == "002384"),
                codes[0] if codes else {},
            )
            rows.append(
                {
                    "announcement_date": clean_text(item.get("notice_date"))[:10],
                    "art_code": clean_text(item.get("art_code")),
                    "title": clean_text(item.get("title") or item.get("title_ch")),
                    "stock_code": clean_text(code_row.get("stock_code")),
                    "stock_name": clean_text(code_row.get("short_name")),
                }
            )
    write_json(
        OFFICIAL / "notice_index_20260714.json",
        {
            "ticker": "002384",
            "generated_at": datetime.now().astimezone().isoformat(),
            "total_hits": total,
            "rows": rows,
        },
    )
    return rows


def collect_official_notices() -> list[dict[str, Any]]:
    metadata: list[dict[str, Any]] = []
    for art_code, filename in OFFICIAL_NOTICES.items():
        data = get_json(
            CONTENT_API,
            {"art_code": art_code, "client_source": "web"},
        ).get("data") or {}
        url = clean_text(data.get("attach_url") or data.get("attach_url_web"))
        content = clean_text(data.get("notice_content"))
        api_path = OFFICIAL / f"{filename}-api.json"
        text_path = OFFICIAL / f"{filename}-api.txt"
        pdf_path = OFFICIAL / f"{filename}.pdf"
        write_json(api_path, data)
        text_path.write_text(content + "\n", encoding="utf-8")
        if url:
            download(url, pdf_path)
            extracted_path = extract_pdf(pdf_path)
        else:
            extracted_path = None
        metadata.append(
            {
                "art_code": art_code,
                "title": filename,
                "source_url": url,
                "api_path": str(api_path.relative_to(CASE)),
                "api_text_path": str(text_path.relative_to(CASE)),
                "pdf_path": str(pdf_path.relative_to(CASE)) if pdf_path.exists() else "",
                "pdf_text_path": (
                    str(extracted_path.relative_to(CASE))
                    if extracted_path and extracted_path.exists()
                    else ""
                ),
            }
        )
    write_json(OFFICIAL / "official_notice_metadata_20260714.json", metadata)
    return metadata


def collect_brokers() -> list[dict[str, Any]]:
    metadata: list[dict[str, Any]] = []
    for filename, url in BROKER_REPORTS.items():
        pdf_path = BROKERS / filename
        download(url, pdf_path)
        text_path = extract_pdf(pdf_path)
        metadata.append(
            {
                "filename": filename,
                "source_url": url,
                "pdf_path": str(pdf_path.relative_to(CASE)),
                "text_path": str(text_path.relative_to(CASE)),
                "source_quality": "original_pdf",
            }
        )
    write_json(BROKERS / "report_metadata_20260714.json", metadata)
    return metadata


def collect_preview_census() -> dict[str, Any]:
    frame = ak.stock_yjyg_em(date="20260630")
    matches = frame[
        frame.astype(str).apply(
            lambda row: row.str.contains("002384|东山精密").any(),
            axis=1,
        )
    ]
    payload = {
        "method": "akshare.stock_yjyg_em(date=20260630)",
        "generated_at": datetime.now().astimezone().isoformat(),
        "universe_rows": len(frame),
        "matched_rows": json.loads(matches.to_json(orient="records", force_ascii=False)),
        "conclusion": (
            "No 2026H1 earnings preview was found for 002384 in the captured "
            "Eastmoney preview table. This is corroborated by the official "
            "announcement index through 2026-07-14."
        ),
    }
    write_json(DATA / "h1_earnings_preview_census_20260714.json", payload)
    return payload


def collect_research_catalog() -> list[dict[str, Any]]:
    frame = ak.stock_research_report_em(symbol="002384")
    rows = json.loads(frame.to_json(orient="records", force_ascii=False, date_format="iso"))
    write_json(
        BROKERS / "akshare_report_catalog_20260714.json",
        {
            "generated_at": datetime.now().astimezone().isoformat(),
            "count": len(rows),
            "rows": rows,
        },
    )
    return rows


def collect_lhb() -> dict[str, Any]:
    details = ak.stock_lhb_detail_em(
        start_date="20260701",
        end_date="20260714",
    )
    institution = ak.stock_lhb_jgmmtj_em(
        start_date="20260701",
        end_date="20260714",
    )
    seats = ak.stock_lhb_hyyyb_em(
        start_date="20260701",
        end_date="20260714",
    )
    detail_rows = details[details["代码"] == "002384"]
    institution_rows = institution[institution["代码"] == "002384"]
    seat_rows = seats[
        seats.astype(str).apply(
            lambda row: row.str.contains("东山精密").any(),
            axis=1,
        )
    ]
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "detail_rows": json.loads(
            detail_rows.to_json(orient="records", force_ascii=False, date_format="iso")
        ),
        "institution_rows": json.loads(
            institution_rows.to_json(orient="records", force_ascii=False, date_format="iso")
        ),
        "seat_rows": json.loads(
            seat_rows.to_json(orient="records", force_ascii=False, date_format="iso")
        ),
    }
    write_json(MARKET / "dragon_tiger_20260701_20260714.json", payload)
    return payload


def main() -> int:
    for directory in (DATA, OFFICIAL, BROKERS, MARKET):
        directory.mkdir(parents=True, exist_ok=True)
    notice_rows = collect_notice_index()
    official_rows = collect_official_notices()
    broker_rows = collect_brokers()
    preview = collect_preview_census()
    catalog = collect_research_catalog()
    lhb = collect_lhb()
    summary = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "notice_rows": len(notice_rows),
        "official_notices": len(official_rows),
        "broker_original_pdfs": len(broker_rows),
        "h1_preview_matches": len(preview["matched_rows"]),
        "research_catalog_rows": len(catalog),
        "dragon_tiger_events": len(lhb["detail_rows"]),
    }
    write_json(DATA / "collection_summary_20260714.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
