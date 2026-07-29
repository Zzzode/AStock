#!/usr/bin/env python3
"""Collect financial and broker evidence for the full-market priority pool."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd
import requests

from astock import capabilities


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "full-market-priority-20260712"
FINANCIAL_DIR = DATA_DIR / "full_market_priority_financials"
REPORT_DIR = SOURCE_DIR / "broker-reports"
CUTOFF = date(2026, 7, 11)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def safe_slug(value: str, limit: int = 48) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value).strip("-")
    return (cleaned or "report")[:limit]


async def collect_financials(codes: list[str]) -> dict[str, dict[str, Any]]:
    semaphore = asyncio.Semaphore(4)

    async def one(code: str) -> tuple[str, dict[str, Any]]:
        async with semaphore:
            try:
                packet = await capabilities.get_financial_statements(code, periods=8)
                return code, packet
            except Exception as exc:
                return code, {
                    "code": code,
                    "data_quality": "unavailable",
                    "error": repr(exc),
                    "periods": [],
                }

    return dict(await asyncio.gather(*(one(code) for code in codes)))


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


def collect_reports(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    report_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, item in enumerate(rows, 1):
        code = item["ticker"]
        company = item["company"]
        try:
            frame = ak.stock_research_report_em(symbol=code)
        except Exception as exc:
            failures.append(
                {"ticker": code, "company": company, "stage": "metadata", "error": repr(exc)}
            )
            report_rows.append(
                {
                    "ticker": code,
                    "company": company,
                    "report_status": "not_found",
                    "latest_report_date": None,
                    "report_age_days": None,
                    "latest_broker": None,
                    "latest_title": None,
                    "latest_2026e_eps": None,
                    "latest_2026e_pe": None,
                    "local_pdf": None,
                    "local_text": None,
                }
            )
            continue
        if frame.empty:
            failures.append(
                {"ticker": code, "company": company, "stage": "metadata", "error": "empty"}
            )
            continue
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
        ok, note = download_pdf(str(report["报告PDF链接"]), pdf_path)
        text_path = pdf_path.with_suffix(".txt")
        if ok:
            completed = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(text_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                note += f"; pdftotext={completed.stderr.strip()}"
        else:
            failures.append(
                {
                    "ticker": code,
                    "company": company,
                    "stage": "pdf",
                    "error": note,
                }
            )
        report_rows.append(
            {
                "ticker": code,
                "company": company,
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
                "local_text": (
                    str(text_path.relative_to(CASE_DIR)) if text_path.exists() else None
                ),
                "source_url": str(report["报告PDF链接"]),
                "note": note,
            }
        )
        print(f"reports {index}/{len(rows)} {code} age={age} status={report_rows[-1]['report_status']}")
    return report_rows, failures


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
            "q1_gross_margin_pct": None,
            "q1_data_quality": packet.get("data_quality"),
            "q1_error": packet.get("error"),
        }
    metrics = period.get("metrics") or {}
    def scale(key: str) -> float | None:
        value = metrics.get(key)
        return round(float(value) / 1e8, 2) if value is not None else None
    return {
        "q1_revenue_100mn": scale("total_revenue"),
        "q1_parent_np_100mn": scale("net_profit_parent"),
        "q1_deducted_np_100mn": scale("net_profit_deducted"),
        "q1_ocf_100mn": scale("operating_cash_flow"),
        "q1_gross_margin_pct": metrics.get("gross_margin"),
        "q1_data_quality": packet.get("data_quality"),
        "q1_error": packet.get("error"),
    }


def main() -> None:
    FINANCIAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    priority = load_json(DATA_DIR / "full_market_priority_pool_20260712.json")["rows"]
    codes = [row["ticker"] for row in priority]
    financials = asyncio.run(collect_financials(codes))
    for code, packet in financials.items():
        write_json(FINANCIAL_DIR / f"{code}_20260712.json", packet)
    reports, failures = collect_reports(priority)
    report_map = {row["ticker"]: row for row in reports}
    rows: list[dict[str, Any]] = []
    for row in priority:
        code = row["ticker"]
        rows.append({**row, **q1_summary(financials[code]), **report_map.get(code, {})})
    payload = {
        "schema_version": "astock.full_market_priority_evidence.v1",
        "data_cutoff": "2026-07-12 collection; market 2026-07-10 close",
        "row_count": len(rows),
        "financial_success_count": sum(row["q1_revenue_100mn"] is not None for row in rows),
        "report_pdf_count": sum(bool(row.get("local_pdf")) for row in rows),
        "failures": failures,
        "rows": rows,
    }
    write_json(DATA_DIR / "full_market_priority_evidence_20260712.json", payload)
    lines = [
        "# Full-Market Priority Evidence",
        "",
        f"- Priority rows: {len(rows)}",
        f"- Q1 financial packets: {payload['financial_success_count']}",
        f"- Latest broker PDFs: {payload['report_pdf_count']}",
        f"- Failures: {len(failures)}",
        "",
        "| Industry | Ticker | Company | Position | H1 NP | Non-recurring | Q1 NP | Q1 OCF | Broker/date | EPS | Report status | Disposition |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['sws_industry']} | {row['ticker']} | {row['company']} | "
            f"{row.get('position_1y_pct')}% | {row['h1_parent_np_midpoint_100mn']:.2f} | "
            f"{row.get('nonrecurring_share_pct')}% | {row.get('q1_parent_np_100mn')} | "
            f"{row.get('q1_ocf_100mn')} | {row.get('latest_broker')}/{row.get('latest_report_date')} | "
            f"{row.get('latest_2026e_eps')} | {row.get('report_status')} | "
            f"{row['full_market_disposition']} |"
        )
    markdown = "\n".join(lines)
    write_text(DATA_DIR / "full_market_priority_evidence_20260712.md", markdown)
    write_text(CASE_DIR / "analysis" / "full_market_priority_evidence.md", markdown)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "financials": payload["financial_success_count"],
                "pdfs": payload["report_pdf_count"],
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
