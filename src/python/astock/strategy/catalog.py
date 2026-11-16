"""An honest catalog of institutional strategy families for personal research.

The catalog is a boundary-control feature.  It prevents a future UI, skill, or
report from labelling a long-only signal as "global statistical arbitrage" or
"institutional volatility arbitrage" when the required market structure is
absent.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import (
    PersonalAccessProfile,
    StrategyAvailability,
    StrategyDefinition,
    StrategyLifecycle,
)

_CRYPTO_LEGAL_ACCESS_NOTICE = (
    "A self-attested crypto access fact plus dated jurisdiction, venue, custody and data evidence is not a "
    "legal conclusion and does not establish legal availability in the China mainland or any other regulated jurisdiction."
)

# This metadata is deliberately separate from ``StrategyDefinition``.  The
# definition describes an immutable strategy contract, while this map is an
# explanatory translation layer for a personal account's markets.  Neither
# field is an investment recommendation or an eligibility override.
_MARKET_TRANSLATIONS: dict[str, dict[str, object]] = {
    "core_reserve": {
        "institutional_archetypes": ["Bridgewater strategic risk budgeting"],
        "china_mainland": {
            "status": "paper_research",
            "summary": "A common-NAV reserve and liability-aware framework; it is not an All Weather replication.",
        },
        "crypto_market": {
            "status": "not_a_crypto_alpha",
            "summary": "Crypto is not required to implement a reserve or risk-budget framework.",
        },
        "personal_protocol": [
            "Separate near-term liabilities and futures collateral from risk capital.",
            "Measure every sleeve against one common NAV and do not double-count cash.",
        ],
        "reference_urls": ["https://www.bridgewater.com/research-and-insights/the-all-weather-story"],
    },
    "global_macro_risk_balanced_allocation": {
        "institutional_archetypes": ["Bridgewater All Weather", "Citadel fixed income and macro"],
        "china_mainland": {
            "status": "conditional_research",
            "summary": "Global derivatives, FX, product, tax and funding access remain external gates.",
        },
        "crypto_market": {
            "status": "research_only",
            "summary": "A token price is not a lawful or economic substitute for a global macro implementation.",
        },
        "personal_protocol": [
            "Write observable growth, inflation, liquidity and policy scenarios before taking risk.",
            "Treat financing, currency and product terms as dated inputs, not static assumptions.",
        ],
        "reference_urls": [
            "https://www.bridgewater.com/research-and-insights/the-all-weather-story",
            "https://www.citadel.com/what-we-do/fixed-income-and-macro/",
        ],
    },
    "pe_style_public_market_underwriting": {
        "institutional_archetypes": ["Blackstone private equity", "KKR/Carlyle-style public underwriting analogue"],
        "china_mainland": {
            "status": "research_framework",
            "summary": "Public-information underwriting can be used, but control rights, deal allocation and private diligence are absent.",
        },
        "crypto_market": {
            "status": "not_applicable",
            "summary": "Token ownership is not an equivalent to private-company control or a negotiated capital structure.",
        },
        "personal_protocol": [
            "Create a cash-flow, governance, competition, valuation and invalidation dossier for each issuer.",
            "Do not treat a PE-style checklist as evidence of a private-equity return stream.",
        ],
        "reference_urls": ["https://www.blackstone.com/our-businesses/private-equity/"],
    },
    "private_credit_real_assets_underwriting": {
        "institutional_archetypes": ["Apollo credit", "private real-assets underwriting"],
        "china_mainland": {
            "status": "research_framework",
            "summary": "Product terms, seniority, collateral, valuation policy and liquidity must be diligenced separately.",
        },
        "crypto_market": {
            "status": "not_applicable",
            "summary": "A tokenised or high-yield token product is not an equivalent private-credit implementation.",
        },
        "personal_protocol": [
            "Check asset coverage, cash-flow waterfall, fees, redemption terms and default procedures.",
            "Never use stated yield as a substitute for loss, liquidity or valuation analysis.",
        ],
        "reference_urls": ["https://www.apollo.com/institutional/strategies/asset-management/credit"],
    },
    "ashare_factor_tilt": {
        "institutional_archetypes": ["AQR style premia", "systematic long-only equity factors"],
        "china_mainland": {
            "status": "paper_implemented_if_eligible",
            "summary": "A-share long-only quality, value, momentum and investment tilt with liquidity and trade-state vetoes.",
        },
        "crypto_market": {
            "status": "conditional_research",
            "summary": "Crypto cross-sectional research has venue, survival, custody and shorting biases that are not A-share-equivalent.",
        },
        "personal_protocol": [
            "Freeze point-in-time fundamental and trading-state data before ranking.",
            "Use industry, liquidity and concentration caps; do not describe a net-long book as market neutral.",
        ],
        "reference_urls": [
            "https://australia.aqr.com/funds/aqr-style-premia-trust/",
            "https://doi.org/10.1016/j.jfineco.2014.10.010",
        ],
    },
    "earnings_event_repricing": {
        "institutional_archetypes": ["event-driven public-information research"],
        "china_mainland": {
            "status": "paper_implemented_if_eligible",
            "summary": "Long-only, timestamped earnings-event research with A-share trading-state and exit-risk gates.",
        },
        "crypto_market": {
            "status": "research_only",
            "summary": "Public-event timestamps, venue integrity and manipulation risk require an independent data protocol.",
        },
        "personal_protocol": [
            "Record both publication and actual availability times before a signal is evaluated.",
            "Predeclare surprise logic, holding horizon, liquidity limits and invalidation conditions.",
        ],
        "reference_urls": ["https://doi.org/10.1111/0022-1082.00401"],
    },
    "public_merger_event_research": {
        "institutional_archetypes": ["event-driven merger and special-situations research"],
        "china_mainland": {
            "status": "research_framework",
            "summary": "A filing timeline and scenario process only; no short-spread or completion-profit claim is made.",
        },
        "crypto_market": {
            "status": "not_economic_equivalent",
            "summary": "There is no reliable equivalent of regulated public merger-arbitrage mechanics.",
        },
        "personal_protocol": [
            "Map consideration, approvals, financing, timeline and break scenarios from public documents.",
            "Treat halts, price limits and missing hedge access as central risks.",
        ],
        "reference_urls": ["https://www.hfr.com/hfr-indices/hfr-hedge-fund-strategy-classifications/"],
    },
    "domestic_futures_cta_tsmom": {
        "institutional_archetypes": ["Man AHL trend following", "managed futures CTA"],
        "china_mainland": {
            "status": "paper_implemented_if_account_and_contract_eligible",
            "summary": "Low-frequency domestic actual-contract time-series momentum with daily settlement, roll and margin controls.",
        },
        "crypto_market": {
            "status": "research_only_non_mainland",
            "summary": "The trend premise can be researched, but 24/7 operation, funding, custody, venue and jurisdiction are separate gates.",
        },
        "personal_protocol": [
            "Use 21/63/126-session signals after close and allow execution no earlier than the next session.",
            "Require dated active-contract, settlement, margin, position-limit and roll facts for every session.",
            "Use one common-NAV margin cap and assume a limit or unavailable session may prevent an exit.",
        ],
        "reference_urls": [
            "https://www.man.com/ahl",
            "https://doi.org/10.1016/j.jfineco.2011.11.003",
            "https://www.cffex.com.cn/u/cms/www/202003/271635174xwg.pdf",
        ],
    },
    "domestic_futures_calendar_relative_value": {
        "institutional_archetypes": ["futures curve relative value", "commodity carry research"],
        "china_mainland": {
            "status": "conditional_research",
            "summary": "Requires paired actual contracts, delivery rules, volume, margin, position-limit and price-limit facts; it is not a global-carry proxy.",
        },
        "crypto_market": {
            "status": "not_a_mainland_route",
            "summary": "Crypto basis and funding strategies are not treated as a compliant or risk-equivalent domestic implementation.",
        },
        "personal_protocol": [
            "Audit both legs, expiry calendar, delivery exposure, fees and worst-case combined margin before modelling a spread.",
            "Do not create a target from contango/backwardation alone.",
        ],
        "reference_urls": ["https://www.czce.com.cn/cn/uploadfile/2021/03/01/20210301134917265.pdf"],
    },
    "crypto_liquid_tsmom": {
        "institutional_archetypes": ["liquid crypto trend research"],
        "china_mainland": {
            "status": "not_a_personal_implementation_route",
            "summary": "The system does not offer a crypto implementation route for China-mainland residents.",
        },
        "crypto_market": {
            "status": "research_only_non_mainland",
            "summary": "A dated non-Mainland jurisdiction, venue, custody, data and funding-evidence gate is required; output remains paper research.",
        },
        "personal_protocol": [
            "Do not use a generic global-access claim, foreign venue or self-attestation as a Mainland workaround.",
            "For a lawful non-Mainland setting, verify timestamped data, venue, custody, funding and immutable archives before paper research.",
        ],
        "reference_urls": ["https://www.csrc.gov.cn/csrc/c100028/c7614318/content.shtml?f_link_type=f_linkinlinenote"],
    },
    "global_market_neutral_stat_arb": {
        "institutional_archetypes": ["Two Sigma systematic investing", "market-neutral statistical arbitrage"],
        "china_mainland": {
            "status": "not_economic_equivalent",
            "summary": "Borrow, neutral execution, global point-in-time data and capacity are structural requirements.",
        },
        "crypto_market": {
            "status": "not_economic_equivalent",
            "summary": "Venue fragmentation and 24/7 operation add counterparty and execution requirements rather than remove them.",
        },
        "personal_protocol": [
            "Do not label a correlation, grid or single-pair chart rule as institutional statistical arbitrage.",
            "Keep it blocked unless the full data, borrow, cost and execution assumptions can be verified.",
        ],
        "reference_urls": ["https://www.twosigma.com/businesses/investment-management/"],
    },
    "global_carry_relative_value": {
        "institutional_archetypes": ["cross-asset carry and relative value"],
        "china_mainland": {
            "status": "not_economic_equivalent",
            "summary": "Global funding, FX, collateral, OTC access and hedging are absent from a domestic personal account.",
        },
        "crypto_market": {
            "status": "not_a_mainland_route",
            "summary": "Funding or basis is compensation for tail, venue and liquidation risk, not a risk-free yield.",
        },
        "personal_protocol": [
            "Do not use high yield, a futures curve or a funding rate as a substitute for a global carry programme.",
        ],
        "reference_urls": ["https://australia.aqr.com/funds/aqr-style-premia-trust/"],
    },
    "volatility_dispersion": {
        "institutional_archetypes": ["index-component volatility dispersion", "volatility market making"],
        "china_mainland": {
            "status": "not_economic_equivalent",
            "summary": "Option surface, correlation, dynamic hedging, margin and tail-liquidity infrastructure are required.",
        },
        "crypto_market": {
            "status": "not_economic_equivalent",
            "summary": "Crypto option venues add counterparty, liquidity and 24/7 hedging requirements.",
        },
        "personal_protocol": [
            "Do not replace dispersion with naked option selling or one volatility indicator.",
        ],
        "reference_urls": ["https://www.hfr.com/hfr-indices/hfr-hedge-fund-strategy-classifications/"],
    },
}

_CATALOG: tuple[StrategyDefinition, ...] = (
    StrategyDefinition(
        strategy_id="core_reserve",
        version="v1",
        name="Core reserve and liability-aware allocation",
        family="strategic_allocation",
        availability=StrategyAvailability.AVAILABLE,
        lifecycle=StrategyLifecycle.PAPER,
        asset_scope=("cash", "eligible_domestic_bonds", "broad_etfs"),
        required_access=("domestic_securities_account",),
        required_data=("product_terms", "liquidity", "personal_cashflow_facts"),
        economic_engine="Liquidity matching and capital preservation, not alpha.",
        personal_translation="Keep near-term obligations outside risk sleeves and measure total return once.",
        non_replicable_components=("insurance_balance_sheet", "institutional_ALM_capital_relief"),
        risk_notes=("Product terms, duration, credit and liquidity must be dated and sourced.",),
    ),
    StrategyDefinition(
        strategy_id="global_macro_risk_balanced_allocation",
        version="v1",
        name="Global macro and risk-balanced allocation research",
        family="global_macro_risk_balanced",
        availability=StrategyAvailability.CONDITIONAL,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=(
            "global_public_equities",
            "sovereign_bonds",
            "inflation_hedges",
            "commodities",
            "cash",
        ),
        required_access=("lawful_global_market_access", "global_investment_product_access"),
        required_data=(
            "dated_multi_asset_returns",
            "currency_tax_and_product_terms",
            "liquidity_and_funding_terms",
            "personal_liability_facts",
        ),
        economic_engine=(
            "Diversification of explicitly budgeted risk across growth, inflation, liquidity and "
            "policy regimes, rather than directional macro forecasting."
        ),
        personal_translation=(
            "A research-only risk-budget framework using independently verified public instruments; "
            "it does not reproduce discretionary global macro, swaps, leverage or institutional funding."
        ),
        non_replicable_components=(
            "discretionary_macro_research",
            "global_derivatives_and_financing",
            "institutional_currency_tax_implementation",
        ),
        risk_notes=(
            "Diversification can fail when nominally distinct assets share funding or liquidity stress.",
            "Global access, tax, currency and product eligibility require independent current verification.",
        ),
    ),
    StrategyDefinition(
        strategy_id="pe_style_public_market_underwriting",
        version="v1",
        name="PE-style public-market underwriting analogue",
        family="private_equity_public_underwriting_analogue",
        availability=StrategyAvailability.RESEARCH_ONLY,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("public_equities", "public_company_disclosures"),
        required_access=("domestic_securities_account",),
        required_data=(
            "audited_financials",
            "capital_structure",
            "operating_kpis",
            "valuation_scenarios",
            "governance_disclosures",
        ),
        economic_engine=(
            "Long-horizon underwriting discipline: downside cash flow, debt capacity, operational "
            "evidence, valuation and explicit invalidation."
        ),
        personal_translation=(
            "A public-information research process, not ownership, deal allocation, a miniature LBO "
            "or a claim to private-equity returns."
        ),
        non_replicable_components=(
            "control_rights",
            "private_due_diligence",
            "deal_sourcing",
            "underwriting_syndicate_allocation",
            "illiquid_capital_structure",
        ),
        risk_notes=(
            (
                "Public disclosures can lag deterioration and a disciplined underwriting process need not "
                "outperform a diversified benchmark."
            ),
        ),
    ),
    StrategyDefinition(
        strategy_id="private_credit_real_assets_underwriting",
        version="v1",
        name="Private-credit and real-assets underwriting research",
        family="private_markets_underwriting",
        availability=StrategyAvailability.RESEARCH_ONLY,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("private_credit", "private_real_assets", "public_disclosures"),
        required_access=("qualified_investor_status", "lawful_product_access", "manager_due_diligence"),
        required_data=(
            "dated_product_terms",
            "cashflow_waterfall",
            "debt_and_collateral_terms",
            "valuation_policy",
            "liquidity_and_fee_terms",
        ),
        economic_engine=(
            "Contractual cash-flow, asset coverage and capital-structure underwriting, with no implied "
            "liquidity premium or credit return forecast."
        ),
        personal_translation=(
            "Due-diligence research only; it does not originate a loan, create a bespoke structure, "
            "supply manager access or represent a product as suitable or available."
        ),
        non_replicable_components=(
            "direct_origination",
            "negotiated_seniority_and_covenants",
            "asset_control",
            "institutional_liability_funding",
            "private_secondary_liquidity",
        ),
        risk_notes=(
            (
                "Appraisal marks, fees, leverage, cash-call timing and exit timing are not comparable with "
                "a liquid public-account return series."
            ),
        ),
    ),
    StrategyDefinition(
        strategy_id="ashare_factor_tilt",
        version="v1",
        name="Liquid A-share long-only factor tilt",
        family="systematic_equity",
        availability=StrategyAvailability.CONDITIONAL,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("a_shares", "domestic_equity_etfs"),
        required_access=("domestic_securities_account",),
        required_data=("point_in_time_fundamentals", "listing_status", "liquidity", "price_limits"),
        economic_engine="Diversified long-only exposure to quality, value, investment and momentum characteristics.",
        personal_translation="A low-turnover long-only tilt with A-share T+1, halt and price-limit constraints.",
        non_replicable_components=("borrow", "market_neutrality", "institutional_execution"),
        risk_notes=("A historical factor premium is not a named-stock recommendation or guaranteed alpha.",),
    ),
    StrategyDefinition(
        strategy_id="earnings_event_repricing",
        version="v1",
        name="Public-announcement earnings repricing",
        family="event_driven",
        availability=StrategyAvailability.CONDITIONAL,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("a_shares", "domestic_equity_etfs"),
        required_access=("domestic_securities_account",),
        required_data=("timestamped_announcements", "prior_expectations", "liquidity", "trading_status"),
        economic_engine="Slow incorporation of verified earnings information after a public disclosure.",
        personal_translation="Long-only, evidence-led post-announcement research with explicit catalyst expiry and invalidation.",
        non_replicable_components=("short_leg", "real_time_news_infrastructure", "guaranteed_gap_exit"),
        risk_notes=("T+1, gaps, halts and limit locks must be modelled as exit risk rather than stop fills.",),
    ),
    StrategyDefinition(
        strategy_id="public_merger_event_research",
        version="v1",
        name="Public merger and special-situations event research",
        family="merger_event_driven",
        availability=StrategyAvailability.RESEARCH_ONLY,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("public_equities", "public_transaction_documents"),
        required_access=("domestic_securities_account",),
        required_data=(
            "timestamped_transaction_filings",
            "consideration_terms",
            "approval_timeline",
            "financing_conditions",
            "trading_status",
        ),
        economic_engine=(
            "Scenario-weighted public information about deal consideration, timing, approvals and break "
            "risk; not a riskless spread."
        ),
        personal_translation=(
            "A filing-timeline and scenario-research process only; no merger-arbitrage, short-spread "
            "or guaranteed completion implementation is claimed."
        ),
        non_replicable_components=(
            "borrow_and_hedging",
            "event_driven_financing",
            "cross_border_legal_process",
            "institutional_information_and_execution",
        ),
        risk_notes=(
            (
                "Deal terms, approvals and timing can change abruptly; price limits, halts and gaps make "
                "exit assumptions particularly fragile in A shares."
            ),
        ),
    ),
    StrategyDefinition(
        strategy_id="domestic_futures_cta_tsmom",
        version="v1",
        name="Domestic futures multi-horizon time-series momentum",
        family="cta_trend_following",
        availability=StrategyAvailability.CONDITIONAL,
        lifecycle=StrategyLifecycle.PAPER,
        asset_scope=("domestic_commodity_futures", "financial_futures"),
        required_access=("futures_eligible", "contract_eligibility"),
        required_data=("dated_contract_master", "daily_settlements", "volume", "open_interest", "margin", "roll_facts"),
        economic_engine="Diversified trend premia across independently traded futures markets, scaled by volatility.",
        personal_translation="A domestic futures CTA sub-strategy with signed positions, daily marking, margin and roll controls.",
        non_replicable_components=("global_cross_currency_universe", "institutional_execution", "proprietary_data"),
        risk_notes=("Trend signals are not forecasts; margin, contract roll and gap risk can dominate an individual signal.",),
    ),
    StrategyDefinition(
        strategy_id="domestic_futures_calendar_relative_value",
        version="v1",
        name="Domestic futures calendar-spread relative-value research",
        family="domestic_futures_relative_value",
        availability=StrategyAvailability.RESEARCH_ONLY,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("domestic_commodity_futures", "domestic_financial_futures"),
        required_access=("futures_eligible", "contract_eligibility"),
        required_data=(
            "dated_contract_master",
            "point_in_time_near_and_deferred_settlements",
            "expiry_and_delivery_rules",
            "volume_and_open_interest",
            "margin_position_limit_and_price_limit_facts",
        ),
        economic_engine=(
            "Matched-leg term-structure and relative-value research with explicitly observed carry, "
            "liquidity, margin and delivery risks; it is not a proxy for a global carry fund."
        ),
        personal_translation=(
            "Research-only calendar-spread diligence using dated executable contracts and a documented "
            "close-before-delivery discipline. No target is produced without an actual-contract data lane."
        ),
        non_replicable_components=(
            "global_cross_currency_funding",
            "otc_relative_value",
            "institutional_financing_and_collateral",
            "large_scale_cross_venue_execution",
        ),
        risk_notes=(
            (
                "A spread can lose on both legs when liquidity, margin, position limits, delivery rules or "
                "correlations change; contango or backwardation is not a standalone return forecast."
            ),
        ),
    ),
    StrategyDefinition(
        strategy_id="crypto_liquid_tsmom",
        version="v1",
        name="Liquid crypto time-series momentum sleeve (research only)",
        family="crypto_liquid_trend",
        availability=StrategyAvailability.RESEARCH_ONLY,
        lifecycle=StrategyLifecycle.DRAFT,
        asset_scope=("cryptoassets", "crypto_spot_or_derivatives"),
        required_access=("lawful_crypto_market_access",),
        required_data=(
            "dated_venue_ohlcv",
            "asset_listing_history",
            "venue_and_custody_terms",
            "liquidity_and_outage_history",
            "jurisdictional_compliance_review",
        ),
        economic_engine=(
            "Time-series momentum in liquid cryptoassets, with returns exposed to discontinuous "
            "liquidity, leverage, custody and venue-counterparty risk."
        ),
        personal_translation=(
            "A research-only liquid-trend study. The self-attested access field is a non-inference gate; "
            "it does not establish legal availability in the China mainland or any other regulated jurisdiction."
        ),
        non_replicable_components=(
            "jurisdiction_specific_legal_access",
            "venue_and_custody_due_diligence",
            "institutional_counterparty_controls",
            "continuous_24_7_operations",
        ),
        risk_notes=(
            (
                "For mainland-resident retail, this catalog does not present crypto as a defensible compliant "
                "implementation path or a workaround."
            ),
            "Self-attestation does not replace current independent legal, venue, custody or tax verification.",
        ),
    ),
    StrategyDefinition(
        strategy_id="global_market_neutral_stat_arb",
        version="v1",
        name="Global market-neutral statistical arbitrage",
        family="statistical_arbitrage",
        availability=StrategyAvailability.NOT_REPLICABLE,
        lifecycle=StrategyLifecycle.DISABLED,
        asset_scope=("global_equities", "derivatives"),
        required_access=("borrow", "prime_broker", "low_latency_execution", "global_data"),
        required_data=("point_in_time_global_universe", "corporate_actions", "borrow", "transaction_cost_model"),
        economic_engine="Relative mispricing harvested through neutral long-short portfolios and execution technology.",
        personal_translation="No economic-equivalent personal implementation is claimed.",
        non_replicable_components=("borrow", "neutral_execution", "capacity", "latency"),
        risk_notes=("Correlations and liquidity can fail together in stressed markets.",),
    ),
    StrategyDefinition(
        strategy_id="global_carry_relative_value",
        version="v1",
        name="Global carry and relative value",
        family="carry_relative_value",
        availability=StrategyAvailability.NOT_REPLICABLE,
        lifecycle=StrategyLifecycle.DISABLED,
        asset_scope=("global_rates", "fx", "credit", "commodities"),
        required_access=("global_derivatives", "funding", "fx", "institutional_counterparties"),
        required_data=("forward_curves", "funding", "collateral", "fx", "transaction_cost_model"),
        economic_engine="Compensation for bearing liquidity, funding, term and crash risk across curves.",
        personal_translation="No simple high-yield or futures-contango proxy is labelled as global carry.",
        non_replicable_components=("cross_currency_funding", "otc_access", "global_hedging"),
        risk_notes=("Carry losses can be correlated and discontinuous during deleveraging.",),
    ),
    StrategyDefinition(
        strategy_id="volatility_dispersion",
        version="v1",
        name="Index-component volatility dispersion",
        family="volatility_arbitrage",
        availability=StrategyAvailability.NOT_REPLICABLE,
        lifecycle=StrategyLifecycle.DISABLED,
        asset_scope=("listed_options", "index_options"),
        required_access=("options_permissions", "dynamic_hedging", "margin"),
        required_data=("option_surface", "correlation", "greeks", "intraday_execution"),
        economic_engine="Trading implied correlation and volatility-risk transfer, not a directional view.",
        personal_translation="No economic-equivalent retail implementation is claimed.",
        non_replicable_components=("surface_market_making", "continuous_delta_hedging", "tail_margin_capacity"),
        risk_notes=("Correlation can jump precisely when option liquidity weakens.",),
    ),
)


def list_personal_strategy_catalog(
    profile: PersonalAccessProfile | None = None,
) -> list[dict[str, object]]:
    """Return the catalog with a transparent eligibility verdict per entry."""

    return [strategy_catalog_entry(definition, profile) for definition in _CATALOG]


def get_personal_strategy_definition(strategy_id: str) -> StrategyDefinition:
    normalized = str(strategy_id).strip()
    for definition in _CATALOG:
        if definition.strategy_id == normalized:
            return definition
    raise ValueError(f"unknown personal strategy id: {strategy_id}")


def strategy_catalog_entry(
    definition: StrategyDefinition,
    profile: PersonalAccessProfile | None = None,
) -> dict[str, object]:
    """Add eligibility reasons without hiding structural non-replicability."""

    access = profile or PersonalAccessProfile()
    blockers = _access_blockers(definition, access)
    status = definition.availability.value
    if definition.availability == StrategyAvailability.NOT_REPLICABLE or blockers:
        decision = "blocked"
    elif definition.availability == StrategyAvailability.RESEARCH_ONLY or definition.lifecycle in {
        StrategyLifecycle.DRAFT,
        StrategyLifecycle.DISABLED,
    }:
        decision = "research_only"
    else:
        decision = "paper_eligible"
    payload = definition.to_dict()
    payload["profile_id"] = access.profile_id
    payload["eligibility"] = {
        "status": decision,
        "availability": status,
        "blockers": blockers,
        "required_access": list(definition.required_access),
    }
    if "lawful_crypto_market_access" in definition.required_access:
        payload["eligibility"]["legal_access_notice"] = _CRYPTO_LEGAL_ACCESS_NOTICE
    translation = _MARKET_TRANSLATIONS.get(definition.strategy_id)
    if translation is None:
        raise RuntimeError(
            f"missing market translation metadata for strategy {definition.strategy_id}"
        )
    # Rebuild nested containers so a caller cannot mutate catalog metadata for
    # a later capability call in the same process.
    payload["market_translation"] = {
        "institutional_archetypes": list(translation["institutional_archetypes"]),
        "china_mainland": dict(translation["china_mainland"]),
        "crypto_market": dict(translation["crypto_market"]),
        "personal_protocol": list(translation["personal_protocol"]),
        "reference_urls": list(translation["reference_urls"]),
        "research_only": True,
        "no_order_execution": True,
    }
    return payload


def _access_blockers(
    definition: StrategyDefinition,
    profile: PersonalAccessProfile,
) -> list[str]:
    blockers: list[str] = []
    required = set(definition.required_access)
    if "futures_eligible" in required and not profile.futures_eligible:
        blockers.append("futures eligibility is not recorded")
    if "contract_eligibility" in required and profile.futures_access_evidence is None:
        blockers.append(
            "dated broker/exchange instrument eligibility evidence is not recorded"
        )
    if "options_permissions" in required and not profile.option_eligible:
        blockers.append("options eligibility is not recorded")
    if "borrow" in required and not profile.margin_short_eligible:
        blockers.append("borrow/short access is not recorded")
    if "global_data" in required and not profile.licensed_eod_data:
        blockers.append("licensed global data entitlement is not recorded")
    if (
        "lawful_global_market_access" in required
        or any(token in required for token in ("global_derivatives", "global_data", "fx"))
    ) and not profile.lawful_global_market_access:
        blockers.append("lawful documented global-market access is not recorded")
    if "lawful_crypto_market_access" in required:
        if not profile.lawful_crypto_market_access:
            blockers.append(
                "self-attested lawful crypto-market access is not recorded; the assertion does not establish legality"
            )
        jurisdiction = (profile.residency_jurisdiction or "").strip().upper()
        if not jurisdiction:
            blockers.append("residency jurisdiction is not recorded for crypto research gating")
        elif jurisdiction in {"CN", "CHN", "CHINA", "MAINLAND_CHINA", "CHINA_MAINLAND"}:
            blockers.append(
                "this system does not present crypto as a personal implementation route for China-mainland residents"
            )
        if profile.crypto_access_evidence is None:
            blockers.append(
                "dated crypto venue, custody and data-entitlement evidence is not recorded"
            )
    if definition.availability == StrategyAvailability.NOT_REPLICABLE:
        blockers.append("strategy relies on institutional market structure that this system does not emulate")
    return list(dict.fromkeys(blockers))


def iter_personal_strategy_definitions() -> Iterable[StrategyDefinition]:
    """Expose immutable definitions for deterministic strategy registries."""

    return iter(_CATALOG)


_catalog_ids = {definition.strategy_id for definition in _CATALOG}
_translation_ids = set(_MARKET_TRANSLATIONS)
if _catalog_ids != _translation_ids:
    raise RuntimeError(
        "market translation metadata must cover exactly the personal strategy catalog; "
        f"missing={sorted(_catalog_ids - _translation_ids)}, "
        f"unknown={sorted(_translation_ids - _catalog_ids)}"
    )
