"""Deterministic quality checks for system evolution workflows."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

DEGRADED_QUALITY_TIERS = {
    "cached",
    "degraded",
    "delayed",
    "partial",
    "snapshot",
    "snapshot_degraded",
    "unavailable",
}

DEFAULT_REPORT_CHECKS: dict[str, tuple[str, ...]] = {
    "evidence": ("evidence", "source", "provenance", "data"),
    "risk": ("risk", "downside", "drawdown"),
    "contrarian": ("contrarian", "bear case", "counterargument"),
    "monitoring_trigger": ("trigger", "monitor", "watch"),
    "invalidation": ("invalidation", "invalidate", "fails if"),
    "data_quality": ("data quality", "quality_tier", "degraded"),
    "source_exhaustion": ("source exhaustion", "source_exhaustion", "exhaustion log"),
    "full_chain_coverage": ("full-chain", "full_chain_universe", "coverage gap"),
    "valuation_reproducibility": (
        "model reproducibility",
        "valuation audit",
        "valuation_reproducibility",
    ),
    "review_lifecycle": ("review findings", "repair plan", "review lifecycle"),
    "final_signoff": ("final sign-off", "final_signoff", "publishability score"),
}

CASE_ROOT_ARTIFACTS = (
    "research_brief.md",
    "gate_manifest.json",
    "artifact_contract.json",
    "review_log.md",
    "final_signoff.json",
)

CASE_MD_JSON_PAIRS = (
    "gate_manifest",
    "artifact_contract",
    "final_signoff",
    "source_exhaustion_log",
    "data/source_registry",
    "data/claim_audit",
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

CLOSED_REVIEW_STATUSES = {"closed", "verified", "resolved", "pass", "passed"}

DEFAULT_FORBIDDEN_SKILL_TERMS = (
    "place order",
    "submit order",
    "execute trade",
    "route order",
    "broker login",
    "brokerage password",
)


@dataclass(frozen=True)
class SkillEvalCase:
    """One deterministic skill-boundary evaluation case."""

    name: str
    response: str
    prompt: str = ""
    required_terms: tuple[str, ...] = ()
    forbidden_terms: tuple[str, ...] = DEFAULT_FORBIDDEN_SKILL_TERMS
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SkillEvalCase":
        return cls(
            name=str(data.get("name", "unnamed_case")),
            prompt=str(data.get("prompt", "")),
            response=str(data.get("response", "")),
            required_terms=_tuple_from_value(data.get("required_terms")),
            forbidden_terms=(
                _tuple_from_value(data.get("forbidden_terms"))
                or DEFAULT_FORBIDDEN_SKILL_TERMS
            ),
            metadata=_json_ready_mapping(
                cast(Mapping[str, Any], data.get("metadata", {}))
                if isinstance(data.get("metadata"), Mapping)
                else {}
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "response": self.response,
            "required_terms": list(self.required_terms),
            "forbidden_terms": list(self.forbidden_terms),
            "metadata": dict(self.metadata),
        }


def evaluate_source_health(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate source health from provenance-like records."""

    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        source = _text(record.get("source"), "unknown")
        grouped.setdefault(source, []).append(record)

    summaries = [
        _source_summary(source, items) for source, items in sorted(grouped.items())
    ]
    failing = sum(1 for item in summaries if item["status"] == "failing")
    degraded = sum(1 for item in summaries if item["status"] == "degraded")
    overall_status = "good"
    if failing:
        overall_status = "failing"
    elif degraded:
        overall_status = "degraded"

    return {
        "schema_version": "quality.source_health.v1",
        "record_count": len(records),
        "source_count": len(summaries),
        "overall_status": overall_status,
        "sources": summaries,
    }


