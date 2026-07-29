#!/usr/bin/env python3
"""Refresh financial and broker evidence for all 2026-07-15 candidates."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = CASE_DIR / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from refresh_candidate_evidence_20260715 import (  # noqa: E402
    collect_financials,
    collect_report,
    load_json,
    q1_summary,
    write_json,
    write_text,
)


REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
DATA_CUTOFF = "2026-07-15"


def main() -> None:
    candidates = load_json(DATA_DIR / "full_market_candidates_20260715.json")["rows"]
    codes = [row["ticker"] for row in candidates]
    financials = asyncio.run(collect_financials(codes))
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, candidate in enumerate(candidates, 1):
        ticker = candidate["ticker"]
        report, report_failures = collect_report(ticker, candidate["company"])
        failures.extend(report_failures)
        rows.append(
            {
                **candidate,
                **q1_summary(financials[ticker]),
                **report,
            }
        )
        if index % 10 == 0 or index == len(candidates):
            print(
                f"{index}/{len(candidates)} {ticker} "
                f"financial={rows[-1].get('q1_data_quality')} "
                f"report={rows[-1].get('report_status')}"
            )
    result = {
        "schema_version": "astock.full_market_valuation_evidence.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(rows),
        "financial_success_count": sum(
            row.get("q1_revenue_100mn") is not None for row in rows
        ),
        "report_metadata_count": sum(
            row.get("latest_report_date") is not None for row in rows
        ),
        "report_pdf_count": sum(bool(row.get("local_pdf")) for row in rows),
        "target_extract_count": sum(
            row.get("target_price") is not None for row in rows
        ),
        "failures": failures,
        "source_candidate_pool": "data/full_market_candidates_20260715.json",
        "rows": rows,
    }
    write_json(DATA_DIR / "full_market_valuation_evidence_20260715.json", result)
    lines = [
        "# Full-Market Valuation Evidence Through 2026-07-15",
        "",
        f"- Candidate rows: {result['row_count']}",
        f"- Q1 financial packets: {result['financial_success_count']}",
        f"- Report metadata: {result['report_metadata_count']}",
        f"- Broker PDFs: {result['report_pdf_count']}",
        f"- Extracted target fields: {result['target_extract_count']}",
        f"- Failures: {len(failures)}",
        "",
        "| Ticker | Company | Industry | Price | Q1 NP | H1 NP | Broker/date | EPS | Target | Disposition |",
        "|---|---|---|---:|---:|---:|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['sws_industry']} | "
            f"{row.get('current_price')} | {row.get('q1_parent_np_100mn')} | "
            f"{row.get('h1_parent_np_midpoint_100mn')} | "
            f"{row.get('latest_broker')}/{row.get('latest_report_date')} | "
            f"{row.get('latest_2026e_eps')} | {row.get('target_price')} | "
            f"{row.get('full_market_disposition')} |"
        )
    if failures:
        lines += ["", "## Failures", ""]
        lines.extend(
            f"- {failure['ticker']} {failure['stage']}: {failure['error']}"
            for failure in failures
        )
    write_text(DATA_DIR / "full_market_valuation_evidence_20260715.md", "\n".join(lines))
    print(
        json.dumps(
            {
                "rows": result["row_count"],
                "financials": result["financial_success_count"],
                "reports": result["report_metadata_count"],
                "pdfs": result["report_pdf_count"],
                "targets": result["target_extract_count"],
                "failures": len(failures),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
