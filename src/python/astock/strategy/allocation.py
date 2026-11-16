"""Fail-closed, common-NAV aggregation of personal strategy paper sleeves.

The allocator is deliberately an accounting boundary, not an execution layer.
Every active target must fit in one common cash/collateral waterfall.  In
particular, a futures sleeve cannot silently treat its own proposal capital as
an independent account, and a crypto target cannot become active merely
because untrusted JSON says that it is eligible.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any


_STRATEGY_TARGET_ASSET_CLASS = {
    "ashare_factor_tilt": "equity",
    "earnings_event_repricing": "equity",
    "domestic_futures_cta_tsmom": "futures",
    "crypto_liquid_tsmom": "crypto",
}
_ASHARE_EXCHANGES = {"sse", "szse", "bse"}
_ASHARE_MARKETS = {"ashare", "a_share", "a-share"}


class AllocationState(str, Enum):
    """Outcome of the paper-allocation validation gate."""

    ACTIVE = "active"
    FROZEN = "frozen"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AllocationPolicy:
    """Explicit common-NAV risk budget for the personal paper book."""

    strategy_id: str = "personal_multi_sleeve_allocation"
    version: str = "v3"
    max_total_equity_weight: float = 0.70
    max_total_crypto_weight: float = 0.10
    max_total_cash_asset_weight: float = 0.80
    max_total_futures_margin_fraction: float = 0.25
    max_single_equity_weight: float = 0.10
    max_single_crypto_weight: float = 0.04
    max_sleeve_budget_fraction: float = 0.50
    require_source_refs: bool = True

    def __post_init__(self) -> None:
        for name, value in (
            ("max_total_equity_weight", self.max_total_equity_weight),
            ("max_total_crypto_weight", self.max_total_crypto_weight),
            ("max_total_cash_asset_weight", self.max_total_cash_asset_weight),
            ("max_total_futures_margin_fraction", self.max_total_futures_margin_fraction),
            ("max_single_equity_weight", self.max_single_equity_weight),
            ("max_single_crypto_weight", self.max_single_crypto_weight),
            ("max_sleeve_budget_fraction", self.max_sleeve_budget_fraction),
        ):
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if not isinstance(self.require_source_refs, bool):
            raise TypeError("require_source_refs must be a boolean")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> AllocationPolicy:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise TypeError("allocation policy must be an object")
        default = cls()
        fields = {name: value.get(name, getattr(default, name)) for name in cls.__dataclass_fields__}
        for name in (
            "max_total_equity_weight",
            "max_total_crypto_weight",
            "max_total_cash_asset_weight",
            "max_total_futures_margin_fraction",
            "max_single_equity_weight",
            "max_single_crypto_weight",
            "max_sleeve_budget_fraction",
        ):
            fields[name] = _positive_fraction(fields[name], name)
        fields["strategy_id"] = str(fields["strategy_id"])
        fields["version"] = str(fields["version"])
        fields["require_source_refs"] = _strict_bool(
            fields["require_source_refs"], "require_source_refs"
        )
        return cls(**fields)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "version": self.version,
            "max_total_equity_weight": self.max_total_equity_weight,
            "max_total_crypto_weight": self.max_total_crypto_weight,
            "max_total_cash_asset_weight": self.max_total_cash_asset_weight,
            "max_total_futures_margin_fraction": self.max_total_futures_margin_fraction,
            "max_single_equity_weight": self.max_single_equity_weight,
            "max_single_crypto_weight": self.max_single_crypto_weight,
            "max_sleeve_budget_fraction": self.max_sleeve_budget_fraction,
            "require_source_refs": self.require_source_refs,
        }


class MultiSleeveAllocator:
    """Combine eligible sleeves into one reconciled, paper-only ledger."""

    def __init__(self, policy: AllocationPolicy | None = None) -> None:
        self.policy = policy or AllocationPolicy()

    def allocate(
        self,
        sleeve_proposals: Mapping[str, Mapping[str, Any]],
        *,
        security_ledger: Mapping[str, Any] | None = None,
        futures_ledger: Mapping[str, Any] | None = None,
        crypto_ledger: Mapping[str, Any] | None = None,
        risk_budget: Mapping[str, Any] | None = None,
        previous_state: Mapping[str, Any] | None = None,
        as_of: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(sleeve_proposals, Mapping) or not sleeve_proposals:
            raise ValueError("sleeve_proposals must be a non-empty mapping")

        blockers: list[str] = []
        warnings: list[str] = []
        frozen_reasons = _frozen_reasons(risk_budget, previous_state)
        equities: list[dict[str, Any]] = []
        futures: list[dict[str, Any]] = []
        crypto: list[dict[str, Any]] = []
        sleeves: list[dict[str, Any]] = []
        for sleeve_name, proposal in sleeve_proposals.items():
            if not isinstance(proposal, Mapping):
                blockers.append(f"{sleeve_name}: proposal is not an object")
                continue
            parsed, issues = _parse_sleeve(
                str(sleeve_name),
                proposal,
                self.policy,
                crypto_ledger=crypto_ledger,
            )
            blockers.extend(issues)
            if parsed is None:
                continue
            sleeves.append(parsed["summary"])
            equities.extend(parsed["equities"])
            futures.extend(parsed["futures"])
            crypto.extend(parsed["crypto"])
            warnings.extend(parsed["warnings"])

        allocation_capital, capital_issues = _resolve_allocation_capital(risk_budget, futures)
        blockers.extend(capital_issues)
        blockers.extend(
            _sleeve_budget_issues(
                equities,
                futures,
                crypto,
                self.policy,
                allocation_capital=allocation_capital,
            )
        )
        if not equities and not futures and not crypto and not blockers:
            blockers.append("no sleeve produced an eligible paper target")

        state: AllocationState
        if frozen_reasons:
            blockers.extend(frozen_reasons)
            state = AllocationState.FROZEN
            equities, futures, crypto = [], [], []
        elif blockers:
            state = AllocationState.BLOCKED
            equities, futures, crypto = [], [], []
        else:
            # Futures are integer-sized first.  Their final collateral amount,
            # not a pre-rounding fraction, is then reserved before cash assets.
            futures = _cap_futures_targets(futures, self.policy, allocation_capital)
            equities = _cap_equity_targets(equities, self.policy)
            crypto = _cap_crypto_targets(crypto, self.policy)
            futures_margin = sum(float(item["margin_fraction"]) for item in futures)
            equities, crypto = _cap_cash_asset_targets(
                equities,
                crypto,
                self.policy,
                futures_margin_fraction=futures_margin,
            )
            total_commitment = _total_commitment_fraction(equities, crypto, futures)
            if total_commitment > 1.0 + 1e-8:
                blockers.append(
                    "common-NAV cash/collateral waterfall exceeds 100% after integer futures sizing"
                )
                state = AllocationState.BLOCKED
                equities, futures, crypto = [], [], []
            else:
                state = AllocationState.ACTIVE

        effective_as_of = as_of or _latest_as_of(sleeve_proposals) or datetime.now(UTC).date().isoformat()
        equity_weight = sum(float(item["target_weight"]) for item in equities)
        futures_margin = sum(float(item["margin_fraction"]) for item in futures)
        crypto_gross_weight = sum(abs(float(item["target_weight"])) for item in crypto)
        crypto_net_weight = sum(float(item["target_weight"]) for item in crypto)
        total_commitment = _total_commitment_fraction(equities, crypto, futures)
        residual_weight = round(max(0.0, 1.0 - total_commitment), 8)
        capital_waterfall = _capital_waterfall(
            allocation_capital=allocation_capital,
            equity_weight=equity_weight,
            crypto_gross_weight=crypto_gross_weight,
            futures_margin_fraction=futures_margin,
            residual_weight=residual_weight,
        )
        resolved_risk_budget = {
            **self.policy.to_dict(),
            "allocation_capital": allocation_capital,
            "capital_basis": "common_nav" if allocation_capital is not None else "weight_only_no_futures",
        }
        return {
            "schema_version": "multi_sleeve_allocation.v3",
            "strategy_id": self.policy.strategy_id,
            "strategy_version": self.policy.version,
            "as_of": effective_as_of,
            "state": state.value,
            "allocation_state": state.value,
            "risk_budget": resolved_risk_budget,
            "capital_waterfall": capital_waterfall,
            "ledgers": {
                "security": {
                    "targets": equities,
                    "total_target_weight": round(equity_weight, 8),
                    "ledger_context": _serializable_ledger_context(security_ledger),
                },
                "futures": {
                    "targets": futures,
                    "total_margin_fraction": round(futures_margin, 8),
                    "total_margin_required": round(
                        sum(float(item["margin_required"]) for item in futures), 8
                    ),
                    "ledger_context": _serializable_ledger_context(futures_ledger),
                },
                "crypto": {
                    "targets": crypto,
                    "total_target_weight": round(crypto_gross_weight, 8),
                    "total_gross_target_weight": round(crypto_gross_weight, 8),
                    "net_target_weight": round(crypto_net_weight, 8),
                    "exposure_by_venue_market_direction": _crypto_leg_exposures(crypto),
                    "counterparty_exposures": _crypto_counterparty_exposures(crypto),
                    "ledger_context": _serializable_ledger_context(crypto_ledger),
                },
            },
            "sleeves": sleeves,
            "blockers": list(dict.fromkeys(blockers)),
            "warnings": list(
                dict.fromkeys(
                    warnings
                    + [
                        "This allocator produces a common-NAV paper ledger only and never routes broker, futures, exchange, custody, or wallet orders.",
                        "Futures collateral and cash-funded assets are reconciled once in capital_waterfall; do not sum ledger-level residuals.",
                        "A crypto residual is not a recommendation to hold a stablecoin; custody, venue, counterparty and legal-access facts remain external gates.",
                    ]
                )
            ),
            "research_only": True,
            "no_order_execution": True,
            "formal_decision_eligible": False,
        }


def allocate_multi_sleeve(
    sleeve_proposals: Mapping[str, Mapping[str, Any]],
    security_ledger: Mapping[str, Any] | None = None,
    futures_ledger: Mapping[str, Any] | None = None,
    crypto_ledger: Mapping[str, Any] | None = None,
    risk_budget: Mapping[str, Any] | None = None,
    previous_state: Mapping[str, Any] | None = None,
    as_of: str | None = None,
    policy: AllocationPolicy | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Allocate source-labelled proposals into a reconciled paper ledger."""

    resolved = policy if isinstance(policy, AllocationPolicy) else AllocationPolicy.from_mapping(policy)
    return MultiSleeveAllocator(resolved).allocate(
        sleeve_proposals,
        security_ledger=security_ledger,
        futures_ledger=futures_ledger,
        crypto_ledger=crypto_ledger,
        risk_budget=risk_budget,
        previous_state=previous_state,
        as_of=as_of,
    )


