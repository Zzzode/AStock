"""Tests for version-bound, benchmarked paper-decision reviews."""

import hashlib
import json

import pytest

from astock import capabilities
from astock.market_data import build_public_market_observation_packet
from astock.market_desk import review_paper_decision


def _plan() -> dict[str, object]:
    return {
        "plan_id": "short-600460-20260728",
        "horizon": "short_term",
        "state": "active",
        "target": "600460",
        "thesis": "Conditional paper-plan thesis.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "A verified condition occurs.",
        "invalidation_condition": "The defined risk level breaks.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["market_snapshot:2026-07-28T15:00:00+08:00"],
    }


def _decision() -> dict[str, object]:
    return {
        "schema_version": "market-desk-ic-decision.v1",
        "candidate_id": "short-600460-20260728",
        "decision": "approve",
        "decision_owner": "portfolio-manager",
        "decided_at": "2026-07-28T15:05:00+08:00",
        "model_versions": {"market_regime": "market-desk-regime.v1", "risk_policy": "risk-limits.v1"},
    }


def _frozen_archive(
    tmp_path,
    *,
    gross_paper_return: float = 0.12,
    implementation_cost_return: float = 0.002,
    benchmark_return: float = 0.04,
) -> tuple[str, str]:
    raw_records = {
        "formal_paper_return_review": {
            "schema_version": "formal_paper_return_review.v1",
            "gross_paper_return": gross_paper_return,
            "implementation_cost_return": implementation_cost_return,
            "evaluation_start": "2026-07-28T15:05:00+08:00",
            "evaluation_end": "2026-08-07T15:00:00+08:00",
            "benchmark": {"benchmark_id": "000300.SH", "return": benchmark_return},
            "portfolio_replay": {
                "input_archive_id": "sha256:portfolio-input",
                "result_reference": "portfolio-backtest:sha256:portfolio-result",
                "reproducibility_assurance": {"status": "pass"},
            },
        }
    }
    source = "tushare_pro"
    envelope = {
        "schema_version": "market_data_frozen_archive.v1",
        "source": source,
        "raw_source_records": raw_records,
    }
    digest = hashlib.sha256(
        json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    archive_id = f"sha256:{digest}"
    path = tmp_path / f"{digest}.json"
    path.write_text(
        json.dumps({**envelope, "archive_id": archive_id}), encoding="utf-8"
    )
    return str(path), archive_id


def _return_evidence(source_archive_path: str, archive_id: str) -> dict[str, object]:
    return {
        "source": "tushare_pro",
        "archive_id": archive_id,
        "source_archive_path": source_archive_path,
        "as_of": "2026-08-07T15:30:00+08:00",
        "license_attestation": {"authorized": True, "attested_by": "research-data-owner"},
        "paper_return_ref": f"portfolio-backtest:{archive_id}",
        "benchmark_return_ref": f"benchmark:000300.SH:{archive_id}",
        "evaluation_start": "2026-07-28T15:05:00+08:00",
        "evaluation_end": "2026-08-07T15:00:00+08:00",
        "benchmark_id": "000300.SH",
    }


def test_review_is_benchmarked_cost_aware_and_version_bound(tmp_path) -> None:
    archive_path, archive_id = _frozen_archive(tmp_path)
    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan=_plan(),
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.12,
        implementation_cost_return=0.002,
        benchmark_return=0.04,
        return_evidence=_return_evidence(archive_path, archive_id),
    )

    assert review.net_paper_return == 0.118
    assert review.active_return == 0.078
    assert review.outcome.value == "outperformed"
    assert review.decision_fingerprint
    assert review.evidence_status == "pass"
    assert review.return_evidence["return_value_assurance"]["status"] == "pass"
    assert "selection" in review.limitations[0]


def test_review_rejects_missing_model_version_or_pre_decision_period() -> None:
    decision = _decision()
    decision.pop("model_versions")
    with pytest.raises(ValueError, match="model versions"):
        review_paper_decision(
            entry_id="entry-1", strategy_plan=_plan(), ic_decision=decision,
            evaluation_start="2026-07-28T15:05:00+08:00", evaluation_end="2026-08-07T15:00:00+08:00",
            benchmark_id="000300.SH", gross_paper_return=0.1, implementation_cost_return=0.001, benchmark_return=0.03,
        )


def test_review_without_frozen_return_evidence_is_recorded_but_not_publishable() -> None:
    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan=_plan(),
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.1,
        implementation_cost_return=0.001,
        benchmark_return=0.03,
    )

    assert review.evidence_status == "blocked"
    assert "frozen source" in review.limitations[-1]
    with pytest.raises(ValueError, match="cannot precede"):
        review_paper_decision(
            entry_id="entry-1", strategy_plan=_plan(), ic_decision=_decision(),
            evaluation_start="2026-07-28T15:04:00+08:00", evaluation_end="2026-08-07T15:00:00+08:00",
            benchmark_id="000300.SH", gross_paper_return=0.1, implementation_cost_return=0.001, benchmark_return=0.03,
        )


