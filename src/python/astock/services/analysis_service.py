"""分析服务

提供原始技术指标数据和上下文信息，不进行任何解读。
解读由 LLM 进行动态推理。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..storage import Database
from ..quote import QuoteService
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.interpretation import detect_signals, calculate_statistics
from ..memory import MemoryStore, FeedbackLearner


@dataclass
class FullAnalysisResult:
    """完整分析结果 - 原始数据 + 上下文"""

    code: str
    name: Optional[str] = None

    # 原始指标数据
    indicators: dict[str, Any] = field(default_factory=dict)

    # 前一日指标（用于对比）
    prev_indicators: dict[str, Any] = field(default_factory=dict)

    # 检测到的信号（只含类型和数值，不含解读）
    signals: list[dict[str, Any]] = field(default_factory=list)

    # 信号统计
    signal_stats: dict[str, Any] = field(default_factory=dict)

    # 历史上下文
    history: dict[str, Any] = field(default_factory=dict)

    # 用户反馈统计
    feedback_stats: dict[str, Any] = field(default_factory=dict)

    # 行情数据
    quote: dict[str, Any] = field(default_factory=dict)

    # 元数据
    analyzed_at: datetime = field(default_factory=datetime.now)
    days: int = 100
    error: Optional[str] = None


class AnalysisService:
    """分析服务 - 提供原始数据和上下文"""

    def __init__(
        self,
        db: Database,
        quote_service: Optional[QuoteService] = None,
        memory_store: Optional[MemoryStore] = None,
        feedback_learner: Optional[FeedbackLearner] = None,
    ):
        self.db = db
        self._quote_service = quote_service
        self._memory_store = memory_store
        self._feedback_learner = feedback_learner

    @property
    def quote_service(self) -> QuoteService:
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    @property
    def memory_store(self) -> MemoryStore:
        if not self._memory_store:
            self._memory_store = MemoryStore()
        return self._memory_store

    @property
    def feedback_learner(self) -> FeedbackLearner:
        if not self._feedback_learner:
            self._feedback_learner = FeedbackLearner()
        return self._feedback_learner

    async def analyze(
        self,
        code: str,
        days: int = 100,
        include_context: bool = True,
    ) -> FullAnalysisResult:
        """执行技术分析，输出原始数据 + 上下文

        Args:
            code: 股票代码
            days: 分析天数
            include_context: 是否包含历史和反馈上下文

        Returns:
            原始数据 + 上下文
        """
        try:
            # 获取历史数据
            df = await self.quote_service.get_daily(code, limit=days)

            if df.empty:
                return FullAnalysisResult(
                    code=code,
                    error="无数据",
                    days=days,
                )

            # 计算技术指标
            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            df_with_indicators = analyzer.df

            # 获取最新和前一日数据
            latest = df_with_indicators.iloc[-1]
            prev = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest

            # 转换为字典
            latest_dict = self._series_to_dict(latest)
            prev_dict = self._series_to_dict(prev)

            # 检测信号
            signals = detect_signals(latest_dict, prev_dict)

            # 计算信号统计
            signal_stats = calculate_statistics(signals)

            # 获取股票名称
            name = None
            try:
                stock_info = await self.quote_service.get_stock_info(code)
                name = stock_info.get("name") if stock_info else None
            except Exception:
                pass

            # 获取实时行情
            quote = {}
            try:
                quote = await self.quote_service.get_realtime(code)
            except Exception:
                pass

            # 获取上下文
            history = {}
            feedback_stats = {}

            if include_context:
                # 获取历史分析记录
                try:
                    history_entries = await self.memory_store.recall(
                        agent_name="technical-analyst",
                        user_id="default",
                        key=f"analysis:{code}",
                        limit=5,
                    )
                    if history_entries:
                        history["recent_analyses"] = [
                            {
                                "date": e.get("created_at", "")[:10],
                                "signals": e.get("value", {}).get("signals", []),
                            }
                            for e in history_entries
                        ]
                except Exception:
                    pass

                # 获取信号反馈统计
                try:
                    feedback_summary = await self.feedback_learner.get_feedback_summary()
                    if feedback_summary.get("total", 0) > 0:
                        feedback_stats["overall"] = {
                            "total": feedback_summary.get("total"),
                            "success_rate": feedback_summary.get("success_rate"),
                        }

                    # 各信号的成功率
                    signal_perf = feedback_summary.get("signal_performance", {})
                    if signal_perf:
                        feedback_stats["signals"] = signal_perf
                except Exception:
                    pass

            # 存储本次分析
            try:
                await self.memory_store.store(
                    agent_name="technical-analyst",
                    session_id=datetime.now().strftime("%Y%m%d"),
                    user_id="default",
                    key=f"analysis:{code}",
                    value={
                        "signals": [s["type"] for s in signals],
                        "signal_stats": signal_stats,
                        "indicators": latest_dict,
                    },
                )
            except Exception:
                pass

            return FullAnalysisResult(
                code=code,
                name=name,
                indicators=latest_dict,
                prev_indicators=prev_dict,
                signals=signals,
                signal_stats=signal_stats,
                history=history,
                feedback_stats=feedback_stats,
                quote=quote,
                days=days,
            )

        except Exception as e:
            return FullAnalysisResult(
                code=code,
                error=str(e),
                days=days,
            )

    def _series_to_dict(self, series) -> dict[str, Any]:
        """将 pandas Series 转换为字典，处理 NaN 和特殊类型"""
        import math
        import numpy as np
        from datetime import date, datetime

        result = {}
        for key, value in series.items():
            if isinstance(value, float):
                if math.isnan(value) or np.isinf(value):
                    result[key] = None
                else:
                    result[key] = float(value)
            elif isinstance(value, (np.integer, np.floating)):
                if np.isinf(value):
                    result[key] = None
                else:
                    result[key] = float(value) if isinstance(value, np.floating) else int(value)
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, str):
                result[key] = value
            else:
                try:
                    # 尝试转换为字符串
                    result[key] = str(value)
                except Exception:
                    result[key] = None
        return result

    def _clean_for_json(self, obj: Any) -> Any:
        """清理数据使其可 JSON 序列化"""
        import math
        import numpy as np
        from datetime import date, datetime

        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        elif isinstance(obj, (np.integer, np.floating)):
            if np.isinf(obj):
                return None
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def to_dict(self, result: FullAnalysisResult) -> dict[str, Any]:
        """转换为可序列化字典"""
        raw = {
            "code": result.code,
            "name": result.name,
            "indicators": result.indicators,
            "prev_indicators": result.prev_indicators,
            "signals": result.signals,
            "signal_stats": result.signal_stats,
            "history": result.history,
            "feedback_stats": result.feedback_stats,
            "quote": result.quote,
            "analyzed_at": result.analyzed_at.isoformat(),
            "days": result.days,
            "error": result.error,
        }
        return self._clean_for_json(raw)