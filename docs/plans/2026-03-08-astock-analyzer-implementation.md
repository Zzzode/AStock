# A股交易策略分析工具 - Phase 1 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 搭建 MVP 框架，实现 `/quote` 行情查询和 `/analyze` 技术分析两个核心 Skill。

**Architecture:** Skill 中心化架构，Python 数据层负责行情获取和技术分析，TypeScript 应用层负责 CLI 入口和 Skill 编排，SQLite 存储数据。

**Tech Stack:** Node.js 18+, TypeScript 5.x, Python 3.11+, AkShare, ta-lib, SQLite, Commander.js, execa

---

## Task 1: 项目初始化 - 基础结构

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `.gitignore`
- Create: `CLAUDE.md`

**Step 1: 创建 package.json**

```json
{
  "name": "astock-analyzer",
  "version": "0.1.0",
  "description": "A股交易策略分析工具 - 基于 Agent Skills 的多 Agent 架构",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "vitest",
    "lint": "eslint src/ts/**/*.ts"
  },
  "dependencies": {
    "commander": "^12.0.0",
    "execa": "^8.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "typescript": "^5.3.0",
    "vitest": "^1.2.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**Step 2: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src/ts",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/ts/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Step 3: 创建 .gitignore**

```
# Dependencies
node_modules/
__pycache__/
*.pyc
.pyo
.pyd

# Build
dist/
*.egg-info/
.eggs/

