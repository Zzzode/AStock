from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from astock.strategy import (
    CTAStrategyConfig,
    FuturesExecutionAssumptions,
    FuturesInstrumentSpec,
)
from astock.strategy.cta import (
    _build_domestic_futures_cta_proposal,
    _DomesticFuturesCTABacktestEngine,
)


def _frame(
    *,
    direction: float = 1.0,
    periods: int = 190,
    start: float = 100.0,
    days_to_expiry: int = 90,
    active_contract: str = "UP0",
) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    shocks = np.sin(np.arange(periods) / 7) * 0.001
    returns = direction * 0.002 + shocks
    settlement = start * np.exp(np.cumsum(returns))
    return pd.DataFrame(
        {
            "date": dates,
            "open": settlement * 0.999,
            "close": settlement,
            "settlement": settlement,
            "volume": [100_000] * periods,
            "open_interest": [200_000] * periods,
            "tradable": [True] * periods,
            "execution_status": ["tradable"] * periods,
            "days_to_expiry": [days_to_expiry] * periods,
            "active_contract": [active_contract] * periods,
            "contract_multiplier": [10.0] * periods,
            "initial_margin_rate": [0.12] * periods,
            "maintenance_margin_rate": [0.10] * periods,
            "position_limit": [500] * periods,
            "contract_facts_as_of": [timestamp.date().isoformat() for timestamp in dates],
            "contract_source_ref": ["fixture:dated-contract-facts"] * periods,
        }
    )


def _spec(instrument_id: str, group: str) -> FuturesInstrumentSpec:
    return FuturesInstrumentSpec(
        instrument_id=instrument_id,
        active_contract=f"{instrument_id}0",
        exchange="shfe",
        group=group,
        currency="CNY",
        multiplier=10.0,
        tick_size=1.0,
        initial_margin_rate=0.12,
        maintenance_margin_rate=0.10,
        as_of="2025-10-01",
        source_ref="fixture:contract-master",
        contract_lifecycle_coverage="verified",
    )


def _config(**updates: object) -> CTAStrategyConfig:
    values: dict[str, object] = {
        "minimum_history": 160,
        "minimum_daily_volume": 1,
        "minimum_open_interest": 1,
        "minimum_days_to_expiry": 10,
        "annual_target_volatility": 0.10,
        "max_margin_fraction": 0.25,
        "rebalance_buffer_contracts": 0,
    }
    values.update(updates)
    return CTAStrategyConfig(**values)


def test_cta_proposal_generates_signed_targets_and_respects_margin_cap() -> None:
    market_data = {
        "UP": _frame(direction=1.0, active_contract="UP0"),
        "DOWN": _frame(direction=-1.0, active_contract="DOWN0"),
    }
    instruments = {"UP": _spec("UP", "metals"), "DOWN": _spec("DOWN", "agriculture")}

    result = _build_domestic_futures_cta_proposal(
        market_data,
        instruments,
        capital=1_000_000,
        config=_config(),
        source_archive_ids=["sha256:fixture"],
    )

    targets = {target["instrument_id"]: target for target in result["targets"]}
    assert targets["UP"]["target_contracts"] > 0
    assert targets["DOWN"]["target_contracts"] < 0
    assert result["gross_margin"] <= 250_000 + 1e-6
    assert result["capital"] == 1_000_000
    assert result["no_order_execution"] is True


def test_cta_proposal_blocks_delivery_buffer_and_missing_expiry_facts() -> None:
    market_data = {"UP": _frame(direction=1.0, days_to_expiry=5)}
    result = _build_domestic_futures_cta_proposal(
        market_data,
        {"UP": _spec("UP", "metals")},
        capital=1_000_000,
        config=_config(),
    )

    assert result["targets"] == []
    assert result["data_quality"] == "blocked"
    assert "delivery/roll safety buffer" in " ".join(result["warnings"])


def test_cta_backtest_uses_next_session_and_marks_variation_margin() -> None:
    frame = _frame(direction=1.0, periods=175)
    engine = _DomesticFuturesCTABacktestEngine(
        _config(),
        FuturesExecutionAssumptions(
            slippage_bps=0.0,
            commission_per_contract=0.0,
            rebalance_buffer_contracts=0,
            max_volume_participation=0.10,
        ),
    )

    result = engine.run(
        {"UP": frame},
        {"UP": _spec("UP", "metals")},
        initial_capital=1_000_000,
        source_archive_ids=["sha256:fixture-contract-history"],
    ).to_dict()

    assert result["schema_version"] == "domestic_futures_cta_backtest.v1"
    assert result["trades"]
    first_trade = result["trades"][0]
    assert first_trade["date"] > frame.iloc[159]["date"].date().isoformat()
    assert result["equity_curve"][-1]["equity"] > 0
    assert result["formal_decision_eligible"] is False


