# A股交易策略分析工具 - 架构设计

## 项目概述

本项目目标是构建一个以 **Agent Team 为主导** 的 A 股专家分析交易团队。用户只需提出简单问题，系统自动组织多位专家 Agent 协作完成数据获取、分析、讨论、建议和持续学习。Skill 与代码是团队执行能力，而不是产品本体。

## 需求总结

| 维度 | 选择 |
|------|------|
| 数据源 | AkShare |
| 交易记录来源 | 券商导出 + 同花顺/东财 |
| 交易风格 | 短线 + 波段 |
| 实时性 | 盘中实时监控 |
| 监控范围 | 自选池 + 全市场扫描 |
| 提醒方式 | 多渠道组合 |
| 技术栈 | Python 数据层 + TS 应用层 |
| Agent 模式 | 专业分工 + 多策略结合 |
| 数据存储 | SQLite |
| 分析指标 | 全维度 (均线/MACD/KDJ/RSI/量价/形态) |

## 架构方案

采用 **Agent Team 主导架构**：以 Orchestrator Agent 为核心调度多专家协作，Skill/CLI/API 作为能力触发入口，TypeScript 层负责编排，Python 层负责确定性能力计算。

```
┌─────────────────────────────────────────────────────────┐
│                 用户自然语言请求 / 技能触发                │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐       │
│  │      Agent Team Orchestrator (主控 Agent)    │       │
│  │  意图解析 | 任务拆解 | 专家调度 | 结论整合    │       │
│  └────────────────────┬────────────────────────┘       │
│                       │                                 │
│  ┌────────────────────┴────────────────────────┐       │
│  │      Expert Agents（行情/技术/风险/策略/风格） │       │
│  └────────────────────┬────────────────────────┘       │
│                       │                                 │
│  ┌────────────────────┴────────────────────────┐       │
│  │        Skills / TS Handlers / API 入口层     │       │
│  └────────────────────┬────────────────────────┘       │
│                       │                                 │
│  ┌────────────────────┴────────────────────────┐       │
│  │             Python Capability Layer          │       │
│  │   quote | analysis | screen | backtest       │       │
│  │   monitor | recommend | config | learning     │       │
│  └─────────────────────────────────────────────┘       │
│                       │                                 │
│  ┌────────────────────┴────────────────────────┐       │
│  │              SQLite Storage                  │       │
│  │  行情数据 | 交易记录 | 分析结果 | 用户配置    │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Skill 体系设计

| Skill | 功能 | 描述 |
|-------|------|------|
| `/quote` | 实时行情查询 | 获取实时价格、涨跌幅、成交量，显示分时图、K线简图 |
| `/analyze` | 深度技术分析 | 均线系统、指标分析、量价关系、K线形态识别 |
| `/select` | 智能选股 | 全市场/自选池筛选，按技术条件/题材/资金流向筛选 |
| `/watch` | 监控管理 | 添加/移除监控标的，设置监控条件，查看监控列表 |
| `/alert` | 机会提醒 | 启动实时监控服务，查看当前机会，配置提醒渠道 |
| `/portfolio` | 持仓管理 | 导入交易记录，持仓盈亏分析，持仓建议 |
| `/style` | 交易风格学习 | 分析历史交易模式，生成风格画像，个性化建议优化 |
| `/backtest` | 策略回测 | 历史数据回测，策略效果评估 |

> Skills 在本项目中定位为 Agent Team 的标准化工具接口，用于让不同专家 Agent 通过统一协议调用能力模块。

## Agent 架构设计

### Agent 分工

```
┌─────────────────────────────────────────────────────┐
│          Orchestrator Agent (主控)                   │
│  - 接收用户问题，解析目标与约束                        │
│  - 拆解任务并调度专家 Agent 并行工作                    │
│  - 整合观点冲突，生成可执行建议与风险提示                │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Market   │   │ Analysis  │   │  Style    │
│  Agent    │   │  Agent    │   │  Agent    │
│  行情专家  │   │  技术专家  │   │  学习专家  │
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      │               │               │
      │   ┌───────────┼───────────┐   │
      │   │           │           │   │
      ▼   ▼           ▼           ▼   ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Strategy  │   │ Pattern  │   │   Risk   │