def check_prompt_drift(
    file_pairs: Sequence[Mapping[str, Any]],
    *,
    root_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compare prompt file pairs and report hash drift or missing files."""

    root = Path(root_path) if root_path is not None else None
    results: list[dict[str, Any]] = []
    for pair in file_pairs:
        name = _text(pair.get("name"), "prompt_pair")
        left = _resolve_path(pair.get("left"), root)
        right = _resolve_path(pair.get("right"), root)
        left_exists = left.exists()
        right_exists = right.exists()
        left_hash = _sha256_file(left) if left_exists else None
        right_hash = _sha256_file(right) if right_exists else None
        identical = bool(left_exists and right_exists and left_hash == right_hash)
        results.append(
            {
                "name": name,
                "left": str(left),
                "right": str(right),
                "left_exists": left_exists,
                "right_exists": right_exists,
                "left_sha256": left_hash,
                "right_sha256": right_hash,
                "identical": identical,
                "status": "ok" if identical else "drift",
            }
        )

    drift_count = sum(1 for item in results if item["status"] != "ok")
    return {
        "schema_version": "quality.prompt_drift.v1",
        "pair_count": len(results),
        "drift_count": drift_count,
        "status": "ok" if drift_count == 0 else "drift",
        "pairs": results,
    }


def evaluate_report_quality(
    report_text: str,
    *,
    checks: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a report includes required research-quality elements."""

    check_terms = checks or DEFAULT_REPORT_CHECKS
    normalized = _normalize(report_text)
    results: list[dict[str, Any]] = []
    passed_count = 0
    for name, terms in check_terms.items():
        hits = [term for term in terms if _normalize(term) in normalized]
        passed = bool(hits)
        if passed:
            passed_count += 1
        results.append(
            {
                "name": name,
                "passed": passed,
                "hits": hits,
                "expected_terms": list(terms),
            }
        )

    total = len(results)
    score = round(passed_count / total * 100, 2) if total else 100.0
    return {
        "schema_version": "quality.report_quality.v1",
        "score": score,
        "passed_count": passed_count,
        "check_count": total,
        "status": _score_status(score),
        "checks": results,
    }


def evaluate_research_case_quality(case_dir: str | Path) -> dict[str, Any]:
    """Evaluate artifact-level quality gates for a research case directory."""

    root = Path(case_dir)
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str = "", severity: str = "A") -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "severity": severity,
                "detail": detail,
            }
        )

    add("case directory exists", root.exists(), str(root), "S")
    if not root.exists():
        return _research_case_result(root, checks, requires_industry_chain=False)

    for rel in CASE_ROOT_ARTIFACTS:
        add(f"exists {rel}", (root / rel).exists(), rel, "S")

    for stem in CASE_MD_JSON_PAIRS:
        add(
            f"md/json pair present: {stem}",
            (root / f"{stem}.md").exists() and (root / f"{stem}.json").exists(),
            stem,
            "A",
        )

    gate_manifest, gate_error = _load_json_document(root / "gate_manifest.json")
    artifact_contract, contract_error = _load_json_document(
        root / "artifact_contract.json"
    )
    final_signoff, signoff_error = _load_json_document(root / "final_signoff.json")
    add("gate manifest json parses", gate_error is None, gate_error or "", "S")
    add("artifact contract json parses", contract_error is None, contract_error or "", "S")
    add("final sign-off json parses", signoff_error is None, signoff_error or "", "S")

    required_artifacts = set()
    required_artifacts.update(_artifact_paths_from_payload(gate_manifest))
    required_artifacts.update(_artifact_paths_from_payload(artifact_contract))
    for rel in sorted(required_artifacts):
        add(f"required artifact exists: {rel}", (root / rel).exists(), rel, "S")

    requires_industry_chain = _case_requires_industry_chain(
        gate_manifest,
        "\n".join(
            (
                _read_text(root / "research_brief.md"),
                _read_text(root / "analysis" / "template_brief.md"),
            )
        ),
    )
    if requires_industry_chain:
        for rel in INDUSTRY_CHAIN_ARTIFACTS:
            add(f"industry-chain artifact exists: {rel}", (root / rel).exists(), rel, "S")
        universe_files = sorted((root / "data").glob("full_chain_universe_*.json"))
        add(
            "industry-chain full-chain universe json present",
            bool(universe_files),
            "data/full_chain_universe_<YYYYMMDD>.json",
            "S",
        )

    review_findings = sorted(root.glob("review_findings_*.json"))
    add("review findings present", bool(review_findings), "review_findings_*.json", "S")
    open_s_count = 0
    open_unwaived_a_count = 0
    parse_failures = 0
    for findings_path in review_findings:
        payload, error = _load_json_document(findings_path)
        add(f"review findings parse: {findings_path.name}", error is None, error or "", "S")
        if error:
            parse_failures += 1
            continue
        for finding in _extract_review_findings(payload):
            severity = _review_severity(finding)
            status = _review_status(finding)
            waived = _review_waived(finding)
            if severity == "S" and status not in CLOSED_REVIEW_STATUSES:
                open_s_count += 1
            if (
                severity == "A"
                and status not in CLOSED_REVIEW_STATUSES
                and not waived
            ):
                open_unwaived_a_count += 1

        cycle = findings_path.stem.removeprefix("review_findings_")
        if cycle != "R4_final_ic":
            add(
                f"repair plan pair present: {cycle}",
                (root / f"repair_plan_{cycle}.md").exists()
                and (root / f"repair_plan_{cycle}.json").exists(),
                cycle,
                "A",
            )

    add("no open S-Level findings", open_s_count == 0, str(open_s_count), "S")
    add(
        "no open unwaived A-Level findings",
        open_unwaived_a_count == 0,
        str(open_unwaived_a_count),
        "A",
    )

    review_log = _read_text(root / "review_log.md")
    publishability_score = _extract_publishability_score(review_log)
    add(
        "publishability score present",
        publishability_score is not None,
        "review_log.md",
        "S",
    )
    if publishability_score is not None:
        add(
            "publishability score >= 90",
            publishability_score >= 90,
            str(publishability_score),
            "S",
        )

    valuation_audit = _read_text(root / "analysis" / "valuation_audit.md")
    add(
        "valuation model reproducibility pass",
        "model reproducibility: pass" in _normalize(valuation_audit),
        "analysis/valuation_audit.md",
        "S",
    )

    signoff_status = ""
    if isinstance(final_signoff, Mapping):
        signoff_status = _normalize(
            final_signoff.get("signoff_status") or final_signoff.get("status")
        )
    add(
        "final sign-off status pass",
        signoff_status in {"pass", "passed", "approved", "signed", "publishable"},
        signoff_status or "missing",
        "S",
    )

    result = _research_case_result(root, checks, requires_industry_chain)
    result["review_summary"] = {
        "finding_file_count": len(review_findings),
        "parse_failure_count": parse_failures,
        "open_s_count": open_s_count,
        "open_unwaived_a_count": open_unwaived_a_count,
        "publishability_score": publishability_score,
    }
    return result


