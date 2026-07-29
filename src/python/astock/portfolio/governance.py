"""Paper-portfolio linkage checks for market-desk strategy plans.

Manual paper trades remain useful for experiments, but they must not be
presented as investment-committee-governed positions unless their source plan
has an active, independently assured release record.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from ..market_data import verify_frozen_market_archive
from ..market_desk import RestrictedListStore, StrategyPlan, StrategyState
from ..research import ResearchLedger, ResearchStatus


def validate_governed_strategy_link(
    *, entry_id: str, code: str, ledger_path: Path
) -> dict[str, Any]:
    """Validate that one paper trade can be linked to an active desk plan."""
    entry = ResearchLedger(ledger_path).get(entry_id)
    if entry is None:
        raise ValueError("strategy_entry_id was not found in the research ledger")
    if entry.target_type != "strategy_plan":
        raise ValueError("strategy_entry_id must refer to a market-desk strategy plan")
    if entry.status != ResearchStatus.ACTIVE:
        raise ValueError("governed paper trade requires an active strategy-plan entry")
    plan_payload, release_assurance = _latest_plan_and_assurance(entry)
    if not isinstance(plan_payload, Mapping):
        raise ValueError("strategy-plan entry has no valid plan payload")
    plan = StrategyPlan.from_dict(plan_payload)
    if plan.state != StrategyState.ACTIVE:
        raise ValueError("governed paper trade requires an active strategy plan")
    if plan.target != str(code).strip():
        raise ValueError("strategy plan target must match the paper-trade code")
    if not isinstance(release_assurance, Mapping) or release_assurance.get("verdict") != "pass":
        raise ValueError("governed paper trade requires a passing independent release assurance")
    return {
        "strategy_entry_id": str(entry.entry_id),
        "strategy_plan_id": plan.plan_id,
        "target": plan.target,
        "as_of": plan.as_of,
        "review_at": plan.review_at,
        "time_stop_at": plan.time_stop_at,
        "transition_history": list(plan.transition_history),
        "release_assurance": dict(release_assurance),
    }


def validate_governed_paper_entry(
    *,
    entry_id: str,
    code: str,
    ledger_path: Path,
    entry_observed_at: str,
    entry_evidence_refs: Sequence[str],
    entry_observation_archive_path: Path | None,
    restricted_list_path: Path,
) -> dict[str, Any]:
    """Validate one auditable paper entry against an active strategy plan.

    Strategy-plan linkage alone is insufficient for a new position.  The entry
    must be inside the plan's live review window, cite the specific evidence
    that confirmed its textual entry condition, retain a valid frozen market
    observation, and pass the *current* compliance authority check.
    """
    link = validate_governed_strategy_link(
        entry_id=entry_id,
        code=code,
        ledger_path=ledger_path,
    )
    timestamp = _parse_timestamp(entry_observed_at, "entry-observed-at")
    normalized_refs = tuple(
        str(reference).strip() for reference in entry_evidence_refs if str(reference).strip()
    )
    if not normalized_refs:
        raise ValueError("governed paper entry requires at least one entry-evidence-ref")
    plan_as_of = _parse_timestamp(str(link["as_of"]), "strategy plan as_of")
    if timestamp < plan_as_of:
        raise ValueError("paper entry cannot precede the strategy plan as_of timestamp")
    active_at = _active_transition_timestamp(link.get("transition_history"))
    if active_at is not None and timestamp < active_at:
        raise ValueError("paper entry cannot precede the strategy plan active transition")
    review_at = _parse_timestamp(str(link["review_at"]), "strategy plan review_at")
    if timestamp >= review_at:
        raise ValueError("paper entry is blocked because the strategy plan review is due")
    time_stop_value = link.get("time_stop_at")
    if time_stop_value:
        time_stop_at = _parse_timestamp(str(time_stop_value), "strategy plan time_stop_at")
        if timestamp >= time_stop_at:
            raise ValueError("paper entry is blocked because the strategy plan time stop is due")

    archive = verify_frozen_market_archive(entry_observation_archive_path)
    if archive.get("status") != "pass":
        failures = archive.get("failures") or ["unknown archive verification failure"]
        raise ValueError(f"paper entry requires a verified frozen market observation: {failures[0]}")
    if not any(str(archive["archive_id"]) in reference for reference in normalized_refs):
        raise ValueError("entry-evidence-ref must explicitly include the frozen observation archive_id")

    restricted_health = RestrictedListStore(restricted_list_path).health()
    if (
        restricted_health.get("status") != "current"
        or restricted_health.get("signature_status") != "verified"
    ):
        raise ValueError(
            "paper entry requires a current restricted-list authority with a verified compliance signature"
        )
    if str(code).strip() in {
        str(target).strip() for target in restricted_health.get("active_targets", ()) if str(target).strip()
    }:
        raise ValueError("paper entry target is currently restricted")

    return {
        **link,
        "entry_evidence": {
            "observed_at": timestamp.isoformat(),
            "evidence_refs": list(normalized_refs),
            "observation_archive": {
                "archive_id": archive["archive_id"],
                "archive_path": archive["archive_path"],
                "source": archive["source"],
            },
            "restricted_list": {
                "version": restricted_health.get("version"),
                "status": restricted_health.get("status"),
                "signature_status": restricted_health.get("signature_status"),
            },
        },
    }


def validate_governed_paper_exit(
    *,
    entry_id: str,
    code: str,
    ledger_path: Path,
    exit_reason: str,
    exit_observed_at: str,
    exit_evidence_refs: Sequence[str],
    exit_observation_archive_path: Path | None,
) -> dict[str, Any]:
    """Validate auditable evidence for a risk-reducing paper exit.

    An exit never needs a fresh compliance clearance because it reduces risk.
    It does, however, retain its strategy identity and an immutable observation
    so a later lifecycle review can distinguish a planned exit from an
    unreviewed manual record.
    """
    entry = ResearchLedger(ledger_path).get(entry_id)
    if entry is None:
        raise ValueError("strategy_entry_id was not found in the research ledger")
    if entry.target_type != "strategy_plan":
        raise ValueError("strategy_entry_id must refer to a market-desk strategy plan")
    plan_payload, _ = _latest_plan_and_assurance(entry)
    if not isinstance(plan_payload, Mapping):
        raise ValueError("strategy-plan entry has no valid plan payload")
    plan = StrategyPlan.from_dict(plan_payload)
    if plan.target != str(code).strip():
        raise ValueError("strategy plan target must match the paper-trade code")
    normalized_reason = str(exit_reason).strip()
    if not normalized_reason:
        raise ValueError("governed paper exit requires an exit-reason")
    timestamp = _parse_timestamp(exit_observed_at, "exit-observed-at")
    normalized_refs = tuple(
        str(reference).strip() for reference in exit_evidence_refs if str(reference).strip()
    )
    if not normalized_refs:
        raise ValueError("governed paper exit requires at least one exit-evidence-ref")
    archive = verify_frozen_market_archive(exit_observation_archive_path)
    if archive.get("status") != "pass":
        failures = archive.get("failures") or ["unknown archive verification failure"]
        raise ValueError(f"paper exit requires a verified frozen market observation: {failures[0]}")
    if not any(str(archive["archive_id"]) in reference for reference in normalized_refs):
        raise ValueError("exit-evidence-ref must explicitly include the frozen observation archive_id")
    return {
        "strategy_entry_id": str(entry.entry_id),
        "strategy_plan_id": plan.plan_id,
        "target": plan.target,
        "strategy_state_at_exit": plan.state.value,
        "exit_evidence": {
            "reason": normalized_reason,
            "observed_at": timestamp.isoformat(),
            "evidence_refs": list(normalized_refs),
            "observation_archive": {
                "archive_id": archive["archive_id"],
                "archive_path": archive["archive_path"],
                "source": archive["source"],
            },
            "lifecycle_review_required": True,
        },
    }


def audit_paper_portfolio_governance(
    portfolio: Mapping[str, Any], *, ledger_path: Path
) -> dict[str, Any]:
    """Classify paper positions by linkage and retained entry evidence."""
    positions = portfolio.get("positions")
    position_items = positions.items() if isinstance(positions, Mapping) else ()
    governed: list[dict[str, Any]] = []
    unlinked: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    entry_evidence_gaps: list[dict[str, Any]] = []
    exit_review_queue, resolved_exit_reviews = _paper_exit_review_status(
        portfolio, ledger_path=ledger_path
    )
    for key, raw_position in position_items:
        position = raw_position if isinstance(raw_position, Mapping) else {}
        code = str(position.get("code") or key).strip()
        entry_id = str(position.get("strategy_entry_id") or "").strip()
        if not entry_id:
            unlinked.append(
                {
                    "code": code,
                    "reason": "Position has no strategy_entry_id and is legacy/manual paper tracking only.",
                }
            )
            continue
        try:
            link = validate_governed_strategy_link(
                entry_id=entry_id, code=code, ledger_path=ledger_path
            )
        except (TypeError, ValueError) as error:
            invalid.append({"code": code, "strategy_entry_id": entry_id, "reason": str(error)})
            continue
        evidence_error = _validate_recorded_entry_evidence(position)
        if evidence_error:
            entry_evidence_gaps.append(
                {"code": code, "strategy_entry_id": entry_id, "reason": evidence_error}
            )
            continue
        governed.append({"code": code, **link})
    total = len(governed) + len(unlinked) + len(invalid) + len(entry_evidence_gaps)
    status = (
        "pass"
        if total > 0
        and not unlinked
        and not invalid
        and not entry_evidence_gaps
        and not exit_review_queue
        else "not_ready"
        if total == 0 and not exit_review_queue
        else "blocked"
    )
    return {
        "schema_version": "paper-portfolio-governance.v1",
        "ledger_path": str(ledger_path),
        "governance_status": status,
        "position_count": total,
        "governed_count": len(governed),
        "unlinked_legacy_count": len(unlinked),
        "invalid_link_count": len(invalid),
        "entry_evidence_gap_count": len(entry_evidence_gaps),
        "exit_review_required_count": len(exit_review_queue),
        "resolved_exit_review_count": len(resolved_exit_reviews),
        "governed_positions": governed,
        "unlinked_legacy_positions": unlinked,
        "invalid_link_positions": invalid,
        "entry_evidence_gap_positions": entry_evidence_gaps,
        "exit_review_queue": exit_review_queue,
        "resolved_exit_reviews": resolved_exit_reviews,
        "research_only": True,
        "no_order_execution": True,
        "limitations": [
            "This checks strategy-plan linkage only; it does not validate current prices, realized fills, or performance attribution.",
            "An unlinked legacy paper position is preserved but cannot be described as investment-committee-governed.",
            "A linked position without a retained, hash-verifiable paper-entry observation is blocked from governed status.",
            "A governed paper exit remains under lifecycle-review control until a later strategy review explicitly anchors its exit_id.",
        ],
    }


def _latest_plan_and_assurance(entry: Any) -> tuple[Mapping[str, Any] | None, Mapping[str, Any] | None]:
    plan: Mapping[str, Any] | None = (
        entry.metadata.get("strategy_plan")
        if isinstance(getattr(entry, "metadata", None), Mapping)
        else None
    )
    assurance: Mapping[str, Any] | None = None
    for observation in reversed(getattr(entry, "observations", ())):
        evidence = getattr(observation, "evidence", {})
        if not isinstance(evidence, Mapping):
            continue
        observed_plan = evidence.get("strategy_plan")
        if isinstance(observed_plan, Mapping):
            plan = observed_plan
        observed_assurance = evidence.get("release_assurance")
        if isinstance(observed_assurance, Mapping):
            assurance = observed_assurance
        if plan is not None and assurance is not None:
            break
    return plan, assurance


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from error
    if timestamp.tzinfo is None:
        raise ValueError(f"{label} must include a timezone offset")
    return timestamp.astimezone(timezone.utc)


def _active_transition_timestamp(history: Any) -> datetime | None:
    if not isinstance(history, Sequence) or isinstance(history, str):
        return None
    for transition in reversed(history):
        if not isinstance(transition, Mapping) or transition.get("to") != StrategyState.ACTIVE.value:
            continue
        return _parse_timestamp(str(transition.get("observed_at") or ""), "active transition observed_at")
    return None


def _validate_recorded_entry_evidence(position: Mapping[str, Any]) -> str | None:
    history = position.get("entry_evidence_history")
    if not isinstance(history, Sequence) or isinstance(history, str) or not history:
        return "Position has a strategy link but no retained paper-entry evidence history."
    for index, item in enumerate(history):
        if not isinstance(item, Mapping):
            return f"Paper-entry evidence history item {index} is malformed."
        try:
            _parse_timestamp(str(item.get("observed_at") or ""), "entry evidence observed_at")
        except ValueError as error:
            return str(error)
        evidence_refs = item.get("evidence_refs")
        archive = item.get("observation_archive")
        if (
            not isinstance(evidence_refs, Sequence)
            or isinstance(evidence_refs, str)
            or not any(str(reference).strip() for reference in evidence_refs)
            or not isinstance(archive, Mapping)
        ):
            return f"Paper-entry evidence history item {index} lacks evidence references or archive metadata."
        assurance = verify_frozen_market_archive(
            archive.get("archive_path"),
            expected_archive_id=str(archive.get("archive_id") or "") or None,
            expected_source=str(archive.get("source") or "") or None,
        )
        if assurance.get("status") != "pass":
            return f"Paper-entry evidence history item {index} archive cannot be verified."
        if not any(str(archive["archive_id"]) in str(reference) for reference in evidence_refs):
            return f"Paper-entry evidence history item {index} does not reference its archive ID."
    return None


def _paper_exit_review_status(
    portfolio: Mapping[str, Any], *, ledger_path: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Identify governed paper exits awaiting an explicitly anchored review."""
    raw_trades = portfolio.get("trades")
    trades = raw_trades if isinstance(raw_trades, Sequence) and not isinstance(raw_trades, str) else ()
    ledger = ResearchLedger(ledger_path)
    due: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    for index, raw_trade in enumerate(trades):
        if not isinstance(raw_trade, Mapping) or raw_trade.get("governance_status") != "governed_exit":
            continue
        evidence = raw_trade.get("exit_evidence")
        entry_id = str(raw_trade.get("strategy_entry_id") or "").strip()
        if not isinstance(evidence, Mapping) or not entry_id:
            due.append(
                {
                    "trade_index": index,
                    "code": str(raw_trade.get("code") or "").strip(),
                    "reason": "Governed exit lacks strategy identity or structured exit evidence.",
                }
            )
            continue
        if not evidence.get("lifecycle_review_required"):
            continue
        exit_id = str(evidence.get("exit_id") or "").strip()
        try:
            observed_at = _parse_timestamp(str(evidence.get("observed_at") or ""), "exit evidence observed_at")
        except ValueError as error:
            due.append(
                {
                    "trade_index": index,
                    "strategy_entry_id": entry_id,
                    "code": str(raw_trade.get("code") or "").strip(),
                    "reason": str(error),
                }
            )
            continue
        if not exit_id:
            due.append(
                {
                    "trade_index": index,
                    "strategy_entry_id": entry_id,
                    "code": str(raw_trade.get("code") or "").strip(),
                    "reason": "Governed exit evidence lacks an exit_id for lifecycle-review anchoring.",
                }
            )
            continue
        entry = ledger.get(entry_id)
        if entry is None:
            due.append(
                {
                    "trade_index": index,
                    "strategy_entry_id": entry_id,
                    "exit_id": exit_id,
                    "code": str(raw_trade.get("code") or "").strip(),
                    "reason": "Governed exit strategy entry no longer exists in the research ledger.",
                }
            )
            continue
        review = _anchored_exit_review(entry.observations, exit_id=exit_id, after=observed_at)
        item = {
            "trade_index": index,
            "strategy_entry_id": entry_id,
            "strategy_plan_id": str(raw_trade.get("strategy_plan_id") or "").strip(),
            "exit_id": exit_id,
            "code": str(raw_trade.get("code") or "").strip(),
            "trade_date": str(raw_trade.get("trade_date") or "").strip(),
            "position_closed": bool(raw_trade.get("position_closed")),
        }
        if review is None:
            due.append(
                {
                    **item,
                    "reason": "Governed exit requires a later strategy lifecycle review that explicitly references exit_id.",
                }
            )
        else:
            resolved.append({**item, "review_observed_at": review})
    return due, resolved


def _anchored_exit_review(observations: Sequence[Any], *, exit_id: str, after: datetime) -> str | None:
    for observation in observations:
        if getattr(observation, "observation_type", "") != "strategy_lifecycle_review":
            continue
        observed_at = getattr(observation, "observed_at", None)
        if not isinstance(observed_at, datetime) or observed_at.astimezone(timezone.utc) < after:
            continue
        evidence = getattr(observation, "evidence", {})
        refs = evidence.get("evidence_refs") if isinstance(evidence, Mapping) else None
        if (
            isinstance(refs, Sequence)
            and not isinstance(refs, str)
            and exit_id in {str(reference).strip() for reference in refs if str(reference).strip()}
        ):
            return observed_at.isoformat()
    return None
