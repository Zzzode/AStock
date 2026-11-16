"""Domestic-futures CTA proposal and paper-replay engine.

This is a low-frequency research implementation of a multi-horizon
time-series-momentum sleeve.  It is intentionally not an order-management
system: it produces signed paper targets and replays settlement-to-settlement
P&L under explicit margin, roll and liquidity assumptions.

The module does *not* claim to be a global CTA.  Its input universe is a
dated, source-labelled set of domestic futures contracts.  The same contracts
and rules are used in generation and replay so that a result can be audited.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .models import (
    CTAStrategyConfig,
    FuturesInstrumentSpec,
    FuturesTarget,
    StrategyProposal,
)

_TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class FuturesExecutionAssumptions:
    """Assumptions for research-only daily futures replay."""

    settlement_timing: str = "daily_settlement_mark_to_market"
    signal_timing: str = "close_to_next_session"
    slippage_bps: float = 2.0
    commission_per_contract: float = 0.0
    max_volume_participation: float = 0.02
    rebalance_buffer_contracts: int = 1
    maintenance_margin_buffer_fraction: float = 0.10
    liquidation_policy: str = "de_risk_on_next_available_session"

    def __post_init__(self) -> None:
        if self.slippage_bps < 0 or self.commission_per_contract < 0:
            raise ValueError("futures execution costs cannot be negative")
        if not 0 < self.max_volume_participation <= 1:
            raise ValueError("max_volume_participation must be in (0, 1]")
        if self.rebalance_buffer_contracts < 0:
            raise ValueError("rebalance_buffer_contracts cannot be negative")
        if not 0 <= self.maintenance_margin_buffer_fraction < 1:
            raise ValueError("maintenance_margin_buffer_fraction must be in [0, 1)")

    def to_dict(self) -> dict[str, Any]:
        return {
            "settlement_timing": self.settlement_timing,
            "signal_timing": self.signal_timing,
            "slippage_bps": self.slippage_bps,
            "commission_per_contract": self.commission_per_contract,
            "max_volume_participation": self.max_volume_participation,
            "rebalance_buffer_contracts": self.rebalance_buffer_contracts,
            "maintenance_margin_buffer_fraction": self.maintenance_margin_buffer_fraction,
            "liquidation_policy": self.liquidation_policy,
        }


@dataclass(frozen=True)
class FuturesBacktestResult:
    """A deterministic daily paper replay with variation-margin accounting."""

    strategy_id: str
    strategy_version: str
    initial_capital: float
    final_equity: float
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    execution_assumptions: FuturesExecutionAssumptions
    equity_curve: list[dict[str, Any]]
    trades: list[dict[str, Any]]
    roll_events: list[dict[str, Any]]
    warnings: list[str]
    data_assurance: dict[str, Any]
    strategy_implementation_fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "domestic_futures_cta_backtest.v1",
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "initial_capital": self.initial_capital,
            "final_equity": self.final_equity,
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "annualized_volatility": self.annualized_volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "execution_assumptions": self.execution_assumptions.to_dict(),
            "equity_curve": self.equity_curve,
            "trades": self.trades,
            "roll_events": self.roll_events,
            "warnings": self.warnings,
            "data_assurance": self.data_assurance,
            "strategy_implementation_fingerprint": self.strategy_implementation_fingerprint,
            "research_only": True,
            "no_order_execution": True,
            "formal_decision_eligible": False,
        }


class _DomesticFuturesCTAStrategy:
    """Generate signed targets from diversified futures settlement histories."""

    def __init__(self, config: CTAStrategyConfig | None = None) -> None:
        self.config = config or CTAStrategyConfig()

    def generate_proposal(
        self,
        market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]]],
        instruments: Mapping[str, FuturesInstrumentSpec | Mapping[str, Any]],
        *,
        capital: float,
        as_of: str | None = None,
        previous_contracts: Mapping[str, int] | None = None,
        source_archive_ids: Sequence[str] = (),
        enforce_current_spec_contract: bool = True,
    ) -> StrategyProposal:
        """Generate a next-session paper target with risk and margin caps.

        A target is refused for each instrument with missing dated contract
        facts, insufficient history, failed liquidity, or a roll/expiry block.
        Valid instruments are risk-balanced within group and portfolio caps.
        """

        if not math.isfinite(capital) or capital <= 0:
            raise ValueError("capital must be a positive finite number")
        normalized_specs = _normalize_specs(instruments)
        frames = _normalize_market_data(market_data, normalized_specs)
        common_as_of = pd.Timestamp(as_of).normalize() if as_of else _latest_common_as_of(frames)
        if pd.isna(common_as_of):
            raise ValueError("CTA proposal cannot determine an as-of date")
        previous = {str(key): int(value) for key, value in (previous_contracts or {}).items()}
        candidates: list[dict[str, Any]] = []
        warnings: list[str] = []
        errors: list[str] = []
        for instrument_id, spec in normalized_specs.items():
            frame = frames[instrument_id]
            candidate, issue = _instrument_candidate(
                frame,
                spec,
                self.config,
                common_as_of,
                previous.get(instrument_id, 0),
                enforce_current_spec_contract=enforce_current_spec_contract,
            )
            if issue is not None:
                warnings.append(f"{instrument_id}: {issue}")
                continue
            assert candidate is not None
            candidates.append(candidate)
        if not candidates:
            errors.append("No futures instrument passed dated history, liquidity, expiry, and contract-fact gates.")
            return StrategyProposal(
                strategy_id=self.config.strategy_id,
                strategy_version=self.config.version,
                as_of=common_as_of.date().isoformat(),
                effective_session=None,
                targets=(),
                gross_notional=0.0,
                gross_margin=0.0,
                estimated_daily_volatility=0.0,
                data_quality="blocked",
                source_archive_ids=tuple(source_archive_ids),
                warnings=tuple(warnings),
                errors=tuple(errors),
            )
        targets = _size_candidates(candidates, capital, self.config)
        gross_notional = sum(abs(item.reference_price * item.target_contracts) * _spec_by_id(normalized_specs, item.instrument_id).multiplier for item in targets)
        gross_margin = sum(item.margin_required for item in targets)
        estimated_daily_volatility = _estimate_target_portfolio_daily_volatility(targets, normalized_specs)
        if gross_margin > capital * self.config.max_margin_fraction + 1e-7:
            errors.append("CTA sizing breached the configured margin cap after risk allocation.")
        return StrategyProposal(
            strategy_id=self.config.strategy_id,
            strategy_version=self.config.version,
            as_of=common_as_of.date().isoformat(),
            effective_session=_next_effective_session(frames, common_as_of),
            targets=tuple(targets),
            gross_notional=round(gross_notional, 8),
            gross_margin=round(gross_margin, 8),
            estimated_daily_volatility=round(estimated_daily_volatility, 10),
            data_quality="public_observation" if not source_archive_ids else "source_frozen_research",
            source_archive_ids=tuple(source_archive_ids),
            warnings=tuple(dict.fromkeys(warnings + _proposal_warnings(source_archive_ids))),
            errors=tuple(errors),
        )


class _DomesticFuturesCTABacktestEngine:
    """Settlement-to-settlement paper simulator for the CTA proposal contract."""

    def __init__(
        self,
        config: CTAStrategyConfig | None = None,
        execution: FuturesExecutionAssumptions | None = None,
    ) -> None:
        self.config = config or CTAStrategyConfig()
        self.execution = execution or FuturesExecutionAssumptions(
            slippage_bps=self.config.slippage_bps,
            commission_per_contract=self.config.commission_per_contract,
            rebalance_buffer_contracts=self.config.rebalance_buffer_contracts,
        )

    def run(
        self,
        market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]]],
        instruments: Mapping[str, FuturesInstrumentSpec | Mapping[str, Any]],
        *,
        initial_capital: float,
        source_archive_ids: Sequence[str] = (),
    ) -> FuturesBacktestResult:
        """Replay one continuous domestic-futures CTA paper portfolio.

        Signals use information through D close.  Target deltas become eligible
        on D+1 if that contract is tradable.  The engine marks all open
        positions at the daily settlement and applies variation P&L to cash.
        It does not fabricate a fill when a market is unavailable or locked.
        """

        if not math.isfinite(initial_capital) or initial_capital <= 0:
            raise ValueError("initial_capital must be a positive finite number")
        specs = _normalize_specs(instruments)
        frames = _normalize_market_data(market_data, specs)
        _validate_historical_replay_inputs(frames, specs, source_archive_ids)
        sessions = _union_sessions(frames)
        if len(sessions) < self.config.minimum_history + 2:
            raise ValueError("CTA replay lacks enough sessions for its declared minimum_history")
        strategy = _DomesticFuturesCTAStrategy(self.config)
        cash = float(initial_capital)
        positions = {instrument_id: 0 for instrument_id in specs}
        mark_prices: dict[str, float] = {}
        active_contracts: dict[str, str] = {}
        contract_facts: dict[str, dict[str, Any]] = {}
        pending_targets: Mapping[str, Mapping[str, Any]] | None = None
        trades: list[dict[str, Any]] = []
        roll_events: list[dict[str, Any]] = []
        warnings: list[str] = [
            "Signals observed at a session close are eligible no earlier than the next available session.",
            "P&L is marked from verified dated contract facts; public continuous histories are blocked from this replay.",
            "This is a research-only paper simulation and never routes broker orders.",
        ]
        curve: list[dict[str, Any]] = []
        for index, session in enumerate(sessions):
            cash = _settle_existing_positions(
                session,
                frames,
                positions,
                active_contracts,
                mark_prices,
                contract_facts,
                cash,
                roll_events,
            )
            if pending_targets is not None:
                cash = self._apply_pending_targets(
                    session,
                    pending_targets,
                    frames,
                    positions,
                    active_contracts,
                    contract_facts,
                    cash,
                    trades,
                    warnings,
                )
            active_data = {
                instrument_id: frame.loc[frame.index <= session].reset_index()
                for instrument_id, frame in frames.items()
            }
            if index >= self.config.minimum_history - 1:
                proposal = strategy.generate_proposal(
                    active_data,
                    specs,
                    capital=max(cash, 1.0),
                    as_of=session.date().isoformat(),
                    previous_contracts=positions,
                    source_archive_ids=source_archive_ids,
                    enforce_current_spec_contract=False,
                )
                pending_targets = {
                    target.instrument_id: {
                        "target_contracts": target.target_contracts,
                        "active_contract": target.active_contract,
                    }
                    for target in proposal.targets
                }
                if proposal.errors:
                    warnings.extend(proposal.errors)
            equity, margin, gross_notional = _account_state(
                positions, mark_prices, contract_facts, cash
            )
            if margin > equity * self.config.max_margin_fraction + 1e-7:
                warnings.append(f"{session.date()}: margin cap breach; next eligible target is forced to zero.")
                pending_targets = {
                    instrument_id: {"target_contracts": 0, "active_contract": active_contracts.get(instrument_id)}
                    for instrument_id in specs
                }
            if margin > equity * (1 - self.execution.maintenance_margin_buffer_fraction):
                warnings.append(f"{session.date()}: maintenance-buffer breach; next eligible target is forced to zero.")
                pending_targets = {
                    instrument_id: {"target_contracts": 0, "active_contract": active_contracts.get(instrument_id)}
                    for instrument_id in specs
                }
            curve.append(
                {
                    "date": session.date().isoformat(),
                    "equity": round(equity, 8),
                    "cash": round(cash, 8),
                    "margin_required": round(margin, 8),
                    "gross_notional": round(gross_notional, 8),
                    "positions": dict(positions),
                }
            )
        metrics = _performance_metrics(curve, initial_capital)
        return FuturesBacktestResult(
            strategy_id=self.config.strategy_id,
            strategy_version=self.config.version,
            initial_capital=initial_capital,
            final_equity=float(curve[-1]["equity"]),
            total_return=metrics["total_return"],
            annualized_return=metrics["annualized_return"],
            annualized_volatility=metrics["annualized_volatility"],
            sharpe_ratio=metrics["sharpe_ratio"],
            max_drawdown=metrics["max_drawdown"],
            execution_assumptions=self.execution,
            equity_curve=curve,
            trades=trades,
            roll_events=roll_events,
            warnings=list(dict.fromkeys(warnings + _proposal_warnings(source_archive_ids))),
            data_assurance={
                "status": "verified_contract_replay",
                "source_archive_ids": list(source_archive_ids),
                "limitations": [
                    "Dated contract, roll, margin, position-limit and execution-status facts were required, but the replay remains a research-only model rather than a fill-quality proof.",
                    "No order, broker instruction or performance claim is created by this deterministic paper replay.",
                ],
            },
            strategy_implementation_fingerprint=_implementation_fingerprint(),
        )

    def _apply_pending_targets(
        self,
        session: pd.Timestamp,
        targets: Mapping[str, Mapping[str, Any]],
        frames: Mapping[str, pd.DataFrame],
        positions: dict[str, int],
        active_contracts: Mapping[str, str],
        contract_facts: Mapping[str, Mapping[str, Any]],
        cash: float,
        trades: list[dict[str, Any]],
        warnings: list[str],
    ) -> float:
        for instrument_id, current in positions.items():
            raw_target = targets.get(instrument_id, {})
            if not isinstance(raw_target, Mapping):
                raise TypeError("pending CTA targets must retain contract identity")
            target = int(raw_target.get("target_contracts", 0))
            delta = target - current
            if abs(delta) <= self.execution.rebalance_buffer_contracts:
                continue
            row = _session_row(frames[instrument_id], session)
            if row is None or not bool(row["tradable"]) or str(row["execution_status"]) != "tradable":
                warnings.append(f"{session.date()} {instrument_id}: target delta could not trade; market unavailable or locked.")
                continue
            active_contract = str(row["active_contract"])
            expected_contract = str(raw_target.get("active_contract") or "").strip()
            if expected_contract and expected_contract != active_contract:
                warnings.append(
                    f"{session.date()} {instrument_id}: target was not traded because its active contract changed "
                    f"from {expected_contract} to {active_contract}; wait for a newly generated target."
                )
                continue
            if active_contracts.get(instrument_id) != active_contract:
                warnings.append(
                    f"{session.date()} {instrument_id}: target delta could not trade; active contract state is not reconciled."
                )
                continue
            facts = contract_facts.get(instrument_id)
            if facts is None:
                warnings.append(
                    f"{session.date()} {instrument_id}: target delta could not trade; dated contract facts are unavailable."
                )
                continue
            position_limit = int(facts["position_limit"])
            if abs(target) > position_limit:
                target = int(math.copysign(position_limit, target))
                delta = target - current
                warnings.append(
                    f"{session.date()} {instrument_id}: target was reduced to the dated position limit."
                )
            if abs(delta) <= self.execution.rebalance_buffer_contracts:
                continue
            capacity = math.floor(float(row["volume"]) * self.execution.max_volume_participation)
            if capacity <= 0:
                warnings.append(f"{session.date()} {instrument_id}: target delta could not trade; no conservative capacity.")
                continue
            executed = int(math.copysign(min(abs(delta), capacity), delta))
            reference = float(row["open"])
            execution_price = reference * (1 + (self.execution.slippage_bps / 10_000) * (1 if executed > 0 else -1))
            costs = abs(executed) * self.execution.commission_per_contract
            fill_to_settlement_pnl = (
                executed
                * (float(row["settlement"]) - execution_price)
                * float(facts["contract_multiplier"])
            )
            cash -= costs
            cash += fill_to_settlement_pnl
            positions[instrument_id] += executed
            trades.append(
                {
                    "date": session.date().isoformat(),
                    "instrument_id": instrument_id,
                    "active_contract": active_contract,
                    "side": "buy" if executed > 0 else "sell",
                    "contracts": abs(executed),
                    "signed_delta": executed,
                    "execution_price": round(execution_price, 8),
                    "reference_open": round(reference, 8),
                    "settlement": round(float(row["settlement"]), 8),
                    "fill_to_settlement_pnl": round(fill_to_settlement_pnl, 8),
                    "costs": round(costs, 8),
                    "capacity_limited": abs(executed) < abs(delta),
                    "paper_only": True,
                }
            )
            if abs(executed) < abs(delta):
                warnings.append(f"{session.date()} {instrument_id}: target delta capped by conservative volume participation.")
        return cash


def _build_domestic_futures_cta_proposal(
    market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]]],
    instruments: Mapping[str, FuturesInstrumentSpec | Mapping[str, Any]],
    *,
    capital: float,
    config: CTAStrategyConfig | Mapping[str, Any] | None = None,
    as_of: str | None = None,
    previous_contracts: Mapping[str, int] | None = None,
    source_archive_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Convenience capability for an auditable domestic-futures CTA proposal."""

    resolved = config if isinstance(config, CTAStrategyConfig) else CTAStrategyConfig.from_mapping(config)
    result = _DomesticFuturesCTAStrategy(resolved).generate_proposal(
        market_data,
        instruments,
        capital=capital,
        as_of=as_of,
        previous_contracts=previous_contracts,
        source_archive_ids=source_archive_ids,
    ).to_dict()
    # Allocation must use a named risk-capital denominator rather than infer
    # it from notional or margin.  It remains a paper-target attribute only.
    result["capital"] = capital
    return result


