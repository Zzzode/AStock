#!/usr/bin/env python3
"""Build auditable report digests from the 56 archived broker PDF texts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def normalize_text(text: str) -> str:
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def excerpt_after(
    text: str, patterns: list[str], length: int, fallback: str = "not extracted"
) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            excerpt = text[match.end() : match.end() + length].strip(" ：:；;，,")
            return excerpt or fallback
    return fallback


def clean_excerpt(text: str, limit: int) -> str:
    text = re.sub(
        r"(请务必阅读|市场有风险|免责声明|证券投资评级说明|投资评级说明).*$",
        "",
        text,
    )
    text = text.strip()
    return text[:limit].rstrip(" ，；。") + ("…" if len(text) > limit else "")


def main() -> None:
    catalog = load_json(DATA_DIR / "core_broker_report_catalog_20260711.json")
    company_cards = load_json(DATA_DIR / "company_cards_20260711.json")
    disposition_map = {
        row["ticker"]: {
            "disposition": row["valuation_disposition"],
            "monitor": row["upgrade_or_monitor_trigger"],
            "preview_status": row["preview_status"],
            "report_vs_preview": row["report_vs_preview"],
        }
        for row in company_cards["rows"]
    }

    report_rows: list[dict[str, Any]] = []
    for report in catalog["download_rows"]:
        text_path = CASE_DIR / report["local_text"]
        normalized = normalize_text(text_path.read_text(errors="ignore"))
        thesis = clean_excerpt(
            excerpt_after(
                normalized,
                [
                    r"核心观点",
                    r"投资要点",
                    r"事件[:：]",
                    r"报告要点",
                ],
                900,
            ),
            520,
        )
        forecast = clean_excerpt(
            excerpt_after(
                normalized,
                [
                    r"盈利预测与估值",
                    r"盈利预测、估值与评级",
                    r"盈利预测与投资建议",
                    r"盈利预测",
                    r"投资建议",
                ],
                650,
            ),
            420,
        )
        risk = clean_excerpt(
            excerpt_after(normalized, [r"风险提示"], 420),
            260,
        )
        report_rows.append(
            {
                **report,
                "thesis_excerpt": thesis,
                "forecast_excerpt": forecast,
                "risk_excerpt": risk,
                "text_sha256_required": True,
            }
        )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in report_rows:
        grouped.setdefault(row["ticker"], []).append(row)
    ticker_rows: list[dict[str, Any]] = []
    for ticker, reports in grouped.items():
        reports.sort(key=lambda row: (row["report_date"], -row["sequence"]), reverse=True)
        latest = reports[0]
        ticker_rows.append(
            {
                "ticker": ticker,
                "company": latest["company"],
                "sector": latest["sector"],
                "tier": latest["tier"],
                "report_count_archived": len(reports),
                "reports": reports,
                **disposition_map[ticker],
            }
        )
    ticker_rows.sort(key=lambda row: (row["sector"], row["ticker"]))

    write_json(
        DATA_DIR / "core_broker_report_digests_20260711.json",
        {
            "schema_version": "astock.core_broker_report_digest.v1",
            "data_cutoff": "2026-07-11",
            "ticker_count": len(ticker_rows),
            "report_count": len(report_rows),
            "rows": ticker_rows,
        },
    )

    lines = [
        "# Core Broker Report Digests",
        "",
        f"- Priority tickers: {len(ticker_rows)}",
        f"- Original PDF texts reviewed: {len(report_rows)}",
        "",
    ]
    for ticker_row in ticker_rows:
        lines += [
            f"## {ticker_row['company']} ({ticker_row['ticker']})",
            "",
            f"- AStock disposition: `{ticker_row['disposition']}`",
            f"- Report timing versus preview: `{ticker_row['report_vs_preview']}`",
            f"- Monitor rule: {ticker_row['monitor']}",
            "",
        ]
        for report in ticker_row["reports"]:
            lines += [
                f"### {report['broker']} | {report['report_date']} | {report['title']}",
                "",
                f"- 2026E EPS / PE metadata: {report['eps_2026e']} / {report['pe_2026e']}",
                f"- Relation to preview: `{report['report_vs_preview']}`",
                f"- Thesis excerpt: {report['thesis_excerpt']}",
                f"- Forecast excerpt: {report['forecast_excerpt']}",
                f"- Risk excerpt: {report['risk_excerpt']}",
                f"- Source: `{report['local_pdf']}`",
                "",
            ]
    markdown = "\n".join(lines)
    write_text(DATA_DIR / "core_broker_report_digests_20260711.md", markdown)
    write_text(ANALYSIS_DIR / "core_broker_report_digests.md", markdown)
    print(
        json.dumps(
            {"ticker_count": len(ticker_rows), "report_count": len(report_rows)},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
