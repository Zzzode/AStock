from datetime import datetime, timezone

from astock.market_desk import (
    DeskDecision,
    MarketRegime,
    assess_market_regime,
    decide_investment_committee,
    evaluate_candidate_gate,
)

ASSESSMENT_NOW = datetime(2026, 7, 28, 2, 5, tzinfo=timezone.utc)


def _snapshot(*, advances: int = 3000, declines: int = 1800, sh: float = 0.8, growth: float = 1.2):
    return {
        "observed_at": "2026-07-28T02:00:00+00:00",
        "market_session": {"state": "continuous_morning", "calendar_basis": "exchange_calendar"},
        "indices": [
            {"code": "sh000001", "change_pct": sh},
            {"code": "sz399006", "change_pct": growth},
        ],
        "breadth": {
            "advances": advances,
            "declines": declines,
            "limit_up": 80,
            "limit_down": 8,
            "coverage_ratio": 1.0,
        },
        "provenance": {
            "quality_tier": "realtime",
            "components": {"trading_calendar": {"status": "available"}},
        },
    }


def _candidate():
    return {
        "targets": ["600460"],
        "universe": {"eligible": True, "liquid": True},
        "data": {
            "as_of": "2026-07-28T15:00:00+08:00",
            "source": "tushare_pro",
            "quality": "realtime",
            "archive_id": "sha256:decision-packet",
            "license_attestation": {"authorized": True, "attested_by": "research-data-owner"},
        },
        "edge": {"thesis": "test", "catalyst": "test", "invalidation": "test"},
        "risk": {"max_loss_pct": 0.01, "position_limit_pct": 0.1},
        "execution": {"entry_condition": "test", "exit_condition": "test", "review_at": "close"},
        "compliance": {
            "research_only_disclosure": True,
            "no_execution_instruction": True,
            "conflicts_disclosed": True,
            "suitability_disclosure": True,
            "restricted": False,
            "mnpi_or_inside_information": False,
            "prohibited_claims": [],
        },
    }


def _controls(*, override=None):
    controls = {
        "data-verifier": {"status": "pass", "reason": "sources current"},
        "risk-analyst": {"status": "pass", "reason": "risk budget available"},
        "quant-risk-modeler": {"status": "pass", "reason": "model limits reviewed"},
        "execution-liquidity-analyst": {"status": "pass", "reason": "liquidity supports size"},
        "compliance-officer": {"status": "pass", "reason": "research boundary disclosed"},
    }
    if override:
        controls.update(override)
    return controls


def test_assess_market_regime_blocks_missing_breadth():
    snapshot = _snapshot()
    snapshot.pop("breadth")
    assessment = assess_market_regime(snapshot, now=ASSESSMENT_NOW)
    assert assessment.regime == MarketRegime.INSUFFICIENT_DATA
    assert not assessment.allowed_horizons


def test_assess_market_regime_identifies_risk_off():
    assessment = assess_market_regime(
        _snapshot(advances=1200, declines=3600, sh=-2.0, growth=-4.0), now=ASSESSMENT_NOW
    )
    assert assessment.regime == MarketRegime.RISK_OFF
    assert assessment.allowed_horizons == ("risk_management",)


def test_assess_market_regime_identifies_trend_risk_on():
    assessment = assess_market_regime(_snapshot(), now=ASSESSMENT_NOW)
    assert assessment.regime == MarketRegime.TREND_RISK_ON


def test_assess_market_regime_blocks_stale_market_snapshot():
    assessment = assess_market_regime(
        _snapshot(), now=datetime(2026, 7, 28, 2, 16, tzinfo=timezone.utc)
    )

    assert assessment.regime == MarketRegime.INSUFFICIENT_DATA
    assert "freshness window" in assessment.warnings[-1]


def test_assess_market_regime_blocks_risk_on_for_snapshot_quality():
    snapshot = _snapshot()
    snapshot["provenance"]["quality_tier"] = "snapshot"

    assessment = assess_market_regime(snapshot, now=ASSESSMENT_NOW)

    assert assessment.regime == MarketRegime.DEFENSIVE_ROTATION
    assert assessment.allowed_horizons == ("watch", "conditional")


def test_assess_market_regime_blocks_risk_on_for_partial_breadth_coverage():
    snapshot = _snapshot()
    snapshot["breadth"]["coverage_ratio"] = 0.97

    assessment = assess_market_regime(snapshot, now=ASSESSMENT_NOW)

    assert assessment.regime == MarketRegime.DEFENSIVE_ROTATION


def test_candidate_gate_never_approves_missing_execution():
    candidate = _candidate()
    candidate["execution"] = {}
    result = evaluate_candidate_gate(candidate, regime=MarketRegime.TREND_RISK_ON)
    assert result.decision == DeskDecision.WATCH
    assert result.failed_gates == ("execution",)


