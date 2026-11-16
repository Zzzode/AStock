#!/usr/bin/env python3
"""Mechanical checks for the R0 evidence-repair handoff; not an IC approval."""

from __future__ import annotations

import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]


def _load(relative_path: str):
    return json.loads((CASE_DIR / relative_path).read_text(encoding="utf-8"))


def _workspace_path(path: str) -> Path:
    return (REPO_ROOT / path).resolve()


def main() -> int:
    failures: list[str] = []
    registry = _load("data/source_registry.json")
    source_ids = {row["source_id"] for row in registry}
    if len(source_ids) != len(registry):
        failures.append("duplicate source registry ID")

    for claim in _load("data/claim_audit.json"):
        missing = set(claim.get("source_ids", [])).difference(source_ids)
        if missing:
            failures.append(f"claim {claim['claim_id']} has unknown sources {sorted(missing)}")
    for item in _load("source_exhaustion_log.json")["items"]:
        missing = set(item.get("sources_checked", [])).difference(source_ids)
        if missing:
            failures.append(f"exhaustion item {item['id']} has unknown sources {sorted(missing)}")

    public_source = next(row for row in registry if row["source_id"] == "P01")
    frozen_input = json.loads(_workspace_path(public_source["local_path"]).read_text(encoding="utf-8"))
    expected_basis = "forward_adjusted_or_unknown"
    if frozen_input.get("price_basis") != expected_basis:
        failures.append("P01 frozen input has an unexpected adjustment basis")
    public_result = _load("data/etf_public_price_falsification_20260814.json")
    if public_result.get("source", {}).get("source_declared_basis") != expected_basis:
        failures.append("ETF derived result does not disclose the source-declared basis")
    if public_result.get("protocol", {}).get("status") != "exploratory_post_source_diagnostic_not_predeclared_not_frozen":
        failures.append("ETF diagnostic protocol is not classified as exploratory post-source")
    if public_result.get("formal_decision_eligible") is not False or public_result.get("portfolio_q") != 0:
        failures.append("ETF diagnostic is unexpectedly decision eligible")

    sample_manifest = _load("sources/probe-exchange-data-r0-20260814/manifest.json")
    sample_files = sample_manifest.get("files", [])
    if len(sample_files) != 12:
        failures.append(f"expected 12 retained futures raw samples, found {len(sample_files)}")
    by_path = {str(_workspace_path(row["path"]).relative_to(CASE_DIR)): row for row in sample_files}
    futures_result = _load("data/futures_exchange_data_access_probe_20260814.json")
    provenance = futures_result.get("historical_provenance", {})
    if provenance.get("retrieval_basis") != "retrospective_source_access_sample":
        failures.append("futures probe lacks retrospective retrieval_basis")
    if not provenance.get("source_archive_retrieved_at"):
        failures.append("futures probe lacks source archive retrieval time")
    for exchange in ("shfe", "czce"):
        rows = futures_result.get(exchange, [])
        if len(rows) != 6:
            failures.append(f"expected six {exchange} rows in futures probe")
        for row in rows:
            if row.get("retrieval_basis") != "retrospective_source_access_sample" or not row.get("retrieved_at"):
                failures.append(f"{exchange} probe row lacks retrospective sample provenance")
            entry = by_path.get(row.get("archive_path", ""))
            if entry is None:
                failures.append(f"{exchange} probe row lacks a manifest-bound archive path")
            elif entry.get("sha256") != row.get("raw_sha256"):
                failures.append(f"{exchange} probe hash differs from source manifest")

    failed_probe_manifest = _load("sources/probe-contract-rule-r0-20260814/manifest.json")
    attempts = failed_probe_manifest.get("attempts", [])
    if {attempt.get("probe_id") for attempt in attempts} != {"PX01", "PX02", "PX03"}:
        failures.append("failed-probe manifest does not contain PX01/PX02/PX03")
    if any(attempt.get("response_body_retained") is not False for attempt in attempts):
        failures.append("failed-probe manifest claims a retained response body")

    vendor_manifest = _load("sources/vendor-data-r0-20260814/manifest.json")
    vendor_required = {"path", "local_path", "publisher", "title", "url", "document_effective_date", "retrieval_date", "use_boundary", "bytes", "sha256"}
    for entry in vendor_manifest.get("files", []):
        missing = vendor_required.difference(entry)
        if missing:
            failures.append(f"vendor row lacks fields {sorted(missing)}")

    universe = _load("data/t2_candidate_universe_20260814.json")
    for candidate in universe.get("candidates", []):
        if candidate.get("current_q") != 0 or candidate.get("current_decision") != "not admitted":
            failures.append(f"candidate {candidate.get('id')} violates q=0/not-admitted boundary")

    required = [
        "review_findings_R0_evidence.json",
        "repair_plan_R0_evidence.json",
        "repair_plan_R0_evidence.md",
        "review_log.md",
    ]
    for relative_path in required:
        if not (CASE_DIR / relative_path).is_file():
            failures.append(f"missing required R0 lifecycle artifact {relative_path}")

    if failures:
        print("R0 REPAIR CHECK: FAIL")
        print("\n".join(failures))
        return 1
    print("R0 REPAIR CHECK: PASS (governance repairs only; strategy remains q=0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