def test_review_is_persisted_as_a_research_observation(tmp_path) -> None:
    archive_path, archive_id = _frozen_archive(tmp_path)
    created = capabilities.create_market_desk_strategy_plan(
        {**_plan(), "state": "observation"}, title="test plan", ledger_path=tmp_path / "ledger.json"
    )
    result = capabilities.record_market_desk_paper_decision_review(
        created["entry"]["entry_id"],
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.12,
        implementation_cost_return=0.002,
        benchmark_return=0.04,
        return_evidence=_return_evidence(archive_path, archive_id),
        ledger_path=tmp_path / "ledger.json",
    )

    assert result["review"]["outcome"] == "outperformed"
    assert result["review"]["evidence_status"] == "pass"
    assert result["entry"]["observations"][-1]["observation_type"] == "paper_decision_review"


def test_underperformance_review_requires_a_later_explicitly_anchored_postmortem(tmp_path) -> None:
    archive_path, archive_id = _frozen_archive(tmp_path, gross_paper_return=0.01)
    created = capabilities.create_market_desk_strategy_plan(
        {**_plan(), "state": "observation"}, title="test plan", ledger_path=tmp_path / "ledger.json"
    )
    entry_id = created["entry"]["entry_id"]
    reviewed = capabilities.record_market_desk_paper_decision_review(
        entry_id,
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.01,
        implementation_cost_return=0.002,
        benchmark_return=0.04,
        return_evidence=_return_evidence(archive_path, archive_id),
        ledger_path=tmp_path / "ledger.json",
    )

    queue = capabilities.get_market_desk_postmortem_queue(ledger_path=tmp_path / "ledger.json")
    assert reviewed["review"]["outcome"] == "underperformed"
    assert queue["due_count"] == 1
    assert queue["due"][0]["attention"] == "postmortem_required"
    anchor = queue["due"][0]["required_review_anchor"]

    capabilities.record_research_postmortem(
        entry_id,
        outcome="underperformed",
        root_cause="timing",
        expected="The plan would outperform its benchmark.",
        actual="The verified paper result lagged the benchmark.",
        error_analysis="Reviewed after the frozen result packet.",
        lessons=["Review timing risk before repeating the setup."],
        evidence={"review_anchor": anchor},
        ledger_path=tmp_path / "ledger.json",
    )

    resolved = capabilities.get_market_desk_postmortem_queue(ledger_path=tmp_path / "ledger.json")
    assert resolved["due_count"] == 0


def test_review_with_declared_but_missing_archive_stays_blocked(tmp_path) -> None:
    _, archive_id = _frozen_archive(tmp_path)
    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan=_plan(),
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.1,
        implementation_cost_return=0.001,
        benchmark_return=0.03,
        return_evidence=_return_evidence(str(tmp_path / "missing.json"), archive_id),
    )

    assert review.evidence_status == "blocked"
    assert review.return_evidence["archive_assurance"]["status"] == "blocked"


def test_review_blocks_return_values_that_do_not_match_the_frozen_record(tmp_path) -> None:
    archive_path, archive_id = _frozen_archive(tmp_path)

    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan=_plan(),
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.11,
        implementation_cost_return=0.002,
        benchmark_return=0.04,
        return_evidence=_return_evidence(archive_path, archive_id),
    )

    assert review.evidence_status == "blocked"
    assert review.return_evidence["return_value_assurance"]["status"] == "blocked"
    assert "gross_paper_return" in review.return_evidence["return_value_assurance"]["failures"][0]


def test_review_records_frozen_public_evidence_without_promoting_it_to_formal_status(tmp_path) -> None:
    packet = build_public_market_observation_packet(
        subject="frozen_public_portfolio_review",
        observation={
            "observed_at": "2026-08-07T15:30:00+08:00",
            "portfolio_replay": {
                "total_return": 0.1,
                "implementation_cost_return": 0.001,
                "data_assurance": {"status": "pass"},
            },
            "benchmark": {
                "benchmark_id": "000300.SH",
                "evaluation_start": "2026-07-28T15:05:00+08:00",
                "evaluation_end": "2026-08-07T15:00:00+08:00",
                "return": 0.04,
            },
        },
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan=_plan(),
        ic_decision=_decision(),
        evaluation_start="2026-07-28T15:05:00+08:00",
        evaluation_end="2026-08-07T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=0.1,
        implementation_cost_return=0.001,
        benchmark_return=0.04,
        return_evidence={
            "source": "akshare_public",
            "archive_id": packet.archive_id,
            "source_archive_path": str(archive_path),
            "paper_return_ref": f"paper:{packet.archive_id}",
            "benchmark_return_ref": f"benchmark:000300.SH:{packet.archive_id}",
            "evaluation_start": "2026-07-28T15:05:00+08:00",
            "evaluation_end": "2026-08-07T15:00:00+08:00",
            "benchmark_id": "000300.SH",
        },
    )

    assert review.evidence_status == "public_frozen"
    assert review.return_evidence["evidence_tier"] == "public_frozen_observation"
    assert "public aggregation" in review.limitations[-1]
