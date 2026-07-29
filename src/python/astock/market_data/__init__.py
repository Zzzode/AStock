"""Licensed market-data adapters that emit source-frozen research packets."""

from .archive import verify_frozen_market_archive
from .jqdata import JQDataMinuteAdapter
from .public_observation import (
    PublicMarketObservationPacket,
    build_public_market_observation_packet,
)
from .public_spot import (
    EASTMONEY_A_SHARE_SPOT_SOURCE,
    fetch_eastmoney_a_share_spot,
    fetch_sina_a_share_spot,
    SINA_A_SHARE_SPOT_SOURCE,
)
from .tushare_pro import TushareProBacktestAdapter, TushareUniverseSnapshotPacket

__all__ = [
    "JQDataMinuteAdapter",
    "PublicMarketObservationPacket",
    "TushareProBacktestAdapter",
    "TushareUniverseSnapshotPacket",
    "build_public_market_observation_packet",
    "EASTMONEY_A_SHARE_SPOT_SOURCE",
    "fetch_eastmoney_a_share_spot",
    "fetch_sina_a_share_spot",
    "SINA_A_SHARE_SPOT_SOURCE",
    "verify_frozen_market_archive",
]
