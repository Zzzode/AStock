"""Deterministic quality checks for system evolution workflows."""

from __future__ import annotations

import hashlib
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
}

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