│ Agent    │   │Recognizer│   │ Agent    │
│ 策略专家  │   │ 形态识别  │   │ 风控专家  │
└──────────┘   └──────────┘   └──────────┘
```

### Agent 职责

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| Orchestrator | 主控调度与整合 | 用户请求 | 综合建议与解释 |
| Market Agent | 行情获取 | 股票代码 | 实时行情数据 |
| Analysis Agent | 技术分析 | 行情数据 | 技术指标结论 |
| Style Agent | 风格学习 | 历史交易 | 风格画像、个性化偏好 |
| Strategy Agent | 策略评估 | 指标与行情 | 策略候选与回测要点 |
| Pattern Recognizer | 形态识别 | K线数据 | K线形态信号 |
| Risk Agent | 风控评估 | 持仓+行情 | 风险评分、仓位建议 |

### 协作与讨论机制

- 专家 Agent 独立输出观点（看多/看空/中性）与证据
- Orchestrator 对冲突观点执行置信度加权与风险优先策略
- 输出包含建议、反方观点、关键假设与不确定性说明

## Python 数据层设计

### 模块架构

```
src/python/astock/
├── quote/              # 行情服务
│   ├── akshare_client.py
│   └── quote_service.py
├── analysis/           # 分析服务
│   ├── technical.py    # 技术指标
│   ├── patterns.py     # 形态识别
│   └── signals.py      # 信号生成
├── import/             # 导入服务
│   ├── brokers/        # 各券商解析器
│   └── importer.py
├── learning/           # 风格学习
│   ├── pattern_analyzer.py
│   └── style_profiler.py
├── monitor/            # 监控服务
│   ├── scanner.py
│   └── alert_engine.py
└── storage/            # 存储层
    ├── database.py
    └── models.py
```

### 数据库设计

```sql
-- 股票基础信息
CREATE TABLE stocks (
    code TEXT PRIMARY KEY,
    name TEXT,
    industry TEXT,
    list_date DATE
);

-- 日线行情
CREATE TABLE daily_quotes (
    code TEXT,
    date DATE,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    amount REAL,
    PRIMARY KEY (code, date)
);

-- 分时行情
CREATE TABLE intraday_quotes (
    code TEXT,
    datetime DATETIME,
    price REAL,
    volume REAL,
    amount REAL,
    PRIMARY KEY (code, datetime)
);

-- 交易记录
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    code TEXT,
    direction TEXT,
    price REAL,
    quantity REAL,
    traded_at DATETIME,
    source TEXT
);

-- 用户风格画像
CREATE TABLE style_profile (
    id INTEGER PRIMARY KEY,
    preference_vector TEXT,
    updated_at DATETIME
);

-- 监控配置
CREATE TABLE watchlist (
    code TEXT PRIMARY KEY,
    conditions TEXT,
    alert_channels TEXT,
    created_at DATETIME
);

-- 告警记录
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    code TEXT,
    type TEXT,
    message TEXT,
    triggered_at DATETIME,
    status TEXT
);
```

## 实时监控与提醒系统

### 监控架构

```
┌─────────────────────────────────────────────────────┐
│          Monitor Service (后台守护进程)              │
│                  Python asyncio                      │
└──────────────────────────┬──────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │ Quote Monitor │ │Signal Scanner │ │ Alert Engine  │
   │ 行情监控器     │ │ 信号扫描器     │ │ 告警引擎      │
   └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
           │                 │                 │
           │  每 30s 轮询    │  每 1min 扫描   │
           └─────────────────┴─────────────────┘
                             │
                             ▼
   ┌─────────────────────────────────────────────────┐
   │              Alert Dispatcher                    │
   │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
   │  │Terminal │  │ System  │  │ Webhook │         │
   │  │ CLI输出 │  │ 通知    │  │ 微信/钉钉│         │
   │  └─────────┘  └─────────┘  └─────────┘         │
   └─────────────────────────────────────────────────┘
```

### 监控任务

| 任务 | 频率 | 触发条件 |
|------|------|----------|
| 实时价格监控 | 30s | 价格突破设定阈值 |
| 技术信号扫描 | 1min | 金叉/死叉/背离等信号出现 |
| 形态识别扫描 | 5min | K线形态完成 |
| 全市场机会扫描 | 15min | 自选条件命中 |

### 告警分级

| Level | 说明 | 渠道 |
|-------|------|------|
| Level 1 - 紧急 | 持仓重大风险/触发止损止盈 | 终端 + 系统通知 + 微信/钉钉 |
| Level 2 - 重要 | 自选股买入信号/技术形态突破 | 终端 + 系统通知 |
| Level 3 - 一般 | 全市场扫描机会/常规状态更新 | 终端显示 |

## 交易风格学习系统

### 风格画像结构

```json
{
  "user_id": "default",
  "style_profile": {
    "holding_period": {
      "short_term": 0.7,
      "swing": 0.25,
      "long_term": 0.05
    },
    "risk_preference": {
      "aggressive": 0.6,
      "balanced": 0.3,
      "conservative": 0.1
    },
    "profit_taking": {
      "avg_profit_rate": 8.5,
      "avg_loss_rate": -5.2
    },
    "preferred_patterns": [
      {"pattern": "突破形态", "win_rate": 0.72, "count": 45},
      {"pattern": "回调买入", "win_rate": 0.65, "count": 38}
    ],
    "preferred_sectors": ["科技", "新能源", "医药"],
    "avoid_patterns": ["追高", "抄底失败"],
    "updated_at": "2026-03-08"
  }
}
```

### 个性化建议流程

```
市场机会 → 风格匹配度计算 → 历史相似度对比 → 生成建议

