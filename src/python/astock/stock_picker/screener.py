"""选股器 - 支持并行处理和错误处理"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import asyncio
import pandas as pd
import numpy as np

from .factors import Factor, FactorType, FACTORS, get_factor
from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer
from ..utils import get_logger, DataSourceError, ValidationError

logger = get_logger("screener")


@dataclass
class ScreenResult:
    """选股结果"""

    code: str  # 股票代码
    name: Optional[str]  # 股票名称
    score: float  # 综合得分
    matched_factors: list[str]  # 匹配的因子列表
    factor_scores: dict[str, float]  # 各因子得分
    data: dict[str, Any]  # 原始数据
    screened_at: datetime  # 选股时间


class StockScreener:
    """股票选股器 - 支持并行处理"""

    def __init__(self, quote_service: QuoteService, max_concurrent: int = 10):
        """
        Args:
            quote_service: 行情服务实例
            max_concurrent: 最大并发数
        """
        self.quote_service = quote_service
        self.max_concurrent = max_concurrent
        logger.debug(f"选股器初始化完成，最大并发数: {max_concurrent}")

    async def screen(
        self,
        factors: Optional[list[str]] = None,
        codes: Optional[list[str]] = None,
        limit: int = 50,
        min_score: float = 0.0,
    ) -> list[ScreenResult]:
        """执行选股（并行处理）

        Args:
            factors: 因子键名列表，为空则使用所有因子
            codes: 股票代码列表，为空则使用全部A股
            limit: 返回数量限制
            min_score: 最低得分阈值

        Returns:
            选股结果列表，按得分降序排列
        """
        # 获取因子列表
        factor_list = self._get_factor_list(factors)

        if not factor_list:
            logger.warning("没有可用的因子")
            return []

        # 获取股票列表
        stock_codes = codes or await self._get_all_codes()
        logger.info(
            f"开始选股，股票数量: {len(stock_codes)}, 因子数量: {len(factor_list)}"
        )

        # 并行执行选股
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def limited_screen(code: str) -> Optional[ScreenResult]:
            async with semaphore:
                return await self._screen_stock(code, factor_list)

        tasks = [limited_screen(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤有效结果
        valid_results = [
            r for r in results if isinstance(r, ScreenResult) and r.score >= min_score
        ]

        # 记录错误
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.warning(f"选股过程中有 {len(errors)} 个错误")

        # 按得分排序
        valid_results.sort(key=lambda x: x.score, reverse=True)

        logger.info(f"选股完成，有效结果: {len(valid_results)}")
        return valid_results[:limit]

    async def _screen_stock(
        self, code: str, factors: list[Factor]
    ) -> Optional[ScreenResult]:
        """对单只股票执行选股

        Args:
            code: 股票代码
            factors: 因子列表

        Returns:
            选股结果
        """
        try:
            # 获取股票数据
            data = await self._get_stock_data(code)

            if not data:
                return None

            # 计算匹配的因子和得分
            matched_factors = self._get_matched_factors(data, factors)
            factor_scores = self._calculate_factor_scores(data, factors)
            score = sum(factor_scores.values())

            return ScreenResult(
                code=code,
                name=data.get("name"),
                score=score,
                matched_factors=matched_factors,
                factor_scores=factor_scores,
                data=data,
                screened_at=datetime.now(),
            )

        except DataSourceError as e:
            logger.debug(f"获取 {code} 数据失败: {e}")
            return None
        except Exception as e:
            logger.debug(f"选股 {code} 失败: {e}")
            return None

    async def _get_stock_data(self, code: str) -> Optional[dict[str, Any]]:
        """获取股票数据

        Args:
            code: 股票代码

        Returns:
            股票数据字典
        """
        try:
            # 获取日线数据
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty or len(df) < 30:
                logger.debug(f"股票 {code} 数据不足")
                return None

            # 计算技术指标
            analyzer = TechnicalAnalyzer(df)
            df_with_indicators = analyzer.add_all()

            # 获取最新数据
            latest = df_with_indicators.iloc[-1]
            prev = (
                df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest
            )

            # 计算额外指标
            vol_ma5 = df_with_indicators["volume"].rolling(5).mean().iloc[-1]
            volatility_20 = (
                df_with_indicators["close"].pct_change().rolling(20).std().iloc[-1]
            )

            # 获取实时行情中的 PE、PB
            realtime = await self.quote_service.get_realtime(code)

            return {
                "code": code,
                "name": realtime.get("name", ""),
                "close": float(latest["close"]),
                "open": float(latest["open"]),
                "high": float(latest["high"]),
                "low": float(latest["low"]),
                "volume": float(latest["volume"]),
                "amount": float(latest["amount"]) if "amount" in latest else 0,
                "pe": float(realtime.get("pe", 0)) if realtime.get("pe") else None,
                "pb": float(realtime.get("pb", 0)) if realtime.get("pb") else None,
                "ma5": float(latest.get("ma5", 0)),
                "ma10": float(latest.get("ma10", 0)),
                "ma20": float(latest.get("ma20", 0)),
                "ma60": float(latest.get("ma60", 0)),
                "macd": float(latest.get("macd", 0)),
                "macd_signal": float(latest.get("macd_signal", 0)),
                "macd_hist": float(latest.get("macd_hist", 0)),
                "kdj_k": float(latest.get("kdj_k", 0)),
                "kdj_d": float(latest.get("kdj_d", 0)),
                "kdj_j": float(latest.get("kdj_j", 0)),
                "rsi6": float(latest.get("rsi6", 0)),
                "prev_ma5": float(prev.get("ma5", 0)),
                "prev_ma20": float(prev.get("ma20", 0)),
                "vol_ma5": float(vol_ma5),
                "vol_ma5_2x": float(vol_ma5 * 2),
                "volatility_20": float(volatility_20),
            }

        except Exception as e:
            logger.debug(f"获取 {code} 数据失败: {e}")
            return None

    def _calculate_factor_scores(
        self, data: dict[str, Any], factors: list[Factor]
    ) -> dict[str, float]:
        """计算因子得分"""
        scores = {}

        for factor in factors:
            if self._check_condition(data, factor):
                scores[factor.key] = factor.weight
            else:
                scores[factor.key] = 0.0

        return scores

    def _check_condition(self, data: dict[str, Any], factor: Factor) -> bool:
        """检查条件是否满足"""
        # 获取字段值
        value = data.get(factor.field)
        if value is None:
            return False

        # 获取阈值
        threshold = factor.threshold

        # 如果阈值是字符串，说明是引用其他字段
        if isinstance(threshold, str):
            threshold = data.get(threshold)
            if threshold is None:
                return False

        # 处理特殊操作符
        if factor.operator == "cross_up":
            prev_value = data.get(f"prev_{factor.field}")
            prev_threshold_key = (
                f"prev_{factor.threshold}"
                if isinstance(factor.threshold, str)
                else None
            )
            prev_threshold = (
                data.get(prev_threshold_key) if prev_threshold_key else threshold
            )

            if prev_value is None or prev_threshold is None:
                return False

            return bool(value > threshold and prev_value <= prev_threshold)

        if factor.operator == "cross_down":
            prev_value = data.get(f"prev_{factor.field}")
            prev_threshold_key = (
                f"prev_{factor.threshold}"
                if isinstance(factor.threshold, str)
                else None
            )
            prev_threshold = (
                data.get(prev_threshold_key) if prev_threshold_key else threshold
            )

            if prev_value is None or prev_threshold is None:
                return False

            return bool(value < threshold and prev_value >= prev_threshold)

        # 处理常规操作符
        return self._compare_values(value, factor.operator, threshold)

    def _compare_values(self, value: Any, operator: str, threshold: Any) -> bool:
        """比较值"""
        try:
            if operator == "lt":
                return bool(value < threshold)
            elif operator == "le":
                return bool(value <= threshold)
            elif operator == "gt":
                return bool(value > threshold)
            elif operator == "ge":
                return bool(value >= threshold)
            elif operator == "eq":
                return bool(value == threshold)
            else:
                return False
        except (TypeError, ValueError):
            return False

    def _get_matched_factors(
        self, data: dict[str, Any], factors: list[Factor]
    ) -> list[str]:
        """获取匹配的因子列表"""
        return [factor.key for factor in factors if self._check_condition(data, factor)]

    def _get_factor_list(self, factor_keys: Optional[list[str]]) -> list[Factor]:
        """获取因子列表"""
        if not factor_keys:
            return list(FACTORS.values())

        factors = []
        for key in factor_keys:
            factor = get_factor(key)
            if factor:
                factors.append(factor)

        return factors

    async def _get_all_codes(self) -> list[str]:
        """获取所有A股代码"""
        try:
            df = await self.quote_service.client.get_stock_list()
            codes = [str(code) for code in df["code"].tolist()]
            # 限制前500只用于性能
            return codes[:500] if len(codes) > 500 else codes
        except Exception as e:
            logger.warning(f"获取股票列表失败: {e}，使用默认列表")
            return ["000001", "000002", "600000", "600036", "600519"]