def _frozen_reasons(
    risk_budget: Mapping[str, Any] | None,
    previous_state: Mapping[str, Any] | None,
) -> list[str]:
    values = [risk_budget or {}, previous_state or {}]
    reasons: list[str] = []
    for value in values:
        if not isinstance(value, Mapping):
            continue
        if value.get("freeze") is True or value.get("hard_veto") is True or value.get("risk_off") is True:
            reason = str(value.get("reason") or value.get("freeze_reason") or "external hard risk veto")
            reasons.append(f"allocation frozen: {reason}")
    return reasons


def _parse_sleeve(
    name: str,
    proposal: Mapping[str, Any],
    policy: AllocationPolicy,
    *,
    crypto_ledger: Mapping[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    issues: list[str] = []
    if proposal.get("no_order_execution") is not True or proposal.get("research_only") is not True:
        issues.append(f"{name}: proposal lacks research-only/no-order-execution contract")
    if proposal.get("errors"):
        issues.append(f"{name}: proposal reports errors")
    if policy.require_source_refs and not _proposal_source_ids(proposal):
        issues.append(f"{name}: source references are required")
    if issues:
        return None, issues

    strategy_id = str(proposal.get("strategy_id") or "").strip()
    version = str(proposal.get("strategy_version") or proposal.get("version") or "").strip()
    if not strategy_id or not version:
        return None, [f"{name}: strategy_id and strategy_version are required"]
    expected_asset_class = _STRATEGY_TARGET_ASSET_CLASS.get(strategy_id)
    if expected_asset_class is None:
        return None, [f"{name}: strategy_id is not registered for an allocatable target schema"]
    raw_targets = proposal.get("targets")
    if not isinstance(raw_targets, Sequence) or isinstance(raw_targets, (str, bytes)):
        return None, [f"{name}: targets must be a sequence"]

    crypto_raw_targets = [
        raw
        for raw in raw_targets
        if isinstance(raw, Mapping) and str(raw.get("asset_class") or "").strip().lower() == "crypto"
    ]
    crypto_artifact: Mapping[str, Any] | None = None
    if crypto_raw_targets:
        if expected_asset_class != "crypto":
            return None, [f"{name}: crypto target is incompatible with strategy_id {strategy_id}"]
        crypto_artifact, crypto_issues = _resolve_crypto_activation_artifact(
            name,
            proposal,
            crypto_ledger,
        )
        if crypto_issues:
            return None, crypto_issues

    equities: list[dict[str, Any]] = []
    futures: list[dict[str, Any]] = []
    crypto: list[dict[str, Any]] = []
    proposal_as_of = str(proposal.get("as_of") or "").strip()
    for raw in raw_targets:
        if not isinstance(raw, Mapping):
            return None, [f"{name}: target is not an object"]
        asset_class = str(raw.get("asset_class") or "").strip().lower()
        if asset_class == "crypto":
            if expected_asset_class != "crypto":
                return None, [f"{name}: crypto target is incompatible with strategy_id {strategy_id}"]
            parsed_crypto, target_issues = _parse_crypto_target(
                name,
                raw,
                strategy_id=strategy_id,
                version=version,
                artifact=crypto_artifact,
            )
            if target_issues:
                return None, target_issues
            assert parsed_crypto is not None
            crypto.append(parsed_crypto)
            continue
        if "target_weight" in raw:
            if expected_asset_class != "equity":
                return None, [f"{name}: equity target is incompatible with strategy_id {strategy_id}"]
            weight = _finite_float(raw["target_weight"], f"{name}: target_weight")
            if weight < 0:
                return None, [f"{name}: target_weight must be non-negative and finite"]
            code = str(raw.get("code") or "").strip()
            source_ref = str(raw.get("source_ref") or "").strip()
            if not code or not source_ref:
                return None, [f"{name}: equity targets require code and source_ref"]
            identity_issue = _equity_identity_issue(raw, proposal_as_of, name)
            if identity_issue is not None:
                return None, [identity_issue]
            equities.append(
                {
                    "sleeve": name,
                    "strategy_id": strategy_id,
                    "strategy_version": version,
                    "code": code,
                    "target_weight": weight,
                    "source_ref": source_ref,
                    "exchange": str(raw.get("exchange")).strip().lower(),
                    "market": str(raw.get("market") or raw.get("market_type")).strip().lower(),
                    "trading_state_as_of": str(raw.get("trading_state_as_of")).strip(),
                    "rationale": str(raw.get("rationale") or "").strip(),
                }
            )
            continue
        if "target_contracts" in raw:
            if expected_asset_class != "futures":
                return None, [f"{name}: futures target is incompatible with strategy_id {strategy_id}"]
            parsed_future, target_issues = _parse_futures_target(
                name,
                raw,
                proposal=proposal,
                proposal_as_of=proposal_as_of,
                strategy_id=strategy_id,
                version=version,
            )
            if target_issues:
                return None, target_issues
            assert parsed_future is not None
            futures.append(parsed_future)
            continue
        return None, [f"{name}: target must include target_weight or target_contracts"]

    return {
        "equities": equities,
        "futures": futures,
        "crypto": crypto,
        "warnings": [str(item) for item in proposal.get("warnings") or []],
        "summary": {
            "sleeve": name,
            "strategy_id": strategy_id,
            "strategy_version": version,
            "target_count": len(raw_targets),
            "source_ids": _proposal_source_ids(proposal),
        },
    }, []


def _equity_identity_issue(
    raw: Mapping[str, Any],
    proposal_as_of: str,
    name: str,
) -> str | None:
    exchange = str(raw.get("exchange") or "").strip().lower()
    market = str(raw.get("market") or raw.get("market_type") or "").strip().lower()
    if exchange not in _ASHARE_EXCHANGES or market not in _ASHARE_MARKETS:
        return f"{name}: equity target lacks verified A-share exchange and market identity"
    try:
        proposal_time = _parse_aware_timestamp(proposal_as_of, f"{name}: proposal as_of")
        state_time = _parse_aware_timestamp(
            raw.get("trading_state_as_of"), f"{name}: trading_state_as_of"
        )
    except ValueError as error:
        return str(error)
    if state_time > proposal_time:
        return f"{name}: equity trading-state timestamp is after proposal as_of"
    if proposal_time - state_time > timedelta(hours=24):
        return f"{name}: equity trading-state timestamp is stale for proposal as_of"
    return None


def _parse_crypto_target(
    name: str,
    raw: Mapping[str, Any],
    *,
    strategy_id: str,
    version: str,
    artifact: Mapping[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    weight = _finite_float(raw.get("target_weight"), f"{name}: crypto target_weight")
    asset_id = str(raw.get("asset_id") or raw.get("symbol") or "").strip()
    symbol = str(raw.get("symbol") or asset_id).strip()
    venue = str(raw.get("venue") or raw.get("exchange") or "").strip().lower()
    market_type = str(raw.get("market_type") or "").strip().lower()
    source_ref = str(raw.get("source_ref") or "").strip()
    if not asset_id or not symbol or not venue or not market_type or not source_ref:
        return None, [
            f"{name}: crypto targets require asset_id, symbol, venue, market_type, and source_ref"
        ]
    if market_type not in {"spot", "perpetual"}:
        return None, [f"{name}: crypto market_type must be spot or perpetual"]
    short_eligible = raw.get("short_eligible") is True
    direction = "long" if weight >= 0 else "short"
    if weight < 0 and (market_type != "perpetual" or not short_eligible):
        return None, [
            f"{name}: a negative crypto target requires a short-eligible perpetual market"
        ]
    if artifact is None:
        # Defensive only: `_resolve_crypto_activation_artifact` must already
        # have rejected this.  Do not allow a future refactor to bypass it.
        return None, [f"{name}: crypto target lacks a validated allocation artifact"]
    artifact_id = str(artifact["artifact_id"])
    if str(raw.get("validation_artifact_id") or "").strip() != artifact_id:
        return None, [f"{name}: crypto target does not bind to the validated allocation artifact"]
    leg = {
        "asset_id": asset_id,
        "symbol": symbol,
        "venue": venue,
        "market_type": market_type,
        "direction": direction,
    }
    if not _crypto_leg_is_approved(leg, artifact):
        return None, [
            f"{name}: crypto target is outside the validated artifact's approved venue/market/direction scope"
        ]
    return {
        "sleeve": name,
        "strategy_id": strategy_id,
        "strategy_version": version,
        "asset_class": "crypto",
        **leg,
        "short_eligible": short_eligible,
        "target_weight": weight,
        "source_ref": source_ref,
        "validation_artifact_id": artifact_id,
        "rationale": str(raw.get("rationale") or "").strip(),
        "funding": dict(raw["funding"]) if isinstance(raw.get("funding"), Mapping) else None,
    }, []


def _parse_futures_target(
    name: str,
    raw: Mapping[str, Any],
    *,
    proposal: Mapping[str, Any],
    proposal_as_of: str,
    strategy_id: str,
    version: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    capital = _positive_float(
        proposal.get("capital") or proposal.get("initial_capital"),
        f"{name}: futures proposal capital",
    )
    instrument_id = str(raw.get("instrument_id") or "").strip()
    active_contract = str(raw.get("active_contract") or "").strip()
    source_ref = str(raw.get("source_ref") or "").strip()
    if not instrument_id or not active_contract or not source_ref:
        return None, [f"{name}: futures targets require instrument_id, active_contract, and source_ref"]
    try:
        contracts = _strict_integer(raw.get("target_contracts"), f"{name}: target_contracts")
        facts, margin_per_contract = _futures_margin_facts(
            raw,
            active_contract=active_contract,
            proposal_as_of=proposal_as_of,
            name=name,
        )
    except ValueError as error:
        return None, [str(error)]
    expected_margin = abs(contracts) * margin_per_contract
    if raw.get("margin_required") is not None:
        declared_margin = _finite_float(raw.get("margin_required"), f"{name}: margin_required")
        if declared_margin < 0:
            return None, [f"{name}: margin_required must be non-negative and finite"]
        if not _approximately_equal(declared_margin, expected_margin):
            return None, [
                f"{name}: declared margin_required does not equal integer contracts times point-in-time margin_per_contract"
            ]
    return {
        "sleeve": name,
        "strategy_id": strategy_id,
        "strategy_version": version,
        "instrument_id": instrument_id,
        "active_contract": active_contract,
        "requested_contracts": contracts,
        "target_contracts": contracts,
        "proposal_capital": capital,
        "margin_per_contract": margin_per_contract,
        "margin_required": expected_margin,
        "source_ref": source_ref,
        "contract_facts": facts,
        "margin_fraction": expected_margin / capital,
    }, []


def _futures_margin_facts(
    raw: Mapping[str, Any],
    *,
    active_contract: str,
    proposal_as_of: str,
    name: str,
) -> tuple[dict[str, Any], float]:
    """Read dated, executable-contract margin facts and derive per-lot margin.

    `margin_required` is intentionally not a source of truth here.  It is an
    output that must reconcile to a dated contract fact plus integer contracts.
    """

    contract_facts = raw.get("contract_facts")
    if not isinstance(contract_facts, Mapping):
        raise ValueError(f"{name}: futures target requires dated contract_facts")  # noqa: TRY004
    fact_contract = str(
        contract_facts.get("active_contract") or contract_facts.get("contract_id") or ""
    ).strip()
    if fact_contract != active_contract:
        raise ValueError(f"{name}: contract_facts must match active_contract")
    fact_source_ref = str(contract_facts.get("source_ref") or "").strip()
    if not fact_source_ref:
        raise ValueError(f"{name}: contract_facts requires source_ref")
    fact_as_of = str(contract_facts.get("as_of") or "").strip()
    if not fact_as_of:
        raise ValueError(f"{name}: contract_facts requires as_of")
    fact_timestamp = _parse_timestamp(fact_as_of, f"{name}: contract_facts.as_of")
    if proposal_as_of:
        proposal_timestamp = _parse_timestamp(proposal_as_of, f"{name}: proposal as_of")
        # A proposal timestamp is often stored as a trading *date* while the
        # contract fact carries its session-close time.  Permit facts from the
        # same calendar session, but never a later trading date.
        if fact_timestamp.date() > proposal_timestamp.date():
            raise ValueError(f"{name}: contract_facts are later than the proposal as_of")
    if str(contract_facts.get("data_quality") or "").strip().lower() != "point_in_time_verified":
        raise ValueError(f"{name}: contract_facts must be point_in_time_verified")
    if str(contract_facts.get("point_in_time_coverage") or "").strip().lower() != "verified":
        raise ValueError(f"{name}: contract_facts must have verified point-in-time coverage")
    if str(contract_facts.get("trading_status") or "").strip().lower() != "tradable":
        raise ValueError(f"{name}: contract_facts must show a tradable contract")

    margin_per_contract_raw = raw.get("margin_per_contract", contract_facts.get("margin_per_contract"))
    formula_values = _futures_margin_formula_values(raw, contract_facts, name)
    if margin_per_contract_raw is None:
        if formula_values is None:
            raise ValueError(
                f"{name}: futures target needs margin_per_contract or reference_price, contract_multiplier, and initial_margin_rate"
            )
        reference_price, multiplier, initial_margin_rate = formula_values
        margin_per_contract = reference_price * multiplier * initial_margin_rate
    else:
        margin_per_contract = _positive_float(
            margin_per_contract_raw,
            f"{name}: margin_per_contract",
        )
        if formula_values is not None:
            reference_price, multiplier, initial_margin_rate = formula_values
            expected = reference_price * multiplier * initial_margin_rate
            if not _approximately_equal(margin_per_contract, expected):
                raise ValueError(
                    f"{name}: margin_per_contract disagrees with point-in-time price/multiplier/margin-rate facts"
                )
    facts = {
        "active_contract": fact_contract,
        "as_of": fact_as_of,
        "source_ref": fact_source_ref,
        "data_quality": "point_in_time_verified",
        "point_in_time_coverage": "verified",
        "trading_status": "tradable",
    }
    if formula_values is not None:
        reference_price, multiplier, initial_margin_rate = formula_values
        facts.update(
            {
                "reference_price": reference_price,
                "contract_multiplier": multiplier,
                "initial_margin_rate": initial_margin_rate,
            }
        )
    return facts, margin_per_contract


def _futures_margin_formula_values(
    raw: Mapping[str, Any],
    contract_facts: Mapping[str, Any],
    name: str,
) -> tuple[float, float, float] | None:
    def pick(key: str, *aliases: str) -> Any:
        for item in (raw, contract_facts):
            for candidate in (key, *aliases):
                if item.get(candidate) is not None:
                    return item[candidate]
        return None

    price = pick("reference_price", "settlement_price")
    multiplier = pick("contract_multiplier", "multiplier")
    margin_rate = pick("initial_margin_rate")
    values = (price, multiplier, margin_rate)
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise ValueError(
            f"{name}: point-in-time futures margin formula requires reference_price, contract_multiplier, and initial_margin_rate"
        )
    resolved_price = _positive_float(price, f"{name}: reference_price")
    resolved_multiplier = _positive_float(multiplier, f"{name}: contract_multiplier")
    resolved_margin_rate = _positive_fraction(margin_rate, f"{name}: initial_margin_rate")
    return resolved_price, resolved_multiplier, resolved_margin_rate


def _resolve_allocation_capital(
    risk_budget: Mapping[str, Any] | None,
    futures: Sequence[Mapping[str, Any]],
) -> tuple[float | None, list[str]]:
    """Require one common NAV whenever a futures sleeve is present."""

    if not futures:
        return None, []
    if not isinstance(risk_budget, Mapping):
        return None, ["futures allocation requires risk_budget.allocation_capital"]
    try:
        allocation_capital = _positive_float(
            risk_budget.get("allocation_capital"),
            "risk_budget.allocation_capital",
        )
    except ValueError as error:
        return None, [str(error)]
    issues: list[str] = []
    for target in futures:
        proposal_capital = float(target["proposal_capital"])
        if not _approximately_equal(proposal_capital, allocation_capital):
            issues.append(
                f"{target['sleeve']}: futures proposal capital {proposal_capital:.8f} does not match risk_budget.allocation_capital {allocation_capital:.8f}"
            )
    return allocation_capital, issues


def _resolve_crypto_activation_artifact(
    name: str,
    proposal: Mapping[str, Any],
    crypto_ledger: Mapping[str, Any] | None,
) -> tuple[Mapping[str, Any] | None, list[str]]:
    """Allow crypto only through a reviewed artifact and trusted verifier.

    A JSON proposal cannot create its own eligibility.  The caller must supply
    an external validator callback in the crypto ledger, so JSON-only CLI
    input remains fail-closed by design.
    """

    issues: list[str] = []
    if proposal.get("formal_decision_eligible") is not True:
        issues.append(
            f"{name}: crypto proposal is not formally decision-eligible; research-only crypto targets cannot be active"
        )
    data_quality = str(proposal.get("data_quality") or "").strip().lower()
    if data_quality != "point_in_time_verified":
        issues.append(f"{name}: crypto proposal data_quality must be point_in_time_verified")
    if proposal.get("blockers") or proposal.get("errors") or proposal.get("degraded") is True:
        issues.append(f"{name}: crypto proposal has blockers, errors, or degraded input")
    assurance = proposal.get("data_assurance")
    if not isinstance(assurance, Mapping) or str(assurance.get("status") or "").strip().lower() != "point_in_time_verified":
        issues.append(f"{name}: crypto proposal lacks point-in-time-verified data assurance")
    access_gate = proposal.get("access_gate")
    if not isinstance(access_gate, Mapping) or str(access_gate.get("status") or "").strip().lower() != "validated":
        issues.append(f"{name}: crypto proposal lacks a validated access gate")
        artifact_id = ""
    else:
        artifact_id = str(
            proposal.get("crypto_allocation_artifact_id") or access_gate.get("artifact_id") or ""
        ).strip()
    if not artifact_id:
        issues.append(f"{name}: crypto proposal lacks crypto_allocation_artifact_id")
    if issues:
        return None, issues
    if not isinstance(crypto_ledger, Mapping):
        return None, [f"{name}: crypto allocation requires a trusted validation ledger"]
    artifact = _find_crypto_artifact(crypto_ledger, artifact_id)
    if artifact is None:
        return None, [f"{name}: validated crypto allocation artifact was not found in the validation ledger"]
    artifact_issues = _validate_crypto_artifact(artifact, proposal)
    if artifact_issues:
        return None, [f"{name}: {issue}" for issue in artifact_issues]
    validator = crypto_ledger.get("validate_crypto_allocation_artifact")
    if not callable(validator):
        return None, [
            f"{name}: crypto allocation needs an external trusted artifact validator; JSON-only artifacts are not accepted"
        ]
    try:
        verdict = _call_crypto_validator(validator, artifact, proposal)
    except Exception as error:  # noqa: BLE001  # pragma: no cover - defensive integration boundary
        return None, [f"{name}: crypto artifact validator failed: {type(error).__name__}"]
    if verdict is not True:
        return None, [f"{name}: trusted crypto artifact validator did not approve this proposal"]
    return artifact, []


def _find_crypto_artifact(
    crypto_ledger: Mapping[str, Any],
    artifact_id: str,
) -> Mapping[str, Any] | None:
    raw_artifacts = crypto_ledger.get("validated_access_artifacts")
    if isinstance(raw_artifacts, Mapping):
        if str(raw_artifacts.get("artifact_id") or "").strip() == artifact_id:
            return raw_artifacts
        candidate = raw_artifacts.get(artifact_id)
        return candidate if isinstance(candidate, Mapping) else None
    if isinstance(raw_artifacts, Sequence) and not isinstance(raw_artifacts, (str, bytes)):
        for artifact in raw_artifacts:
            if isinstance(artifact, Mapping) and str(artifact.get("artifact_id") or "").strip() == artifact_id:
                return artifact
    return None


def _validate_crypto_artifact(
    artifact: Mapping[str, Any],
    proposal: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    if str(artifact.get("status") or "").strip().lower() != "validated":
        issues.append("crypto allocation artifact status is not validated")
    if artifact.get("formal_decision_eligible") is not True:
        issues.append("crypto allocation artifact is not formally decision-eligible")
    if artifact.get("degraded") is True or artifact.get("blockers") or artifact.get("errors"):
        issues.append("crypto allocation artifact has blockers, errors, or degraded input")
    if str(artifact.get("data_quality") or "").strip().lower() != "point_in_time_verified":
        issues.append("crypto allocation artifact data_quality is not point_in_time_verified")
    for field in ("artifact_id", "validator_id", "source_ref", "artifact_hash", "validated_at", "expires_at"):
        if not str(artifact.get(field) or "").strip():
            issues.append(f"crypto allocation artifact requires {field}")
    approved_legs = artifact.get("approved_legs")
    if isinstance(approved_legs, (str, bytes)) or not isinstance(approved_legs, Sequence) or not approved_legs:
        issues.append("crypto allocation artifact requires non-empty approved_legs")
    try:
        validated_at = _parse_timestamp(artifact.get("validated_at"), "crypto artifact validated_at")
        expires_at = _parse_timestamp(artifact.get("expires_at"), "crypto artifact expires_at")
        proposal_as_of = _parse_timestamp(proposal.get("as_of"), "crypto proposal as_of")
        if validated_at > proposal_as_of:
            issues.append("crypto allocation artifact was validated after the proposal as_of")
        if expires_at < proposal_as_of:
            issues.append("crypto allocation artifact expired before the proposal as_of")
    except ValueError as error:
        issues.append(str(error))
    return issues


def _call_crypto_validator(
    validator: Callable[..., Any],
    artifact: Mapping[str, Any],
    proposal: Mapping[str, Any],
) -> bool:
    """Invoke the external validator with named arguments when supported."""

    try:
        return validator(artifact=artifact, proposal=proposal) is True
    except TypeError:
        return validator(artifact, proposal) is True


def _crypto_leg_is_approved(leg: Mapping[str, str], artifact: Mapping[str, Any]) -> bool:
    raw_legs = artifact.get("approved_legs")
    if not isinstance(raw_legs, Sequence) or isinstance(raw_legs, (str, bytes)):
        return False
    normalized_leg = {key: str(value).strip().lower() for key, value in leg.items()}
    for candidate in raw_legs:
        if not isinstance(candidate, Mapping):
            continue
        normalized_candidate = {
            key: str(candidate.get(key) or "").strip().lower()
            for key in ("asset_id", "symbol", "venue", "market_type", "direction")
        }
        if normalized_candidate == normalized_leg:
            return True
    return False


def _cap_equity_targets(targets: Sequence[Mapping[str, Any]], policy: AllocationPolicy) -> list[dict[str, Any]]:
    by_code: dict[str, dict[str, Any]] = {}
    for raw in targets:
        code = str(raw["code"])
        if not code:
            continue
        entry = by_code.get(code)
        if entry is None:
            by_code[code] = dict(raw)
        else:
            entry["target_weight"] = float(entry["target_weight"]) + float(raw["target_weight"])
            entry["sleeve"] = f"{entry['sleeve']},{raw['sleeve']}"
    merged = [
        {**entry, "target_weight": min(float(entry["target_weight"]), policy.max_single_equity_weight)}
        for entry in by_code.values()
    ]
    total = sum(float(item["target_weight"]) for item in merged)
    scale = min(1.0, policy.max_total_equity_weight / total) if total else 1.0
    return [{**item, "target_weight": round(float(item["target_weight"]) * scale, 8)} for item in merged]


def _cap_futures_targets(
    targets: Sequence[Mapping[str, Any]],
    policy: AllocationPolicy,
    allocation_capital: float | None,
) -> list[dict[str, Any]]:
    """Integer-size contracts, then compute collateral from per-lot facts."""

    if not targets:
        return []
    if allocation_capital is None:  # Defensive: caller must have blocked first.
        raise ValueError("internal error: futures allocation lacks common allocation_capital")
    requested_margin = sum(
        abs(int(item["requested_contracts"])) * float(item["margin_per_contract"])
        for item in targets
    )
    margin_cap = allocation_capital * policy.max_total_futures_margin_fraction
    scale = min(1.0, margin_cap / requested_margin) if requested_margin else 0.0
    output: list[dict[str, Any]] = []
    for raw in targets:
        requested_contracts = int(raw["requested_contracts"])
        scaled_count = math.floor(abs(requested_contracts) * scale + 1e-12)
        contracts = int(math.copysign(scaled_count, requested_contracts)) if scaled_count else 0
        if contracts == 0:
            # A sub-lot risk budget is cash, not a zero-contract futures target.
            continue
        margin_per_contract = float(raw["margin_per_contract"])
        margin_required = abs(contracts) * margin_per_contract
        output.append(
            {
                **dict(raw),
                "target_contracts": contracts,
                "margin_required": round(margin_required, 8),
                "margin_fraction": round(margin_required / allocation_capital, 8),
                "allocation_capital": allocation_capital,
            }
        )
    # Integer truncation can only reduce collateral.  Keep a hard assertion so
    # an upstream malformed fact cannot create an apparent cap-compliant book.
    final_margin = sum(float(item["margin_required"]) for item in output)
    if final_margin > margin_cap + 1e-7:
        raise ValueError("internal error: integer-sized futures collateral exceeds configured cap")
    return output


def _cap_crypto_targets(
    targets: Sequence[Mapping[str, Any]],
    policy: AllocationPolicy,
) -> list[dict[str, Any]]:
    """Cap crypto legs without netting venue, market-type, or direction risk."""

    by_leg: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for raw in targets:
        direction = "long" if float(raw["target_weight"]) >= 0 else "short"
        key = (
            str(raw["asset_id"]),
            str(raw["symbol"]),
            str(raw["venue"]),
            str(raw["market_type"]),
            direction,
        )
        entry = by_leg.get(key)
        if entry is None:
            entry = {**dict(raw), "direction": direction, "source_refs": [str(raw["source_ref"])]}
            by_leg[key] = entry
            continue
        entry["target_weight"] = float(entry["target_weight"]) + float(raw["target_weight"])
        entry["sleeve"] = f"{entry['sleeve']},{raw['sleeve']}"
        entry["source_refs"] = sorted({*entry.get("source_refs", []), str(raw["source_ref"])})
    capped = [
        {
            **entry,
            "target_weight": math.copysign(
                min(abs(float(entry["target_weight"])), policy.max_single_crypto_weight),
                float(entry["target_weight"]),
            ),
        }
        for entry in by_leg.values()
    ]
    total = sum(abs(float(item["target_weight"])) for item in capped)
    scale = min(1.0, policy.max_total_crypto_weight / total) if total else 1.0
    return [
        {**item, "target_weight": round(float(item["target_weight"]) * scale, 8)}
        for item in capped
    ]


def _cap_cash_asset_targets(
    equities: Sequence[Mapping[str, Any]],
    crypto: Sequence[Mapping[str, Any]],
    policy: AllocationPolicy,
    *,
    futures_margin_fraction: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Reserve futures collateral before allocating cash-funded risk assets."""

    available_cash_assets = min(
        policy.max_total_cash_asset_weight,
        max(0.0, 1.0 - futures_margin_fraction),
    )
    total_cash_assets = sum(float(item["target_weight"]) for item in equities) + sum(
        abs(float(item["target_weight"])) for item in crypto
    )
    scale = min(1.0, available_cash_assets / total_cash_assets) if total_cash_assets else 1.0
    adjusted_equities = [
        {**dict(item), "target_weight": round(float(item["target_weight"]) * scale, 8)}
        for item in equities
    ]
    adjusted_crypto = [
        {**dict(item), "target_weight": round(float(item["target_weight"]) * scale, 8)}
        for item in crypto
    ]
    # Guard against a one-unit rounding excess.  The second scale runs only on
    # the rare boundary and preserves every leg's sign and identity.
    final_cash_assets = sum(float(item["target_weight"]) for item in adjusted_equities) + sum(
        abs(float(item["target_weight"])) for item in adjusted_crypto
    )
    if final_cash_assets > available_cash_assets + 1e-8:
        correction = available_cash_assets / final_cash_assets if final_cash_assets else 1.0
        adjusted_equities = [
            {**item, "target_weight": round(float(item["target_weight"]) * correction, 8)}
            for item in adjusted_equities
        ]
        adjusted_crypto = [
            {**item, "target_weight": round(float(item["target_weight"]) * correction, 8)}
            for item in adjusted_crypto
        ]
    return adjusted_equities, adjusted_crypto


def _sleeve_budget_issues(
    equities: Sequence[Mapping[str, Any]],
    futures: Sequence[Mapping[str, Any]],
    crypto: Sequence[Mapping[str, Any]],
    policy: AllocationPolicy,
    *,
    allocation_capital: float | None,
) -> list[str]:
    """Refuse an unbounded sleeve before portfolio-level scaling."""

    budgets: dict[str, float] = {}
    for target in equities:
        sleeve = str(target["sleeve"])
        budgets[sleeve] = budgets.get(sleeve, 0.0) + float(target["target_weight"])
    for target in futures:
        sleeve = str(target["sleeve"])
        denominator = allocation_capital or float(target["proposal_capital"])
        requested_margin = abs(int(target["requested_contracts"])) * float(target["margin_per_contract"])
        budgets[sleeve] = budgets.get(sleeve, 0.0) + requested_margin / denominator
    for target in crypto:
        sleeve = str(target["sleeve"])
        budgets[sleeve] = budgets.get(sleeve, 0.0) + abs(float(target["target_weight"]))
    return [
        f"{sleeve}: declared sleeve exposure {exposure:.6f} exceeds max_sleeve_budget_fraction"
        for sleeve, exposure in sorted(budgets.items())
        if exposure > policy.max_sleeve_budget_fraction + 1e-9
    ]


def _total_commitment_fraction(
    equities: Sequence[Mapping[str, Any]],
    crypto: Sequence[Mapping[str, Any]],
    futures: Sequence[Mapping[str, Any]],
) -> float:
    return sum(float(item["target_weight"]) for item in equities) + sum(
        abs(float(item["target_weight"])) for item in crypto
    ) + sum(float(item["margin_fraction"]) for item in futures)


def _capital_waterfall(
    *,
    allocation_capital: float | None,
    equity_weight: float,
    crypto_gross_weight: float,
    futures_margin_fraction: float,
    residual_weight: float,
) -> dict[str, Any]:
    committed_weight = equity_weight + crypto_gross_weight + futures_margin_fraction
    result: dict[str, Any] = {
        "basis": "common_nav",
        "allocation_capital": allocation_capital,
        "equity_cash_commitment_fraction": round(equity_weight, 8),
        "crypto_gross_collateral_fraction": round(crypto_gross_weight, 8),
        "futures_margin_collateral_fraction": round(futures_margin_fraction, 8),
        "total_committed_fraction": round(committed_weight, 8),
        "residual_cash_fraction": residual_weight,
    }
    if allocation_capital is not None:
        result.update(
            {
                "equity_cash_commitment": round(allocation_capital * equity_weight, 8),
                "crypto_gross_collateral": round(allocation_capital * crypto_gross_weight, 8),
                "futures_margin_collateral": round(allocation_capital * futures_margin_fraction, 8),
                "residual_cash": round(allocation_capital * residual_weight, 8),
            }
        )
    return result


def _crypto_leg_exposures(targets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for target in targets:
        direction = "long" if float(target["target_weight"]) >= 0 else "short"
        key = (str(target["venue"]), str(target["market_type"]), direction)
        entry = grouped.setdefault(
            key,
            {
                "venue": key[0],
                "market_type": key[1],
                "direction": direction,
                "gross_target_weight": 0.0,
                "net_target_weight": 0.0,
                "asset_ids": set(),
                "target_count": 0,
            },
        )
        weight = float(target["target_weight"])
        entry["gross_target_weight"] += abs(weight)
        entry["net_target_weight"] += weight
        entry["asset_ids"].add(str(target["asset_id"]))
        entry["target_count"] += 1
    return [
        {
            **{key: value for key, value in entry.items() if key != "asset_ids"},
            "gross_target_weight": round(float(entry["gross_target_weight"]), 8),
            "net_target_weight": round(float(entry["net_target_weight"]), 8),
            "asset_ids": sorted(entry["asset_ids"]),
        }
        for _, entry in sorted(grouped.items())
    ]


def _crypto_counterparty_exposures(targets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for target in targets:
        venue = str(target["venue"])
        entry = grouped.setdefault(
            venue,
            {
                "venue": venue,
                "gross_target_weight": 0.0,
                "net_target_weight": 0.0,
                "long_gross_target_weight": 0.0,
                "short_gross_target_weight": 0.0,
                "market_types": set(),
                "asset_ids": set(),
                "target_count": 0,
            },
        )
        weight = float(target["target_weight"])
        entry["gross_target_weight"] += abs(weight)
        entry["net_target_weight"] += weight
        if weight >= 0:
            entry["long_gross_target_weight"] += abs(weight)
        else:
            entry["short_gross_target_weight"] += abs(weight)
        entry["market_types"].add(str(target["market_type"]))
        entry["asset_ids"].add(str(target["asset_id"]))
        entry["target_count"] += 1
    return [
        {
            **{
                key: value
                for key, value in entry.items()
                if key not in {"market_types", "asset_ids"}
            },
            "gross_target_weight": round(float(entry["gross_target_weight"]), 8),
            "net_target_weight": round(float(entry["net_target_weight"]), 8),
            "long_gross_target_weight": round(float(entry["long_gross_target_weight"]), 8),
            "short_gross_target_weight": round(float(entry["short_gross_target_weight"]), 8),
            "market_types": sorted(entry["market_types"]),
            "asset_ids": sorted(entry["asset_ids"]),
        }
        for _, entry in sorted(grouped.items())
    ]


def _proposal_source_ids(proposal: Mapping[str, Any]) -> list[str]:
    raw = proposal.get("source_refs") or proposal.get("source_archive_ids") or ()
    if isinstance(raw, (str, bytes)):
        raw = (raw,)
    if not isinstance(raw, Sequence):
        return []
    return list(dict.fromkeys(str(item).strip() for item in raw if str(item).strip()))


def _serializable_ledger_context(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    # A trusted callback is intentionally a process-bound integration, never a
    # serializable claim that a JSON client can replay as a valid verifier.
    return {
        str(key): item
        for key, item in value.items()
        if not callable(item)
    }


def _latest_as_of(sleeves: Mapping[str, Mapping[str, Any]]) -> str | None:
    values = [str(value.get("as_of") or "").strip() for value in sleeves.values()]
    return max((value for value in values if value), default=None)


def _positive_fraction(value: Any, name: str) -> float:
    result = _positive_float(value, name)
    if result > 1:
        raise ValueError(f"{name} must be in (0, 1]")
    return result


def _positive_float(value: Any, name: str) -> float:
    result = _finite_float(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return result


def _finite_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")  # noqa: TRY004
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _strict_integer(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")  # noqa: TRY004
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError(f"{name} must be an integer")
    return int(number)


def _strict_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{name} must be boolean")


def _approximately_equal(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-7)


def _parse_timestamp(value: Any, name: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError(f"{name} is required")
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(f"{raw}T00:00:00")
        except ValueError as error:
            raise ValueError(f"{name} must be ISO-8601 dated") from error
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _parse_aware_timestamp(value: Any, name: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError(f"{name} is required")
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must be a timezone-aware ISO-8601 timestamp")
    return parsed.astimezone(UTC)
