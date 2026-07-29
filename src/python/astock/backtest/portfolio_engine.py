"""Point-in-time, multi-asset paper-portfolio backtest contract."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pandas as pd

from ..data_provenance import assess_backtest_source_manifest
from ..market_data import verify_frozen_market_archive


@dataclass(frozen=True)
class PortfolioExecutionAssumptions:
    commission_rate: float = 0.0003
    stamp_duty_rate: float = 0.0005
    transfer_fee_rate: float = 0.00001
    lot_size: int = 100
    execution_timing: str = "next_open"
    settlement: str = "t_plus_one"
    slippage_bps: float = 0.0
    max_participation_rate: float | None = None


@dataclass(frozen=True)
class PortfolioBacktestResult:
    """Result of a point-in-time target-weight paper portfolio simulation."""

    initial_capital: float
    final_capital: float
    total_return: float
    execution_assumptions: PortfolioExecutionAssumptions
    equity_curve: list[dict[str, Any]]
    trades: list[dict[str, Any]]
    warnings: list[str]
    coverage: dict[str, str]
    source_assurance: dict[str, Any]
    corporate_action_events: list[dict[str, Any]]
    delisting_status: dict[str, dict[str, Any]]
    universe_assurance: dict[str, Any]
    archive_assurance: dict[str, Any]
    reproducibility_assurance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "portfolio_backtest.v1",
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "execution_assumptions": {
                "commission_rate": self.execution_assumptions.commission_rate,
                "stamp_duty_rate": self.execution_assumptions.stamp_duty_rate,
                "transfer_fee_rate": self.execution_assumptions.transfer_fee_rate,
                "lot_size": self.execution_assumptions.lot_size,
                "execution_timing": self.execution_assumptions.execution_timing,
                "settlement": self.execution_assumptions.settlement,
                "slippage_bps": self.execution_assumptions.slippage_bps,
                "max_participation_rate": self.execution_assumptions.max_participation_rate,
            },
            "equity_curve": self.equity_curve,
            "trades": self.trades,
            "warnings": self.warnings,
            "coverage": self.coverage,
            "source_assurance": self.source_assurance,
            "corporate_action_events": self.corporate_action_events,
            "delisting_status": self.delisting_status,
            "universe_assurance": self.universe_assurance,
            "archive_assurance": self.archive_assurance,
            "reproducibility_assurance": self.reproducibility_assurance,
        }


class PortfolioBacktestEngine:
    """Execute point-in-time target weights as a paper book.

    The engine evaluates the implementation layer, not alpha selection. Targets
    dated D are first actionable at the next available global session open and
    each target date must name its historical point-in-time universe source.
    """

    def run(
        self,
        market_data: Mapping[str, pd.DataFrame],
        target_weights: Mapping[str, Mapping[str, float]],
        *,
        universe_references: Mapping[str, str],
        trading_calendar: Sequence[str | pd.Timestamp],
        universe_snapshots: Mapping[str, Mapping[str, Any]] | None = None,
        initial_capital: float = 100_000.0,
        commission_rate: float = 0.0003,
        stamp_duty_rate: float = 0.0005,
        transfer_fee_rate: float = 0.00001,
        slippage_bps: float = 0.0,
        max_participation_rate: float | None = None,
        coverage_manifest: Mapping[str, str] | None = None,
        source_manifest: Mapping[str, Any] | None = None,
        source_archive_path: str | None = None,
        corporate_actions: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
        delisting_status: Mapping[str, Mapping[str, Any]] | None = None,
        price_basis: str = "unknown",
    ) -> PortfolioBacktestResult:
        if initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        if not target_weights:
            raise ValueError("portfolio backtest requires at least one target-weight date")
        if not math.isfinite(slippage_bps) or slippage_bps < 0 or slippage_bps > 1_000:
            raise ValueError("slippage_bps must be a finite value between zero and 1000")
        if max_participation_rate is not None and (
            not math.isfinite(max_participation_rate)
            or max_participation_rate <= 0
            or max_participation_rate > 1
        ):
            raise ValueError("max_participation_rate must be a finite fraction in (0, 1]")
        data = {str(code): _normalize_frame(str(code), frame) for code, frame in market_data.items()}
        if not data:
            raise ValueError("portfolio backtest requires market data")
        calendar = _normalize_trading_calendar(trading_calendar)
        if len(calendar) < 2:
            raise ValueError("portfolio backtest requires at least two trading sessions")
        calendar_set = set(calendar)
        for code, frame in data.items():
            if any(day not in calendar_set for day in frame.index):
                raise ValueError(f"market data for {code} includes dates outside the supplied exchange calendar")
        targets = _normalize_targets(target_weights, data, universe_references, calendar_set)
        normalized_universes = _normalize_universe_snapshots(universe_snapshots, calendar_set)
        universe_assurance = _assess_universe_assurance(targets, universe_references, normalized_universes)
        assumptions = PortfolioExecutionAssumptions(
            commission_rate=commission_rate,
            stamp_duty_rate=stamp_duty_rate,
            transfer_fee_rate=transfer_fee_rate,
            slippage_bps=slippage_bps,
            max_participation_rate=max_participation_rate,
        )
        cash = float(initial_capital)
        shares = {code: 0 for code in data}
        sellable = {code: 0 for code in data}
        settlements: dict[str, list[tuple[pd.Timestamp, int]]] = {code: [] for code in data}
        last_close: dict[str, float] = {}
        warnings: list[str] = [
            "Target weights observed on D execute no earlier than the next global session open.",
            "T+1 settlement prevents same-day resale of newly purchased shares.",
            "Settlement and target eligibility use the supplied exchange trading calendar, not a union of instrument price dates.",
            "Trades are skipped when a code lacks a tradable open; no synthetic fill is created.",
            "Point-in-time universe references are required for each target date; corporate actions and delistings are applied only when supplied as source-labelled events.",
        ]
        coverage = _normalize_coverage_manifest(coverage_manifest)
        source_assurance = assess_backtest_source_manifest(source_manifest)
        if source_assurance["status"] == "pass" and universe_assurance["status"] != "pass":
            raise ValueError(
                "a reproducible portfolio backtest requires frozen point-in-time universe snapshots: "
                + "; ".join(universe_assurance["failures"])
            )
        archive_assurance = _assess_source_archive(source_manifest, source_archive_path, source_assurance)
        normalized_price_basis = str(price_basis).strip().lower()
        if coverage["corporate_actions"] == "covered" and normalized_price_basis != "raw":
            raise ValueError("covered corporate actions require raw, unadjusted market prices")
        if coverage["corporate_actions"] == "covered" and source_assurance["status"] != "pass":
            raise ValueError("covered corporate actions require a passing frozen source manifest")
        action_schedule = _normalize_corporate_actions(corporate_actions, data, calendar)
        supplied_actions = [event for events in action_schedule.values() for event in events]
        if supplied_actions and coverage["corporate_actions"] != "covered":
            raise ValueError("supplied corporate actions require corporate_actions coverage=covered")
        if supplied_actions and normalized_price_basis != "raw":
            raise ValueError("supplied corporate actions require raw, unadjusted market prices")
        if supplied_actions and source_assurance["status"] != "pass":
            raise ValueError("supplied corporate actions require a passing frozen source manifest")
        if any(event["type"] == "cash_delisting" for event in supplied_actions) and coverage["delistings"] != "covered":
            raise ValueError("cash delisting events require delistings coverage=covered")
        normalized_delisting_status = _normalize_delisting_status(delisting_status, data)
        _validate_delisting_coverage(
            normalized_delisting_status,
            data,
            coverage,
            source_assurance,
            supplied_actions,
            calendar,
        )
        if source_assurance["status"] != "pass":
            warnings.append(
                "This replay is not eligible for a reproducibility claim: "
                + "; ".join(source_assurance["failures"])
            )
        if universe_assurance["status"] != "pass":
            warnings.append(
                "This replay lacks frozen point-in-time universe membership evidence: "
                + "; ".join(universe_assurance["failures"])
            )
        if archive_assurance["status"] != "pass":
            warnings.append(
                "This replay lacks verifiable frozen source bytes: "
                + "; ".join(archive_assurance["failures"])
            )
        warnings.extend(source_assurance["warnings"])
        excluded = [name for name, status in coverage.items() if status != "covered"]
        if excluded:
            warnings.append(
                "Historical replay excludes or lacks verified coverage for: " + ", ".join(excluded) + "."
            )
        reproducibility_assurance = _assess_reproducibility(
            source_assurance,
            universe_assurance,
            archive_assurance,
            coverage,
        )
        if reproducibility_assurance["status"] != "pass":
            warnings.append(
                "This replay is not eligible for a full reproducibility claim: "
                + "; ".join(reproducibility_assurance["failures"])
            )
        if max_participation_rate is None:
            warnings.append("No volume participation cap was supplied; replay does not make a capacity claim.")
        elif any("volume" not in frame.columns for frame in data.values()):
            raise ValueError("max_participation_rate requires a volume column for every market-data frame")
        trades: list[dict[str, Any]] = []
        corporate_action_events: list[dict[str, Any]] = []
        equity_curve: list[dict[str, Any]] = []
        pending: Mapping[str, float] | None = None
        for day_index, day in enumerate(calendar):
            cash = _apply_corporate_actions(
                day,
                action_schedule,
                shares,
                sellable,
                settlements,
                cash,
                calendar,
                day_index,
                corporate_action_events,
            )
            for code in data:
                due, remaining = _settle_lots(settlements[code], day)
                sellable[code] += due
                settlements[code] = remaining
            if pending is not None:
                cash = self._rebalance(day, pending, data, shares, sellable, settlements, last_close, cash, assumptions, trades, warnings, calendar, day_index)
            pending = targets.get(day)
            equity = cash
            for code, frame in data.items():
                if day in frame.index:
                    last_close[code] = float(frame.loc[day, "close"])
                close = last_close.get(code)
                if close is None and shares[code] > 0:
                    raise ValueError(f"cannot mark holding {code}: no close is available")
                equity += shares[code] * (close or 0.0)
            equity_curve.append({"date": day.date().isoformat(), "equity": round(equity, 8), "cash": round(cash, 8), "positions": dict(shares)})
        final_capital = float(equity_curve[-1]["equity"])
        return PortfolioBacktestResult(
            initial_capital,
            final_capital,
            (final_capital - initial_capital) / initial_capital,
            assumptions,
            equity_curve,
            trades,
            list(dict.fromkeys(warnings)),
            coverage,
            source_assurance,
            corporate_action_events,
            normalized_delisting_status,
            universe_assurance,
            archive_assurance,
            reproducibility_assurance,
        )

    def _rebalance(self, day: pd.Timestamp, target: Mapping[str, float], data: Mapping[str, pd.DataFrame], shares: dict[str, int], sellable: dict[str, int], settlements: dict[str, list[tuple[pd.Timestamp, int]]], last_close: Mapping[str, float], cash: float, assumptions: PortfolioExecutionAssumptions, trades: list[dict[str, Any]], warnings: list[str], calendar: Sequence[pd.Timestamp], day_index: int) -> float:
        prices = {code: _tradable_open(data[code], day) for code in data}
        equity = cash + sum(shares[code] * (prices[code] or last_close.get(code, 0.0)) for code in data)
        desired_values = {code: equity * target.get(code, 0.0) for code in data}
        for code in data:
            price = prices[code]
            if price is None or shares[code] <= 0:
                continue
            desired_shares = _lot_floor(desired_values[code] / price, assumptions.lot_size)
            quantity = min(max(0, shares[code] - desired_shares), sellable[code])
            quantity, capacity_limited = _cap_trade_quantity(
                quantity, data[code], day, assumptions.max_participation_rate, assumptions.lot_size
            )
            if quantity <= 0:
                if shares[code] > desired_shares and sellable[code] == 0:
                    warnings.append(f"{day.date()} {code}: T+1 settlement blocked requested sale.")
                continue
            if capacity_limited:
                warnings.append(f"{day.date()} {code}: sell capped by volume participation limit.")
            execution_price = _apply_slippage(price, "sell", assumptions.slippage_bps)
            value = quantity * execution_price
            costs = value * (assumptions.commission_rate + assumptions.stamp_duty_rate + assumptions.transfer_fee_rate)
            cash += value - costs
            shares[code] -= quantity
            sellable[code] -= quantity
            trades.append(_trade(day, code, "sell", quantity, execution_price, costs, capacity_limited=capacity_limited))
        for code in data:
            price = prices[code]
            if price is None:
                if target.get(code, 0.0) > 0:
                    warnings.append(f"{day.date()} {code}: target could not trade because open/tradable data is unavailable.")
                continue
            desired_shares = _lot_floor(desired_values[code] / price, assumptions.lot_size)
            quantity = max(0, desired_shares - shares[code])
            quantity, capacity_limited = _cap_trade_quantity(
                quantity, data[code], day, assumptions.max_participation_rate, assumptions.lot_size
            )
            execution_price = _apply_slippage(price, "buy", assumptions.slippage_bps)
            affordable = _lot_floor(cash / (execution_price * (1 + assumptions.commission_rate + assumptions.transfer_fee_rate)), assumptions.lot_size)
            quantity = min(quantity, affordable)
            if quantity <= 0:
                continue
            if capacity_limited:
                warnings.append(f"{day.date()} {code}: buy capped by volume participation limit.")
            value = quantity * execution_price
            costs = value * (assumptions.commission_rate + assumptions.transfer_fee_rate)
            cash -= value + costs
            shares[code] += quantity
            settlements[code].append((calendar[min(day_index + 1, len(calendar) - 1)], quantity))
            trades.append(_trade(day, code, "buy", quantity, execution_price, costs, capacity_limited=capacity_limited))
        return cash


def _normalize_frame(code: str, frame: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "open", "close", "tradable"}
    if not isinstance(frame, pd.DataFrame) or not required.issubset(frame.columns):
        raise ValueError(f"market data for {code} requires date, open, close, and tradable columns")
    columns = list(required)
    if "volume" in frame.columns:
        columns.append("volume")
    if "execution_status" in frame.columns:
        columns.append("execution_status")
    normalized = frame[columns].copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.normalize()
    normalized["open"] = pd.to_numeric(normalized["open"], errors="coerce")
    normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
    if "volume" in normalized:
        normalized["volume"] = pd.to_numeric(normalized["volume"], errors="coerce")
    normalized = normalized.dropna(subset=["date", "close"]).sort_values("date")
    if normalized["date"].duplicated().any():
        raise ValueError(f"market data for {code} has duplicate trading dates")
    if (normalized["close"] <= 0).any():
        raise ValueError(f"market data for {code} has non-positive closes")
    if "volume" in normalized and (normalized["volume"].isna() | (normalized["volume"] < 0)).any():
        raise ValueError(f"market data for {code} has invalid volume values")
    if "execution_status" not in normalized:
        normalized["execution_status"] = normalized["tradable"].map(
            lambda value: "tradable" if bool(value) else "halted"
        )
    normalized["execution_status"] = normalized["execution_status"].astype(str).str.strip().str.lower()
    allowed = {"tradable", "halted", "limit_up_locked", "limit_down_locked", "unknown"}
    if not normalized["execution_status"].isin(allowed).all():
        raise ValueError(f"market data for {code} has an invalid execution_status")
    return normalized.set_index("date")


def _normalize_targets(value: Mapping[str, Mapping[str, float]], data: Mapping[str, pd.DataFrame], universe_references: Mapping[str, str], calendar: set[pd.Timestamp]) -> dict[pd.Timestamp, dict[str, float]]:
    targets: dict[pd.Timestamp, dict[str, float]] = {}
    for raw_day, raw_weights in value.items():
        day = pd.Timestamp(raw_day).normalize()
        if day not in calendar:
            raise ValueError(f"target date {day.date()} is absent from the supplied exchange calendar")
        reference = str(universe_references.get(str(raw_day)) or universe_references.get(day.date().isoformat()) or "").strip()
        if not reference:
            raise ValueError(f"target date {day.date()} lacks a point-in-time universe reference")
        if not isinstance(raw_weights, Mapping):
            raise ValueError(f"target date {day.date()} must map codes to weights")
        weights: dict[str, float] = {}
        for raw_code, raw_weight in raw_weights.items():
            code = str(raw_code)
            if code not in data:
                raise ValueError(f"target date {day.date()} references unknown code {code}")
            try:
                weight = float(raw_weight)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"target weight for {code} must be numeric") from exc
            if not math.isfinite(weight) or weight < 0 or weight > 1:
                raise ValueError(f"target weight for {code} must be between zero and one")
            weights[code] = weight
        if sum(weights.values()) > 1 + 1e-9:
            raise ValueError(f"target weights on {day.date()} exceed 100%")
        targets[day] = weights
    return targets


def _normalize_universe_snapshots(
    value: Mapping[str, Mapping[str, Any]] | None,
    calendar: set[pd.Timestamp],
) -> dict[pd.Timestamp, dict[str, Any]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("universe_snapshots must map target dates to frozen membership records")
    snapshots: dict[pd.Timestamp, dict[str, Any]] = {}
    for raw_day, raw_snapshot in value.items():
        day = pd.Timestamp(raw_day).normalize()
        if pd.isna(day) or day not in calendar:
            raise ValueError("universe snapshot date must be an exchange trading day")
        if day in snapshots:
            raise ValueError(f"duplicate universe snapshot for {day.date()}")
        if not isinstance(raw_snapshot, Mapping):
            raise ValueError(f"universe snapshot for {day.date()} must be a mapping")
        as_of_date = pd.Timestamp(raw_snapshot.get("as_of_date")).normalize()
        if pd.isna(as_of_date) or as_of_date != day:
            raise ValueError(f"universe snapshot for {day.date()} requires matching as_of_date")
        source_ref = str(raw_snapshot.get("source_ref") or "").strip()
        archive_id = str(raw_snapshot.get("archive_id") or "").strip()
        raw_members = raw_snapshot.get("members")
        if not source_ref or not archive_id:
            raise ValueError(f"universe snapshot for {day.date()} requires source_ref and archive_id")
        if not isinstance(raw_members, Sequence) or isinstance(raw_members, (str, bytes)):
            raise ValueError(f"universe snapshot for {day.date()} requires a member sequence")
        members = {str(item).strip() for item in raw_members if str(item).strip()}
        if not members:
            raise ValueError(f"universe snapshot for {day.date()} cannot be empty")
        snapshots[day] = {
            "as_of_date": day,
            "source_ref": source_ref,
            "archive_id": archive_id,
            "members": members,
        }
    return snapshots


def _assess_universe_assurance(
    targets: Mapping[pd.Timestamp, Mapping[str, float]],
    references: Mapping[str, str],
    snapshots: Mapping[pd.Timestamp, Mapping[str, Any]],
) -> dict[str, Any]:
    failures: list[str] = []
    resolved: dict[str, dict[str, str]] = {}
    for day, weights in targets.items():
        day_label = day.date().isoformat()
        reference = str(references.get(day_label) or references.get(day.strftime("%Y-%m-%d")) or "").strip()
        snapshot = snapshots.get(day)
        if snapshot is None:
            failures.append(f"{day_label} lacks a frozen universe snapshot")
            continue
        if snapshot["source_ref"] != reference:
            failures.append(f"{day_label} universe snapshot source_ref does not match its point-in-time reference")
            continue
        non_members = sorted(set(weights).difference(snapshot["members"]))
        if non_members:
            failures.append(f"{day_label} targets are outside the frozen universe: {', '.join(non_members)}")
            continue
        resolved[day_label] = {
            "source_ref": str(snapshot["source_ref"]),
            "archive_id": str(snapshot["archive_id"]),
        }
    return {
        "status": "pass" if not failures else "blocked",
        "failures": failures,
        "resolved_snapshots": resolved,
    }


def _normalize_trading_calendar(value: Sequence[str | pd.Timestamp]) -> list[pd.Timestamp]:
    if isinstance(value, (str, bytes)):
        raise ValueError("trading_calendar must be a sequence of exchange trading dates")
    dates = [pd.Timestamp(item).normalize() for item in value]
    if any(pd.isna(day) for day in dates):
        raise ValueError("trading_calendar contains an invalid date")
    if len(set(dates)) != len(dates):
        raise ValueError("trading_calendar contains duplicate dates")
    return sorted(dates)


def _normalize_coverage_manifest(value: Mapping[str, str] | None) -> dict[str, str]:
    required = ("corporate_actions", "delistings", "price_limits", "halts")
    raw = value or {}
    coverage = {name: str(raw.get(name) or "unverified").strip().lower() for name in required}
    if any(status not in {"covered", "excluded", "unverified"} for status in coverage.values()):
        raise ValueError("coverage_manifest values must be covered, excluded, or unverified")
    return coverage


def _assess_source_archive(
    source_manifest: Mapping[str, Any] | None,
    source_archive_path: str | None,
    source_assurance: Mapping[str, Any],
) -> dict[str, Any]:
    if source_assurance["status"] != "pass":
        return {
            "status": "blocked",
            "failures": ["Source manifest is not structurally eligible; archive verification is unavailable."],
        }
    domains = source_manifest.get("domains") if isinstance(source_manifest, Mapping) else {}
    source_ids = {str(value).strip() for value in domains.values()} if isinstance(domains, Mapping) else set()
    expected_source = next(iter(source_ids)) if len(source_ids) == 1 else None
    return verify_frozen_market_archive(
        source_archive_path,
        expected_archive_id=str(source_manifest.get("archive_id") or ""),
        expected_source=expected_source,
    )


def _assess_reproducibility(
    source_assurance: Mapping[str, Any],
    universe_assurance: Mapping[str, Any],
    archive_assurance: Mapping[str, Any],
    coverage: Mapping[str, str],
) -> dict[str, Any]:
    failures: list[str] = []
    if source_assurance["status"] != "pass":
        failures.append("source manifest is not eligible")
    elif not bool(source_assurance.get("formal_evidence_eligible")):
        sources = source_assurance.get("unconfigured_sources") or []
        failures.append(
            "licensed runtime source is not configured"
            + (": " + ", ".join(str(source) for source in sources) if sources else "")
        )
    if universe_assurance["status"] != "pass":
        failures.append("point-in-time universe evidence is incomplete")
    if archive_assurance["status"] != "pass":
        failures.append("frozen source archive is unavailable or invalid")
    uncovered = sorted(name for name, status in coverage.items() if status != "covered")
    if uncovered:
        failures.append("execution-critical coverage is not complete: " + ", ".join(uncovered))
    return {
        "status": "pass" if not failures else "blocked",
        "failures": failures,
        "source_status": source_assurance["status"],
        "formal_evidence_eligible": bool(source_assurance.get("formal_evidence_eligible")),
        "universe_status": universe_assurance["status"],
        "archive_status": archive_assurance["status"],
    }


def _normalize_corporate_actions(
    value: Mapping[str, Sequence[Mapping[str, Any]]] | None,
    data: Mapping[str, pd.DataFrame],
    calendar: Sequence[pd.Timestamp],
) -> dict[pd.Timestamp, list[dict[str, Any]]]:
    """Normalize explicitly sourced corporate-action and delisting events.

    This engine intentionally accepts only raw-price events that have an
    arithmetic portfolio effect. Rights offerings, mergers, spin-offs, and
    other non-standard treatments must be excluded or modelled by a dedicated
    event adapter; silently approximating them would fabricate a return.
    """
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("corporate_actions must map codes to event sequences")
    calendar_set = set(calendar)
    schedule: dict[pd.Timestamp, list[dict[str, Any]]] = {}
    seen_event_ids: set[str] = set()
    for raw_code, raw_events in value.items():
        code = str(raw_code).strip()
        if code not in data:
            raise ValueError(f"corporate action references unknown code {code}")
        if not isinstance(raw_events, Sequence) or isinstance(raw_events, (str, bytes)):
            raise ValueError(f"corporate actions for {code} must be a sequence")
        for raw_event in raw_events:
            if not isinstance(raw_event, Mapping):
                raise ValueError(f"corporate action for {code} must be a mapping")
            event_type = str(raw_event.get("type") or "").strip().lower()
            if event_type not in {"cash_dividend", "share_distribution", "cash_delisting"}:
                raise ValueError(f"unsupported corporate-action type for {code}: {event_type or 'missing'}")
            event_id = str(raw_event.get("event_id") or "").strip()
            if not event_id or event_id in seen_event_ids:
                raise ValueError("every corporate action requires a unique event_id")
            seen_event_ids.add(event_id)
            source_ref = str(raw_event.get("source_ref") or "").strip()
            if not source_ref:
                raise ValueError(f"corporate action {event_id} requires source_ref")
            effective_date = pd.Timestamp(raw_event.get("effective_date")).normalize()
            if pd.isna(effective_date) or effective_date not in calendar_set:
                raise ValueError(f"corporate action {event_id} effective_date must be an exchange trading day")
            sequence = raw_event.get("sequence", 0)
            if not isinstance(sequence, int):
                raise ValueError(f"corporate action {event_id} sequence must be an integer")
            event: dict[str, Any] = {
                "event_id": event_id,
                "code": code,
                "type": event_type,
                "effective_date": effective_date,
                "source_ref": source_ref,
                "sequence": sequence,
            }
            if event_type in {"cash_dividend", "cash_delisting"}:
                key = "cash_per_share" if event_type == "cash_dividend" else "cash_settlement_per_share"
                value_per_share = _positive_finite(raw_event.get(key), f"corporate action {event_id} {key}")
                event[key] = value_per_share
            else:
                factor = _positive_finite(raw_event.get("share_factor"), f"corporate action {event_id} share_factor")
                if factor <= 1:
                    raise ValueError(f"corporate action {event_id} share_factor must exceed one")
                event["share_factor"] = factor
                available_on = raw_event.get("sellable_on")
                if available_on is not None:
                    available_day = pd.Timestamp(available_on).normalize()
                    if pd.isna(available_day) or available_day not in calendar_set or available_day < effective_date:
                        raise ValueError(f"corporate action {event_id} sellable_on must be a later exchange trading day")
                    event["sellable_on"] = available_day
            schedule.setdefault(effective_date, []).append(event)
    for events in schedule.values():
        events.sort(key=lambda item: (item["code"], item["sequence"], item["event_id"]))
    return schedule


def _normalize_delisting_status(
    value: Mapping[str, Mapping[str, Any]] | None,
    data: Mapping[str, pd.DataFrame],
) -> dict[str, dict[str, Any]]:
    """Normalize source-labelled listing status without inferring settlement.

    A list-status response can establish that a code delisted, but it does not
    provide the consideration or distribution date needed to value a holding.
    The latter must be an explicit ``cash_delisting`` event.
    """
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("delisting_status must map codes to source-labelled status records")
    normalized: dict[str, dict[str, Any]] = {}
    for raw_code, raw_record in value.items():
        code = str(raw_code).strip()
        if code not in data:
            raise ValueError(f"delisting status references unknown code {code}")
        if not isinstance(raw_record, Mapping):
            raise ValueError(f"delisting status for {code} must be a mapping")
        list_status = str(raw_record.get("list_status") or "").strip().upper()
        if not list_status:
            raise ValueError(f"delisting status for {code} requires list_status")
        source_ref = str(raw_record.get("source_ref") or "").strip()
        if not source_ref:
            raise ValueError(f"delisting status for {code} requires source_ref")
        raw_delist_date = raw_record.get("delist_date")
        delist_date: pd.Timestamp | None = None
        if raw_delist_date is not None and str(raw_delist_date).strip():
            delist_date = pd.Timestamp(raw_delist_date).normalize()
            if pd.isna(delist_date):
                raise ValueError(f"delisting status for {code} has an invalid delist_date")
        if list_status == "D" and delist_date is None:
            raise ValueError(f"delisting status for {code} requires delist_date when list_status=D")
        normalized[code] = {
            "code": code,
            "list_status": list_status,
            "delist_date": delist_date,
            "source_ref": source_ref,
        }
    return normalized


def _validate_delisting_coverage(
    statuses: Mapping[str, Mapping[str, Any]],
    data: Mapping[str, pd.DataFrame],
    coverage: Mapping[str, str],
    source_assurance: Mapping[str, Any],
    supplied_actions: Sequence[Mapping[str, Any]],
    calendar: Sequence[pd.Timestamp],
) -> None:
    if coverage["delistings"] != "covered":
        return
    if source_assurance["status"] != "pass":
        raise ValueError("covered delistings require a passing frozen source manifest")
    missing = sorted(set(data).difference(statuses))
    if missing:
        raise ValueError("covered delistings require a source-labelled status record for every code: " + ", ".join(missing))
    end_day = calendar[-1]
    cash_events = {
        str(event["code"])
        for event in supplied_actions
        if str(event["type"]) == "cash_delisting"
    }
    for code, record in statuses.items():
        delist_date = record["delist_date"]
        if record["list_status"] == "D" and delist_date <= end_day and code not in cash_events:
            raise ValueError(
                f"covered delisting for {code} requires a source-labelled cash_delisting settlement event; "
                "list status alone cannot value a holding"
            )


def _apply_corporate_actions(
    day: pd.Timestamp,
    schedule: Mapping[pd.Timestamp, Sequence[Mapping[str, Any]]],
    shares: dict[str, int],
    sellable: dict[str, int],
    settlements: dict[str, list[tuple[pd.Timestamp, int]]],
    cash: float,
    calendar: Sequence[pd.Timestamp],
    day_index: int,
    applied_events: list[dict[str, Any]],
) -> float:
    for event in schedule.get(day, ()):
        code = str(event["code"])
        held = shares[code]
        event_type = str(event["type"])
        record: dict[str, Any] = {
            "date": day.date().isoformat(),
            "event_id": event["event_id"],
            "code": code,
            "type": event_type,
            "source_ref": event["source_ref"],
            "shares_before": held,
        }
        if event_type == "cash_dividend":
            amount = held * float(event["cash_per_share"])
            cash += amount
            record.update({"cash_amount": round(amount, 8), "shares_after": held})
        elif event_type == "share_distribution":
            resulting_shares = held * float(event["share_factor"])
            rounded_shares = round(resulting_shares)
            if not math.isclose(resulting_shares, rounded_shares, rel_tol=0.0, abs_tol=1e-8):
                raise ValueError(
                    f"corporate action {event['event_id']} produces fractional shares; provide a dedicated event adapter"
                )
            added = int(rounded_shares) - held
            shares[code] = int(rounded_shares)
            sellable_on = event.get("sellable_on")
            available_day = (
                pd.Timestamp(sellable_on)
                if sellable_on is not None
                else calendar[min(day_index + 1, len(calendar) - 1)]
            )
            settlements[code].append((available_day, added))
            record.update({"shares_added": added, "shares_after": shares[code], "sellable_on": available_day.date().isoformat()})
        else:  # cash_delisting
            amount = held * float(event["cash_settlement_per_share"])
            cash += amount
            shares[code] = 0
            sellable[code] = 0
            settlements[code] = []
            record.update({"cash_amount": round(amount, 8), "shares_after": 0})
        applied_events.append(record)
    return cash


def _positive_finite(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a positive finite number") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{label} must be a positive finite number")
    return parsed


def _tradable_open(frame: pd.DataFrame, day: pd.Timestamp) -> float | None:
    if day not in frame.index or not bool(frame.loc[day, "tradable"]):
        return None
    if str(frame.loc[day, "execution_status"]) != "tradable":
        return None
    value = frame.loc[day, "open"]
    return float(value) if pd.notna(value) and float(value) > 0 else None


def _cap_trade_quantity(
    quantity: int,
    frame: pd.DataFrame,
    day: pd.Timestamp,
    participation_rate: float | None,
    lot_size: int,
) -> tuple[int, bool]:
    if participation_rate is None:
        return quantity, False
    if day not in frame.index:
        return 0, quantity > 0
    capacity = _lot_floor(float(frame.loc[day, "volume"]) * participation_rate, lot_size)
    capped = min(quantity, capacity)
    return capped, capped < quantity


def _apply_slippage(open_price: float, side: str, slippage_bps: float) -> float:
    adjustment = slippage_bps / 10_000
    return open_price * (1 + adjustment if side == "buy" else 1 - adjustment)


def _lot_floor(value: float, lot_size: int) -> int:
    return max(0, int(value // lot_size) * lot_size)


def _settle_lots(lots: Sequence[tuple[pd.Timestamp, int]], day: pd.Timestamp) -> tuple[int, list[tuple[pd.Timestamp, int]]]:
    due = sum(quantity for available_on, quantity in lots if available_on <= day)
    return due, [(available_on, quantity) for available_on, quantity in lots if available_on > day]


def _trade(
    day: pd.Timestamp,
    code: str,
    side: str,
    shares: int,
    price: float,
    costs: float,
    *,
    capacity_limited: bool = False,
) -> dict[str, Any]:
    return {
        "date": day.date().isoformat(),
        "code": code,
        "side": side,
        "shares": shares,
        "price": price,
        "value": round(shares * price, 8),
        "costs": round(costs, 8),
        "capacity_limited": capacity_limited,
    }
