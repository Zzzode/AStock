#!/usr/bin/env python3
"""Collect official CNINFO evidence for AIDC candidates with proxy fields."""

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
OUT_DIR = BASE / "sources" / "proxy-field-official-filings-20260701"
OUT_JSON = DATA / "proxy_field_official_filing_collection_20260701.json"
OUT_MD = DATA / "proxy_field_official_filing_collection_20260701.md"

CNINFO_SEARCH = "http://www.cninfo.com.cn/new/information/topSearch/query"
CNINFO_QUERY = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_STATIC = "http://static.cninfo.com.cn/"

FIELD_KEYWORDS = {
    "revenue_exposure": ("营业收入", "主营业务", "分产品", "数据中心", "算力", "服务器", "光模块", "PCB", "液冷"),
    "customer_or_platform": ("客户", "前五名客户", "认证", "导入", "互联网", "运营商", "云", "数据中心"),
    "order_or_backlog": ("订单", "在手订单", "中标", "合同", "交付", "出货", "预付款", "项目"),
    "capacity_or_certification": ("产能", "扩产", "投产", "量产", "基地", "工厂", "认证", "产线", "募投"),
    "asp_or_price_proxy": ("ASP", "单价", "价格", "产品结构", "毛利率", "高端", "价值量", "800G", "1.6T", "HDI"),
    "utilization_or_yield": ("利用率", "产能利用", "稼动率", "良率", "上架率", "投运", "爬坡", "PUE", "生产效率"),
    "margin_impact": ("毛利率", "净利率", "利润", "盈利", "成本", "费用率", "现金流"),
}


@dataclass(frozen=True)
class Candidate:
    ticker: str
    company: str
    proxy_fields: tuple[str, ...]
    target_model: bool


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--begin", default="2025-01-01")
    parser.add_argument("--end", default="2026-07-01")
    parser.add_argument("--sleep", type=float, default=0.12)
    parser.add_argument("--max-candidates", type=int, default=0)
    parser.add_argument("--ticker", action="append", default=[])
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates()
    if args.ticker:
        wanted = {str(ticker) for ticker in args.ticker}
        candidates = [candidate for candidate in candidates if candidate.ticker in wanted]
    if args.max_candidates > 0:
        candidates = candidates[: args.max_candidates]

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
        print(
            f"[{idx:02d}/{len(candidates):02d}] {candidate.ticker} {candidate.company} "
            f"proxy={','.join(candidate.proxy_fields)}",
            flush=True,
        )
        try:
            org_id = lookup_org_id(session, candidate.ticker)
            announcements = fetch_announcements(session, candidate.ticker, org_id, args.begin, args.end)
        except Exception as exc:
            rows.append(error_row(candidate, f"query_failed:{exc.__class__.__name__}"))
            continue

        candidate_dir = OUT_DIR / f"{candidate.ticker}-{slug(candidate.company)}"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        filings = []
        for item in announcements:
            filings.append(archive_announcement(session, candidate, item, candidate_dir))
            time.sleep(args.sleep)
        field_summary = summarize_fields(filings)
        rows.append(
            {
                "ticker": candidate.ticker,
                "company": candidate.company,
                "target_model": candidate.target_model,
                "proxy_fields_requested": list(candidate.proxy_fields),
                "org_id": org_id,
                "announcements_found": len(announcements),
                "filings_archived": len([f for f in filings if f.get("pdf_path")]),
                "best_evidence_score": max((f.get("evidence_score", 0) for f in filings), default=0),
                "field_summary": field_summary,
                "proxy_field_direct_hits": {
                    field: field_summary.get(field, {}).get("evidence_count", 0)
                    for field in candidate.proxy_fields
                },
                "filings": filings,
            }
        )

    packet = {
        "case_id": "aidc-supply-chain-20260630",
        "collection_date": "2026-07-01",
        "source": "CNINFO official announcements for proxy-field completion",
        "candidate_count": len(candidates),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_index(packet), encoding="utf-8")
    print(json.dumps({"candidate_count": len(candidates), "rows": len(rows)}, ensure_ascii=False))
    return 0


