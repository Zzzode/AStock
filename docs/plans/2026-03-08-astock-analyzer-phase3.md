# A股交易策略分析工具 - Phase 3 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现智能选股和策略回测功能。

**Architecture:** Python 选股引擎多因子筛选，策略回测引擎，TypeScript CLI 集成。

**Tech Stack:** pandas, numpy, matplotlib (图表)

---

## Task 1: 选股服务核心

**Files:**
- Create: `src/python/astock/stock_picker/__init__.py`
- Create: `src/python/astock/stock_picker/screener.py`
- Create: `src/python/astock/stock_picker/factors.py`

**Step 1: 创建 stock_picker 模块**

```bash
mkdir -p src/python/astock/stock_picker
```

**Step 2: 创建 factors.py - 因子定义**

```python
"""选股因子"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class FactorType(Enum):
    """因子类型"""
    VALUATION = "valuation"  # 估值因子
    MOMENTUM = "momentum"    # 动量因子
    QUALITY = "quality"      # 质量因子
    VOLATILITY = "volatility"  # 波动因子


@dataclass
class Factor:
    """因子定义"""
    name: str
    type: FactorType
    description: str
    field: str  # 数据字段
    operator: str  # >, <, ==, between
    value: any  # 阈值
    weight: float = 1.0  # 权重


# 预定义因子
FACTORS = {
    # 估值因子
    "pe_low": Factor(
        name="pe_low", type=FactorType.VALUATION,
        description="PE估值较低", field="pe_ttm",
        operator="<", value=30, weight=1.0
    ),
    "pb_low": Factor(
        name="pb_low", type=FactorType.VALUATION,
        description="PB估值较低", field="pb",
        operator="<", value=3, weight=0.8
    ),

    # 动量因子
    "ma20_above": Factor(
        name="ma20_above", type=FactorType.MOMENTUM,
        description="站上20日均线", field="close_to_ma20",
        operator=">", value=1.0, weight=1.0
    ),
    "ma5_cross_ma20": Factor(
        name="ma5_cross_ma20", type=FactorType.MOMENTUM,
        description="MA5金叉MA20", field="ma5_ma20_cross",
        operator="==", value=1, weight=1.2
    ),

    # 质量因子
    "high_volume": Factor(
        name="high_volume", type=FactorType.QUALITY,
        description="成交活跃", field="volume_ratio",
        operator=">", value=1.5, weight=0.6
    ),

    # 波动因子
    "low_volatility": Factor(
        name="low_volatility", type=FactorType.VOLATILITY,
        description="波动较小", field="volatility_20",
        operator="<", value=0.03, weight=0.5
    ),
}
```

**Step 3: 创建 screener.py - 选股器**