def _run_domestic_futures_cta_backtest(
    market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]]],
    instruments: Mapping[str, FuturesInstrumentSpec | Mapping[str, Any]],
    *,
    initial_capital: float,
    config: CTAStrategyConfig | Mapping[str, Any] | None = None,
    execution: FuturesExecutionAssumptions | Mapping[str, Any] | None = None,
    source_archive_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Run a deterministic research-only domestic-futures CTA paper replay."""

    resolved_config = config if isinstance(config, CTAStrategyConfig) else CTAStrategyConfig.from_mapping(config)
    if execution is None or isinstance(execution, FuturesExecutionAssumptions):
        resolved_execution = execution
    elif isinstance(execution, Mapping):
        defaults = FuturesExecutionAssumptions(
            slippage_bps=resolved_config.slippage_bps,
            commission_per_contract=resolved_config.commission_per_contract,
            rebalance_buffer_contracts=resolved_config.rebalance_buffer_contracts,
        )
        values = {
            name: execution.get(name, getattr(defaults, name))
            for name in FuturesExecutionAssumptions.__dataclass_fields__
        }
        resolved_execution = FuturesExecutionAssumptions(**values)
    else:
        raise ValueError("futures execution assumptions must be an object")
    return _DomesticFuturesCTABacktestEngine(resolved_config, resolved_execution).run(
        market_data,
        instruments,
        initial_capital=initial_capital,
        source_archive_ids=source_archive_ids,
    ).to_dict()


def run_frozen_public_domestic_futures_cta_backtest(
    replay_input: Mapping[str, Any],
    *,
    source_archive_path: str | None = None,
    initial_capital: float,
    config: CTAStrategyConfig | Mapping[str, Any] | None = None,
    execution: FuturesExecutionAssumptions | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Replay a frozen public CTA input while retaining its research limits."""

    from ..market_data import verify_frozen_market_archive
    from .data import (
        PUBLIC_DOMESTIC_FUTURES_SOURCE,
        parse_public_domestic_futures_cta_input,
    )

    parsed = parse_public_domestic_futures_cta_input(replay_input)
    manifest = replay_input.get("source_manifest") if isinstance(replay_input, Mapping) else {}
    archive_id = str(manifest.get("archive_id") or "") if isinstance(manifest, Mapping) else ""
    archive_assurance = verify_frozen_market_archive(
        source_archive_path,
        expected_archive_id=archive_id,
        expected_source=PUBLIC_DOMESTIC_FUTURES_SOURCE,
    )
    result = _blocked_public_continuous_replay(
        parsed,
        initial_capital=initial_capital,
        config=config,
        execution=execution,
    )
    result["data_assurance"] = {
        "status": "blocked",
        "scope": "exact_public_input_replay",
        "source": PUBLIC_DOMESTIC_FUTURES_SOURCE,
        "archive_assurance": archive_assurance,
        "limitations": [
            "Exact public input bytes can be verified, but the public continuous series is blocked from P&L replay and remains insufficient for a formal futures execution or performance claim.",
            "No complete point-in-time contract roll, exchange risk-control, margin-history, position-limit, or fill-quality coverage is asserted.",
        ],
    }
    result["formal_decision_eligible"] = False
    result["research_only"] = True
    result["no_order_execution"] = True
    result["warnings"] = list(
        dict.fromkeys(
            list(result.get("warnings") or [])
            + [
                "This frozen public CTA replay is deterministic only for its archived input; it is not a formal futures performance or execution claim."
            ]
        )
    )
    return result