# Data
data/*.db
data/imports/*
!data/imports/.gitkeep
data/logs/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.local
.venv/
venv/

# Test
coverage/
.pytest_cache/
```

**Step 4: 创建 CLAUDE.md**

```markdown
# A股交易策略分析工具

基于 Agent Skills 的多 Agent A股交易策略分析工具。

## 快速开始

```bash
# 安装依赖
pnpm install
pip install -e src/python

# 初始化数据库
pnpm run init-db

# 使用 Skills
/quote 000001      # 查询平安银行行情
/analyze 000001    # 分析技术指标
```

## Skills

| Skill | 功能 | 示例 |
|-------|------|------|
| /quote | 实时行情查询 | `/quote 000001` |
| /analyze | 技术分析 | `/analyze 000001` |

## 项目结构

```
src/
├── ts/           # TypeScript 应用层
└── python/       # Python 数据层
```

## 开发规范

- TypeScript 代码放在 `src/ts/`
- Python 代码放在 `src/python/astock/`
- 测试与源码同级 `__tests__/` 目录
```

**Step 5: 提交基础结构**

```bash
git add package.json tsconfig.json .gitignore CLAUDE.md
git commit -m "chore: init project structure"
```

---

## Task 2: Python 项目初始化

**Files:**
- Create: `src/python/pyproject.toml`
- Create: `src/python/astock/__init__.py`
- Create: `src/python/astock/py.typed`

**Step 1: 创建目录结构**

```bash
mkdir -p src/python/astock
```

**Step 2: 创建 pyproject.toml**

```toml
[project]
name = "astock"
version = "0.1.0"
description = "A股交易策略分析工具 - Python 数据层"
requires-python = ">=3.11"
dependencies = [
    "akshare>=1.12.0",
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "ta-lib>=0.4.28",
    "aiosqlite>=0.19.0",
    "typer>=0.9.0",
    "rich>=13.7.0",
    "pydantic>=2.5.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "mypy>=1.8.0"
]

[project.scripts]
astock = "astock.cli:app"

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["astock*"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

**Step 3: 创建 __init__.py**

```python
"""
A股交易策略分析工具 - Python 数据层
"""

__version__ = "0.1.0"
```

**Step 4: 创建 py.typed**

```
# Marker file for PEP 561
```

**Step 5: 提交 Python 项目结构**

```bash
git add src/python/
git commit -m "chore: init python project structure"
```

---

## Task 3: SQLite 数据库层

**Files:**
- Create: `src/python/astock/storage/__init__.py`
- Create: `src/python/astock/storage/database.py`
- Create: `src/python/astock/storage/models.py`
- Create: `src/python/astock/storage/__tests__/test_database.py`

**Step 1: 创建存储模块目录**

```bash
mkdir -p src/python/astock/storage/__tests__
```

**Step 2: 创建 storage/__init__.py**

```python
"""存储层模块"""

from .database import Database
from .models import Stock, DailyQuote

__all__ = ["Database", "Stock", "DailyQuote"]
```

**Step 3: 创建 storage/models.py**

```python
"""数据模型定义"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Stock(BaseModel):
    """股票基础信息"""

    code: str
    name: str
    industry: Optional[str] = None
    list_date: Optional[date] = None


class DailyQuote(BaseModel):
    """日线行情"""

    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


class IntradayQuote(BaseModel):
    """分时行情"""

    code: str
    datetime: datetime
    price: float
    volume: float
    amount: float


class Trade(BaseModel):
    """交易记录"""

    id: Optional[int] = None
    code: str
    direction: str  # buy/sell
    price: float
    quantity: float
    traded_at: datetime
    source: str  # broker/ths/eastmoney
```

**Step 4: 创建 storage/database.py**

```python
"""SQLite 数据库管理"""

import aiosqlite
from pathlib import Path
from typing import Optional

from .models import Stock, DailyQuote


class Database:
    """异步 SQLite 数据库管理器"""

    def __init__(self, db_path: str = "data/stocks.db"):
        self.db_path = Path(db_path)
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """连接数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def init_tables(self) -> None:
        """初始化数据表"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.executescript("""
            -- 股票基础信息
            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                list_date DATE
            );

            -- 日线行情
            CREATE TABLE IF NOT EXISTS daily_quotes (
                code TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (code, date)
            );

            -- 创建索引
            CREATE INDEX IF NOT EXISTS idx_daily_quotes_date
                ON daily_quotes(date);
        """)
        await self._conn.commit()

    async def save_stock(self, stock: Stock) -> None:
        """保存股票信息"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            """
            INSERT OR REPLACE INTO stocks (code, name, industry, list_date)
            VALUES (?, ?, ?, ?)
            """,
            (stock.code, stock.name, stock.industry, stock.list_date)
        )
        await self._conn.commit()

    async def save_daily_quotes(self, quotes: list[DailyQuote]) -> None:
        """批量保存日线行情"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.executemany(
            """
            INSERT OR REPLACE INTO daily_quotes
                (code, date, open, high, low, close, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (q.code, q.date, q.open, q.high, q.low, q.close, q.volume, q.amount)
                for q in quotes
            ]
        )
        await self._conn.commit()

    async def get_daily_quotes(
        self, code: str, limit: int = 100
    ) -> list[DailyQuote]:
        """获取日线行情"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        cursor = await self._conn.execute(
            """
            SELECT code, date, open, high, low, close, volume, amount
            FROM daily_quotes
            WHERE code = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (code, limit)
        )
        rows = await cursor.fetchall()

        return [
            DailyQuote(
                code=row["code"],
                date=row["date"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                amount=row["amount"]
            )
            for row in rows
        ]
```

**Step 5: 创建测试文件**

```python
"""数据库模块测试"""

import pytest
import asyncio
from pathlib import Path
import tempfile

from astock.storage import Database, Stock, DailyQuote
from datetime import date


@pytest.fixture
async def db():
    """创建临时数据库"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        database = Database(str(db_path))
        await database.connect()
        await database.init_tables()
        yield database
        await database.close()


@pytest.mark.asyncio
async def test_init_tables(db: Database):
    """测试表初始化"""
    # 应该不会抛出异常
    await db.init_tables()


@pytest.mark.asyncio
async def test_save_and_get_stock(db: Database):
    """测试保存和获取股票信息"""
    stock = Stock(
        code="000001",
        name="平安银行",
        industry="银行"
    )
    await db.save_stock(stock)

    # 验证可以重复保存
    stock2 = Stock(code="000001", name="平安银行", industry="银行")
    await db.save_stock(stock2)


@pytest.mark.asyncio
async def test_save_and_get_daily_quotes(db: Database):
    """测试保存和获取日线行情"""
    quotes = [
        DailyQuote(
            code="000001",
            date=date(2024, 1, 1),
            open=10.0,
            high=10.5,
            low=9.8,
            close=10.2,
            volume=1000000,
            amount=10200000
        ),
        DailyQuote(
            code="000001",
            date=date(2024, 1, 2),
            open=10.2,
            high=10.8,
            low=10.1,
            close=10.6,
            volume=1200000,
            amount=12720000
        )
    ]
    await db.save_daily_quotes(quotes)

    result = await db.get_daily_quotes("000001", limit=10)
    assert len(result) == 2
    assert result[0].date == date(2024, 1, 2)  # 最新的在前
```

**Step 6: 运行测试**

```bash
cd src/python
pip install -e ".[dev]"
pytest astock/storage/__tests__/test_database.py -v
```

**Step 7: 提交数据库层**

```bash
git add src/python/astock/storage/
git commit -m "feat(storage): add sqlite database layer with async support"
```

---

## Task 4: AkShare 行情服务

**Files:**
- Create: `src/python/astock/quote/__init__.py`
- Create: `src/python/astock/quote/akshare_client.py`
- Create: `src/python/astock/quote/quote_service.py`
- Create: `src/python/astock/quote/__tests__/test_quote_service.py`

**Step 1: 创建行情模块目录**

```bash
mkdir -p src/python/astock/quote/__tests__
```

**Step 2: 创建 quote/__init__.py**

```python
"""行情服务模块"""

from .quote_service import QuoteService
from .akshare_client import AkShareClient

__all__ = ["QuoteService", "AkShareClient"]
```

**Step 3: 创建 quote/akshare_client.py**

```python
"""AkShare 行情客户端"""

import akshare as ak
import pandas as pd
from datetime import date
from typing import Optional
import asyncio
from functools import wraps


def async_wrap(func):
    """将同步函数包装为异步"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class AkShareClient:
    """AkShare 行情数据客户端"""

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict:
        """获取实时行情

        Args:
            code: 股票代码，如 "000001"

        Returns:
            行情数据字典
        """
        # A股实时行情
        df = ak.stock_zh_a_spot_em()

        # 查找对应股票
        result = df[df["代码"] == code]
        if result.empty:
            raise ValueError(f"股票代码 {code} 不存在")

        row = result.iloc[0]
        return {
            "code": row["代码"],
            "name": row["名称"],
            "price": float(row["最新价"]) if row["最新价"] else 0.0,
            "change_percent": float(row["涨跌幅"]) if row["涨跌幅"] else 0.0,
            "change": float(row["涨跌额"]) if row["涨跌额"] else 0.0,
            "volume": float(row["成交量"]) if row["成交量"] else 0.0,
            "amount": float(row["成交额"]) if row["成交额"] else 0.0,
            "high": float(row["最高"]) if row["最高"] else 0.0,
            "low": float(row["最低"]) if row["最低"] else 0.0,
            "open": float(row["今开"]) if row["今开"] else 0.0,
            "prev_close": float(row["昨收"]) if row["昨收"] else 0.0,
        }

    @async_wrap
    def get_daily_quotes(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """获取日线行情

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame，包含 OHLCV 数据
        """
        period = "daily"
        adjust = "qfq"  # 前复权

        df = ak.stock_zh_a_hist(
            symbol=code,
            period=period,
            adjust=adjust
        )

        # 日期过滤
        if start_date:
            df = df[df["日期"] >= start_date.strftime("%Y-%m-%d")]
        if end_date:
            df = df[df["日期"] <= end_date.strftime("%Y-%m-%d")]

        # 重命名列
        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
        })

        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A股股票列表"""
        df = ak.stock_zh_a_spot_em()
        return df[["代码", "名称"]].rename(columns={
            "代码": "code",
            "名称": "name"
        })
```

**Step 4: 创建 quote/quote_service.py**

```python
"""行情服务"""

from datetime import date, datetime
from typing import Optional
import pandas as pd

from .akshare_client import AkShareClient
from ..storage import Database, DailyQuote


class QuoteService:
    """行情服务"""

    def __init__(self, db: Database):
        self.client = AkShareClient()
        self.db = db

    async def get_realtime(self, code: str) -> dict:
        """获取实时行情

        Args:
            code: 股票代码

        Returns:
            实时行情数据
        """
        return await self.client.get_realtime_quote(code)

    async def get_daily(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """获取日线数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            save: 是否保存到数据库

        Returns:
            日线 DataFrame
        """
        df = await self.client.get_daily_quotes(code, start_date, end_date)

        if save and not df.empty:
            quotes = [
                DailyQuote(
                    code=code,
                    date=row["date"] if isinstance(row["date"], date)
                        else datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    amount=float(row["amount"])
                )
                for _, row in df.iterrows()
            ]
            await self.db.save_daily_quotes(quotes)

        return df

    async def refresh_stocks(self) -> int:
        """刷新股票列表

        Returns:
            更新的股票数量
        """
        from ..storage import Stock

        df = await self.client.get_stock_list()
        count = 0

        for _, row in df.iterrows():
            stock = Stock(code=row["code"], name=row["name"])
            await self.db.save_stock(stock)
            count += 1

        return count
```

**Step 5: 创建测试文件**

```python
"""行情服务测试"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, patch

from astock.quote import QuoteService, AkShareClient


@pytest.fixture
def mock_db():
    """模拟数据库"""
    db = AsyncMock()
    return db


@pytest.fixture
def client():
    """创建客户端"""
    return AkShareClient()


@pytest.mark.asyncio
async def test_get_realtime_quote(client: AkShareClient):
    """测试获取实时行情"""
    # 这是一个集成测试，需要网络连接
    # 在实际测试中应该 mock
    try:
        result = await client.get_realtime_quote("000001")
        assert "code" in result
        assert "name" in result
        assert "price" in result
    except Exception as e:
        pytest.skip(f"网络不可用: {e}")


@pytest.mark.asyncio
async def test_quote_service_get_realtime(mock_db):
    """测试行情服务获取实时数据"""
    service = QuoteService(mock_db)

    with patch.object(
        service.client,
        "get_realtime_quote",
        return_value={"code": "000001", "name": "平安银行", "price": 10.5}
    ):
        result = await service.get_realtime("000001")
        assert result["code"] == "000001"
        assert result["price"] == 10.5
```

**Step 6: 运行测试**

```bash
cd src/python
pytest astock/quote/__tests__/test_quote_service.py -v
```

**Step 7: 提交行情服务**

```bash
git add src/python/astock/quote/
git commit -m "feat(quote): add akshare quote service with realtime and daily data"
```

---

## Task 5: 技术分析服务

**Files:**
- Create: `src/python/astock/analysis/__init__.py`
- Create: `src/python/astock/analysis/technical.py`
- Create: `src/python/astock/analysis/__tests__/test_technical.py`

**Step 1: 创建分析模块目录**

```bash
mkdir -p src/python/astock/analysis/__tests__
```

**Step 2: 创建 analysis/__init__.py**

```python
"""技术分析模块"""

from .technical import TechnicalAnalyzer

__all__ = ["TechnicalAnalyzer"]
```

**Step 3: 创建 analysis/technical.py**

```python
"""技术指标分析"""

import pandas as pd
import numpy as np
from typing import Optional
import talib


class TechnicalAnalyzer:
    """技术指标分析器"""

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: 包含 open, high, low, close, volume 的 DataFrame
        """
        self.df = df.copy()
        self.close = df["close"].values
        self.high = df["high"].values
        self.low = df["low"].values
        self.volume = df["volume"].values

    def add_ma(self, periods: list[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """添加均线指标

        Args:
            periods: 均线周期列表

        Returns:
            添加均线后的 DataFrame
        """
        for period in periods:
            self.df[f"ma{period}"] = talib.MA(self.close, timeperiod=period)
        return self.df

    def add_macd(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """添加 MACD 指标

        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            添加 MACD 后的 DataFrame
        """
        macd, signal_line, hist = talib.MACD(
            self.close,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )
        self.df["macd"] = macd
        self.df["macd_signal"] = signal_line
        self.df["macd_hist"] = hist
        return self.df

    def add_kdj(
        self,
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> pd.DataFrame:
        """添加 KDJ 指标

        Args:
            n: RSV 周期
            m1: K 值平滑周期
            m2: D 值平滑周期

        Returns:
            添加 KDJ 后的 DataFrame
        """
        rsv = (
            (self.close - talib.MIN(self.low, n)) /
            (talib.MAX(self.high, n) - talib.MIN(self.low, n))
        ) * 100

        # 处理除零情况
        rsv = np.nan_to_num(rsv, nan=50.0)

        k = talib.EMA(rsv, timeperiod=m1)
        d = talib.EMA(k, timeperiod=m2)
        j = 3 * k - 2 * d

        self.df["kdj_k"] = k
        self.df["kdj_d"] = d
        self.df["kdj_j"] = j
        return self.df

    def add_rsi(self, periods: list[int] = [6, 12, 24]) -> pd.DataFrame:
        """添加 RSI 指标

        Args:
            periods: RSI 周期列表

        Returns:
            添加 RSI 后的 DataFrame
        """
        for period in periods:
            self.df[f"rsi{period}"] = talib.RSI(self.close, timeperiod=period)
        return self.df

    def add_all(self) -> pd.DataFrame:
        """添加所有常用指标

        Returns:
            添加所有指标后的 DataFrame
        """
        self.add_ma()
        self.add_macd()
        self.add_kdj()
        self.add_rsi()
        return self.df

    def get_signals(self) -> dict:
        """获取技术信号

        Returns:
            信号字典
        """
        signals = []

        # 获取最新数据
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2] if len(self.df) > 1 else latest

        # MA 信号
        if "ma5" in self.df.columns and "ma20" in self.df.columns:
            if prev["ma5"] <= prev["ma20"] and latest["ma5"] > latest["ma20"]:
                signals.append({
                    "type": "ma_cross_up",
                    "name": "金叉",
                    "description": "MA5 上穿 MA20",
                    "bias": "bullish"
                })
            elif prev["ma5"] >= prev["ma20"] and latest["ma5"] < latest["ma20"]:
                signals.append({
                    "type": "ma_cross_down",
                    "name": "死叉",
                    "description": "MA5 下穿 MA20",
                    "bias": "bearish"
                })

        # MACD 信号
        if "macd" in self.df.columns:
            if prev["macd_hist"] <= 0 and latest["macd_hist"] > 0:
                signals.append({
                    "type": "macd_cross_up",
                    "name": "MACD金叉",
                    "description": "MACD 柱状线由负转正",
                    "bias": "bullish"
                })
            elif prev["macd_hist"] >= 0 and latest["macd_hist"] < 0:
                signals.append({
                    "type": "macd_cross_down",
                    "name": "MACD死叉",
                    "description": "MACD 柱状线由正转负",
                    "bias": "bearish"
                })

        # KDJ 信号
        if "kdj_k" in self.df.columns:
            # 超买超卖
            if latest["kdj_j"] < 20:
                signals.append({
                    "type": "kdj_oversold",
                    "name": "KDJ超卖",
                    "description": f"J值={latest['kdj_j']:.1f}，超卖区域",
                    "bias": "bullish"
                })
            elif latest["kdj_j"] > 80:
                signals.append({
                    "type": "kdj_overbought",
                    "name": "KDJ超买",
                    "description": f"J值={latest['kdj_j']:.1f}，超买区域",
                    "bias": "bearish"
                })

        # RSI 信号
        if "rsi6" in self.df.columns:
            if latest["rsi6"] < 30:
                signals.append({
                    "type": "rsi_oversold",
                    "name": "RSI超卖",
                    "description": f"RSI6={latest['rsi6']:.1f}，超卖区域",
                    "bias": "bullish"
                })
            elif latest["rsi6"] > 70:
                signals.append({
                    "type": "rsi_overbought",
                    "name": "RSI超买",
                    "description": f"RSI6={latest['rsi6']:.1f}，超买区域",
                    "bias": "bearish"
                })

        return {
            "signals": signals,
            "latest": {
                "close": float(latest["close"]),
                "ma5": float(latest.get("ma5", 0)),
                "ma10": float(latest.get("ma10", 0)),
                "ma20": float(latest.get("ma20", 0)),
                "macd": float(latest.get("macd", 0)),
                "macd_signal": float(latest.get("macd_signal", 0)),
                "macd_hist": float(latest.get("macd_hist", 0)),
                "kdj_k": float(latest.get("kdj_k", 0)),
                "kdj_d": float(latest.get("kdj_d", 0)),
                "kdj_j": float(latest.get("kdj_j", 0)),
                "rsi6": float(latest.get("rsi6", 0)),
            }
        }
```

**Step 4: 创建测试文件**

```python
"""技术分析测试"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta

from astock.analysis import TechnicalAnalyzer


@pytest.fixture
def sample_df():
    """创建示例数据"""
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    np.random.seed(42)

    # 生成模拟价格数据
    close = 10 + np.cumsum(np.random.randn(100) * 0.1)
    high = close + np.random.rand(100) * 0.5
    low = close - np.random.rand(100) * 0.5
    open_price = close + np.random.randn(100) * 0.2
    volume = np.random.rand(100) * 1000000

    return pd.DataFrame({
        "date": dates,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })


def test_add_ma(sample_df: pd.DataFrame):
    """测试均线计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_ma([5, 10, 20])

    assert "ma5" in result.columns
    assert "ma10" in result.columns
    assert "ma20" in result.columns

    # 验证 MA5 计算正确
    expected_ma5 = sample_df["close"].rolling(5).mean().iloc[-1]
    assert np.isclose(result["ma5"].iloc[-1], expected_ma5, equal_nan=True)


def test_add_macd(sample_df: pd.DataFrame):
    """测试 MACD 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_macd()

    assert "macd" in result.columns
    assert "macd_signal" in result.columns
    assert "macd_hist" in result.columns


def test_add_kdj(sample_df: pd.DataFrame):
    """测试 KDJ 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_kdj()

    assert "kdj_k" in result.columns
    assert "kdj_d" in result.columns
    assert "kdj_j" in result.columns

    # J 值应该更敏感
    latest = result.iloc[-1]
    assert 0 <= latest["kdj_k"] <= 100 or np.isnan(latest["kdj_k"])


def test_add_rsi(sample_df: pd.DataFrame):
    """测试 RSI 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_rsi([6, 12, 24])

    assert "rsi6" in result.columns
    assert "rsi12" in result.columns
    assert "rsi24" in result.columns


def test_get_signals(sample_df: pd.DataFrame):
    """测试信号获取"""
    analyzer = TechnicalAnalyzer(sample_df)
    analyzer.add_all()
    signals = analyzer.get_signals()

    assert "signals" in signals
    assert "latest" in signals
    assert isinstance(signals["signals"], list)


def test_add_all(sample_df: pd.DataFrame):
    """测试添加所有指标"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_all()

    assert "ma5" in result.columns
    assert "macd" in result.columns
    assert "kdj_k" in result.columns
    assert "rsi6" in result.columns
```

**Step 5: 运行测试**

```bash
cd src/python
pytest astock/analysis/__tests__/test_technical.py -v
```

**Step 6: 提交技术分析服务**

```bash
git add src/python/astock/analysis/
git commit -m "feat(analysis): add technical indicators (MA/MACD/KDJ/RSI)"
```

---

## Task 6: Python CLI 入口

**Files:**
- Create: `src/python/astock/cli.py`

**Step 1: 创建 CLI 入口**

```python
"""CLI 入口"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .storage import Database
from .quote import QuoteService
from .analysis import TechnicalAnalyzer


app = typer.Typer(name="astock")
console = Console()

# 默认数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"


@app.command()
def quote(
    code: str = typer.Argument(..., help="股票代码"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """获取实时行情"""
    async def _get_quote():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            result = await service.get_realtime(code)
            return result
        finally:
            await db.close()

    result = asyncio.run(_get_quote())

    if json_output:
        console.print_json(data=result)
    else:
        table = Table(title=f"{result['name']} ({result['code']})")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="green")

        table.add_row("最新价", f"{result['price']:.2f}")
        table.add_row("涨跌幅", f"{result['change_percent']:.2f}%")
        table.add_row("涨跌额", f"{result['change']:.2f}")
        table.add_row("今开", f"{result['open']:.2f}")
        table.add_row("最高", f"{result['high']:.2f}")
        table.add_row("最低", f"{result['low']:.2f}")
        table.add_row("昨收", f"{result['prev_close']:.2f}")
        table.add_row("成交量", f"{result['volume']/10000:.0f}万手")
        table.add_row("成交额", f"{result['amount']/100000000:.2f}亿")

        console.print(table)


@app.command()
def analyze(
    code: str = typer.Argument(..., help="股票代码"),
    days: int = typer.Option(100, "--days", "-d", help="分析天数"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """技术分析"""
    async def _analyze():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            df = await service.get_daily(code)

            if df.empty:
                return {"error": "无数据"}

            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            return analyzer.get_signals()
        finally:
            await db.close()

    result = asyncio.run(_analyze())

    if json_output:
        console.print_json(data=result)
    else:
        # 显示技术指标
        latest = result.get("latest", {})

        panel_content = f"""
[bold cyan]价格指标[/bold cyan]
收盘价: {latest.get('close', 0):.2f}
MA5: {latest.get('ma5', 0):.2f}
MA10: {latest.get('ma10', 0):.2f}
MA20: {latest.get('ma20', 0):.2f}

[bold cyan]MACD[/bold cyan]
DIF: {latest.get('macd', 0):.4f}
DEA: {latest.get('macd_signal', 0):.4f}
柱: {latest.get('macd_hist', 0):.4f}

[bold cyan]KDJ[/bold cyan]
K: {latest.get('kdj_k', 0):.2f}
D: {latest.get('kdj_d', 0):.2f}
J: {latest.get('kdj_j', 0):.2f}

[bold cyan]RSI[/bold cyan]
RSI6: {latest.get('rsi6', 0):.2f}
"""
        console.print(Panel(panel_content, title=f"技术分析 - {code}"))

        # 显示信号
        signals = result.get("signals", [])
        if signals:
            console.print("\n[bold yellow]检测到的信号:[/bold yellow]")
            for signal in signals:
                color = "green" if signal["bias"] == "bullish" else "red"
                console.print(f"  [{color}]●[/{color}] {signal['name']}: {signal['description']}")
        else:
            console.print("\n[dim]暂无明显信号[/dim]")


@app.command()
def init_db():
    """初始化数据库"""
    async def _init():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db = Database(str(DB_PATH))
        await db.connect()
        await db.init_tables()

        service = QuoteService(db)
        count = await service.refresh_stocks()

        await db.close()
        return count

    count = asyncio.run(_init())
    console.print(f"[green]数据库初始化完成，已加载 {count} 只股票[/green]")


if __name__ == "__main__":
    app()
```

**Step 2: 测试 CLI**

```bash
cd src/python
pip install -e .

# 初始化数据库
astock init-db

# 测试行情
astock quote 000001

# 测试分析
astock analyze 000001
```

**Step 3: 提交 CLI**

```bash
git add src/python/astock/cli.py
git commit -m "feat(cli): add python cli entry with quote and analyze commands"
```

---

## Task 7: TypeScript 应用层 - Python 桥接

**Files:**
- Create: `src/ts/utils/python-bridge.ts`
- Create: `src/ts/utils/__tests__/python-bridge.test.ts`

**Step 1: 创建目录结构**

```bash
mkdir -p src/ts/utils/__tests__
```

**Step 2: 创建 python-bridge.ts**

```typescript
/**
 * Python 调用桥接
 */