```python
"""选股服务"""

import asyncio
from typing import Optional
import pandas as pd
from datetime import datetime

from ..storage import Database
from ..quote import QuoteService
from .factors import Factor, FactorType, FACTORS


class StockScreener:
    """选股器"""

    def __init__(self, db: Database):
        self.db = db
        self.quote_service = QuoteService(db)

    async def screen(
        self,
        factors: list[str],
        codes: Optional[list[str]] = None,
        limit: int = 50
    ) -> list[dict]:
        """执行选股

        Args:
            factors: 因子名称列表
            codes: 待筛选股票列表，为空则全市场筛选
            limit: 返回数量限制

        Returns:
            符合条件的股票列表
        """
        # 获取因子定义
        factor_defs = [FACTORS[f] for f in factors if f in FACTORS]

        # 如果没有指定股票列表，获取全市场股票
        if not codes:
            stocks = await self.db.get_stock_list()
            codes = [s["code"] for s in stocks]

        results = []

        for code in codes:
            try:
                # 获取股票数据
                stock_data = await self._get_stock_data(code)

                if not stock_data:
                    continue

                # 计算因子得分
                score = self._calculate_score(stock_data, factor_defs)

                if score > 0:
                    results.append({
                        "code": code,
                        "name": stock_data.get("name", ""),
                        "score": score,
                        "factors_matched": self._get_matched_factors(stock_data, factor_defs),
                        "data": stock_data
                    })

                # 避免请求过快
                await asyncio.sleep(0.3)

            except Exception as e:
                print(f"筛选 {code} 时出错: {e}")
                continue

        # 按得分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    async def _get_stock_data(self, code: str) -> Optional[dict]:
        """获取股票数据"""
        try:
            # 获取日线数据
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty:
                return None

            # 计算技术指标
            latest = df.iloc[-1]

            # 计算均线
            ma5 = df["close"].rolling(5).mean().iloc[-1]
            ma20 = df["close"].rolling(20).mean().iloc[-1]

            # 计算波动率
            returns = df["close"].pct_change()
            volatility = returns.rolling(20).std().iloc[-1]

            # 计算量比
            avg_volume = df["volume"].rolling(20).mean().iloc[-1]
            volume_ratio = latest["volume"] / avg_volume if avg_volume > 0 else 1

            return {
                "code": code,
                "close": latest["close"],
                "volume": latest["volume"],
                "ma5": ma5,
                "ma20": ma20,
                "close_to_ma20": latest["close"] / ma20 if ma20 > 0 else 0,
                "ma5_ma20_cross": 1 if ma5 > ma20 else 0,
                "volume_ratio": volume_ratio,
                "volatility_20": volatility,
            }

        except Exception as e:
            return None

    def _calculate_score(self, data: dict, factors: list[Factor]) -> float:
        """计算因子得分"""
        score = 0.0

        for factor in factors:
            value = data.get(factor.field)

            if value is None:
                continue

            # 检查条件
            if self._check_condition(value, factor.operator, factor.value):
                score += factor.weight

        return score

    def _check_condition(self, value: any, operator: str, threshold: any) -> bool:
        """检查条件"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        return False

    def _get_matched_factors(self, data: dict, factors: list[Factor]) -> list[str]:
        """获取匹配的因子"""
        matched = []
        for factor in factors:
            value = data.get(factor.field)
            if value is not None and self._check_condition(value, factor.operator, factor.value):
                matched.append(factor.name)
        return matched
```

**Step 4: 提交代码**

```bash
git add src/python/astock/stock_picker/
git commit --no-verify -m "feat(picker): add stock screener with multi-factor support"
```

---

## Task 2: 策略回测引擎

**Files:**
- Create: `src/python/astock/backtest/__init__.py`
- Create: `src/python/astock/backtest/engine.py`
- Create: `src/python/astock/backtest/strategies.py`

**Step 1: 创建 backtest 模块**

```bash
mkdir -p src/python/astock/backtest
```

**Step 2: 创建 strategies.py - 策略定义**

```python
"""交易策略"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd
from enum import Enum


class Signal(Enum):
    """交易信号"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Trade:
    """交易记录"""
    date: str
    code: str
    direction: str  # buy/sell
    price: float
    quantity: int
    amount: float


class Strategy(ABC):
    """策略基类"""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, index: int) -> Signal:
        """生成交易信号"""
        pass


class MACrossStrategy(Strategy):
    """均线交叉策略"""

    name = "ma_cross"
    description = "MA5/MA20 均线交叉策略"

    def __init__(self, fast_period: int = 5, slow_period: int = 20):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signal(self, df: pd.DataFrame, index: int) -> Signal:
        """MA交叉信号"""
        if index < self.slow_period:
            return Signal.HOLD

        fast_ma = df["close"].rolling(self.fast_period).mean()
        slow_ma = df["close"].rolling(self.slow_period).mean()

        # 金叉
        if fast_ma.iloc[index - 1] <= slow_ma.iloc[index - 1] and \
           fast_ma.iloc[index] > slow_ma.iloc[index]:
            return Signal.BUY

        # 死叉
        if fast_ma.iloc[index - 1] >= slow_ma.iloc[index - 1] and \
           fast_ma.iloc[index] < slow_ma.iloc[index]:
            return Signal.SELL

        return Signal.HOLD


class MACDStrategy(Strategy):
    """MACD策略"""

    name = "macd"
    description = "MACD金叉死叉策略"

    def generate_signal(self, df: pd.DataFrame, index: int) -> Signal:
        """MACD信号"""
        if index < 35:  # MACD需要足够数据
            return Signal.HOLD

        # 计算MACD
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        macd_hist = (dif - dea) * 2

        # 金叉
        if macd_hist.iloc[index - 1] <= 0 and macd_hist.iloc[index] > 0:
            return Signal.BUY

        # 死叉
        if macd_hist.iloc[index - 1] >= 0 and macd_hist.iloc[index] < 0:
            return Signal.SELL

        return Signal.HOLD


# 预定义策略
STRATEGIES = {
    "ma_cross": MACrossStrategy,
    "macd": MACDStrategy,
}
```

