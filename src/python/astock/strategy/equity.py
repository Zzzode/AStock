"""Transparent long-only equity sleeves for personal-investor research.

These are deliberately *not* market-neutral factor or full institutional
event-arbitrage implementations.  They make a bounded A-share translation:
liquid long-only targets, current-state hard vetoes, diversified position caps,
and explicit source references.  They produce paper targets only.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any


_ASHARE_EXCHANGES = {"sse", "szse", "bse"}
_ASHARE_MARKETS = {"ashare", "a_share", "a-share"}
_MAX_TRADING_STATE_AGE = timedelta(hours=24)


def _as_of_timestamp(value: str | date | datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        stamp = value
    if isinstance(value, date):
        raise TypeError("as_of must be a timezone-aware ISO-8601 timestamp, not a date")
    else:
        raw = str(value).strip()
        normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        try:
            stamp = datetime.fromisoformat(normalized)
        except ValueError as error:
            raise ValueError("as_of must be a timezone-aware ISO-8601 timestamp") from error
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("as_of must be a timezone-aware ISO-8601 timestamp")
    return stamp.astimezone(UTC)


def _timestamp(value: Any, name: str) -> datetime:
    raw = _required_text(value, name)
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        stamp = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp") from error
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp")
    return stamp.astimezone(UTC)


def _strict_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise ValueError(f"{name} must be boolean")


def _finite_fraction(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _required_text(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{name} is required")
    return result


@dataclass(frozen=True)
class AShareFactorTiltConfig:
    """Predeclared rules for a low-turnover, long-only factor tilt."""

    strategy_id: str = "ashare_factor_tilt"
    version: str = "v1"
    max_positions: int = 20
    max_gross_weight: float = 0.40
    max_position_weight: float = 0.06
    max_industry_weight: float = 0.25
    minimum_average_daily_turnover: float = 20_000_000.0
    minimum_listing_days: int = 180
    required_factor_fields: tuple[str, ...] = (
        "quality_score",
        "value_score",
        "momentum_score",
        "investment_score",
    )
    factor_weights: tuple[float, ...] = (0.30, 0.25, 0.25, 0.20)

    def __post_init__(self) -> None:
        if self.max_positions <= 0:
            raise ValueError("max_positions must be positive")
        for name, value in (
            ("max_gross_weight", self.max_gross_weight),
            ("max_position_weight", self.max_position_weight),
            ("max_industry_weight", self.max_industry_weight),
        ):
            if not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if self.max_industry_weight < self.max_position_weight:
            raise ValueError("max_industry_weight cannot be below max_position_weight")
        if self.max_gross_weight < self.max_position_weight:
            raise ValueError("max_gross_weight cannot be below max_position_weight")
        if self.minimum_average_daily_turnover <= 0 or self.minimum_listing_days < 0:
            raise ValueError("liquidity and listing thresholds are invalid")
        if len(self.required_factor_fields) != len(self.factor_weights) or not self.factor_weights:
            raise ValueError("factor fields and weights must have the same non-zero length")
        if any(weight < 0 or not math.isfinite(weight) for weight in self.factor_weights):
            raise ValueError("factor weights must be finite non-negative values")
        if not math.isclose(sum(self.factor_weights), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("factor_weights must sum to one")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> AShareFactorTiltConfig:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("factor configuration must be an object")
        default = cls()
        fields: dict[str, Any] = {
            name: value.get(name, getattr(default, name)) for name in cls.__dataclass_fields__
        }
        fields["strategy_id"] = str(fields["strategy_id"])
        fields["version"] = str(fields["version"])
        fields["max_positions"] = int(fields["max_positions"])
        fields["minimum_listing_days"] = int(fields["minimum_listing_days"])
        for name in (
            "max_gross_weight",
            "max_position_weight",
            "max_industry_weight",
            "minimum_average_daily_turnover",
        ):
            fields[name] = _finite_fraction(fields[name], name)
        for name in ("required_factor_fields", "factor_weights"):
            raw = fields[name]
            if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
                raise TypeError(f"{name} must be a sequence")
            fields[name] = tuple(raw)
        fields["required_factor_fields"] = tuple(str(item) for item in fields["required_factor_fields"])
        fields["factor_weights"] = tuple(float(item) for item in fields["factor_weights"])
        return cls(**fields)


@dataclass(frozen=True)
class EarningsEventRepricingConfig:
    """Predeclared public-announcement event-sleeve rules."""

    strategy_id: str = "earnings_event_repricing"
    version: str = "v1"
    maximum_event_age_days: int = 5
    max_positions: int = 12
    max_gross_weight: float = 0.20
    max_position_weight: float = 0.08
    max_industry_weight: float = 0.30
    minimum_surprise_score: float = 0.50
    minimum_average_daily_turnover: float = 20_000_000.0

    def __post_init__(self) -> None:
        if self.maximum_event_age_days < 0 or self.max_positions <= 0:
            raise ValueError("event age and max_positions must be valid")
        for name, value in (
            ("max_gross_weight", self.max_gross_weight),
            ("max_position_weight", self.max_position_weight),
            ("max_industry_weight", self.max_industry_weight),
        ):
            if not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if self.max_industry_weight < self.max_position_weight:
            raise ValueError("max_industry_weight cannot be below max_position_weight")
        if self.max_gross_weight < self.max_position_weight:
            raise ValueError("max_gross_weight cannot be below max_position_weight")
        if self.minimum_average_daily_turnover <= 0:
            raise ValueError("minimum_average_daily_turnover must be positive")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> EarningsEventRepricingConfig:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("event configuration must be an object")
        default = cls()
        fields: dict[str, Any] = {
            name: value.get(name, getattr(default, name)) for name in cls.__dataclass_fields__
        }
        fields["strategy_id"] = str(fields["strategy_id"])
        fields["version"] = str(fields["version"])
        fields["maximum_event_age_days"] = int(fields["maximum_event_age_days"])
        fields["max_positions"] = int(fields["max_positions"])
        for name in (
            "max_position_weight",
            "max_gross_weight",
            "max_industry_weight",
            "minimum_surprise_score",
            "minimum_average_daily_turnover",
        ):
            fields[name] = _finite_fraction(fields[name], name)
        return cls(**fields)


class AShareFactorTiltStrategy:
    """Build an industry-capped long-only factor-tilt paper proposal."""

    def __init__(self, config: AShareFactorTiltConfig | None = None) -> None:
        self.config = config or AShareFactorTiltConfig()

    def generate_proposal(
        self,
        universe: Sequence[Mapping[str, Any]],
        *,
        as_of: str | date | datetime | None = None,
        source_refs: Sequence[str] = (),
    ) -> dict[str, Any]:
        observation_time = _as_of_timestamp(as_of)
        candidates: list[dict[str, Any]] = []
        hard_vetoes: list[dict[str, str]] = []
        for raw in universe:
            candidate, veto = _factor_candidate(raw, self.config, observation_time)
            if veto is not None:
                hard_vetoes.append(veto)
            elif candidate is not None:
                candidates.append(candidate)
        targets = _allocate_equity_targets(
            candidates,
            self.config.max_positions,
            self.config.max_gross_weight,
            self.config.max_position_weight,
            self.config.max_industry_weight,
        )
        warnings = _equity_warnings(source_refs)
        if not targets:
            warnings.append("No security passed factor, liquidity, current trading-state, and A-share exit-risk gates.")
        return _equity_proposal(
            strategy_id=self.config.strategy_id,
            version=self.config.version,
            as_of=observation_time.isoformat(),
            targets=targets,
            hard_vetoes=hard_vetoes,
            source_refs=source_refs,
            warnings=warnings,
        )


class PublicAnnouncementEarningsRepricingStrategy:
    """Build a public-information, long-only post-announcement paper sleeve."""

    def __init__(self, config: EarningsEventRepricingConfig | None = None) -> None:
        self.config = config or EarningsEventRepricingConfig()

    def generate_proposal(
        self,
        announcements: Sequence[Mapping[str, Any]],
        *,
        as_of: str | date | datetime | None = None,
        source_refs: Sequence[str] = (),
    ) -> dict[str, Any]:
        observation_time = _as_of_timestamp(as_of)
        candidates: list[dict[str, Any]] = []
        hard_vetoes: list[dict[str, str]] = []
        for raw in announcements:
            candidate, veto = _event_candidate(raw, self.config, observation_time)
            if veto is not None:
                hard_vetoes.append(veto)
            elif candidate is not None:
                candidates.append(candidate)
        targets = _allocate_equity_targets(
            candidates,
            self.config.max_positions,
            self.config.max_gross_weight,
            self.config.max_position_weight,
            self.config.max_industry_weight,
        )
        warnings = _equity_warnings(source_refs)
        warnings.extend(
            [
                "The event score is a public-information ranking, not a claim that analyst expectations or post-earnings drift are fully observed.",
                "A-share T+1, gaps, trading halts and price-limit locks make stop levels non-guaranteed exits.",
            ]
        )
        if not targets:
            warnings.append("No announcement passed timestamp, surprise, liquidity, and current trading-state gates.")
        return _equity_proposal(
            strategy_id=self.config.strategy_id,
            version=self.config.version,
            as_of=observation_time.isoformat(),
            targets=targets,
            hard_vetoes=hard_vetoes,
            source_refs=source_refs,
            warnings=warnings,
        )


EarningsEventRepricingStrategy = PublicAnnouncementEarningsRepricingStrategy


def build_ashare_factor_tilt_proposal(
    universe: Sequence[Mapping[str, Any]],
    *,
    config: AShareFactorTiltConfig | Mapping[str, Any] | None = None,
    as_of: str | date | datetime | None = None,
    source_refs: Sequence[str] = (),
) -> dict[str, Any]:
    resolved = config if isinstance(config, AShareFactorTiltConfig) else AShareFactorTiltConfig.from_mapping(config)
    return AShareFactorTiltStrategy(resolved).generate_proposal(universe, as_of=as_of, source_refs=source_refs)


def build_earnings_event_repricing_proposal(
    announcements: Sequence[Mapping[str, Any]],
    *,
    config: EarningsEventRepricingConfig | Mapping[str, Any] | None = None,
    as_of: str | date | datetime | None = None,
    source_refs: Sequence[str] = (),
) -> dict[str, Any]:
    resolved = config if isinstance(config, EarningsEventRepricingConfig) else EarningsEventRepricingConfig.from_mapping(config)
    return PublicAnnouncementEarningsRepricingStrategy(resolved).generate_proposal(
        announcements,
        as_of=as_of,
        source_refs=source_refs,
    )


build_public_announcement_earnings_repricing_proposal = build_earnings_event_repricing_proposal


def _factor_candidate(
    raw: Mapping[str, Any],
    config: AShareFactorTiltConfig,
    observation_time: datetime,
) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    code = str(raw.get("code") or raw.get("symbol") or "").strip()
    if not code:
        return None, {"code": "unknown", "reason": "missing code"}
    reason = _security_hard_veto(
        raw,
        config.minimum_average_daily_turnover,
        config.minimum_listing_days,
        observation_time,
    )
    if reason:
        return None, {"code": code, "reason": reason}
    scores: list[float] = []
    try:
        for field in config.required_factor_fields:
            scores.append(_finite_fraction(raw.get(field), field))
    except ValueError as error:
        return None, {"code": code, "reason": str(error)}
    score = sum(weight * value for weight, value in zip(config.factor_weights, scores, strict=True))
    if score <= 0:
        return None, {"code": code, "reason": "composite factor score is not positive"}
    try:
        industry = _required_text(raw.get("industry"), "industry")
    except ValueError as error:
        return None, {"code": code, "reason": str(error)}
    return {
        "code": code,
        "industry": industry,
        "score": score,
        "source_ref": str(raw.get("source_ref") or "").strip(),
        "exchange": str(raw.get("exchange")).strip().lower(),
        "market": str(raw.get("market") or raw.get("market_type")).strip().lower(),
        "trading_state_as_of": str(raw.get("trading_state_as_of")).strip(),
        "rationale": "quality/value/momentum/investment composite",
    }, None


def _event_candidate(
    raw: Mapping[str, Any],
    config: EarningsEventRepricingConfig,
    observation_time: datetime,
) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    code = str(raw.get("code") or raw.get("symbol") or "").strip()
    if not code:
        return None, {"code": "unknown", "reason": "missing code"}
    reason = _security_hard_veto(
        raw,
        config.minimum_average_daily_turnover,
        0,
        observation_time,
    )
    if reason:
        return None, {"code": code, "reason": reason}
    published_value = str(raw.get("published_at") or "").strip()
    if not published_value:
        return None, {"code": code, "reason": "missing published_at timestamp"}
    try:
        published_at = _timestamp(published_value, "published_at")
    except ValueError as error:
        return None, {"code": code, "reason": f"invalid published_at: {error}"}
    available_value = str(raw.get("available_at") or "").strip()
    if not available_value:
        return None, {"code": code, "reason": "missing available_at timestamp"}
    try:
        available_at = _timestamp(available_value, "available_at")
    except ValueError as error:
        return None, {"code": code, "reason": f"invalid available_at: {error}"}
    if available_at < published_at:
        return None, {"code": code, "reason": "available_at precedes published_at"}
    age = observation_time - available_at
    if age.total_seconds() < 0 or age > timedelta(days=config.maximum_event_age_days):
        return None, {"code": code, "reason": "announcement is outside the configured public-information window"}
    if not str(raw.get("announcement_id") or "").strip() or not str(raw.get("source_ref") or "").strip():
        return None, {"code": code, "reason": "missing immutable announcement identifier or source reference"}
    try:
        surprise = _finite_fraction(raw.get("surprise_score"), "surprise_score")
    except ValueError as error:
        return None, {"code": code, "reason": str(error)}
    if surprise < config.minimum_surprise_score:
        return None, {"code": code, "reason": "surprise score is below the configured threshold"}
    try:
        industry = _required_text(raw.get("industry"), "industry")
    except ValueError as error:
        return None, {"code": code, "reason": str(error)}
    return {
        "code": code,
        "industry": industry,
        "score": surprise,
        "source_ref": str(raw.get("source_ref")).strip(),
        "exchange": str(raw.get("exchange")).strip().lower(),
        "market": str(raw.get("market") or raw.get("market_type")).strip().lower(),
        "trading_state_as_of": str(raw.get("trading_state_as_of")).strip(),
        "published_at": published_at.isoformat(),
        "available_at": available_at.isoformat(),
        "rationale": f"public announcement {str(raw.get('announcement_id')).strip()} surprise={surprise:.4f}",
    }, None


def _security_hard_veto(
    raw: Mapping[str, Any],
    minimum_turnover: float,
    minimum_listing_days: int,
    observation_time: datetime,
) -> str | None:
    if not isinstance(raw, Mapping):
        return "security record is not an object"
    exchange = str(raw.get("exchange") or "").strip().lower()
    market = str(raw.get("market") or raw.get("market_type") or "").strip().lower()
    if exchange not in _ASHARE_EXCHANGES or market not in _ASHARE_MARKETS:
        return "security lacks verified A-share exchange and market identity"
    try:
        state_as_of = _timestamp(raw.get("trading_state_as_of"), "trading_state_as_of")
    except ValueError as error:
        return f"missing or invalid current trading-state timestamp: {error}"
    if state_as_of > observation_time:
        return "trading-state timestamp is after the signal cutoff"
    if observation_time - state_as_of > _MAX_TRADING_STATE_AGE:
        return "trading-state timestamp is stale for the signal cutoff"
    try:
        tradable = _strict_bool(raw.get("tradable"), "tradable")
        halted = _strict_bool(raw.get("halted"), "halted")
        limit_up_locked = _strict_bool(raw.get("limit_up_locked"), "limit_up_locked")
        limit_down_locked = _strict_bool(raw.get("limit_down_locked"), "limit_down_locked")
        risk_warning = _strict_bool(raw.get("risk_warning"), "risk_warning")
        delisting_risk = _strict_bool(raw.get("delisting_risk"), "delisting_risk")
    except ValueError as error:
        return str(error)
    if not tradable:
        return "security is not currently tradable"
    if halted:
        return "security is halted"
    if limit_up_locked or limit_down_locked:
        return "security is price-limit locked; no executable capacity may be assumed"
    if risk_warning or delisting_risk:
        return "security has a risk-warning or delisting state"
    try:
        turnover = _finite_fraction(raw.get("average_daily_turnover"), "average_daily_turnover")
        listing_days = int(raw.get("listing_days"))
    except (TypeError, ValueError) as error:
        return f"missing or invalid liquidity/listing data: {error}"
    if turnover < minimum_turnover:
        return "average daily turnover is below the configured liquidity gate"
    if listing_days < minimum_listing_days:
        return "listing history is below the configured gate"
    if not str(raw.get("source_ref") or "").strip():
        return "missing source reference"
    return None


def _allocate_equity_targets(
    candidates: Sequence[Mapping[str, Any]],
    max_positions: int,
    max_gross_weight: float,
    max_position_weight: float,
    max_industry_weight: float,
) -> list[dict[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    industry_counts: dict[str, int] = {}
    industry_max_positions = max(1, math.floor(max_industry_weight / max_position_weight))
    for candidate in sorted(candidates, key=lambda item: (-float(item["score"]), str(item["code"]))):
        industry = str(candidate["industry"])
        if industry_counts.get(industry, 0) >= industry_max_positions:
            continue
        selected.append(candidate)
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
        if len(selected) >= max_positions:
            break
    if not selected:
        return []
    scores = [max(float(item["score"]), 0.0) for item in selected]
    total_score = sum(scores)
    # A sleeve has a fixed gross budget: its capacity is the sum of declared
    # per-name caps.  Within that budget, high composite scores receive a
    # larger share and unallocated capital remains cash rather than being
    # forced into weaker candidates.
    sleeve_budget = min(max_gross_weight, max_position_weight * len(selected))
    targets: list[dict[str, Any]] = []
    for candidate, score in zip(selected, scores, strict=True):
        equal_fallback = 1.0 / len(selected)
        raw_weight = score / total_score if total_score > 0 else equal_fallback
        weight = min(max_position_weight, sleeve_budget * raw_weight)
        if weight <= 0:
            continue
        targets.append(
            {
                "code": candidate["code"],
                "target_weight": round(weight, 8),
                "industry": candidate["industry"],
                "score": round(float(candidate["score"]), 8),
                "source_ref": candidate["source_ref"],
                "exchange": candidate["exchange"],
                "market": candidate["market"],
                "trading_state_as_of": candidate["trading_state_as_of"],
                "rationale": candidate["rationale"],
                "long_only": True,
                "paper_only": True,
            }
        )
    return targets


def _equity_proposal(
    *,
    strategy_id: str,
    version: str,
    as_of: str,
    targets: Sequence[Mapping[str, Any]],
    hard_vetoes: Sequence[Mapping[str, str]],
    source_refs: Sequence[str],
    warnings: Sequence[str],
) -> dict[str, Any]:
    total_weight = sum(float(item["target_weight"]) for item in targets)
    return {
        "schema_version": "personal_equity_strategy_proposal.v1",
        "strategy_id": strategy_id,
        "strategy_version": version,
        "as_of": as_of,
        "targets": [dict(item) for item in targets],
        "total_target_weight": round(total_weight, 8),
        "cash_weight": round(max(0.0, 1.0 - total_weight), 8),
        "hard_vetoes": [dict(item) for item in hard_vetoes],
        "source_refs": list(dict.fromkeys(str(item) for item in source_refs if str(item).strip())),
        "warnings": list(dict.fromkeys(str(item) for item in warnings)),
        "data_quality": "source_labelled_research" if source_refs else "source_refs_required",
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
    }


def _equity_warnings(source_refs: Sequence[str]) -> list[str]:
    warnings = [
        "This is a long-only personal translation, not a market-neutral institutional factor or event-arbitrage strategy.",
        "Current trading status, price-limit state, liquidity and source timestamps must be revalidated before manual action.",
        "New A-share purchases have T+1 exit risk; a stop level is not a guaranteed fill.",
    ]
    if not source_refs:
        warnings.append("No proposal-level source references were supplied; this output is not decision-eligible.")
    return warnings
