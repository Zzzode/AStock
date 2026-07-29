"""Tests for the bounded rotation flow-persistence proxy."""

from astock import capabilities


def _rotation() -> dict[str, object]:
    return {
        "rankings": {
            "industries": [
                {
                    "name": "创新药",
                    "turnover_attention_percentile": 0.95,
                    "multi_horizon_return_pct": {"5d": 4.0},
                },
                {
                    "name": "电力",
                    "turnover_attention_percentile": 0.5,
                    "multi_horizon_return_pct": {"5d": 1.0},
                },
            ],
            "concepts": [],
        }
    }


def test_proxy_requires_repeated_source_labelled_flow_observations() -> None:
    observations = [
        {
            "subject_type": "industry",
            "name": "创新药",
            "source": "flow-source",
            "quality": "full",
            "observed_at": f"2026-07-{day:02d}T15:00:00+08:00",
            "net_flow": 100.0,
        }
        for day in range(1, 6)
    ] + [
        {
            "subject_type": "industry",
            "name": "电力",
            "source": "flow-source",
            "quality": "full",
            "observed_at": f"2026-07-{day:02d}T15:00:00+08:00",
            "net_flow": 10.0,
        }
        for day in range(1, 6)
    ]

    result = capabilities.build_market_rotation_crowding_proxy_v1(
        _rotation(), observations
    )

    assert result["status"] == "available"
    assert result["coverage_ratio"] == 1.0
    assert result["records"][0]["flow_attention_risk"] is True
    assert result["decision_weight"] == 0


def test_proxy_remains_partial_without_full_cross_section_observation_history() -> None:
    result = capabilities.build_market_rotation_crowding_proxy_v1(
        _rotation(),
        [
            {
                "subject_type": "industry",
                "name": "创新药",
                "source": "flow-source",
                "quality": "full",
                "observed_at": "2026-07-01T15:00:00+08:00",
                "net_flow": 100.0,
            }
        ],
    )

    assert result["status"] == "partial"
    assert result["covered_count"] == 0