def evaluate_skill_response_cases(
    cases: Sequence[Mapping[str, Any] | SkillEvalCase],
) -> dict[str, Any]:
    """Run deterministic skill-boundary checks over response cases."""

    parsed_cases = [
        case if isinstance(case, SkillEvalCase) else SkillEvalCase.from_dict(case)
        for case in cases
    ]
    results = [_evaluate_skill_case(case) for case in parsed_cases]
    passed_count = sum(1 for result in results if result["passed"])
    total = len(results)
    score = round(passed_count / total * 100, 2) if total else 100.0
    return {
        "schema_version": "quality.skill_eval.v1",
        "score": score,
        "passed_count": passed_count,
        "case_count": total,
        "status": _score_status(score),
        "cases": results,
    }


def _research_case_result(
    root: Path,
    checks: Sequence[Mapping[str, Any]],
    requires_industry_chain: bool,
) -> dict[str, Any]:
    passed_count = sum(1 for check in checks if bool(check.get("passed")))
    total = len(checks)
    score = round(passed_count / total * 100, 2) if total else 100.0
    blocking_failures = [
        check
        for check in checks
        if not bool(check.get("passed")) and str(check.get("severity")) in {"S", "A"}
    ]
    publishable = not blocking_failures and score >= 90
    status = "excellent" if publishable else _score_status(score)
    if blocking_failures and status == "excellent":
        status = "pass"
    return {
        "schema_version": "quality.research_case.v1",
        "case_dir": str(root),
        "score": score,
        "passed_count": passed_count,
        "check_count": total,
        "blocking_failure_count": len(blocking_failures),
        "requires_industry_chain": requires_industry_chain,
        "publishable": publishable,
        "status": status,
        "checks": list(checks),
        "blocking_failures": blocking_failures,
    }


def _load_json_document(path: Path) -> tuple[Any, str | None]:
    if not path.exists():
        return {}, f"missing: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        return {}, f"{path}: {exc}"


def _artifact_paths_from_payload(payload: Any) -> set[str]:
    paths: set[str] = set()
    paths.update(_artifact_paths_from_value(payload))
    return paths


def _artifact_paths_from_value(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, str):
        if _looks_like_artifact_path(value):
            paths.add(value.strip())
        return paths
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = _normalize(key)
            if key_text in {
                "path",
                "file",
                "relpath",
                "relative_path",
                "artifact",
                "artifact_path",
                "output",
            } and isinstance(item, str):
                if _looks_like_artifact_path(item):
                    paths.add(item.strip())
                continue
            paths.update(_artifact_paths_from_value(item))
        return paths
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            paths.update(_artifact_paths_from_value(item))
    return paths


def _looks_like_artifact_path(value: str) -> bool:
    text = value.strip()
    if not text or text.startswith(("http://", "https://")):
        return False
    if any(token in text for token in ("\n", "\t", "{", "}")):
        return False
    suffix = Path(text).suffix.lower()
    artifact_suffixes = {
        ".csv",
        ".json",
        ".md",
        ".pdf",
        ".png",
        ".tex",
        ".txt",
        ".xlsx",
    }
    return suffix in artifact_suffixes


