"""行业数据获取服务

使用 AkShare 获取 A 股行业分类数据，支持缓存机制。
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

# 默认缓存路径
DEFAULT_CACHE_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
CACHE_FILE = "industry_cache.json"
CACHE_TTL_HOURS = 24  # 缓存有效期 1 天


def async_wrap(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """将同步函数包装为异步"""
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_event_loop()
        return cast(T, await loop.run_in_executor(None, lambda: func(*args, **kwargs)))
    return wrapper


@dataclass
class IndustryInfo:
    """行业信息"""
    name: str                           # 行业名称
    code: Optional[str] = None          # 行业代码
    change_percent: Optional[float] = None  # 行业涨跌幅
    stock_count: int = 0                # 行业内股票数量
    updated_at: str = ""                # 更新时间

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
    """股票行业信息"""
    code: str                           # 股票代码
    name: str                           # 股票名称
    industry: str                       # 所属行业名称
    industry_code: Optional[str] = None  # 行业代码
    industry_change: Optional[float] = None  # 行业涨跌幅

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
    """行业数据缓存结构"""
    industries: dict[str, IndustryInfo] = field(default_factory=dict)  # 行业名 -> 行业信息
    stock_industries: dict[str, StockIndustry] = field(default_factory=dict)  # 股票代码 -> 股票行业
    industry_stocks: dict[str, list[str]] = field(default_factory=dict)  # 行业名 -> 股票代码列表
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
        """检查缓存是否过期"""
        if not self.cached_at:
            return True
        try:
            cached_time = datetime.fromisoformat(self.cached_at)
            return datetime.now() - cached_time > timedelta(hours=ttl_hours)
        except (ValueError, TypeError):
            return True


class IndustryService:
    """行业数据服务

    使用 AkShare 获取 A 股行业分类数据，支持缓存机制。
    主要接口:
    - stock_board_industry_name_em(): 获取行业板块名称列表
    - stock_individual_info_em(): 获取个股信息（包含行业）
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """初始化行业服务

        Args:
            cache_dir: 缓存目录，默认为 data/
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_file = self.cache_dir / CACHE_FILE
        self._cache: Optional[IndustryCache] = None
        self._initialized = False

        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def _load_cache(self) -> IndustryCache:
        """加载缓存"""
        if not self.cache_file.exists():
            return IndustryCache()

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return IndustryCache.from_dict(data)
        except Exception as e:
            logger.warning(f"加载行业缓存失败: {e}")
            return IndustryCache()

    async def _save_cache(self, cache: IndustryCache) -> None:
        """保存缓存"""
        try:
            cache.cached_at = datetime.now().isoformat()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"行业缓存已保存: {self.cache_file}")
        except Exception as e:
            logger.error(f"保存行业缓存失败: {e}")

    @async_wrap
    def _fetch_industry_list(self) -> pd.DataFrame:
        """获取行业板块列表（同步）

        Returns:
            DataFrame: 行业数据
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # 离线模式返回模拟数据
            return pd.DataFrame({
                "板块名称": ["银行", "证券", "保险", "房地产", "汽车"],
                "板块代码": ["BK0477", "BK0478", "BK0479", "BK0480", "BK0481"],
                "涨跌幅": [0.5, 1.2, -0.3, 0.8, 2.1],
                "总市值": [100000, 80000, 50000, 60000, 70000],
            })

        try:
            # 获取行业板块行情数据
            df = ak.stock_board_industry_name_em()
            return df
        except Exception as e:
            logger.error(f"获取行业板块列表失败: {e}")
            raise

    @async_wrap
    def _fetch_stock_industry(self, code: str) -> Optional[dict[str, Any]]:
        """获取个股行业信息（同步）

        Args:
            code: 股票代码

        Returns:
            行业信息字典
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # 离线模式返回模拟数据
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
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=code)
            if df.empty:
                return None

            # 转换为字典
            info = dict(zip(df["item"], df["value"]))
            return {
                "code": code,
                "name": info.get("股票简称", ""),
                "industry": info.get("行业", ""),
            }
        except Exception as e:
            logger.debug(f"获取股票 {code} 行业信息失败: {e}")
            return None

    @async_wrap
    def _fetch_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """获取行业内股票列表（同步）

        Args:
            industry_name: 行业名称

        Returns:
            DataFrame: 行业内股票数据
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            # 离线模式返回模拟数据
            offline_stocks = {
                "银行": [("000001", "平安银行"), ("600000", "浦发银行"), ("600036", "招商银行")],
                "房地产": [("000002", "万科A"), ("600048", "保利发展")],
                "白酒": [("600519", "贵州茅台"), ("000858", "五粮液")],
            }
            stocks = offline_stocks.get(industry_name, [])
            return pd.DataFrame(stocks, columns=["代码", "名称"])

        try:
            # 获取行业内股票
            df = ak.stock_board_industry_cons_em(symbol=industry_name)
            return df
        except Exception as e:
            logger.error(f"获取行业 {industry_name} 股票列表失败: {e}")
            return pd.DataFrame()

    async def initialize(self, force_refresh: bool = False) -> None:
        """初始化行业数据

        Args:
            force_refresh: 是否强制刷新
        """
        if self._initialized and not force_refresh:
            return

        # 加载缓存
        cache = await self._load_cache()

        # 检查缓存是否过期
        if not force_refresh and not cache.is_expired():
            logger.info("使用缓存的行业数据")
            self._cache = cache
            self._initialized = True
            return

        logger.info("开始刷新行业数据...")

        try:
            # 获取行业列表
            industry_df = await self._fetch_industry_list()

            # 构建行业信息
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

            # 保存缓存
            await self._save_cache(cache)

            self._cache = cache
            self._initialized = True
            logger.info(f"行业数据初始化完成，共 {len(cache.industries)} 个行业")

        except Exception as e:
            logger.error(f"初始化行业数据失败: {e}")
            # 使用已有缓存
            if cache.industries:
                self._cache = cache
                self._initialized = True

    async def get_all_industries(self) -> list[IndustryInfo]:
        """获取所有行业列表

        Returns:
            行业信息列表
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return []

        return list(self._cache.industries.values())

    async def get_industry_names(self) -> list[str]:
        """获取所有行业名称列表

        Returns:
            行业名称列表
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return []

        return list(self._cache.industries.keys())

    async def get_industry_info(self, industry_name: str) -> Optional[IndustryInfo]:
        """获取行业详情

        Args:
            industry_name: 行业名称

        Returns:
            行业信息
        """
        if not self._initialized:
            await self.initialize()

        if not self._cache:
            return None

        return self._cache.industries.get(industry_name)

    async def get_stock_industry(self, code: str) -> Optional[StockIndustry]:
        """获取股票所属行业

        Args:
            code: 股票代码

        Returns:
            股票行业信息
        """
        if not self._initialized:
            await self.initialize()

        # 标准化股票代码（6位数字）
        normalized_code = "".join(ch for ch in str(code) if ch.isdigit())
        if len(normalized_code) >= 6:
            normalized_code = normalized_code[-6:]

        # 先检查缓存
        if self._cache and normalized_code in self._cache.stock_industries:
            return self._cache.stock_industries[normalized_code]

        # 缓存中没有，从接口获取
        info = await self._fetch_stock_industry(normalized_code)
        if not info:
            return None

        industry_name = info.get("industry", "")
        if not industry_name:
            return None

        # 获取行业信息
        industry_info = await self.get_industry_info(industry_name)

        stock_industry = StockIndustry(
            code=normalized_code,
            name=info.get("name", ""),
            industry=industry_name,
            industry_code=industry_info.code if industry_info else None,
            industry_change=industry_info.change_percent if industry_info else None,
        )

        # 更新缓存
        if self._cache:
            self._cache.stock_industries[normalized_code] = stock_industry
            await self._save_cache(self._cache)

        return stock_industry

    async def get_industry_stocks(self, industry_name: str) -> list[str]:
        """获取行业内股票代码列表

        Args:
            industry_name: 行业名称

        Returns:
            股票代码列表
        """
        # 检查缓存
        if self._cache and industry_name in self._cache.industry_stocks:
            return self._cache.industry_stocks[industry_name]

        # 从接口获取
        df = await self._fetch_industry_stocks(industry_name)
        if df.empty:
            return []

        # 提取股票代码
        code_col = "代码" if "代码" in df.columns else "code"
        codes = [str(code).zfill(6) for code in df[code_col].tolist()]

        # 更新缓存
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
        """按行业筛选股票

        Args:
            codes: 待筛选的股票代码列表
            include_industries: 包含的行业列表（白名单）
            exclude_industries: 排除的行业列表（黑名单）

        Returns:
            筛选后的股票代码列表
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

            # 白名单筛选
            if include_industries and industry not in include_industries:
                continue

            # 黑名单筛选
            if exclude_industries and industry in exclude_industries:
                continue

            result.append(code)

        return result

    async def get_industry_change(self, industry_name: str) -> Optional[float]:
        """获取行业涨跌幅

        Args:
            industry_name: 行业名称

        Returns:
            涨跌幅百分比
        """
        industry_info = await self.get_industry_info(industry_name)
        if industry_info:
            return industry_info.change_percent
        return None

    async def refresh(self) -> bool:
        """强制刷新行业数据

        Returns:
            是否成功
        """
        try:
            await self.initialize(force_refresh=True)
            return True
        except Exception as e:
            logger.error(f"刷新行业数据失败: {e}")
            return False


# 全局行业服务实例
_industry_service: Optional[IndustryService] = None


def get_industry_service() -> IndustryService:
    """获取全局行业服务实例"""
    global _industry_service
    if _industry_service is None:
        _industry_service = IndustryService()
    return _industry_service
