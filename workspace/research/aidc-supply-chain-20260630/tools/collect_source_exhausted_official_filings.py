#!/usr/bin/env python3
"""Collect official CNINFO filings for source-exhausted AIDC core candidates."""

from __future__ import annotations

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
OUT_DIR = BASE / "sources" / "source-exhausted-official-filings-20260701"
CNINFO_SEARCH = "http://www.cninfo.com.cn/new/information/topSearch/query"
CNINFO_QUERY = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_STATIC = "http://static.cninfo.com.cn/"

FIELD_KEYWORDS = {
    "revenue_exposure": ("收入", "营业收入", "主营业务", "分产品", "分行业", "数据中心", "算力", "服务器"),
    "customer_or_platform": ("客户", "前五名客户", "认证", "供应商", "数据中心", "互联网", "运营商"),
    "order_or_backlog": ("订单", "在手订单", "中标", "合同", "交付", "项目", "backlog"),
    "capacity_or_certification": ("产能", "募投", "扩产", "认证", "产线", "基地", "项目"),
    "asp_or_price_proxy": ("单价", "价格", "毛利率", "产品结构", "高端", "价值量"),
    "utilization_or_yield": ("利用率", "稼动率", "良率", "上架率", "投运", "PUE"),
    "margin_impact": ("毛利率", "净利率", "利润", "盈利", "费用", "现金流"),
}


