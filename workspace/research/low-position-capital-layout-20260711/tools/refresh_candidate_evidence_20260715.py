#!/usr/bin/env python3
"""Refresh Q1 financial packets and latest broker metadata for the new priority pool."""

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
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
FINANCIAL_DIR = DATA_DIR / "financials"
SOURCE_DIR = REFRESH_DIR / "sources" / "broker-reports-20260715"
CUTOFF = date(2026, 7, 15)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def safe_slug(value: str, limit: int = 54) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value).strip("-")
    return (cleaned or "report")[:limit]


async def collect_financials(codes: list[str]) -> dict[str, dict[str, Any]]:
    semaphore = asyncio.Semaphore(6)

    async def one(code: str) -> tuple[str, dict[str, Any]]:
        path = FINANCIAL_DIR / f"{code}_20260715.json"
        if path.exists() and path.stat().st_size:
            return code, load_json(path)
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
            write_json(path, packet)
            return code, packet

    return dict(await asyncio.gather(*(one(code) for code in codes)))


def q1_summary(packet: dict[str, Any]) -> dict[str, Any]:
    period = next(
        (
            item
            for item in packet.get("periods", [])
            if str(item.get("period")) == "20260331"
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
    patterns = (
        r"目标价(?:格)?\s*[：:]?\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*元?",
        r"目标价\s*[（(]\s*元\s*[）)]\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*元?",
        r"目标价\s+(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)\s*(?:人民币|元)?",
        r"目标价人\s*民币\s*(\d+(?:\.\d+)?)",
        r"对应目标价(?:为)?\s*(\d+(?:\.\d+)?)\s*元",
        r"对应每股价值(?:为)?\s*(\d+(?:\.\d+)?)\s*元",
        r"每股合理价值(?:为)?\s*(\d+(?:\.\d+)?)\s*元",
        r"6\s*个月目标价\s*(\d+(?:\.\d+)?)\s*元",
        r"(?:TP|target price|12M TP|new TP)\s*(?:of|to)?\s*(?:人民币|RMB|CNY)?\s*(\d+(?:\.\d+)?)",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            return {
                "target_price": value,
                "target_low": value,
                "target_high": value,
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        return True, "ok"
    except Exception as exc:
        return False, repr(exc)


def collect_report(
    ticker: str, company: str
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    failures: list[dict[str, str]] = []
    try:
        frame = ak.stock_research_report_em(symbol=ticker)
    except Exception as exc:
        return {
            "report_status": "not_found",
            "report_error": repr(exc),
            "latest_report_date": None,
            "latest_broker": None,
            "latest_title": None,
            "latest_2026e_eps": None,
            "latest_2026e_pe": None,
            "local_pdf": None,
            "local_text": None,
            **parse_target(""),
        }, [
            {"ticker": ticker, "company": company, "stage": "metadata", "error": repr(exc)}
        ]
    if frame.empty:
        return {
            "report_status": "not_found",
            "report_error": "empty",
            "latest_report_date": None,
            "latest_broker": None,
            "latest_title": None,
            "latest_2026e_eps": None,
            "latest_2026e_pe": None,
            "local_pdf": None,
            "local_text": None,
            **parse_target(""),
        }, [
            {"ticker": ticker, "company": company, "stage": "metadata", "error": "empty"}
        ]

    frame = frame.copy()
    frame["日期"] = pd.to_datetime(frame["日期"])
    frame.sort_values("日期", ascending=False, inplace=True)
    directory = SOURCE_DIR / f"{ticker}-{safe_slug(company)}"
    latest_report = frame.iloc[0]
    latest_date = latest_report["日期"].date()
    latest_age = (CUTOFF - latest_date).days
    selected: dict[str, Any] | None = None
    archived: list[dict[str, Any]] = []
    for _, report in frame.head(8).iterrows():
        report_date = report["日期"].date()
        age = (CUTOFF - report_date).days
        pdf_path = directory / (
            f"{report_date.isoformat()}-{safe_slug(str(report['机构']), 18)}-"
            f"{safe_slug(str(report['报告名称']))}.pdf"
        )
        if pdf_path.exists() and pdf_path.read_bytes().startswith(b"%PDF"):
            ok, note = True, "cached"
        else:
            ok, note = download_pdf(str(report["报告PDF链接"]), pdf_path)
        text_path = pdf_path.with_suffix(".txt")
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
                {"ticker": ticker, "company": company, "stage": "pdf", "error": note}
            )
        text = text_path.read_text(errors="ignore") if text_path.exists() else ""
        if ok and ticker not in text and company not in text:
            failures.append(
                {
                    "ticker": ticker,
                    "company": company,
                    "stage": "pdf_validation",
                    "error": "ticker/company absent in text",
                }
            )
        target = parse_target(text)
        candidate = {
            "report": report,
            "report_date": report_date,
            "age": age,
            "ok": ok,
            "note": note,
            "pdf_path": pdf_path,
            "text_path": text_path,
            "target": target,
        }
        archived.append(candidate)
        if selected is None:
            selected = candidate
        if ok and target.get("target_price") is not None and age <= 365:
            selected = candidate
            break
    if selected is None:
        selected = {
            "report": latest_report,
            "report_date": latest_date,
            "age": latest_age,
            "ok": False,
            "note": "no downloadable report",
            "pdf_path": directory / "not-found.pdf",
            "text_path": directory / "not-found.txt",
            "target": parse_target(""),
        }
    report = selected["report"]
    report_date = selected["report_date"]
    age = selected["age"]
    ok = bool(selected["ok"])
    note = str(selected["note"])
    pdf_path = selected["pdf_path"]
    text_path = selected["text_path"]
    target = selected["target"]
    selected_is_latest = report_date == latest_date and str(report["机构"]) == str(latest_report["机构"])
    archived_target_reports = [
        {
            "report_date": item["report_date"].isoformat(),
            "broker": str(item["report"]["机构"]),
            "title": str(item["report"]["报告名称"]),
            "target_price": item["target"].get("target_price"),
            "source_path": str(item["pdf_path"].relative_to(CASE_DIR))
            if item["ok"]
            else None,
        }
        for item in archived
        if item["target"].get("target_price") is not None
    ]
    return {
        "report_status": "current" if age <= 90 else "aging" if age <= 180 else "stale",
        "report_age_days": age,
        "latest_report_date": report_date.isoformat(),
        "latest_metadata_report_date": latest_date.isoformat(),
        "selected_report_is_latest": selected_is_latest,
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
        "local_text": str(text_path.relative_to(CASE_DIR))
        if text_path.exists()
        else None,
        "source_url": str(report["报告PDF链接"]),
        "report_note": note,
        "archived_target_reports": archived_target_reports,
        **target,
    }, failures


def main() -> None:
    packet = load_json(DATA_DIR / "full_market_candidates_20260715.json")
    priority = load_json(DATA_DIR / "full_market_priority_pool_20260715.json")["rows"]
    codes = [row["ticker"] for row in priority]
    financials = asyncio.run(collect_financials(codes))
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, candidate in enumerate(priority, 1):
        report, report_failures = collect_report(
            candidate["ticker"], candidate["company"]
        )
        failures.extend(report_failures)
        rows.append(
            {
                **candidate,
                **q1_summary(financials[candidate["ticker"]]),
                **report,
            }
        )
        print(
            f"{index}/{len(priority)} {candidate['ticker']} "
            f"financial={rows[-1]['q1_data_quality']} "
            f"report={rows[-1]['report_status']}"
        )
    result = {
        "schema_version": "astock.full_market_priority_evidence.refresh.v1",
        "data_cutoff": str(CUTOFF),
        "row_count": len(rows),
        "financial_success_count": sum(
            row.get("q1_revenue_100mn") is not None for row in rows
        ),
        "report_pdf_count": sum(bool(row.get("local_pdf")) for row in rows),
        "report_metadata_count": sum(bool(row.get("latest_report_date")) for row in rows),
        "failures": failures,
        "source_priority_pool": "data/full_market_priority_pool_20260715.json",
        "rows": rows,
    }
    write_json(DATA_DIR / "full_market_priority_evidence_20260715.json", result)
    lines = [
        "# Full-Market Priority Evidence Through 2026-07-15",
        "",
        f"- Priority rows: {len(rows)}",
        f"- Q1 financial packets: {result['financial_success_count']}",
        f"- Latest broker PDFs: {result['report_pdf_count']}",
        f"- Report metadata rows: {result['report_metadata_count']}",
        f"- Failures: {len(failures)}",
        "",
        "| Industry | Ticker | Company | Position | H1 NP | H1 deducted | Q1 NP | Q1 OCF | Broker/date | EPS | Report status | Disposition |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['sws_industry']} | {row['ticker']} | {row['company']} | "
            f"{row.get('position_1y_pct')}% | {row.get('h1_parent_np_midpoint_100mn')} | "
            f"{row.get('h1_deducted_np_midpoint_100mn')} | "
            f"{row.get('q1_parent_np_100mn')} | {row.get('q1_ocf_100mn')} | "
            f"{row.get('latest_broker')}/{row.get('latest_report_date')} | "
            f"{row.get('latest_2026e_eps')} | {row.get('report_status')} | "
            f"{row.get('full_market_disposition')} |"
        )
    if failures:
        lines += ["", "## Failures", ""]
        lines.extend(
            f"- {failure['ticker']} {failure['stage']}: {failure['error']}"
            for failure in failures
        )
    write_text(DATA_DIR / "full_market_priority_evidence_20260715.md", "\n".join(lines))
    print(
        json.dumps(
            {
                "rows": len(rows),
                "financials": result["financial_success_count"],
                "reports": result["report_metadata_count"],
                "pdfs": result["report_pdf_count"],
                "failures": len(failures),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
