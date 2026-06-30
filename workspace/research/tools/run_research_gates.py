#!/usr/bin/env python3
"""Run publication gates for an AStock research case.

This runner is intentionally stricter than a layout verifier. It checks the
workflow artifacts that prove a research report went through evidence intake,
review/repair cycles, model reproducibility, final sign-off, and case-local
verification before publication.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast


EXPECTED_REVIEW_CYCLES = (
    "R0_evidence",
    "R1_model",
    "R2_draft",
    "R3_render_compliance",
    "R4_final_ic",
)

CLOSED_REVIEW_STATUSES = {"closed", "verified", "resolved", "pass", "passed"}

REQUIRED_ROOT_ARTIFACTS = (
    "research_brief.md",
    "gate_manifest.md",
    "gate_manifest.json",
    "artifact_contract.md",
    "artifact_contract.json",
    "review_log.md",
    "final_signoff.md",
    "final_signoff.json",
    "research_workflow_eval.md",
    "research_workflow_eval.json",
)

REQUIRED_MD_JSON_PAIRS = (
    "gate_manifest",
    "artifact_contract",
    "final_signoff",
    "research_workflow_eval",
    "source_exhaustion_log",
    "data/source_registry",
    "data/claim_audit",
)

FINAL_SIGNOFF_KEYS = (
    "case_id",
    "report_type",
    "data_cutoff",
    "pdf_path",
    "page_count",
    "publishability_score",
    "verifier_results",
    "open_s_count",
    "open_a_count",
    "residual_risks",
    "signoff_status",
)

INDUSTRY_CHAIN_ARTIFACTS = (
    "analysis/template_brief.md",
    "analysis/full_chain_taxonomy.md",
    "analysis/core_vs_satellite_universe.md",
    "analysis/coverage_gap_matrix.md",
    "analysis/supply_chain_model.md",
    "analysis/company_fundamental_cards.md",
    "analysis/value_chain_economics.md",
    "analysis/chain_earnings_bridge.md",
    "analysis/competitive_landscape.md",
    "analysis/variant_perception.md",
    "data/supply_chain_relationships.json",
    "data/customer_chain_audit.json",
)


class GateRunner:
    def __init__(self, case_dir: Path) -> None:
        self.case_dir = case_dir.resolve()
        self.repo_root = Path(__file__).resolve().parents[3]
        self.passes: list[str] = []
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        message = f"{name}: {detail}" if detail else name
        if condition:
            self.passes.append(message)
        else:
            self.failures.append(message)

    def warn(self, name: str, detail: str = "") -> None:
        self.warnings.append(f"{name}: {detail}" if detail else name)

    def exists(self, rel: str) -> Path:
        path = self.case_dir / rel
        self.check(f"exists {rel}", path.exists())
        return path

    def run(self) -> int:
        self.check("case directory exists", self.case_dir.exists(), str(self.case_dir))
        if not self.case_dir.exists():
            return self.finish()

        for rel in REQUIRED_ROOT_ARTIFACTS:
            self.exists(rel)
        for stem in REQUIRED_MD_JSON_PAIRS:
            self.check(
                f"md/json pair present {stem}",
                (self.case_dir / f"{stem}.md").exists()
                and (self.case_dir / f"{stem}.json").exists(),
            )

        gate_manifest = self.load_json("gate_manifest.json")
        artifact_contract = self.load_json("artifact_contract.json")
        final_signoff = self.load_json("final_signoff.json")
        workflow_eval = self.load_json("research_workflow_eval.json")

        required_artifacts = set()
        required_artifacts.update(artifact_paths_from_payload(gate_manifest))
        required_artifacts.update(artifact_paths_from_payload(artifact_contract))
        for rel in sorted(required_artifacts):
            self.check(
                f"manifest artifact exists {rel}",
                resolve_artifact(self.case_dir, rel).exists(),
            )

        self.check_review_lifecycle(gate_manifest)
        self.check_source_governance()
        self.check_valuation_reproducibility()
        self.check_final_signoff(final_signoff)
        self.check_workflow_eval(workflow_eval)
        self.check_case_verifier()

        if case_requires_industry_chain(gate_manifest, self.case_text()):
            self.check_industry_chain_artifacts()
            self.check_industry_chain_verifier()
        else:
            self.warn("industry-chain verifier skipped", "case not marked as full-chain")

        return self.finish()

    def load_json(self, rel: str) -> Any:
        path = self.case_dir / rel
        if not path.exists():
            self.check(f"json parses {rel}", False, "missing")
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive CLI output
            self.check(f"json parses {rel}", False, str(exc))
            return {}
        self.check(f"json parses {rel}", True)
        return payload

    def case_text(self) -> str:
        return "\n".join(
            read_text(self.case_dir / rel)
            for rel in (
                "research_brief.md",
                "analysis/template_brief.md",
                "review_log.md",
            )
        )

    def check_review_lifecycle(self, gate_manifest: Any) -> None:
        expected_cycles = expected_review_cycles(gate_manifest)
        review_log = read_text(self.case_dir / "review_log.md")
        score = extract_publishability_score(review_log)
        self.check("publishability score present", score is not None)
        if score is not None:
            self.check("publishability score >= 90", score >= 90, str(score))

        open_s_count = 0
        open_unwaived_a_count = 0
        for cycle in expected_cycles:
            findings_path = self.case_dir / f"review_findings_{cycle}.json"
            self.check(f"review findings present {cycle}", findings_path.exists())
            if not findings_path.exists():
                continue
            payload = self.load_json(findings_path.name)
            for finding in extract_review_findings(payload):
                severity = review_severity(finding)
                status = review_status(finding)
                waived = review_waived(finding)
                if severity == "S" and status not in CLOSED_REVIEW_STATUSES:
                    open_s_count += 1
                if (
                    severity == "A"
                    and status not in CLOSED_REVIEW_STATUSES
                    and not waived
                ):
                    open_unwaived_a_count += 1

            if cycle != "R4_final_ic":
                self.check(
                    f"repair plan pair present {cycle}",
                    (self.case_dir / f"repair_plan_{cycle}.md").exists()
                    and (self.case_dir / f"repair_plan_{cycle}.json").exists(),
                )

        self.check("zero open S-Level findings", open_s_count == 0, str(open_s_count))
        self.check(
            "zero open unwaived A-Level findings",
            open_unwaived_a_count == 0,
            str(open_unwaived_a_count),
        )

    def check_source_governance(self) -> None:
        for rel in (
            "data/source_registry.json",
            "data/claim_audit.json",
            "source_exhaustion_log.json",
        ):
            self.load_json(rel)
        self.check("sources directory present", (self.case_dir / "sources").exists())

    def check_valuation_reproducibility(self) -> None:
        valuation_audit = read_text(self.case_dir / "analysis/valuation_audit.md")
        self.check(
            "valuation model reproducibility pass",
            "model reproducibility: pass" in normalize(valuation_audit),
        )

    def check_final_signoff(self, final_signoff: Any) -> None:
        if not isinstance(final_signoff, Mapping):
            self.check("final sign-off is object", False)
            return

        for key in FINAL_SIGNOFF_KEYS:
            self.check(
                f"final sign-off has {key}",
                key in final_signoff and final_signoff.get(key) not in (None, ""),
            )

        status = normalize(final_signoff.get("signoff_status") or final_signoff.get("status"))
        self.check(
            "final sign-off status pass",
            status in {"pass", "passed", "approved", "signed", "publishable"},
            status or "missing",
        )

        score = int_value(final_signoff.get("publishability_score"))
        self.check("final sign-off score >= 90", score is not None and score >= 90, str(score))
        self.check("final sign-off open S count zero", int_value(final_signoff.get("open_s_count")) == 0)
        self.check("final sign-off open A count zero", int_value(final_signoff.get("open_a_count")) == 0)

    def check_workflow_eval(self, workflow_eval: Any) -> None:
        if not isinstance(workflow_eval, Mapping):
            self.check("workflow eval is object", False)
            return
        quality = workflow_eval.get("quality")
        self.check("workflow eval has quality packet", isinstance(quality, Mapping))
        if not isinstance(quality, Mapping):
            return
        self.check("workflow eval publishable", quality.get("publishable") is True)
        self.check(
            "workflow eval zero blocking failures",
            int_value(quality.get("blocking_failure_count")) == 0,
        )
        score = int_value(quality.get("score"))
        self.check("workflow eval score >= 90", score is not None and score >= 90, str(score))

    def check_case_verifier(self) -> None:
        verifier = self.case_dir / "tools" / "verify_research_workspace.py"
        self.check("generic case verifier present", verifier.exists())
        if verifier.exists():
            completed = subprocess.run(
                [sys.executable, "tools/verify_research_workspace.py"],
                cwd=self.case_dir,
                text=True,
                capture_output=True,
                check=False,
            )
            detail = tail(completed.stdout + completed.stderr)
            self.check("generic case verifier pass", completed.returncode == 0, detail)

    def check_industry_chain_artifacts(self) -> None:
        for rel in INDUSTRY_CHAIN_ARTIFACTS:
            self.exists(rel)
        universe_files = sorted((self.case_dir / "data").glob("full_chain_universe_*.json"))
        self.check("full-chain universe json present", bool(universe_files))

    def check_industry_chain_verifier(self) -> None:
        verifier = (
            self.repo_root
            / "workspace"
            / "research"
            / "templates"
            / "industry_chain_verify_research_workspace.py"
        )
        self.check("industry-chain verifier present", verifier.exists())
        if verifier.exists():
            completed = subprocess.run(
                [sys.executable, str(verifier), str(self.case_dir)],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            detail = tail(completed.stdout + completed.stderr)
            self.check("industry-chain verifier pass", completed.returncode == 0, detail)

    def finish(self) -> int:
        for item in self.passes:
            print(f"PASS {item}")
        for item in self.warnings:
            print(f"WARN {item}")
        for item in self.failures:
            print(f"FAIL {item}")
        print(f"SUMMARY {len(self.passes)} PASS / {len(self.failures)} FAIL")
        print("RESULT PASS" if not self.failures else "RESULT FAIL")
        return 0 if not self.failures else 1


def expected_review_cycles(gate_manifest: Any) -> tuple[str, ...]:
    if isinstance(gate_manifest, Mapping):
        cycles = gate_manifest.get("review_cycles")
        if isinstance(cycles, Sequence) and not isinstance(cycles, (str, bytes, bytearray)):
            parsed = tuple(str(cycle) for cycle in cycles if str(cycle).strip())
            if parsed:
                return parsed
    return EXPECTED_REVIEW_CYCLES


def artifact_paths_from_payload(payload: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(payload, str):
        if looks_like_artifact_path(payload):
            paths.add(payload.strip())
        return paths
    if isinstance(payload, Mapping):
        for key, item in payload.items():
            key_text = normalize(key)
            if key_text in {
                "path",
                "file",
                "relpath",
                "relative_path",
                "artifact",
                "artifact_path",
                "output",
            } and isinstance(item, str):
                if looks_like_artifact_path(item):
                    paths.add(item.strip())
                continue
            paths.update(artifact_paths_from_payload(item))
        return paths
    if isinstance(payload, Sequence) and not isinstance(payload, (bytes, bytearray)):
        for item in payload:
            paths.update(artifact_paths_from_payload(item))
    return paths


def looks_like_artifact_path(value: str) -> bool:
    text = value.strip()
    if not text or text.startswith(("http://", "https://")):
        return False
    if any(token in text for token in ("\n", "\t", "{", "}")):
        return False
    suffix = Path(text).suffix.lower()
    return suffix in {".csv", ".json", ".md", ".pdf", ".png", ".tex", ".txt", ".xlsx"}


def resolve_artifact(case_dir: Path, rel: str) -> Path:
    path = Path(rel)
    if path.is_absolute():
        return path
    return case_dir / path


def case_requires_industry_chain(gate_manifest: Any, text_blob: str) -> bool:
    gate_text = ""
    if isinstance(gate_manifest, Mapping):
        gate_text = json.dumps(gate_manifest, ensure_ascii=False)
    haystack = normalize(f"{gate_text}\n{text_blob}")
    return any(
        token in haystack
        for token in (
            "industry-chain",
            "industry_chain",
            "full-chain",
            "full_chain",
            "supply-chain",
            "supply_chain",
            "coverage_pack",
            "coverage pack",
            "产业链",
            "全产业链",
        )
    )


def extract_review_findings(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [cast(Mapping[str, Any], item) for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("findings", "issues", "items", "review_findings"):
            value = payload.get(key)
            if isinstance(value, list):
                return [
                    cast(Mapping[str, Any], item)
                    for item in value
                    if isinstance(item, Mapping)
                ]
        for value in payload.values():
            if isinstance(value, list) and all(isinstance(item, Mapping) for item in value):
                return [cast(Mapping[str, Any], item) for item in value]
    return []


def review_severity(finding: Mapping[str, Any]) -> str:
    severity = normalize(
        finding.get("severity") or finding.get("level") or finding.get("priority")
    ).upper()
    if severity.startswith("S"):
        return "S"
    if severity.startswith("A"):
        return "A"
    return "B"


def review_status(finding: Mapping[str, Any]) -> str:
    return normalize(
        finding.get("status")
        or finding.get("lifecycle_status")
        or finding.get("state")
        or "open"
    )


def review_waived(finding: Mapping[str, Any]) -> bool:
    waiver_status = normalize(finding.get("waiver_status"))
    return (
        review_status(finding) == "waived"
        or waiver_status == "waived"
        or truthy(finding.get("waived"))
    )


def extract_publishability_score(review_log: str) -> int | None:
    patterns = (
        r"publishability\s+score\D+(\d{1,3})",
        r"publishability_score\D+(\d{1,3})",
    )
    for pattern in patterns:
        match = re.search(pattern, review_log, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return normalize(value) in {"1", "true", "yes", "y", "waived"}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def tail(text: str, lines: int = 20) -> str:
    cleaned = [line for line in text.splitlines() if line.strip()]
    return "\n".join(cleaned[-lines:])


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run_research_gates.py <case-dir>", file=sys.stderr)
        return 2
    return GateRunner(Path(argv[1])).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
