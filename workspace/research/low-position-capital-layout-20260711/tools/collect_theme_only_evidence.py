#!/usr/bin/env python3
"""Collect financials and original broker PDFs for theme-only report names."""

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
SOURCE_DIR = CASE_DIR / "sources" / "theme-only-evidence-20260713"
FINANCIAL_DIR = DATA_DIR / "theme_only_financials"
CUTOFF = date(2026, 7, 13)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def safe_slug(value: str, limit: int = 52) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value).strip("-")
    return (cleaned or "report")[:limit]


async def collect_financials(codes: list[str]) -> dict[str, dict[str, Any]]:
    semaphore = asyncio.Semaphore(5)

    async def one(code: str) -> tuple[str, dict[str, Any]]:
        cache = FINANCIAL_DIR / f"{code}_20260713.json"
        if cache.exists() and cache.stat().st_size:
            return code, load_json(cache)
        candidates = [
            DATA_DIR / "all_core_financials" / f"{code}_20260710.json",
            DATA_DIR / "core_financials" / f"{code}_20260710.json",
        ]
        existing = next((path for path in candidates if path.exists() and path.stat().st_size), None)
        if existing:
            packet = load_json(existing)
        else:
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
        write_json(cache, packet)
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
            "financial_quality": packet.get("data_quality"),
            "financial_error": packet.get("error"),
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
        "financial_quality": packet.get("data_quality"),
        "financial_error": packet.get("error"),
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


