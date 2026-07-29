#!/usr/bin/env python3
"""Collect report metadata for the full universe and PDFs for priority names."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import akshare as ak
import pandas as pd
import requests


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
SOURCE_DIR = CASE_DIR / "sources" / "core-broker-reports-20260711"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
PRIORITY_TIERS = {"core", "core_candidate", "preview_candidate"}
MAX_PDFS_PER_PRIORITY = 2

POST_PREVIEW_METADATA_OVERRIDES = {
    "601138": {
        "latest_report_date": "2026-07-10",
        "latest_report_title": "AI推动1H26净利润同比预增93%~101%",
        "latest_broker": "华泰证券",
        "latest_rating": "买入",
        "latest_2026e_eps": 2.82,
        "latest_2026e_pe": 23.5,
        "report_vs_preview": "post_preview",
        "post_preview_source": (
            "sources/core-broker-reports-20260711/"
            "601138-huatai-post-preview.html"
        ),
        "post_preview_cross_check": (
            "sources/core-broker-reports-20260711/"
            "601138-huachuang-post-preview.html"
        ),
    }
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def safe_slug(value: str, max_length: int = 48) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value).strip("-")
    return cleaned[:max_length] or "report"


def format_date(value: Any) -> str:
    if value is None or pd.isna(value):
        return "not disclosed"
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def report_relation(report_date: str, preview_date: str) -> str:
    if preview_date == "not disclosed":
        return "no_preview_date"
    if report_date == "not disclosed":
        return "unknown"
    report_ts = pd.Timestamp(report_date)
    preview_ts = pd.Timestamp(preview_date)
    if report_ts > preview_ts:
        return "post_preview"
    if report_ts == preview_ts:
        return "same_day_as_preview"
    return "pre_preview_forecast_may_be_stale"


def fetch_reports(ticker: str, attempts: int = 2) -> pd.DataFrame:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return ak.stock_research_report_em(symbol=ticker)
        except Exception as exc:
            last_error = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"report metadata failed for {ticker}: {last_error}")


def download_pdf(url: str, path: Path) -> tuple[bool, str]:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=45,
        )
        response.raise_for_status()
        path.write_bytes(response.content)
        if not response.content.startswith(b"%PDF"):
            return False, "downloaded body is not a PDF"
        return True, "ok"
    except Exception as exc:
        return False, repr(exc)


def apply_post_preview_overrides(payload: dict[str, Any]) -> dict[str, Any]:
    for row in payload["metadata_rows"]:
        row.update(POST_PREVIEW_METADATA_OVERRIDES.get(row["ticker"], {}))
    return payload


def catalog_markdown(payload: dict[str, Any]) -> str:
    metadata_rows = payload["metadata_rows"]
    download_rows = payload["download_rows"]
    failures = payload["failures"]
    lines = [
        "# Core Broker Report Catalog",
        "",
        f"- Universe: {payload['universe_count']}",
        f"- Priority names: {payload['priority_count']}",
        f"- PDFs downloaded: {sum(row['status'] == 'downloaded' for row in download_rows)}",
        f"- Failures: {len(failures)}",
        "",
        "## Full-Universe Metadata",
        "",
        "| Sector | Tier | Ticker | Company | Reports | Latest date | Latest broker | Rating | 2026E EPS | 2026E PE | Relation to preview |",
        "|---|---|---|---|---:|---|---|---|---:|---:|---|",
    ]
    for row in metadata_rows:
        eps = f"{row['latest_2026e_eps']:.2f}" if row["latest_2026e_eps"] else "-"
        pe = f"{row['latest_2026e_pe']:.1f}" if row["latest_2026e_pe"] else "-"
        lines.append(
            f"| {row['sector']} | {row['tier']} | {row['ticker']} | "
            f"{row['company']} | {row['report_count']} | "
            f"{row['latest_report_date']} | {row['latest_broker']} | "
            f"{row['latest_rating']} | {eps} | {pe} | {row['report_vs_preview']} |"
        )
    lines += [
        "",
        "## Priority PDF Archive",
        "",
        "| Ticker | Company | Broker | Date | Rating | 2026E EPS | Status | Relation to preview | Local PDF |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    for row in download_rows:
        eps = f"{row['eps_2026e']:.2f}" if row["eps_2026e"] else "-"
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['broker']} | "
            f"{row['report_date']} | {row['rating']} | {eps} | "
            f"{row['status']} | {row['report_vs_preview']} | "
            f"`{row['local_pdf']}` |"
        )
    lines += [
        "",
        "## Post-Preview Supplemental Reports",
        "",
        "- 601138 Industrial Fulian: Huatai 2026-07-10 published CNY2.82 "
        "2026E EPS, 33x PE and CNY93 target; Huachuang published CNY64.597bn "
        "2026E net profit without a point target. Both full pages are archived "
        "under `sources/core-broker-reports-20260711/`.",
    ]
    if failures:
        lines += ["", "## Failed Probes", ""]
        for failure in failures:
            lines.append(
                f"- {failure['ticker']} {failure['company']} "
                f"[{failure['stage']}]: {failure['error']}"
            )
    return "\n".join(lines)


def main() -> None:
    if "--overrides-only" in sys.argv:
        catalog_path = DATA_DIR / "core_broker_report_catalog_20260711.json"
        payload = apply_post_preview_overrides(load_json(catalog_path))
        write_json(catalog_path, payload)
        markdown = catalog_markdown(payload)
        write_text(DATA_DIR / "core_broker_report_catalog_20260711.md", markdown)
        write_text(SOURCE_DIR / "index.md", markdown)
        print(json.dumps({"overrides_applied": sorted(POST_PREVIEW_METADATA_OVERRIDES)}, indent=2))
        return

    census = load_json(DATA_DIR / "core_universe_preview_census_20260711.json")
    universe = census["rows"]
    metadata_rows: list[dict[str, Any]] = []
    download_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for index, company in enumerate(universe, 1):
        ticker = company["ticker"]
        name = company["company"]
        try:
            reports = fetch_reports(ticker)
        except Exception as exc:
            failures.append(
                {
                    "ticker": ticker,
                    "company": name,
                    "stage": "metadata",
                    "error": repr(exc),
                }
            )
            metadata_rows.append(
                {
                    **company,
                    "report_count": 0,
                    "latest_report_date": "not found",
                    "latest_report_title": "not found",
                    "latest_broker": "not found",
                    "latest_rating": "not found",
                    "latest_2026e_eps": None,
                    "latest_2026e_pe": None,
                    "report_vs_preview": "not found",
                }
            )
            continue

        if not reports.empty:
            reports = reports.copy()
            reports["日期"] = pd.to_datetime(reports["日期"])
            reports.sort_values("日期", ascending=False, inplace=True)
        latest = reports.iloc[0].to_dict() if not reports.empty else {}
        latest_date = format_date(latest.get("日期"))
        metadata_rows.append(
            {
                **company,
                "report_count": int(len(reports)),
                "latest_report_date": latest_date,
                "latest_report_title": latest.get("报告名称", "not found"),
                "latest_broker": latest.get("机构", "not found"),
                "latest_rating": latest.get("东财评级", "not found"),
                "latest_2026e_eps": float(latest["2026-盈利预测-收益"])
                if latest and pd.notna(latest.get("2026-盈利预测-收益"))
                else None,
                "latest_2026e_pe": float(latest["2026-盈利预测-市盈率"])
                if latest and pd.notna(latest.get("2026-盈利预测-市盈率"))
                else None,
                "report_vs_preview": report_relation(
                    latest_date, company["announcement_date"]
                ),
            }
        )

        raw_records = json.loads(
            reports.head(20).to_json(
                orient="records", force_ascii=False, date_format="iso"
            )
        )
        ticker_dir = SOURCE_DIR / f"{ticker}-{safe_slug(name)}"
        ticker_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            ticker_dir / "report_metadata.json",
            {
                "ticker": ticker,
                "company": name,
                "report_count": int(len(reports)),
                "rows": raw_records,
            },
        )

        if company["tier"] not in PRIORITY_TIERS:
            continue
        for sequence, (_, report) in enumerate(
            reports.head(MAX_PDFS_PER_PRIORITY).iterrows(), 1
        ):
            report_date = format_date(report["日期"])
            broker = str(report["机构"])
            title = str(report["报告名称"])
            pdf_url = str(report["报告PDF链接"])
            file_name = (
                f"{sequence:02d}-{report_date}-{safe_slug(broker, 18)}-"
                f"{safe_slug(title, 42)}.pdf"
            )
            pdf_path = ticker_dir / file_name
            if not pdf_path.exists():
                ok, note = download_pdf(pdf_url, pdf_path)
            else:
                ok = pdf_path.read_bytes().startswith(b"%PDF")
                note = "cached" if ok else "cached file is not PDF"
            if ok:
                text_path = pdf_path.with_suffix(".txt")
                if not text_path.exists():
                    import subprocess

                    completed = subprocess.run(
                        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    if completed.returncode != 0:
                        note += f"; pdftotext failed: {completed.stderr.strip()}"
                status = "downloaded"
            else:
                status = "failed"
                failures.append(
                    {
                        "ticker": ticker,
                        "company": name,
                        "stage": "pdf_download",
                        "error": note,
                    }
                )
            download_rows.append(
                {
                    "ticker": ticker,
                    "company": name,
                    "sector": company["sector"],
                    "tier": company["tier"],
                    "sequence": sequence,
                    "broker": broker,
                    "report_date": report_date,
                    "title": title,
                    "rating": report["东财评级"],
                    "eps_2026e": float(report["2026-盈利预测-收益"])
                    if pd.notna(report.get("2026-盈利预测-收益"))
                    else None,
                    "pe_2026e": float(report["2026-盈利预测-市盈率"])
                    if pd.notna(report.get("2026-盈利预测-市盈率"))
                    else None,
                    "pdf_url": pdf_url,
                    "local_pdf": str(pdf_path.relative_to(CASE_DIR)),
                    "local_text": str(pdf_path.with_suffix(".txt").relative_to(CASE_DIR))
                    if pdf_path.with_suffix(".txt").exists()
                    else "not found",
                    "status": status,
                    "note": note,
                    "report_vs_preview": report_relation(
                        report_date, company["announcement_date"]
                    ),
                }
            )
        print(f"{index}/{len(universe)} {ticker} {name} reports={len(reports)}")

    payload = apply_post_preview_overrides(
        {
            "schema_version": "astock.core_broker_catalog.v1",
            "data_cutoff": "2026-07-11",
            "universe_count": len(universe),
            "priority_count": sum(
                row["tier"] in PRIORITY_TIERS for row in universe
            ),
            "metadata_rows": metadata_rows,
            "download_rows": download_rows,
            "failures": failures,
        }
    )
    write_json(DATA_DIR / "core_broker_report_catalog_20260711.json", payload)
    markdown = catalog_markdown(payload)
    write_text(DATA_DIR / "core_broker_report_catalog_20260711.md", markdown)
    write_text(SOURCE_DIR / "index.md", markdown)
    print(
        json.dumps(
            {
                "universe_count": len(universe),
                "priority_count": sum(
                    row["tier"] in PRIORITY_TIERS for row in universe
                ),
                "downloaded": sum(
                    row["status"] == "downloaded" for row in download_rows
                ),
                "failed": len(failures),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
