#!/usr/bin/env python3
"""Collect financial and broker evidence for all full-market valuation candidates."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from datetime import date
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd
import requests

from astock import capabilities


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "full-market-valuation-20260712"
REPORT_DIR = SOURCE_DIR / "broker-reports"
FINANCIAL_DIR = DATA_DIR / "full_market_candidate_financials"
CUTOFF = date(2026, 7, 11)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def safe_slug(value: str, limit: int = 54) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value).strip("-")
    return (cleaned or "report")[:limit]


async def collect_financials(codes: list[str]) -> dict[str, dict[str, Any]]:
    semaphore = asyncio.Semaphore(5)

    async def one(code: str) -> tuple[str, dict[str, Any]]:
        cache_path = FINANCIAL_DIR / f"{code}_20260712.json"
        if cache_path.exists() and cache_path.stat().st_size:
            return code, load_json(cache_path)
        priority_path = DATA_DIR / "full_market_priority_financials" / f"{code}_20260712.json"
        if priority_path.exists() and priority_path.stat().st_size:
            packet = load_json(priority_path)
            write_json(cache_path, packet)
            return code, packet
        async with semaphore:
            try:
                packet = await capabilities.get_financial_statements(code, periods=8)
            except Exception as exc:
                packet = {
                    "code": code,
                    "data_quality": "unavailable",
                    "error": repr(exc),
                    "periods": [],
                }
            write_json(cache_path, packet)
            return code, packet

    return dict(await asyncio.gather(*(one(code) for code in codes)))


def q1_summary(packet: dict[str, Any]) -> dict[str, Any]:
    period = next(
        (
            row
            for row in packet.get("periods", [])
            if str(row.get("period")) == "20260331"
        ),
        None,
    )
    if period is None:
        return {
            "q1_revenue_100mn": None,
            "q1_parent_np_100mn": None,
            "q1_deducted_np_100mn": None,
            "q1_ocf_100mn": None,
            "q1_eps": None,
            "q1_bps": None,
            "q1_gross_margin_pct": None,
            "q1_net_margin_pct": None,
            "q1_data_quality": packet.get("data_quality"),
            "q1_error": packet.get("error"),
        }
    metrics = period.get("metrics") or {}

    def scale(key: str) -> float | None:
        value = metrics.get(key)
        return round(float(value) / 1e8, 4) if value is not None else None

    return {
        "q1_revenue_100mn": scale("total_revenue"),
        "q1_parent_np_100mn": scale("net_profit_parent"),
        "q1_deducted_np_100mn": scale("net_profit_deducted"),
        "q1_ocf_100mn": scale("operating_cash_flow"),
        "q1_eps": metrics.get("eps_basic"),
        "q1_bps": metrics.get("bps"),
        "q1_gross_margin_pct": metrics.get("gross_margin"),
        "q1_net_margin_pct": metrics.get("net_margin"),
        "q1_data_quality": packet.get("data_quality"),
        "q1_error": packet.get("error"),
    }


def parse_target(text: str) -> dict[str, Any]:
    normalized = re.sub(r"[\u00a0\s]+", " ", text)
    range_patterns = (
        r"合理估值(?:区间)?(?:为|在|在\s*)?\s*(\d+(?:\.\d+)?)\s*[-~—至]+\s*(\d+(?:\.\d+)?)\s*元",
        r"合理价值(?:区间)?(?:为|在|在\s*)?\s*(\d+(?:\.\d+)?)\s*[-~—至]+\s*(\d+(?:\.\d+)?)\s*元",
        r"目标价(?:格)?区间\s*[：:]?\s*(\d+(?:\.\d+)?)\s*[-~—至]+\s*(\d+(?:\.\d+)?)\s*元",
        r"合理估值\s*(\d+(?:\.\d+)?)\s*[-~—至]+\s*(\d+(?:\.\d+)?)\s*元",
    )
    for pattern in range_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            low, high = sorted((float(match.group(1)), float(match.group(2))))
            return {
                "target_price": round((low + high) / 2, 2),
                "target_low": low,
                "target_high": high,
                "target_extract": match.group(0),
                "target_type": "range",
            }
    point_patterns = (
        r"目标价(?:格)?\s*[：:]?\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*元?",
        r"目标价\s*[（(]\s*元\s*[）)]\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*元?",
        r"目标价格\s*[：:]?\s*(\d+(?:\.\d+)?)\s*元",
        r"目标价\s+(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*(?:人民币|元)?",
        r"目标价人\s*民币\s*(\d+(?:\.\d+)?)",
        r"对应目标价(?:为)?\s*(\d+(?:\.\d+)?)\s*元",
        r"6\s*个月目标价\s*(\d+(?:\.\d+)?)\s*元",
        r"(?:TP|target price|12M TP|new TP)\s*(?:of|to)?\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)",
    )
    for pattern in point_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return {
                "target_price": float(match.group(1)),
                "target_low": float(match.group(1)),
                "target_high": float(match.group(1)),
                "target_extract": match.group(0),
                "target_type": "point",
            }
    return {
        "target_price": None,
        "target_low": None,
        "target_high": None,
        "target_extract": None,
        "target_type": "not_disclosed",
    }


def download_pdf(url: str, path: Path) -> tuple[bool, str]:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=45,
        )
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            return False, "body is not PDF"
        path.write_bytes(response.content)
        return True, "ok"
    except Exception as exc:
        return False, repr(exc)


def existing_priority_map() -> dict[str, dict[str, Any]]:
    path = DATA_DIR / "full_market_priority_evidence_20260712.json"
    if not path.exists():
        return {}
    return {row["ticker"]: row for row in load_json(path)["rows"]}


def collect_report(code: str, company: str, priority: dict[str, Any] | None) -> tuple[dict[str, Any], list[dict[str, str]]]:
    failures: list[dict[str, str]] = []
    if priority and priority.get("local_text"):
        text_path = CASE_DIR / priority["local_text"]
        text = text_path.read_text(errors="ignore") if text_path.exists() else ""
        return {
            "report_status": priority.get("report_status"),
            "latest_report_date": priority.get("latest_report_date"),
            "report_age_days": priority.get("report_age_days"),
            "latest_broker": priority.get("latest_broker"),
            "latest_title": priority.get("latest_title"),
            "latest_rating": priority.get("latest_rating"),
            "latest_2026e_eps": priority.get("latest_2026e_eps"),
            "latest_2026e_pe": priority.get("latest_2026e_pe"),
            "local_pdf": priority.get("local_pdf"),
            "local_text": priority.get("local_text"),
            "source_url": priority.get("source_url"),
            "report_note": priority.get("note"),
            **parse_target(text),
        }, failures

    last_error: Exception | None = None
    frame: pd.DataFrame | None = None
    for attempt in range(3):
        try:
            frame = ak.stock_research_report_em(symbol=code)
            break
        except Exception as exc:
            last_error = exc
            time.sleep(0.8 + attempt)
    if frame is None:
        failures.append(
            {
                "ticker": code,
                "company": company,
                "stage": "metadata",
                "error": repr(last_error),
            }
        )
        return {
            "report_status": "not_found",
            "latest_report_date": None,
            "report_age_days": None,
            "latest_broker": None,
            "latest_title": None,
            "latest_rating": None,
            "latest_2026e_eps": None,
            "latest_2026e_pe": None,
            "local_pdf": None,
            "local_text": None,
            "source_url": None,
            "report_note": repr(last_error),
            **parse_target(""),
        }, failures
    if frame.empty:
        failures.append(
            {"ticker": code, "company": company, "stage": "metadata", "error": "empty"}
        )
        return {
            "report_status": "not_found",
            "latest_report_date": None,
            "report_age_days": None,
            "latest_broker": None,
            "latest_title": None,
            "latest_rating": None,
            "latest_2026e_eps": None,
            "latest_2026e_pe": None,
            "local_pdf": None,
            "local_text": None,
            "source_url": None,
            "report_note": "empty",
            **parse_target(""),
        }, failures

    frame = frame.copy()
    frame["日期"] = pd.to_datetime(frame["日期"])
    frame.sort_values("日期", ascending=False, inplace=True)
    report = frame.iloc[0]
    report_date = report["日期"].date()
    age = (CUTOFF - report_date).days
    ticker_dir = REPORT_DIR / f"{code}-{safe_slug(company)}"
    ticker_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = ticker_dir / (
        f"{report_date.isoformat()}-{safe_slug(str(report['机构']), 18)}-"
        f"{safe_slug(str(report['报告名称']))}.pdf"
    )
    text_path = pdf_path.with_suffix(".txt")
    if pdf_path.exists() and pdf_path.read_bytes().startswith(b"%PDF"):
        ok, note = True, "cached"
    else:
        ok, note = download_pdf(str(report["报告PDF链接"]), pdf_path)
    if ok and not text_path.exists():
        completed = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(text_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            note += f"; pdftotext={completed.stderr.strip()}"
    if not ok:
        failures.append(
            {"ticker": code, "company": company, "stage": "pdf", "error": note}
        )
    text = text_path.read_text(errors="ignore") if text_path.exists() else ""
    ticker_match = code in text or company in text
    if ok and not ticker_match:
        failures.append(
            {
                "ticker": code,
                "company": company,
                "stage": "pdf_validation",
                "error": "ticker/company not found in extracted text",
            }
        )
    return {
        "report_status": (
            "current" if age <= 90 else "aging" if age <= 180 else "stale"
        ),
        "latest_report_date": report_date.isoformat(),
        "report_age_days": age,
        "latest_broker": str(report["机构"]),
        "latest_title": str(report["报告名称"]),
        "latest_rating": str(report["东财评级"]),
        "latest_2026e_eps": (
            float(report["2026-盈利预测-收益"])
            if pd.notna(report.get("2026-盈利预测-收益"))
            else None
        ),
        "latest_2026e_pe": (
            float(report["2026-盈利预测-市盈率"])
            if pd.notna(report.get("2026-盈利预测-市盈率"))
            else None
        ),
        "local_pdf": str(pdf_path.relative_to(CASE_DIR)) if ok else None,
        "local_text": str(text_path.relative_to(CASE_DIR)) if text_path.exists() else None,
        "source_url": str(report["报告PDF链接"]),
        "report_note": note,
        **parse_target(text),
    }, failures


def main() -> None:
    FINANCIAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_json(DATA_DIR / "full_market_preview_candidates_20260712.json")[
        "rows"
    ]
    codes = [row["ticker"] for row in candidates]
    financials = asyncio.run(collect_financials(codes))
    priority_map = existing_priority_map()
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, candidate in enumerate(candidates, 1):
        code = candidate["ticker"]
        report, report_failures = collect_report(
            code, candidate["company"], priority_map.get(code)
        )
        failures.extend(report_failures)
        row = {
            **candidate,
            **q1_summary(financials[code]),
            **report,
        }
        if row.get("latest_report_date") and candidate.get("announcement_date"):
            report_date = pd.Timestamp(row["latest_report_date"])
            preview_date = pd.Timestamp(candidate["announcement_date"])
            row["report_vs_preview"] = (
                "post_preview"
                if report_date > preview_date
                else "same_day_as_preview"
                if report_date == preview_date
                else "pre_preview_forecast_may_be_stale"
            )
        else:
            row["report_vs_preview"] = "not_found"
        rows.append(row)
        print(
            f"{index}/{len(candidates)} {code} "
            f"financial={row['q1_data_quality']} report={row['report_status']} "
            f"target={row['target_price']}"
        )

    payload = {
        "schema_version": "astock.full_market_valuation_evidence.v1",
        "data_cutoff": "2026-07-12 collection; market 2026-07-10 close",
        "row_count": len(rows),
        "financial_success_count": sum(
            row.get("q1_revenue_100mn") is not None for row in rows
        ),
        "report_metadata_count": sum(
            row.get("latest_report_date") is not None for row in rows
        ),
        "report_pdf_count": sum(bool(row.get("local_pdf")) for row in rows),
        "target_extract_count": sum(
            row.get("target_price") is not None for row in rows
        ),
        "failures": failures,
        "rows": rows,
    }
    write_json(DATA_DIR / "full_market_valuation_evidence_20260712.json", payload)
    lines = [
        "# Full-Market Valuation Evidence",
        "",
        f"- Candidate rows: {payload['row_count']}",
        f"- Q1 financial packets: {payload['financial_success_count']}",
        f"- Report metadata: {payload['report_metadata_count']}",
        f"- Original broker PDFs: {payload['report_pdf_count']}",
        f"- Extracted broker target/ranges: {payload['target_extract_count']}",
        f"- Failed probes: {len(failures)}",
        "",
        "| Ticker | Company | Industry | Q1 NP | H1 NP | Broker/date | 2026E EPS | Target/range | Timing | PDF |",
        "|---|---|---|---:|---:|---|---:|---|---|---|",
    ]
    for row in rows:
        target = (
            f"{row['target_low']}-{row['target_high']}"
            if row.get("target_low") is not None
            else "-"
        )
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['sws_industry']} | "
            f"{row.get('q1_parent_np_100mn')} | {row.get('h1_parent_np_midpoint_100mn')} | "
            f"{row.get('latest_broker')}/{row.get('latest_report_date')} | "
            f"{row.get('latest_2026e_eps')} | {target} | "
            f"{row.get('report_vs_preview')} | {row.get('local_pdf')} |"
        )
    write_text(
        DATA_DIR / "full_market_valuation_evidence_20260712.md", "\n".join(lines)
    )
    write_text(
        CASE_DIR / "analysis" / "full_market_valuation_evidence.md",
        "\n".join(lines),
    )
    print(
        json.dumps(
            {
                "rows": payload["row_count"],
                "financials": payload["financial_success_count"],
                "reports": payload["report_metadata_count"],
                "pdfs": payload["report_pdf_count"],
                "targets": payload["target_extract_count"],
                "failures": len(failures),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
