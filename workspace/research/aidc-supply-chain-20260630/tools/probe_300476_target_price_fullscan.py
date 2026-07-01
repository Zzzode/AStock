#!/usr/bin/env python3
"""Full public-corpus target-price probe for 300476.

This case probe archives all Eastmoney public broker-report rows for 300476
and scans downloaded PDF text for explicit target-price language. It is an
evidence generator, not a valuation shortcut: weak media/aggregator numbers are
recorded as rejected evidence and must not become a positive Street anchor.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import requests


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT_DIR = BASE / "sources" / "probe-300476-eastmoney-fullscan-20260630"
REPORT_API = "https://reportapi.eastmoney.com/report/list2"
DETAIL_URL = "https://data.eastmoney.com/report/info/{info_code}.html"
TICKER = "300476"
COMPANY = "胜宏科技"
BEGIN = "2022-01-01"
END = "2026-06-30"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.eastmoney.com/report/stock.jshtml",
            "Origin": "https://data.eastmoney.com",
            "Accept": "application/json, text/plain, */*",
        }
    )
    reports = fetch_report_list(session)
    scan_rows: list[dict[str, Any]] = []
    for idx, report in enumerate(reports, 1):
        print(f"[{idx:02d}/{len(reports):02d}] {report.get('publishDate')} {report.get('orgSName')} {report.get('title')}", flush=True)
        info_code = str(report.get("infoCode") or "")
        row_errors: list[str] = []
        try:
            detail = fetch_detail(session, info_code)
        except Exception as exc:
            detail = {"detail_url": DETAIL_URL.format(info_code=info_code) if info_code else "", "pdf_url": "", "notice_content": ""}
            row_errors.append(f"detail_failed:{exc.__class__.__name__}")
        stem = f"{idx:02d}-{info_code}-{slug(str(report.get('orgSName') or 'broker'))}-{slug(str(report.get('title') or 'report'))}"
        detail_path = OUT_DIR / f"{stem}.md"
        pdf_path = OUT_DIR / f"{stem}.pdf"
        text_path = OUT_DIR / f"{stem}.txt"
        if detail.get("pdf_url") and not pdf_path.exists():
            try:
                download_pdf(session, str(detail["pdf_url"]), pdf_path)
            except Exception as exc:
                row_errors.append(f"pdf_failed:{exc.__class__.__name__}")
        if pdf_path.exists() and not text_path.exists():
            try:
                extract_text(pdf_path, text_path)
            except Exception as exc:
                row_errors.append(f"text_failed:{exc.__class__.__name__}")
        pdf_text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path.exists() else ""
        target_candidates = find_explicit_target_candidates(pdf_text)
        row = {
            "sequence": idx,
            "ticker": TICKER,
            "company": COMPANY,
            "report_date": str(report.get("publishDate") or ""),
            "broker": str(report.get("orgSName") or report.get("orgName") or ""),
            "rating": str(report.get("emRatingName") or ""),
            "title": str(report.get("title") or ""),
            "info_code": info_code,
            "detail_url": DETAIL_URL.format(info_code=info_code) if info_code else "",
            "pdf_url": str(detail.get("pdf_url") or ""),
            "api_target_low": value_or_blank(report.get("indvAimPriceL")),
            "api_target_high": value_or_blank(report.get("indvAimPriceT")),
            "api_target_available": bool(value_or_blank(report.get("indvAimPriceL")) or value_or_blank(report.get("indvAimPriceT"))),
            "pdf_path": rel(pdf_path) if pdf_path.exists() else "",
            "text_path": rel(text_path) if text_path.exists() else "",
            "target_candidates": target_candidates,
            "explicit_target_found": bool(target_candidates),
            "errors": row_errors,
        }
        detail_path.write_text(render_detail(row, detail, pdf_text), encoding="utf-8")
        row["detail_path"] = rel(detail_path)
        scan_rows.append(row)

    explicit_rows = [row for row in scan_rows if row["api_target_available"] or row["explicit_target_found"]]
    packet = {
        "ticker": TICKER,
        "company": COMPANY,
        "probe_date": "2026-06-30",
        "source": "Eastmoney public broker report API plus downloaded public PDFs",
        "date_range": {"begin": BEGIN, "end": END},
        "report_count": len(scan_rows),
        "api_target_count": sum(1 for row in scan_rows if row["api_target_available"]),
        "pdf_explicit_target_count": sum(1 for row in scan_rows if row["explicit_target_found"]),
        "explicit_target_rows": explicit_rows,
        "rows": scan_rows,
        "verdict": "no explicit public A-share broker target price found in this Eastmoney full scan"
        if not explicit_rows
        else "manual review required for candidate target-price rows",
    }
    (OUT_DIR / "scan_results.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "index.md").write_text(render_index(packet), encoding="utf-8")
    update_probe_summary(packet)
    print(json.dumps({k: packet[k] for k in ("report_count", "api_target_count", "pdf_explicit_target_count", "verdict")}, ensure_ascii=False))
    return 0


def fetch_report_list(session: requests.Session) -> list[dict[str, Any]]:
    payload = {
        "beginTime": BEGIN,
        "endTime": END,
        "industryCode": "*",
        "ratingChange": "*",
        "rating": "*",
        "orgCode": "*",
        "code": TICKER,
        "rcode": "",
        "pageSize": 100,
        "pageNo": 1,
    }
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = session.post(REPORT_API, json=payload, timeout=(10, 30))
            response.raise_for_status()
            data = response.json()
            reports = data.get("data", [])
            return [item for item in reports if isinstance(item, dict)]
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(attempt * 1.5)
    raise RuntimeError(f"Eastmoney report list failed after retries: {last_error}")


def fetch_detail(session: requests.Session, info_code: str) -> dict[str, Any]:
    if not info_code:
        return {"pdf_url": "", "notice_content": ""}
    url = DETAIL_URL.format(info_code=info_code)
    response = retry_get(session, url, timeout=(10, 20))
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
    response = session.get(url, timeout=(5, 12), stream=True)
    response.raise_for_status()
    chunks: list[bytes] = []
    total = 0
    max_bytes = 25 * 1024 * 1024
    for chunk in response.iter_content(chunk_size=128 * 1024):
        if not chunk:
            continue
        chunks.append(chunk)
        total += len(chunk)
        if total > max_bytes:
            raise RuntimeError(f"PDF exceeds {max_bytes} bytes")
    content = b"".join(chunks)
    if content.startswith(b"%PDF"):
        path.write_bytes(content)
    else:
        raise RuntimeError("downloaded content is not a PDF")


def retry_get(
    session: requests.Session, url: str, *, timeout: tuple[int, int]
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(attempt * 1.5)
    raise RuntimeError(f"GET failed after retries for {url}: {last_error}")


def extract_text(pdf_path: Path, text_path: Path) -> None:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        text_path.write_text("", encoding="utf-8")


def find_explicit_target_candidates(text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for pattern in (
        r"目标价[^。；;\n]{0,40}?([0-9]{2,4}(?:\.[0-9]+)?)\s*元",
        r"目标价格[^。；;\n]{0,40}?([0-9]{2,4}(?:\.[0-9]+)?)\s*元",
        r"合理(?:价值|价格|股价)[^。；;\n]{0,40}?([0-9]{2,4}(?:\.[0-9]+)?)\s*元",
        r"对应目标市值[^。；;\n]{0,80}?目标价[^。；;\n]{0,40}?([0-9]{2,4}(?:\.[0-9]+)?)\s*元",
    ):
        for match in re.finditer(pattern, text, flags=re.I):
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            candidates.append(
                {
                    "value": float(match.group(1)),
                    "context": re.sub(r"\s+", " ", text[start:end]).strip(),
                }
            )
    return candidates


def render_detail(row: dict[str, Any], detail: dict[str, Any], text: str) -> str:
    snippets = "\n".join(f"- {item['value']}: {item['context']}" for item in row["target_candidates"]) or "- none"
    return (
        f"# {row['title']}\n\n"
        f"- Ticker: {row['ticker']} {row['company']}\n"
        f"- Broker: {row['broker']}\n"
        f"- Date: {row['report_date']}\n"
        f"- Rating: {row['rating']}\n"
        f"- Detail URL: {row['detail_url']}\n"
        f"- PDF URL: {row['pdf_url']}\n"
        f"- API target low/high: {row['api_target_low']} / {row['api_target_high']}\n"
        f"- Explicit target candidates:\n{snippets}\n\n"
        "## Notice Content\n\n"
        f"{detail.get('notice_content') or 'not available'}\n\n"
        "## Text Preview\n\n"
        f"{text[:4000]}\n"
    )


def render_index(packet: dict[str, Any]) -> str:
    lines = [
        "# 300476 Eastmoney Full Target-Price Scan",
        "",
        f"- Ticker: {packet['ticker']} {packet['company']}",
        f"- Date range: {packet['date_range']['begin']} to {packet['date_range']['end']}",
        f"- Reports scanned: {packet['report_count']}",
        f"- API target rows: {packet['api_target_count']}",
        f"- PDF explicit target rows: {packet['pdf_explicit_target_count']}",
        f"- Verdict: {packet['verdict']}",
        "",
        "| # | Date | Broker | Rating | API target | PDF target candidate | Title | Text |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in packet["rows"]:
        api_target = f"{row['api_target_low']}/{row['api_target_high']}" if row["api_target_available"] else "not disclosed"
        candidates = "; ".join(str(item["value"]) for item in row["target_candidates"]) or "none"
        lines.append(
            f"| {row['sequence']} | {row['report_date'][:10]} | {row['broker']} | {row['rating']} | "
            f"{api_target} | {candidates} | {row['title']} | [{Path(row['text_path']).name}]({Path(row['text_path']).name}) |"
        )
    lines.append("")
    return "\n".join(lines)


def update_probe_summary(packet: dict[str, Any]) -> None:
    path = BASE / "sources" / "probe-300476-target-price-20260630.md"
    prior = path.read_text(encoding="utf-8") if path.exists() else "# 300476 Target-Price Probe\n\n"
    block = (
        "\n## Eastmoney Full Public-Report Scan\n\n"
        f"- Scan path: `sources/probe-300476-eastmoney-fullscan-20260630/`\n"
        f"- Date range: {BEGIN} to {END}\n"
        f"- Reports scanned: {packet['report_count']}\n"
        f"- API target rows: {packet['api_target_count']}\n"
        f"- PDF explicit target rows: {packet['pdf_explicit_target_count']}\n"
        f"- Verdict: {packet['verdict']}\n"
    )
    if "## Eastmoney Full Public-Report Scan" in prior:
        prior = prior.split("## Eastmoney Full Public-Report Scan", 1)[0].rstrip() + "\n"
    path.write_text(prior.rstrip() + block, encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(BASE))


def value_or_blank(value: Any) -> str:
    return "" if value is None else str(value).strip()


def slug(value: str) -> str:
    value = re.sub(r"\s+", "-", value.strip().lower())
    value = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff._-]+", "-", value)
    return value.strip("-")[:64] or "item"


if __name__ == "__main__":
    raise SystemExit(main())
