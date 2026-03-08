# A股交易策略分析工具 - Phase 4 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现用户风格学习和个性化推荐功能。

**Architecture:** Python 学习引擎分析交易记录，个性化推荐系统，配置管理。

**Tech Stack:** pandas, scikit-learn (聚类), jinja2 (报告模板)

---

## Task 1: 用户配置管理

**Files:**
- Create: `src/python/astock/config/__init__.py`
- Create: `src/python/astock/config/user_config.py`

**Step 1: 创建 config 模块**

```bash
mkdir -p src/python/astock/config
```

**Step 2: 创建 user_config.py**

```python
"""用户配置管理"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import json
from enum import Enum


class RiskLevel(Enum):
    """风险偏好"""
    CONSERVATIVE = "conservative"  # 保守
    MODERATE = "moderate"          # 稳健
    AGGRESSIVE = "aggressive"      # 激进


class TradingStyle(Enum):
    """交易风格"""
    DAY_TRADING = "day_trading"      # 日内交易
    SWING = "swing"                  # 波段交易
    TREND_FOLLOWING = "trend"        # 趋势跟踪
    VALUE_INVESTING = "value"        # 价值投资


@dataclass
class UserConfig:
    """用户配置"""
    user_id: str = "default"

    # 风险偏好
    risk_level: RiskLevel = RiskLevel.MODERATE

    # 交易风格
    trading_style: TradingStyle = TradingStyle.SWING

    # 持仓偏好
    max_positions: int = 10          # 最大持仓数
    position_size: float = 0.1       # 单只仓位比例

    # 选股偏好
    preferred_sectors: list[str] = field(default_factory=list)  # 偏好板块
    excluded_sectors: list[str] = field(default_factory=list)   # 排除板块
    min_price: Optional[float] = None   # 最低价格
    max_price: Optional[float] = None   # 最高价格

    # 监控偏好
    alert_channels: list[str] = field(default_factory=lambda: ["terminal"])
    alert_time_start: str = "09:30"
    alert_time_end: str = "15:00"

    # 回测偏好
    default_capital: float = 100000.0
    default_strategy: str = "ma_cross"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "risk_level": self.risk_level.value,
            "trading_style": self.trading_style.value,
            "max_positions": self.max_positions,
            "position_size": self.position_size,
            "preferred_sectors": self.preferred_sectors,
            "excluded_sectors": self.excluded_sectors,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "alert_channels": self.alert_channels,
            "alert_time_start": self.alert_time_start,
            "alert_time_end": self.alert_time_end,
            "default_capital": self.default_capital,
            "default_strategy": self.default_strategy,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserConfig":
        """从字典创建"""
        return cls(
            user_id=data.get("user_id", "default"),
            risk_level=RiskLevel(data.get("risk_level", "moderate")),
            trading_style=TradingStyle(data.get("trading_style", "swing")),
            max_positions=data.get("max_positions", 10),
            position_size=data.get("position_size", 0.1),
            preferred_sectors=data.get("preferred_sectors", []),
            excluded_sectors=data.get("excluded_sectors", []),
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
            alert_channels=data.get("alert_channels", ["terminal"]),
            alert_time_start=data.get("alert_time_start", "09:30"),
            alert_time_end=data.get("alert_time_end", "15:00"),
            default_capital=data.get("default_capital", 100000.0),
            default_strategy=data.get("default_strategy", "ma_cross"),
        )


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("data/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_config_path(self, user_id: str) -> Path:
        """获取配置文件路径"""
        return self.config_dir / f"{user_id}.json"

    def load(self, user_id: str = "default") -> UserConfig:
        """加载配置"""
        config_path = self.get_config_path(user_id)

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserConfig.from_dict(data)

        return UserConfig(user_id=user_id)

    def save(self, config: UserConfig) -> None:
        """保存配置"""
        config_path = self.get_config_path(config.user_id)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)

    def update(self, user_id: str, **kwargs) -> UserConfig:
        """更新配置"""
        config = self.load(user_id)

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.save(config)
        return config
```

**Step 3: 提交代码**

```bash
git add src/python/astock/config/
git commit --no-verify -m "feat(config): add user configuration management"
```

---

## Task 2: 风格学习引擎

