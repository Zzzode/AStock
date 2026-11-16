#!/usr/bin/env python3
"""Case-local evidence and publication verifier for the 2026-08-11 refresh.

The verifier deliberately distinguishes a sound source package from a publishable
PDF.  It never treats a missing MacTeX runtime, PDF, or rendered-page review as
a pass merely because the source files are present.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]
PASS: list[str] = []
FAIL: list[str] = []


def check(number: int, name: str, condition: bool, detail: str = "") -> None:
    line = f"{number:02d} {name}" + (f": {detail}" if detail else "")
    (PASS if condition else FAIL).append(line)


def load_json(relative_path: str) -> Any:
    path = CASE / relative_path
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_text(relative_path: str) -> str:
    path = CASE / relative_path
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def h1_actual_tickers(financials: dict[str, Any]) -> set[str]:
    actual: set[str] = set()
    for record in financials.get("records", []):
        if not isinstance(record, dict):
            continue
        ticker = str(record.get("ticker", ""))
        for period in record.get("financials", []):
            if not isinstance(period, dict):
                continue
            if (
                period.get("reporting_period") == "2026H1"
                and period.get("actuality") == "reported"
            ):
                actual.add(ticker)
    return actual


def review_payload(name: str) -> dict[str, Any]:
    value = load_json(f"review_findings_{name}.json")
    return value if is_mapping(value) else {}


def main() -> int:
    gate = load_json("gate_manifest.json")
    contract = load_json("artifact_contract.json")
    market = load_json("data/raw_market_data_20260811.json")
    financials = load_json("data/raw_financials_20260811.json")
    broker = load_json("data/broker_street_consensus_20260811.json")
    registry = load_json("data/source_registry.json")
    claims = load_json("data/claim_audit.json")
    valuation = load_json("data/current_valuation_model_20260811.json")
    historical = load_json("data/high_upside_recheck_20260811.json")
    r0 = review_payload("R0_evidence")
    r1 = review_payload("R1_model")
    r2 = review_payload("R2_draft")
    r3 = review_payload("R3_render_compliance")
    r4 = review_payload("R4_final_ic")

    market = market if is_mapping(market) else {}
    financials = financials if is_mapping(financials) else {}
    broker = broker if is_mapping(broker) else {}
    registry = registry if is_mapping(registry) else {}
    claims = claims if is_mapping(claims) else {}
    valuation = valuation if is_mapping(valuation) else {}
    historical = historical if is_mapping(historical) else {}
    valuation_rows = [row for row in valuation.get("rows", []) if isinstance(row, dict)]
    broker_tickers = [row for row in broker.get("tickers", []) if isinstance(row, dict)]
    historical_rows = [row for row in historical.get("rows", []) if isinstance(row, dict)]
    section_files = list((CASE / "sections").glob("*.tex"))
    required_fields = {
        "ticker",
        "company",
        "current_price",
        "price_date",
        "shares_100mn",
        "market_cap_100mn_cny",
        "revenue_2026e_100mn",
        "np_2026e_100mn",
        "eps_2026e",
        "method",
        "bear",
        "base",
        "bull",
        "market_implied_anchor",
        "fundamental_weight",
        "market_weight",
        "broker_weight",
        "final_target",
        "upside",
        "action",
        "evidence_quality",
    }
    valuation_text = read_text("analysis/valuation_model.md")
    all_report_text = "\n".join(
        [read_text("main.tex"), read_text("main_current_text.txt"), valuation_text]
    )
    source_ids = {
        str(source.get("source_id"))
        for source in registry.get("sources", [])
        if isinstance(source, dict)
    }
    claim_ids = {
        str(claim.get("claim_id"))
        for claim in claims.get("claims", [])
        if isinstance(claim, dict)
    }

    check(1, "research brief exists", (CASE / "research_brief.md").is_file())
    check(2, "gate manifest parses", is_mapping(gate) and bool(gate))
    check(3, "artifact contract parses", is_mapping(contract) and bool(contract))
    check(4, "LaTeX source exists", (CASE / "main.tex").is_file())
    check(5, "all report sections exist", len(section_files) == 9)
    reading_copy = read_text("main_current_text.txt")
    check(6, "source-text reading copy exists", "source-text reading copy" in reading_copy and "not text extracted from a PDF" in reading_copy)
    check(7, "raw market packet parses", bool(market))
    check(8, "raw financial packet parses", bool(financials))
    check(9, "broker packet parses", bool(broker))
    check(10, "source registry parses", len(source_ids) >= 18)
    check(11, "claim audit parses", len(claim_ids) >= 20)
    check(12, "13-name market universe reconciles", market.get("row_count") == 13 and len(market.get("universe", [])) == 13)
    check(13, "completed-session close boundary", market.get("session_context", {}).get("last_completed_session") == "2026-08-10")
    check(14, "market source archives exist", (CASE / "sources/market-20260811").is_dir() and len(list((CASE / "sources/market-20260811").iterdir())) >= 25)
    check(15, "market quality explicitly warns on pre-open", any("pre-open" in str(item).lower() for item in market.get("warnings", [])))
    check(16, "financial universe reconciles", financials.get("universe_count") == 13 and len(financials.get("records", [])) == 13)
    check(17, "official filing archive exists", len(list((CASE / "sources/official-20260811").glob("*.pdf"))) >= 35)
    check(18, "actual H1 limited to reported names", h1_actual_tickers(financials) == {"000703", "301308"})
    check(19, "financial packet labels preview limits", any("preliminary" in str(item).lower() for item in financials.get("warnings", [])))
    check(20, "13-name broker coverage reconciles", len(broker_tickers) == 13 and {str(row.get("ticker")) for row in broker_tickers} == set(market.get("universe", [])))
    check(21, "broker PDF archive exists", len(list((CASE / "sources/broker-reports/2026-08-11").glob("*.pdf"))) >= 11)
    re_scoped = [
        report
        for ticker in broker_tickers
        for report in ticker.get("reports", [])
        if isinstance(report, dict) and report.get("source_quality") == "re_scoped_original_unverified"
    ]
    check(22, "re-scoped broker provenance is explicitly downgraded", len(re_scoped) == 2 and all(report.get("valuation_weight") == 0.0 for report in re_scoped))
    check(23, "13 current valuation dispositions", len(valuation_rows) == 13 and {str(row.get("ticker")) for row in valuation_rows} == set(market.get("universe", [])))
    check(24, "no-target valuation fields are complete", all(required_fields.issubset(row) for row in valuation_rows))
    check(25, "no AStock house target is issued", valuation.get("formal_house_target_status") == "none_published" and all(row.get("final_target") == "not_published" and row.get("upside") == "not_published" for row in valuation_rows))
    check(26, "house-target blend weights are zero", all(all(row.get(key) == 0.0 for key in ("fundamental_weight", "market_weight", "broker_weight")) for row in valuation_rows))
    check(27, "claim audit prohibits pre-open close use", "C01" in claim_ids and "C20" in claim_ids and "pre-open" in str(next((claim for claim in claims.get("claims", []) if isinstance(claim, dict) and claim.get("claim_id") == "C01"), {})).lower())
    check(28, "historical scenarios remain non-current", len(historical_rows) == 9 and all(row.get("current_status") in {"watchlist_only", "zero_weight_sensitivity"} for row in historical_rows))
    required_sections = (
        "Final Valuation Table",
        "Three-Tier Targets",
        "Relative / PEG / PSG Comparison",
        "Seasonality Calibration",
        "Next-Quarter Threshold",
        "Method and Assumption Bridge",
        "Market-Expectation Valuation Bridge",
        "Broker/Street Comparison",
        "Market-Implied Sentiment Anchor",
        "Growth Earnings Dependency",
        "Full-Chain Classification Dependency",
    )
    check(29, "valuation narrative sections are complete", all(item in valuation_text for item in required_sections))
    check(30, "valuation audit preserves reproducibility boundary", "Model Reproducibility: PASS" in read_text("analysis/valuation_audit.md"))
    check(31, "risk framework exists", "Invalidation" in read_text("analysis/risk_framework.md"))
    check(32, "R0 and R1 review artifacts parse", bool(r0.get("findings")) and bool(r1.get("findings")))
    check(33, "R2 review closed its S/A findings", r2.get("open_s_count") == 0 and r2.get("open_a_count") == 0)
    check(34, "R3 review artifact exists", bool(r3.get("findings")))
    check(35, "R4 review artifact exists", bool(r4.get("findings")))
    xelatex = shutil.which("xelatex") or ("/Library/TeX/texbin/xelatex" if Path("/Library/TeX/texbin/xelatex").exists() else "")
    check(36, "required MacTeX XeLaTeX is available", bool(xelatex), "not available in this runtime" if not xelatex else xelatex)
    pdf = CASE / "main.pdf"
    check(37, "PDF deliverable exists", pdf.is_file() and pdf.stat().st_size > 0, "not generated" if not pdf.exists() else "empty PDF")
    rendered = CASE / "rendered"
    check(38, "rendered-page review material exists", rendered.is_dir() and bool(list(rendered.glob("page-*.png"))), "no rendered pages" if not rendered.exists() else "no page PNGs")
    check(39, "reader-facing source discloses the render limitation", "source-text reading copy" in all_report_text and "not text extracted from a PDF" in all_report_text)

    for item in PASS:
        print(f"PASS {item}")
    for item in FAIL:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(PASS)} PASS / {len(FAIL)} FAIL")
    return 0 if len(PASS) == 39 and not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