def load_candidates() -> list[Candidate]:
    packet = json.loads((DATA / "field_evidence_completion_20260701.json").read_text(encoding="utf-8"))
    candidates: list[Candidate] = []
    for row in packet.get("rows", []):
        proxy_fields = tuple(
            field
            for field, cell in row.get("fields", {}).items()
            if cell.get("status") == "proxy"
        )
        if not proxy_fields:
            continue
        candidates.append(
            Candidate(
                ticker=str(row.get("ticker") or ""),
                company=str(row.get("company") or ""),
                proxy_fields=proxy_fields,
                target_model=bool(row.get("target_model")),
            )
        )
    return candidates


def lookup_org_id(session: requests.Session, ticker: str) -> str:
    response = session.post(CNINFO_SEARCH, data={"keyWord": ticker, "maxNum": 10}, timeout=(10, 20))
    response.raise_for_status()
    rows = response.json()
    for row in rows:
        if str(row.get("code")) == ticker and row.get("orgId"):
            return str(row["orgId"])
    raise RuntimeError(f"orgId not found for {ticker}")


def fetch_announcements(session: requests.Session, ticker: str, org_id: str, begin: str, end: str) -> list[dict[str, Any]]:
    plate = "sz" if ticker.startswith(("0", "3")) else "sh"
    column = "szse" if plate == "sz" else "sse"
    categories = (
        ("category_ndbg_szsh", "annual"),
        ("category_bndbg_szsh", "semiannual"),
        ("category_yjdbg_szsh", "quarterly"),
        ("category_tzzgx_szsh", "ir"),
    )
    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for category, label in categories:
        payload = {
            "pageNum": 1,
            "pageSize": 10,
            "column": column,
            "tabName": "fulltext",
            "plate": plate,
            "stock": f"{ticker},{org_id}",
            "searchkey": "",
            "secid": "",
            "category": category,
            "trade": "",
            "seDate": f"{begin}~{end}",
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
            if "摘要" in title and any(title.replace("摘要", "") in str(x.get("announcementTitle") or "") for x in selected):
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
    field_snippets = {field: extract_snippets(text, keywords)[:6] for field, keywords in FIELD_KEYWORDS.items()}
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
    response = session.get(url, timeout=(10, 35), stream=True)
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
        timeout=90,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "pdftotext failed")


def extract_snippets(body: str, words: tuple[str, ...]) -> list[str]:
    normalized = re.sub(r"\s+", " ", body)
    snippets: list[str] = []
    for word in words:
        for match in re.finditer(re.escape(word), normalized, flags=re.I):
            start = max(0, match.start() - 120)
            end = min(len(normalized), match.end() + 220)
            snippet = normalized[start:end].strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 16:
                return snippets
    return snippets


def evidence_score(field_snippets: dict[str, list[str]], has_pdf: bool) -> int:
    covered = sum(1 for rows in field_snippets.values() if rows)
    return min(7, (2 if has_pdf else 0) + min(5, covered))


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
            "snippets": snippets[:8],
            "sources": [source for source in sources if source][:8],
        }
    return summary


def render_index(packet: dict[str, Any]) -> str:
    lines = [
        "# Proxy-Field Official Filing Collection",
        "",
        f"- Collection date: {packet['collection_date']}",
        f"- Candidate count: {packet['candidate_count']}",
        "",
        "| Ticker | Company | Proxy fields | Filings archived | Best score | Proxy-field hits |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in packet["rows"]:
        hits = ", ".join(f"{k}:{v}" for k, v in row.get("proxy_field_direct_hits", {}).items())
        lines.append(
            f"| {row['ticker']} | {row['company']} | {', '.join(row.get('proxy_fields_requested', []))} | "
            f"{row.get('filings_archived', 0)} | {row.get('best_evidence_score', 0)} | {hits} |"
        )
    return "\n".join(lines) + "\n"


def error_row(candidate: Candidate, error: str) -> dict[str, Any]:
    return {
        "ticker": candidate.ticker,
        "company": candidate.company,
        "target_model": candidate.target_model,
        "proxy_fields_requested": list(candidate.proxy_fields),
        "org_id": "",
        "announcements_found": 0,
        "filings_archived": 0,
        "best_evidence_score": 0,
        "field_summary": {},
        "proxy_field_direct_hits": {},
        "filings": [],
        "errors": [error],
    }


def slug(value: str, limit: int = 48) -> str:
    text = re.sub(r"[\\/:*?\"<>|\\s]+", "-", value).strip("-")
    return text[:limit] or "item"


def rel(path: Path) -> str:
    return str(path.relative_to(BASE))


if __name__ == "__main__":
    raise SystemExit(main())