def _case_requires_industry_chain(gate_manifest: Any, text_blob: str) -> bool:
    gate_text = ""
    if isinstance(gate_manifest, Mapping):
        gate_text = json.dumps(gate_manifest, ensure_ascii=False)
    haystack = _normalize(f"{gate_text}\n{text_blob}")
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


def _extract_review_findings(payload: Any) -> list[Mapping[str, Any]]:
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


def _review_severity(finding: Mapping[str, Any]) -> str:
    severity = _normalize(
        finding.get("severity") or finding.get("level") or finding.get("priority")
    ).upper()
    if severity.startswith("S"):
        return "S"
    if severity.startswith("A"):
        return "A"
    return "B"


def _review_status(finding: Mapping[str, Any]) -> str:
    return _normalize(
        finding.get("status")
        or finding.get("lifecycle_status")
        or finding.get("state")
        or "open"
    )


def _review_waived(finding: Mapping[str, Any]) -> bool:
    waiver_status = _normalize(finding.get("waiver_status"))
    return (
        _review_status(finding) == "waived"
        or waiver_status == "waived"
        or _truthy(finding.get("waived"))
    )


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _normalize(value) in {"1", "true", "yes", "y", "waived"}


def _extract_publishability_score(review_log: str) -> int | None:
    patterns = (
        r"publishability\s+score\D+(\d{1,3})",
        r"publishability_score\D+(\d{1,3})",
    )
    for pattern in patterns:
        match = re.search(pattern, review_log, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _source_summary(
    source: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    total = len(records)
    error_count = sum(1 for record in records if _has_items(record.get("errors")))
    warning_count = sum(1 for record in records if _has_items(record.get("warnings")))
    ok_count = sum(1 for record in records if record.get("ok", True) is not False)
    quality_counts: dict[str, int] = {}
    latency_values: list[float] = []

    degraded_count = 0
    unavailable_count = 0
    for record in records:
        quality = _quality_tier(record)
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
        if quality in DEGRADED_QUALITY_TIERS:
            degraded_count += 1
        if quality == "unavailable":
            unavailable_count += 1
        latency = _float_or_none(record.get("latency_ms"))
        if latency is not None:
            latency_values.append(latency)

    avg_latency = (
        round(sum(latency_values) / len(latency_values), 2) if latency_values else None
    )
    error_rate = error_count / total if total else 0.0
    warning_rate = warning_count / total if total else 0.0
    degraded_rate = degraded_count / total if total else 0.0
    latency_penalty = min((avg_latency or 0.0) / 1000 * 5, 15)
    score = (
        100 - error_rate * 60 - degraded_rate * 25 - warning_rate * 10 - latency_penalty
    )
    score = round(max(min(score, 100.0), 0.0), 2)

    status = "good"
    if score < 50 or error_rate >= 0.5:
        status = "failing"
    elif score < 80 or degraded_count:
        status = "degraded"

    return {
        "source": source,
        "record_count": total,
        "ok_count": ok_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "degraded_count": degraded_count,
        "unavailable_count": unavailable_count,
        "avg_latency_ms": avg_latency,
        "quality_counts": quality_counts,
        "health_score": score,
        "status": status,
    }


def _evaluate_skill_case(case: SkillEvalCase) -> dict[str, Any]:
    normalized = _normalize(case.response)
    required_hits = [
        term for term in case.required_terms if _normalize(term) in normalized
    ]
    missing_required = [
        term for term in case.required_terms if _normalize(term) not in normalized
    ]
    forbidden_hits = [
        term for term in case.forbidden_terms if _normalize(term) in normalized
    ]
    passed = not missing_required and not forbidden_hits
    score = 100 - len(missing_required) * 20 - len(forbidden_hits) * 50
    return {
        "name": case.name,
        "passed": passed,
        "score": max(score, 0),
        "required_hits": required_hits,
        "missing_required": missing_required,
        "forbidden_hits": forbidden_hits,
        "metadata": dict(case.metadata),
    }


def _resolve_path(value: Any, root: Path | None) -> Path:
    path = Path(str(value or ""))
    if root is not None and not path.is_absolute():
        return root / path
    return path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _quality_tier(record: Mapping[str, Any]) -> str:
    for key in ("quality_tier", "level", "quality", "data_quality"):
        value = record.get(key)
        if isinstance(value, Mapping):
            nested = _quality_tier(cast(Mapping[str, Any], value))
            if nested != "unknown":
                return nested
        elif value:
            return _normalize(value)
    return "unknown"


def _tuple_from_value(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def _json_ready_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _json_ready(item) for key, item in value.items()}


def _json_ready(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return _json_ready_mapping(cast(Mapping[str, Any], value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _has_items(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return bool(str(value).strip())


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _text(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _score_status(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "pass"
    if score >= 50:
        return "weak"
    return "fail"
