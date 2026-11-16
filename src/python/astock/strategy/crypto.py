"""Research-only multi-asset crypto time-series-momentum proposals.

The module deliberately stops at a dated, source-labelled paper allocation.
It has no exchange client, credential handling, order payload, or execution
assumption.  Crypto bars and funding observations are caller-supplied because
the proposal must retain the precise point-in-time source and availability
facts that an external data adapter observed.

The supported instrument types are liquid spot and perpetual markets.  Spot
targets are long-only; a negative trend in a spot market is recorded as an
unexpressed signal rather than silently converted into a short.  Perpetual
targets may be signed only when the supplied asset metadata explicitly marks
the venue/instrument as short-eligible.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

_DATA_QUALITY_RANKS = {
    "unverified": 0,
    "partial": 1,
    "source_labelled": 2,
    "point_in_time_verified": 3,
}
_POINT_IN_TIME_COVERAGE = {"verified", "partial", "unverified"}
_MARKET_TYPE_ALIASES = {"spot": "spot", "perpetual": "perpetual", "perp": "perpetual"}
_TRADING_STATUSES = {"tradable", "halted", "suspended", "delisted", "unknown"}


@dataclass(frozen=True)
class CryptoAssetSpec:
    """Dated eligibility and provenance facts for one crypto market.

    ``metadata_as_of`` is intentionally a timezone-aware timestamp rather
    than a date: crypto venues trade continuously, so a calendar-date label
    cannot establish that eligibility or venue facts were known at a signal
    cutoff.  ``source_ref`` identifies the archived or externally verifiable
    source for the asset facts, not an exchange execution destination.
    """

    asset_id: str
    symbol: str
    venue: str
    market_type: str
    quote_currency: str
    source_ref: str
    metadata_as_of: str
    data_quality: str
    point_in_time_coverage: str
    eligible: bool
    trading_status: str
    short_eligible: bool
    is_stablecoin: bool
    listing_age_days: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> CryptoAssetSpec:
        """Parse explicit, dated asset metadata without inferred defaults."""

        if not isinstance(value, Mapping):
            raise TypeError("crypto asset specification must be an object")
        asset_id = _required_text(value.get("asset_id"), "asset_id")
        symbol = _required_text(value.get("symbol"), "symbol")
        venue = _required_text(value.get("venue") or value.get("exchange"), "venue").lower()
        raw_market_type = _required_text(value.get("market_type"), "market_type").lower()
        market_type = _MARKET_TYPE_ALIASES.get(raw_market_type)
        if market_type is None:
            raise ValueError("market_type must be spot or perpetual")
        quote_currency = _required_text(value.get("quote_currency"), "quote_currency").upper()
        source_ref = _required_text(value.get("source_ref"), "source_ref")
        metadata_as_of = _required_text(value.get("metadata_as_of"), "metadata_as_of")
        data_quality = _normalise_data_quality(value.get("data_quality"), "data_quality")
        point_in_time_coverage = _normalise_point_in_time_coverage(
            value.get("point_in_time_coverage"), "point_in_time_coverage"
        )
        if "eligible" not in value:
            raise ValueError("eligible is required")
        eligible = _strict_bool(value.get("eligible"), "eligible")
        trading_status = _required_text(value.get("trading_status"), "trading_status").lower()
        if trading_status not in _TRADING_STATUSES:
            raise ValueError("trading_status is invalid")
        short_eligible = _strict_bool(value.get("short_eligible", False), "short_eligible")
        is_stablecoin = _strict_bool(value.get("is_stablecoin", False), "is_stablecoin")
        try:
            listing_age_days = int(value.get("listing_age_days"))
        except (TypeError, ValueError) as error:
            raise ValueError("listing_age_days must be a non-negative integer") from error
        if listing_age_days < 0:
            raise ValueError("listing_age_days must be a non-negative integer")
        return cls(
            asset_id=asset_id,
            symbol=symbol,
            venue=venue,
            market_type=market_type,
            quote_currency=quote_currency,
            source_ref=source_ref,
            metadata_as_of=metadata_as_of,
            data_quality=data_quality,
            point_in_time_coverage=point_in_time_coverage,
            eligible=eligible,
            trading_status=trading_status,
            short_eligible=short_eligible,
            is_stablecoin=is_stablecoin,
            listing_age_days=listing_age_days,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "exchange": self.venue,
            "market_type": self.market_type,
            "quote_currency": self.quote_currency,
            "source_ref": self.source_ref,
            "metadata_as_of": self.metadata_as_of,
            "data_quality": self.data_quality,
            "point_in_time_coverage": self.point_in_time_coverage,
            "eligible": self.eligible,
            "trading_status": self.trading_status,
            "short_eligible": self.short_eligible,
            "is_stablecoin": self.is_stablecoin,
            "listing_age_days": self.listing_age_days,
        }


@dataclass(frozen=True)
class CryptoTimeSeriesMomentumConfig:
    """Predeclared controls for a liquid spot/perpetual paper sleeve.

    Exposure weights are fractions of a paper risk-capital denominator, not
    exchange instructions.  ``max_total_gross_exposure`` is capped at one so
    the proposal can state a conservative stablecoin/cash residual explicitly
    instead of manufacturing leverage or collateral assumptions.
    """

    strategy_id: str = "crypto_liquid_tsmom"
    version: str = "v1"
    signal_windows: tuple[int, ...] = (7, 28, 84)
    signal_weights: tuple[float, ...] = (0.40, 0.35, 0.25)
    bar_interval_hours: float = 24.0
    volatility_lookback: int = 30
    minimum_history: int = 100
    entry_threshold: float = 0.25
    exit_threshold: float = 0.10
    annual_target_volatility: float = 0.20
    max_single_asset_exposure: float = 0.15
    max_total_gross_exposure: float = 0.50
    max_exchange_gross_exposure: float = 0.35
    minimum_bar_quote_volume: float = 5_000_000.0
    minimum_listing_age_days: int = 90
    maximum_bar_age_hours: float = 30.0
    maximum_metadata_age_hours: float = 168.0
    maximum_bar_gap_multiple: float = 1.5
    minimum_execution_delay_minutes: int = 5
    accepted_quote_currencies: tuple[str, ...] = ("USDT", "USDC", "USD")
    permitted_venues: tuple[str, ...] = ()
    require_point_in_time_coverage: bool = True
    minimum_data_quality: str = "source_labelled"
    require_funding_for_perpetual: bool = True
    minimum_funding_observations: int = 3
    maximum_funding_age_hours: float = 12.0
    minimum_funding_data_quality: str = "source_labelled"
    maximum_absolute_funding_rate: float = 0.05
    stablecoin_cash_asset_id: str = "USDT"
    stablecoin_cash_symbol: str = "USDT"
    cash_residual_source_ref: str = "derived:crypto-tsmom-unallocated-stablecoin-cash"

    def __post_init__(self) -> None:
        if len(self.signal_windows) < 2 or len(self.signal_windows) != len(self.signal_weights):
            raise ValueError("crypto signal_windows and signal_weights need matching multi-horizon values")
        if (
            any(not isinstance(window, int) or window <= 0 for window in self.signal_windows)
            or tuple(sorted(self.signal_windows)) != self.signal_windows
        ):
            raise ValueError("crypto signal_windows must be ascending positive integers")
        if any(weight < 0 or not math.isfinite(weight) for weight in self.signal_weights):
            raise ValueError("crypto signal_weights must be finite non-negative numbers")
        if not math.isclose(sum(self.signal_weights), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("crypto signal_weights must sum to one")
        if self.bar_interval_hours <= 0 or not math.isfinite(self.bar_interval_hours):
            raise ValueError("bar_interval_hours must be a positive finite number")
        if self.volatility_lookback < 2:
            raise ValueError("volatility_lookback must be at least two bars")
        required_history = max(max(self.signal_windows) + 1, self.volatility_lookback + 1)
        if self.minimum_history < required_history:
            raise ValueError("minimum_history is insufficient for trend and volatility windows")
        if not (0 <= self.exit_threshold < self.entry_threshold):
            raise ValueError("thresholds require 0 <= exit_threshold < entry_threshold")
        if self.annual_target_volatility <= 0 or not math.isfinite(self.annual_target_volatility):
            raise ValueError("annual_target_volatility must be positive and finite")
        for name, value in (
            ("max_single_asset_exposure", self.max_single_asset_exposure),
            ("max_total_gross_exposure", self.max_total_gross_exposure),
            ("max_exchange_gross_exposure", self.max_exchange_gross_exposure),
        ):
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if self.max_single_asset_exposure > self.max_total_gross_exposure:
            raise ValueError("max_single_asset_exposure cannot exceed max_total_gross_exposure")
        if self.max_exchange_gross_exposure < self.max_single_asset_exposure:
            raise ValueError("max_exchange_gross_exposure cannot be below max_single_asset_exposure")
        for name, value in (
            ("minimum_bar_quote_volume", self.minimum_bar_quote_volume),
            ("maximum_bar_age_hours", self.maximum_bar_age_hours),
            ("maximum_metadata_age_hours", self.maximum_metadata_age_hours),
            ("maximum_funding_age_hours", self.maximum_funding_age_hours),
            ("maximum_absolute_funding_rate", self.maximum_absolute_funding_rate),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a non-negative finite number")
        if self.maximum_bar_age_hours <= 0 or self.maximum_metadata_age_hours <= 0:
            raise ValueError("bar and metadata age limits must be positive")
        if self.maximum_bar_gap_multiple < 1 or not math.isfinite(self.maximum_bar_gap_multiple):
            raise ValueError("maximum_bar_gap_multiple must be finite and at least one")
        if self.minimum_listing_age_days < 0 or self.minimum_execution_delay_minutes < 0:
            raise ValueError("listing age and execution delay cannot be negative")
        if self.minimum_funding_observations <= 0:
            raise ValueError("minimum_funding_observations must be positive")
        currencies = tuple(str(item).strip().upper() for item in self.accepted_quote_currencies if str(item).strip())
        if not currencies:
            raise ValueError("accepted_quote_currencies cannot be empty")
        if len(set(currencies)) != len(currencies):
            raise ValueError("accepted_quote_currencies must be unique")
        venues = tuple(str(item).strip().lower() for item in self.permitted_venues if str(item).strip())
        if len(set(venues)) != len(venues):
            raise ValueError("permitted_venues must be unique")
        _normalise_data_quality(self.minimum_data_quality, "minimum_data_quality")
        _normalise_data_quality(self.minimum_funding_data_quality, "minimum_funding_data_quality")
        _required_text(self.stablecoin_cash_asset_id, "stablecoin_cash_asset_id")
        _required_text(self.stablecoin_cash_symbol, "stablecoin_cash_symbol")
        _required_text(self.cash_residual_source_ref, "cash_residual_source_ref")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> CryptoTimeSeriesMomentumConfig:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("crypto strategy configuration must be an object")
        defaults = cls()
        fields: dict[str, Any] = {
            name: value.get(name, getattr(defaults, name)) for name in cls.__dataclass_fields__
        }
        for name in ("signal_windows", "signal_weights", "accepted_quote_currencies", "permitted_venues"):
            raw = fields[name]
            if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
                raise TypeError(f"crypto {name} must be a sequence")
            fields[name] = tuple(raw)
        fields["signal_windows"] = tuple(int(item) for item in fields["signal_windows"])
        fields["signal_weights"] = tuple(float(item) for item in fields["signal_weights"])
        for name in ("volatility_lookback", "minimum_history", "minimum_listing_age_days", "minimum_execution_delay_minutes", "minimum_funding_observations"):
            fields[name] = int(fields[name])
        for name in (
            "bar_interval_hours",
            "entry_threshold",
            "exit_threshold",
            "annual_target_volatility",
            "max_single_asset_exposure",
            "max_total_gross_exposure",
            "max_exchange_gross_exposure",
            "minimum_bar_quote_volume",
            "maximum_bar_age_hours",
            "maximum_metadata_age_hours",
            "maximum_bar_gap_multiple",
            "maximum_funding_age_hours",
            "maximum_absolute_funding_rate",
        ):
            fields[name] = float(fields[name])
        for name in ("require_point_in_time_coverage", "require_funding_for_perpetual"):
            fields[name] = _strict_bool(fields[name], name)
        for name in (
            "strategy_id",
            "version",
            "minimum_data_quality",
            "minimum_funding_data_quality",
            "stablecoin_cash_asset_id",
            "stablecoin_cash_symbol",
            "cash_residual_source_ref",
        ):
            fields[name] = str(fields[name])
        fields["accepted_quote_currencies"] = tuple(str(item).upper() for item in fields["accepted_quote_currencies"])
        fields["permitted_venues"] = tuple(str(item).lower() for item in fields["permitted_venues"])
        return cls(**fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "version": self.version,
            "signal_windows": list(self.signal_windows),
            "signal_weights": list(self.signal_weights),
            "bar_interval_hours": self.bar_interval_hours,
            "volatility_lookback": self.volatility_lookback,
            "minimum_history": self.minimum_history,
            "entry_threshold": self.entry_threshold,
            "exit_threshold": self.exit_threshold,
            "annual_target_volatility": self.annual_target_volatility,
            "max_single_asset_exposure": self.max_single_asset_exposure,
            "max_total_gross_exposure": self.max_total_gross_exposure,
            "max_exchange_gross_exposure": self.max_exchange_gross_exposure,
            "minimum_bar_quote_volume": self.minimum_bar_quote_volume,
            "minimum_listing_age_days": self.minimum_listing_age_days,
            "maximum_bar_age_hours": self.maximum_bar_age_hours,
            "maximum_metadata_age_hours": self.maximum_metadata_age_hours,
            "maximum_bar_gap_multiple": self.maximum_bar_gap_multiple,
            "minimum_execution_delay_minutes": self.minimum_execution_delay_minutes,
            "accepted_quote_currencies": list(self.accepted_quote_currencies),
            "permitted_venues": list(self.permitted_venues),
            "require_point_in_time_coverage": self.require_point_in_time_coverage,
            "minimum_data_quality": self.minimum_data_quality,
            "require_funding_for_perpetual": self.require_funding_for_perpetual,
            "minimum_funding_observations": self.minimum_funding_observations,
            "maximum_funding_age_hours": self.maximum_funding_age_hours,
            "minimum_funding_data_quality": self.minimum_funding_data_quality,
            "maximum_absolute_funding_rate": self.maximum_absolute_funding_rate,
            "stablecoin_cash_asset_id": self.stablecoin_cash_asset_id,
            "stablecoin_cash_symbol": self.stablecoin_cash_symbol,
            "cash_residual_source_ref": self.cash_residual_source_ref,
        }


class _CryptoTimeSeriesMomentumStrategy:
    """Create a source-auditable crypto trend proposal without execution.

    The caller must provide a timezone-aware ``as_of`` value.  Every OHLCV
    observation used by the signal needs its own ``timestamp``, ``available_at``
    and ``source_ref``.  The latter prevents a bar that was only published
    after the cutoff from becoming a hidden look-ahead input.
    """

    def __init__(self, config: CryptoTimeSeriesMomentumConfig | None = None) -> None:
        self.config = config or CryptoTimeSeriesMomentumConfig()

    def generate_proposal(
        self,
        market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any]],
        assets: Mapping[str, CryptoAssetSpec | Mapping[str, Any]],
        *,
        as_of: str | datetime,
        funding_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any]] | None = None,
        previous_weights: Mapping[str, float] | None = None,
        source_refs: Sequence[str] = (),
        source_archive_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Generate deterministic, bounded paper targets from dated inputs.

        ``market_data`` maps ``asset_id`` to OHLCV bars.  Each bar requires
        ``timestamp``, ``available_at``, ``source_ref``, ``open``, ``high``,
        ``low``, ``close``, ``volume`` and ``tradable``.  A bar timestamp is
        interpreted as the end of its completed interval.  Perpetual funding
        observations are optional at the API boundary, but are an eligibility
        blocker by default for a perpetual target.
        """

        if not isinstance(market_data, Mapping):
            raise TypeError("crypto market_data must be an asset mapping")
        if not isinstance(assets, Mapping) or not assets:
            raise ValueError("crypto assets must be a non-empty asset mapping")
        if funding_data is not None and not isinstance(funding_data, Mapping):
            raise TypeError("crypto funding_data must be an asset mapping when supplied")
        observation_time = _parse_utc_timestamp(as_of, "as_of")
        prior_weights = _normalise_previous_weights(previous_weights)
        proposal_sources = _unique_strings(source_refs)
        archive_ids = _unique_strings(source_archive_ids)
        candidates: list[dict[str, Any]] = []
        blockers: list[dict[str, str]] = []
        warnings: list[str] = []
        assurance_assets: list[dict[str, Any]] = []
        assurance_funding: list[dict[str, Any]] = []
        degraded_input = False

        unknown_market_data = sorted(
            {str(key) for key in market_data}.difference(str(key) for key in assets)
        )
        if unknown_market_data:
            warnings.append(
                "Market data was supplied for unmapped asset ids and was excluded: "
                + ", ".join(unknown_market_data)
            )

        for raw_asset_id in sorted(assets, key=lambda item: str(item)):
            mapping_key = str(raw_asset_id).strip()
            raw_spec = assets[raw_asset_id]
            try:
                spec = (
                    CryptoAssetSpec.from_mapping(raw_spec.to_dict())
                    if isinstance(raw_spec, CryptoAssetSpec)
                    else CryptoAssetSpec.from_mapping(raw_spec)
                )
                if spec.asset_id != mapping_key:
                    raise ValueError("asset mapping keys must match asset_id")
            except (TypeError, ValueError) as error:
                blockers.append(_blocker(mapping_key or "unknown", "asset_specification", str(error)))
                degraded_input = True
                continue
            proposal_sources = _unique_strings([*proposal_sources, spec.source_ref])
            issue = _asset_eligibility_issue(spec, observation_time, self.config)
            if issue is not None:
                gate, reason = issue
                blockers.append(_blocker(spec.asset_id, gate, reason, symbol=spec.symbol))
                assurance_assets.append(_asset_assurance(spec, status="blocked", reason=reason))
                if gate in {"data_quality", "point_in_time"}:
                    degraded_input = True
                continue
            if spec.asset_id not in market_data:
                reason = "missing OHLCV input for asset"
                blockers.append(_blocker(spec.asset_id, "ohlcv_input", reason, symbol=spec.symbol))
                assurance_assets.append(_asset_assurance(spec, status="blocked", reason=reason))
                degraded_input = True
                continue
            frame, bar_assurance, bar_sources, bar_issue = _normalise_bars(
                market_data[spec.asset_id],
                spec.asset_id,
                observation_time,
                self.config,
            )
            proposal_sources = _unique_strings([*proposal_sources, *bar_sources])
            if bar_issue is not None or frame is None:
                reason = bar_issue or "invalid OHLCV input"
                blockers.append(_blocker(spec.asset_id, "point_in_time", reason, symbol=spec.symbol))
                assurance_assets.append(_asset_assurance(spec, status="blocked", reason=reason))
                degraded_input = True
                continue
            funding_summary: dict[str, Any] | None = None
            if spec.market_type == "perpetual":
                funding_raw = None if funding_data is None else funding_data.get(spec.asset_id)
                funding_summary, funding_sources, funding_issue = _normalise_funding(
                    funding_raw,
                    spec.asset_id,
                    observation_time,
                    self.config,
                )
                proposal_sources = _unique_strings([*proposal_sources, *funding_sources])
                if funding_issue is not None:
                    if self.config.require_funding_for_perpetual:
                        blockers.append(
                            _blocker(spec.asset_id, "funding_quality", funding_issue, symbol=spec.symbol)
                        )
                        assurance_assets.append(
                            _asset_assurance(spec, status="blocked", reason=funding_issue, bars=bar_assurance)
                        )
                        assurance_funding.append(
                            _funding_assurance(spec.asset_id, status="blocked", reason=funding_issue)
                        )
                        degraded_input = True
                        continue
                    funding_summary = {
                        "status": "not_verified",
                        "reason": funding_issue,
                        "latest_funding_at": None,
                        "latest_funding_rate": None,
                        "mean_funding_rate": None,
                        "observations": 0,
                    }
                    warnings.append(
                        f"{spec.asset_id}: funding-quality gate was relaxed by configuration: {funding_issue}"
                    )
                    degraded_input = True
                assurance_funding.append(
                    _funding_assurance(
                        spec.asset_id,
                        status=str(funding_summary["status"]),
                        summary=funding_summary,
                    )
                )
            candidate, candidate_issue = _trend_candidate(
                frame,
                spec,
                self.config,
                prior_weights.get(spec.asset_id, 0.0),
                funding_summary,
            )
            if candidate_issue is not None or candidate is None:
                gate = "liquidity" if candidate_issue and "liquidity" in candidate_issue else "trend_input"
                blockers.append(_blocker(spec.asset_id, gate, candidate_issue or "invalid trend input", symbol=spec.symbol))
                assurance_assets.append(
                    _asset_assurance(spec, status="blocked", reason=candidate_issue or "invalid trend input", bars=bar_assurance)
                )
                if gate == "trend_input":
                    degraded_input = True
                continue
            assurance_assets.append(_asset_assurance(spec, status="accepted", bars=bar_assurance))
            if candidate["direction"] == 0:
                if candidate["unexpressed_short_signal"]:
                    warnings.append(
                        f"{spec.asset_id}: negative trend is not expressed because the eligible market is not short-eligible."
                    )
                continue
            candidates.append(candidate)

        targets, concentration, sizing_warnings = _size_candidates(candidates, self.config)
        warnings.extend(sizing_warnings)
        gross_target_weight = sum(abs(float(target["target_weight"])) for target in targets)
        long_target_weight = sum(max(0.0, float(target["target_weight"])) for target in targets)
        short_target_weight = sum(max(0.0, -float(target["target_weight"])) for target in targets)
        cash_weight = max(0.0, 1.0 - gross_target_weight)
        latest_available_at = _latest_available_at(assurance_assets)
        earliest_rebalance_at = max(observation_time, latest_available_at or observation_time) + timedelta(
            minutes=self.config.minimum_execution_delay_minutes
        )
        data_quality = _proposal_data_quality(
            targets=targets,
            blockers=blockers,
            degraded_input=degraded_input,
            config=self.config,
        )
        if not targets and not blockers:
            warnings.append("No eligible asset has a trend signal above the configured entry threshold.")
        if not proposal_sources:
            # This should be unreachable because every valid asset requires a source ref,
            # but it remains an explicit proposal-level protection for malformed inputs.
            blockers.append(_blocker("proposal", "source_provenance", "no source references were retained"))
            data_quality = "blocked"
        cash_residual = {
            "asset_class": "stablecoin_cash",
            "asset_id": self.config.stablecoin_cash_asset_id,
            "symbol": self.config.stablecoin_cash_symbol,
            "target_weight": round(cash_weight, 8),
            "source_ref": self.config.cash_residual_source_ref,
            "purpose": "unallocated paper capital reserve",
            "paper_only": True,
        }
        return {
            "schema_version": "crypto_time_series_momentum_proposal.v1",
            "strategy_id": self.config.strategy_id,
            "strategy_version": self.config.version,
            "as_of": observation_time.isoformat(),
            "effective_at": earliest_rebalance_at.isoformat(),
            "targets": targets,
            "gross_target_weight": round(gross_target_weight, 8),
            "long_target_weight": round(long_target_weight, 8),
            "short_target_weight": round(short_target_weight, 8),
            "net_target_weight": round(long_target_weight - short_target_weight, 8),
            "cash_weight": round(cash_weight, 8),
            "cash_residual": cash_residual,
            "venue_concentration": concentration,
            "execution_timing": {
                "market_schedule": "24x7",
                "signal_cutoff_at": observation_time.isoformat(),
                "latest_input_available_at": latest_available_at.isoformat() if latest_available_at else None,
                "minimum_execution_delay_minutes": self.config.minimum_execution_delay_minutes,
                "earliest_paper_rebalance_at": earliest_rebalance_at.isoformat(),
                "bar_interval_hours": self.config.bar_interval_hours,
                "status": "timing_checked_paper_only",
            },
            "data_quality": data_quality,
            "data_assurance": {
                "status": data_quality,
                "point_in_time_policy": {
                    "require_point_in_time_coverage": self.config.require_point_in_time_coverage,
                    "minimum_data_quality": self.config.minimum_data_quality,
                    "bar_availability_required": True,
                    "funding_availability_required_for_perpetual": self.config.require_funding_for_perpetual,
                },
                "assets": assurance_assets,
                "funding": assurance_funding,
            },
            "source_refs": proposal_sources,
            "source_archive_ids": archive_ids,
            "blockers": blockers,
            "warnings": list(dict.fromkeys(warnings + _base_warnings())),
            "research_only": True,
            "no_order_execution": True,
            "formal_decision_eligible": False,
        }