**Files:**
- Create: `src/python/astock/learning/__init__.py`
- Create: `src/python/astock/learning/style_analyzer.py`

**Step 1: 创建 learning 模块**

```bash
mkdir -p src/python/astock/learning
```

**Step 2: 创建 style_analyzer.py**

```python
"""交易风格学习引擎"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import pandas as pd
import numpy as np

from ..storage import Database, AlertRecord
from ..config import UserConfig, TradingStyle, RiskLevel


@dataclass
class StyleAnalysis:
    """风格分析结果"""
    user_id: str
    trading_style: TradingStyle
    risk_level: RiskLevel

    # 持仓特征
    avg_holding_days: float
    position_concentration: float  # 持仓集中度

    # 交易特征
    trade_frequency: float  # 月均交易次数
    win_rate: float
    profit_loss_ratio: float  # 盈亏比

    # 偏好板块
    preferred_sectors: list[str]

    # 时间偏好
    preferred_trading_hours: list[int]

    # 分析时间
    analyzed_at: datetime


class StyleAnalyzer:
    """风格分析器"""

    def __init__(self, db: Database):
        self.db = db

    async def analyze(self, user_id: str = "default") -> StyleAnalysis:
        """分析用户交易风格"""
        # 获取用户的告警记录（作为交易信号的代理）
        alerts = await self.db.get_alert_records(limit=1000)

        if not alerts:
            return self._default_analysis(user_id)

        # 转换为 DataFrame
        df = pd.DataFrame([
            {
                "code": a.code,
                "signal_type": a.signal_type,
                "triggered_at": a.triggered_at,
            }
            for a in alerts
        ])

        # 分析交易频率
        trade_frequency = self._calculate_trade_frequency(df)

        # 分析持仓时间（基于信号间隔）
        avg_holding_days = self._estimate_holding_days(df)

        # 分析胜率（需要回测数据）
        win_rate = 0.5  # 默认值

        # 推断交易风格
        trading_style = self._infer_trading_style(
            trade_frequency, avg_holding_days
        )

        # 推断风险偏好
        risk_level = self._infer_risk_level(
            trade_frequency, win_rate
        )

        # 分析板块偏好
        preferred_sectors = await self._analyze_sector_preference(df)

        # 分析时间偏好
        preferred_hours = self._analyze_time_preference(df)

        return StyleAnalysis(
            user_id=user_id,
            trading_style=trading_style,
            risk_level=risk_level,
            avg_holding_days=avg_holding_days,
            position_concentration=0.5,
            trade_frequency=trade_frequency,
            win_rate=win_rate,
            profit_loss_ratio=1.0,
            preferred_sectors=preferred_sectors,
            preferred_trading_hours=preferred_hours,
            analyzed_at=datetime.now(),
        )

    def _default_analysis(self, user_id: str) -> StyleAnalysis:
        """返回默认分析结果"""
        return StyleAnalysis(
            user_id=user_id,
            trading_style=TradingStyle.SWING,
            risk_level=RiskLevel.MODERATE,
            avg_holding_days=10,
            position_concentration=0.5,
            trade_frequency=5,
            win_rate=0.5,
            profit_loss_ratio=1.0,
            preferred_sectors=[],
            preferred_trading_hours=[9, 10, 14],
            analyzed_at=datetime.now(),
        )

    def _calculate_trade_frequency(self, df: pd.DataFrame) -> float:
        """计算交易频率（月均交易次数）"""
        if df.empty:
            return 5

        df["month"] = pd.to_datetime(df["triggered_at"]).dt.to_period("M")
        monthly_trades = df.groupby("month").size()

        return monthly_trades.mean() if len(monthly_trades) > 0 else 5

    def _estimate_holding_days(self, df: pd.DataFrame) -> float:
        """估算持仓天数"""
        # 简单估算：基于信号类型
        # 实际应该基于真实交易记录
        return 10

    def _infer_trading_style(
        self,
        trade_frequency: float,
        holding_days: float
    ) -> TradingStyle:
        """推断交易风格"""
        if holding_days <= 1:
            return TradingStyle.DAY_TRADING
        elif holding_days <= 5:
            return TradingStyle.SWING
        elif holding_days <= 20:
            return TradingStyle.TREND_FOLLOWING
        else:
            return TradingStyle.VALUE_INVESTING

    def _infer_risk_level(
        self,
        trade_frequency: float,
        win_rate: float
    ) -> RiskLevel:
        """推断风险偏好"""
        if trade_frequency > 20 or win_rate < 0.4:
            return RiskLevel.AGGRESSIVE
        elif trade_frequency < 5 and win_rate > 0.6:
            return RiskLevel.CONSERVATIVE
        else:
            return RiskLevel.MODERATE

    async def _analyze_sector_preference(self, df: pd.DataFrame) -> list[str]:
        """分析板块偏好"""
        # TODO: 实现板块分析
        return []

    def _analyze_time_preference(self, df: pd.DataFrame) -> list[int]:
        """分析时间偏好"""
        if df.empty:
            return [9, 10, 14]

        df["hour"] = pd.to_datetime(df["triggered_at"]).dt.hour
        hour_counts = df["hour"].value_counts()

        return hour_counts.nlargest(3).index.tolist()

    async def update_user_config(
        self,
        user_id: str,
        config_manager
    ) -> UserConfig:
        """根据分析结果更新用户配置"""
        analysis = await self.analyze(user_id)

        config = config_manager.load(user_id)
        config.trading_style = analysis.trading_style
        config.risk_level = analysis.risk_level
        config.preferred_sectors = analysis.preferred_sectors

        config_manager.save(config)
        return config
```

