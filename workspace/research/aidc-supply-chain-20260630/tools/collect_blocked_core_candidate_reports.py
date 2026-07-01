#!/usr/bin/env python3
"""Collect broker-report evidence for blocked AIDC core candidates.

This script is case-scoped. It reads the current customer-chain audit, finds
rows where valuation is blocked, downloads public Eastmoney broker reports,
extracts text, and writes an evidence packet for later analyst review.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT_DIR = BASE / "sources" / "blocked-core-candidate-broker-reports-20260701"
REPORT_API = "https://reportapi.eastmoney.com/report/list2"
DETAIL_URL = "https://data.eastmoney.com/report/info/{info_code}.html"

KEYWORDS = (
    "AIDC",
    "IDC",
    "AI",
    "智能算力",
    "智算",
    "算力",
    "数据中心",
    "服务器",
    "交换机",
    "800G",
    "1.6T",
    "CPO",
    "LPO",
    "光模块",
    "光通信",
    "PCB",
    "CCL",
    "覆铜板",
    "液冷",
    "冷板",
    "CDU",
    "温控",
    "UPS",
    "HVDC",
    "变压器",
    "订单",
    "在手订单",
    "中标",
    "客户",
    "认证",
    "产能",
    "稼动率",
    "利用率",
    "毛利率",
    "收入",
    "营收",
    "出货",
    "backlog",
)

FIELD_KEYWORDS = {
    "revenue_exposure": ("收入", "营收", "业务", "占比", "AI", "数据中心", "算力"),
    "customer_or_platform": ("客户", "供应商", "认证", "导入", "CSP", "云", "运营商", "政企"),
    "order_or_backlog": ("订单", "在手订单", "中标", "合同", "交付", "出货", "backlog"),
    "capacity_or_certification": ("产能", "募投", "扩产", "认证", "产线", "基地", "项目"),
    "asp_or_price_proxy": ("ASP", "价格", "单价", "毛利率", "产品结构", "高端", "价值量"),
    "utilization_or_yield": ("利用率", "稼动率", "良率", "上架率", "投运", "PUE"),
    "margin_impact": ("毛利率", "净利率", "利润", "盈利", "费用", "现金流"),
}


@dataclass(frozen=True)
class Candidate:
    ticker: str
    company: str
    product_or_process: str
    candidate_method: str


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--begin", default="2025-01-01")
    parser.add_argument("--end", default="2026-07-01")
    parser.add_argument("--per-ticker", type=int, default=2)
    parser.add_argument("--page-size", type=int, default=30)
    parser.add_argument("--sleep", type=float, default=0.25)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates()
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.eastmoney.com/report/stock.jshtml",
            "Origin": "https://data.eastmoney.com",
            "Accept": "application/json, text/plain, */*",
        }
    )

    rows: list[dict[str, Any]] = []
    for idx, candidate in enumerate(candidates, 1):
        print(f"[{idx:02d}/{len(candidates):02d}] {candidate.ticker} {candidate.company}", flush=True)
        candidate_dir = OUT_DIR / f"{candidate.ticker}-{slug(candidate.company)}"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        try:
            reports = fetch_report_list(
                session,
                candidate.ticker,
                begin=args.begin,
                end=args.end,
                page_size=args.page_size,
            )
        except Exception as exc:
            rows.append(error_row(candidate, f"list_failed:{exc.__class__.__name__}"))
            continue
        selected = select_reports(reports, args.per_ticker)
        if not selected:
            rows.append(error_row(candidate, "not_found"))
            continue
        report_rows: list[dict[str, Any]] = []
        for report_index, report in enumerate(selected, 1):
            info_code = str(report.get("infoCode") or "")
            report_stem = f"{report_index:02d}-{info_code}-{slug(str(report.get('orgSName') or 'broker'))}-{slug(str(report.get('title') or 'report'))}"
            detail_path = candidate_dir / f"{report_stem}.md"
            pdf_path = candidate_dir / f"{report_stem}.pdf"
            txt_path = candidate_dir / f"{report_stem}.txt"
            errors: list[str] = []
            try:
                detail = fetch_detail(session, info_code)
            except Exception as exc:
                detail = {"detail_url": DETAIL_URL.format(info_code=info_code), "pdf_url": "", "notice_content": ""}
                errors.append(f"detail_failed:{exc.__class__.__name__}")
            pdf_url = str(detail.get("pdf_url") or "")
            if pdf_url and not pdf_path.exists():
                try:
                    download_pdf(session, pdf_url, pdf_path)
                except Exception as exc:
                    errors.append(f"pdf_failed:{exc.__class__.__name__}")
            if pdf_path.exists() and not txt_path.exists():
                try:
                    extract_text(pdf_path, txt_path)
                except Exception as exc:
                    errors.append(f"text_failed:{exc.__class__.__name__}")
            report_text = txt_path.read_text(encoding="utf-8", errors="ignore") if txt_path.exists() else str(detail.get("notice_content") or "")
            snippets = extract_snippets(report_text)
            field_snippets = {field: extract_snippets(report_text, words)[:3] for field, words in FIELD_KEYWORDS.items()}
            report_row = {
                "ticker": candidate.ticker,
                "company": candidate.company,
                "report_date": str(report.get("publishDate") or ""),
                "broker": str(report.get("orgSName") or report.get("orgName") or ""),
                "rating": str(report.get("emRatingName") or ""),
                "title": str(report.get("title") or ""),
                "info_code": info_code,
                "detail_url": DETAIL_URL.format(info_code=info_code) if info_code else "",
                "pdf_url": pdf_url,
                "pdf_path": rel(pdf_path) if pdf_path.exists() else "",
                "text_path": rel(txt_path) if txt_path.exists() else "",
                "detail_path": rel(detail_path),
                "errors": errors,
                "keyword_snippets": snippets[:8],
                "field_snippets": field_snippets,
                "evidence_score": evidence_score(snippets, field_snippets, bool(pdf_path.exists())),
            }
            detail_path.write_text(render_report_detail(report_row, detail), encoding="utf-8")
            report_rows.append(report_row)
            time.sleep(args.sleep)
        rows.append(
            {
                "ticker": candidate.ticker,
                "company": candidate.company,
                "product_or_process": candidate.product_or_process,
                "candidate_method": candidate.candidate_method,
                "reports_found": len(reports),
                "reports_archived": len(report_rows),
                "best_evidence_score": max((row["evidence_score"] for row in report_rows), default=0),
                "reports": report_rows,
                "field_summary": summarize_fields(report_rows),
            }
        )

    packet = {
        "case_id": "aidc-supply-chain-20260630",
        "collection_date": "2026-07-01",
        "source": "Eastmoney public broker report API",
        "blocked_candidate_count": len(candidates),
        "rows": rows,
    }
    (DATA / "blocked_core_candidate_report_collection_20260701.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "blocked_core_candidate_report_collection_20260701.md").write_text(render_index(packet), encoding="utf-8")
    print(json.dumps({"blocked_candidate_count": len(candidates), "rows": len(rows)}, ensure_ascii=False))
    return 0


def load_candidates() -> list[Candidate]:
    audit = json.loads((DATA / "customer_chain_audit.json").read_text(encoding="utf-8"))
    triage = json.loads((DATA / "valuation_triage_20260630.json").read_text(encoding="utf-8"))
    method_by_company = {str(row.get("company")): str(row.get("candidate_method") or "") for row in triage.get("rows", [])}
    candidates: list[Candidate] = []
    for row in audit.get("audits", []):
        if not row.get("blocks_valuation"):
            continue
        ticker = str(row.get("ticker") or "")
        if not ticker or ticker == "not collected":
            continue
        candidates.append(
            Candidate(
                ticker=ticker,
                company=str(row.get("company") or ""),
                product_or_process=str(row.get("product_or_process") or ""),
                candidate_method=method_by_company.get(str(row.get("company")), ""),
            )
        )
    return candidates


def fetch_report_list(session: requests.Session, code: str, *, begin: str, end: str, page_size: int) -> list[dict[str, Any]]:
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
    response = session.post(REPORT_API, json=payload, timeout=(10, 25))
    response.raise_for_status()
    data = response.json()
    reports = data.get("data", [])
    return [item for item in reports if isinstance(item, dict)]


def select_reports(reports: list[dict[str, Any]], per_ticker: int) -> list[dict[str, Any]]:
    scored = sorted(reports, key=report_score, reverse=True)
    return scored[:per_ticker]


def report_score(report: dict[str, Any]) -> tuple[int, str]:
    title = str(report.get("title") or "")
    rating = str(report.get("emRatingName") or "")
    keyword_hits = sum(1 for word in KEYWORDS if word.lower() in title.lower())
    rating_score = 1 if rating else 0
    return (keyword_hits + rating_score, str(report.get("publishDate") or ""))


def fetch_detail(session: requests.Session, info_code: str) -> dict[str, Any]:
    if not info_code:
        return {"pdf_url": "", "notice_content": ""}
    url = DETAIL_URL.format(info_code=info_code)
    response = session.get(url, timeout=(10, 20))
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


def download_pdf(session: requests.Session, url: str, path: Path) -> None:
    response = session.get(url, timeout=(10, 30), stream=True)
    response.raise_for_status()
    chunks: list[bytes] = []
    total = 0
    max_bytes = 30 * 1024 * 1024
    for chunk in response.iter_content(chunk_size=128 * 1024):
        if not chunk:
            continue
        chunks.append(chunk)
        total += len(chunk)
        if total > max_bytes:
            raise RuntimeError(f"PDF exceeds {max_bytes} bytes")
    content = b"".join(chunks)
    if not content.startswith(b"%PDF"):
        raise RuntimeError("downloaded content is not a PDF")
    path.write_bytes(content)


def extract_text(pdf_path: Path, text_path: Path) -> None:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        timeout=45,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "pdftotext failed")


def extract_snippets(body: str, words: tuple[str, ...] = KEYWORDS) -> list[str]:
    normalized = re.sub(r"\s+", " ", body)
    snippets: list[str] = []
    for word in words:
        pattern = re.compile(re.escape(word), flags=re.I)
        for match in pattern.finditer(normalized):
            start = max(0, match.start() - 90)
            end = min(len(normalized), match.end() + 130)
            snippet = normalized[start:end].strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 10:
                return snippets
    return snippets


def evidence_score(snippets: list[str], field_snippets: dict[str, list[str]], has_pdf: bool) -> int:
    covered_fields = sum(1 for rows in field_snippets.values() if rows)
    score = 1 + min(3, covered_fields // 2)
    if has_pdf and snippets:
        score += 1
    return min(score, 5)


def summarize_fields(report_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for field in FIELD_KEYWORDS:
        snippets: list[str] = []
        sources: list[str] = []
        for row in report_rows:
            for snippet in row.get("field_snippets", {}).get(field, []):
                if snippet not in snippets:
                    snippets.append(snippet)
                    sources.append(str(row.get("text_path") or row.get("detail_path") or ""))
        summary[field] = {
            "evidence_count": len(snippets),
            "snippets": snippets[:5],
            "sources": [source for source in sources if source][:5],
        }
    return summary


def render_report_detail(row: dict[str, Any], detail: dict[str, Any]) -> str:
    lines = [
        f"# {row['title']}",
        "",
        f"- Ticker: {row['ticker']} {row['company']}",
        f"- Broker: {row['broker']}",
        f"- Date: {row['report_date']}",
        f"- Rating: {row['rating']}",
        f"- Detail URL: {row['detail_url']}",
        f"- PDF URL: {row['pdf_url']}",
        f"- Text path: {row['text_path']}",
        f"- Evidence score: {row['evidence_score']}",
        "",
        "## Keyword Snippets",
        "",
    ]
    lines.extend(f"- {snippet}" for snippet in row["keyword_snippets"][:8])
    lines += ["", "## Field Snippets", ""]
    for field, snippets in row["field_snippets"].items():
        lines.append(f"### {field}")
        lines.extend(f"- {snippet}" for snippet in snippets[:3])
        lines.append("")
    notice = str(detail.get("notice_content") or "")
    if notice:
        lines += ["## Notice Content", "", notice[:3000]]
    return "\n".join(lines) + "\n"


def render_index(packet: dict[str, Any]) -> str:
    lines = [
        "# Blocked Core Candidate Broker Report Collection",
        "",
        f"- Collection date: {packet['collection_date']}",
        f"- Source: {packet['source']}",
        f"- Blocked candidates: {packet['blocked_candidate_count']}",
        "",
        "| Ticker | Company | Reports found | Archived | Best score | Field coverage |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in packet["rows"]:
        field_coverage = ", ".join(
            f"{field}:{payload.get('evidence_count', 0)}"
            for field, payload in row.get("field_summary", {}).items()
        )
        lines.append(
            f"| {row.get('ticker')} | {row.get('company')} | {row.get('reports_found', 0)} | {row.get('reports_archived', 0)} | {row.get('best_evidence_score', 0)} | {field_coverage} |"
        )
    return "\n".join(lines) + "\n"


def error_row(candidate: Candidate, status: str) -> dict[str, Any]:
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "product_or_process": candidate.product_or_process,
        "candidate_method": candidate.candidate_method,
        "reports_found": 0,
        "reports_archived": 0,
        "best_evidence_score": 0,
        "status": status,
        "field_summary": {},
        "reports": [],
    }


def slug(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip().lower())
    value = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value)
    return value.strip("-")[:80] or "report"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
