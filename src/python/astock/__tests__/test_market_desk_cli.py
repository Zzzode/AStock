"""CLI coverage for auditable market-desk paper-plan lifecycle adapters."""

import json
from pathlib import Path

from typer.testing import CliRunner

from astock import cli


def _strategy_plan() -> dict[str, object]:
    return {
        "plan_id": "short-600460-20260728",
        "horizon": "short_term",
        "state": "observation",
        "target": "600460",
        "thesis": "Conditional paper-plan thesis.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "A verified condition occurs.",
        "invalidation_condition": "The defined risk level breaks.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["market_snapshot:2026-07-28T15:00:00+08:00"],
    }


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_market_desk_run_cli_emits_the_shared_team_packet(monkeypatch) -> None:
    runner = CliRunner()
    expected = {
        "observed_at": "2026-07-28T15:10:00+08:00",
        "market_overview": {"regime": {"regime": "risk_off"}},
        "whole_market_discovery": {"screening_counts": {"returned_candidates": 0}},
        "operational_readiness": {
            "observation_desk_status": "ready",
            "public_paper_entry_status": "blocked",
            "formal_paper_desk_status": "not_enabled",
        },
        "research_only": True,
        "no_order_execution": True,
    }

    async def _packet(**kwargs):
        assert kwargs["candidate_limit"] == 12
        assert kwargs["min_amount"] == 100_000_000.0
        return expected

    monkeypatch.setattr(cli.capabilities, "build_market_desk_team_packet", _packet)
    result = runner.invoke(
        cli.app,
        ["market-desk-run", "--candidate-limit", "12", "--min-amount", "100000000", "--json"],
    )

    assert result.exit_code == 0, result.stdout
    assert json.loads(result.stdout) == expected


def test_market_desk_playbook_cli_uses_capability_kernel(monkeypatch) -> None:
    runner = CliRunner()
    expected = {
        "schema_version": "market-desk-playbook-catalog.v1",
        "playbooks": [{"playbook_id": "event_repricing", "horizon": "short_term"}],
        "research_only": True,
        "no_order_execution": True,
    }
    monkeypatch.setattr(cli.capabilities, "list_market_desk_playbooks", lambda: expected)

    result = runner.invoke(cli.app, ["market-desk-playbooks", "--json"])

    assert result.exit_code == 0, result.stdout
    assert json.loads(result.stdout) == expected


def test_market_desk_playbook_evaluation_cli_reads_evidence(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    evidence_path = _write_json(tmp_path / "evidence.json", {"primary_event": {"source": "fixture"}})
    received: dict[str, object] = {}

    def _evaluate(playbook_id: str, evidence: dict[str, object], *, regime: str) -> dict[str, object]:
        received.update({"playbook_id": playbook_id, "evidence": evidence, "regime": regime})
        return {
            "playbook_id": playbook_id,
            "decision": "watch",
            "failed_requirements": ["fundamental_bridge"],
            "research_only": True,
            "no_order_execution": True,
        }

    monkeypatch.setattr(cli.capabilities, "evaluate_market_desk_playbook", _evaluate)
    result = runner.invoke(
        cli.app,
        ["market-desk-evaluate-playbook", "event_repricing", str(evidence_path), "--regime", "selective_risk_on", "--json"],
    )

    assert result.exit_code == 0, result.stdout
    assert received == {
        "playbook_id": "event_repricing",
        "evidence": {"primary_event": {"source": "fixture"}},
        "regime": "selective_risk_on",
    }
    assert json.loads(result.stdout)["decision"] == "watch"


def test_strategy_plan_lifecycle_cli_uses_the_validated_capabilities(tmp_path: Path) -> None:
    runner = CliRunner()
    ledger_path = tmp_path / "ledger.json"
    plan_path = _write_json(tmp_path / "plan.json", _strategy_plan())

    created = runner.invoke(
        cli.app,
        [
            "market-desk-create-plan",
            str(plan_path),
            "--title",
            "600460 short-term paper plan",
            "--tag",
            "semiconductor",
            "--ledger-path",
            str(ledger_path),
            "--json",
        ],
    )

    assert created.exit_code == 0, created.stdout
    entry_id = json.loads(created.stdout)["entry"]["entry_id"]

    watched = runner.invoke(
        cli.app,
        [
            "market-desk-transition-plan",
            entry_id,
            "--next-state",
            "watch",
            "--reason",
            "Awaiting independent verification.",
            "--ledger-path",
            str(ledger_path),
            "--json",
        ],
    )
    assert watched.exit_code == 0, watched.stdout
    assert json.loads(watched.stdout)["entry"]["status"] == "monitoring"

    reviewed = runner.invoke(
        cli.app,
        [
            "market-desk-record-strategy-review",
            entry_id,
            "--reviewer",
            "portfolio-manager",
            "--reason",
            "No invalidation; retain the observation plan.",
            "--evidence-ref",
            "public-observation:fixture",
            "--observed-at",
            "2026-07-28T16:00:00+08:00",
            "--next-review-at",
            "2026-07-30T15:00:00+08:00",
            "--ledger-path",
            str(ledger_path),
            "--json",
        ],
    )
    assert reviewed.exit_code == 0, reviewed.stdout
    plan = json.loads(reviewed.stdout)["entry"]["observations"][-1]["evidence"]["strategy_plan"]
    assert plan["state"] == "watch"
    assert plan["review_at"] == "2026-07-30T15:00:00+08:00"

    active_without_release = runner.invoke(
        cli.app,
        [
            "market-desk-transition-plan",
            entry_id,
            "--next-state",
            "active",
            "--reason",
            "Attempt an unverified release.",
            "--ledger-path",
            str(ledger_path),
            "--json",
        ],
    )
    assert active_without_release.exit_code != 0


def test_paper_decision_review_cli_passes_structured_inputs_to_capability(
    tmp_path: Path, monkeypatch
) -> None:
    runner = CliRunner()
    received: dict[str, object] = {}

    def _record(entry_id: str, **kwargs: object) -> dict[str, object]:
        received["entry_id"] = entry_id
        received.update(kwargs)
        return {
            "success": True,
            "review": {"outcome": "underperformed", "evidence_status": "public_frozen"},
            "entry": {"entry_id": entry_id},
        }

    monkeypatch.setattr(cli.capabilities, "record_market_desk_paper_decision_review", _record)
    decision_path = _write_json(
        tmp_path / "decision.json",
        {"schema_version": "market-desk-ic-decision.v1", "candidate_id": "plan-1"},
    )
    evidence_path = _write_json(
        tmp_path / "return-evidence.json", {"archive_id": "sha256:fixture"}
    )

    result = runner.invoke(
        cli.app,
        [
            "market-desk-record-paper-review",
            "entry-1",
            "--ic-decision-file",
            str(decision_path),
            "--evaluation-start",
            "2026-07-28T15:00:00+08:00",
            "--evaluation-end",
            "2026-07-29T15:00:00+08:00",
            "--benchmark-id",
            "CSI300",
            "--gross-paper-return",
            "0.01",
            "--implementation-cost-return",
            "0.001",
            "--benchmark-return",
            "0.002",
            "--return-evidence-file",
            str(evidence_path),
            "--ledger-path",
            str(tmp_path / "ledger.json"),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert received["entry_id"] == "entry-1"
    assert received["ic_decision"] == {
        "schema_version": "market-desk-ic-decision.v1",
        "candidate_id": "plan-1",
    }
    assert received["return_evidence"] == {"archive_id": "sha256:fixture"}
    assert received["gross_paper_return"] == 0.01