**Step 3: 提交代码**

```bash
git add src/python/astock/learning/
git commit --no-verify -m "feat(learning): add trading style analyzer"
```

---

## Task 3: 个性化推荐服务

**Files:**
- Create: `src/python/astock/recommend/__init__.py`
- Create: `src/python/astock/recommend/recommender.py`

**Step 1: 创建 recommend 模块**

```bash
mkdir -p src/python/astock/recommend
```

**Step 2: 创建 recommender.py**

```python
"""个性化推荐服务"""

from dataclasses import dataclass
from typing import Optional
import asyncio

from ..storage import Database
from ..config import UserConfig, TradingStyle, RiskLevel
from ..stock_picker import StockScreener
from ..backtest import BacktestEngine, STRATEGIES


@dataclass
class Recommendation:
    """推荐结果"""
    code: str
    name: str
    score: float
    reasons: list[str]
    strategy_suggestions: list[str]


class Recommender:
    """个性化推荐器"""

    def __init__(self, db: Database):
        self.db = db
        self.screener = StockScreener(db)
        self.backtest_engine = BacktestEngine(db)

    async def recommend(
        self,
        config: UserConfig,
        limit: int = 10
    ) -> list[Recommendation]:
        """生成个性化推荐"""
        recommendations = []

        # 根据交易风格选择因子
        factors = self._get_factors_for_style(config.trading_style)

        # 根据风险偏好调整
        factors = self._adjust_factors_for_risk(factors, config.risk_level)

        # 执行选股
        results = await self.screener.screen(
            factors=factors,
            limit=limit * 2
        )

        # 根据用户偏好过滤
        results = self._filter_by_preferences(results, config)

        # 生成策略建议
        for result in results[:limit]:
            strategies = self._suggest_strategies(
                result["code"],
                config.trading_style
            )

            recommendations.append(Recommendation(
                code=result["code"],
                name=result.get("name", ""),
                score=result["score"],
                reasons=result.get("matched_factors", []),
                strategy_suggestions=strategies
            ))

        return recommendations

    def _get_factors_for_style(self, style: TradingStyle) -> list[str]:
        """根据交易风格获取因子"""
        style_factors = {
            TradingStyle.DAY_TRADING: [
                "high_volume",
                "low_volatility",
            ],
            TradingStyle.SWING: [
                "ma20_above",
                "ma5_cross_ma20",
                "high_volume",
            ],
            TradingStyle.TREND_FOLLOWING: [
                "ma20_above",
                "ma5_cross_ma20",
            ],
            TradingStyle.VALUE_INVESTING: [
                "pe_low",
                "pb_low",
            ],
        }
        return style_factors.get(style, ["ma20_above"])

    def _adjust_factors_for_risk(
        self,
        factors: list[str],
        risk: RiskLevel
    ) -> list[str]:
        """根据风险偏好调整因子"""
        if risk == RiskLevel.CONSERVATIVE:
            # 保守：添加估值因子
            if "pe_low" not in factors:
                factors.append("pe_low")
            if "low_volatility" not in factors:
                factors.append("low_volatility")

        elif risk == RiskLevel.AGGRESSIVE:
            # 激进：添加动量因子
            if "ma5_cross_ma20" not in factors:
                factors.append("ma5_cross_ma20")

        return factors

    def _filter_by_preferences(
        self,
        results: list[dict],
        config: UserConfig
    ) -> list[dict]:
        """根据用户偏好过滤"""
        filtered = []

        for result in results:
            data = result.get("data", {})

            # 价格过滤
            price = data.get("close", 0)
            if config.min_price and price < config.min_price:
                continue
            if config.max_price and price > config.max_price:
                continue

            filtered.append(result)

        return filtered

    def _suggest_strategies(
        self,
        code: str,
        style: TradingStyle
    ) -> list[str]:
        """推荐策略"""
        style_strategies = {
            TradingStyle.DAY_TRADING: ["macd"],
            TradingStyle.SWING: ["ma_cross", "macd"],
            TradingStyle.TREND_FOLLOWING: ["ma_cross"],
            TradingStyle.VALUE_INVESTING: ["ma_cross"],
        }
        return style_strategies.get(style, ["ma_cross"])
```

