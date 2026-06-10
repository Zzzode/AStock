"""Industry data fetching service

Uses AkShare to fetch A-share industry classification data with caching support.
"""

import json
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable, TypeVar, ParamSpec, cast
from functools import wraps
import os

import akshare as ak
import pandas as pd

from ..utils import get_logger

logger = get_logger("industry")

P = ParamSpec("P")
T = TypeVar("T")

# Default cache path
DEFAULT_CACHE_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
CACHE_FILE = "industry_cache.json"
CACHE_TTL_HOURS = 24  # Cache validity period: 1 day


def async_wrap(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Wrap a synchronous function as async"""
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return cast(T, await loop.run_in_executor(None, lambda: func(*args, **kwargs)))
    return wrapper


@dataclass
class IndustryInfo:
    """Industry information"""
    name: str                           # Industry name
    code: Optional[str] = None          # Industry code
    change_percent: Optional[float] = None  # Industry change percentage
    stock_count: int = 0                # Number of stocks in the industry
    updated_at: str = ""                # Update timestamp

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndustryInfo":
        return cls(
            name=data.get("name", ""),
            code=data.get("code"),
            change_percent=data.get("change_percent"),
            stock_count=data.get("stock_count", 0),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class StockIndustry:
    """Stock industry information"""
    code: str                           # Stock code
    name: str                           # Stock name
    industry: str                       # Industry name
    industry_code: Optional[str] = None  # Industry code
    industry_change: Optional[float] = None  # Industry change percentage

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StockIndustry":
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            industry=data.get("industry", ""),
            industry_code=data.get("industry_code"),
            industry_change=data.get("industry_change"),
        )


@dataclass
class IndustryCache:
    """Industry data cache structure"""
    industries: dict[str, IndustryInfo] = field(default_factory=dict)  # Industry name -> industry info
    stock_industries: dict[str, StockIndustry] = field(default_factory=dict)  # Stock code -> stock industry
    industry_stocks: dict[str, list[str]] = field(default_factory=dict)  # Industry name -> stock code list
    cached_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "industries": {k: v.to_dict() for k, v in self.industries.items()},
            "stock_industries": {k: v.to_dict() for k, v in self.stock_industries.items()},
            "industry_stocks": self.industry_stocks,
            "cached_at": self.cached_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndustryCache":
        return cls(
            industries={k: IndustryInfo.from_dict(v) for k, v in data.get("industries", {}).items()},
            stock_industries={k: StockIndustry.from_dict(v) for k, v in data.get("stock_industries", {}).items()},
            industry_stocks=data.get("industry_stocks", {}),
            cached_at=data.get("cached_at", ""),
        )

    def is_expired(self, ttl_hours: int = CACHE_TTL_HOURS) -> bool:
        """Check whether cache is expired"""
        if not self.cached_at:
            return True
        try:
            cached_time = datetime.fromisoformat(self.cached_at)
            return datetime.now() - cached_time > timedelta(hours=ttl_hours)
        except (ValueError, TypeError):
            return True


class IndustryService:
    """Industry data service

    Uses AkShare to fetch A-share industry classification data with caching support.
    Main interfaces:
    - stock_board_industry_name_em(): Get industry sector name list
    - stock_individual_info_em(): Get individual stock info (including industry)
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize industry service

        Args:
            cache_dir: Cache directory, defaults to data/
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_file = self.cache_dir / CACHE_FILE
        self._cache: Optional[IndustryCache] = None
        self._initialized = False

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def _load_cache(self) -> IndustryCache:
        """Load cache"""
        if not self.cache_file.exists():
            return IndustryCache()

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return IndustryCache.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load industry cache: {e}")
            return IndustryCache()

    async def _save_cache(self, cache: IndustryCache) -> None:
        """Save cache"""
        try:
            cache.cached_at = datetime.now().isoformat()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"Industry cache saved: {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save industry cache: {e}")

    @async_wrap
    def _fetch_industry_list(self) -> pd.DataFrame:
        """Fetch industry sector list (synchronous)

        Returns:
            DataFrame: Industry data
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # Offline mode returns mock data
            return pd.DataFrame({
                "板块名称": ["银行", "证券", "保险", "房地产", "汽车"],
                "板块代码": ["BK0477", "BK0478", "BK0479", "BK0480", "BK0481"],
                "涨跌幅": [0.5, 1.2, -0.3, 0.8, 2.1],
                "总市值": [100000, 80000, 50000, 60000, 70000],
            })

        try:
            # Fetch industry sector market data
            df = ak.stock_board_industry_name_em()
            return df
        except Exception as e:
            logger.error(f"Failed to fetch industry sector list: {e}")
            raise

    @async_wrap
    def _fetch_stock_industry(self, code: str) -> Optional[dict[str, Any]]:
        """Fetch individual stock industry info (synchronous)

        Args:
            code: Stock code

        Returns:
            Industry info dictionary
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # Offline mode returns mock data
            offline_industries = {
                "000001": "银行",
                "000002": "房地产",
                "600000": "银行",
                "600036": "银行",
                "600519": "白酒",
            }
            return {
                "code": code,
                "industry": offline_industries.get(code, "其他"),
            }

        try:
            # Fetch individual stock info
            df = ak.stock_individual_info_em(symbol=code)
            if df.empty:
                return None

            # Convert to dictionary
            info = dict(zip(df["item"], df["value"]))
            return {
                "code": code,
                "name": info.get("股票简称", ""),
                "industry": info.get("行业", ""),
            }
        except Exception as e:
            logger.debug(f"Failed to fetch industry info for stock {code}: {e}")
            return None

    @async_wrap
    def _fetch_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """Fetch stock list within an industry (synchronous)

        Args:
            industry_name: Industry name

        Returns:
            DataFrame: Stock data within the industry
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # Offline mode returns mock data
            offline_stocks = {
                "银行": [("000001", "平安银行"), ("600000", "浦发银行"), ("600036", "招商银行")],
                "房地产": [("000002", "万科A"), ("600048", "保利发展")],
                "白酒": [("600519", "贵州茅台"), ("000858", "五粮液")],
            }
            stocks = offline_stocks.get(industry_name, [])
            return pd.DataFrame(stocks, columns=["代码", "名称"])

        try:
            # Fetch stocks within industry
            df = ak.stock_board_industry_cons_em(symbol=industry_name)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch stock list for industry {industry_name}: {e}")
            return pd.DataFrame()

    async def initialize(
        self,
        force_refresh: bool = False,
        allow_stale_cache: bool = False,
    ) -> None:
        """Initialize industry data

        Args:
            force_refresh: Whether to force refresh
            allow_stale_cache: Whether to allow using expired cache directly
        """
        if self._initialized and not force_refresh:
            return

        # Load cache
        cache = await self._load_cache()

        # Check if cache is expired
        if not force_refresh and not cache.is_expired():
            logger.info("Using cached industry data")
            self._cache = cache
            self._initialized = True
            return

        if not force_refresh and allow_stale_cache and cache.industries:
            logger.info("Using expired industry cache data")
            self._cache = cache
            self._initialized = True
            return

        logger.info("Starting industry data refresh...")

        try:
            # Fetch industry list
            industry_df = await self._fetch_industry_list()

            # Build industry information
            for _, row in industry_df.iterrows():
                name = str(row.get("板块名称", ""))
                if not name:
                    continue

                industry_info = IndustryInfo(
                    name=name,
                    code=str(row.get("板块代码", "")) if "板块代码" in row else None,
                    change_percent=float(row.get("涨跌幅", 0)) if "涨跌幅" in row else None,
                    stock_count=int(row.get("股票家数", 0)) if "股票家数" in row else 0,
                    updated_at=datetime.now().isoformat(),
                )
                cache.industries[name] = industry_info

            # Save cache
            await self._save_cache(cache)

            self._cache = cache
            self._initialized = True
            logger.info(f"Industry data initialization complete, {len(cache.industries)} industries total")

        except Exception as e:
            logger.error(f"Failed to initialize industry data: {e}")
            # Use existing cache
            if cache.industries:
                self._cache = cache
                self._initialized = True

    async def get_all_industries(self) -> list[IndustryInfo]:
        """Get all industry list

        Returns:
            Industry info list
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return []

        return list(self._cache.industries.values())

    async def get_industry_names(self) -> list[str]:
        """Get all industry name list

        Returns:
            Industry name list
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return []

        return list(self._cache.industries.keys())

    async def get_industry_info(self, industry_name: str) -> Optional[IndustryInfo]:
        """Get industry details

        Args:
            industry_name: Industry name

        Returns:
            Industry information
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return None

        return self._cache.industries.get(industry_name)

    async def get_stock_industry(self, code: str) -> Optional[StockIndustry]:
        """Get stock's industry

        Args:
            code: Stock code

        Returns:
            Stock industry information
        """
        if not self._initialized:
            await self.initialize()

        # Normalize stock code (6 digits)
        normalized_code = "".join(ch for ch in str(code) if ch.isdigit())
        if len(normalized_code) >= 6:
            normalized_code = normalized_code[-6:]

        # Check cache first
        if self._cache and normalized_code in self._cache.stock_industries:
            return self._cache.stock_industries[normalized_code]

        # Not in cache, fetch from API
        info = await self._fetch_stock_industry(normalized_code)
        if not info:
            return None

        industry_name = info.get("industry", "")
        if not industry_name:
            return None

        # Get industry info
        industry_info = await self.get_industry_info(industry_name)

        stock_industry = StockIndustry(
            code=normalized_code,
            name=info.get("name", ""),
            industry=industry_name,
            industry_code=industry_info.code if industry_info else None,
            industry_change=industry_info.change_percent if industry_info else None,
        )

        # Update cache
        if self._cache:
            self._cache.stock_industries[normalized_code] = stock_industry
            await self._save_cache(self._cache)

        return stock_industry

    async def get_industry_stocks(self, industry_name: str) -> list[str]:
        """Get stock code list within an industry

        Args:
            industry_name: Industry name

        Returns:
            Stock code list
        """
        # Check cache
        if self._cache and industry_name in self._cache.industry_stocks:
            return self._cache.industry_stocks[industry_name]

        # Fetch from API
        df = await self._fetch_industry_stocks(industry_name)
        if df.empty:
            return []

        # Extract stock codes
        code_col = "代码" if "代码" in df.columns else "code"
        codes = [str(code).zfill(6) for code in df[code_col].tolist()]

        # Update cache
        if self._cache:
            self._cache.industry_stocks[industry_name] = codes
            await self._save_cache(self._cache)

        return codes

    async def filter_by_industry(
        self,
        codes: list[str],
        include_industries: Optional[list[str]] = None,
        exclude_industries: Optional[list[str]] = None,
    ) -> list[str]:
        """Filter stocks by industry

        Args:
            codes: Stock code list to filter
            include_industries: Industries to include (whitelist)
            exclude_industries: Industries to exclude (blacklist)

        Returns:
            Filtered stock code list
        """
        if not include_industries and not exclude_industries:
            return codes

        if not self._initialized:
            await self.initialize()

        result = []
        for code in codes:
            stock_industry = await self.get_stock_industry(code)
            if not stock_industry:
                continue

            industry = stock_industry.industry

            # Whitelist filtering
            if include_industries and industry not in include_industries:
                continue

            # Blacklist filtering
            if exclude_industries and industry in exclude_industries:
                continue

            result.append(code)

        return result

    async def get_industry_change(self, industry_name: str) -> Optional[float]:
        """Get industry change percentage

        Args:
            industry_name: Industry name

        Returns:
            Change percentage
        """
        industry_info = await self.get_industry_info(industry_name)
        if industry_info:
            return industry_info.change_percent
        return None

    async def refresh(self) -> bool:
        """Force refresh industry data

        Returns:
            Whether successful
        """
        try:
            await self.initialize(force_refresh=True)
            return True
        except Exception as e:
            logger.error(f"Failed to refresh industry data: {e}")
            return False


# Global industry service instance
_industry_service: Optional[IndustryService] = None


def get_industry_service() -> IndustryService:
    """Get global industry service instance"""
    global _industry_service
    if _industry_service is None:
        _industry_service = IndustryService()
    return _industry_service
