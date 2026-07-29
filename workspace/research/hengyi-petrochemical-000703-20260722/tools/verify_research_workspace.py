#!/usr/bin/env python3
"""Case-local publication verifier for the Hengyi Petrochemical report."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
passes: list[str] = []
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    message = f"{name}: {detail}" if detail else name
    (passes if condition else failures).append(message)


def text(rel: str) -> str:
    path = CASE / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def payload(rel: str) -> object:
    path = CASE / rel
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def page_count() -> int:
    pdf = CASE / "main.pdf"
    if not pdf.exists():
        return 0
    completed = subprocess.run(
        ["pdfinfo", str(pdf)], text=True, capture_output=True, check=False
    )
    match = re.search(r"^Pages:\s+(\d+)$", completed.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def main() -> int:
    gate = payload("gate_manifest.json")
    contract = payload("artifact_contract.json")
    registry = payload("data/source_registry.json")
    claims = payload("data/claim_audit.json")
    exhaustion = payload("source_exhaustion_log.json")
    broker = payload("data/broker_street_consensus_20260722.json")
    valuation = payload("data/current_valuation_model_20260722.json")
    rows = valuation.get("rows", []) if isinstance(valuation, dict) else []
    row = rows[0] if rows and isinstance(rows[0], dict) else {}
    scenario = row.get("scenario_inputs", {}) if isinstance(row, dict) else {}
    share_bridge = row.get("share_reconciliation", {}) if isinstance(row, dict) else {}

    check("01 research brief", (CASE / "research_brief.md").exists())
    check("02 gate manifest parses", isinstance(gate, dict) and bool(gate))
    check("03 artifact contract parses", isinstance(contract, dict) and bool(contract))
    check("04 source registry pair", (CASE / "data/source_registry.md").exists() and isinstance(registry, dict) and len(registry.get("sources", [])) >= 18)
    check("05 claim audit pair", (CASE / "data/claim_audit.md").exists() and isinstance(claims, dict) and len(claims.get("claims", [])) >= 18)
    check("06 source exhaustion pair", (CASE / "source_exhaustion_log.md").exists() and isinstance(exhaustion, dict) and bool(exhaustion))
    check("07 verified financials", "2026Q1" in text("data/verified_financials.md") and "经营现金流" in text("data/verified_financials.md"))
    check("08 verified market data", "15.06" in text("data/verified_market_data.md") and "13:52" in text("data/verified_market_data.md"))
    check("09 broker consensus pair", (CASE / "data/broker_street_consensus_20260722.md").exists() and isinstance(broker, dict) and len(broker.get("rows", [])) >= 1)
    check("10 official PDFs archived", len(list((CASE / "sources/official-20260722").glob("*.pdf"))) >= 12)
    check("11 original broker PDF archived", any((CASE / "sources/broker-reports/2026-07-22").glob("*.pdf")))
    check("12 industry evidence manifest", (CASE / "sources/industry-20260722/capture_manifest.md").exists())
    check("13 valuation structured row", len(rows) == 1 and row.get("ticker") == "000703.SZ")
    required = {"ticker", "company", "current_price", "price_date", "shares_100mn", "market_cap_100mn_cny", "revenue_2026e_100mn", "np_2026e_100mn", "eps_2026e", "method", "bear", "base", "bull", "market_implied_anchor", "fundamental_weight", "market_weight", "broker_weight", "final_target", "upside", "action", "evidence_quality"}
    check("14 valuation required fields", required.issubset(row.keys()))
    check("15 current price frozen", abs(float(row.get("current_price", 0)) - 15.06) < 1e-9 and "13:51:54" in str(row.get("price_date", "")))
    target = float(row.get("final_target", 0) or 0)
    upside = float(row.get("upside", 0) or 0)
    check("16 target and upside reproduce", abs(target - 15.7) < 1e-9 and abs(target / 15.06 - 1 - upside) < 0.0005)
    check("17 disclosed dilution shares", abs(float(row.get("shares_100mn", 0)) - 38.80694189) < 1e-6)
    check("18 employee plan bridge", share_bridge.get("approved_employee_plan_max_shares") == 150813800 and abs(float(share_bridge.get("approved_employee_plan_max_cash_proceeds_100mn_cny", 0)) - 18.7462) < 0.001)
    expected_values = {"bear": 10.5328, "base": 15.4611, "bull": 22.5152}
    check("19 scenario values reproduce", all(abs(float(row.get(key, 0)) - value) < 0.001 for key, value in expected_values.items()) and set(scenario) == {"bear", "base", "bull"})
    check("20 anchor weights sum", abs(sum(float(row.get(key, 0)) for key in ("fundamental_weight", "market_weight", "broker_weight")) - 1.0) < 1e-9)
    valuation_text = text("analysis/valuation_model.md")
    sections = ("Final Valuation Table", "Three-Tier Targets", "Relative / PEG / PSG Comparison", "Seasonality Calibration", "Next-Quarter Threshold", "Method and Assumption Bridge", "Market-Expectation Valuation Bridge", "Broker/Street Comparison", "Market-Implied Sentiment Anchor", "Growth Earnings Dependency", "Full-Chain Classification Dependency")
    check("21 valuation sections complete", all(section in valuation_text for section in sections))
    check("22 valuation reproducibility", "Model Reproducibility: PASS" in text("analysis/valuation_audit.md"))
    segment = text("analysis/segment_valuation_model.md").lower()
    check("23 segment model depth", all(term in segment for term in ("segment", "sotp", "revenue", "net profit", "multiple", "sensitivity", "validation trigger")))
    secondary = text("analysis/secondary_market_analysis.md").lower()
    check("24 secondary market depth", all(term in secondary for term in ("price", "volume", "turnover", "drawdown", "relative performance", "support", "resistance", "institutional", "northbound", "financing", "hot-money", "fund attitude", "trend swing")))
    check("25 risk framework", "风险矩阵" in text("analysis/risk_framework.md") and "监控阈值" in text("analysis/risk_framework.md"))
    house = text("analysis/house_view.md")
    check("26 house view frozen", "15.7 元" in house and "77.5" in house and "38.81" in house)
    reader_text = "\n".join(text(rel) for rel in ("main.tex", "main_current_text.txt", "analysis/house_view.md", "analysis/valuation_model.md"))
    banned = ("TODO", "TBD", "待补", "PLACEHOLDER", "16.1 元目标")
    check("27 no generic placeholders", not any(item in reader_text for item in banned))
    check("28 main tex present", (CASE / "main.tex").exists() and len(text("main.tex")) >= 1000)
    section_files = list((CASE / "sections").glob("*.tex")) if (CASE / "sections").exists() else []
    check("29 section depth", len(section_files) >= 10)
    tex_corpus = text("main.tex") + "\n" + "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in section_files)
    check("30 report source markers", "HY-OFF-2025AR" in tex_corpus and "HY-BRK-GUOXIN" in tex_corpus and "IND-PTA-202606" in tex_corpus)
    check("31 PDF present", (CASE / "main.pdf").exists() and (CASE / "main.pdf").stat().st_size >= 100_000 if (CASE / "main.pdf").exists() else False)
    pages = page_count()
    check("32 PDF page count", 40 <= pages <= 60, f"pages={pages}")
    current_text = text("main_current_text.txt")
    check("33 extracted text present", len(current_text) >= 40_000)
    check(
        "34 extracted report anchors",
        all(item in current_text for item in ("15.06", "15.7", "77.5"))
        and ("38.81" in current_text or "38.806" in current_text),
    )
    check(
        "35 extracted report conclusion",
        "中性" in current_text and "观察" in current_text and "研究优先级" in current_text,
    )
    review_cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("36 review lifecycle", all((CASE / f"review_findings_{cycle}.json").exists() for cycle in review_cycles))
    check("37 repair plans", all((CASE / f"repair_plan_{cycle}.json").exists() and (CASE / f"repair_plan_{cycle}.md").exists() for cycle in review_cycles[:-1]))
    signoff = payload("final_signoff.json")
    check("38 final signoff", isinstance(signoff, dict) and signoff.get("signoff_status") == "PASS" and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
    workflow = payload("research_workflow_eval.json")
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("39 workflow eval", isinstance(quality, dict) and quality.get("publishable") is True and quality.get("blocking_failure_count") == 0 and int(quality.get("score", 0)) >= 90)

    for item in passes:
        print(f"PASS {item}")
    for item in failures:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(passes)} PASS / {len(failures)} FAIL")
    return 0 if not failures and len(passes) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
