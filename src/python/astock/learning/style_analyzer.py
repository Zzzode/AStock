"""Trading style analyzer

Analyzes trading style and risk preferences based on user historical trading data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from astock.config import ConfigManager, RiskLevel, TradingStyle


@dataclass
class StyleAnalysis:
    """Style analysis result"""

    user_id: str

    # Trade frequency analysis
    trade_frequency: float = 0.0  # Average monthly trades
    avg_holding_days: float = 0.0  # Average holding period in days
    total_trades: int = 0  # Total number of trades

    # Profit/loss analysis
    win_rate: float = 0.0  # Win rate
    profit_loss_ratio: float = 0.0  # Profit/loss ratio
    total_profit: float = 0.0  # Total profit/loss

    # Inferred results
    trading_style: TradingStyle = TradingStyle.SWING
    risk_level: RiskLevel = RiskLevel.MODERATE

    # Analysis timestamp
    analyzed_at: datetime = field(default_factory=datetime.now)

    # Sector preferences
    preferred_sectors: list[str] = field(default_factory=list)

    # Confidence
    confidence: float = 0.0  # Analysis confidence (0-1)


class StyleAnalyzer:
    """Trading style analyzer

    Analyzes user historical trading data to infer trading style and risk preferences.
    """

    def __init__(self, data_source: Optional[object] = None):
        """Initialize style analyzer

        Args:
            data_source: Data source for fetching trade records
        """
        self.data_source = data_source
        self.min_trades_for_analysis = 5  # Minimum trade count required

    def analyze(self, user_id: str) -> StyleAnalysis:
        """Analyze user trading style

        Args:
            user_id: User ID

        Returns:
            Style analysis result
        """
        # Get user trade data
        df = self._get_trade_data(user_id)

        if df is None or len(df) < self.min_trades_for_analysis:
            # Insufficient data, return defaults
            return StyleAnalysis(
                user_id=user_id,
                confidence=0.0,
            )

        # Calculate trade frequency
        frequency = self._calculate_trade_frequency(df)

        # Calculate holding days
        holding_days = self._estimate_holding_days(df)

        # Calculate profit/loss metrics
        win_rate, profit_loss_ratio, total_profit = self._calculate_profit_metrics(df)

        # Infer trading style
        trading_style = self._infer_trading_style(frequency, holding_days)

        # Infer risk preference
        risk_level = self._infer_risk_level(frequency, win_rate)

        # Analyze sector preference
        preferred_sectors = self._analyze_sector_preference(df)

        # Calculate confidence
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
        """Get user trade data

        Args:
            user_id: User ID

        Returns:
            Trade data DataFrame with columns:
            - code: Stock code
            - direction: Trade direction (buy/sell)
            - price: Execution price
            - quantity: Execution quantity
            - traded_at: Trade timestamp
            - sector: Industry sector (optional)
        """
        if self.data_source is not None:
            # Use data source to get data
            if hasattr(self.data_source, "get_trades"):
                trades = self.data_source.get_trades(user_id)
                if trades:
                    return pd.DataFrame([t.model_dump() for t in trades])

        # Try to fetch from database
        try:
            from astock.storage.database import Database

            db = Database()
            trades = db.get_trades(user_id)
            if trades:
                return pd.DataFrame([t.model_dump() for t in trades])
        except Exception:
            pass

        # Return empty DataFrame for testing
        return pd.DataFrame()

    def _calculate_trade_frequency(self, df: pd.DataFrame) -> float:
        """Calculate trade frequency (average monthly trades)

        Args:
            df: Trade data DataFrame

        Returns:
            Average monthly trade count
        """
        if len(df) == 0:
            return 0.0

        # Ensure traded_at is datetime type
        if "traded_at" not in df.columns:
            return 0.0

        df = df.copy()
        df["traded_at"] = pd.to_datetime(df["traded_at"])

        # Calculate time span
        min_date = df["traded_at"].min()
        max_date = df["traded_at"].max()

        if pd.isna(min_date) or pd.isna(max_date):
            return 0.0

        days = (max_date - min_date).days
        if days == 0:
            # Single day trading
            return float(len(df))

        months = days / 30.0
        return float(round(len(df) / months, 2))

    def _estimate_holding_days(self, df: pd.DataFrame) -> float:
        """Estimate average holding days

        Estimates holding period by matching buy/sell records.

        Args:
            df: Trade data DataFrame

        Returns:
            Average holding days
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

        # Group by code, match buy/sell records
        for code, group in df.groupby("code"):
            buys = group[group["direction"] == "buy"].copy()
            sells = group[group["direction"] == "sell"].copy()

            if len(buys) == 0 or len(sells) == 0:
                continue

            # Simple FIFO matching
            for _, sell in sells.iterrows():
                # Find the most recent buy record
                buy = buys[buys["traded_at"] < sell["traded_at"]]
                if len(buy) > 0:
                    buy_date = buy.iloc[-1]["traded_at"]
                    sell_date = sell["traded_at"]
                    days = (sell_date - buy_date).days
                    if days >= 0:
                        holding_days_list.append(days)

        if len(holding_days_list) == 0:
            return 0.0

        return float(round(sum(holding_days_list) / len(holding_days_list), 1))

    def _calculate_profit_metrics(
        self, df: pd.DataFrame
    ) -> tuple[float, float, float]:
        """Calculate profit/loss metrics

        Args:
            df: Trade data DataFrame

        Returns:
            (win_rate, profit_loss_ratio, total_profit)
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

        # Group by code to calculate profit/loss
        for code, group in df.groupby("code"):
            buys = group[group["direction"] == "buy"].copy()
            sells = group[group["direction"] == "sell"].copy()

            if len(buys) == 0 or len(sells) == 0:
                continue

            # Simple FIFO matching for profit/loss calculation
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

        # Calculate win rate
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        win_rate = len(wins) / len(profits) if profits else 0.0

        # Calculate profit/loss ratio
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 1.0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        # Total profit/loss
        total_profit = sum(profits)

        return round(win_rate, 2), round(profit_loss_ratio, 2), round(total_profit, 2)

    def _infer_trading_style(
        self, frequency: float, holding_days: float
    ) -> TradingStyle:
        """Infer trading style

        Args:
            frequency: Average monthly trade count
            holding_days: Average holding days

        Returns:
            Trading style
        """
        # Day Trading: high frequency + short holding
        if frequency > 20 and holding_days <= 1:
            return TradingStyle.DAY_TRADING

        # Swing Trading: medium frequency + medium holding
        if frequency >= 5 and holding_days <= 30:
            return TradingStyle.SWING

        # Trend Following: medium-low frequency + longer holding
        if frequency >= 2 and holding_days <= 90:
            return TradingStyle.TREND_FOLLOWING

        # Value Investing: low frequency + long-term holding
        return TradingStyle.VALUE_INVESTING

    def _infer_risk_level(self, frequency: float, win_rate: float) -> RiskLevel:
        """Infer risk preference

        Args:
            frequency: Average monthly trade count
            win_rate: Win rate

        Returns:
            Risk level
        """
        # Aggressive: high-frequency trading or low win rate but still trading
        if frequency > 15 or (frequency > 5 and win_rate < 0.4):
            return RiskLevel.AGGRESSIVE

        # Conservative: low frequency and high win rate
        if frequency < 5 and win_rate > 0.6:
            return RiskLevel.CONSERVATIVE

        # Moderate
        return RiskLevel.MODERATE

    def _analyze_sector_preference(self, df: pd.DataFrame) -> list[str]:
        """Analyze sector preference

        Args:
            df: Trade data DataFrame

        Returns:
            Preferred sector list
        """
        if len(df) == 0 or "sector" not in df.columns:
            return []

        # Count trades per sector
        sector_counts = df["sector"].value_counts()

        # Return top 3 sectors by trade count
        return list(sector_counts.head(3).index)

    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculate analysis confidence

        More data leads to higher confidence.

        Args:
            df: Trade data DataFrame

        Returns:
            Confidence (0-1)
        """
        trade_count = len(df)

        if trade_count < self.min_trades_for_analysis:
            return 0.0

        # Base confidence
        confidence = min(1.0, trade_count / 50.0)

        # Time span bonus
        if "traded_at" in df.columns:
            df = df.copy()
            df["traded_at"] = pd.to_datetime(df["traded_at"])
            days = (df["traded_at"].max() - df["traded_at"].min()).days

            # Bonus for span over 3 months
            if days > 90:
                confidence = min(1.0, confidence * 1.2)
            elif days > 30:
                confidence = min(1.0, confidence * 1.1)

        return round(confidence, 2)

    def update_user_config(
        self, user_id: str, config_manager: Optional[ConfigManager] = None
    ) -> StyleAnalysis:
        """Analyze and update user configuration

        Updates user configuration based on trading style analysis results.

        Args:
            user_id: User ID
            config_manager: Configuration manager, creates a new one if None

        Returns:
            Style analysis result
        """
        if config_manager is None:
            config_manager = ConfigManager()

        # Analyze trading style
        analysis = self.analyze(user_id)

        # Only update config when sufficient data is available
        if analysis.confidence > 0.5:
            config_manager.update(
                user_id,
                trading_style=analysis.trading_style,
                risk_level=analysis.risk_level,
                preferred_sectors=analysis.preferred_sectors,
            )

        return analysis
