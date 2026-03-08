"""回测引擎"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

from .strategies import Signal, Strategy, Trade, get_strategy


@dataclass
class BacktestResult:
    """回测结果"""
    code: str
    strategy: str
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float  # 总收益率
    annual_return: float  # 年化收益
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    win_rate: float  # 胜率
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "strategy": self.strategy,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": self.equity_curve,
        }


class BacktestEngine:
    """回测引擎"""

    def __init__(self):
        self.position = 0  # 当前持仓数量
        self.capital = 0.0  # 当前资金
        self.trades: list[Trade] = []
        self.equity_curve: list[dict] = []

    def run(
        self,
        df: pd.DataFrame,
        strategy_name: str,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        strategy_params: Optional[dict] = None,
    ) -> BacktestResult:
        """运行回测

        Args:
            df: 包含 OHLCV 数据的 DataFrame，需要有 date, open, high, low, close, volume 列
            strategy_name: 策略名称
            initial_capital: 初始资金
            commission_rate: 手续费率
            strategy_params: 策略参数

        Returns:
            回测结果
        """
        # 重置状态
        self.position = 0
        self.capital = initial_capital
        self.trades = []
        self.equity_curve = []

        # 获取策略
        params = strategy_params or {}
        strategy = get_strategy(strategy_name, **params)

        # 生成信号
        df = strategy.generate_signals(df)

        # 确保 date 列存在且格式正确
        if "date" not in df.columns:
            df["date"] = df.index

        # 按日期遍历执行交易
        for i, row in df.iterrows():
            current_date = row["date"]
            if isinstance(current_date, str):
                current_date = date.fromisoformat(current_date)
            signal = row.get("signal", Signal.HOLD)
            close_price = row["close"]

            # 执行交易
            if signal == Signal.BUY and self.position == 0:
                # 全仓买入
                shares = int(self.capital / close_price / 100) * 100  # A股一手100股
                if shares > 0:
                    trade_value = shares * close_price
                    commission = trade_value * commission_rate
                    self.capital -= (trade_value + commission)
                    self.position = shares

                    self.trades.append(Trade(
                        date=current_date,
                        signal=Signal.BUY,
                        price=close_price,
                        shares=shares,
                        value=trade_value,
                        commission=commission,
                    ))

            elif signal == Signal.SELL and self.position > 0:
                # 全仓卖出
                trade_value = self.position * close_price
                commission = trade_value * commission_rate
                self.capital += (trade_value - commission)

                self.trades.append(Trade(
                    date=current_date,
                    signal=Signal.SELL,
                    price=close_price,
                    shares=self.position,
                    value=trade_value,
                    commission=commission,
                ))

                self.position = 0

            # 记录权益曲线
            equity = self.capital + self.position * close_price
            self.equity_curve.append({
                "date": current_date.isoformat() if isinstance(current_date, date) else current_date,
                "equity": equity,
                "cash": self.capital,
                "position": self.position,
                "price": close_price,
            })

        # 计算最终权益
        final_price = df.iloc[-1]["close"]
        final_capital = self.capital + self.position * final_price

        # 如果最后还持仓，添加一个虚拟卖出用于计算
        if self.position > 0:
            self.trades.append(Trade(
                date=current_date,
                signal=Signal.SELL,
                price=final_price,
                shares=self.position,
                value=self.position * final_price,
                commission=0,
            ))

        # 计算回测指标
        result = BacktestResult(
            code="",  # 由调用者设置
            strategy=strategy_name,
            start_date=self._get_start_date(df),
            end_date=self._get_end_date(df),
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=self._calc_total_return(initial_capital, final_capital),
            annual_return=self._calc_annual_return(initial_capital, final_capital, df),
            max_drawdown=self._calc_max_drawdown(),
            sharpe_ratio=self._calc_sharpe_ratio(),
            win_rate=self._calc_win_rate(),
            trades=self.trades[:-1] if self.position > 0 else self.trades,  # 排除虚拟卖出
            equity_curve=self.equity_curve,
        )

        return result

    def _get_start_date(self, df: pd.DataFrame) -> date:
        """获取开始日期"""
        d = df.iloc[0]["date"]
        if isinstance(d, str):
            return date.fromisoformat(d)
        return d

    def _get_end_date(self, df: pd.DataFrame) -> date:
        """获取结束日期"""
        d = df.iloc[-1]["date"]
        if isinstance(d, str):
            return date.fromisoformat(d)
        return d

    def _calc_total_return(self, initial: float, final: float) -> float:
        """计算总收益率"""
        return (final - initial) / initial * 100

    def _calc_annual_return(
        self,
        initial: float,
        final: float,
        df: pd.DataFrame
    ) -> float:
        """计算年化收益率"""
        start = self._get_start_date(df)
        end = self._get_end_date(df)
        days = (end - start).days

        if days <= 0:
            return 0.0

        years = days / 365.0
        if years <= 0:
            return 0.0

        # 年化收益率 = (最终价值 / 初始价值)^(1/年数) - 1
        annual_return = (final / initial) ** (1 / years) - 1
        return annual_return * 100

    def _calc_max_drawdown(self) -> float:
        """计算最大回撤"""
        if not self.equity_curve:
            return 0.0

        equities = [e["equity"] for e in self.equity_curve]
        peak = equities[0]
        max_dd = 0.0

        for equity in equities:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calc_sharpe_ratio(self) -> float:
        """计算夏普比率"""
        if len(self.equity_curve) < 2:
            return 0.0

        equities = [e["equity"] for e in self.equity_curve]
        returns = []

        for i in range(1, len(equities)):
            if equities[i-1] > 0:
                r = (equities[i] - equities[i-1]) / equities[i-1]
                returns.append(r)

        if not returns:
            return 0.0

        returns = np.array(returns)
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # 年化夏普比率（假设每年252个交易日）
        risk_free_rate = 0.03 / 252  # 年化无风险利率约3%
        sharpe = (mean_return - risk_free_rate) / std_return * np.sqrt(252)

        return sharpe

    def _calc_win_rate(self) -> float:
        """计算胜率"""
        # 配对买卖交易
        buy_sell_pairs = []
        buy_trade = None

        for trade in self.trades:
            if trade.signal == Signal.BUY:
                buy_trade = trade
            elif trade.signal == Signal.SELL and buy_trade is not None:
                buy_sell_pairs.append((buy_trade, trade))
                buy_trade = None

        if not buy_sell_pairs:
            return 0.0

        wins = sum(1 for buy, sell in buy_sell_pairs if sell.price > buy.price)
        return wins / len(buy_sell_pairs) * 100
