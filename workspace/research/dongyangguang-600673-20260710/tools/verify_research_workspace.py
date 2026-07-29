#!/usr/bin/env python3
"""Verify the refreshed Dongyangguang research case with 39 hard checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8", errors="ignore")


def pdf_pages() -> int:
    result = subprocess.run(
        ["pdfinfo", str(ROOT / "main.pdf")],
        text=True,
        capture_output=True,
        check=True,
    )
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else 0


def pdf_title() -> str:
    result = subprocess.run(
        ["pdfinfo", str(ROOT / "main.pdf")],
        text=True,
        capture_output=True,
        check=True,
    )
    match = re.search(r"^Title:\s+(.+)$", result.stdout, re.MULTILINE)
    return match.group(1).strip() if match else ""


def latex_build_clean() -> bool:
    xelatex = shutil.which("xelatex")
    if xelatex is None:
        fallback = Path("/Library/TeX/texbin/xelatex")
        xelatex = str(fallback) if fallback.exists() else None
    if xelatex is None:
        return False
    with tempfile.TemporaryDirectory(prefix="dyg-latex-verify-") as temp_dir:
        command = [
            xelatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={temp_dir}",
            "main.tex",
        ]
        for _ in range(2):
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                return False
        log_path = Path(temp_dir) / "main.log"
        if not log_path.exists():
            return False
        log_text = log_path.read_text(errors="ignore")
        return not any(
            token in log_text
            for token in (
                "Overfull",
                "Extra alignment tab",
                "Undefined control sequence",
                "Missing character",
                "LaTeX Error",
            )
        )


def pdf_out_of_bounds_count() -> int:
    rendered = ROOT / "rendered"
    rendered.mkdir(exist_ok=True)
    bbox = rendered / "bbox-layout.xml"
    subprocess.run(
        ["pdftotext", "-bbox-layout", str(ROOT / "main.pdf"), str(bbox)],
        check=True,
    )
    root = ET.parse(bbox).getroot()
    violations = 0
    for page in (node for node in root.iter() if node.tag.endswith("page")):
        width = float(page.attrib.get("width", 0))
        height = float(page.attrib.get("height", 0))
        for word in (node for node in page.iter() if node.tag.endswith("word")):
            attrs = word.attrib
            x_min = float(attrs.get("xMin", attrs.get("xmin", 0)))
            y_min = float(attrs.get("yMin", attrs.get("ymin", 0)))
            x_max = float(attrs.get("xMax", attrs.get("xmax", 0)))
            y_max = float(attrs.get("yMax", attrs.get("ymax", 0)))
            if (
                x_min < -0.5
                or y_min < -0.5
                or x_max > width + 0.5
                or y_max > height + 0.5
            ):
                violations += 1
    return violations


def source_paths_exist(source_registry: dict[str, Any]) -> bool:
    for row in source_registry["rows"]:
        source_path = str(row["path"])
        if source_path.startswith("http") or source_path.startswith("../"):
            continue
        path = ROOT / source_path
        if not path.exists():
            return False
        if path.suffix.lower() == ".pdf" and not path.read_bytes().startswith(b"%PDF"):
            return False
    return True


def review_closed() -> bool:
    cycles = (
        "R0_evidence",
        "R1_model",
        "R2_draft",
        "R3_render_compliance",
        "R4_final_ic",
    )
    for cycle in cycles:
        payload = load_json(f"review_findings_{cycle}.json")
        if payload.get("publishability_status") != "PASS":
            return False
        if payload.get("open_s_count") != 0 or payload.get("open_a_count") != 0:
            return False
        if any(
            finding.get("status") not in {"closed", "verified", "resolved", "pass"}
            for finding in payload.get("findings", [])
        ):
            return False
    signoff = load_json("final_signoff.json")
    return (
        signoff.get("signoff_status") == "PASS"
        and signoff.get("publishability_score", 0) >= 90
        and signoff.get("open_s_count") == 0
        and signoff.get("open_a_count") == 0
    )


def main() -> int:
    manifest = load_json("gate_manifest.json")
    contract = load_json("artifact_contract.json")
    source_registry = load_json("data/source_registry.json")
    claim_audit = load_json("data/claim_audit.json")
    valuation = load_json("data/current_valuation_model_20260713.json")
    dilution = load_json("data/transaction_dilution_model_20260713.json")
    contracts = load_json("data/compute_contract_bridge_20260713.json")
    growth = load_json("data/growth_driver_model.json")
    consensus = load_json("data/broker_street_consensus_20260713.json")
    workflow = load_json("research_workflow_eval.json")
    signoff = load_json("final_signoff.json")
    text = read_text("main_current_text.txt")
    compact = re.sub(r"\s+", "", text)
    row = valuation["rows"][0]

    required = set(manifest["required_artifacts"])
    required.update(item["artifact"] for item in contract["artifacts"])

    checks: list[tuple[str, Callable[[], bool]]] = [
        ("main.tex and main.pdf exist", lambda: (ROOT / "main.tex").is_file() and (ROOT / "main.pdf").is_file()),
        ("PDF page count matches sign-off", lambda: pdf_pages() == signoff["page_count"]),
        ("PDF title is updated", lambda: pdf_title() == "东阳光深度研究更新"),
        ("extracted PDF text exists", lambda: len(text) > 1000),
        ("required artifacts exist", lambda: all((ROOT / rel).exists() for rel in required)),
        ("manifest has five depth gates", lambda: len(manifest["depth_gates"]) == 5),
        ("artifact contract has field depth", lambda: all(item.get("required_fields") and item.get("minimum_depth") and item.get("blocking_conditions") for item in contract["artifacts"])),
        ("source registry paths and PDFs validate", lambda: len(source_registry["rows"]) >= 12 and source_paths_exist(source_registry)),
        ("claim audit covers material refresh claims", lambda: len(claim_audit["rows"]) >= 7 and all(row.get("formal_boundary") and row.get("model_impact") for row in claim_audit["rows"])),
        ("current price and date are refreshed", lambda: row["current_price"] == 38.99 and row["price_date"].startswith("2026-07-13")),
        ("market cap recalculates", lambda: abs(row["market_cap_100mn_cny"] - row["current_price"] * row["shares_100mn"]) < 0.02),
        ("latest legacy forecast denominator is used", lambda: row["np_2026e_100mn"] == 19.47 and row["eps_2026e"] == 0.647),
        ("three contract rows exist", lambda: len(contracts["contracts"]) == 3),
        ("contract total reconciles", lambda: contracts["total_low_100mn"] == 390.0 and contracts["total_high_100mn"] == 460.0),
        ("annualized contract midpoint reconciles", lambda: abs(contracts["annualized_gross_mid_100mn"] - 85.0) < 0.001),
        ("prior contract acceptance is recorded", lambda: all("accepted" in item["status"] for item in contracts["contracts"][:2])),
        ("C contract remains conditional", lambda: "pending" in contracts["contracts"][2]["status"]),
        ("purchase shares reconcile", lambda: abs(dilution["purchase_shares_100mn"] - 4.09054851) < 1e-8),
        ("post-purchase shares reconcile", lambda: abs(dilution["post_purchase_shares_100mn"] - (30.095551 + 4.09054851)) < 1e-8),
        ("base placement dilution is included", lambda: dilution["base_total_shares_100mn"] > dilution["post_purchase_shares_100mn"]),
        ("regulatory max dilution is disclosed", lambda: dilution["regulatory_max_total_shares_100mn"] > 44.4),
        ("official pro-forma EPS is preserved", lambda: dilution["official_2025_proforma_eps"] == 0.28),
        ("growth driver has institutional fields", lambda: len(growth["drivers"]) == 1 and all(growth["drivers"][0].get(field) for field in ("base_business", "growth_segment", "unit_order_asp_proxy", "recognized_revenue_ratio", "gross_margin", "current_price_implied_growth", "formal_boundary", "valuation_credit", "next_quarter_validation_threshold"))),
        ("scenario bands include downside and upside", lambda: row["bear"] < row["base"] < row["current_price"] < row["bull"]),
        ("scenario expected value is below spot", lambda: row["scenario_expected_value"] < row["current_price"]),
        ("fundamental anchor is below spot", lambda: row["fundamental_anchor"] < row["current_price"]),
        ("broker anchor is external and above spot", lambda: row["broker_anchor"] > row["current_price"]),
        ("valuation weights sum to one", lambda: abs(row["fundamental_weight"] + row["broker_weight"] + row["market_weight"] - 1.0) < 1e-9),
        ("final target arithmetic reconciles", lambda: abs(row["final_target"] - round(row["fundamental_anchor"] * row["fundamental_weight"] + row["broker_anchor"] * row["broker_weight"] + row["market_implied_anchor"] * row["market_weight"], 2)) < 0.001),
        ("final upside arithmetic reconciles", lambda: abs(row["upside"] - round(row["final_target"] / row["current_price"] - 1, 4)) < 0.0001),
        ("action is not an unsupported buy", lambda: "中性" in row["action"] and "不追高" in row["action"]),
        ("original broker PDF has positive weight", lambda: any(item["source_quality"] == "original_pdf" and item["valuation_weight"] > 0 for item in consensus["rows"])),
        ("weak broker sources are not in positive consensus packet", lambda: all(item["source_quality"] in {"original_pdf", "auditable_broker_repost"} for item in consensus["rows"])),
        ("reader-facing report contains current thesis", lambda: all(token in compact for token in ("390–460亿元", "前序合同已交付", "购买资产新增4.09亿股", "最终目标", "中性／持有／事件驱动观察", "旧43元目标"))),
        ("reader-facing placeholders absent", lambda: not any(token in text for token in ("TODO", "TBD", "未完成", "<Report"))),
        ("valuation audit passes", lambda: "Model Reproducibility: PASS" in read_text("analysis/valuation_audit.md")),
        ("ephemeral two-pass XeLaTeX build is clean", latex_build_clean),
        ("PDF text stays inside bounds", lambda: pdf_out_of_bounds_count() == 0),
        ("review cycles and final sign-off are closed", review_closed),
    ]

    failures: list[str] = []
    for name, predicate in checks:
        try:
            passed = bool(predicate())
        except Exception as exc:
            passed = False
            name = f"{name}: {exc}"
        print(("PASS " if passed else "FAIL ") + name)
        if not passed:
            failures.append(name)
    print(f"SUMMARY {len(checks) - len(failures)} PASS / {len(failures)} FAIL")
    print("RESULT PASS" if not failures else "RESULT FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