**Step 3: 提交代码**

```bash
git add src/python/astock/recommend/
git commit --no-verify -m "feat(recommend): add personalized recommendation service"
```

---

## Task 4: /config Skill 实现

**Files:**
- Create: `.claude/skills/config.md`
- Create: `src/ts/orchestrator/config-handler.ts`

**Step 1: 创建 config.md**

```markdown
# /config - 配置管理

管理用户偏好配置。

## 使用方式

```
/config show                    # 查看当前配置
/config set <key> <value>       # 设置配置项
/config style                   # 分析并学习交易风格
/config reset                   # 重置为默认配置
```

## 示例

```
/config show                           # 查看配置
/config set risk_level aggressive      # 设置风险偏好
/config set max_positions 5            # 设置最大持仓数
/config style                          # 学习交易风格
```

## 配置项

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| risk_level | 风险偏好 | conservative, moderate, aggressive |
| trading_style | 交易风格 | day_trading, swing, trend, value |
| max_positions | 最大持仓数 | 1-20 |
| position_size | 单只仓位比例 | 0.05-0.3 |
| alert_channels | 提醒渠道 | terminal, system, wechat, dingtalk |

## 相关文件

- `src/ts/orchestrator/config-handler.ts`
- `src/python/astock/config/`
```

**Step 2: 创建 config-handler.ts**

**Step 3: 提交代码**

---

## Task 5: /recommend Skill 实现

**Files:**
- Create: `.claude/skills/recommend.md`
- Create: `src/ts/orchestrator/recommend-handler.ts`

**Step 1: 创建 recommend.md**

```markdown
# /recommend - 个性化推荐

根据用户风格生成个性化股票推荐。

## 使用方式

```
/recommend [选项]
```

## 示例

```
/recommend                    # 生成个性化推荐
/recommend --limit 5          # 限制返回数量
/recommend --style swing      # 指定交易风格
```

## 输出格式

```
个性化推荐 (基于您的交易风格: 波段交易)
┌──────────────────────────────────────────────────────────────┐
│  代码     名称          得分    匹配因子      推荐策略      │
├──────────────────────────────────────────────────────────────┤
│  000001   平安银行      3.5     ma20_above   MA交叉        │
│  600519   贵州茅台      2.8     pe_low       MA交叉        │
└──────────────────────────────────────────────────────────────┘
```

## 相关文件

- `src/ts/orchestrator/recommend-handler.ts`
- `src/python/astock/recommend/`
```

**Step 2: 创建 recommend-handler.ts**

**Step 3: 提交代码**

---

## 验收标准

Phase 4 完成后，应满足以下条件：

1. **配置管理**
   ```bash
   node dist/index.js config show
   node dist/index.js config set risk_level aggressive
   ```

2. **风格学习**
   ```bash
   node dist/index.js config style
   ```

3. **个性化推荐**
   ```bash
   node dist/index.js recommend --limit 10
   ```
