from astock.strategy.equity import (
    AShareFactorTiltConfig,
    build_ashare_factor_tilt_proposal,
    build_earnings_event_repricing_proposal,
)


def _security(code: str, industry: str, score: float) -> dict[str, object]:
    return {
        "code": code,
        "industry": industry,
        "quality_score": score,
        "value_score": score,
        "momentum_score": score,
        "investment_score": score,
        "tradable": True,
        "halted": False,
        "limit_up_locked": False,
        "limit_down_locked": False,
        "risk_warning": False,
        "delisting_risk": False,
        "average_daily_turnover": 100_000_000,
        "listing_days": 500,
        "source_ref": "fixture:security-status",
        "exchange": "szse",
        "market": "ashare",
        "trading_state_as_of": "2026-08-14T06:50:00+00:00",
    }


def test_factor_tilt_caps_industry_and_vetoes_locked_security() -> None:
    locked = _security("000003", "bank", 99)
    locked["limit_up_locked"] = True
    result = build_ashare_factor_tilt_proposal(
        [_security("000001", "bank", 4), _security("000002", "bank", 3), locked],
        config=AShareFactorTiltConfig(
            max_positions=3, max_position_weight=0.20, max_industry_weight=0.20
        ),
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:universe"],
    )

    assert [item["code"] for item in result["targets"]] == ["000001"]
    assert "price-limit locked" in result["hard_vetoes"][0]["reason"]
    assert result["no_order_execution"] is True


def test_earnings_event_requires_fresh_timestamped_public_announcement() -> None:
    event = _security("000001", "bank", 1)
    event.update(
        {
            "announcement_id": "cninfo:1",
            "published_at": "2026-08-13T10:00:00+00:00",
            "available_at": "2026-08-13T10:01:00+00:00",
            "surprise_score": 1.2,
        }
    )
    stale = _security("000002", "bank", 1)
    stale.update(
        {
            "announcement_id": "cninfo:2",
            "published_at": "2026-07-01T10:00:00+00:00",
            "available_at": "2026-07-01T10:01:00+00:00",
            "surprise_score": 2.0,
        }
    )
    result = build_earnings_event_repricing_proposal(
        [event, stale],
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:announcements"],
    )

    assert [item["code"] for item in result["targets"]] == ["000001"]
    assert "outside the configured" in result["hard_vetoes"][0]["reason"]


def test_earnings_event_vetoes_missing_publish_timestamp() -> None:
    event = _security("000001", "bank", 1)
    event.update({"announcement_id": "cninfo:1", "surprise_score": 1.2})
    result = build_earnings_event_repricing_proposal(
        [event],
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:announcements"],
    )
    assert result["targets"] == []
    assert "missing published_at" in result["hard_vetoes"][0]["reason"]


def test_factor_default_keeps_unallocated_cash_for_other_sleeves() -> None:
    result = build_ashare_factor_tilt_proposal(
        [
            _security(f"0000{index:02d}", f"industry-{index}", 1)
            for index in range(1, 21)
        ],
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:universe"],
    )
    assert result["total_target_weight"] == 0.4


def test_factor_vetoes_unverified_market_identity_and_stale_trading_state() -> None:
    foreign = _security("AAPL", "technology", 2)
    foreign["exchange"] = "nasdaq"
    stale = _security("000002", "bank", 2)
    stale["trading_state_as_of"] = "2026-08-12T06:00:00+00:00"

    result = build_ashare_factor_tilt_proposal(
        [foreign, stale],
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:universe"],
    )

    assert result["targets"] == []
    reasons = " ".join(item["reason"] for item in result["hard_vetoes"])
    assert "A-share exchange and market identity" in reasons
    assert "trading-state timestamp is stale" in reasons


def test_event_rejects_same_day_post_cutoff_and_naive_announcement_timestamps() -> None:
    post_cutoff = _security("000001", "bank", 1)
    post_cutoff.update(
        {
            "announcement_id": "cninfo:after-close",
            "published_at": "2026-08-14T08:00:00+00:00",
            "available_at": "2026-08-14T08:01:00+00:00",
            "surprise_score": 2.0,
        }
    )
    naive = _security("000002", "bank", 1)
    naive.update(
        {
            "announcement_id": "cninfo:naive",
            "published_at": "2026-08-14T06:00:00",
            "available_at": "2026-08-14T06:01:00",
            "surprise_score": 2.0,
        }
    )

    result = build_earnings_event_repricing_proposal(
        [post_cutoff, naive],
        as_of="2026-08-14T07:00:00+00:00",
        source_refs=["fixture:announcements"],
    )

    assert result["targets"] == []
    reasons = " ".join(item["reason"] for item in result["hard_vetoes"])
    assert "outside the configured public-information window" in reasons
    assert "timezone-aware" in reasons
