"""Dependency Injection Container

Centrally manages creation and dependencies of all services,
avoiding duplicated instantiation logic across CLI/API.
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
    """Centrally manages creation and dependencies of all services"""

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
        """Initialize the container and establish database connection"""
        self._db = Database(str(self.db_path))
        await self._db.connect()

    async def cleanup(self) -> None:
        """Clean up resources and close database connection"""
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> Database:
        """Get database instance"""
        if not self._db:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._db

    @property
    def quote_service(self) -> QuoteService:
        """Get quote service instance"""
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    @property
    def industry_service(self) -> IndustryService:
        """Get industry service instance"""
        if not self._industry_service:
            self._industry_service = get_industry_service()
        return self._industry_service

    @property
    def config_manager(self) -> ConfigManager:
        """Get config manager instance"""
        if not self._config_manager:
            self._config_manager = ConfigManager()
        return self._config_manager

    @property
    def memory_store(self) -> MemoryStore:
        """Get memory store instance"""
        if not self._memory_store:
            self._memory_store = MemoryStore(self.data_path / "memory.json")
        return self._memory_store

    @property
    def feedback_learner(self) -> FeedbackLearner:
        """Get feedback learner instance"""
        if not self._feedback_learner:
            self._feedback_learner = FeedbackLearner(self.data_path / "team-feedback.json")
        return self._feedback_learner

    @property
    def analysis_service(self) -> AnalysisService:
        """Get analysis service instance"""
        if not self._analysis_service:
            self._analysis_service = AnalysisService(self.db, self.quote_service)
        return self._analysis_service

    def get_screener(self) -> StockScreener:
        """Get stock screener instance"""
        return StockScreener(self.quote_service)

    def get_recommender(self) -> Recommender:
        """Get recommender instance"""
        return Recommender(self.get_screener(), self.industry_service)

    async def ensure_industry_service_ready(self) -> None:
        """Ensure industry service is initialized"""
        await self.industry_service.initialize()


# Global container instance (for simple scenarios)
_container: Optional[ServiceContainer] = None


async def get_container() -> ServiceContainer:
    """Get global container instance

    Note: Call cleanup_container() to release resources after use
    """
    global _container
    if not _container:
        _container = ServiceContainer()
        await _container.initialize()
    return _container


async def cleanup_container() -> None:
    """Clean up global container"""
    global _container
    if _container:
        await _container.cleanup()
        _container = None
