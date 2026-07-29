"""Internal compliance controls for research-only paper-desk candidates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Sequence


class ComplianceStatus(StrEnum):
    PASS = "pass"
    CONDITIONAL = "conditional"
    VETO = "veto"


@dataclass(frozen=True)
class ComplianceAssessment:
    status: ComplianceStatus
    findings: tuple[str, ...]
    required_remediation: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-compliance.v1",
            "status": self.status.value,
            "findings": list(self.findings),
            "required_remediation": list(self.required_remediation),
        }


def assess_candidate_compliance(
    candidate: Mapping[str, Any], *, restricted_targets: Sequence[str] = ()
) -> ComplianceAssessment:
    """Apply internal research-boundary and restricted-information controls.

    This does not determine legal compliance. It enforces the desk's own rule:
    unknown disclosure/control state is not an approval state.
    """
    compliance = candidate.get("compliance")
    if not isinstance(compliance, Mapping):
        return ComplianceAssessment(
            ComplianceStatus.CONDITIONAL,
            ("Candidate lacks a structured compliance assessment.",),
            ("Provide research-only, conflict, restricted-information, and suitability declarations.",),
        )
    targets = {str(item).strip() for item in candidate.get("targets", ()) if str(item).strip()}
    restricted = {str(item).strip() for item in restricted_targets if str(item).strip()}
    findings: list[str] = []
    remediation: list[str] = []
    veto = False
    if targets.intersection(restricted) or bool(compliance.get("restricted")):
        findings.append("Candidate is on a restricted list or marked restricted.")
        veto = True
    if bool(compliance.get("mnpi_or_inside_information")):
        findings.append("Candidate is marked as involving material non-public or inside information.")
        veto = True
    if compliance.get("restricted_list_current") is False:
        remediation.append(
            "Refresh the externally sourced restricted list and record a current compliance review."
        )
    if not bool(compliance.get("research_only_disclosure")):
        remediation.append("Disclose that output is research and paper-plan support only, not order execution.")
    if not bool(compliance.get("no_execution_instruction")):
        remediation.append("Remove execution, routing, or rule-evasion instructions.")
    if not bool(compliance.get("conflicts_disclosed")):
        remediation.append("Disclose or clear conflicts of interest.")
    if not bool(compliance.get("suitability_disclosure")):
        remediation.append("Provide the required risk and suitability disclosure.")
    claims = compliance.get("prohibited_claims", ())
    if isinstance(claims, Sequence) and not isinstance(claims, str) and any(str(item).strip() for item in claims):
        findings.append("Candidate declares prohibited or guaranteed-return claims.")
        veto = True
    if veto:
        return ComplianceAssessment(ComplianceStatus.VETO, tuple(findings), tuple(remediation))
    if remediation:
        return ComplianceAssessment(ComplianceStatus.CONDITIONAL, tuple(findings), tuple(remediation))
    return ComplianceAssessment(ComplianceStatus.PASS, tuple(findings), ())