@dataclass(frozen=True)
class Candidate:
    ticker: str
    company: str


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates()
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            "Accept": "application/json, text/plain, */*",
        }
    )
    rows: list[dict[str, Any]] = []
    for idx, candidate in enumerate(candidates, 1):
        print(f"[{idx:02d}/{len(candidates):02d}] {candidate.ticker} {candidate.company}", flush=True)
        try:
            org_id = lookup_org_id(session, candidate.ticker)
            announcements = fetch_announcements(session, candidate.ticker, org_id)
        except Exception as exc:
            rows.append(error_row(candidate, f"query_failed:{exc.__class__.__name__}"))
            continue
        candidate_dir = OUT_DIR / f"{candidate.ticker}-{slug(candidate.company)}"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        filings = []
        for item in announcements:
            filing = archive_announcement(session, candidate, item, candidate_dir)
            filings.append(filing)
            time.sleep(0.15)
        rows.append(
            {
                "ticker": candidate.ticker,
                "company": candidate.company,
                "org_id": org_id,
                "announcements_found": len(announcements),
                "filings_archived": len([f for f in filings if f.get("pdf_path")]),
                "best_evidence_score": max((f.get("evidence_score", 0) for f in filings), default=0),
                "filings": filings,
                "field_summary": summarize_fields(filings),
            }
        )
    packet = {
        "case_id": "aidc-supply-chain-20260630",
        "collection_date": "2026-07-01",
        "source": "CNINFO official announcements",
        "candidate_count": len(candidates),
        "rows": rows,
    }
    (DATA / "source_exhausted_official_filing_collection_20260701.json").write_text(
        json.dumps(packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (DATA / "source_exhausted_official_filing_collection_20260701.md").write_text(
        render_index(packet),
        encoding="utf-8",
    )
    print(json.dumps({"candidate_count": len(candidates), "rows": len(rows)}, ensure_ascii=False))
    return 0


def load_candidates() -> list[Candidate]:
    packet = json.loads((DATA / "blocked_core_candidate_report_collection_20260701.json").read_text(encoding="utf-8"))
    candidates = []
    for row in packet.get("rows", []):
        if int(row.get("reports_archived") or 0) > 0:
            continue
        candidates.append(Candidate(ticker=str(row.get("ticker")), company=str(row.get("company"))))
    return candidates


def lookup_org_id(session: requests.Session, ticker: str) -> str:
    response = session.post(CNINFO_SEARCH, data={"keyWord": ticker, "maxNum": 10}, timeout=(10, 20))
    response.raise_for_status()
    rows = response.json()
    for row in rows:
        if str(row.get("code")) == ticker and row.get("orgId"):
            return str(row["orgId"])
    raise RuntimeError(f"orgId not found for {ticker}")


def fetch_announcements(session: requests.Session, ticker: str, org_id: str) -> list[dict[str, Any]]:
    plate = "sz" if ticker.startswith(("0", "3")) else "sh"
    column = "szse" if plate == "sz" else "sse"
    categories = (
        ("category_ndbg_szsh", "annual"),
        ("category_bndbg_szsh", "semiannual"),
        ("category_yjdbg_szsh", "quarterly"),
    )
    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for category, label in categories:
        payload = {
            "pageNum": 1,
            "pageSize": 5,
            "column": column,
            "tabName": "fulltext",
            "plate": plate,
            "stock": f"{ticker},{org_id}",
            "searchkey": "",
            "secid": "",
            "category": category,
            "trade": "",
            "seDate": "2025-01-01~2026-07-01",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        response = session.post(CNINFO_QUERY, data=payload, timeout=(10, 25))
        response.raise_for_status()
        announcements = response.json().get("announcements") or []
        for announcement in announcements:
            title = str(announcement.get("announcementTitle") or "")
            url = str(announcement.get("adjunctUrl") or "")
            if not url or url in seen_urls:
                continue
            if label == "annual" and "摘要" in title and any("年度报告" in str(a.get("announcementTitle") or "") and "摘要" not in str(a.get("announcementTitle") or "") for a in selected):
                continue
            announcement["filing_type"] = label
            selected.append(announcement)
            seen_urls.add(url)
            break
    return selected


def archive_announcement(session: requests.Session, candidate: Candidate, item: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    title = str(item.get("announcementTitle") or "announcement")
    adjunct = str(item.get("adjunctUrl") or "")
    filing_type = str(item.get("filing_type") or "filing")
    stem = f"{filing_type}-{slug(title)}"
    pdf_url = CNINFO_STATIC + adjunct
    pdf_path = out_dir / f"{stem}.pdf"
    txt_path = out_dir / f"{stem}.txt"
    errors: list[str] = []
    if adjunct and not pdf_path.exists():
        try:
            download_pdf(session, pdf_url, pdf_path)
        except Exception as exc:
            errors.append(f"pdf_failed:{exc.__class__.__name__}")
    if pdf_path.exists() and not txt_path.exists():
        try:
            extract_text(pdf_path, txt_path)
        except Exception as exc:
            errors.append(f"text_failed:{exc.__class__.__name__}")
    text = txt_path.read_text(encoding="utf-8", errors="ignore") if txt_path.exists() else ""
    field_snippets = {field: extract_snippets(text, keywords)[:4] for field, keywords in FIELD_KEYWORDS.items()}
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "filing_type": filing_type,
        "title": title,
        "announcement_time": item.get("announcementTime"),
        "pdf_url": pdf_url,
        "pdf_path": rel(pdf_path) if pdf_path.exists() else "",
        "text_path": rel(txt_path) if txt_path.exists() else "",
        "errors": errors,
        "field_snippets": field_snippets,
        "evidence_score": evidence_score(field_snippets, bool(pdf_path.exists())),
    }


def download_pdf(session: requests.Session, url: str, path: Path) -> None:
    response = session.get(url, timeout=(10, 30), stream=True)
    response.raise_for_status()
    content = b"".join(chunk for chunk in response.iter_content(128 * 1024) if chunk)
    if not content.startswith(b"%PDF"):
        raise RuntimeError("downloaded content is not a PDF")
    path.write_bytes(content)


def extract_text(pdf_path: Path, text_path: Path) -> None:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "pdftotext failed")


def extract_snippets(body: str, words: tuple[str, ...]) -> list[str]:
    normalized = re.sub(r"\s+", " ", body)
    snippets: list[str] = []
    for word in words:
        for match in re.finditer(re.escape(word), normalized, flags=re.I):
            start = max(0, match.start() - 90)
            end = min(len(normalized), match.end() + 150)
            snippet = normalized[start:end].strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 12:
                return snippets
    return snippets


def evidence_score(field_snippets: dict[str, list[str]], has_pdf: bool) -> int:
    covered = sum(1 for rows in field_snippets.values() if rows)
    return min(5, (1 if has_pdf else 0) + min(4, covered))


def summarize_fields(filings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for field in FIELD_KEYWORDS:
        snippets: list[str] = []
        sources: list[str] = []
        for filing in filings:
            for snippet in filing.get("field_snippets", {}).get(field, []):
                if snippet not in snippets:
                    snippets.append(snippet)
                    sources.append(str(filing.get("text_path") or filing.get("pdf_path") or ""))
        summary[field] = {
            "evidence_count": len(snippets),
            "snippets": snippets[:6],
            "sources": [source for source in sources if source][:6],
        }
    return summary


def render_index(packet: dict[str, Any]) -> str:
    lines = [
        "# Source-Exhausted Official Filing Collection",
        "",
        f"- Collection date: {packet['collection_date']}",
        f"- Source: {packet['source']}",
        f"- Candidates: {packet['candidate_count']}",
        "",
        "| Ticker | Company | Filings archived | Best score | Field coverage |",
        "|---|---|---:|---:|---|",
    ]
    for row in packet["rows"]:
        coverage = ", ".join(
            f"{field}:{payload.get('evidence_count', 0)}"
            for field, payload in row.get("field_summary", {}).items()
        )
        lines.append(f"| {row['ticker']} | {row['company']} | {row['filings_archived']} | {row['best_evidence_score']} | {coverage} |")
    return "\n".join(lines) + "\n"


def error_row(candidate: Candidate, status: str) -> dict[str, Any]:
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "status": status,
        "filings_archived": 0,
        "best_evidence_score": 0,
        "field_summary": {},
        "filings": [],
    }


def slug(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip().lower())
    value = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value)
    return value.strip("-")[:100] or "filing"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
