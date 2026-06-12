"""Research quality feedback loop.

Extends postmortem tracking to evaluate:
- Catalyst realization rate (which predicted catalysts actually materialized)
- Risk foresight rate (did we predict the actual risks that materialized)
- Agent role accuracy (which agent perspectives were most accurate)

Provides structured metrics for iterative improvement of agent analysis.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..utils import get_logger

logger = get_logger("quality_feedback")


@dataclass
class CatalystOutcome:
    """Tracking whether a predicted catalyst materialized."""

    catalyst: str
    realized: bool = False
    partial: bool = False
    notes: str = ""
    realized_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalyst": self.catalyst,
            "realized": self.realized,
            "partial": self.partial,
            "notes": self.notes,
            "realized_at": self.realized_at.isoformat() if self.realized_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CatalystOutcome":
        return cls(
            catalyst=str(data["catalyst"]),
            realized=bool(data.get("realized", False)),
            partial=bool(data.get("partial", False)),
            notes=str(data.get("notes", "")),
            realized_at=(
                datetime.fromisoformat(data["realized_at"])
                if data.get("realized_at")
                else None
            ),
        )


@dataclass
class RiskOutcome:
    """Tracking whether a predicted risk materialized."""

    risk: str
    materialized: bool = False
    severity_actual: str = ""  # none | minor | major | critical
    was_predicted: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk": self.risk,
            "materialized": self.materialized,
            "severity_actual": self.severity_actual,
            "was_predicted": self.was_predicted,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskOutcome":
        return cls(
            risk=str(data["risk"]),
            materialized=bool(data.get("materialized", False)),
            severity_actual=str(data.get("severity_actual", "")),
            was_predicted=bool(data.get("was_predicted", True)),
            notes=str(data.get("notes", "")),
        )


@dataclass
class AgentRoleScore:
    """Accuracy score for a specific agent role."""

    role: str
    correct_calls: int = 0
    total_calls: int = 0
    notable_misses: list[str] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct_calls / self.total_calls if self.total_calls > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "correct_calls": self.correct_calls,
            "total_calls": self.total_calls,
            "accuracy": round(self.accuracy, 4),
            "notable_misses": self.notable_misses,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentRoleScore":
        return cls(
            role=str(data["role"]),
            correct_calls=int(data.get("correct_calls", 0)),
            total_calls=int(data.get("total_calls", 0)),
            notable_misses=list(data.get("notable_misses", [])),
        )


@dataclass
class ResearchQualityReport:
    """Full quality assessment for a research entry's outcome."""

    entry_id: str
    catalyst_outcomes: list[CatalystOutcome] = field(default_factory=list)
    risk_outcomes: list[RiskOutcome] = field(default_factory=list)
    unpredicted_risks: list[RiskOutcome] = field(default_factory=list)
    agent_scores: list[AgentRoleScore] = field(default_factory=list)
    overall_catalyst_rate: float = 0.0
    overall_risk_foresight: float = 0.0
    assessed_at: datetime = field(default_factory=datetime.now)
    notes: str = ""

    def compute_rates(self) -> None:
        """Recompute catalyst realization rate and risk foresight rate."""
        if self.catalyst_outcomes:
            realized = sum(
                1 for c in self.catalyst_outcomes if c.realized or c.partial
            )
            self.overall_catalyst_rate = realized / len(self.catalyst_outcomes)

        all_risks = self.risk_outcomes + self.unpredicted_risks
        materialized = [r for r in all_risks if r.materialized]
        if materialized:
            predicted = sum(1 for r in materialized if r.was_predicted)
            self.overall_risk_foresight = predicted / len(materialized)

    def to_dict(self) -> dict[str, Any]:
        self.compute_rates()
        return {
            "entry_id": self.entry_id,
            "catalyst_outcomes": [c.to_dict() for c in self.catalyst_outcomes],
            "risk_outcomes": [r.to_dict() for r in self.risk_outcomes],
            "unpredicted_risks": [r.to_dict() for r in self.unpredicted_risks],
            "agent_scores": [a.to_dict() for a in self.agent_scores],
            "overall_catalyst_rate": round(self.overall_catalyst_rate, 4),
            "overall_risk_foresight": round(self.overall_risk_foresight, 4),
            "assessed_at": self.assessed_at.isoformat(),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchQualityReport":
        report = cls(
            entry_id=str(data["entry_id"]),
            catalyst_outcomes=[
                CatalystOutcome.from_dict(c)
                for c in data.get("catalyst_outcomes", [])
            ],
            risk_outcomes=[
                RiskOutcome.from_dict(r) for r in data.get("risk_outcomes", [])
            ],
            unpredicted_risks=[
                RiskOutcome.from_dict(r) for r in data.get("unpredicted_risks", [])
            ],
            agent_scores=[
                AgentRoleScore.from_dict(a)
                for a in data.get("agent_scores", [])
            ],
            assessed_at=datetime.fromisoformat(data["assessed_at"]),
            notes=str(data.get("notes", "")),
        )
        report.compute_rates()
        return report


class QualityFeedbackStore:
    """JSON-backed store for research quality feedback data."""

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or Path("data/quality-feedback.json")
        self._reports: dict[str, ResearchQualityReport] = {}
        self._role_scores: dict[str, AgentRoleScore] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        if not self.store_path.exists():
            return
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            self._reports = {
                item["entry_id"]: ResearchQualityReport.from_dict(item)
                for item in raw.get("reports", [])
            }
            self._role_scores = {
                item["role"]: AgentRoleScore.from_dict(item)
                for item in raw.get("aggregate_role_scores", [])
            }
        except Exception:
            self._reports = {}
            self._role_scores = {}

    def _save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "quality-feedback.v1",
            "updated_at": datetime.now().isoformat(),
            "reports": [r.to_dict() for r in self._reports.values()],
            "aggregate_role_scores": [s.to_dict() for s in self._role_scores.values()],
        }
        self.store_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def record_quality_report(self, report: ResearchQualityReport) -> None:
        """Record a quality assessment for a research entry."""
        self._ensure_loaded()
        report.compute_rates()
        self._reports[report.entry_id] = report
        self._update_aggregate_scores(report)
        self._save()

    def get_report(self, entry_id: str) -> Optional[ResearchQualityReport]:
        self._ensure_loaded()
        return self._reports.get(entry_id)

    def get_aggregate_stats(self) -> dict[str, Any]:
        """Get aggregate quality statistics across all assessed entries."""
        self._ensure_loaded()
        if not self._reports:
            return {"total_assessed": 0}

        catalyst_rates = [
            r.overall_catalyst_rate for r in self._reports.values()
        ]
        risk_rates = [
            r.overall_risk_foresight for r in self._reports.values()
        ]

        return {
            "total_assessed": len(self._reports),
            "avg_catalyst_realization_rate": (
                round(sum(catalyst_rates) / len(catalyst_rates), 4)
                if catalyst_rates else 0.0
            ),
            "avg_risk_foresight_rate": (
                round(sum(risk_rates) / len(risk_rates), 4)
                if risk_rates else 0.0
            ),
            "agent_role_scores": {
                role: score.to_dict()
                for role, score in self._role_scores.items()
            },
        }

    def _update_aggregate_scores(self, report: ResearchQualityReport) -> None:
        """Update aggregate role accuracy scores."""
        for score in report.agent_scores:
            if score.role not in self._role_scores:
                self._role_scores[score.role] = AgentRoleScore(role=score.role)
            agg = self._role_scores[score.role]
            agg.correct_calls += score.correct_calls
            agg.total_calls += score.total_calls
            agg.notable_misses.extend(score.notable_misses[-3:])
            if len(agg.notable_misses) > 10:
                agg.notable_misses = agg.notable_misses[-10:]
