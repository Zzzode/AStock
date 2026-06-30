#!/usr/bin/env python3
"""Reusable industry-chain research workspace content verifier.

Copy this script into `workspace/research/<case>/tools/` or run it directly:

    python3 workspace/research/templates/industry_chain_verify_research_workspace.py workspace/research/<case>

This template checks content gates that generic case verifiers often miss:
full-chain universe, core/satellite classification, coverage gaps, value-chain
economics, competitive landscape, source exhaustion, valuation reproducibility,
variant perception, and publishability score.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


NODE_TYPES = {"listed", "overseas", "private", "demand_anchor", "low_purity", "unavailable"}
REQUIRED_UNIVERSE_FIELDS = {
    "node_type",
    "chain_block",
    "subsegment",
    "evidence_status",
    "source_count",
    "classification",
    "valuation_status",
    "next_verification_path",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("rows", "nodes", "universe", "full_chain_universe", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        for value in payload.values():
            if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                return value
    return []


def text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


class Verifier:
    def __init__(self, case_dir: Path) -> None:
        self.case_dir = case_dir
        self.failures: list[str] = []
        self.passes: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        message = f"{name}: {detail}" if detail else name
        if condition:
            self.passes.append(message)
        else:
            self.failures.append(message)

    def exists(self, rel: str) -> Path:
        path = self.case_dir / rel
        self.check(f"exists {rel}", path.exists())
        return path

    def run(self) -> int:
        if not self.case_dir.exists():
            print(f"FAIL case directory missing: {self.case_dir}")
            return 2

        self.exists("research_brief.md")
        self.exists("analysis/template_brief.md")
        self.exists("analysis/full_chain_taxonomy.md")
        self.exists("analysis/core_vs_satellite_universe.md")
        self.exists("analysis/coverage_gap_matrix.md")
        self.exists("analysis/competitive_landscape.md")
        self.exists("analysis/value_chain_economics.md")
        self.exists("analysis/supply_chain_model.md")
        self.exists("analysis/company_fundamental_cards.md")
        self.exists("analysis/chain_earnings_bridge.md")
        self.exists("analysis/variant_perception.md")
        self.exists("analysis/valuation_audit.md")
        self.exists("data/supply_chain_relationships.json")
        self.exists("data/customer_chain_audit.json")
        self.exists("data/source_registry.json")
        self.exists("data/claim_audit.json")
        self.exists("source_exhaustion_log.md")
        self.exists("source_exhaustion_log.json")
        self.exists("review_log.md")

        universe_files = sorted((self.case_dir / "data").glob("full_chain_universe_*.json"))
        self.check("full-chain universe json present", bool(universe_files))
        rows: list[dict[str, Any]] = []
        if universe_files:
            try:
                rows = extract_rows(load_json(universe_files[-1]))
            except Exception as exc:  # pragma: no cover - defensive verifier output
                self.failures.append(f"full-chain universe json parses: {exc}")
            self.check("full-chain universe rows present", bool(rows))

        if rows:
            missing_fields = [
                idx
                for idx, row in enumerate(rows, start=1)
                if REQUIRED_UNIVERSE_FIELDS - set(row.keys())
            ]
            invalid_node_types = [
                idx for idx, row in enumerate(rows, start=1) if str(row.get("node_type", "")) not in NODE_TYPES
            ]
            blocks = {str(row.get("chain_block", "")).strip() for row in rows if row.get("chain_block")}
            classifications = {str(row.get("classification", "")).strip() for row in rows}
            node_types = {str(row.get("node_type", "")).strip() for row in rows}
            brief = (text(self.case_dir / "research_brief.md") + "\n" + text(self.case_dir / "analysis/template_brief.md")).lower()
            min_blocks = 8 if "aidc" in brief or "ai data-center" in brief else 4
            self.check("universe required fields", not missing_fields, f"rows missing fields: {missing_fields[:10]}")
            self.check("universe node_type enum", not invalid_node_types, f"invalid rows: {invalid_node_types[:10]}")
            self.check("universe chain block count", len(blocks) >= min_blocks, f"{len(blocks)} blocks, required {min_blocks}")
            self.check("core valuation classification present", "core_valuation" in classifications)
            self.check("satellite or watch classification present", bool({"satellite_watch", "watchlist", "satellite"} & classifications))
            self.check("demand anchor nodes present", "demand_anchor" in node_types)

        coverage = text(self.case_dir / "analysis/coverage_gap_matrix.md").lower()
        self.check("coverage gap has next verification path", "next verification" in coverage or "next_verification_path" in coverage)
        self.check("coverage gap has valuation blocker", "valuation" in coverage and "block" in coverage)

        economics = text(self.case_dir / "analysis/value_chain_economics.md").lower()
        for keyword in ("asp", "margin", "capacity", "certification", "valuation"):
            self.check(f"value-chain economics has {keyword}", keyword in economics)

        competitive = text(self.case_dir / "analysis/competitive_landscape.md").lower()
        for keyword in ("global", "china", "localization", "substitution"):
            self.check(f"competitive landscape has {keyword}", keyword in competitive)

        consensus = text(self.case_dir / "data/consensus_analysis.md").lower()
        self.check("consensus labels source quality", "source_quality" in consensus or "source quality" in consensus)

        valuation_audit = text(self.case_dir / "analysis/valuation_audit.md")
        self.check("valuation model reproducibility pass", "Model Reproducibility: PASS" in valuation_audit)

        variant = text(self.case_dir / "analysis/variant_perception.md").lower()
        for keyword in ("consensus", "opposing", "falsification", "trigger"):
            self.check(f"variant perception has {keyword}", keyword in variant)

        review_log = text(self.case_dir / "review_log.md")
        score_match = re.search(r"publishability\s+score\D+(\d{1,3})", review_log, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None
        self.check("review log publishability score present", score is not None)
        if score is not None:
            self.check("publishability score pass threshold", score >= 90, str(score))

        for item in self.passes:
            print(f"PASS {item}")
        for item in self.failures:
            print(f"FAIL {item}")
        print(f"SUMMARY {len(self.passes)} PASS / {len(self.failures)} FAIL")
        return 1 if self.failures else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: industry_chain_verify_research_workspace.py <case-dir>", file=sys.stderr)
        return 2
    return Verifier(Path(argv[1])).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