def test_cta_input_rejects_undeclared_contract_facts() -> None:
    with pytest.raises(ValueError, match="initial_margin_rate"):
        FuturesInstrumentSpec.from_mapping(
            {
                "instrument_id": "UP",
                "active_contract": "UP0",
                "exchange": "shfe",
                "group": "metals",
                "currency": "CNY",
                "multiplier": 10,
                "tick_size": 1,
                "maintenance_margin_rate": 0.1,
                "as_of": "2025-10-01",
                "source_ref": "fixture",
            }
        )


def test_cta_proposal_refuses_unspecified_contract_lifecycle_coverage() -> None:
    raw = _spec("UP", "metals").to_dict()
    raw.pop("contract_lifecycle_coverage")
    result = _build_domestic_futures_cta_proposal(
        {"UP": _frame(direction=1.0)},
        {"UP": raw},
        capital=1_000_000,
        config=_config(),
    )
    assert result["targets"] == []
    assert "contract lifecycle is not verified" in result["warnings"][0]


def test_cta_backtest_blocks_unevidenced_historical_contract_data() -> None:
    with pytest.raises(ValueError, match="immutable sha256 source archive"):
        _DomesticFuturesCTABacktestEngine(_config()).run(
            {"UP": _frame(direction=1.0, periods=175)},
            {"UP": _spec("UP", "metals")},
            initial_capital=1_000_000,
        )


def test_cta_backtest_books_fill_to_settlement_slippage() -> None:
    frame = _frame(direction=1.0, periods=175)
    zero_slippage = _DomesticFuturesCTABacktestEngine(
        _config(),
        FuturesExecutionAssumptions(
            slippage_bps=0.0,
            commission_per_contract=0.0,
            rebalance_buffer_contracts=0,
            max_volume_participation=0.10,
        ),
    ).run(
        {"UP": frame},
        {"UP": _spec("UP", "metals")},
        initial_capital=1_000_000,
        source_archive_ids=["sha256:fixture-contract-history"],
    ).to_dict()
    expensive_slippage = _DomesticFuturesCTABacktestEngine(
        _config(),
        FuturesExecutionAssumptions(
            slippage_bps=100.0,
            commission_per_contract=0.0,
            rebalance_buffer_contracts=0,
            max_volume_participation=0.10,
        ),
    ).run(
        {"UP": frame},
        {"UP": _spec("UP", "metals")},
        initial_capital=1_000_000,
        source_archive_ids=["sha256:fixture-contract-history"],
    ).to_dict()

    assert zero_slippage["trades"]
    assert zero_slippage["trades"][0]["fill_to_settlement_pnl"] > expensive_slippage["trades"][0]["fill_to_settlement_pnl"]
    assert zero_slippage["final_equity"] > expensive_slippage["final_equity"]


def test_cta_backtest_requires_and_uses_dated_actual_contract_roll_facts() -> None:
    frame = _frame(direction=1.0, periods=175, active_contract="UP0")
    roll_index = 165
    frame.loc[roll_index:, "active_contract"] = "UP1"
    frame["roll_from_contract"] = None
    frame["roll_exit_price"] = None
    frame["roll_entry_price"] = None
    frame["roll_source_ref"] = None
    frame.loc[roll_index, "roll_from_contract"] = "UP0"
    frame.loc[roll_index, "roll_exit_price"] = float(frame.loc[roll_index - 1, "settlement"])
    frame.loc[roll_index, "roll_entry_price"] = float(frame.loc[roll_index, "open"])
    frame.loc[roll_index, "roll_source_ref"] = "fixture:verified-roll"
    raw_spec = _spec("UP", "metals").to_dict()
    raw_spec["active_contract"] = "UP1"

    result = _DomesticFuturesCTABacktestEngine(
        _config(),
        FuturesExecutionAssumptions(rebalance_buffer_contracts=0, max_volume_participation=0.10),
    ).run(
        {"UP": frame},
        {"UP": raw_spec},
        initial_capital=1_000_000,
        source_archive_ids=["sha256:fixture-contract-history"],
    ).to_dict()

    assert result["roll_events"]
    roll = result["roll_events"][0]
    assert roll["from_contract"] == "UP0"
    assert roll["to_contract"] == "UP1"
    assert roll["roll_source_ref"] == "fixture:verified-roll"
    assert roll["status"] == "verified_actual_contract_roll"


def test_cta_input_rejects_zero_margin_or_non_date_as_of() -> None:
    raw = _spec("UP", "metals").to_dict()
    raw["initial_margin_rate"] = 0
    with pytest.raises(ValueError, match="positive finite fraction"):
        FuturesInstrumentSpec.from_mapping(raw)

    raw = _spec("UP", "metals").to_dict()
    raw["as_of"] = "not-a-date"
    with pytest.raises(ValueError, match="ISO date"):
        FuturesInstrumentSpec.from_mapping(raw)
