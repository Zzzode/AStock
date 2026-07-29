"""Factor-taxonomy and stress-scenario governance tests."""

from datetime import datetime, timezone

import pytest

from astock.portfolio import validate_factor_risk_context


def _context() -> dict[str, object]:
    return {
        "schema_version": "portfolio-factor-risk-context.v1",
        "taxonomy_version": "factor-taxonomy.v1",
        "approved_by": "quant-risk-modeler",
        "approved_at": "2026-07-28T15:00:00+08:00",
        "valid_until": "2026-08-28T15:00:00+08:00",
        "classifications": {
            "600460": {
                "taxonomy_version": "factor-taxonomy.v1",
                "as_of": "2026-07-28T15:00:00+08:00",
                "source_refs": ["risk-model:factor-taxonomy.v1"],
                "factor_exposures": {"growth": 0.8},
            }
        },
        "stress_scenarios": {
            "growth_down": {
                "as_of": "2026-07-28T15:00:00+08:00",
                "source_refs": ["risk-scenario:growth-down.v1"],
                "shocks": {"growth": -0.2},
            }
        },
    }


def test_context_keeps_only_source_bound_classifications_and_scenarios() -> None:
    result = validate_factor_risk_context(
        _context(),
        required_codes=["600460"],
        now=datetime(2026, 7, 28, 7, 0, tzinfo=timezone.utc),
    )

    risk_inputs = result.to_risk_inputs()
    assert risk_inputs["factor_exposures"]["600460"] == {"growth": 0.8}
    assert risk_inputs["stress_scenarios"]["growth_down"] == {"growth": -0.2}


def test_context_rejects_unclassified_scenario_factor() -> None:
    context = _context()
    context["stress_scenarios"]["growth_down"]["shocks"] = {"rate": -0.2}

    with pytest.raises(ValueError, match="unclassified factor"):
        validate_factor_risk_context(context, required_codes=["600460"])
