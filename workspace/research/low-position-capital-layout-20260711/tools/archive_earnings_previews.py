#!/usr/bin/env python3
"""Archive and validate official 2026H1 earnings-preview announcement PDFs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "earnings-previews-20260711"
INDEX_URL = "https://np-anotice-stock.eastmoney.com/api/security/ann"
CONTENT_URL = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://data.eastmoney.com/notices/",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def fetch_preview_notice(ticker: str) -> dict[str, Any]:
    response = requests.get(
        INDEX_URL,
        params={
            "sr": "-1",
            "page_size": "100",
            "page_index": "1",
            "ann_type": "A",
            "client_source": "web",
            "f_node": "0",
            "s_node": "0",
            "begin_time": "2026-06-25",
            "end_time": "2026-07-11",
            "stock_list": ticker,
        },
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    notices = (response.json().get("data") or {}).get("list") or []
    matches = [
        item
        for item in notices
        if "半年度业绩预" in str(item.get("title") or item.get("title_ch") or "")
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"{ticker}: expected exactly one H1 preview notice, found {len(matches)}"
        )
    notice = matches[0]
    art_code = str(notice.get("art_code") or "")
    content_response = requests.get(
        CONTENT_URL,
        params={"art_code": art_code, "client_source": "web"},
        headers=HEADERS,
        timeout=30,
    )
    content_response.raise_for_status()
    content = content_response.json().get("data") or {}
    attach_url = str(content.get("attach_url") or content.get("attach_url_web") or "")
    if not attach_url:
        raise RuntimeError(f"{ticker}: missing announcement attachment URL")
    return {
        "ticker": ticker,
        "art_code": art_code,
        "announcement_date": str(notice.get("notice_date") or "")[:10],
        "title": str(notice.get("title") or notice.get("title_ch") or ""),
        "notice_url": f"https://data.eastmoney.com/notices/detail/{ticker}/{art_code}.html",
        "attach_url": attach_url,
        "content_char_count": len(str(content.get("notice_content") or "")),
    }


def download_and_validate(row: dict[str, Any], company: str) -> dict[str, Any]:
    ticker = row["ticker"]
    pdf_path = SOURCE_DIR / f"{ticker}_preview.pdf"
    text_path = SOURCE_DIR / f"{ticker}_preview.txt"
    response = requests.get(row["attach_url"], headers=HEADERS, timeout=60)
    response.raise_for_status()
    body = response.content
    if not body.startswith(b"%PDF"):
        raise RuntimeError(f"{ticker}: attachment body is not a PDF")
    pdf_path.write_bytes(body)
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{ticker}: pdftotext failed: {completed.stderr.strip()}")
    text = text_path.read_text(errors="ignore")
    compact_text = "".join(text.split())
    if ticker not in compact_text:
        raise RuntimeError(f"{ticker}: extracted announcement does not contain ticker")
    if "半年度业绩预" not in compact_text:
        raise RuntimeError(f"{ticker}: extracted announcement title is not an H1 preview")
    if company not in compact_text and company not in row["title"]:
        raise RuntimeError(f"{ticker}: extracted announcement does not match {company}")
    return {
        **row,
        "company": company,
        "local_pdf": str(pdf_path.relative_to(CASE_DIR)),
        "local_text": str(text_path.relative_to(CASE_DIR)),
        "pdf_size": pdf_path.stat().st_size,
        "text_char_count": len(text),
        "validation_status": "PASS",
    }


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    preview_quality = load_json(DATA_DIR / "earnings_preview_quality_20260711.json")
    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for preview in preview_quality["rows"]:
        ticker = preview["ticker"]
        company = preview["company"]
        try:
            notice = fetch_preview_notice(ticker)
            results.append(download_and_validate(notice, company))
            print(f"PASS {ticker} {company}")
        except Exception as exc:
            failures.append(
                {"ticker": ticker, "company": company, "error": repr(exc)}
            )
            print(f"FAIL {ticker} {company}: {exc}")

    manifest = {
        "schema_version": "astock.earnings_preview_archive.v1",
        "data_cutoff": "2026-07-11",
        "expected_count": preview_quality["row_count"],
        "archived_count": len(results),
        "failure_count": len(failures),
        "rows": results,
        "failures": failures,
    }
    write_json(DATA_DIR / "earnings_preview_archive_20260711.json", manifest)
    lines = [
        "# 2026H1 Earnings Preview Announcement Archive",
        "",
        f"- Expected: {manifest['expected_count']}",
        f"- Archived and validated: {manifest['archived_count']}",
        f"- Failures: {manifest['failure_count']}",
        "",
        "| Ticker | Company | Date | Title | PDF bytes | Text chars | Status | Local PDF |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['announcement_date']} | "
            f"{row['title']} | {row['pdf_size']} | {row['text_char_count']} | "
            f"{row['validation_status']} | `{row['local_pdf']}` |"
        )
    if failures:
        lines += ["", "## Failures", ""]
        for failure in failures:
            lines.append(
                f"- {failure['ticker']} {failure['company']}: {failure['error']}"
            )
    write_text(DATA_DIR / "earnings_preview_archive_20260711.md", "\n".join(lines))
    write_text(SOURCE_DIR / "index.md", "\n".join(lines))
    if failures or len(results) != preview_quality["row_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