def _blocked_public_continuous_replay(
    parsed: Mapping[str, Any],
    *,
    initial_capital: float,
    config: CTAStrategyConfig | Mapping[str, Any] | None,
    execution: FuturesExecutionAssumptions | Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return a reproducible *but non-performance* response for public bars.

    Continuous proxy bars are useful for audit and signal exploration, but a
    daily P&L simulation on them would still look like a tradable historical
    CTA result.  Refuse it until a point-in-time contract/roll history is
    supplied through the dated-contract input path.
    """

    resolved_config = config if isinstance(config, CTAStrategyConfig) else CTAStrategyConfig.from_mapping(config)
    if execution is None or isinstance(execution, FuturesExecutionAssumptions):
        resolved_execution = execution or FuturesExecutionAssumptions(
            slippage_bps=resolved_config.slippage_bps,
            commission_per_contract=resolved_config.commission_per_contract,
            rebalance_buffer_contracts=resolved_config.rebalance_buffer_contracts,
        )
    elif isinstance(execution, Mapping):
        defaults = FuturesExecutionAssumptions(
            slippage_bps=resolved_config.slippage_bps,
            commission_per_contract=resolved_config.commission_per_contract,
            rebalance_buffer_contracts=resolved_config.rebalance_buffer_contracts,
        )
        resolved_execution = FuturesExecutionAssumptions(
            **{name: execution.get(name, getattr(defaults, name)) for name in FuturesExecutionAssumptions.__dataclass_fields__}
        )
    else:
        raise TypeError("futures execution assumptions must be an object")
    if not math.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("initial_capital must be a positive finite number")
    dates = [
        str(row.get("date") or "")
        for series in parsed["market_data"].values()
        if isinstance(series, Sequence)
        for row in series
        if isinstance(row, Mapping) and str(row.get("date") or "")
    ]
    as_of = max(dates) if dates else None
    return {
        "schema_version": "domestic_futures_cta_backtest.v1",
        "strategy_id": resolved_config.strategy_id,
        "strategy_version": resolved_config.version,
        "initial_capital": initial_capital,
        "final_equity": initial_capital,
        "total_return": 0.0,
        "annualized_return": 0.0,
        "annualized_volatility": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "execution_assumptions": resolved_execution.to_dict(),
        "equity_curve": [],
        "trades": [],
        "roll_events": [],
        "warnings": [
            "Public continuous-contract data was verified as an immutable archive but is blocked from P&L replay: no point-in-time executable contract lifecycle or roll history is attached.",
            "Provide dated actual-contract bars, expiry/roll facts, margin history, position limits and execution-status coverage through the non-public CTA input path before running a paper backtest.",
        ],
        "data_assurance": {
            "status": "blocked",
            "scope": "public_continuous_series_only",
            "source_archive_ids": list(parsed["source_archive_ids"]),
            "as_of": as_of,
        },
        "strategy_implementation_fingerprint": _implementation_fingerprint(),
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
    }


def _normalize_specs(
    instruments: Mapping[str, FuturesInstrumentSpec | Mapping[str, Any]],
) -> dict[str, FuturesInstrumentSpec]:
    if not isinstance(instruments, Mapping) or not instruments:
        raise ValueError("CTA requires a non-empty instrument mapping")
    normalized: dict[str, FuturesInstrumentSpec] = {}
    for raw_key, raw_spec in instruments.items():
        spec = raw_spec if isinstance(raw_spec, FuturesInstrumentSpec) else FuturesInstrumentSpec.from_mapping(raw_spec)
        key = str(raw_key).strip()
        if not key or key != spec.instrument_id:
            raise ValueError("instrument mapping keys must match each specification instrument_id")
        if spec.instrument_id in normalized:
            raise ValueError("CTA instrument ids must be unique")
        normalized[spec.instrument_id] = spec
    return normalized


def _normalize_market_data(
    market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]]],
    specs: Mapping[str, FuturesInstrumentSpec],
) -> dict[str, pd.DataFrame]:
    if not isinstance(market_data, Mapping):
        raise TypeError("CTA market_data must be an instrument mapping")
    missing = sorted(set(specs).difference(market_data))
    if missing:
        raise ValueError("CTA market_data lacks instruments: " + ", ".join(missing))
    normalized: dict[str, pd.DataFrame] = {}
    for instrument_id in specs:
        raw = market_data[instrument_id]
        frame = raw.copy() if isinstance(raw, pd.DataFrame) else pd.DataFrame(list(raw))
        required = {
            "date",
            "open",
            "close",
            "settlement",
            "volume",
            "open_interest",
            "tradable",
            "execution_status",
            "days_to_expiry",
            "active_contract",
            "contract_multiplier",
            "initial_margin_rate",
            "maintenance_margin_rate",
            "position_limit",
            "contract_facts_as_of",
            "contract_source_ref",
        }
        missing_columns = sorted(required.difference(frame.columns))
        if missing_columns:
            raise ValueError(f"CTA market data for {instrument_id} lacks: " + ", ".join(missing_columns))
        columns = [
            "date",
            "open",
            "close",
            "settlement",
            "volume",
            "open_interest",
            "tradable",
            "execution_status",
            "days_to_expiry",
            "active_contract",
            "contract_multiplier",
            "initial_margin_rate",
            "maintenance_margin_rate",
            "position_limit",
            "contract_facts_as_of",
            "contract_source_ref",
        ]
        roll_columns = ["roll_from_contract", "roll_exit_price", "roll_entry_price", "roll_source_ref"]
        frame = frame[columns + [column for column in roll_columns if column in frame.columns]].copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
        if frame["date"].isna().any() or frame["date"].duplicated().any():
            raise ValueError(f"CTA market data for {instrument_id} has invalid or duplicate dates")
        frame = frame.sort_values("date", kind="stable").reset_index(drop=True)
        for column in (
            "open",
            "close",
            "settlement",
            "volume",
            "open_interest",
            "contract_multiplier",
            "initial_margin_rate",
            "maintenance_margin_rate",
            "position_limit",
        ):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        numeric = [
            "open",
            "close",
            "settlement",
            "volume",
            "open_interest",
            "contract_multiplier",
            "initial_margin_rate",
            "maintenance_margin_rate",
            "position_limit",
        ]
        if frame[numeric].isna().any().any():
            raise ValueError(f"CTA market data for {instrument_id} has non-numeric fields")
        if (frame[["open", "close", "settlement"]] <= 0).any().any() or (frame[["volume", "open_interest"]] < 0).any().any():
            raise ValueError(f"CTA market data for {instrument_id} has invalid prices or liquidity")
        if (frame["contract_multiplier"] <= 0).any() or (frame["position_limit"] <= 0).any():
            raise ValueError(f"CTA market data for {instrument_id} has invalid contract multiplier or position limit")
        if (
            (frame["initial_margin_rate"] <= 0).any()
            or (frame["initial_margin_rate"] > 1).any()
            or (frame["maintenance_margin_rate"] <= 0).any()
            or (frame["maintenance_margin_rate"] > frame["initial_margin_rate"]).any()
        ):
            raise ValueError(f"CTA market data for {instrument_id} has invalid dated margin facts")
        if not np.allclose(frame["position_limit"], np.floor(frame["position_limit"])):
            raise ValueError(f"CTA market data for {instrument_id} has a non-integer position limit")
        try:
            frame["tradable"] = [
                _strict_bool(value, f"CTA market data {instrument_id} tradable")
                for value in frame["tradable"]
            ]
        except ValueError as error:
            raise ValueError(f"CTA market data for {instrument_id} has invalid tradable state") from error
        frame["execution_status"] = frame["execution_status"].astype(str).str.strip().str.lower()
        allowed = {"tradable", "halted", "limit_up_locked", "limit_down_locked", "unknown"}
        if not frame["execution_status"].isin(allowed).all():
            raise ValueError(f"CTA market data for {instrument_id} has an invalid execution_status")
        frame["days_to_expiry"] = pd.to_numeric(frame["days_to_expiry"], errors="coerce")
        if frame["days_to_expiry"].isna().any() or (frame["days_to_expiry"] < 0).any():
            raise ValueError(f"CTA market data for {instrument_id} has invalid days_to_expiry")
        for field_name in ("active_contract", "contract_facts_as_of", "contract_source_ref"):
            frame[field_name] = frame[field_name].astype(str).str.strip()
            if (frame[field_name] == "").any() or (frame[field_name].str.lower() == "nan").any():
                raise ValueError(f"CTA market data for {instrument_id} lacks dated {field_name}")
        for row_index, row in frame.iterrows():
            try:
                fact_date = pd.Timestamp(str(row["contract_facts_as_of"])).normalize()
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"CTA market data for {instrument_id} has invalid contract_facts_as_of"
                ) from error
            if pd.isna(fact_date) or fact_date > row["date"]:
                raise ValueError(
                    f"CTA market data for {instrument_id} has future-dated contract facts"
                )
            if row_index == 0:
                continue
            previous_contract = str(frame.loc[row_index - 1, "active_contract"])
            current_contract = str(row["active_contract"])
            if previous_contract == current_contract:
                continue
            missing_roll_fields = [
                field
                for field in roll_columns
                if field not in frame.columns or not str(row.get(field) or "").strip()
            ]
            if missing_roll_fields:
                raise ValueError(
                    f"CTA market data for {instrument_id} changed active_contract without dated roll facts: "
                    + ", ".join(missing_roll_fields)
                )
            if str(row["roll_from_contract"]).strip() != previous_contract:
                raise ValueError(
                    f"CTA market data for {instrument_id} roll_from_contract does not match the prior active contract"
                )
            for field in ("roll_exit_price", "roll_entry_price"):
                try:
                    value = float(row[field])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"CTA market data for {instrument_id} has invalid {field}"
                    ) from error
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f"CTA market data for {instrument_id} has invalid {field}")
        normalized[instrument_id] = frame.set_index("date")
    return normalized


def _validate_historical_replay_inputs(
    frames: Mapping[str, pd.DataFrame],
    specs: Mapping[str, FuturesInstrumentSpec],
    source_archive_ids: Sequence[str],
) -> None:
    """Block P&L replay unless immutable, actual-contract facts are present."""

    archive_ids = [str(value).strip() for value in source_archive_ids if str(value).strip()]
    if not archive_ids or any(not value.startswith("sha256:") for value in archive_ids):
        raise ValueError(
            "CTA historical P&L replay requires at least one immutable sha256 source archive id"
        )
    for instrument_id, spec in specs.items():
        if spec.contract_lifecycle_coverage != "verified":
            raise ValueError(
                f"CTA historical P&L replay requires verified actual-contract lifecycle coverage for {instrument_id}"
            )
        frame = frames[instrument_id]
        if frame.empty:
            raise ValueError(f"CTA historical P&L replay has no dated rows for {instrument_id}")
        latest_contract = str(frame.iloc[-1]["active_contract"])
        if latest_contract != spec.active_contract:
            raise ValueError(
                f"CTA current contract specification for {instrument_id} does not match its latest dated active contract"
            )


def _row_contract_facts(row: pd.Series) -> dict[str, Any]:
    return {
        "active_contract": str(row["active_contract"]),
        "contract_multiplier": float(row["contract_multiplier"]),
        "initial_margin_rate": float(row["initial_margin_rate"]),
        "maintenance_margin_rate": float(row["maintenance_margin_rate"]),
        "position_limit": int(row["position_limit"]),
        "contract_facts_as_of": str(row["contract_facts_as_of"]),
        "contract_source_ref": str(row["contract_source_ref"]),
    }


def _row_roll_facts(row: pd.Series, *, from_contract: str) -> dict[str, Any]:
    roll_from = str(row.get("roll_from_contract") or "").strip()
    source_ref = str(row.get("roll_source_ref") or "").strip()
    if roll_from != from_contract or not source_ref:
        raise ValueError("CTA active-contract roll lacks matching dated roll evidence")
    try:
        exit_price = float(row.get("roll_exit_price"))
        entry_price = float(row.get("roll_entry_price"))
    except (TypeError, ValueError) as error:
        raise ValueError("CTA active-contract roll has invalid prices") from error
    if not math.isfinite(exit_price) or exit_price <= 0 or not math.isfinite(entry_price) or entry_price <= 0:
        raise ValueError("CTA active-contract roll has invalid prices")
    return {
        "roll_exit_price": exit_price,
        "roll_entry_price": entry_price,
        "roll_source_ref": source_ref,
    }


def _instrument_candidate(
    frame: pd.DataFrame,
    spec: FuturesInstrumentSpec,
    config: CTAStrategyConfig,
    as_of: pd.Timestamp,
    previous_contracts: int,
    *,
    enforce_current_spec_contract: bool,
) -> tuple[dict[str, Any] | None, str | None]:
    history = frame.loc[frame.index <= as_of]
    if len(history) < config.minimum_history:
        return None, f"insufficient history ({len(history)} < {config.minimum_history})"
    row = history.iloc[-1]
    if not bool(row["tradable"]) or str(row["execution_status"]) != "tradable":
        return None, "latest session is not tradable"
    if float(row["volume"]) < config.minimum_daily_volume:
        return None, "latest volume is below the configured threshold"
    if float(row["open_interest"]) < config.minimum_open_interest:
        return None, "latest open interest is below the configured threshold"
    if spec.contract_lifecycle_coverage != "verified":
        return None, "contract lifecycle is not verified; continuous-series proxy cannot pass delivery/roll gate"
    if int(row["days_to_expiry"]) < config.minimum_days_to_expiry:
        return None, "contract is inside the configured delivery/roll safety buffer"
    if enforce_current_spec_contract and str(row["active_contract"]) != spec.active_contract:
        return None, "dated active contract does not match the supplied current contract specification"
    settlement = history["settlement"].astype(float)
    returns = np.log(settlement / settlement.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
    if len(returns) < max(config.volatility_lookback, max(config.signal_windows)):
        return None, "insufficient return history after normalization"
    daily_vol = float(returns.iloc[-config.volatility_lookback:].std(ddof=1))
    if not math.isfinite(daily_vol) or daily_vol <= 0:
        return None, "non-positive realized daily volatility"
    components = []
    for window in config.signal_windows:
        raw_return = float(math.log(settlement.iloc[-1] / settlement.iloc[-1 - window]))
        components.append(raw_return / (daily_vol * math.sqrt(window)))
    score = float(sum(weight * component for weight, component in zip(config.signal_weights, components, strict=True)))
    direction = _direction_with_hysteresis(score, previous_contracts, config)
    return {
        "instrument_id": spec.instrument_id,
        "spec": spec,
        "signal_score": score,
        "direction": direction,
        "daily_volatility": daily_vol,
        "reference_price": float(row["settlement"]),
        "volume": float(row["volume"]),
        "open_interest": float(row["open_interest"]),
        "days_to_expiry": int(row["days_to_expiry"]),
        "active_contract": str(row["active_contract"]),
        "contract_multiplier": float(row["contract_multiplier"]),
        "initial_margin_rate": float(row["initial_margin_rate"]),
        "maintenance_margin_rate": float(row["maintenance_margin_rate"]),
        "position_limit": int(row["position_limit"]),
        "contract_facts_as_of": str(row["contract_facts_as_of"]),
        "contract_source_ref": str(row["contract_source_ref"]),
    }, None


def _direction_with_hysteresis(score: float, previous_contracts: int, config: CTAStrategyConfig) -> int:
    if previous_contracts > 0 and score >= -config.entry_threshold and score > config.exit_threshold:
        return 1
    if previous_contracts < 0 and score <= config.entry_threshold and score < -config.exit_threshold:
        return -1
    if score >= config.entry_threshold:
        return 1
    if score <= -config.entry_threshold:
        return -1
    return 0


def _size_candidates(
    candidates: Sequence[Mapping[str, Any]],
    capital: float,
    config: CTAStrategyConfig,
) -> list[FuturesTarget]:
    active = [candidate for candidate in candidates if int(candidate["direction"]) != 0]
    if not active:
        return []
    group_members: dict[str, list[Mapping[str, Any]]] = {}
    for candidate in active:
        group_members.setdefault(candidate["spec"].group, []).append(candidate)
    # A group cannot consume the whole sleeve simply because it is currently
    # the only group with a valid trend signal.  This cap is deliberately
    # applied before integer-contract and margin constraints.
    group_budget = min(1.0 / len(group_members), config.max_group_risk_fraction)
    annual_risk_budget = capital * config.annual_target_volatility
    preliminary: list[dict[str, Any]] = []
    for members in group_members.values():
        allocation = group_budget / len(members)
        for candidate in members:
            score_scale = min(1.0, abs(float(candidate["signal_score"])))
            risk_fraction = min(allocation * score_scale, config.max_instrument_risk_fraction)
            preliminary.append({**candidate, "risk_fraction": risk_fraction})
    total_fraction = sum(item["risk_fraction"] for item in preliminary)
    if total_fraction <= 0:
        return []
    scale = min(1.0, 1.0 / total_fraction)
    output: list[FuturesTarget] = []
    for item in preliminary:
        spec: FuturesInstrumentSpec = item["spec"]
        risk_dollars = annual_risk_budget * item["risk_fraction"] * scale
        annual_vol = float(item["daily_volatility"]) * math.sqrt(_TRADING_DAYS_PER_YEAR)
        contract_multiplier = float(item["contract_multiplier"])
        dollars_per_contract_at_annual_vol = item["reference_price"] * contract_multiplier * annual_vol
        raw_contracts = risk_dollars / dollars_per_contract_at_annual_vol if dollars_per_contract_at_annual_vol > 0 else 0.0
        contracts = math.floor(raw_contracts) * int(item["direction"])
        contracts = int(
            math.copysign(
                min(abs(contracts), int(item["position_limit"])),
                contracts,
            )
        )
        if spec.max_contracts is not None:
            contracts = int(math.copysign(min(abs(contracts), spec.max_contracts), contracts))
        if contracts == 0:
            continue
        notional = abs(contracts) * item["reference_price"] * contract_multiplier
        margin = notional * float(item["initial_margin_rate"])
        output.append(
            FuturesTarget(
                instrument_id=spec.instrument_id,
                active_contract=str(item["active_contract"]),
                group=spec.group,
                direction=int(item["direction"]),
                target_contracts=contracts,
                raw_target_contracts=round(raw_contracts * int(item["direction"]), 8),
                signal_score=round(float(item["signal_score"]), 8),
                daily_volatility=round(float(item["daily_volatility"]), 10),
                reference_price=round(float(item["reference_price"]), 8),
                risk_dollars=round(risk_dollars, 8),
                margin_required=round(margin, 8),
                source_ref=spec.source_ref,
                contract_multiplier=contract_multiplier,
                initial_margin_rate=float(item["initial_margin_rate"]),
                maintenance_margin_rate=float(item["maintenance_margin_rate"]),
                position_limit=int(item["position_limit"]),
                contract_facts_as_of=str(item["contract_facts_as_of"]),
                contract_source_ref=str(item["contract_source_ref"]),
            )
        )
    return _apply_margin_cap(output, capital, config)


def _apply_margin_cap(
    targets: list[FuturesTarget], capital: float, config: CTAStrategyConfig) -> list[FuturesTarget]:
    cap = capital * config.max_margin_fraction
    margin = sum(target.margin_required for target in targets)
    if margin <= cap + 1e-9:
        return targets
    scale = cap / margin if margin else 0.0
    resized: list[FuturesTarget] = []
    for target in targets:
        contracts = int(math.copysign(math.floor(abs(target.target_contracts) * scale), target.target_contracts))
        per_contract_margin = (
            target.reference_price * target.contract_multiplier * target.initial_margin_rate
        )
        resized.append(
            FuturesTarget(
                **{
                    **target.__dict__,
                    "target_contracts": contracts,
                    "margin_required": round(abs(contracts) * per_contract_margin, 8),
                    "risk_dollars": round(target.risk_dollars * scale, 8),
                }
            )
        )
    return [target for target in resized if target.target_contracts != 0]


def _estimate_target_portfolio_daily_volatility(
    targets: Sequence[FuturesTarget],
    specs: Mapping[str, FuturesInstrumentSpec],
) -> float:
    if not targets:
        return 0.0
    risk_variance = 0.0
    for target in targets:
        daily_pnl_std = (
            abs(target.target_contracts)
            * target.reference_price
            * target.contract_multiplier
            * target.daily_volatility
        )
        risk_variance += daily_pnl_std**2
    return math.sqrt(risk_variance)


def _settle_existing_positions(
    session: pd.Timestamp,
    frames: Mapping[str, pd.DataFrame],
    positions: Mapping[str, int],
    active_contracts: dict[str, str],
    mark_prices: dict[str, float],
    contract_facts: dict[str, dict[str, Any]],
    cash: float,
    roll_events: list[dict[str, Any]],
) -> float:
    """Mark existing positions and process a fully evidenced actual-contract roll.

    A position receives its old-contract variation margin through the dated
    roll exit price, then its new-contract entry-to-settlement variation.  A
    continuous series cannot enter this path because `_normalize_market_data`
    rejects it without actual contract and roll facts.
    """

    for instrument_id in positions:
        row = _session_row(frames[instrument_id], session)
        if row is None:
            continue
        facts = _row_contract_facts(row)
        settlement = float(row["settlement"])
        current_contract = active_contracts.get(instrument_id)
        position = positions[instrument_id]
        if current_contract is None:
            active_contracts[instrument_id] = facts["active_contract"]
            contract_facts[instrument_id] = facts
            mark_prices[instrument_id] = settlement
            continue
        previous_mark = mark_prices.get(instrument_id)
        previous_facts = contract_facts.get(instrument_id)
        if previous_mark is None or previous_facts is None:
            raise ValueError(f"{instrument_id} has an unreconciled contract state")
        if current_contract != facts["active_contract"]:
            roll = _row_roll_facts(row, from_contract=current_contract)
            if position != 0:
                old_variation = (
                    position
                    * (float(roll["roll_exit_price"]) - previous_mark)
                    * float(previous_facts["contract_multiplier"])
                )
                new_variation = (
                    position
                    * (settlement - float(roll["roll_entry_price"]))
                    * float(facts["contract_multiplier"])
                )
                cash += old_variation + new_variation
                roll_events.append(
                    {
                        "date": session.date().isoformat(),
                        "instrument_id": instrument_id,
                        "from_contract": current_contract,
                        "to_contract": facts["active_contract"],
                        "position_contracts": position,
                        "roll_exit_price": round(float(roll["roll_exit_price"]), 8),
                        "roll_entry_price": round(float(roll["roll_entry_price"]), 8),
                        "roll_source_ref": roll["roll_source_ref"],
                        "old_contract_variation_pnl": round(old_variation, 8),
                        "new_contract_variation_pnl": round(new_variation, 8),
                        "status": "verified_actual_contract_roll",
                    }
                )
            active_contracts[instrument_id] = facts["active_contract"]
            contract_facts[instrument_id] = facts
            mark_prices[instrument_id] = settlement
            continue
        if position != 0:
            cash += position * (settlement - previous_mark) * float(facts["contract_multiplier"])
        contract_facts[instrument_id] = facts
        mark_prices[instrument_id] = settlement
    return cash


def _account_state(
    positions: Mapping[str, int],
    mark_prices: Mapping[str, float],
    contract_facts: Mapping[str, Mapping[str, Any]],
    cash: float,
) -> tuple[float, float, float]:
    margin = 0.0
    gross_notional = 0.0
    for instrument_id, position in positions.items():
        price = mark_prices.get(instrument_id)
        if price is None:
            continue
        facts = contract_facts.get(instrument_id)
        if facts is None:
            raise ValueError(f"{instrument_id} has no dated contract facts for account valuation")
        notional = abs(position) * price * float(facts["contract_multiplier"])
        gross_notional += notional
        margin += notional * float(facts["initial_margin_rate"])
    return cash, margin, gross_notional


def _performance_metrics(curve: Sequence[Mapping[str, Any]], initial_capital: float) -> dict[str, float]:
    equity = np.asarray([float(item["equity"]) for item in curve], dtype=float)
    if len(equity) < 2:
        return {name: 0.0 for name in ("total_return", "annualized_return", "annualized_volatility", "sharpe_ratio", "max_drawdown")}
    returns = equity[1:] / equity[:-1] - 1.0
    total_return = float(equity[-1] / initial_capital - 1.0)
    annualized_volatility = float(np.std(returns, ddof=1) * math.sqrt(_TRADING_DAYS_PER_YEAR)) if len(returns) > 1 else 0.0
    years = len(returns) / _TRADING_DAYS_PER_YEAR
    annualized_return = float((equity[-1] / initial_capital) ** (1 / years) - 1.0) if years > 0 and equity[-1] > 0 else -1.0
    sharpe = float(np.mean(returns) / np.std(returns, ddof=1) * math.sqrt(_TRADING_DAYS_PER_YEAR)) if len(returns) > 1 and np.std(returns, ddof=1) > 0 else 0.0
    peaks = np.maximum.accumulate(equity)
    max_drawdown = float(np.max(1.0 - equity / peaks)) if len(peaks) else 0.0
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }


def _latest_common_as_of(frames: Mapping[str, pd.DataFrame]) -> pd.Timestamp:
    latest = [frame.index[-1] for frame in frames.values() if len(frame)]
    return min(latest) if latest else pd.NaT


def _next_effective_session(frames: Mapping[str, pd.DataFrame], as_of: pd.Timestamp) -> str | None:
    candidates = sorted({day for frame in frames.values() for day in frame.index if day > as_of})
    return candidates[0].date().isoformat() if candidates else None


def _union_sessions(frames: Mapping[str, pd.DataFrame]) -> list[pd.Timestamp]:
    return sorted({day for frame in frames.values() for day in frame.index})


def _session_row(frame: pd.DataFrame, session: pd.Timestamp) -> pd.Series | None:
    if session not in frame.index:
        return None
    row = frame.loc[session]
    if isinstance(row, pd.DataFrame):
        raise TypeError("CTA market data has duplicate session rows")
    return row


def _strict_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise ValueError(f"{name} must be boolean")


def _spec_by_id(specs: Mapping[str, FuturesInstrumentSpec], instrument_id: str) -> FuturesInstrumentSpec:
    return specs[instrument_id]


def _proposal_warnings(source_archive_ids: Sequence[str]) -> list[str]:
    base = [
        "Domestic futures CTA is a bounded personal sub-strategy, not a claim of global CTA replication.",
        "A proposal is a paper research target only; verify current broker permissions, contract facts, margin, position limits, and liquidity before any manual action.",
    ]
    if not source_archive_ids:
        base.append("No immutable source archive ids were supplied; result is public-observation research only.")
    return base


def _implementation_fingerprint() -> str:
    source = "domestic_futures_cta.v1|tsmom=21,63,126|vol=60|daily_settlement_mark_to_market"
    return "sha256:" + hashlib.sha256(source.encode("utf-8")).hexdigest()