def test_candidate_gate_rejects_public_aggregation_as_decision_evidence():
    candidate = _candidate()
    candidate["data"]["source"] = "akshare_public"

    result = evaluate_candidate_gate(candidate, regime=MarketRegime.TREND_RISK_ON)

    assert result.decision == DeskDecision.WATCH
    assert "data" in result.failed_gates


def test_candidate_gate_rejects_unfrozen_vendor_label_as_decision_evidence():
    candidate = _candidate()
    candidate["data"].pop("archive_id")

    result = evaluate_candidate_gate(candidate, regime=MarketRegime.TREND_RISK_ON)

    assert result.decision == DeskDecision.WATCH
    assert "data" in result.failed_gates


def test_candidate_gate_blocks_missing_internal_compliance_disclosures():
    candidate = _candidate()
    candidate["compliance"] = {"research_only_disclosure": True}

    result = evaluate_candidate_gate(
        candidate, regime=MarketRegime.TREND_RISK_ON, control_assessments=_controls()
    )

    assert result.decision == DeskDecision.WATCH
    assert "compliance" in result.failed_gates


def test_candidate_gate_rejects_restricted_target_even_with_pass_control() -> None:
    candidate = _candidate()
    candidate["targets"] = ["600460"]

    result = evaluate_candidate_gate(
        candidate,
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(),
        restricted_targets=["600460"],
    )

    assert result.decision == DeskDecision.REJECT
    assert "restricted" in result.control_blockers[0].lower()


def test_candidate_gate_requires_market_permission():
    result = evaluate_candidate_gate(
        _candidate(),
        regime=MarketRegime.RISK_OFF,
        control_assessments=_controls(),
    )
    assert result.decision == DeskDecision.WATCH


def test_candidate_gate_blocks_missing_control_assessment():
    result = evaluate_candidate_gate(
        _candidate(),
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(override={"compliance-officer": None}),
    )

    assert result.decision == DeskDecision.WATCH
    assert "Missing required control assessment: compliance-officer." in result.control_blockers


def test_candidate_gate_rejects_binding_veto():
    result = evaluate_candidate_gate(
        _candidate(),
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(
            override={"execution-liquidity-analyst": {"status": "veto", "reason": "suspended"}}
        ),
    )

    assert result.decision == DeskDecision.REJECT
    assert result.control_statuses["execution-liquidity-analyst"] == "veto"


def test_candidate_gate_rejects_invalid_risk_bounds():
    candidate = _candidate()
    candidate["risk"] = {"max_loss_pct": 0, "position_limit_pct": 1.2}

    result = evaluate_candidate_gate(
        candidate,
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(),
    )

    assert result.decision == DeskDecision.WATCH
    assert result.failed_gates == ("risk",)


def test_short_candidate_requires_overnight_and_limit_down_stress():
    candidate = _candidate()
    candidate["risk"] = {
        "max_loss_pct": 0.01,
        "position_limit_pct": 0.1,
        "horizon": "short_term",
    }

    result = evaluate_candidate_gate(
        candidate,
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(),
    )

    assert result.decision == DeskDecision.WATCH
    assert result.failed_gates == ("risk",)


def test_investment_committee_decision_requires_controls_and_evidence():
    result = decide_investment_committee(
        _candidate(),
        candidate_id="600460-short-20260728",
        regime=MarketRegime.TREND_RISK_ON,
        control_assessments=_controls(),
        decision_owner="portfolio-manager",
        evidence_refs=("market_snapshot:2026-07-28T15:00:00+08:00",),
        model_versions={"market_regime": "market-desk-regime.v1", "risk_policy": "risk-limits.v1"},
        decided_at="2026-07-28T15:05:00+08:00",
    )

    assert result.decision == DeskDecision.APPROVE
    assert result.to_dict()["schema_version"] == "market-desk-ic-decision.v1"
    assert result.to_dict()["model_versions"]["market_regime"] == "market-desk-regime.v1"


def test_investment_committee_decision_requires_named_model_versions() -> None:
    try:
        decide_investment_committee(
            _candidate(),
            candidate_id="600460-short-20260728",
            regime=MarketRegime.TREND_RISK_ON,
            control_assessments=_controls(),
            decision_owner="portfolio-manager",
            evidence_refs=("market_snapshot:2026-07-28T15:00:00+08:00",),
            decided_at="2026-07-28T15:05:00+08:00",
        )
    except ValueError as exc:
        assert "model version" in str(exc)
    else:
        raise AssertionError("IC decision without explicit model versions was accepted")
