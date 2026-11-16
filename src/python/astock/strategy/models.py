"""Versioned contracts for personal-investor strategy research.

The strategy domain deliberately separates a *research proposal* from a
broker instruction.  A proposal can be backtested, paper-traded, reviewed and
manually reconciled, but it never contains an order-routing payload.

The contracts in this module are intentionally instrument-agnostic.  They are
used by the domestic-futures CTA implementation today and leave room for
long-only equity and event sleeves without pretending that every institutional
strategy can be replicated by an individual account.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class StrategyAvailability(str, Enum):
    """Whether a strategy is economically usable by a personal account."""

    AVAILABLE = "available"
    CONDITIONAL = "conditional"
    RESEARCH_ONLY = "research_only"
    NOT_REPLICABLE = "not_replicable"


class StrategyLifecycle(str, Enum):
    """Lifecycle is evidence-based; no object authorises execution."""

    DRAFT = "draft"
    PAPER = "paper"
    REVIEW = "review"
    DISABLED = "disabled"
    RETIRED = "retired"


@dataclass(frozen=True)
class FuturesAccessEvidence:
    """Dated broker/exchange eligibility facts for a personal futures account.

    This record intentionally contains no account number, credentials, or
    order-routing information.  It is only the minimum auditable evidence
    needed to prevent a generic ``futures_eligible`` flag from being treated
    as permission for every exchange and contract.
    """

    as_of: str
    source_ref: str
    data_entitlement_source_ref: str
    permitted_exchanges: tuple[str, ...]
    eligible_instruments: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> FuturesAccessEvidence:
        if not isinstance(value, Mapping):
            raise TypeError("futures_access_evidence must be an object")
        return cls(
            as_of=_required_iso_date(value.get("as_of"), "futures_access_evidence.as_of"),
            source_ref=_required_text(value.get("source_ref"), "futures_access_evidence.source_ref"),
            data_entitlement_source_ref=_required_text(
                value.get("data_entitlement_source_ref"),
                "futures_access_evidence.data_entitlement_source_ref",
            ),
            permitted_exchanges=_identifier_tuple(
                value.get("permitted_exchanges"),
                "futures_access_evidence.permitted_exchanges",
            ),
            eligible_instruments=_identifier_tuple(
                value.get("eligible_instruments"),
                "futures_access_evidence.eligible_instruments",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "source_ref": self.source_ref,
            "data_entitlement_source_ref": self.data_entitlement_source_ref,
            "permitted_exchanges": list(self.permitted_exchanges),
            "eligible_instruments": list(self.eligible_instruments),
        }


@dataclass(frozen=True)
class CryptoAccessEvidence:
    """Dated non-Mainland compliance, venue, custody and data evidence.

    The evidence is deliberately a *research gate*, not a legal opinion or a
    method for accessing a market.  China-mainland residents are rejected by
    the capability regardless of this object.
    """

    as_of: str
    source_ref: str
    data_entitlement_source_ref: str
    custody_review_source_ref: str
    approved_venues: tuple[str, ...]
    permitted_market_types: tuple[str, ...]
    short_eligible_venues: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> CryptoAccessEvidence:
        if not isinstance(value, Mapping):
            raise TypeError("crypto_access_evidence must be an object")
        market_types = _identifier_tuple(
            value.get("permitted_market_types"),
            "crypto_access_evidence.permitted_market_types",
        )
        invalid_types = sorted(set(market_types).difference({"spot", "perpetual"}))
        if invalid_types:
            raise ValueError(
                "crypto_access_evidence.permitted_market_types must contain only spot or perpetual"
            )
        return cls(
            as_of=_required_iso_timestamp(
                value.get("as_of"), "crypto_access_evidence.as_of"
            ),
            source_ref=_required_text(value.get("source_ref"), "crypto_access_evidence.source_ref"),
            data_entitlement_source_ref=_required_text(
                value.get("data_entitlement_source_ref"),
                "crypto_access_evidence.data_entitlement_source_ref",
            ),
            custody_review_source_ref=_required_text(
                value.get("custody_review_source_ref"),
                "crypto_access_evidence.custody_review_source_ref",
            ),
            approved_venues=_identifier_tuple(
                value.get("approved_venues"), "crypto_access_evidence.approved_venues"
            ),
            permitted_market_types=market_types,
            short_eligible_venues=_optional_identifier_tuple(
                value.get("short_eligible_venues"),
                "crypto_access_evidence.short_eligible_venues",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "source_ref": self.source_ref,
            "data_entitlement_source_ref": self.data_entitlement_source_ref,
            "custody_review_source_ref": self.custody_review_source_ref,
            "approved_venues": list(self.approved_venues),
            "permitted_market_types": list(self.permitted_market_types),
            "short_eligible_venues": list(self.short_eligible_venues),
        }


@dataclass(frozen=True)
class PersonalAccessProfile:
    """Facts that determine which strategy families are even admissible.

    ``futures_eligible`` is deliberately a separate fact from legal market
    access and data entitlement.  Having a futures account does not make an
    overseas, market-neutral, options-volatility, or institutional-credit
    strategy available.  ``lawful_crypto_market_access`` is only a
    self-attested access-profile fact.  It is not a legal opinion, cannot be
    inferred from global-market access or a listed market, and never
    establishes that crypto activity is lawful in the China mainland or any
    other regulated jurisdiction.
    """

    profile_id: str = "default"
    futures_eligible: bool = False
    option_eligible: bool = False
    margin_short_eligible: bool = False
    licensed_eod_data: bool = False
    lawful_global_market_access: bool = False
    lawful_crypto_market_access: bool = False
    permitted_markets: tuple[str, ...] = ()
    risk_capital: float | None = None
    as_of: str | None = None
    residency_jurisdiction: str | None = None
    futures_access_evidence: FuturesAccessEvidence | None = None
    crypto_access_evidence: CryptoAccessEvidence | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "futures_eligible",
            "option_eligible",
            "margin_short_eligible",
            "licensed_eod_data",
            "lawful_global_market_access",
            "lawful_crypto_market_access",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be an explicit boolean")
        if self.futures_access_evidence is not None and not isinstance(
            self.futures_access_evidence, FuturesAccessEvidence
        ):
            raise TypeError("futures_access_evidence must be FuturesAccessEvidence")
        if self.crypto_access_evidence is not None and not isinstance(
            self.crypto_access_evidence, CryptoAccessEvidence
        ):
            raise TypeError("crypto_access_evidence must be CryptoAccessEvidence")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> PersonalAccessProfile:
        raw = value or {}
        markets = raw.get("permitted_markets") or ()
        if isinstance(markets, (str, bytes)) or not isinstance(markets, Sequence):
            raise TypeError("permitted_markets must be a sequence of market identifiers")
        risk_capital = raw.get("risk_capital")
        if risk_capital is not None:
            risk_capital = _positive_finite(risk_capital, "risk_capital")
        raw_futures_evidence = raw.get("futures_access_evidence")
        raw_crypto_evidence = raw.get("crypto_access_evidence")
        if raw_futures_evidence is not None and not isinstance(raw_futures_evidence, Mapping):
            raise TypeError("futures_access_evidence must be an object")
        if raw_crypto_evidence is not None and not isinstance(raw_crypto_evidence, Mapping):
            raise TypeError("crypto_access_evidence must be an object")
        return cls(
            profile_id=str(raw.get("profile_id") or "default").strip() or "default",
            futures_eligible=_strict_bool(raw.get("futures_eligible", False), "futures_eligible"),
            option_eligible=_strict_bool(raw.get("option_eligible", False), "option_eligible"),
            margin_short_eligible=_strict_bool(
                raw.get("margin_short_eligible", False), "margin_short_eligible"
            ),
            licensed_eod_data=_strict_bool(raw.get("licensed_eod_data", False), "licensed_eod_data"),
            lawful_global_market_access=_strict_bool(
                raw.get("lawful_global_market_access", False), "lawful_global_market_access"
            ),
            lawful_crypto_market_access=_strict_bool(
                raw.get("lawful_crypto_market_access", False),
                "lawful_crypto_market_access",
            ),
            permitted_markets=tuple(
                sorted({str(item).strip().lower() for item in markets if str(item).strip()})
            ),
            risk_capital=risk_capital,
            as_of=_optional_text(raw.get("as_of")),
            residency_jurisdiction=_optional_text(raw.get("residency_jurisdiction")),
            futures_access_evidence=(
                FuturesAccessEvidence.from_mapping(raw_futures_evidence)
                if raw_futures_evidence is not None
                else None
            ),
            crypto_access_evidence=(
                CryptoAccessEvidence.from_mapping(raw_crypto_evidence)
                if raw_crypto_evidence is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "futures_eligible": self.futures_eligible,
            "option_eligible": self.option_eligible,
            "margin_short_eligible": self.margin_short_eligible,
            "licensed_eod_data": self.licensed_eod_data,
            "lawful_global_market_access": self.lawful_global_market_access,
            "lawful_crypto_market_access": self.lawful_crypto_market_access,
            "permitted_markets": list(self.permitted_markets),
            "risk_capital": self.risk_capital,
            "as_of": self.as_of,
            "residency_jurisdiction": self.residency_jurisdiction,
            "futures_access_evidence": (
                self.futures_access_evidence.to_dict()
                if self.futures_access_evidence is not None
                else None
            ),
            "crypto_access_evidence": (
                self.crypto_access_evidence.to_dict()
                if self.crypto_access_evidence is not None
                else None
            ),
        }

    def validate_futures_access(
        self,
        instruments: Sequence[FuturesInstrumentSpec],
    ) -> FuturesAccessEvidence:
        """Return dated access evidence only for explicitly eligible contracts."""

        if not self.futures_eligible:
            raise ValueError("futures eligibility is not recorded")
        evidence = self.futures_access_evidence
        if evidence is None:
            raise ValueError(
                "dated futures_access_evidence with broker/exchange instrument permissions is required"
            )
        for spec in instruments:
            if spec.exchange.lower() not in evidence.permitted_exchanges:
                raise ValueError(
                    f"futures access evidence does not permit exchange {spec.exchange} for {spec.instrument_id}"
                )
            if spec.instrument_id.lower() not in evidence.eligible_instruments:
                raise ValueError(
                    f"futures access evidence does not permit instrument {spec.instrument_id}"
                )
        return evidence

    def validate_crypto_access(
        self,
        assets: Sequence[Mapping[str, Any]],
    ) -> CryptoAccessEvidence:
        """Fail closed for domestic routes and undocumented venue permissions.

        The return value is deliberately evidence metadata only.  Calling it
        does not constitute a legal conclusion or authorise activity.
        """

        if not self.lawful_crypto_market_access:
            raise ValueError("lawful_crypto_market_access must be explicitly recorded")
        jurisdiction = (self.residency_jurisdiction or "").strip().upper()
        if not jurisdiction:
            raise ValueError("residency_jurisdiction is required for crypto research gating")
        if jurisdiction in {"CN", "CHN", "CHINA", "MAINLAND_CHINA", "CHINA_MAINLAND"}:
            raise ValueError(
                "this personal strategy system does not offer a crypto implementation route for China-mainland residents"
            )
        evidence = self.crypto_access_evidence
        if evidence is None:
            raise ValueError(
                "dated crypto_access_evidence with jurisdiction, venue, custody and data-entitlement records is required"
            )
        for asset in assets:
            venue = str(asset.get("venue") or asset.get("exchange") or "").strip().lower()
            market_type = str(asset.get("market_type") or "").strip().lower()
            if market_type == "perp":
                market_type = "perpetual"
            target_weight = float(asset.get("target_weight", 0.0))
            if venue not in evidence.approved_venues:
                raise ValueError(f"crypto access evidence does not permit venue {venue or 'unknown'}")
            if market_type not in evidence.permitted_market_types:
                raise ValueError(
                    f"crypto access evidence does not permit market type {market_type or 'unknown'}"
                )
            if target_weight < 0 and venue not in evidence.short_eligible_venues:
                raise ValueError(
                    f"crypto access evidence does not permit a short position at venue {venue}"
                )
        return evidence


@dataclass(frozen=True)
class StrategyDefinition:
    """A transparent strategy family entry in the personal strategy catalog."""

    strategy_id: str
    version: str
    name: str
    family: str
    availability: StrategyAvailability
    lifecycle: StrategyLifecycle
    asset_scope: tuple[str, ...]
    required_access: tuple[str, ...]
    required_data: tuple[str, ...]
    economic_engine: str
    personal_translation: str
    non_replicable_components: tuple[str, ...]
    risk_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "personal_strategy_definition.v1",
            "strategy_id": self.strategy_id,
            "version": self.version,
            "name": self.name,
            "family": self.family,
            "availability": self.availability.value,
            "lifecycle": self.lifecycle.value,
            "asset_scope": list(self.asset_scope),
            "required_access": list(self.required_access),
            "required_data": list(self.required_data),
            "economic_engine": self.economic_engine,
            "personal_translation": self.personal_translation,
            "non_replicable_components": list(self.non_replicable_components),
            "risk_notes": list(self.risk_notes),
            "research_only": True,
            "no_order_execution": True,
        }


@dataclass(frozen=True)
class FuturesInstrumentSpec:
    """Contract facts required before a futures target can be calculated.

    The caller must bind this record to a dated broker or exchange source.
    Multipliers and margin rates are therefore inputs rather than permanent
    hard-coded exchange assumptions.
    """

    instrument_id: str
    active_contract: str
    exchange: str
    group: str
    currency: str
    multiplier: float
    tick_size: float
    initial_margin_rate: float
    maintenance_margin_rate: float
    as_of: str
    source_ref: str
    max_contracts: int | None = None
    contract_lifecycle_coverage: str = "unverified"

    def __post_init__(self) -> None:
        _required_text(self.instrument_id, "instrument_id")
        _required_text(self.active_contract, "active_contract")
        _required_text(self.exchange, "exchange")
        _required_text(self.group, "group")
        _required_text(self.currency, "currency")
        _required_iso_date(self.as_of, "as_of")
        _required_text(self.source_ref, "source_ref")
        _positive_finite(self.multiplier, "multiplier")
        _positive_finite(self.tick_size, "tick_size")
        initial_margin_rate = _positive_fraction(
            self.initial_margin_rate, "initial_margin_rate"
        )
        maintenance_margin_rate = _positive_fraction(
            self.maintenance_margin_rate, "maintenance_margin_rate"
        )
        if maintenance_margin_rate > initial_margin_rate:
            raise ValueError("maintenance_margin_rate cannot exceed initial_margin_rate")
        if self.max_contracts is not None:
            if isinstance(self.max_contracts, bool) or int(self.max_contracts) != self.max_contracts:
                raise ValueError("max_contracts must be a positive integer when supplied")
            if self.max_contracts <= 0:
                raise ValueError("max_contracts must be a positive integer when supplied")
        if self.contract_lifecycle_coverage not in {"verified", "proxy", "unverified"}:
            raise ValueError("contract_lifecycle_coverage must be verified, proxy, or unverified")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> FuturesInstrumentSpec:
        if not isinstance(value, Mapping):
            raise TypeError("futures instrument specification must be an object")
        instrument_id = _required_text(value.get("instrument_id"), "instrument_id")
        active_contract = _required_text(value.get("active_contract"), "active_contract")
        exchange = _required_text(value.get("exchange"), "exchange").lower()
        group = _required_text(value.get("group"), "group").lower()
        currency = _required_text(value.get("currency"), "currency").upper()
        as_of = _required_iso_date(value.get("as_of"), "as_of")
        source_ref = _required_text(value.get("source_ref"), "source_ref")
        multiplier = _positive_finite(value.get("multiplier"), "multiplier")
        tick_size = _positive_finite(value.get("tick_size"), "tick_size")
        initial_margin_rate = _positive_fraction(
            value.get("initial_margin_rate"), "initial_margin_rate"
        )
        maintenance_margin_rate = _positive_fraction(
            value.get("maintenance_margin_rate"), "maintenance_margin_rate"
        )
        if maintenance_margin_rate > initial_margin_rate:
            raise ValueError("maintenance_margin_rate cannot exceed initial_margin_rate")
        raw_cap = value.get("max_contracts")
        max_contracts: int | None = None
        if raw_cap is not None:
            try:
                max_contracts = int(raw_cap)
            except (TypeError, ValueError) as error:
                raise ValueError("max_contracts must be a positive integer when supplied") from error
            if max_contracts <= 0:
                raise ValueError("max_contracts must be a positive integer when supplied")
        contract_lifecycle_coverage = str(
            value.get("contract_lifecycle_coverage") or "unverified"
        ).strip().lower()
        if contract_lifecycle_coverage not in {"verified", "proxy", "unverified"}:
            raise ValueError(
                "contract_lifecycle_coverage must be verified, proxy, or unverified"
            )
        return cls(
            instrument_id=instrument_id,
            active_contract=active_contract,
            exchange=exchange,
            group=group,
            currency=currency,
            multiplier=multiplier,
            tick_size=tick_size,
            initial_margin_rate=initial_margin_rate,
            maintenance_margin_rate=maintenance_margin_rate,
            as_of=as_of,
            source_ref=source_ref,
            max_contracts=max_contracts,
            contract_lifecycle_coverage=contract_lifecycle_coverage,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "active_contract": self.active_contract,
            "exchange": self.exchange,
            "group": self.group,
            "currency": self.currency,
            "multiplier": self.multiplier,
            "tick_size": self.tick_size,
            "initial_margin_rate": self.initial_margin_rate,
            "maintenance_margin_rate": self.maintenance_margin_rate,
            "as_of": self.as_of,
            "source_ref": self.source_ref,
            "max_contracts": self.max_contracts,
            "contract_lifecycle_coverage": self.contract_lifecycle_coverage,
        }


@dataclass(frozen=True)
class CTAStrategyConfig:
    """Predeclared parameters for a low-frequency time-series momentum sleeve."""

    strategy_id: str = "domestic_futures_cta_tsmom"
    version: str = "v1"
    signal_windows: tuple[int, int, int] = (21, 63, 126)
    signal_weights: tuple[float, float, float] = (0.45, 0.35, 0.20)
    volatility_lookback: int = 60
    minimum_history: int = 160
    entry_threshold: float = 0.35
    exit_threshold: float = 0.15
    annual_target_volatility: float = 0.10
    max_margin_fraction: float = 0.25
    max_group_risk_fraction: float = 0.30
    max_instrument_risk_fraction: float = 0.12
    minimum_daily_volume: float = 0.0
    minimum_open_interest: float = 0.0
    minimum_days_to_expiry: int = 10
    rebalance_buffer_contracts: int = 1
    slippage_bps: float = 2.0
    commission_per_contract: float = 0.0

    def __post_init__(self) -> None:
        if len(self.signal_windows) != 3 or len(self.signal_weights) != 3:
            raise ValueError("CTA signal_windows and signal_weights must each contain three values")
        if any(window <= 0 for window in self.signal_windows) or tuple(sorted(self.signal_windows)) != self.signal_windows:
            raise ValueError("CTA signal_windows must be ascending positive integers")
        if any(weight < 0 or not math.isfinite(weight) for weight in self.signal_weights):
            raise ValueError("CTA signal_weights must be finite non-negative numbers")
        if not math.isclose(sum(self.signal_weights), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("CTA signal_weights must sum to one")
        if self.volatility_lookback < 20 or self.minimum_history < max(self.signal_windows):
            raise ValueError("CTA history and volatility lookbacks are insufficient")
        if not (0 <= self.exit_threshold < self.entry_threshold):
            raise ValueError("CTA thresholds require 0 <= exit_threshold < entry_threshold")
        for name, value in (
            ("annual_target_volatility", self.annual_target_volatility),
            ("max_margin_fraction", self.max_margin_fraction),
            ("max_group_risk_fraction", self.max_group_risk_fraction),
            ("max_instrument_risk_fraction", self.max_instrument_risk_fraction),
        ):
            _fraction(value, name)
        if self.annual_target_volatility <= 0 or self.max_margin_fraction <= 0:
            raise ValueError("CTA annual_target_volatility and max_margin_fraction must be positive")
        if self.minimum_daily_volume < 0 or self.minimum_open_interest < 0:
            raise ValueError("CTA liquidity thresholds cannot be negative")
        if self.minimum_days_to_expiry < 0 or self.rebalance_buffer_contracts < 0:
            raise ValueError("CTA days-to-expiry and rebalance buffers cannot be negative")
        if self.slippage_bps < 0 or self.commission_per_contract < 0:
            raise ValueError("CTA execution costs cannot be negative")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> CTAStrategyConfig:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("CTA configuration must be an object")
        defaults = cls()
        fields = {
            name: value.get(name, getattr(defaults, name))
            for name in cls.__dataclass_fields__
        }
        for name in ("signal_windows", "signal_weights"):
            raw = fields[name]
            if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
                raise TypeError(f"CTA {name} must be a sequence")
            fields[name] = tuple(raw)
        for name in (
            "volatility_lookback",
            "minimum_history",
            "minimum_days_to_expiry",
            "rebalance_buffer_contracts",
        ):
            fields[name] = int(fields[name])
        for name in (
            "entry_threshold",
            "exit_threshold",
            "annual_target_volatility",
            "max_margin_fraction",
            "max_group_risk_fraction",
            "max_instrument_risk_fraction",
            "minimum_daily_volume",
            "minimum_open_interest",
            "slippage_bps",
            "commission_per_contract",
        ):
            fields[name] = float(fields[name])
        fields["strategy_id"] = str(fields["strategy_id"])
        fields["version"] = str(fields["version"])
        return cls(**fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "version": self.version,
            "signal_windows": list(self.signal_windows),
            "signal_weights": list(self.signal_weights),
            "volatility_lookback": self.volatility_lookback,
            "minimum_history": self.minimum_history,
            "entry_threshold": self.entry_threshold,
            "exit_threshold": self.exit_threshold,
            "annual_target_volatility": self.annual_target_volatility,
            "max_margin_fraction": self.max_margin_fraction,
            "max_group_risk_fraction": self.max_group_risk_fraction,
            "max_instrument_risk_fraction": self.max_instrument_risk_fraction,
            "minimum_daily_volume": self.minimum_daily_volume,
            "minimum_open_interest": self.minimum_open_interest,
            "minimum_days_to_expiry": self.minimum_days_to_expiry,
            "rebalance_buffer_contracts": self.rebalance_buffer_contracts,
            "slippage_bps": self.slippage_bps,
            "commission_per_contract": self.commission_per_contract,
        }


@dataclass(frozen=True)
class FuturesTarget:
    """One signed paper target, expressed in actual contract units."""

    instrument_id: str
    active_contract: str
    group: str
    direction: int
    target_contracts: int
    raw_target_contracts: float
    signal_score: float
    daily_volatility: float
    reference_price: float
    risk_dollars: float
    margin_required: float
    source_ref: str
    contract_multiplier: float
    initial_margin_rate: float
    maintenance_margin_rate: float
    position_limit: int
    contract_facts_as_of: str
    contract_source_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "active_contract": self.active_contract,
            "group": self.group,
            "direction": self.direction,
            "target_contracts": self.target_contracts,
            "raw_target_contracts": self.raw_target_contracts,
            "signal_score": self.signal_score,
            "daily_volatility": self.daily_volatility,
            "reference_price": self.reference_price,
            "risk_dollars": self.risk_dollars,
            "margin_required": self.margin_required,
            "source_ref": self.source_ref,
            "contract_multiplier": self.contract_multiplier,
            "initial_margin_rate": self.initial_margin_rate,
            "maintenance_margin_rate": self.maintenance_margin_rate,
            "position_limit": self.position_limit,
            "contract_facts_as_of": self.contract_facts_as_of,
            "contract_source_ref": self.contract_source_ref,
            "contract_facts": {
                "active_contract": self.active_contract,
                "as_of": self.contract_facts_as_of,
                "source_ref": self.contract_source_ref,
                "data_quality": "point_in_time_verified",
                "point_in_time_coverage": "verified",
                "trading_status": "tradable",
                "reference_price": self.reference_price,
                "contract_multiplier": self.contract_multiplier,
                "initial_margin_rate": self.initial_margin_rate,
                "maintenance_margin_rate": self.maintenance_margin_rate,
                "position_limit": self.position_limit,
            },
        }


@dataclass(frozen=True)
class StrategyProposal:
    """A paper-only strategy output with evidence and explicit failure states."""

    strategy_id: str
    strategy_version: str
    as_of: str
    effective_session: str | None
    targets: tuple[FuturesTarget, ...]
    gross_notional: float
    gross_margin: float
    estimated_daily_volatility: float
    data_quality: str
    source_archive_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    research_only: bool = True
    no_order_execution: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "personal_strategy_proposal.v1",
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "as_of": self.as_of,
            "effective_session": self.effective_session,
            "targets": [target.to_dict() for target in self.targets],
            "gross_notional": self.gross_notional,
            "gross_margin": self.gross_margin,
            "estimated_daily_volatility": self.estimated_daily_volatility,
            "data_quality": self.data_quality,
            "source_archive_ids": list(self.source_archive_ids),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "research_only": self.research_only,
            "no_order_execution": self.no_order_execution,
        }


def _required_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _required_iso_date(value: Any, field_name: str) -> str:
    text = _required_text(value, field_name)
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO date (YYYY-MM-DD)") from error


def _required_iso_timestamp(value: Any, field_name: str) -> str:
    text = _required_text(value, field_name)
    candidate = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed.isoformat()


def _identifier_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a non-empty sequence of identifiers")
    result = tuple(sorted({str(item).strip().lower() for item in value if str(item).strip()}))
    if not result:
        raise ValueError(f"{field_name} must contain at least one identifier")
    return result


def _optional_identifier_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a sequence of identifiers")
    return tuple(sorted({str(item).strip().lower() for item in value if str(item).strip()}))


def _strict_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise ValueError(f"{field_name} must be boolean")


def _positive_finite(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a positive finite number") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return parsed


def _fraction(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a finite fraction in [0, 1]") from error
    if not math.isfinite(parsed) or parsed < 0 or parsed > 1:
        raise ValueError(f"{field_name} must be a finite fraction in [0, 1]")
    return parsed


def _positive_fraction(value: Any, field_name: str) -> float:
    parsed = _fraction(value, field_name)
    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive finite fraction in (0, 1]")
    return parsed