输出示例:
┌────────────────────────────────────────────────┐
│ 股票: XXXXXX                                    │
│ 信号: 突破20日均线+放量                         │
│                                                │
│ 风格匹配度: ★★★★☆ (85%)                        │
│ 历史相似交易胜率: 72%                           │
│                                                │
│ 建议: 适合你的交易风格                          │
│ 理由: 你在"突破形态"上历史胜率较高(72%)         │
│       该形态与你的偏好匹配度高                  │
│                                                │
│ 建议: 关注回调至20日均线附近入场                │
│ 止损: 跌破20日均线 -3%                          │
│ 止盈: 参考8-10%                                │
└────────────────────────────────────────────────┘
```

## 项目目录结构

```
a-stock-analyzer/
├── .claude/
│   └── skills/                    # Claude Code Skills
│       ├── quote.md
│       ├── analyze.md
│       ├── select.md
│       ├── watch.md
│       ├── alert.md
│       ├── portfolio.md
│       ├── style.md
│       └── backtest.md
│
├── src/
│   ├── ts/                        # TypeScript 应用层
│   │   ├── index.ts
│   │   ├── orchestrator/
│   │   ├── agents/
│   │   ├── services/
│   │   └── utils/
│   │
│   └── python/                    # Python 数据层
│       ├── astock/
│       │   ├── quote/
│       │   ├── analysis/
│       │   ├── import/
│       │   ├── learning/
│       │   ├── monitor/
│       │   └── storage/
│       ├── cli.py
│       └── pyproject.toml
│
├── data/                          # 数据目录
│   ├── stocks.db
│   ├── imports/
│   └── config.json
│
├── docs/
│   └── plans/
│
├── package.json
├── tsconfig.json
├── CLAUDE.md
└── README.md
```

## 技术栈

### TypeScript 应用层

| 依赖 | 用途 |
|------|------|
| Node.js 18+ | 运行时 |
| Commander.js / Inquirer.js | CLI 框架 |
| execa | 子进程调用 Python |
| node-notifier | 系统通知 |
| undici | HTTP 请求 (Webhook) |

### Python 数据层

| 依赖 | 用途 |
|------|------|
| Python 3.11+ | 运行时 |
| akshare | 行情数据 |
| ta-lib / pandas-ta | 技术指标 |
| pandas, numpy | 数据处理 |
| openpyxl | Excel 解析 |
| aiosqlite | 异步 SQLite |
| typer, rich | CLI 美化 |

### 存储与集成

| 组件 | 用途 |
|------|------|
| SQLite | 主数据库 |
| Redis (可选) | 高频缓存 |
| Server酱/企业微信 | 微信推送 |
| 钉钉机器人 | 钉钉推送 |

## 错误处理策略

### 数据获取层

- **重试机制**: 最多3次，指数退避 (1s, 2s, 4s)
- **降级方案**: 使用本地缓存 + 告知数据可能过时
- **错误提示**: 明确接口状态，建议稍后重试

### 交易数据导入

- **自动识别**: 文件来源 (券商/同花顺/东财)
- **字段校验**: 标记无法识别的行
- **预览模式**: 展示解析结果，用户确认后入库

### 监控服务异常

- **进程守护**: 自动重启，记录异常日志
- **状态持久化**: 配置写入文件，重启后恢复
- **心跳检测**: 定期检查服务状态

### 边界情况

| 场景 | 处理方式 |
|------|----------|
| 非交易时间 | 监控休眠，提示非交易时间 |
| 股票停牌 | 标记停牌，排除监控 |
| ST/退市股 | 识别风险，添加提示 |
| 数据缺失 | 标注缺失，不影响其他分析 |
| 配置损坏 | 使用默认配置 + 提示重置 |

## 实现路线图

### Phase 1: 基础框架 (MVP)

目标: 跑通核心链路，能查行情、能看分析

- [ ] 项目初始化 (TypeScript + Python 结构)
- [ ] Python 数据层: AkShare 行情获取
- [ ] SQLite 数据库初始化
- [ ] /quote Skill: 实时行情查询
- [ ] /analyze Skill: 基础技术指标 (MA/MACD/KDJ)
- [ ] Python 调用桥接

验收: `/quote 000001` 能返回实时行情和基础指标

### Phase 2: 监控与提醒

目标: 盘中实时监控，机会提醒

- [ ] /watch Skill: 自选池管理
- [ ] 监控服务: 后台守护进程
- [ ] 信号扫描器: 技术信号检测
- [ ] /alert Skill: 提醒服务
- [ ] 多渠道通知: 终端 + 系统通知 + Webhook

验收: 盘中能自动监控自选股并推送提醒

### Phase 3: 选股与回测

目标: 全市场扫描，策略验证

- [ ] 全市场扫描: 条件筛选
- [ ] /select Skill: 智能选股
- [ ] /backtest Skill: 策略回测
- [ ] K线形态识别

验收: `/select` 能从全市场筛选符合条件的股票

### Phase 4: 风格学习与个性化

目标: 学习交易风格，提供个性化建议

- [ ] 交易记录导入: 券商/同花顺/东财解析
- [ ] /portfolio Skill: 持仓管理
- [ ] 风格学习引擎
- [ ] /style Skill: 风格分析与画像
- [ ] 个性化建议: 基于风格匹配度

验收: 导入交易记录后能生成风格画像和个性化建议
