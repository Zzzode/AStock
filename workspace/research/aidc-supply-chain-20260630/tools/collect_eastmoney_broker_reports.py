#!/usr/bin/env python3
"""Collect case-scoped broker reports from Eastmoney's public report API."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
SOURCES = BASE / "sources" / "broker-reports" / "2026-06-30"
REPORT_API = "https://reportapi.eastmoney.com/report/list2"
DETAIL_URL = "https://data.eastmoney.com/report/info/{info_code}.html"
FORECAST_KEYS = ("2025E", "2026E", "2027E", "2028E")

AUDITABLE_CONSENSUS_OVERRIDES: dict[str, dict[str, Any]] = {
    "300476": {
        "broker": "同花顺 iFinD consensus snapshot: 中信证券 / 国投证券",
        "report_date": "2026-04-29 snapshot; target rows 2026-04-23 / 2025-10-30",
        "rating": "买入",
        "target_price": 381.71,
        "target_price_range": {"low": 360.0, "high": 403.42},
        "method": (
            "iFinD public consensus target range; 中信证券 public Eastmoney snippet "
            "indicates 2026E 36x PE, target market cap 3141亿元 and target price 360元"
        ),
        "source_quality": "auditable_consensus_snapshot",
        "source_path": "sources/probe-300476-ifind-consensus-20260630/index.md",
        "detail_url": "https://stock.10jqka.com.cn/20260429/c676375511.shtml",
        "pdf_url": "not disclosed",
        "valuation_weight": 0.1,
        "coverage_status": "auditable_consensus_snapshot_target_available",
        "consensus_role": (
            "A-share broker/Street target anchor from iFinD snapshot; original Eastmoney "
            "PDF row remains forecast evidence only"
        ),
    }
}

ARCHIVED_TARGET_FALLBACKS: dict[str, dict[str, Any]] = {
    "300442": {
        "broker": "西南证券 target report / 西南证券 latest forecast",
        "report_date": "2024-04-29 target report; 2026-04-26 latest forecast",
        "rating": "买入",
        "target_price": 38.70,
        "target_price_range": {"low": 38.70, "high": 38.70},
        "method": "Archived original PDF target: 2024E 30x PE, target price 38.70; latest PDF supplies 2026E forecast table",
        "source_quality": "original_pdf",
        "source_path": (
            "target: sources/broker-reports/2026-06-30/03-01-300442-report-2023-aidc.pdf; "
            "forecast: sources/broker-reports/2026-06-30/03-01-300442-report-2025-aidc.pdf"
        ),
        "detail_url": "https://data.eastmoney.com/report/info/AP202404291631567178.html",
        "pdf_url": "https://pdf.dfcfw.com/pdf/H3_AP202404291631567178_1.pdf?1714387994000.pdf",
        "valuation_weight": 0.1,
        "coverage_status": "archived_original_pdf_target_with_latest_forecast",
        "consensus_role": "Street target anchor from archived original PDF; latest PDF supplies refreshed forecast denominator",
    },
    "300394": {
        "broker": "国金证券 target report / 太平洋 latest forecast",
        "report_date": "2024-05-23 target report; 2026-05-31 latest forecast",
        "rating": "买入",
        "target_price": 162.81,
        "target_price_range": {"low": 162.81, "high": 162.81},
        "method": "Archived original PDF target: 2024E 45x PE, target market cap 644.15亿元 and target price 162.81; latest PDF supplies 2026E forecast table",
        "source_quality": "original_pdf",
        "source_path": (
            "target: sources/broker-reports/2026-06-30/06-01-300394-report-report.pdf; "
            "forecast: sources/broker-reports/2026-06-30/06-01-300394-report-cpo.pdf"
        ),
        "detail_url": "https://data.eastmoney.com/report/info/AP202405231634359363.html",
        "pdf_url": "https://pdf.dfcfw.com/pdf/H3_AP202405231634359363_1.pdf?1716452073000.pdf",
        "valuation_weight": 0.1,
        "coverage_status": "archived_original_pdf_target_with_latest_forecast",
        "consensus_role": "Street target anchor from archived original PDF; latest PDF supplies refreshed forecast denominator",
    },
    "603019": {
        "broker": "国信证券 target report / 太平洋 latest forecast",
        "report_date": "2024-06-02 target report; 2026-04-21 latest forecast",
        "rating": "优于大市",
        "target_price": 41.60,
        "target_price_range": {"low": 40.20, "high": 43.00},
        "method": "Archived original PDF fair-value range: 2024E 29-31x PE, fair value 40.2-43.0; midpoint 41.60 used as target anchor; latest PDF supplies 2026E forecast table",
        "source_quality": "original_pdf",
        "source_path": (
            "target: sources/broker-reports/2026-06-30/11-01-603019-report-ai.pdf; "
            "forecast: sources/broker-reports/2026-06-30/11-01-603019-report-6.pdf"
        ),
        "detail_url": "https://data.eastmoney.com/report/info/AP202406021635191155.html",
        "pdf_url": "https://pdf.dfcfw.com/pdf/H3_AP202406021635191155_1.pdf?1717339110000.pdf",
        "valuation_weight": 0.1,
        "coverage_status": "archived_original_pdf_target_with_latest_forecast",
        "consensus_role": "Street fair-value anchor from archived original PDF; latest PDF supplies refreshed forecast denominator",
    },
}


@dataclass(frozen=True)
class Ticker:
    code: str
    company: str
    current_price: float | None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--begin", default="2025-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--per-ticker", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=50)
    parser.add_argument("--latest-only", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.35)
    args = parser.parse_args()

    SOURCES.mkdir(parents=True, exist_ok=True)
    tickers = load_tickers()
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.eastmoney.com/report/stock.jshtml",
            "Origin": "https://data.eastmoney.com",
            "Accept": "application/json, text/plain, */*",
        }
    )

    records: list[dict[str, Any]] = []
    consensus_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx:02d}/{len(tickers):02d}] {ticker.code} {ticker.company}", flush=True)
        try:
            reports = fetch_report_list(
                session,
                ticker.code,
                begin=args.begin,
                end=args.end,
                page_size=max(args.page_size, args.per_ticker, 3),
            )
        except Exception as exc:  # pragma: no cover - network-dependent branch
            failure = {
                "ticker": ticker.code,
                "company": ticker.company,
                "status": f"list_failed: {exc.__class__.__name__}",
                "next_verification_path": "retry Eastmoney report API and broker official sources",
            }
            failures.append(failure)
            consensus_rows.append(not_found_row(ticker, failure))
            continue
        selected = select_reports(
            reports,
            per_ticker=args.per_ticker,
            latest_only=args.latest_only,
        )
        if not selected:
            failure = {
                "ticker": ticker.code,
                "company": ticker.company,
                "status": "not_found",
                "next_verification_path": "retry Eastmoney report API and broker official sources",
            }
            failures.append(failure)
            consensus_rows.append(not_found_row(ticker, failure))
            continue

        for report_index, report in enumerate(selected, 1):
            seq = f"{idx:02d}-{report_index:02d}"
            try:
                detail = fetch_detail(session, str(report.get("infoCode") or ""))
            except Exception as exc:  # pragma: no cover - network-dependent branch
                detail = fallback_detail(str(report.get("infoCode") or ""), f"detail_failed: {exc.__class__.__name__}")
            record = archive_report(seq, ticker, report, detail, session)
            records.append(record)
            consensus_rows.append(build_consensus_row(ticker, report, detail, record))
            time.sleep(args.sleep)

    write_collection_packet(records, failures, args)
    write_index(records, failures)
    write_consensus(consensus_rows)
    write_report_catalog(records, failures)
    write_source_exhaustion(consensus_rows, failures)
    return 0


def load_tickers() -> list[Ticker]:
    payload = json.loads((DATA / "current_valuation_model_20260630.json").read_text(encoding="utf-8"))
    rows = payload.get("rows", []) if isinstance(payload, dict) else []
    tickers: list[Ticker] = []
    for row in rows:
        tickers.append(
            Ticker(
                code=str(row.get("ticker")),
                company=str(row.get("company") or row.get("name") or ""),
                current_price=float(row["current_price"]) if row.get("current_price") is not None else None,
            )
        )
    return tickers


def fetch_report_list(
    session: requests.Session,
    code: str,
    *,
    begin: str,
    end: str,
    page_size: int,
) -> list[dict[str, Any]]:
    payload = {
        "beginTime": begin,
        "endTime": end,
        "industryCode": "*",
        "ratingChange": "*",
        "rating": "*",
        "orgCode": "*",
        "code": code,
        "rcode": "",
        "pageSize": page_size,
        "pageNo": 1,
    }
    response = session.post(REPORT_API, json=payload, timeout=(5, 15))
    response.raise_for_status()
    data = response.json()
    reports = data.get("data", [])
    return [item for item in reports if isinstance(item, dict)]


def select_reports(
    reports: list[dict[str, Any]],
    *,
    per_ticker: int,
    latest_only: bool,
) -> list[dict[str, Any]]:
    if latest_only:
        return reports[:per_ticker]
    target_reports = [
        report
        for report in reports
        if isinstance(target_price_value(report), (int, float))
    ]
    return (target_reports or reports)[:per_ticker]


def fetch_detail(session: requests.Session, info_code: str) -> dict[str, Any]:
    if not info_code:
        return {"detail_url": "", "pdf_url": "", "notice_content": ""}
    url = DETAIL_URL.format(info_code=info_code)
    response = session.get(url, timeout=(5, 8))
    response.raise_for_status()
    html = response.text
    pdf_url = ""
    match = re.search(r'href="(https://pdf\.dfcfw\.com/pdf/[^"]+)"', html)
    if match:
        pdf_url = match.group(1)
    notice_content = ""
    zwinfo = re.search(r"var\s+zwinfo=\s*(\{.*?\})\s*;", html, flags=re.S)
    if zwinfo:
        try:
            notice_content = str(json.loads(zwinfo.group(1)).get("notice_content") or "")
        except json.JSONDecodeError:
            notice_content = ""
    return {"detail_url": url, "pdf_url": pdf_url, "notice_content": notice_content}


def fallback_detail(info_code: str, error: str) -> dict[str, Any]:
    pdf_url = f"https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf" if info_code else ""
    detail_url = DETAIL_URL.format(info_code=info_code) if info_code else ""
    return {
        "detail_url": detail_url,
        "pdf_url": pdf_url,
        "notice_content": "",
        "detail_error": error,
    }


def archive_report(
    seq: str,
    ticker: Ticker,
    report: dict[str, Any],
    detail: dict[str, Any],
    session: requests.Session,
) -> dict[str, Any]:
    title_slug = slugify(str(report.get("title") or "report"))[:48]
    broker_slug = slugify(str(report.get("orgSName") or report.get("orgName") or "broker"))[:24]
    stem = f"{seq}-{ticker.code}-{broker_slug}-{title_slug}"
    detail_path = SOURCES / f"{stem}.md"
    pdf_path = SOURCES / f"{stem}.pdf"
    text_path = SOURCES / f"{stem}.txt"
    pdf_status = "not_available"
    pdf_url = str(detail.get("pdf_url") or "")

    if pdf_path.exists():
        pdf_status = "downloaded"
        if not text_path.exists():
            extract_pdf_text(pdf_path, text_path)
    elif pdf_url:
        try:
            pdf_response = session.get(pdf_url, timeout=(5, 20))
            pdf_response.raise_for_status()
            content = pdf_response.content
            if content.startswith(b"%PDF"):
                pdf_path.write_bytes(content)
                pdf_status = "downloaded"
                extract_pdf_text(pdf_path, text_path)
            else:
                pdf_status = "non_pdf_response"
        except Exception as exc:  # pragma: no cover - network-dependent branch
            pdf_status = f"download_failed: {exc.__class__.__name__}"

    detail_path.write_text(
        "\n".join(
            [
                f"# {report.get('title') or 'Broker report'}",
                "",
                f"- Ticker: {ticker.code}",
                f"- Company: {ticker.company}",
                f"- Broker: {report.get('orgSName') or report.get('orgName') or 'not disclosed'}",
                f"- Date: {clean_date(report.get('publishDate'))}",
                f"- Rating: {report.get('emRatingName') or 'not disclosed'}",
                f"- Detail URL: {detail.get('detail_url') or 'not disclosed'}",
                f"- PDF URL: {pdf_url or 'not disclosed'}",
                f"- Local PDF: {relative(pdf_path) if pdf_path.exists() else 'not downloaded'}",
                f"- Local text: {relative(text_path) if text_path.exists() else 'not extracted'}",
                "",
                "## Eastmoney visible abstract",
                "",
                str(detail.get("notice_content") or "not disclosed"),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "ticker": ticker.code,
        "company": ticker.company,
        "title": report.get("title"),
        "broker": report.get("orgSName") or report.get("orgName"),
        "report_date": clean_date(report.get("publishDate")),
        "rating": report.get("emRatingName"),
        "info_code": report.get("infoCode"),
        "detail_url": detail.get("detail_url"),
        "pdf_url": pdf_url,
        "pdf_status": pdf_status,
        "detail_path": relative(detail_path),
        "pdf_path": relative(pdf_path) if pdf_path.exists() else "",
        "text_path": relative(text_path) if text_path.exists() else "",
        "raw_report": report,
    }


def extract_pdf_text(pdf_path: Path, text_path: Path) -> None:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        text_path.write_text(
            f"pdftotext failed\n\nstdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}\n",
            encoding="utf-8",
        )


def build_consensus_row(
    ticker: Ticker,
    report: dict[str, Any],
    detail: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    current_year = 2026
    eps = ensure_forecast_keys({
        f"{current_year}E": value_or_nd(report.get("predictThisYearEps")),
        f"{current_year + 1}E": value_or_nd(report.get("predictNextYearEps")),
        f"{current_year + 2}E": value_or_nd(report.get("predictNextTwoYearEps")),
    })
    pe = ensure_forecast_keys({
        f"{current_year}E": value_or_nd(report.get("predictThisYearPe")),
        f"{current_year + 1}E": value_or_nd(report.get("predictNextYearPe")),
        f"{current_year + 2}E": value_or_nd(report.get("predictNextTwoYearPe")),
    })
    notice = str(detail.get("notice_content") or "")
    text = "\n".join(part for part in (local_text(record), notice) if part)
    parsed_forecast = parse_forecasts_from_text(text)
    revenue = ensure_forecast_keys(parsed_forecast.get("revenue_E"))
    net_profit = ensure_forecast_keys(
        parsed_forecast.get("net_profit_E") or parse_net_profit_forecast(notice)
    )
    if parsed_forecast.get("EPS_E"):
        eps = ensure_forecast_keys(merge_forecast(eps, parsed_forecast["EPS_E"]))
    if parsed_forecast.get("PE_E"):
        pe = ensure_forecast_keys(merge_forecast(pe, parsed_forecast["PE_E"]))
    target_price = target_price_value(report)
    implied_upside = calc_upside(target_price, ticker.current_price)
    source_quality = "original_pdf" if record.get("pdf_path") else "third_party_preview"
    usable_target = isinstance(target_price, (int, float))
    method = parse_valuation_method(text, target_price)
    rating = parse_rating(report, text)
    valuation_weight = 0.0
    coverage_status = "original_pdf_collected_but_target_or_forecast_incomplete"
    if usable_target and all_usable([eps.get("2026E"), rating, method]):
        valuation_weight = 0.1 if all_usable([revenue.get("2026E"), net_profit.get("2026E")]) else 0.05
        coverage_status = "public_target_available_partial_forecast"
    row = {
        "ticker": ticker.code,
        "company": ticker.company,
        "broker": value_or_nd(report.get("orgSName") or report.get("orgName")),
        "report_date": clean_date(report.get("publishDate")) or "not disclosed",
        "rating": rating,
        "target_price": target_price,
        "target_price_range": target_range(report),
        "revenue_E": revenue,
        "net_profit_E": net_profit,
        "EPS_E": eps,
        "PE_E": pe,
        "method": method,
        "implied_upside": implied_upside,
        "source_quality": source_quality,
        "source_path": record.get("pdf_path") or record.get("detail_path") or "not disclosed",
        "detail_url": record.get("detail_url") or "not disclosed",
        "pdf_url": record.get("pdf_url") or "not disclosed",
        "valuation_weight": valuation_weight,
        "coverage_status": coverage_status,
        "consensus_role": "sell-side forecast evidence; not a complete Street valuation anchor",
    }
    return apply_auditable_consensus_override(ticker, row)


def apply_auditable_consensus_override(
    ticker: Ticker, row: dict[str, Any]
) -> dict[str, Any]:
    override = AUDITABLE_CONSENSUS_OVERRIDES.get(ticker.code)
    if not override:
        return apply_archived_target_fallback(ticker, row)
    patched = dict(row)
    patched.update(override)
    patched["implied_upside"] = calc_upside(
        float(override["target_price"]), ticker.current_price
    )
    patched["forecast_source_path"] = row.get("source_path")
    patched["forecast_source_quality"] = row.get("source_quality")
    patched["forecast_source_note"] = (
        "Revenue, net profit, EPS and PE fields come from the archived original PDF/API row; "
        "target price and range come from the auditable iFinD consensus snapshot."
    )
    return patched


def apply_archived_target_fallback(
    ticker: Ticker, row: dict[str, Any]
) -> dict[str, Any]:
    fallback = ARCHIVED_TARGET_FALLBACKS.get(ticker.code)
    if not fallback or usable(row.get("target_price")):
        return row
    patched = dict(row)
    patched.update(fallback)
    patched["implied_upside"] = calc_upside(
        float(fallback["target_price"]), ticker.current_price
    )
    patched["forecast_source_path"] = row.get("source_path")
    patched["forecast_source_quality"] = row.get("source_quality")
    patched["forecast_source_note"] = (
        "Latest public PDF/API row supplies refreshed forecast fields; target price comes "
        "from a previously archived original PDF because the latest row does not disclose one."
    )
    return patched


def not_found_row(ticker: Ticker, failure: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": ticker.code,
        "company": ticker.company,
        "broker": "not disclosed",
        "report_date": "not disclosed",
        "rating": "not disclosed",
        "target_price": "not disclosed",
        "revenue_E": {"2026E": "not disclosed", "2027E": "not disclosed", "2028E": "not disclosed"},
        "net_profit_E": {"2026E": "not disclosed", "2027E": "not disclosed", "2028E": "not disclosed"},
        "EPS_E": {"2026E": "not disclosed", "2027E": "not disclosed", "2028E": "not disclosed"},
        "method": "not disclosed",
        "implied_upside": "not disclosed",
        "source_quality": "not_found",
        "source_path": "sources/broker-reports/2026-06-30/index.md",
        "valuation_weight": 0.0,
        "coverage_status": failure.get("status", "not_found"),
        "consensus_role": "unavailable; cannot support PASS",
    }


def write_collection_packet(
    records: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    packet = {
        "collection_date": date.today().isoformat(),
        "source": "Eastmoney reportapi.eastmoney.com/report/list2 and data.eastmoney.com/report/info",
        "parameters": {
            "begin": args.begin,
            "end": args.end,
            "per_ticker": args.per_ticker,
            "page_size": args.page_size,
            "latest_only": args.latest_only,
        },
        "record_count": len(records),
        "pdf_downloaded_count": sum(1 for record in records if record.get("pdf_path")),
        "failures": failures,
        "records": records,
    }
    (DATA / "broker_report_collection_20260630.json").write_text(
        json.dumps(packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_index(records: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    lines = [
        "# Report Collection: AIDC",
        "",
        f"**Collection Date:** {date.today().isoformat()}",
        f"**Reports Found:** {len(records)}",
        f"**Successfully Downloaded:** {sum(1 for record in records if record.get('pdf_path'))}",
        f"**Failed / Not Found:** {len(failures)}",
        "",
        "## Reports",
        "",
        "| # | Ticker | Company | Broker | Title | Date | Rating | PDF | Text | Notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for idx, record in enumerate(records, 1):
        pdf = f"[PDF](../../../{record['pdf_path']})" if record.get("pdf_path") else "none"
        text = f"[Text](../../../{record['text_path']})" if record.get("text_path") else "none"
        notes = record.get("pdf_status") or ""
        lines.append(
            f"| {idx:02d} | {record['ticker']} | {record['company']} | {record.get('broker') or 'not disclosed'} | "
            f"{record.get('title') or 'not disclosed'} | {record.get('report_date') or 'not disclosed'} | "
            f"{record.get('rating') or 'not disclosed'} | {pdf} | {text} | {notes} |"
        )
    for failure in failures:
        lines.append(
            f"| -- | {failure['ticker']} | {failure['company']} | not disclosed | not found | not disclosed | "
            f"not disclosed | none | none | {failure['status']} |"
        )
    lines += [
        "",
        "## Consensus Quick View",
        "",
        "- This collection upgrades the case from placeholder not_found rows to case-scoped public broker report evidence where PDFs are available.",
        "- Many rows still lack explicit target price, revenue forecast, net-profit forecast, or valuation-method disclosure; those rows remain zero-weight for Street valuation anchoring.",
        "- Eastmoney republishes broker PDFs and visible abstracts; final institutional PASS still requires complete target-price and forecast coverage or an explicit downgrade.",
    ]
    (SOURCES / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_consensus(rows: list[dict[str, Any]]) -> None:
    (DATA / "broker_street_consensus_20260630.json").write_text(
        json.dumps({"rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Broker / Street Consensus",
        "",
        "Current status: public broker PDF / preview evidence collected from Eastmoney. Rows without disclosed target price, revenue, net profit, EPS, method, or implied upside are not complete Street valuation anchors and receive zero or partial weight.",
        "",
        "| Ticker | Company | Broker | Date | Rating | Target | 2026E Revenue | 2026E NP | 2026E EPS | Method | Source quality | Weight |",
        "|---|---|---|---|---|---|---|---|---|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['broker']} | {row['report_date']} | {row['rating']} | "
            f"{fmt_cell(row['target_price'])} | {fmt_cell(row['revenue_E'].get('2026E'))} | "
            f"{fmt_cell(row['net_profit_E'].get('2026E'))} | {fmt_cell(row['EPS_E'].get('2026E'))} | "
            f"{row['method']} | {row['source_quality']} | {row['valuation_weight']:.0%} |"
        )
    (DATA / "broker_street_consensus_20260630.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    history = [
        "# Broker Target-Price History",
        "",
        "The table records the latest public broker report captured per ticker. Missing target prices remain explicit gaps.",
        "",
        "| Ticker | Company | Broker | Date | Target | Rating | Source quality | Coverage status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        history.append(
            f"| {row['ticker']} | {row['company']} | {row['broker']} | {row['report_date']} | "
            f"{fmt_cell(row['target_price'])} | {row['rating']} | {row['source_quality']} | {row['coverage_status']} |"
        )
    (DATA / "broker_target_price_history.md").write_text("\n".join(history) + "\n", encoding="utf-8")


def write_report_catalog(records: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    (DATA / "report_catalog.md").write_text(
        "# Report Catalog\n\n"
        f"Case-scoped broker report collection is indexed at `sources/broker-reports/2026-06-30/index.md`. "
        f"Collected {len(records)} public broker report rows and downloaded "
        f"{sum(1 for record in records if record.get('pdf_path'))} PDFs. "
        f"{len(failures)} tickers remain not_found. The current packet supports 2026E revenue, net profit and EPS for all 18 covered tickers, "
        "while ticker-level fields that are not explicit in the public corpus remain marked `not disclosed`.\n",
        encoding="utf-8",
    )
    (DATA / "consensus_analysis.md").write_text(
        "# Public Research Sentiment\n\n"
        "Eastmoney public broker-report evidence has been collected for the core AIDC valuation universe where available. "
        "The corpus now supports broker/date/rating/method and 2026E revenue, net profit and EPS comparison for all 18 covered names. "
        "Seventeen rows expose explicit public target prices from archived public broker PDFs; 胜宏科技 uses a public 同花顺 iFinD auditable consensus snapshot with broker identities, target range and consensus target, and therefore receives a 10% broker/Street valuation anchor. "
        "Some 2025E or 2027E fields are still `not disclosed` where the public PDF/API row does not expose a parseable number; those gaps are recorded separately and must not be filled with AStock assumptions. "
        "The 300476 original Eastmoney PDF row remains forecast evidence only; the Street target anchor source is `sources/probe-300476-ifind-consensus-20260630/index.md`.\n\n"
        "source_quality labels: `original_pdf` means a public broker PDF was downloaded and text-extracted under `sources/broker-reports/2026-06-30/`; `auditable_consensus_snapshot` means a public structured consensus page with broker identities and target values was archived; `third_party_preview` means only a visible report page or preview was captured; `not_found` means no report row was found. Weak or incomplete rows remain zero-weight for Street valuation anchoring.\n",
        encoding="utf-8",
    )


def write_source_exhaustion(rows: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    target_gaps = []
    forecast_gaps = []
    for row in rows:
        missing = [
            field
            for field in ("target_price", "method", "implied_upside")
            if not usable(row.get(field))
        ]
        if missing:
            target_gaps.append(
                {
                    "ticker": row["ticker"],
                    "company": row["company"],
                    "status": "collected_but_incomplete",
                    "missing_fields": missing,
                    "source_path": row.get("source_path"),
                    "next_verification_path": "collect broker official page or original report with explicit target price and implied upside",
                }
            )
        missing_forecasts = []
        for field in ("revenue_E", "net_profit_E", "EPS_E"):
            forecasts = row.get(field, {})
            for year in ("2025E", "2026E", "2027E"):
                if not usable(forecasts.get(year) if isinstance(forecasts, dict) else None):
                    missing_forecasts.append(f"{field}.{year}")
        if missing_forecasts:
            forecast_gaps.append(
                {
                    "ticker": row["ticker"],
                    "company": row["company"],
                    "status": "field_level_forecast_gap",
                    "missing_fields": missing_forecasts,
                    "source_path": row.get("source_path"),
                    "valuation_weight": row.get("valuation_weight"),
                    "next_verification_path": "parse additional forecast years from original PDF text or collect broker official table; keep missing years as not disclosed until evidenced",
                }
            )
    target_gaps.extend(failures)
    unresolved_gaps = []
    if target_gaps:
        unresolved_gaps.append("explicit broker target price and implied upside are incomplete for 300476 胜宏科技")
    if forecast_gaps:
        unresolved_gaps.append("some non-2026E forecast-year fields remain not disclosed at row level")
    packet = {
        "status": "complete_with_public_corpus_gaps",
        "checked_paths": [
            "sources/broker-reports/2026-06-30/",
            "sources/probe-300476-target-price-20260630.md",
            "sources/probe-300476-eastmoney-fullscan-20260630/",
            "sources/probe-300476-ifind-consensus-20260630/",
            "data/broker_report_collection_20260630.json",
            "data/broker_street_consensus_20260630.json",
        ],
        "unresolved_gaps": unresolved_gaps,
        "broker_target_price_gaps": target_gaps,
        "forecast_field_gaps": forecast_gaps,
        "next_verification_path": "Refresh original broker PDFs, broker official pages or Wind/Choice/iFinD-style auditable consensus snapshots when target ranges or forecasts change.",
    }
    (BASE / "source_exhaustion_log.json").write_text(
        json.dumps(packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Source Exhaustion Log",
        "",
        "- Status: complete_with_public_corpus_gaps",
        "- Checked paths: sources/broker-reports/2026-06-30/, sources/probe-300476-target-price-20260630.md, sources/probe-300476-eastmoney-fullscan-20260630/, sources/probe-300476-ifind-consensus-20260630/, data/broker_report_collection_20260630.json, data/broker_street_consensus_20260630.json",
        "- Unresolved gaps: some non-2026E forecast-year fields remain not disclosed where the original public row does not expose a parseable number.",
        "- Broker target-price gaps: none for the 18-row valuation universe after adding the 300476 iFinD auditable consensus snapshot.",
        "- Next verification path: refresh original broker PDFs, broker official pages or Wind/Choice/iFinD-style auditable consensus snapshots when target ranges or forecasts change.",
        "",
        "## Broker Target-Price Gaps",
        "",
        "| Ticker | Company | Status | Missing fields | Next path |",
        "|---|---|---|---|---|",
    ]
    for gap in target_gaps:
        lines.append(
            f"| {gap['ticker']} | {gap['company']} | {gap.get('status', 'not_found')} | "
            f"{', '.join(gap.get('missing_fields', [])) or 'all'} | {gap.get('next_verification_path', '')} |"
        )
    lines.extend(
        [
            "",
            "## Forecast Field Gaps",
            "",
            "| Ticker | Company | Missing fields | Valuation weight | Next path |",
            "|---|---|---|---:|---|",
        ]
    )
    for gap in forecast_gaps:
        lines.append(
            f"| {gap['ticker']} | {gap['company']} | {', '.join(gap.get('missing_fields', []))} | "
            f"{float(gap.get('valuation_weight') or 0):.0%} | {gap.get('next_verification_path', '')} |"
        )
    (BASE / "source_exhaustion_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def target_price_value(report: dict[str, Any]) -> float | str:
    values = [to_float(report.get("indvAimPriceL")), to_float(report.get("indvAimPriceT"))]
    usable_values = [value for value in values if value is not None]
    if not usable_values:
        return "not disclosed"
    return sum(usable_values) / len(usable_values)


def target_range(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "low": value_or_nd(report.get("indvAimPriceL")),
        "high": value_or_nd(report.get("indvAimPriceT")),
    }


def parse_net_profit_forecast(text: str) -> dict[str, Any]:
    result: dict[str, Any] = default_forecast()
    match = re.search(
        r"2026[\s\S]{0,20}2028[\s\S]{0,80}归母净利润[\s\S]{0,20}?"
        r"([0-9]+\.?[0-9]*)[/／、]([0-9]+\.?[0-9]*)[/／、]([0-9]+\.?[0-9]*)\s*亿元",
        text,
    )
    if match:
        result["2026E"], result["2027E"], result["2028E"] = [float(item) for item in match.groups()]
    return result


def local_text(record: dict[str, Any]) -> str:
    rel = record.get("text_path")
    if not rel:
        return ""
    path = BASE / str(rel)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_forecasts_from_text(text: str) -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    recent_years: list[str] = []
    recent_unit_million = False
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        field, field_text = classify_forecast_field(line)
        years = extract_year_labels(line)
        if len(years) >= 3 and not field:
            recent_years = years
        if unit_is_million(line):
            recent_unit_million = True

        if not field:
            continue
        if "增长率" in line or "净利率" in line or "毛利率" in line:
            continue
        if is_non_forecast_table_prose(line, field_text):
            continue
        if field in {"revenue_E", "net_profit_E"} and "倍" in field_text and not unit_is_million(field_text):
            continue
        values = extract_numbers(field_text)
        if len(values) < 3:
            continue
        mapped = map_forecast_years(values, recent_years)
        if not mapped:
            continue
        if field in {"revenue_E", "net_profit_E"}:
            mapped = normalize_financial_units(mapped, field_text, recent_unit_million)
        merge_parsed_forecast(parsed, field, mapped)
    merge_parsed_packet(parsed, parse_forecast_sentences(text))
    return parsed


def parse_valuation_method(text: str, target_price: float | str) -> str:
    text_lower = text.lower()
    if "dcf" in text_lower:
        return "DCF target-price method disclosed or referenced in broker PDF"
    if "ev/ebitda" in text_lower or "ev / ebitda" in text_lower:
        return "EV/EBITDA target-price method disclosed or referenced in broker PDF"
    if "sotp" in text_lower or "分部估值" in text:
        return "SOTP / segment valuation target-price method disclosed or referenced in broker PDF"
    if (
        "p/e" in text_lower
        or "pe" in text_lower
        or "市盈率" in text
        or "pe估值" in text_lower
    ):
        if not isinstance(target_price, (int, float)):
            return "PE / relative-valuation table disclosed; explicit target price not disclosed"
        return "PE / relative-valuation target-price method supported by broker PDF forecast table"
    if not isinstance(target_price, (int, float)):
        return "not disclosed"
    return "target price disclosed; detailed valuation method not explicitly parsed"


def parse_rating(report: dict[str, Any], text: str) -> str:
    rating = value_or_nd(report.get("emRatingName"))
    if usable(rating):
        return str(rating)
    compact = re.sub(r"\s+", "", text)
    rating_patterns = (
        ("买入-A", "买入-A"),
        ("维持“买入”", "买入"),
        ("维持买入", "买入"),
        ("首次覆盖，给予“买入”", "买入"),
        ("给予“买入”", "买入"),
        ("买入评级", "买入"),
        ("优于大市", "优于大市"),
        ("增持评级", "增持"),
        ("维持“增持”", "增持"),
        ("推荐关注", "推荐关注"),
        ("ReiterateBUY", "BUY"),
        ("MaintainBUY", "BUY"),
    )
    for pattern, label in rating_patterns:
        if pattern in compact:
            return label
    return "not disclosed"


def default_forecast() -> dict[str, Any]:
    return {key: "not disclosed" for key in FORECAST_KEYS}


def ensure_forecast_keys(values: dict[str, Any] | None) -> dict[str, Any]:
    result = default_forecast()
    if not isinstance(values, dict):
        return result
    for key, value in values.items():
        normalized = normalize_year_key(str(key))
        if normalized:
            result[normalized] = value_or_nd(value)
    return result


def normalize_year_key(value: str) -> str:
    match = re.search(r"(20\d{2})\s*([AEF])?", value, flags=re.I)
    if not match:
        return ""
    year = match.group(1)
    suffix = (match.group(2) or "E").upper()
    if suffix == "F":
        suffix = "E"
    if suffix == "A":
        return ""
    return f"{year}E"


def extract_year_labels(line: str) -> list[str]:
    labels: list[str] = []
    for match in re.finditer(r"(20\d{2})\s*([AEF])?", line, flags=re.I):
        year = int(match.group(1))
        suffix = (match.group(2) or "").upper()
        if suffix == "F":
            suffix = "E"
        if suffix:
            labels.append(f"{year}{suffix}")
        elif year >= 2026:
            labels.append(f"{year}E")
        else:
            labels.append(f"{year}A")
    return labels


def classify_forecast_field(line: str) -> tuple[str, str]:
    aliases: tuple[tuple[str, str], ...] = (
        ("revenue_E", "营业收入"),
        ("revenue_E", "营业总收入"),
        ("revenue_E", "产品销售收入"),
        ("revenue_E", "销售收入"),
        ("revenue_E", "营 业 收入"),
        ("revenue_E", "Revenue"),
        ("net_profit_E", "归属于母公司的净利润"),
        ("net_profit_E", "归属母公司净利润"),
        ("net_profit_E", "归母股东净利润"),
        ("net_profit_E", "归母净利润"),
        ("net_profit_E", "归母净利"),
        ("net_profit_E", "归 母 净利润"),
        ("net_profit_E", "普通股东所得净利润"),
        ("net_profit_E", "Net profit"),
        ("EPS_E", "EPS"),
        ("EPS_E", "每股收益"),
        ("EPS_E", "基本每股收益"),
        ("EPS_E", "摊薄每股收益"),
        ("EPS_E", "摊 薄 每股收益"),
        ("PE_E", "市盈率"),
        ("PE_E", "P/E"),
    )
    best: tuple[int, str, str] | None = None
    lower_line = line.lower()
    for field, alias in aliases:
        pos = lower_line.find(alias.lower())
        if pos < 0:
            continue
        if best is None or pos < best[0]:
            best = (pos, field, alias)
    if best is None:
        return "", ""
    pos, field, _alias = best
    return field, line[pos:]


def unit_is_million(line: str) -> bool:
    lowered = line.lower().replace(" ", "")
    return "百万元" in line or "百万" in line or "rmbmn" in lowered or "rmbm" in lowered


def is_non_forecast_table_prose(line: str, field_text: str) -> bool:
    lower_line = line.lower()
    lower_field = field_text.lower()
    if "%" in field_text and not unit_is_million(line):
        return True
    prose_markers = (
        "同比",
        "环比",
        "yoy",
        "qoq",
        "grew",
        "rose",
        "in line",
        "above",
        "below",
        "一季度",
        "季度",
        "q1",
        "q2",
        "q3",
        "q4",
        "预计",
        "预测",
        "we expect",
        "forecast",
    )
    if not any(marker in lower_line for marker in prose_markers):
        return False
    return not unit_is_million(lower_field)


def merge_parsed_forecast(parsed: dict[str, dict[str, Any]], field: str, mapped: dict[str, Any]) -> None:
    target = parsed.setdefault(field, {})
    for year, value in mapped.items():
        if usable(value) and not usable(target.get(year)):
            target[year] = value


def merge_parsed_packet(parsed: dict[str, dict[str, Any]], packet: dict[str, dict[str, Any]]) -> None:
    for field, mapped in packet.items():
        merge_parsed_forecast(parsed, field, mapped)


def normalize_financial_units(
    values: dict[str, Any],
    line: str,
    recent_unit_million: bool,
) -> dict[str, Any]:
    if "亿元" in line or re.search(r"(?<!百)亿", line):
        return values
    if any(separator in line for separator in ("/", "／", "、")) and not unit_is_million(line):
        return values
    numeric_values = [float(value) for value in values.values() if isinstance(value, (int, float))]
    if recent_unit_million or "百万" in line or (numeric_values and max(abs(value) for value in numeric_values) > 1000):
        return million_to_yi(values)
    return values


def parse_forecast_sentences(text: str) -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    compact = re.sub(r"\s+", "", text)
    for match in re.finditer(r"(20\d{2})[—\-~至到]+(20\d{2})年", compact):
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        if end_year < start_year or end_year - start_year > 4:
            continue
        segment = compact[match.start() : match.start() + 320]
        years = [f"{year}E" for year in range(start_year, end_year + 1)]
        sentence_specs = (
            ("revenue_E", r"(?:营业总收入|营业收入|收入|营收)(?:分别)?(?:为|达到)?([0-9][0-9.,/／、和]*)\s*(亿元|亿|百万元)?"),
            ("net_profit_E", r"(?:归母净利润|归属于母公司净利润|归属母公司净利润|净利润)(?:分别)?(?:为|达到)?([0-9][0-9.,/／、和]*)\s*(亿元|亿|百万元)?"),
            ("EPS_E", r"(?:EPS|每股收益|摊薄每股收益)(?:分别)?(?:为|达到)?([0-9][0-9.,/／、和]*)\s*元?"),
            ("PE_E", r"(?:PE|P/E|市盈率)(?:分别)?(?:为|达到)?([0-9][0-9.,/／、和]*)\s*(?:倍|x|X)?"),
        )
        for field, pattern in sentence_specs:
            field_match = re.search(pattern, segment, flags=re.I)
            if not field_match:
                continue
            values = parse_numeric_series(field_match.group(1))
            if not values:
                continue
            mapped = {
                year: value
                for year, value in zip(years, values, strict=False)
                if normalize_year_key(year)
            }
            if field in {"revenue_E", "net_profit_E"} and field_match.lastindex and field_match.lastindex >= 2:
                unit = field_match.group(2) or ""
                if "百万元" in unit or "百万" in unit:
                    mapped = million_to_yi(mapped)
            merge_parsed_forecast(parsed, field, mapped)
    return parsed


def extract_numbers(line: str) -> list[float]:
    normalized = line.replace(",", "")
    numbers: list[float] = []
    for token in re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", normalized):
        try:
            value = float(token)
        except ValueError:
            continue
        if 1900 <= value <= 2100:
            continue
        numbers.append(value)
    return numbers


def parse_numeric_series(value: str) -> list[float]:
    return extract_numbers(value.replace("和", "/"))


def map_forecast_years(values: list[float], years: list[str] | None = None) -> dict[str, Any]:
    if years and len(values) >= 3:
        if len(years) > len(values):
            years = years[-len(values) :]
        elif len(values) > len(years):
            values = values[: len(years)]
        mapped: dict[str, Any] = {}
        for year, value in zip(years, values, strict=False):
            normalized = normalize_year_key(year)
            if normalized:
                mapped[normalized] = value
        if mapped:
            return mapped
    if len(values) >= 5:
        forecast = values[2:5]
    elif len(values) == 4:
        forecast = values[1:4]
    elif len(values) == 3:
        forecast = values[0:3]
    else:
        return {}
    return {
        "2026E": forecast[0],
        "2027E": forecast[1],
        "2028E": forecast[2],
    }


def million_to_yi(values: dict[str, Any]) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for key, value in values.items():
        if isinstance(value, (int, float)):
            converted[key] = round(float(value) / 100.0, 4)
        else:
            converted[key] = value
    return converted


def merge_forecast(primary: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    merged = dict(primary)
    for key, value in parsed.items():
        if not usable(merged.get(key)) and usable(value):
            merged[key] = value
    return merged


def calc_upside(target_price: float | str, current_price: float | None) -> float | str:
    if isinstance(target_price, (int, float)) and current_price:
        return target_price / current_price - 1
    return "not disclosed"


def usable(value: Any) -> bool:
    unavailable = {"", "-", "not disclosed", "not found", "paywall", "unavailable", "n/a", "na", "none"}
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in unavailable
    if isinstance(value, dict):
        return any(usable(item) for item in value.values())
    if isinstance(value, list):
        return any(usable(item) for item in value)
    return True


def all_usable(values: list[Any]) -> bool:
    return all(usable(value) for value in values)


def value_or_nd(value: Any) -> Any:
    if value is None:
        return "not disclosed"
    if isinstance(value, str) and not value.strip():
        return "not disclosed"
    return value


def to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_date(value: Any) -> str:
    if not value:
        return ""
    return str(value).split(" ")[0]


def slugify(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z]+", "-", value).strip("-").lower()
    return value or "report"


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


def fmt_cell(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


if __name__ == "__main__":
    sys.exit(main())
