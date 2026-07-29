"""Industry data service tests"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
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
    """Create temporary cache directory"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def industry_service(temp_cache_dir: Path) -> IndustryService:
    """Create industry service instance"""
    return IndustryService(cache_dir=temp_cache_dir)


class TestIndustryInfo:
    """Test IndustryInfo data class"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
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
        """Test creation from dictionary"""
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
    """Test StockIndustry data class"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
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
        """Test creation from dictionary"""
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
    """Test industry cache"""

    def test_is_expired_with_empty_cache(self):
        """Test whether empty cache is expired"""
        cache = IndustryCache()
        assert cache.is_expired() is True

    def test_is_expired_with_old_cache(self):
        """Test expired cache"""
        cache = IndustryCache(
            cached_at=(datetime.now() - timedelta(hours=25)).isoformat()
        )
        assert cache.is_expired() is True

    def test_is_expired_with_fresh_cache(self):
        """Test fresh cache"""
        cache = IndustryCache(
            cached_at=datetime.now().isoformat()
        )
        assert cache.is_expired() is False

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
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

        # Serialize
        data = cache.to_dict()
        assert "industries" in data
        assert "stock_industries" in data
        assert "industry_stocks" in data

        # Deserialize
        restored = IndustryCache.from_dict(data)
        assert len(restored.industries) == 2
        assert "银行" in restored.industries
        assert restored.stock_industries["000001"].industry == "银行"


class TestIndustryService:
    """Test industry service"""

    def test_initialization(self, industry_service: IndustryService):
        """Test service initialization"""
        assert industry_service.cache_dir.exists()
        assert industry_service._cache is None
        assert industry_service._initialized is False

    @pytest.mark.asyncio
    async def test_initialize_offline(self, industry_service: IndustryService):
        """Test offline initialization"""
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
        """Test getting industry name list (offline)"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            names = await industry_service.get_industry_names()
            assert len(names) > 0
            assert "银行" in names
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_get_stock_industry_offline(self, industry_service: IndustryService):
        """Test getting stock industry (offline)"""
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
        """Test stock industry caching"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            # First retrieval
            result1 = await industry_service.get_stock_industry("000001")
            assert result1 is not None

            # Second retrieval should come from cache
            result2 = await industry_service.get_stock_industry("000001")
            assert result2 is not None
            assert result1.industry == result2.industry
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_filter_by_industry_offline(self, industry_service: IndustryService):
        """Test filtering by industry (offline)"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            codes = ["000001", "000002", "600519"]

            # Select only banking
            filtered = await industry_service.filter_by_industry(
                codes, include_industries=["银行"]
            )
            assert "000001" in filtered
            assert "600519" not in filtered

            # Exclude banking
            excluded = await industry_service.filter_by_industry(
                codes, exclude_industries=["银行"]
            )
            assert "000001" not in excluded
        finally:
            del os.environ["ASTOCK_OFFLINE"]

    @pytest.mark.asyncio
    async def test_cache_persistence(self, industry_service: IndustryService):
        """Test cache persistence"""
        os.environ["ASTOCK_OFFLINE"] = "1"
        try:
            # Initialize and get data
            await industry_service.initialize()
            await industry_service.get_stock_industry("000001")

            # Create new instance
            new_service = IndustryService(cache_dir=industry_service.cache_dir)
            await new_service.initialize()

            # Should load from cache
            assert new_service._cache is not None
            assert not new_service._cache.is_expired()
        finally:
            del os.environ["ASTOCK_OFFLINE"]


class TestGetIndustryService:
    """Test global service instance"""

    def test_singleton(self):
        """Test singleton pattern"""
        service1 = get_industry_service()
        service2 = get_industry_service()
        assert service1 is service2