import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = path.resolve(__dirname, '../../python');

export interface QuoteResult {
  code: string;
  name: string;
  price: number;
  change_percent: number;
  change: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
}

export interface AnalysisResult {
  signals: Array<{
    type: string;
    name: string;
    description: string;
    bias: 'bullish' | 'bearish';
  }>;
  latest: {
    close: number;
    ma5: number;
    ma10: number;
    ma20: number;
    macd: number;
    macd_signal: number;
    macd_hist: number;
    kdj_k: number;
    kdj_d: number;
    kdj_j: number;
    rsi6: number;
  };
}

/**
 * 调用 Python CLI
 */
async function callPython(
  command: string,
  args: string[] = []
): Promise<string> {
  const result = await execa(
    'python',
    ['-m', 'astock.cli', command, ...args, '--json'],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return result.stdout;
}

/**
 * 获取实时行情
 */
export async function getQuote(code: string): Promise<QuoteResult> {
  const output = await callPython('quote', [code]);
  return JSON.parse(output);
}

/**
 * 获取技术分析
 */
export async function analyzeStock(
  code: string,
  days: number = 100
): Promise<AnalysisResult> {
  const output = await callPython('analyze', [code, '--days', String(days)]);
  return JSON.parse(output);
}

/**
 * 初始化数据库
 */
export async function initDatabase(): Promise<void> {
  await callPython('init-db');
}
```

**Step 3: 创建测试文件**

```typescript
/**
 * Python 桥接测试
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { initDatabase, getQuote, analyzeStock } from '../python-bridge';

describe('Python Bridge', () => {
  beforeAll(async () => {
    // 初始化数据库
    await initDatabase();
  }, 30000);

  it('should get quote', async () => {
    const result = await getQuote('000001');

    expect(result).toHaveProperty('code', '000001');
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('price');
    expect(typeof result.price).toBe('number');
  }, 30000);

  it('should analyze stock', async () => {
    const result = await analyzeStock('000001');

    expect(result).toHaveProperty('signals');
    expect(result).toHaveProperty('latest');
    expect(Array.isArray(result.signals)).toBe(true);
    expect(result.latest).toHaveProperty('close');
    expect(result.latest).toHaveProperty('ma5');
    expect(result.latest).toHaveProperty('macd');
  }, 30000);
});
```

**Step 4: 运行测试**

```bash
pnpm test src/ts/utils/__tests__/python-bridge.test.ts
```

**Step 5: 提交桥接模块**

```bash
git add src/ts/utils/
git commit -m "feat(ts): add python bridge for quote and analyze"
```

---

## Task 8: /quote Skill 实现

**Files:**
- Create: `.claude/skills/quote.md`
- Create: `src/ts/orchestrator/index.ts`
- Create: `src/ts/orchestrator/quote-handler.ts`

**Step 1: 创建目录结构**

```bash
mkdir -p .claude/skills src/ts/orchestrator
```

**Step 2: 创建 Skill 文件**

```markdown
# /quote - 实时行情查询

获取 A股股票的实时行情数据。

## 使用方式

```
/quote <股票代码>
```

## 示例

```
/quote 000001     # 查询平安银行
/quote 600519     # 查询贵州茅台
```

## 功能

1. 获取实时价格、涨跌幅、涨跌额
2. 显示今日开盘价、最高价、最低价
3. 显示成交量和成交额
4. 显示昨收价格

## 输出格式

```
┌─────────────────────────────────────────┐
│        平安银行 (000001)                 │
├─────────────────────────────────────────┤
│  最新价: 10.50      涨跌幅: +2.34%      │
│  涨跌额: +0.24      昨收: 10.26         │
│  今开: 10.28        最高: 10.68         │
│  最低: 10.22        成交量: 1523万手    │
│  成交额: 1.58亿                        │
└─────────────────────────────────────────┘
```

## 实现说明

调用 TypeScript 层的 `getQuote()` 函数，该函数通过 Python 桥接调用 AkShare 获取实时数据。

## 相关文件

- `src/ts/orchestrator/quote-handler.ts` - 处理逻辑
- `src/ts/utils/python-bridge.ts` - Python 调用桥接
- `src/python/astock/quote/` - Python 行情服务
```

**Step 3: 创建 quote-handler.ts**

```typescript
/**
 * /quote 命令处理器
 */

import { getQuote, QuoteResult } from '../utils/python-bridge.js';

export interface QuoteOutput {
  success: boolean;
  data?: QuoteResult;
  error?: string;
}

/**
 * 格式化行情数据为可读字符串
 */
function formatQuote(data: QuoteResult): string {
  const changeIcon = data.change_percent >= 0 ? '🔺' : '🔻';
  const changeColor = data.change_percent >= 0 ? '\x1b[31m' : '\x1b[32m';
  const reset = '\x1b[0m';

  return `
┌─────────────────────────────────────────┐
│        ${data.name} (${data.code})                 │
├─────────────────────────────────────────┤
│  最新价: ${data.price.toFixed(2).padEnd(12)}${changeColor}${changeIcon} ${data.change_percent.toFixed(2)}%${reset}
│  涨跌额: ${data.change >= 0 ? '+' : ''}${data.change.toFixed(2).padEnd(12)}昨收: ${data.prev_close.toFixed(2)}
│  今开: ${data.open.toFixed(2).padEnd(12)}最高: ${data.high.toFixed(2)}
│  最低: ${data.low.toFixed(2).padEnd(12)}成交量: ${(data.volume / 10000).toFixed(0)}万手
│  成交额: ${(data.amount / 100000000).toFixed(2)}亿                        │
└─────────────────────────────────────────┘
`;
}

/**
 * 处理 /quote 命令
 */
export async function handleQuote(code: string): Promise<QuoteOutput> {
  try {
    // 验证股票代码格式
    if (!/^\d{6}$/.test(code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${code}，应为6位数字`,
      };
    }

    const data = await getQuote(code);

    // 输出格式化结果
    console.log(formatQuote(data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取行情失败: ${message}`,
    };
  }
}
```

**Step 4: 创建 orchestrator/index.ts**

```typescript
/**
 * 主控模块入口
 */

export { handleQuote } from './quote-handler.js';
```

**Step 5: 提交 Skill**

```bash
git add .claude/skills/quote.md src/ts/orchestrator/
git commit -m "feat(skills): add /quote skill for realtime stock quotes"
```

---

## Task 9: /analyze Skill 实现

**Files:**
- Create: `.claude/skills/analyze.md`
- Create: `src/ts/orchestrator/analyze-handler.ts`

**Step 1: 创建 Skill 文件**

```markdown
# /analyze - 技术分析

对股票进行技术分析，包括均线、MACD、KDJ、RSI 等指标。

## 使用方式

```
/analyze <股票代码> [天数]
```

## 示例

```
/analyze 000001       # 分析平安银行，默认100天数据
/analyze 000001 200   # 分析平安银行，使用200天数据
```

## 功能

1. 均线系统 (MA5/10/20/60)
2. MACD 指标分析
3. KDJ 指标分析
4. RSI 指标分析
5. 信号检测（金叉、死叉、超买超卖等）

## 输出格式

```
┌─────────────────────────────────────────┐
│        技术分析 - 平安银行 (000001)      │
├─────────────────────────────────────────┤
│  价格指标                               │
│  收盘价: 10.50                         │
│  MA5: 10.32   MA10: 10.28  MA20: 10.15 │
│                                         │
│  MACD                                   │
│  DIF: 0.052   DEA: 0.041   柱: 0.011   │
│                                         │
│  KDJ                                    │
│  K: 72.5   D: 65.3   J: 86.9           │
│                                         │
│  RSI                                    │
│  RSI6: 58.2                            │
├─────────────────────────────────────────┤
│  检测到的信号                           │
│  🟢 金叉: MA5 上穿 MA20                 │
│  🟢 MACD金叉: MACD 柱状线由负转正       │
└─────────────────────────────────────────┘
```

## 信号说明

| 信号 | 含义 | 偏向 |
|------|------|------|
| 金叉 | 短期均线上穿长期均线 | 看多 |
| 死叉 | 短期均线下穿长期均线 | 看空 |
| MACD金叉 | MACD柱状线由负转正 | 看多 |
| MACD死叉 | MACD柱状线由正转负 | 看空 |
| KDJ超卖 | J值<20，可能反弹 | 看多 |
| KDJ超买 | J值>80，可能回调 | 看空 |
| RSI超卖 | RSI<30，可能反弹 | 看多 |
| RSI超买 | RSI>70，可能回调 | 看空 |

## 实现说明

调用 TypeScript 层的 `analyzeStock()` 函数，该函数通过 Python 桥接获取历史数据并计算技术指标。

## 相关文件

- `src/ts/orchestrator/analyze-handler.ts` - 处理逻辑
- `src/ts/utils/python-bridge.ts` - Python 调用桥接
- `src/python/astock/analysis/` - Python 技术分析服务
```

**Step 2: 创建 analyze-handler.ts**

```typescript
/**
 * /analyze 命令处理器
 */

import { analyzeStock, AnalysisResult } from '../utils/python-bridge.js';

export interface AnalyzeOutput {
  success: boolean;
  data?: AnalysisResult;
  error?: string;
}

/**
 * 格式化分析结果
 */
function formatAnalysis(code: string, data: AnalysisResult): string {
  const latest = data.latest;
  const signals = data.signals;

  let output = `
┌─────────────────────────────────────────┐
│        技术分析 - ${code}                   │
├─────────────────────────────────────────┤
│  价格指标                               │
│  收盘价: ${latest.close.toFixed(2)}                         │
│  MA5: ${latest.ma5.toFixed(2)}   MA10: ${latest.ma10.toFixed(2)}  MA20: ${latest.ma20.toFixed(2)} │
│                                         │
│  MACD                                   │
│  DIF: ${latest.macd.toFixed(4)}   DEA: ${latest.macd_signal.toFixed(4)}   柱: ${latest.macd_hist.toFixed(4)}   │
│                                         │
│  KDJ                                    │
│  K: ${latest.kdj_k.toFixed(2)}   D: ${latest.kdj_d.toFixed(2)}   J: ${latest.kdj_j.toFixed(2)}           │
│                                         │
│  RSI                                    │
│  RSI6: ${latest.rsi6.toFixed(2)}                            │
├─────────────────────────────────────────┤
`;

  if (signals.length > 0) {
    output += `│  检测到的信号                           │\n`;
    for (const signal of signals) {
      const icon = signal.bias === 'bullish' ? '🟢' : '🔴';
      output += `│  ${icon} ${signal.name}: ${signal.description.padEnd(20)}│\n`;
    }
  } else {
    output += `│  暂无明显信号                           │\n`;
  }

  output += `└─────────────────────────────────────────┘\n`;

  return output;
}

/**
 * 处理 /analyze 命令
 */
export async function handleAnalyze(
  code: string,
  days: number = 100
): Promise<AnalyzeOutput> {
  try {
    // 验证股票代码格式
    if (!/^\d{6}$/.test(code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${code}，应为6位数字`,
      };
    }

    const data = await analyzeStock(code, days);

    // 输出格式化结果
    console.log(formatAnalysis(code, data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `技术分析失败: ${message}`,
    };
  }
}
```

**Step 3: 更新 orchestrator/index.ts**

```typescript
/**
 * 主控模块入口
 */

export { handleQuote } from './quote-handler.js';
export { handleAnalyze } from './analyze-handler.js';
```

**Step 4: 提交 Skill**

```bash
git add .claude/skills/analyze.md src/ts/orchestrator/analyze-handler.ts
git commit -m "feat(skills): add /analyze skill for technical analysis"
```

---

## Task 10: CLI 入口与集成测试

**Files:**
- Create: `src/ts/index.ts`
- Create: `src/ts/__tests__/integration.test.ts`

**Step 1: 创建 CLI 入口**

```typescript
/**
 * A股交易策略分析工具 - CLI 入口
 */

import { Command } from 'commander';
import { handleQuote } from './orchestrator/quote-handler.js';
import { handleAnalyze } from './orchestrator/analyze-handler.js';
import { initDatabase } from './utils/python-bridge.js';

const program = new Command();

program
  .name('astock')
  .description('A股交易策略分析工具')
  .version('0.1.0');

program
  .command('quote <code>')
  .description('获取股票实时行情')
  .action(async (code: string) => {
    const result = await handleQuote(code);
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('analyze <code>')
  .description('技术分析')
  .option('-d, --days <days>', '分析天数', '100')
  .action(async (code: string, options: { days: string }) => {
    const result = await handleAnalyze(code, parseInt(options.days, 10));
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('init')
  .description('初始化数据库')
  .action(async () => {
    console.log('正在初始化数据库...');
    await initDatabase();
    console.log('数据库初始化完成');
  });

program.parse();
```

**Step 2: 更新 package.json 添加 bin**

```json
{
  "bin": {
    "astock": "./dist/index.js"
  }
}
```

**Step 3: 创建集成测试**

```typescript
/**
 * 集成测试
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLI_PATH = path.resolve(__dirname, '../../python');

describe('Integration Tests', () => {
  beforeAll(async () => {
    // 初始化数据库
    await execa('python', ['-m', 'astock.cli', 'init-db'], {
      cwd: CLI_PATH,
    });
  }, 60000);

  it('should get quote via CLI', async () => {
    const result = await execa('python', [
      '-m', 'astock.cli', 'quote', '000001', '--json'
    ], {
      cwd: CLI_PATH,
    });

    const data = JSON.parse(result.stdout);
    expect(data.code).toBe('000001');
    expect(data).toHaveProperty('name');
    expect(data).toHaveProperty('price');
  }, 30000);

  it('should analyze via CLI', async () => {
    const result = await execa('python', [
      '-m', 'astock.cli', 'analyze', '000001', '--json'
    ], {
      cwd: CLI_PATH,
    });

    const data = JSON.parse(result.stdout);
    expect(data).toHaveProperty('signals');
    expect(data).toHaveProperty('latest');
    expect(Array.isArray(data.signals)).toBe(true);
  }, 30000);
});
```

**Step 4: 构建和测试**

```bash
# 安装依赖
pnpm install
cd src/python && pip install -e ".[dev]" && cd ../..

# 初始化数据库
pnpm run build
node dist/index.js init

# 测试
pnpm test

# 测试 Skill
node dist/index.js quote 000001
node dist/index.js analyze 000001
```

**Step 5: 提交最终集成**

```bash
git add src/ts/index.ts src/ts/__tests__/ package.json
git commit -m "feat: complete phase 1 mvp with cli and skills integration"
```

---

## 验收标准

Phase 1 完成后，应满足以下条件：

1. **数据库初始化**
   ```bash
   node dist/index.js init
   # 或
   astock init
   ```
   输出：`数据库初始化完成，已加载 XXXX 只股票`

2. **行情查询**
   ```bash
   node dist/index.js quote 000001
   ```
   输出格式化的行情数据，包含价格、涨跌幅、成交量等

3. **技术分析**
   ```bash
   node dist/index.js analyze 000001
   ```
   输出技术指标和信号检测

4. **Skills 可用**
   - `/quote 000001` - 在 Claude Code 中可用
   - `/analyze 000001` - 在 Claude Code 中可用

---

## 后续阶段

完成 Phase 1 后，继续实现：
- **Phase 2**: 监控与提醒 (/watch, /alert)
- **Phase 3**: 选股与回测 (/select, /backtest)
- **Phase 4**: 风格学习与个性化 (/portfolio, /style)