def _build_crypto_time_series_momentum_proposal(
    market_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any]],
    assets: Mapping[str, CryptoAssetSpec | Mapping[str, Any]],
    *,
    as_of: str | datetime,
    config: CryptoTimeSeriesMomentumConfig | Mapping[str, Any] | None = None,
    funding_data: Mapping[str, pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any]] | None = None,
    previous_weights: Mapping[str, float] | None = None,
    source_refs: Sequence[str] = (),
    source_archive_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Convenience capability for a dated, research-only crypto proposal."""

    resolved = (
        config
        if isinstance(config, CryptoTimeSeriesMomentumConfig)
        else CryptoTimeSeriesMomentumConfig.from_mapping(config)
    )
    return _CryptoTimeSeriesMomentumStrategy(resolved).generate_proposal(
        market_data,
        assets,
        as_of=as_of,
        funding_data=funding_data,
        previous_weights=previous_weights,
        source_refs=source_refs,
        source_archive_ids=source_archive_ids,
    )


def _asset_eligibility_issue(
    spec: CryptoAssetSpec,
    observation_time: pd.Timestamp,
    config: CryptoTimeSeriesMomentumConfig,
) -> tuple[str, str] | None:
    if not spec.eligible:
        return "asset_eligibility", "asset is not explicitly marked eligible"
    if spec.trading_status != "tradable":
        return "asset_eligibility", "asset trading status is not tradable"
    if spec.is_stablecoin:
        return "asset_eligibility", "stablecoins cannot be momentum risk targets"
    if spec.quote_currency not in config.accepted_quote_currencies:
        return "asset_eligibility", "quote currency is outside the configured collateral/cash universe"
    if config.permitted_venues and spec.venue not in config.permitted_venues:
        return "asset_eligibility", "venue is outside the configured permitted venue list"
    if spec.listing_age_days < config.minimum_listing_age_days:
        return "asset_eligibility", "listing age is below the configured eligibility threshold"
    if _DATA_QUALITY_RANKS[spec.data_quality] < _DATA_QUALITY_RANKS[config.minimum_data_quality]:
        return "data_quality", "asset data_quality is below the configured minimum"
    if config.require_point_in_time_coverage and spec.point_in_time_coverage != "verified":
        return "point_in_time", "asset point-in-time coverage is not verified"
    try:
        metadata_at = _parse_utc_timestamp(spec.metadata_as_of, "metadata_as_of")
    except ValueError as error:
        return "point_in_time", str(error)
    if metadata_at > observation_time:
        return "point_in_time", "asset metadata_as_of is after the proposal cutoff"
    age_hours = _hours_between(metadata_at, observation_time)
    if age_hours > config.maximum_metadata_age_hours:
        return "point_in_time", "asset metadata is older than the configured freshness limit"
    return None


def _normalise_bars(
    raw_value: pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any],
    asset_id: str,
    observation_time: pd.Timestamp,
    config: CryptoTimeSeriesMomentumConfig,
) -> tuple[pd.DataFrame | None, dict[str, Any], list[str], str | None]:
    try:
        records = _records_from_value(raw_value, "bars")
    except (TypeError, ValueError) as error:
        return None, {}, [], str(error)
    if not records:
        return None, {}, [], "OHLCV input is empty"
    rows: list[dict[str, Any]] = []
    sources: list[str] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            return None, {}, sources, f"OHLCV row {index} is not an object"
        try:
            timestamp = _parse_utc_timestamp(raw.get("timestamp"), f"OHLCV row {index} timestamp")
            available_at = _parse_utc_timestamp(raw.get("available_at"), f"OHLCV row {index} available_at")
            source_ref = _required_text(raw.get("source_ref"), f"OHLCV row {index} source_ref")
            if timestamp > observation_time:
                raise ValueError("OHLCV timestamp is after the proposal cutoff")
            if available_at < timestamp:
                raise ValueError("OHLCV available_at precedes its completed bar timestamp")
            if available_at > observation_time:
                raise ValueError("OHLCV observation was not available at the proposal cutoff")
            open_price = _positive_float(raw.get("open"), f"OHLCV row {index} open")
            high_price = _positive_float(raw.get("high"), f"OHLCV row {index} high")
            low_price = _positive_float(raw.get("low"), f"OHLCV row {index} low")
            close_price = _positive_float(raw.get("close"), f"OHLCV row {index} close")
            volume = _non_negative_float(raw.get("volume"), f"OHLCV row {index} volume")
            tradable = _strict_bool(raw.get("tradable"), f"OHLCV row {index} tradable")
            quote_volume = raw.get("quote_volume")
            if quote_volume is None:
                quote_volume = volume * close_price
            else:
                quote_volume = _non_negative_float(quote_volume, f"OHLCV row {index} quote_volume")
            if low_price > min(open_price, close_price) or high_price < max(open_price, close_price):
                raise ValueError("OHLCV high/low does not bound open and close")
        except ValueError as error:
            return None, {}, sources, str(error)
        rows.append(
            {
                "timestamp": timestamp,
                "available_at": available_at,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "quote_volume": quote_volume,
                "tradable": tradable,
                "source_ref": source_ref,
            }
        )
        sources.append(source_ref)
    frame = pd.DataFrame(rows).sort_values("timestamp", kind="stable").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        return None, {}, sources, f"{asset_id} OHLCV has duplicate timestamps"
    if len(frame) < config.minimum_history:
        return None, {}, sources, (
            f"OHLCV history is shorter than configured minimum ({len(frame)} < {config.minimum_history})"
        )
    intervals = frame["timestamp"].diff().dropna().dt.total_seconds().to_numpy(dtype=float) / 3600.0
    maximum_gap = config.bar_interval_hours * config.maximum_bar_gap_multiple
    if np.any(intervals > maximum_gap + 1e-9):
        return None, {}, sources, "OHLCV cadence has a gap larger than the configured 24/7 tolerance"
    if np.any(intervals < config.bar_interval_hours * 0.5 - 1e-9):
        return None, {}, sources, "OHLCV cadence is materially shorter than the configured bar interval"
    latest = frame.iloc[-1]
    if not bool(latest["tradable"]):
        return None, {}, sources, "latest OHLCV state is not tradable"
    if _hours_between(latest["timestamp"], observation_time) > config.maximum_bar_age_hours:
        return None, {}, sources, "latest OHLCV bar is older than the configured 24/7 freshness limit"
    assurance = {
        "asset_id": asset_id,
        "bars": len(frame),
        "bar_interval_hours": config.bar_interval_hours,
        "latest_bar_at": latest["timestamp"].isoformat(),
        "latest_available_at": latest["available_at"].isoformat(),
        "latest_bar_source_ref": str(latest["source_ref"]),
    }
    return frame, assurance, _unique_strings(sources), None


def _normalise_funding(
    raw_value: pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    asset_id: str,
    observation_time: pd.Timestamp,
    config: CryptoTimeSeriesMomentumConfig,
) -> tuple[dict[str, Any] | None, list[str], str | None]:
    if raw_value is None:
        return None, [], "funding data is missing for a perpetual market"
    try:
        records = _records_from_value(raw_value, "funding")
    except (TypeError, ValueError) as error:
        return None, [], str(error)
    if len(records) < config.minimum_funding_observations:
        return None, [], "funding history is shorter than the configured minimum"
    rows: list[dict[str, Any]] = []
    sources: list[str] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            return None, sources, f"funding row {index} is not an object"
        try:
            timestamp = _parse_utc_timestamp(raw.get("timestamp"), f"funding row {index} timestamp")
            available_at = _parse_utc_timestamp(raw.get("available_at"), f"funding row {index} available_at")
            source_ref = _required_text(raw.get("source_ref"), f"funding row {index} source_ref")
            quality = _normalise_data_quality(raw.get("data_quality"), f"funding row {index} data_quality")
            funding_rate = _finite_float(raw.get("funding_rate"), f"funding row {index} funding_rate")
            if timestamp > observation_time:
                raise ValueError("funding timestamp is after the proposal cutoff")
            if available_at < timestamp:
                raise ValueError("funding available_at precedes its observation timestamp")
            if available_at > observation_time:
                raise ValueError("funding observation was not available at the proposal cutoff")
            if abs(funding_rate) > config.maximum_absolute_funding_rate:
                raise ValueError("funding rate exceeds the configured data-quality sanity limit")
            if _DATA_QUALITY_RANKS[quality] < _DATA_QUALITY_RANKS[config.minimum_funding_data_quality]:
                raise ValueError("funding data_quality is below the configured minimum")
        except ValueError as error:
            return None, sources, str(error)
        rows.append(
            {
                "timestamp": timestamp,
                "available_at": available_at,
                "funding_rate": funding_rate,
                "source_ref": source_ref,
                "data_quality": quality,
            }
        )
        sources.append(source_ref)
    frame = pd.DataFrame(rows).sort_values("timestamp", kind="stable").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        return None, sources, f"{asset_id} funding has duplicate timestamps"
    latest = frame.iloc[-1]
    if _hours_between(latest["timestamp"], observation_time) > config.maximum_funding_age_hours:
        return None, sources, "latest funding observation is older than the configured freshness limit"
    return {
        "status": "verified",
        "latest_funding_at": latest["timestamp"].isoformat(),
        "latest_available_at": latest["available_at"].isoformat(),
        "latest_funding_rate": float(latest["funding_rate"]),
        "mean_funding_rate": float(frame["funding_rate"].mean()),
        "observations": len(frame),
        "source_ref": str(latest["source_ref"]),
    }, _unique_strings(sources), None


def _trend_candidate(
    frame: pd.DataFrame,
    spec: CryptoAssetSpec,
    config: CryptoTimeSeriesMomentumConfig,
    previous_weight: float,
    funding_summary: Mapping[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    latest = frame.iloc[-1]
    latest_quote_volume = float(latest["quote_volume"])
    if latest_quote_volume < config.minimum_bar_quote_volume:
        return None, "latest quote liquidity is below the configured threshold"
    close = frame["close"].to_numpy(dtype=float)
    returns = np.diff(np.log(close))
    if len(returns) < config.volatility_lookback:
        return None, "insufficient normalized returns for volatility sizing"
    daily_volatility = float(np.std(returns[-config.volatility_lookback :], ddof=1))
    if not math.isfinite(daily_volatility) or daily_volatility <= 0:
        return None, "realized volatility is non-positive or invalid"
    trend_components: dict[str, float] = {}
    standardised_components: list[float] = []
    for window in config.signal_windows:
        if len(close) <= window:
            return None, "insufficient OHLCV history for a configured trend window"
        raw_return = float(math.log(close[-1] / close[-1 - window]))
        trend_components[str(window)] = raw_return
        standardised_components.append(raw_return / (daily_volatility * math.sqrt(window)))
    signal_score = float(
        sum(weight * component for weight, component in zip(config.signal_weights, standardised_components, strict=True))
    )
    direction = _direction_with_hysteresis(signal_score, previous_weight, config)
    unexpressed_short_signal = False
    if direction < 0 and spec.market_type == "spot":
        direction = 0
        unexpressed_short_signal = True
    if direction < 0 and not spec.short_eligible:
        direction = 0
        unexpressed_short_signal = True
    periods_per_year = 365.0 * 24.0 / config.bar_interval_hours
    annualized_volatility = daily_volatility * math.sqrt(periods_per_year)
    if not math.isfinite(annualized_volatility) or annualized_volatility <= 0:
        return None, "annualized volatility is non-positive or invalid"
    scaled_weight = config.annual_target_volatility / annualized_volatility
    conviction = min(1.0, abs(signal_score))
    raw_weight = min(config.max_single_asset_exposure, scaled_weight * conviction)
    if not math.isfinite(raw_weight) or raw_weight <= 0:
        return None, "volatility scaling produced an invalid target weight"
    return {
        "spec": spec,
        "direction": direction,
        "unexpressed_short_signal": unexpressed_short_signal,
        "signal_score": signal_score,
        "daily_volatility": daily_volatility,
        "annualized_volatility": annualized_volatility,
        "trend_returns": trend_components,
        "reference_price": float(latest["close"]),
        "latest_quote_volume": latest_quote_volume,
        "raw_weight": raw_weight,
        "funding": dict(funding_summary) if funding_summary is not None else None,
        "market_data_source_ref": str(latest["source_ref"]),
    }, None


def _direction_with_hysteresis(
    signal_score: float,
    previous_weight: float,
    config: CryptoTimeSeriesMomentumConfig,
) -> int:
    if previous_weight > 0 and signal_score > config.exit_threshold:
        return 1
    if previous_weight < 0 and signal_score < -config.exit_threshold:
        return -1
    if signal_score >= config.entry_threshold:
        return 1
    if signal_score <= -config.entry_threshold:
        return -1
    return 0


def _size_candidates(
    candidates: Sequence[Mapping[str, Any]],
    config: CryptoTimeSeriesMomentumConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    active = [candidate for candidate in candidates if int(candidate["direction"]) != 0]
    if not active:
        return [], [], []
    raw_total = sum(float(item["raw_weight"]) for item in active)
    total_scale = min(1.0, config.max_total_gross_exposure / raw_total) if raw_total else 1.0
    preliminary = [
        {**dict(item), "preliminary_weight": float(item["raw_weight"]) * total_scale}
        for item in active
    ]
    by_venue: dict[str, list[dict[str, Any]]] = {}
    for candidate in preliminary:
        venue = str(candidate["spec"].venue)
        by_venue.setdefault(venue, []).append(candidate)
    venue_scales: dict[str, float] = {}
    concentration: list[dict[str, Any]] = []
    warnings: list[str] = []
    for venue in sorted(by_venue):
        members = by_venue[venue]
        uncapped = sum(float(item["preliminary_weight"]) for item in members)
        scale = min(1.0, config.max_exchange_gross_exposure / uncapped) if uncapped else 1.0
        venue_scales[venue] = scale
        final_gross = uncapped * scale
        concentration.append(
            {
                "venue": venue,
                "gross_exposure": round(final_gross, 8),
                "uncapped_gross_exposure": round(uncapped, 8),
                "max_exchange_gross_exposure": config.max_exchange_gross_exposure,
                "status": "capped" if scale < 1.0 - 1e-12 else "within_cap",
            }
        )
        if scale < 1.0 - 1e-12:
            warnings.append(
                f"{venue}: exchange concentration cap reduced paper gross exposure from {uncapped:.6f} to {final_gross:.6f}."
            )
    targets: list[dict[str, Any]] = []
    for candidate in sorted(
        preliminary,
        key=lambda item: (-abs(float(item["signal_score"])), str(item["spec"].asset_id)),
    ):
        spec: CryptoAssetSpec = candidate["spec"]
        gross_weight = min(
            config.max_single_asset_exposure,
            float(candidate["preliminary_weight"]) * venue_scales[spec.venue],
        )
        if gross_weight <= 0:
            continue
        signed_weight = int(candidate["direction"]) * gross_weight
        funding = candidate.get("funding")
        targets.append(
            {
                "asset_class": "crypto",
                "asset_id": spec.asset_id,
                "symbol": spec.symbol,
                "venue": spec.venue,
                "exchange": spec.venue,
                "market_type": spec.market_type,
                "short_eligible": spec.short_eligible,
                "target_weight": round(signed_weight, 8),
                "gross_weight": round(gross_weight, 8),
                "direction": "long" if signed_weight > 0 else "short",
                "signal_score": round(float(candidate["signal_score"]), 8),
                "trend_returns": {
                    key: round(float(value), 8) for key, value in candidate["trend_returns"].items()
                },
                "daily_volatility": round(float(candidate["daily_volatility"]), 10),
                "annualized_volatility": round(float(candidate["annualized_volatility"]), 10),
                "reference_price": round(float(candidate["reference_price"]), 8),
                "latest_quote_volume": round(float(candidate["latest_quote_volume"]), 8),
                "market_data_source_ref": candidate["market_data_source_ref"],
                "funding": funding,
                "source_ref": spec.source_ref,
                "rationale": "multi-horizon time-series momentum with volatility scaling",
                "paper_only": True,
            }
        )
    total = sum(abs(float(target["target_weight"])) for target in targets)
    if total > config.max_total_gross_exposure + 1e-8:
        # This should not occur after the deterministic scaling steps.  Keep an
        # explicit defensive cap rather than let floating-point noise create an
        # apparently unbounded proposal.
        final_scale = config.max_total_gross_exposure / total
        for target in targets:
            target["target_weight"] = round(float(target["target_weight"]) * final_scale, 8)
            target["gross_weight"] = round(abs(float(target["target_weight"])), 8)
        warnings.append("A defensive portfolio gross-exposure rescale was applied.")
    return targets, concentration, warnings


def _asset_assurance(
    spec: CryptoAssetSpec,
    *,
    status: str,
    reason: str | None = None,
    bars: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "asset_id": spec.asset_id,
        "symbol": spec.symbol,
        "venue": spec.venue,
        "status": status,
        "source_ref": spec.source_ref,
        "metadata_as_of": spec.metadata_as_of,
        "data_quality": spec.data_quality,
        "point_in_time_coverage": spec.point_in_time_coverage,
    }
    if bars is not None:
        result["ohlcv"] = dict(bars)
    if reason:
        result["reason"] = reason
    return result


def _funding_assurance(
    asset_id: str,
    *,
    status: str,
    reason: str | None = None,
    summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"asset_id": asset_id, "status": status}
    if summary is not None:
        result.update(dict(summary))
    if reason:
        result["reason"] = reason
    return result


def _latest_available_at(assets: Sequence[Mapping[str, Any]]) -> pd.Timestamp | None:
    values: list[pd.Timestamp] = []
    for asset in assets:
        ohlcv = asset.get("ohlcv")
        if not isinstance(ohlcv, Mapping):
            continue
        value = ohlcv.get("latest_available_at")
        if not value:
            continue
        try:
            values.append(_parse_utc_timestamp(value, "latest_available_at"))
        except ValueError:
            continue
    return max(values) if values else None


def _proposal_data_quality(
    *,
    targets: Sequence[Mapping[str, Any]],
    blockers: Sequence[Mapping[str, Any]],
    degraded_input: bool,
    config: CryptoTimeSeriesMomentumConfig,
) -> str:
    if not targets and blockers:
        return "blocked"
    if degraded_input:
        return "degraded"
    if config.require_point_in_time_coverage:
        return "point_in_time_verified"
    return "source_labelled_research"


def _records_from_value(
    value: pd.DataFrame | Sequence[Mapping[str, Any]] | Mapping[str, Any],
    kind: str,
) -> list[Mapping[str, Any]]:
    if isinstance(value, pd.DataFrame):
        return list(value.to_dict(orient="records"))
    raw: Any = value
    if isinstance(value, Mapping):
        for key in (("bars", "records", "data") if kind == "bars" else ("funding", "records", "data")):
            if key in value:
                raw = value[key]
                break
        else:
            raise ValueError(f"{kind} input object must contain an explicit record sequence")
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
        raise TypeError(f"{kind} input must be a sequence of records")
    return list(raw)


def _normalise_previous_weights(value: Mapping[str, float] | None) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("previous_weights must be an asset mapping")
    normalized: dict[str, float] = {}
    for raw_key, raw_weight in value.items():
        key = str(raw_key).strip()
        if not key:
            raise ValueError("previous_weights cannot contain an empty asset id")
        normalized[key] = _finite_float(raw_weight, f"previous_weights[{key}]")
    return normalized


def _blocker(asset_id: str, gate: str, reason: str, *, symbol: str | None = None) -> dict[str, str]:
    result = {"asset_id": asset_id, "gate": gate, "reason": reason}
    if symbol:
        result["symbol"] = symbol
    return result


def _base_warnings() -> list[str]:
    return [
        "This is a research-only paper proposal and never routes exchange, broker, custody, or wallet instructions.",
        "Crypto markets trade 24/7; outages, liquidations, venue controls, custody transfer delays and market gaps can make a paper target non-executable.",
        "Perpetual funding is venue-specific and can change materially after the dated observation; it is an eligibility/data-quality input, not a fill or carry forecast.",
        "The stablecoin/cash residual is an unallocated paper reserve, not a claim that a stablecoin is risk-free or immediately transferable.",
    ]


def _normalise_data_quality(value: Any, name: str) -> str:
    raw = _required_text(value, name).lower().replace("-", "_").replace(" ", "_")
    if raw == "verified":
        raw = "point_in_time_verified"
    if raw not in _DATA_QUALITY_RANKS:
        raise ValueError(
            f"{name} must be one of: " + ", ".join(sorted(_DATA_QUALITY_RANKS))
        )
    return raw


def _normalise_point_in_time_coverage(value: Any, name: str) -> str:
    raw = _required_text(value, name).lower()
    if raw not in _POINT_IN_TIME_COVERAGE:
        raise ValueError(f"{name} must be verified, partial, or unverified")
    return raw


def _required_text(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{name} is required")
    return result


def _strict_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise ValueError(f"{name} must be boolean")


def _finite_float(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _positive_float(value: Any, name: str) -> float:
    result = _finite_float(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def _non_negative_float(value: Any, name: str) -> float:
    result = _finite_float(value, name)
    if result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


def _parse_utc_timestamp(value: Any, name: str) -> pd.Timestamp:
    if value is None or not str(value).strip():
        raise ValueError(f"{name} is required and must be a timezone-aware ISO-8601 timestamp")
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp") from error
    if pd.isna(timestamp) or timestamp.tzinfo is None:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp")
    return timestamp.tz_convert("UTC")


def _hours_between(earlier: pd.Timestamp, later: pd.Timestamp) -> float:
    return float((later - earlier).total_seconds() / 3600.0)


def _unique_strings(values: Sequence[Any]) -> list[str]:
    if isinstance(values, (str, bytes)):
        values = (values,)
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


__all__ = [
    "CryptoAssetSpec",
    "CryptoTimeSeriesMomentumConfig",
]
