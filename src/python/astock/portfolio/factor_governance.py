"""Governed factor classifications and stress scenarios for portfolio risk."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class FactorRiskContext:
    """Source- and version-bound factor inputs accepted by the risk engine.

    Factor exposures are research classifications, not estimates inferred from
    a return series.  This object deliberately requires the accountable owner,
    source references, model/taxonomy version, and an expiry date.
    """

    taxonomy_version: str
    approved_by: str
    approved_at: str
    valid_until: str
    classifications: dict[str, dict[str, Any]]
    stress_scenarios: dict[str, dict[str, float]]

    def to_risk_inputs(self) -> dict[str, Any]:
        return {
            "factor_exposures": {
                code: dict(item["factor_exposures"])
                for code, item in self.classifications.items()
            },
            "stress_scenarios": {
                name: dict(shocks) for name, shocks in self.stress_scenarios.items()
            },
            "factor_governance": {
                "schema_version": "portfolio-factor-risk-context.v1",
                "taxonomy_version": self.taxonomy_version,
                "approved_by": self.approved_by,
                "approved_at": self.approved_at,
                "valid_until": self.valid_until,
                "classification_sources": {
                    code: list(item["source_refs"])
                    for code, item in self.classifications.items()
                },
            },
        }


def validate_factor_risk_context(
    context: Mapping[str, Any],
    *,
    required_codes: Sequence[str],
    now: datetime | None = None,
) -> FactorRiskContext:
    """Validate a factor-risk context before it may reach portfolio controls."""
    if str(context.get("schema_version") or "") != "portfolio-factor-risk-context.v1":
        raise ValueError("factor risk context must use portfolio-factor-risk-context.v1")
    taxonomy_version = _required_text(context, "taxonomy_version")
    approved_by = _required_text(context, "approved_by")
    approved_at = _required_timestamp(context, "approved_at")
    valid_until = _required_timestamp(context, "valid_until")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if valid_until.astimezone(timezone.utc) < current:
        raise ValueError("factor risk context has expired and cannot be used for a new risk decision")
    if approved_at > valid_until:
        raise ValueError("factor risk context valid_until must not precede approved_at")
    classifications_raw = context.get("classifications")
    if not isinstance(classifications_raw, Mapping):
        raise ValueError("factor risk context requires classifications by code")
    codes = tuple(dict.fromkeys(_normalize_code(code) for code in required_codes))
    classifications: dict[str, dict[str, Any]] = {}
    for code in codes:
        payload = classifications_raw.get(code)
        if not isinstance(payload, Mapping):
            raise ValueError(f"factor risk context lacks a classification for {code}")
        classifications[code] = _validate_classification(code, payload, taxonomy_version)
    scenarios_raw = context.get("stress_scenarios")
    if not isinstance(scenarios_raw, Mapping) or not scenarios_raw:
        raise ValueError("factor risk context requires at least one approved stress scenario")
    known_factors = {
        factor
        for item in classifications.values()
        for factor in item["factor_exposures"]
    }
    scenarios: dict[str, dict[str, float]] = {}
    for raw_name, raw_scenario in scenarios_raw.items():
        name = str(raw_name).strip()
        if not name or not isinstance(raw_scenario, Mapping):
            raise ValueError("stress scenarios require named object records")
        scenarios[name] = _validate_scenario(name, raw_scenario, known_factors)
    return FactorRiskContext(
        taxonomy_version=taxonomy_version,
        approved_by=approved_by,
        approved_at=approved_at.isoformat(),
        valid_until=valid_until.isoformat(),
        classifications=classifications,
        stress_scenarios=scenarios,
    )


def _validate_classification(
    code: str, payload: Mapping[str, Any], taxonomy_version: str
) -> dict[str, Any]:
    if str(payload.get("taxonomy_version") or "").strip() != taxonomy_version:
        raise ValueError(f"factor classification {code} taxonomy_version does not match context")
    _required_timestamp(payload, "as_of")
    source_refs = _string_items(payload.get("source_refs"))
    if not source_refs:
        raise ValueError(f"factor classification {code} requires source_refs")
    raw_exposures = payload.get("factor_exposures")
    if not isinstance(raw_exposures, Mapping) or not raw_exposures:
        raise ValueError(f"factor classification {code} requires non-empty factor_exposures")
    exposures: dict[str, float] = {}
    for raw_factor, raw_exposure in raw_exposures.items():
        factor = str(raw_factor).strip()
        if not factor:
            raise ValueError(f"factor classification {code} has an empty factor name")
        exposure = _bounded_number(raw_exposure, f"factor classification {code} {factor}")
        exposures[factor] = exposure
    return {
        "taxonomy_version": taxonomy_version,
        "as_of": str(payload["as_of"]),
        "source_refs": source_refs,
        "factor_exposures": dict(sorted(exposures.items())),
    }


def _validate_scenario(
    name: str, payload: Mapping[str, Any], known_factors: set[str]
) -> dict[str, float]:
    _required_timestamp(payload, "as_of")
    if not _string_items(payload.get("source_refs")):
        raise ValueError(f"stress scenario {name} requires source_refs")
    shocks = payload.get("shocks")
    if not isinstance(shocks, Mapping) or not shocks:
        raise ValueError(f"stress scenario {name} requires non-empty shocks")
    validated: dict[str, float] = {}
    for raw_factor, raw_shock in shocks.items():
        factor = str(raw_factor).strip()
        if factor not in known_factors:
            raise ValueError(f"stress scenario {name} references unclassified factor {factor!r}")
        shock = _bounded_number(raw_shock, f"stress scenario {name} {factor}")
        if shock >= 0:
            raise ValueError(f"stress scenario {name} shock for {factor} must be negative")
        validated[factor] = shock
    return dict(sorted(validated.items()))


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise ValueError(f"factor risk context requires {key}")
    return value


def _required_timestamp(payload: Mapping[str, Any], key: str) -> datetime:
    value = str(payload.get(key) or "").strip()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{key} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{key} must include a timezone offset")
    return parsed


def _bounded_number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite number between -1 and 1") from exc
    if not math.isfinite(number) or number < -1 or number > 1:
        raise ValueError(f"{label} must be a finite number between -1 and 1")
    return number


def _normalize_code(value: Any) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    if len(digits) != 6:
        raise ValueError(f"invalid A-share code: {value!r}")
    return digits


def _string_items(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in (str(item).strip() for item in value) if item)
