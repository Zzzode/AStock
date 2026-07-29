"""Data-source eligibility rules for published market research and replay.

This is deliberately a registry of *claims the system is allowed to make*, not
an adapter catalogue.  A public aggregation endpoint may be useful for an
observation, but it is not automatically suitable for a reproducible paper
backtest or an investment-committee packet.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = "market_data_source_governance.v1"
BACKTEST_REQUIRED_DOMAINS = (
    "trading_calendar",
    "eod_bars",
    "halts",
    "price_limits",
    "corporate_actions",
    "delistings",
)


@dataclass(frozen=True)
class MarketDataSource:
    """A vendor/data authority and the capabilities it can substantiate."""

    source_id: str
    vendor: str
    access_model: str
    domains: tuple[str, ...]
    decision_eligible: bool
    reproducible_backtest_eligible: bool
    credential_environment: tuple[str, ...] = ()
    credential_match_all: bool = False
    documentation_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        credential_values = [bool(os.environ.get(name, "").strip()) for name in self.credential_environment]
        configured = not credential_values or (
            all(credential_values) if self.credential_match_all else any(credential_values)
        )
        return {
            "source_id": self.source_id,
            "vendor": self.vendor,
            "access_model": self.access_model,
            "domains": list(self.domains),
            "decision_eligible": self.decision_eligible,
            "reproducible_backtest_eligible": self.reproducible_backtest_eligible,
            "configured": configured,
            "credential_required": bool(self.credential_environment),
            "documentation_url": self.documentation_url,
        }


# These entries are intentionally conservative.  They record the vendor's
# documented product scope, not an assertion that this process owns a licence.
MARKET_DATA_SOURCES: tuple[MarketDataSource, ...] = (
    MarketDataSource(
        source_id="akshare_public",
        vendor="AKShare public aggregation",
        access_model="best-effort public aggregation",
        domains=("observation", "spot", "eod_bars", "trading_calendar"),
        decision_eligible=False,
        reproducible_backtest_eligible=False,
        documentation_url="https://akshare.akfamily.xyz/",
    ),
    MarketDataSource(
        source_id="tushare_pro",
        vendor="Tushare Pro",
        access_model="token-authorized data service",
        domains=("trading_calendar", "eod_bars", "halts", "price_limits", "corporate_actions", "delistings"),
        decision_eligible=True,
        reproducible_backtest_eligible=True,
        credential_environment=("TUSHARE_TOKEN",),
        documentation_url="https://tushare.pro/document/2",
    ),
    MarketDataSource(
        source_id="jqdata",
        vendor="JoinQuant JQData",
        access_model="licensed research data service",
        domains=("trading_calendar", "eod_bars", "minute_bars", "ticks", "halts", "price_limits", "corporate_actions", "delistings"),
        decision_eligible=True,
        reproducible_backtest_eligible=True,
        credential_environment=("JQDATA_USERNAME", "JQDATA_PASSWORD"),
        credential_match_all=True,
        documentation_url="https://www.joinquant.com/help/api/doc?id=9875&name=JQDatadoc",
    ),
    MarketDataSource(
        source_id="wind_wds",
        vendor="Wind WDS",
        access_model="institutional licensed market-data service",
        domains=("trading_calendar", "eod_bars", "minute_bars", "ticks", "order_book", "order_queue", "halts", "price_limits", "corporate_actions", "delistings"),
        decision_eligible=True,
        reproducible_backtest_eligible=True,
        credential_environment=("WIND_API_PATH", "WIND_USERNAME"),
        documentation_url="https://www.wind.com.cn/portal/zh/WDS/marketdata.html",
    ),
    MarketDataSource(
        source_id="exchange_disclosures",
        vendor="SSE/SZSE/CNINFO issuer disclosures",
        access_model="primary public disclosure archive",
        domains=("corporate_actions", "halts", "listing_status", "delistings", "announcements"),
        decision_eligible=True,
        reproducible_backtest_eligible=False,
        documentation_url="https://www.cninfo.com.cn/",
    ),
)


def list_market_data_source_governance() -> dict[str, Any]:
    """Return the static, auditable data-source registry and runtime status."""
    return {
        "schema_version": SCHEMA_VERSION,
        "sources": [source.to_dict() for source in MARKET_DATA_SOURCES],
        "policy": {
            "public_aggregation": "observation_only",
            "published_decision": "requires decision-eligible, source-labelled data",
            "reproducible_backtest": "requires a frozen manifest with complete event-domain coverage",
            "restricted_list": "must come from an organization-controlled compliance authority; no market-data vendor substitutes for it",
        },
    }


def is_decision_eligible_source(source_id: object) -> bool:
    """Return whether a registered source may support a published decision."""
    normalized = str(source_id or "").strip()
    return any(
        source.source_id == normalized and source.decision_eligible
        for source in MARKET_DATA_SOURCES
    )


def is_auditable_decision_data_reference(value: Mapping[str, Any] | object) -> bool:
    """Require an eligible source *and* a frozen, owned evidence reference.

    Naming a commercial vendor in a candidate JSON cannot turn public data into
    institutional evidence.  The candidate must bind the exact source snapshot
    and identify the accountable data owner who attests to authorized use.
    """
    if not isinstance(value, Mapping):
        return False
    if not is_decision_eligible_source(value.get("source")):
        return False
    if not str(value.get("archive_id") or "").strip():
        return False
    attestation = value.get("license_attestation")
    return bool(
        isinstance(attestation, Mapping)
        and attestation.get("authorized") is True
        and str(attestation.get("attested_by") or "").strip()
    )


def is_frozen_public_observation_reference(value: Mapping[str, Any] | object) -> bool:
    """Recognize a content-addressed public observation without upgrading it.

    This permits an auditable research review to distinguish exact public
    inputs from user-entered values. It deliberately does not make the packet
    decision-eligible or reproducible-backtest eligible.
    """
    return bool(
        isinstance(value, Mapping)
        and str(value.get("source") or "").strip() == "akshare_public"
        and str(value.get("archive_id") or "").strip().startswith("sha256:")
    )


def assess_backtest_source_manifest(manifest: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate the source contract attached to a paper-portfolio replay.

    The check does not verify a vendor entitlement remotely.  It prevents the
    stronger reproducibility claim unless the replay identifies a frozen source
    archive and assigns every execution-critical event domain to a source that
    the registry permits for historical replay.
    """
    failures: list[str] = []
    warnings: list[str] = []
    if not isinstance(manifest, Mapping):
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked",
            "failures": ["A portfolio backtest source manifest is required for a reproducibility claim."],
            "warnings": [],
            "resolved_domains": {},
        }
    if str(manifest.get("schema_version", "")).strip() != "portfolio_backtest_sources.v1":
        failures.append("source manifest must use schema_version portfolio_backtest_sources.v1")
    if not str(manifest.get("as_of", "")).strip():
        failures.append("source manifest requires an as_of timestamp")
    if not str(manifest.get("archive_id", "")).strip():
        failures.append("source manifest requires an immutable archive_id")
    raw_domains = manifest.get("domains")
    if not isinstance(raw_domains, Mapping):
        failures.append("source manifest requires a domains mapping")
        raw_domains = {}

    registered = {source.source_id: source for source in MARKET_DATA_SOURCES}
    resolved: dict[str, str] = {}
    for domain in BACKTEST_REQUIRED_DOMAINS:
        source_id = str(raw_domains.get(domain, "")).strip()
        source = registered.get(source_id)
        if source is None:
            failures.append(f"{domain} must name a registered source")
            continue
        if domain not in source.domains:
            failures.append(f"{source_id} is not registered for {domain}")
            continue
        if not source.reproducible_backtest_eligible:
            failures.append(f"{source_id} is observation-only and cannot substantiate a reproducible backtest")
            continue
        resolved[domain] = source_id

    attestation = manifest.get("license_attestation")
    if not isinstance(attestation, Mapping) or attestation.get("authorized") is not True:
        failures.append("source manifest requires license_attestation.authorized=true")
    elif not str(attestation.get("attested_by", "")).strip():
        failures.append("license_attestation requires an attested_by owner")

    unconfigured: list[str] = []
    if not failures:
        configured_sources = {
            entry["source_id"]: bool(entry["configured"])
            for entry in list_market_data_source_governance()["sources"]
        }
        unconfigured = sorted({source_id for source_id in resolved.values() if not configured_sources[source_id]})
        if unconfigured:
            warnings.append(
                "Manifest is structurally complete but the current runtime has no configured credential for: "
                + ", ".join(unconfigured)
                + ". Re-run must use the frozen archive, not a public fallback."
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not failures else "blocked",
        "formal_evidence_eligible": not failures and not unconfigured,
        "unconfigured_sources": unconfigured,
        "failures": failures,
        "warnings": warnings,
        "resolved_domains": resolved,
    }
