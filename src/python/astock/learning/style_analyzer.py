"""交易风格分析器

基于用户历史交易数据分析交易风格和风险偏好。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from astock.config import ConfigManager, RiskLevel, TradingStyle


@dataclass
class StyleAnalysis:
    """风格分析结果"""

    user_id: str

    # 交易频率分析
    trade_frequency: float = 0.0  # 月均交易次数
    avg_holding_days: float = 0.0  # 平均持仓天数
    total_trades: int = 0  # 总交易次数

    # 盈亏分析
    win_rate: float = 0.0  # 胜率
    profit_loss_ratio: float = 0.0  # 盈亏比
    total_profit: float = 0.0  # 总盈亏

    # 推断结果
    trading_style: TradingStyle = TradingStyle.SWING
    risk_level: RiskLevel = RiskLevel.MODERATE

    # 分析时间
    analyzed_at: datetime = field(default_factory=datetime.now)

    # 行业偏好
    preferred_sectors: list[str] = field(default_factory=list)

    # 置信度
    confidence: float = 0.0  # 分析置信度 (0-1)


class StyleAnalyzer:
    """交易风格分析器

    分析用户历史交易数据，推断交易风格和风险偏好。
    """

    def __init__(self, data_source: Optional[object] = None):
        """初始化风格分析器

        Args:
            data_source: 数据源，用于获取交易记录
        """
        self.data_source = data_source
        self.min_trades_for_analysis = 5  # 最少交易次数要求

    def analyze(self, user_id: str) -> StyleAnalysis:
        """分析用户交易风格

        Args:
            user_id: 用户ID

        Returns:
            风格分析结果
        """
        # 获取用户交易数据
        df = self._get_trade_data(user_id)

        if df is None or len(df) < self.min_trades_for_analysis:
            # 数据不足，返回默认值
            return StyleAnalysis(
                user_id=user_id,
                confidence=0.0,
            )

        # 计算交易频率
        frequency = self._calculate_trade_frequency(df)

        # 计算持仓天数
        holding_days = self._estimate_holding_days(df)

        # 计算盈亏数据
        win_rate, profit_loss_ratio, total_profit = self._calculate_profit_metrics(df)

        # 推断交易风格
        trading_style = self._infer_trading_style(frequency, holding_days)

        # 推断风险偏好
        risk_level = self._infer_risk_level(frequency, win_rate)

        # 分析行业偏好
        preferred_sectors = self._analyze_sector_preference(df)

        # 计算置信度
        confidence = self._calculate_confidence(df)

        return StyleAnalysis(
            user_id=user_id,
            trade_frequency=frequency,
            avg_holding_days=holding_days,
            total_trades=len(df),
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            total_profit=total_profit,
            trading_style=trading_style,
            risk_level=risk_level,
            preferred_sectors=preferred_sectors,
            confidence=confidence,
        )

    def _get_trade_data(self, user_id: str) -> Optional[pd.DataFrame]:
        """获取用户交易数据

        Args:
            user_id: 用户ID

        Returns:
            交易数据 DataFrame，包含列:
            - code: 股票代码
            - direction: 买卖方向 (buy/sell)
            - price: 成交价格
            - quantity: 成交数量
            - traded_at: 交易时间
            - sector: 行业 (可选)
        """
        if self.data_source is not None:
            # 使用数据源获取数据
            if hasattr(self.data_source, "get_trades"):
                trades = self.data_source.get_trades(user_id)
                if trades:
                    return pd.DataFrame([t.model_dump() for t in trades])

        # 尝试从数据库获取
        try:
            from astock.storage.database import Database

            db = Database()
            trades = db.get_trades(user_id)
            if trades:
                return pd.DataFrame([t.model_dump() for t in trades])
        except Exception:
            pass

        # 返回空 DataFrame 用于测试
        return pd.DataFrame()

    def _calculate_trade_frequency(self, df: pd.DataFrame) -> float:
        """计算交易频率 (月均交易次数)

        Args:
            df: 交易数据 DataFrame

        Returns:
            月均交易次数
        """
        if len(df) == 0:
            return 0.0

        # 确保 traded_at 是 datetime 类型
        if "traded_at" not in df.columns:
            return 0.0

        df = df.copy()
        df["traded_at"] = pd.to_datetime(df["traded_at"])

        # 计算时间跨度
        min_date = df["traded_at"].min()
        max_date = df["traded_at"].max()

        if pd.isna(min_date) or pd.isna(max_date):
            return 0.0

        days = (max_date - min_date).days
        if days == 0:
            # 单日交易
            return len(df)

        months = days / 30.0
        return round(len(df) / months, 2)

    def _estimate_holding_days(self, df: pd.DataFrame) -> float:
        """估算平均持仓天数

        通过配对买卖记录估算持仓时间。

        Args:
            df: 交易数据 DataFrame

        Returns:
            平均持仓天数
        """
        if len(df) == 0:
            return 0.0

        required_cols = ["code", "direction", "traded_at"]
        if not all(col in df.columns for col in required_cols):
            return 0.0

        df = df.copy()
        df["traded_at"] = pd.to_datetime(df["traded_at"])
        df = df.sort_values("traded_at")

        holding_days_list = []

        # 按 code 分组，配对买卖记录
        for code, group in df.groupby("code"):
            buys = group[group["direction"] == "buy"].copy()
            sells = group[group["direction"] == "sell"].copy()

            if len(buys) == 0 or len(sells) == 0:
                continue

            # 简单 FIFO 配对
            for _, sell in sells.iterrows():
                # 找到最近的买入记录
                buy = buys[buys["traded_at"] < sell["traded_at"]]
                if len(buy) > 0:
                    buy_date = buy.iloc[-1]["traded_at"]
                    sell_date = sell["traded_at"]
                    days = (sell_date - buy_date).days
                    if days >= 0:
                        holding_days_list.append(days)

        if len(holding_days_list) == 0:
            return 0.0

        return round(sum(holding_days_list) / len(holding_days_list), 1)

    def _calculate_profit_metrics(
        self, df: pd.DataFrame
    ) -> tuple[float, float, float]:
        """计算盈亏指标

        Args:
            df: 交易数据 DataFrame

        Returns:
            (胜率, 盈亏比, 总盈亏)
        """
        if len(df) == 0:
            return 0.0, 0.0, 0.0

        required_cols = ["code", "direction", "price", "quantity", "traded_at"]
        if not all(col in df.columns for col in required_cols):
            return 0.0, 0.0, 0.0

        df = df.copy()
        df["traded_at"] = pd.to_datetime(df["traded_at"])
        df = df.sort_values("traded_at")

        profits = []

        # 按 code 分组计算盈亏
        for code, group in df.groupby("code"):
            buys = group[group["direction"] == "buy"].copy()
            sells = group[group["direction"] == "sell"].copy()

            if len(buys) == 0 or len(sells) == 0:
                continue

            # 简单 FIFO 配对计算盈亏
            buy_queue = []
            for _, trade in group.iterrows():
                if trade["direction"] == "buy":
                    buy_queue.append((trade["price"], trade["quantity"]))
                elif trade["direction"] == "sell" and len(buy_queue) > 0:
                    sell_price = trade["price"]
                    sell_qty = trade["quantity"]

                    remaining_qty = sell_qty
                    cost = 0.0

                    while remaining_qty > 0 and len(buy_queue) > 0:
                        buy_price, buy_qty = buy_queue[0]
                        matched_qty = min(remaining_qty, buy_qty)
                        cost += buy_price * matched_qty
                        remaining_qty -= matched_qty

                        if matched_qty >= buy_qty:
                            buy_queue.pop(0)
                        else:
                            buy_queue[0] = (buy_price, buy_qty - matched_qty)

                    if cost > 0:
                        profit = (sell_price * sell_qty) - cost
                        profits.append(profit)

        if len(profits) == 0:
            return 0.0, 0.0, 0.0

        # 计算胜率
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        win_rate = len(wins) / len(profits) if profits else 0.0

        # 计算盈亏比
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 1.0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        # 总盈亏
        total_profit = sum(profits)

        return round(win_rate, 2), round(profit_loss_ratio, 2), round(total_profit, 2)

    def _infer_trading_style(
        self, frequency: float, holding_days: float
    ) -> TradingStyle:
        """推断交易风格

        Args:
            frequency: 月均交易次数
            holding_days: 平均持仓天数

        Returns:
            交易风格
        """
        # 日内交易: 高频 + 短持仓
        if frequency > 20 and holding_days <= 1:
            return TradingStyle.DAY_TRADING

        # 波段交易: 中频 + 中等持仓
        if frequency >= 5 and holding_days <= 30:
            return TradingStyle.SWING

        # 趋势跟踪: 中低频 + 较长持仓
        if frequency >= 2 and holding_days <= 90:
            return TradingStyle.TREND_FOLLOWING

        # 价值投资: 低频 + 长期持仓
        return TradingStyle.VALUE_INVESTING

    def _infer_risk_level(self, frequency: float, win_rate: float) -> RiskLevel:
        """推断风险偏好

        Args:
            frequency: 月均交易次数
            win_rate: 胜率

        Returns:
            风险等级
        """
        # 激进型: 高频交易 或 胜率较低但仍在交易
        if frequency > 15 or (frequency > 5 and win_rate < 0.4):
            return RiskLevel.AGGRESSIVE

        # 保守型: 低频 且 高胜率
        if frequency < 5 and win_rate > 0.6:
            return RiskLevel.CONSERVATIVE

        # 稳健型
        return RiskLevel.MODERATE

    def _analyze_sector_preference(self, df: pd.DataFrame) -> list[str]:
        """分析行业偏好

        Args:
            df: 交易数据 DataFrame

        Returns:
            偏好行业列表
        """
        if len(df) == 0 or "sector" not in df.columns:
            return []

        # 统计各行业交易次数
        sector_counts = df["sector"].value_counts()

        # 返回交易次数最多的前 3 个行业
        return list(sector_counts.head(3).index)

    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """计算分析置信度

        数据越多，置信度越高。

        Args:
            df: 交易数据 DataFrame

        Returns:
            置信度 (0-1)
        """
        trade_count = len(df)

        if trade_count < self.min_trades_for_analysis:
            return 0.0

        # 基础置信度
        confidence = min(1.0, trade_count / 50.0)

        # 时间跨度加成
        if "traded_at" in df.columns:
            df = df.copy()
            df["traded_at"] = pd.to_datetime(df["traded_at"])
            days = (df["traded_at"].max() - df["traded_at"].min()).days

            # 跨度 3 个月以上加成
            if days > 90:
                confidence = min(1.0, confidence * 1.2)
            elif days > 30:
                confidence = min(1.0, confidence * 1.1)

        return round(confidence, 2)

    def update_user_config(
        self, user_id: str, config_manager: Optional[ConfigManager] = None
    ) -> StyleAnalysis:
        """分析并更新用户配置

        根据交易风格分析结果更新用户配置。

        Args:
            user_id: 用户ID
            config_manager: 配置管理器，如果为 None 则创建新的

        Returns:
            风格分析结果
        """
        if config_manager is None:
            config_manager = ConfigManager()

        # 分析交易风格
        analysis = self.analyze(user_id)

        # 仅在有足够数据时更新配置
        if analysis.confidence > 0.5:
            config_manager.update(
                user_id,
                trading_style=analysis.trading_style,
                risk_level=analysis.risk_level,
                preferred_sectors=analysis.preferred_sectors,
            )

        return analysis