def archive_report(code: str, company: str, report: pd.Series, label: str) -> dict[str, Any]:
    report_date = pd.Timestamp(report["日期"]).date()
    directory = SOURCE_DIR / f"{code}-{safe_slug(company)}"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (
        f"{label}-{report_date.isoformat()}-{safe_slug(str(report['机构']), 18)}-"
        f"{safe_slug(str(report['报告名称']))}.pdf"
    )
    if path.exists() and path.read_bytes().startswith(b"%PDF"):
        ok, note = True, "cached"
    else:
        ok, note = download_pdf(str(report["报告PDF链接"]), path)
    text_path = path.with_suffix(".txt")
    if ok and not text_path.exists():
        completed = subprocess.run(
            ["pdftotext", "-layout", str(path), str(text_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            note += f"; pdftotext={completed.stderr.strip()}"
    text = text_path.read_text(errors="ignore") if text_path.exists() else ""
    text_compact = re.sub(r"\s+", "", text)
    content_match = code in text_compact or company in text_compact
    scanned_or_unextractable = ok and len(text_compact) < 80
    valid = ok and (content_match or scanned_or_unextractable)
    if scanned_or_unextractable:
        note += "; scanned_or_unextractable_pdf_validated_by_metadata"
    return {
        "label": label,
        "report_date": report_date.isoformat(),
        "report_age_days": (CUTOFF - report_date).days,
        "broker": str(report["机构"]),
        "title": str(report["报告名称"]),
        "rating": str(report["东财评级"]),
        "eps_2026e": (
            float(report["2026-盈利预测-收益"])
            if pd.notna(report.get("2026-盈利预测-收益"))
            else None
        ),
        "pe_2026e": (
            float(report["2026-盈利预测-市盈率"])
            if pd.notna(report.get("2026-盈利预测-市盈率"))
            else None
        ),
        "source_url": str(report["报告PDF链接"]),
        "local_pdf": str(path.relative_to(CASE_DIR)) if ok else None,
        "local_text": str(text_path.relative_to(CASE_DIR)) if text_path.exists() else None,
        "pdf_valid": valid,
        "note": note,
    }


def collect_reports(code: str, company: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    failures: list[dict[str, str]] = []
    frame: pd.DataFrame | None = None
    error: Exception | None = None
    for attempt in range(3):
        try:
            frame = ak.stock_research_report_em(symbol=code)
            break
        except Exception as exc:
            error = exc
            time.sleep(0.8 + attempt)
    if frame is None or frame.empty:
        failures.append(
            {
                "ticker": code,
                "company": company,
                "stage": "metadata",
                "error": repr(error) if error else "empty",
            }
        )
        return [], failures
    frame = frame.copy()
    frame["日期"] = pd.to_datetime(frame["日期"])
    frame.sort_values("日期", ascending=False, inplace=True)
    selected: list[tuple[str, pd.Series]] = [("latest", frame.iloc[0])]
    usable = frame[
        frame["2026-盈利预测-收益"].notna()
        & (frame["2026-盈利预测-收益"].astype(float) > 0)
    ]
    if not usable.empty and usable.index[0] != frame.index[0]:
        selected.append(("latest-usable-eps", usable.iloc[0]))
    rows = [archive_report(code, company, report, label) for label, report in selected]
    if not any(row["pdf_valid"] for row in rows):
        selected_indices = {report.name for _, report in selected}
        for report_index, report in frame.iterrows():
            if report_index in selected_indices:
                continue
            fallback = archive_report(
                code,
                company,
                report,
                "latest-valid-original",
            )
            rows.append(fallback)
            if fallback["pdf_valid"]:
                break
    has_valid_original = any(row["pdf_valid"] for row in rows)
    for row in rows:
        if not row["pdf_valid"]:
            failures.append(
                {
                    "ticker": code,
                    "company": company,
                    "stage": f"pdf_validation:{row['label']}",
                    "error": row["note"],
                    "resolution": (
                        "resolved_by_valid_original_pdf_fallback"
                        if has_valid_original
                        else "open"
                    ),
                }
            )
    return rows, failures


def main() -> None:
    FINANCIAL_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    candidates = {
        row["ticker"]
        for row in load_json(DATA_DIR / "full_market_candidate_valuation_20260712.json")[
            "rows"
        ]
    }
    cards = load_json(DATA_DIR / "company_cards_20260711.json")["rows"]
    theme_only = [row for row in cards if row["ticker"] not in candidates]
    financials = asyncio.run(collect_financials([row["ticker"] for row in theme_only]))
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, card in enumerate(theme_only, 1):
        reports, report_failures = collect_reports(card["ticker"], card["company"])
        failures.extend(report_failures)
        usable_report = next(
            (
                row
                for row in reports
                if row.get("eps_2026e") is not None and row.get("pdf_valid")
            ),
            None,
        )
        rows.append(
            {
                "ticker": card["ticker"],
                "company": card["company"],
                "sector": card["sector"],
                "current_price": card.get("current_price"),
                **q1_summary(financials[card["ticker"]]),
                "reports": reports,
                "usable_eps_2026e": (
                    usable_report.get("eps_2026e") if usable_report else None
                ),
                "usable_eps_broker": (
                    usable_report.get("broker") if usable_report else None
                ),
                "usable_eps_date": (
                    usable_report.get("report_date") if usable_report else None
                ),
                "usable_eps_source": (
                    usable_report.get("local_pdf") if usable_report else None
                ),
            }
        )
        print(
            f"{index}/{len(theme_only)} {card['ticker']} "
            f"financial={rows[-1]['financial_quality']} reports={len(reports)} "
            f"eps={rows[-1]['usable_eps_2026e']}"
        )
    payload = {
        "schema_version": "astock.theme_only_evidence.v1",
        "data_cutoff": "2026-07-13 collection",
        "row_count": len(rows),
        "financial_success_count": sum(
            row.get("q1_revenue_100mn") is not None for row in rows
        ),
        "report_covered_count": sum(bool(row["reports"]) for row in rows),
        "valid_original_pdf_count": sum(
            any(report.get("pdf_valid") for report in row["reports"])
            for row in rows
        ),
        "usable_eps_count": sum(
            row.get("usable_eps_2026e") is not None for row in rows
        ),
        "failures": failures,
        "open_failure_count": sum(
            row.get("resolution", "open") == "open" for row in failures
        ),
        "rows": rows,
    }
    write_json(DATA_DIR / "theme_only_evidence_20260713.json", payload)
    lines = [
        "# Theme-Only Evidence",
        "",
        f"- Rows: {payload['row_count']}",
        f"- Q1 financial success: {payload['financial_success_count']}",
        f"- Original-report coverage: {payload['report_covered_count']}",
        f"- Valid original-PDF coverage: {payload['valid_original_pdf_count']}",
        f"- Usable 2026E EPS: {payload['usable_eps_count']}",
        f"- Failures: {len(failures)}",
        f"- Open failures: {payload['open_failure_count']}",
        "",
        "| Ticker | Company | Q1 NP | Q1 EPS | Q1 BPS | Reports | Usable EPS | Broker/date | Source |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row.get('q1_parent_np_100mn')} | "
            f"{row.get('q1_eps')} | {row.get('q1_bps')} | {len(row['reports'])} | "
            f"{row.get('usable_eps_2026e')} | "
            f"{row.get('usable_eps_broker')}/{row.get('usable_eps_date')} | "
            f"{row.get('usable_eps_source')} |"
        )
    write_text(DATA_DIR / "theme_only_evidence_20260713.md", "\n".join(lines))
    write_text(CASE_DIR / "analysis" / "theme_only_evidence.md", "\n".join(lines))
    print(
        json.dumps(
            {
                "rows": payload["row_count"],
                "financials": payload["financial_success_count"],
                "reports": payload["report_covered_count"],
                "valid_original_pdfs": payload["valid_original_pdf_count"],
                "usable_eps": payload["usable_eps_count"],
                "failures": len(failures),
                "open_failures": payload["open_failure_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
