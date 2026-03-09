"""信号扫描器"""

from datetime import datetime
from typing import Optional, Any

import pandas as pd

from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer


class SignalScanner:
    """技术信号扫描器"""

    def __init__(self, quote_service: QuoteService):
        """
        Args:
            quote_service: 行情服务实例
        """
        self.quote_service = quote_service

    async def scan_stock(self, code: str) -> dict[str, Any]:
        """扫描单只股票的技术信号

        Args:
            code: 股票代码

        Returns:
            扫描结果，包含信号列表和级别
        """
        try:
            # 获取日线数据
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty or len(df) < 30:
                return {
                    "code": code,
                    "signals": [],
                    "level": 0,
                    "error": "数据不足"
                }

            # 计算技术指标
            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()

            # 获取信号
            result = analyzer.get_signals()
            signals = result.get("signals", [])

            # 判断信号级别
            level = self._get_signal_level(signals)

            return {
                "code": code,
                "signals": signals,
                "level": level,
                "latest": result.get("latest", {}),
                "scanned_at": datetime.now()
            }

        except Exception as e:
            return {
                "code": code,
                "signals": [],
                "level": 0,
                "error": str(e)
            }

    async def scan_all(self, codes: list[str]) -> list[dict[str, Any]]:
        """扫描多只股票

        Args:
            codes: 股票代码列表

        Returns:
            扫描结果列表
        """
        results = []
        for code in codes:
            result = await self.scan_stock(code)
            results.append(result)
        return results

    def _get_signal_level(self, signals: list[dict[str, Any]]) -> int:
        """判断信号级别

        信号级别规则：
        - 1 (紧急): 出现多个强烈买入/卖出信号
        - 2 (重要): 出现金叉/死叉等趋势信号
        - 3 (一般): 超买超卖等参考信号

        Args:
            signals: 信号列表

        Returns:
            信号级别 (1=紧急, 2=重要, 3=一般, 0=无信号)
        """
        if not signals:
            return 0

        # 按信号类型分组
        bullish_signals = [s for s in signals if s.get("bias") == "bullish"]
        bearish_signals = [s for s in signals if s.get("bias") == "bearish"]

        # 紧急级别：同时出现多个同向信号
        if len(bullish_signals) >= 2 or len(bearish_signals) >= 2:
            return 1

        # 重要级别：出现交叉信号
        cross_signals = [
            s for s in signals
            if "cross" in s.get("type", "")
        ]
        if cross_signals:
            return 2

        # 一般级别：其他信号
        return 3