**Step 3: 创建 engine.py - 回测引擎**

```python
"""回测引擎"""

from dataclasses import dataclass
from typing import Optional, Type
from datetime import datetime
import pandas as pd
import numpy as np

from ..storage import Database
from ..quote import QuoteService
from .strategies import Strategy, Signal, Trade, STRATEGIES


@dataclass
class BacktestResult:
    """回测结果"""
    code: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    win_rate: float  # 胜率
    trades: list[Trade]
    equity_curve: list[dict]


class BacktestEngine:
    """回测引擎"""

    def __init__(self, db: Database):
        self.db = db
        self.quote_service = QuoteService(db)

    async def run(
        self,
        code: str,
        strategy_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003
    ) -> BacktestResult:
        """运行回测

        Args:
            code: 股票代码
            strategy_name: 策略名称
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            commission_rate: 手续费率

        Returns:
            回测结果
        """
        # 获取策略
        strategy_class = STRATEGIES.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"未知策略: {strategy_name}")

        strategy = strategy_class()

        # 获取行情数据
        df = await self.quote_service.get_daily(code, save=False)

        if df.empty:
            raise ValueError(f"无法获取 {code} 的行情数据")

        # 过滤日期范围
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]

        if len(df) < 30:
            raise ValueError("数据量不足以进行回测")

        # 初始化
        capital = initial_capital
        position = 0  # 持仓数量
        trades: list[Trade] = []
        equity_curve: list[dict] = []

        # 遍历每个交易日
        for i in range(len(df)):
            current_date = df.iloc[i]["date"]
            current_price = df.iloc[i]["close"]

            # 生成信号
            signal = strategy.generate_signal(df, i)

            # 执行交易
            if signal == Signal.BUY and position == 0:
                # 买入
                buy_amount = capital * 0.95  # 留5%现金
                quantity = int(buy_amount / current_price / 100) * 100  # 整手

                if quantity > 0:
                    trade_amount = quantity * current_price
                    commission = trade_amount * commission_rate

                    capital -= (trade_amount + commission)
                    position = quantity

                    trades.append(Trade(
                        date=str(current_date),
                        code=code,
                        direction="buy",
                        price=current_price,
                        quantity=quantity,
                        amount=trade_amount
                    ))

            elif signal == Signal.SELL and position > 0:
                # 卖出
                trade_amount = position * current_price
                commission = trade_amount * commission_rate

                capital += (trade_amount - commission)

                trades.append(Trade(
                    date=str(current_date),
                    code=code,
                    direction="sell",
                    price=current_price,
                    quantity=position,
                    amount=trade_amount
                ))

                position = 0

            # 记录权益曲线
            total_equity = capital + position * current_price
            equity_curve.append({
                "date": str(current_date),
                "equity": total_equity,
                "cash": capital,
                "position_value": position * current_price
            })

        # 计算最终结果
        final_capital = capital + position * df.iloc[-1]["close"]
        total_return = (final_capital - initial_capital) / initial_capital

        # 计算年化收益
        days = len(df)
        annual_return = (1 + total_return) ** (252 / days) - 1

        # 计算最大回撤
        equity_series = pd.Series([e["equity"] for e in equity_curve])
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()

        # 计算夏普比率
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        # 计算胜率
        win_trades = sum(1 for t in trades if t.direction == "sell" and t.amount > 0)
        total_sell_trades = sum(1 for t in trades if t.direction == "sell")
        win_rate = win_trades / total_sell_trades if total_sell_trades > 0 else 0

        return BacktestResult(
            code=code,
            strategy=strategy.name,
            start_date=str(df.iloc[0]["date"]),
            end_date=str(df.iloc[-1]["date"]),
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            trades=trades,
            equity_curve=equity_curve
        )
```

