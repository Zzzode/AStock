"""Personal-investor strategy research domain.

This package produces transparent research, paper targets and deterministic
replays.  It contains no brokerage or automated-order capability.
"""

from .allocation import (
    AllocationPolicy,
    AllocationState,
    MultiSleeveAllocator,
    allocate_multi_sleeve,
)
from .catalog import (
    get_personal_strategy_definition,
    iter_personal_strategy_definitions,
    list_personal_strategy_catalog,
    strategy_catalog_entry,
)
from .crypto import (
    CryptoAssetSpec,
    CryptoTimeSeriesMomentumConfig,
)
from .cta import (
    FuturesBacktestResult,
    FuturesExecutionAssumptions,
    run_frozen_public_domestic_futures_cta_backtest,
)
from .data import (
    PUBLIC_DOMESTIC_FUTURES_SOURCE,
    build_public_domestic_futures_cta_input,
    parse_public_domestic_futures_cta_input,
)
from .equity import (
    AShareFactorTiltConfig,
    AShareFactorTiltStrategy,
    EarningsEventRepricingConfig,
    EarningsEventRepricingStrategy,
    PublicAnnouncementEarningsRepricingStrategy,
    build_ashare_factor_tilt_proposal,
    build_earnings_event_repricing_proposal,
    build_public_announcement_earnings_repricing_proposal,
)
from .models import (
    CTAStrategyConfig,
    CryptoAccessEvidence,
    FuturesAccessEvidence,
    FuturesInstrumentSpec,
    FuturesTarget,
    PersonalAccessProfile,
    StrategyAvailability,
    StrategyDefinition,
    StrategyLifecycle,
    StrategyProposal,
)
from .registry import (
    StrategyRegistry,
    record_run,
    register_definition,
    transition_lifecycle,
)

__all__ = [
    "PUBLIC_DOMESTIC_FUTURES_SOURCE",
    "AShareFactorTiltConfig",
    "AShareFactorTiltStrategy",
    "AllocationPolicy",
    "AllocationState",
    "CTAStrategyConfig",
    "CryptoAccessEvidence",
    "CryptoAssetSpec",
    "CryptoTimeSeriesMomentumConfig",
    "EarningsEventRepricingConfig",
    "EarningsEventRepricingStrategy",
    "FuturesAccessEvidence",
    "FuturesBacktestResult",
    "FuturesExecutionAssumptions",
    "FuturesInstrumentSpec",
    "FuturesTarget",
    "MultiSleeveAllocator",
    "PersonalAccessProfile",
    "PublicAnnouncementEarningsRepricingStrategy",
    "StrategyAvailability",
    "StrategyDefinition",
    "StrategyLifecycle",
    "StrategyProposal",
    "StrategyRegistry",
    "allocate_multi_sleeve",
    "build_ashare_factor_tilt_proposal",
    "build_earnings_event_repricing_proposal",
    "build_public_announcement_earnings_repricing_proposal",
    "build_public_domestic_futures_cta_input",
    "get_personal_strategy_definition",
    "iter_personal_strategy_definitions",
    "list_personal_strategy_catalog",
    "parse_public_domestic_futures_cta_input",
    "record_run",
    "register_definition",
    "run_frozen_public_domestic_futures_cta_backtest",
    "strategy_catalog_entry",
    "transition_lifecycle",
]
