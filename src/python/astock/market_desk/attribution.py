"""Auditable paper-decision outcome review without synthetic attribution."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping

from ..data_provenance import (
    is_auditable_decision_data_reference,
    is_frozen_public_observation_reference,
)
from ..market_data import verify_frozen_market_archive
from .strategy_book import StrategyPlan


class ReviewOutcome(StrEnum):
    """Relative result of one completed paper-decision review period."""

    OUTPERFORMED = "outperformed"
    IN_LINE = "in_line"
    UNDERPERFORMED = "underperformed"


@dataclass(frozen=True)
class PaperDecisionReview:
    """A bounded, benchmarked review of a single strategy-plan decision.

    This is a total-return review, not a Brinson attribution model.  A
    holdings-level selection/allocation/timing decomposition is intentionally
    unavailable until the desk has matching daily holdings, benchmark weights,
    and price histories.
    """

    entry_id: str
    plan_id: str
    decision_fingerprint: str
    decision_protocol_version: str
    model_versions: dict[str, str]
    evaluation_start: str
    evaluation_end: str
    benchmark_id: str
    gross_paper_return: float
    implementation_cost_return: float
    net_paper_return: float
    benchmark_return: float
    active_return: float
    outcome: ReviewOutcome
    attribution_components: dict[str, float]
    return_evidence: dict[str, Any]
    evidence_status: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-paper-decision-review.v1",
            "entry_id": self.entry_id,
            "plan_id": self.plan_id,
            "decision_fingerprint": self.decision_fingerprint,
            "decision_protocol_version": self.decision_protocol_version,
            "model_versions": self.model_versions,
            "evaluation_start": self.evaluation_start,
            "evaluation_end": self.evaluation_end,
            "benchmark_id": self.benchmark_id,
            "gross_paper_return": self.gross_paper_return,
            "implementation_cost_return": self.implementation_cost_return,
            "net_paper_return": self.net_paper_return,
            "benchmark_return": self.benchmark_return,
            "active_return": self.active_return,
            "outcome": self.outcome.value,
            "attribution_components": self.attribution_components,
            "return_evidence": self.return_evidence,
            "evidence_status": self.evidence_status,
            "limitations": list(self.limitations),
        }


def review_paper_decision(
    *,
    entry_id: str,
    strategy_plan: Mapping[str, Any],
    ic_decision: Mapping[str, Any],
    evaluation_start: str,
    evaluation_end: str,
    benchmark_id: str,
    gross_paper_return: float,
    implementation_cost_return: float,
    benchmark_return: float,
    in_line_threshold: float = 0.005,
    return_evidence: Mapping[str, Any] | None = None,
) -> PaperDecisionReview:
    """Build one reproducible paper-decision outcome packet.

    Every return is a decimal return for the same closed interval.  Costs are
    required and cannot be silently assumed away.  The caller must supply an
    identified benchmark and its return for that exact interval.
    """
    plan = StrategyPlan.from_dict(strategy_plan)
    decision = _validate_ic_decision(plan, ic_decision)
    start = _parse_timestamp(evaluation_start, "evaluation_start")
    end = _parse_timestamp(evaluation_end, "evaluation_end")
    decided_at = _parse_timestamp(str(decision["decided_at"]), "IC decided_at")
    if end <= start:
        raise ValueError("evaluation_end must be later than evaluation_start")
    if start < decided_at:
        raise ValueError("evaluation_start cannot precede the IC decision")
    benchmark = str(benchmark_id).strip()
    if not benchmark:
        raise ValueError("benchmark_id is required for a paper-decision review")
    gross = _return_value(gross_paper_return, "gross_paper_return", allow_negative=True)
    costs = _return_value(implementation_cost_return, "implementation_cost_return", allow_negative=False)
    benchmark_value = _return_value(benchmark_return, "benchmark_return", allow_negative=True)
    threshold = _return_value(in_line_threshold, "in_line_threshold", allow_negative=False)
    net = gross - costs
    active = net - benchmark_value
    outcome = (
        ReviewOutcome.OUTPERFORMED
        if active > threshold
        else ReviewOutcome.UNDERPERFORMED
        if active < -threshold
        else ReviewOutcome.IN_LINE
    )
    versions = dict(decision["model_versions"])
    components = {
        "gross_paper_return": round(gross, 8),
        "implementation_cost_return": round(-costs, 8),
        "net_paper_return": round(net, 8),
        "benchmark_return": round(benchmark_value, 8),
        "active_return": round(active, 8),
    }
    evidence, evidence_status, evidence_limitations = _normalize_return_evidence(
        return_evidence,
        evaluation_start=start.isoformat(),
        evaluation_end=end.isoformat(),
        benchmark_id=benchmark,
        gross_paper_return=gross,
        implementation_cost_return=costs,
        benchmark_return=benchmark_value,
    )
    return PaperDecisionReview(
        entry_id=str(entry_id).strip(),
        plan_id=plan.plan_id,
        decision_fingerprint=_decision_fingerprint(decision),
        decision_protocol_version=str(decision["schema_version"]),
        model_versions=versions,
        evaluation_start=start.isoformat(),
        evaluation_end=end.isoformat(),
        benchmark_id=benchmark,
        gross_paper_return=components["gross_paper_return"],
        implementation_cost_return=costs,
        net_paper_return=components["net_paper_return"],
        benchmark_return=components["benchmark_return"],
        active_return=components["active_return"],
        outcome=outcome,
        attribution_components=components,
        return_evidence=evidence,
        evidence_status=evidence_status,
        limitations=(
            "This is a total-return review only; it does not claim selection, allocation, timing, or factor attribution.",
            "Such decomposition requires daily holdings, benchmark constituents and weights, and matched price histories.",
            *evidence_limitations,
        ),
    )


def _validate_ic_decision(plan: StrategyPlan, value: Mapping[str, Any]) -> Mapping[str, Any]:
    if str(value.get("schema_version") or "") != "market-desk-ic-decision.v1":
        raise ValueError("paper-decision review requires market-desk-ic-decision.v1")
    if str(value.get("candidate_id") or "") != plan.plan_id:
        raise ValueError("IC decision candidate_id must match strategy plan_id")
    if str(value.get("decision") or "") not in {"approve", "conditional"}:
        raise ValueError("paper-decision review requires an approved or conditional IC decision")
    versions = value.get("model_versions")
    if not isinstance(versions, Mapping) or not any(
        str(name).strip() and str(version).strip() for name, version in versions.items()
    ):
        raise ValueError("paper-decision review requires explicit IC model versions")
    return value


def _parse_timestamp(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc


def _return_value(value: float, field_name: str, *, allow_negative: bool) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a finite decimal return") from exc
    if not math.isfinite(result) or result < -1 or (not allow_negative and result < 0):
        raise ValueError(f"{field_name} must be a valid decimal return")
    return result


def _decision_fingerprint(decision: Mapping[str, Any]) -> str:
    canonical = json.dumps(dict(decision), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _normalize_return_evidence(
    value: Mapping[str, Any] | None,
    *,
    evaluation_start: str,
    evaluation_end: str,
    benchmark_id: str,
    gross_paper_return: float,
    implementation_cost_return: float,
    benchmark_return: float,
) -> tuple[dict[str, Any], str, tuple[str, ...]]:
    """Require frozen data references before a review can support release QA."""
    if not isinstance(value, Mapping):
        return (
            {},
            "blocked",
            ("Return and benchmark inputs are user-supplied values without a frozen source packet; this review cannot support a publishable performance claim.",),
        )
    evidence = dict(value)
    required_refs = ("paper_return_ref", "benchmark_return_ref")
    formal_reference = is_auditable_decision_data_reference(evidence)
    public_reference = is_frozen_public_observation_reference(evidence)
    if not (formal_reference or public_reference) or not all(
        str(evidence.get(field) or "").strip() for field in required_refs
    ):
        return (
            evidence,
            "blocked",
            ("Return evidence lacks an eligible source, frozen archive, authorization attestation, or matched paper/benchmark references.",),
        )
    archive_id = str(evidence["archive_id"])
    if archive_id not in str(evidence["paper_return_ref"]) or archive_id not in str(
        evidence["benchmark_return_ref"]
    ):
        return (
            evidence,
            "blocked",
            ("Paper and benchmark return references must both bind the declared frozen archive ID.",),
        )
    if (
        str(evidence.get("evaluation_start") or "") != evaluation_start
        or str(evidence.get("evaluation_end") or "") != evaluation_end
        or str(evidence.get("benchmark_id") or "") != benchmark_id
    ):
        return (
            evidence,
            "blocked",
            ("Return evidence must identify the exact review interval and benchmark.",),
        )
    archive_assurance = verify_frozen_market_archive(
        evidence.get("source_archive_path"),
        expected_archive_id=archive_id,
        expected_source=str(evidence.get("source") or ""),
    )
    evidence["archive_assurance"] = archive_assurance
    if archive_assurance.get("status") != "pass":
        return (
            evidence,
            "blocked",
            ("Return evidence archive is missing, unreadable, or does not match its declared source/hash.",),
        )
    value_assurance = _verify_archived_return_values(
        evidence,
        gross_paper_return=gross_paper_return,
        implementation_cost_return=implementation_cost_return,
        benchmark_return=benchmark_return,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        benchmark_id=benchmark_id,
    )
    evidence["return_value_assurance"] = value_assurance
    if value_assurance["status"] != "pass":
        return (
            evidence,
            "blocked",
            (
                "Declared paper and benchmark returns cannot be independently matched to the frozen return-calculation record.",
            ),
        )
    if public_reference:
        evidence["evidence_tier"] = "public_frozen_observation"
        return (
            evidence,
            "public_frozen",
            (
                "Return inputs bind a verifiable public observation archive, but public aggregation is not formal decision or full portfolio-backtest evidence.",
            ),
        )
    return evidence, "pass", ()


def _verify_archived_return_values(
    evidence: Mapping[str, Any],
    *,
    gross_paper_return: float,
    implementation_cost_return: float,
    benchmark_return: float,
    evaluation_start: str,
    evaluation_end: str,
    benchmark_id: str,
) -> dict[str, Any]:
    """Bind submitted review returns to the content-addressed archive payload.

    Hash verification alone proves only that a file has not changed.  A review
    also needs to prove that its displayed paper return, costs, benchmark, and
    interval are the figures recorded in that exact file.  Public and formal
    inputs intentionally use separate schemas, but both must be deterministic
    return-calculation records rather than an arbitrary market-data snapshot.
    """
    try:
        payload = json.loads(Path(str(evidence["source_archive_path"])).read_text(encoding="utf-8"))
    except (KeyError, OSError, json.JSONDecodeError) as error:
        return {"status": "blocked", "failures": [f"Unable to read frozen return archive: {error}"]}
    raw_records = payload.get("raw_source_records") if isinstance(payload, Mapping) else None
    if not isinstance(raw_records, Mapping):
        return {"status": "blocked", "failures": ["Frozen return archive lacks raw source records."]}

    public = str(evidence.get("source") or "") == "akshare_public"
    record = (
        raw_records.get("frozen_public_portfolio_review")
        if public
        else raw_records.get("formal_paper_return_review")
    )
    if not isinstance(record, Mapping):
        expected = "frozen_public_portfolio_review" if public else "formal_paper_return_review"
        return {
            "status": "blocked",
            "failures": [f"Frozen return archive lacks the required {expected} record."],
        }

    if public:
        portfolio = record.get("portfolio_replay")
        benchmark = record.get("benchmark")
        observed_values = {
            "gross_paper_return": portfolio.get("total_return") if isinstance(portfolio, Mapping) else None,
            "implementation_cost_return": portfolio.get("implementation_cost_return") if isinstance(portfolio, Mapping) else None,
            "benchmark_return": benchmark.get("return") if isinstance(benchmark, Mapping) else None,
            "benchmark_id": benchmark.get("benchmark_id") if isinstance(benchmark, Mapping) else None,
            "evaluation_start": benchmark.get("evaluation_start") if isinstance(benchmark, Mapping) else None,
            "evaluation_end": benchmark.get("evaluation_end") if isinstance(benchmark, Mapping) else None,
        }
        replay_assurance = portfolio.get("data_assurance") if isinstance(portfolio, Mapping) else None
        if not isinstance(replay_assurance, Mapping) or replay_assurance.get("status") != "pass":
            return {
                "status": "blocked",
                "failures": ["Public return record lacks a verified frozen portfolio replay."],
            }
    else:
        if record.get("schema_version") != "formal_paper_return_review.v1":
            return {
                "status": "blocked",
                "failures": ["Formal return record must use formal_paper_return_review.v1."],
            }
        portfolio = record.get("portfolio_replay")
        benchmark = record.get("benchmark")
        observed_values = {
            "gross_paper_return": record.get("gross_paper_return"),
            "implementation_cost_return": record.get("implementation_cost_return"),
            "benchmark_return": benchmark.get("return") if isinstance(benchmark, Mapping) else None,
            "benchmark_id": benchmark.get("benchmark_id") if isinstance(benchmark, Mapping) else None,
            "evaluation_start": record.get("evaluation_start"),
            "evaluation_end": record.get("evaluation_end"),
        }
        reproducibility = portfolio.get("reproducibility_assurance") if isinstance(portfolio, Mapping) else None
        if (
            not isinstance(portfolio, Mapping)
            or not str(portfolio.get("input_archive_id") or "").strip()
            or not str(portfolio.get("result_reference") or "").strip()
            or not isinstance(reproducibility, Mapping)
            or reproducibility.get("status") != "pass"
        ):
            return {
                "status": "blocked",
                "failures": [
                    "Formal return record lacks a reproducible portfolio replay input, result reference, or passing reproducibility assurance."
                ],
            }

    failures = _return_value_mismatches(
        observed_values,
        gross_paper_return=gross_paper_return,
        implementation_cost_return=implementation_cost_return,
        benchmark_return=benchmark_return,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        benchmark_id=benchmark_id,
    )
    return {
        "status": "pass" if not failures else "blocked",
        "record_type": "public_frozen" if public else "formal",
        "failures": failures,
    }


def _return_value_mismatches(
    observed: Mapping[str, Any],
    *,
    gross_paper_return: float,
    implementation_cost_return: float,
    benchmark_return: float,
    evaluation_start: str,
    evaluation_end: str,
    benchmark_id: str,
) -> list[str]:
    failures: list[str] = []
    for field, expected in (
        ("gross_paper_return", gross_paper_return),
        ("implementation_cost_return", implementation_cost_return),
        ("benchmark_return", benchmark_return),
    ):
        try:
            actual = float(observed.get(field))
        except (TypeError, ValueError):
            failures.append(f"Frozen return record lacks a numeric {field}.")
            continue
        if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-10):
            failures.append(f"Frozen return record {field} does not match the submitted review value.")
    for field, expected in (
        ("benchmark_id", benchmark_id),
        ("evaluation_start", evaluation_start),
        ("evaluation_end", evaluation_end),
    ):
        if str(observed.get(field) or "") != expected:
            failures.append(f"Frozen return record {field} does not match the submitted review value.")
    return failures
