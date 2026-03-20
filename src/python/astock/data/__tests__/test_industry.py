"""行业数据服务测试"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

from ..industry import (
    IndustryService,
    IndustryInfo,
    StockIndustry,
    IndustryCache,
    get_industry_service,
)


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """创建临时缓存目录"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def industry_service(temp_cache_dir: Path) -> IndustryService:
    """创建行业服务实例"""
    return IndustryService(cache_dir=temp_cache_dir)


class TestIndustryInfo:
    """测试 IndustryInfo 数据类"""

    def test_to_dict(self):
        """测试转换为字典"""
        info = IndustryInfo(
            name="银行",
            code="BK0477",
            change_percent=0.5,
            stock_count=42,
            updated_at="2026-03-10T10:00:00",
        )
        result = info.to_dict()
        assert result["name"] == "银行"
        assert result["code"] == "BK0477"
        assert result["change_percent"] == 0.5
        assert result["stock_count"] == 42

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "name": "证券",
            "code": "BK0478",
            "change_percent": 1.2,
            "stock_count": 50,
            "updated_at": "2026-03-10T10:00:00",
        }
        info = IndustryInfo.from_dict(data)
        assert info.name == "证券"
        assert info.code == "BK0478"
        assert info.change_percent == 1.2


class TestStockIndustry:
    """测试 StockIndustry 数据类"""

    def test_to_dict(self):
        """测试转换为字典"""
        stock = StockIndustry(
            code="000001",
            name="平安银行",
            industry="银行",
            industry_code="BK0477",
            industry_change=0.5,
        )
        result = stock.to_dict()
        assert result["code"] == "000001"
        assert result["name"] == "平安银行"
        assert result["industry"] == "银行"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "code": "600519",
            "name": "贵州茅台",
            "industry": "白酒",
            "industry_code": "BK0490",
            "industry_change": 2.1,
        }
        stock = StockIndustry.from_dict(data)
        assert stock.code == "600519"
        assert stock.industry == "白酒"


class TestIndustryCache:
    """测试行业缓存"""

    def test_is_expired_with_empty_cache(self):
        """测试空缓存是否过期"""
        cache = IndustryCache()
        assert cache.is_expired() is True

    def test_is_expired_with_old_cache(self):
        """测试过期缓存"""
        cache = IndustryCache(
            cached_at=(datetime.now() - timedelta(hours=25)).isoformat()
        )
        assert cache.is_expired() is True

    def test_is_expired_with_fresh_cache(self):
        """测试新鲜缓存"""
        cache = IndustryCache(
            cached_at=datetime.now().isoformat()
        )
        assert cache.is_expired() is False

    def test_to_dict_and_from_dict(self):
        """测试序列化和反序列化"""
        cache = IndustryCache(
            industries={
                "银行": IndustryInfo(name="银行", code="BK0477"),
                "证券": IndustryInfo(name="证券", code="BK0478"),
            },
            stock_industries={
                "000001": StockIndustry(code="000001", name="平安银行", industry="银行"),
            },
            industry_stocks={
                "银行": ["000001", "600000"],
            },
            cached_at=datetime.now().isoformat(),
        )

        # 序列化
        data = cache.to_dict()
        assert "industries" in data
        assert "stock_industries" in data
        assert "industry_stocks" in data

        # 反序列化
        restored = IndustryCache.from_dict(data)
        assert len(restored.industries) == 2
        assert "银行" in restored.industries
        assert restored.stock_industries["000001"].industry == "银行"


class TestIndustryService:
    """测试行业服务"""

    def test_initialization(self, industry_service: IndustryService):
        """测试服务初始化"""
        assert industry_service.cache_dir.exists()
        assert industry_service._cache is None
        assert industry_service._initialized is False

    @pytest.mark.asyncio
    async def test_initialize_offline(self, industry_service: IndustryService):
        """测试离线初始化"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            await industry_service.initialize()
            assert industry_service._initialized is True
            assert industry_service._cache is not None
            assert len(industry_service._cache.industries) > 0
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_get_industry_names_offline(self, industry_service: IndustryService):
        """测试获取行业名称列表（离线）"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            names = await industry_service.get_industry_names()
            assert len(names) > 0
            assert "银行" in names
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_get_stock_industry_offline(self, industry_service: IndustryService):
        """测试获取股票行业（离线）"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            stock_industry = await industry_service.get_stock_industry("000001")
            assert stock_industry is not None
            assert stock_industry.code == "000001"
            assert stock_industry.industry == "银行"
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_get_stock_industry_cache(self, industry_service: IndustryService):
        """测试股票行业缓存"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            # 第一次获取
            result1 = await industry_service.get_stock_industry("000001")
            assert result1 is not None

            # 第二次应该从缓存获取
            result2 = await industry_service.get_stock_industry("000001")
            assert result2 is not None
            assert result1.industry == result2.industry
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_filter_by_industry_offline(self, industry_service: IndustryService):
        """测试按行业筛选（离线）"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            codes = ["000001", "000002", "600519"]

            # 只选银行
            filtered = await industry_service.filter_by_industry(
                codes, include_industries=["银行"]
            )
            assert "000001" in filtered
            assert "600519" not in filtered

            # 排除银行
            excluded = await industry_service.filter_by_industry(
                codes, exclude_industries=["银行"]
            )
            assert "000001" not in excluded
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_cache_persistence(self, industry_service: IndustryService):
        """测试缓存持久化"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            # 初始化并获取数据
            await industry_service.initialize()
            await industry_service.get_stock_industry("000001")

            # 创建新实例
            new_service = IndustryService(cache_dir=industry_service.cache_dir)
            await new_service.initialize()

            # 应该从缓存加载
            assert new_service._cache is not None
            assert not new_service._cache.is_expired()
        finally:
            del os.environ["ASTOCK_OFFLINE"]


class TestGetIndustryService:
    """测试全局服务实例"""

    def test_singleton(self):
        """测试单例模式"""
        service1 = get_industry_service()
        service2 = get_industry_service()
        assert service1 is service2
