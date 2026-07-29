from astock.portfolio.risk_manager import RiskLimits, RiskManager


def test_risk_budget_blocks_excess_sector_and_planned_loss():
    manager = RiskManager(
        RiskLimits(
            max_sector_exposure=0.4,
            max_portfolio_risk=0.03,
            min_cash_ratio=0.1,
        )
    )
    report = manager.assess_risk_budget(
        positions=[
            {
                "code": "600460",
                "market_value": 90_000,
                "stop_distance_pct": 0.08,
                "sector": "Semiconductor",
                "theme": "Chip",
            }
        ],
        cash=10_000,
    )

    assert report.planned_loss_ratio == 0.072
    assert any("Sector Semiconductor" in blocker for blocker in report.blockers)
    assert any("Planned-loss budget" in blocker for blocker in report.blockers)


def test_risk_budget_warns_when_stop_distance_is_missing():
    report = RiskManager().assess_risk_budget(
        positions=[{"code": "000001", "market_value": 10_000}],
        cash=90_000,
    )

    assert report.warnings
    assert report.planned_loss == 800


def test_risk_budget_blocks_single_name_exposure():
    report = RiskManager().assess_risk_budget(
        positions=[{"code": "600460", "market_value": 30_000, "stop_distance_pct": 0.02}],
        cash=70_000,
    )

    assert any("Position 600460" in blocker for blocker in report.blockers)


def test_position_limit_does_not_double_count_cash_reallocation():
    passed, _ = RiskManager().check_position_limit(
        current_value=100_000,
        position_value=0,
        new_position_value=20_000,
    )

    assert passed


def test_risk_budget_blocks_position_count_and_theme_exposure():
    manager = RiskManager(
        RiskLimits(max_positions=2, max_theme_exposure=0.4, max_portfolio_risk=0.2)
    )
    report = manager.assess_risk_budget(
        positions=[
            {"code": "000001", "market_value": 20_000, "stop_distance_pct": 0.02, "theme": "AI"},
            {"code": "000002", "market_value": 20_000, "stop_distance_pct": 0.02, "theme": "AI"},
            {"code": "000003", "market_value": 20_000, "stop_distance_pct": 0.02, "theme": "AI"},
        ],
        cash=40_000,
    )

    assert any("Active positions" in blocker for blocker in report.blockers)
    assert any("Theme AI" in blocker for blocker in report.blockers)


def test_short_horizon_risk_requires_gap_and_limit_down_stress():
    report = RiskManager().assess_risk_budget(
        positions=[
            {
                "code": "600460",
                "market_value": 10_000,
                "stop_distance_pct": 0.03,
                "horizon": "short_term",
            }
        ],
        cash=90_000,
    )

    assert any("requires overnight and limit-down stress" in blocker for blocker in report.blockers)


def test_risk_budget_blocks_strategy_sleeve_exposure_independently_of_single_name_limits():
    report = RiskManager(
        RiskLimits(
            max_position_size=0.2,
            max_portfolio_risk=0.2,
            max_horizon_exposure={"short_term": 0.25, "swing": 0.30, "long_term": 0.50},
        )
    ).assess_risk_budget(
        positions=[
            {
                "code": "300001",
                "market_value": 15_000,
                "stop_distance_pct": 0.02,
                "horizon": "short_term",
                "overnight_stress_pct": 0.04,
                "limit_down_stress_pct": 0.10,
            },
            {
                "code": "300002",
                "market_value": 15_000,
                "stop_distance_pct": 0.02,
                "horizon": "short_term",
                "overnight_stress_pct": 0.04,
                "limit_down_stress_pct": 0.10,
            },
        ],
        cash=70_000,
    )

    assert report.horizon_exposure == {"short_term": 0.3}
    assert any("short_term sleeve exposure" in blocker for blocker in report.blockers)


def test_structural_risk_blocks_missing_inputs_and_concentration():
    report = RiskManager(
        RiskLimits(max_factor_exposure=0.4, max_liquidity_participation=0.1)
    ).assess_portfolio_structure(
        positions=[
            {
                "code": "600460",
                "market_value": 60_000,
                "factor_exposures": {"growth": 1.0, "semiconductor": 0.8},
                "average_daily_turnover": 200_000,
                "planned_exit_value": 30_000,
            },
            {
                "code": "688001",
                "market_value": 20_000,
                "factor_exposures": {"growth": 0.8, "semiconductor": 0.7},
                "average_daily_turnover": 1_000_000,
            },
        ],
        cash=20_000,
        correlations={"600460|688001": 0.9},
        stress_scenarios={"growth_down": {"growth": -0.2}},
    )

    assert report.factor_exposure["growth"] == 0.76
    assert report.liquidity[0]["participation_ratio"] == 0.15
    assert report.scenario_losses["growth_down"] == 0.152
    assert any("Factor growth" in blocker for blocker in report.blockers)
    assert any("Pair 600460|688001" in blocker for blocker in report.blockers)
    assert any("planned exit" in blocker for blocker in report.blockers)
    assert any("Stress scenario growth_down" in blocker for blocker in report.blockers)


def test_structural_risk_treats_missing_inputs_as_blockers_not_zero():
    report = RiskManager().assess_portfolio_structure(
        positions=[{"code": "000001", "market_value": 10_000}],
        cash=90_000,
    )

    assert any("factor exposures" in blocker for blocker in report.blockers)
    assert any("average daily turnover" in blocker for blocker in report.blockers)
    assert any("stress scenario" in blocker.lower() for blocker in report.blockers)