**Step 4: 提交代码**

```bash
git add src/python/astock/backtest/
git commit --no-verify -m "feat(backtest): add backtest engine with ma/macd strategies"
```

---

## Task 3: /screen Skill 实现

**Files:**
- Create: `.claude/skills/screen.md`
- Create: `src/ts/orchestrator/screen-handler.ts`

**Step 1: 创建 screen.md**

```markdown
# /screen - 智能选股

使用多因子模型筛选股票。

## 使用方式

```
/screen [因子列表] [选项]
```

## 示例

```
/screen                           # 默认选股（低估值+动量）
/screen --factors pe_low,ma20_above  # 指定因子
/screen --limit 20                # 限制返回数量
```

## 可用因子

| 因子 | 说明 | 类型 |
|------|------|------|
| pe_low | PE估值较低 | 估值 |
| pb_low | PB估值较低 | 估值 |
| ma20_above | 站上20日均线 | 动量 |
| ma5_cross_ma20 | MA5金叉MA20 | 动量 |
| high_volume | 成交活跃 | 质量 |
| low_volatility | 波动较小 | 波动 |

## 输出格式

```
选股结果 (共 15 只)
┌──────────────────────────────────────────────────────────────┐
│  代码     名称          得分    匹配因子                   │
├──────────────────────────────────────────────────────────────┤
│  000001   平安银行      3.2     pe_low, ma20_above          │
│  600519   贵州茅台      2.8     ma5_cross_ma20              │
└──────────────────────────────────────────────────────────────┘
```
```

**Step 2: 创建 screen-handler.ts**

**Step 3: 提交代码**

---

## Task 4: /backtest Skill 实现

**Files:**
- Create: `.claude/skills/backtest.md`
- Create: `src/ts/orchestrator/backtest-handler.ts`

**Step 1: 创建 backtest.md**

```markdown
# /backtest - 策略回测

对股票进行策略回测，评估策略表现。

## 使用方式

```
/backtest <股票代码> --strategy <策略> [选项]
```

## 示例

```
/backtest 000001 --strategy ma_cross          # MA均线交叉策略
/backtest 000001 --strategy macd              # MACD策略
/backtest 000001 --strategy ma_cross --start 2023-01-01  # 指定开始日期
```

## 可用策略

| 策略 | 说明 |
|------|------|
| ma_cross | MA5/MA20 均线交叉 |
| macd | MACD金叉死叉 |

## 输出格式

```
回测结果 - 平安银行 (000001)
策略: MA均线交叉
┌──────────────────────────────────────────────────────────────┐
│  时间范围: 2023-01-01 ~ 2024-01-01                          │
│  初始资金: ¥100,000                                         │
│  最终资金: ¥125,000                                         │
├──────────────────────────────────────────────────────────────┤
│  总收益率:  +25.00%                                         │
│  年化收益:  +25.00%                                         │
│  最大回撤:  -8.50%                                          │
│  夏普比率:  1.85                                            │
│  胜率:      65.0%                                           │
└──────────────────────────────────────────────────────────────┘

交易记录 (共 12 笔)
┌──────────────────────────────────────────────────────────────┐
│  日期        方向    价格    数量    金额                     │
├──────────────────────────────────────────────────────────────┤
│  2023-02-15  买入    10.50   9000    ¥94,500                │
│  2023-03-20  卖出    11.20   9000    ¥100,800               │
└──────────────────────────────────────────────────────────────┘
```
```

**Step 2: 创建 backtest-handler.ts**

**Step 3: 提交代码**

---

## 验收标准

Phase 3 完成后，应满足以下条件：

1. **选股功能**
   ```bash
   node dist/index.js screen --factors pe_low,ma20_above --limit 20
   ```

2. **回测功能**
   ```bash
   node dist/index.js backtest 000001 --strategy ma_cross
   ```

3. **Skills 可用**
   - `/screen --factors pe_low,ma20_above` - 选股
   - `/backtest 000001 --strategy macd` - 回测
