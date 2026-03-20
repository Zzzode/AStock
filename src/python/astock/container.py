"""依赖注入容器

统一管理所有服务的创建和依赖，避免 CLI/API 重复实例化逻辑。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .storage import Database
from .quote import QuoteService
from .stock_picker import StockScreener
from .recommend import Recommender
from .data import get_industry_service, IndustryService
from .config import ConfigManager
from .memory import MemoryStore, FeedbackLearner
from .services import AnalysisService


@dataclass
class ServiceContainer:
    """统一管理所有服务的创建和依赖"""

    db_path: Path = field(default_factory=lambda: Path("data/stocks.db"))
    data_path: Path = field(default_factory=lambda: Path("data"))

    _db: Optional[Database] = field(default=None, repr=False)
    _quote_service: Optional[QuoteService] = field(default=None, repr=False)
    _industry_service: Optional[IndustryService] = field(default=None, repr=False)
    _config_manager: Optional[ConfigManager] = field(default=None, repr=False)
    _memory_store: Optional[MemoryStore] = field(default=None, repr=False)
    _feedback_learner: Optional[FeedbackLearner] = field(default=None, repr=False)
    _analysis_service: Optional[AnalysisService] = field(default=None, repr=False)

    async def initialize(self) -> None:
        """初始化容器，建立数据库连接"""
        self._db = Database(str(self.db_path))
        await self._db.connect()

    async def cleanup(self) -> None:
        """清理资源，关闭数据库连接"""
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> Database:
        """获取数据库实例"""
        if not self._db:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._db

    @property
    def quote_service(self) -> QuoteService:
        """获取行情服务实例"""
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    @property
    def industry_service(self) -> IndustryService:
        """获取行业服务实例"""
        if not self._industry_service:
            self._industry_service = get_industry_service()
        return self._industry_service

    @property
    def config_manager(self) -> ConfigManager:
        """获取配置管理器实例"""
        if not self._config_manager:
            self._config_manager = ConfigManager()
        return self._config_manager

    @property
    def memory_store(self) -> MemoryStore:
        """获取记忆存储实例"""
        if not self._memory_store:
            self._memory_store = MemoryStore(self.data_path / "memory.json")
        return self._memory_store

    @property
    def feedback_learner(self) -> FeedbackLearner:
        """获取反馈学习器实例"""
        if not self._feedback_learner:
            self._feedback_learner = FeedbackLearner(self.data_path / "feedback.json")
        return self._feedback_learner

    @property
    def analysis_service(self) -> AnalysisService:
        """获取分析服务实例"""
        if not self._analysis_service:
            self._analysis_service = AnalysisService(self.db, self.quote_service)
        return self._analysis_service

    def get_screener(self) -> StockScreener:
        """获取选股器实例"""
        return StockScreener(self.quote_service)

    def get_recommender(self) -> Recommender:
        """获取推荐器实例"""
        return Recommender(self.get_screener(), self.industry_service)

    async def ensure_industry_service_ready(self) -> None:
        """确保行业服务已初始化"""
        await self.industry_service.initialize()


# 全局容器实例（用于简单场景）
_container: Optional[ServiceContainer] = None


async def get_container() -> ServiceContainer:
    """获取全局容器实例

    注意：使用后需要调用 cleanup_container() 清理资源
    """
    global _container
    if not _container:
        _container = ServiceContainer()
        await _container.initialize()
    return _container


async def cleanup_container() -> None:
    """清理全局容器"""
    global _container
    if _container:
        await _container.cleanup()
        _container = None