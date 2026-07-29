"""Tests for internal desk compliance controls."""

from astock.market_desk import ComplianceStatus, assess_candidate_compliance


def _candidate() -> dict[str, object]:
    return {
        "targets": ["600460"],
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


def test_restricted_or_inside_information_is_a_binding_veto() -> None:
    candidate = _candidate()
    candidate["compliance"]["mnpi_or_inside_information"] = True  # type: ignore[index]

    result = assess_candidate_compliance(candidate, restricted_targets=["600460"])

    assert result.status == ComplianceStatus.VETO
    assert len(result.findings) == 2


def test_missing_disclosures_are_conditional_not_pass() -> None:
    candidate = _candidate()
    candidate["compliance"]["conflicts_disclosed"] = False  # type: ignore[index]

    result = assess_candidate_compliance(candidate)

    assert result.status == ComplianceStatus.CONDITIONAL
    assert "conflicts" in result.required_remediation[0].lower()
