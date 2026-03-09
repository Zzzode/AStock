# A股交易策略分析工具

基于 Agent Skills 的多 Agent A股交易策略分析工具。

## 🚀 功能特性

- **实时行情** - 获取A股实时行情数据
- **技术分析** - MA/MACD/KDJ/RSI 等技术指标分析
- **智能选股** - 基于多因子的智能选股
- **策略回测** - 支持多种策略的历史回测
- **实时监控** - 股票监控和告警通知
- **个性化推荐** - 基于交易风格的个性化推荐

## 📦 安装

```bash
# 安装 Python 依赖
pip install -e src/python

# 安装 Node.js 依赖
npm install

# 初始化数据库（如需要）
npm run init-db
```

## 🎯 快速开始

### Claude Code 运行方式

1) 打开 Claude Code
2) 通过斜杠命令调用 Skills
3) 关注输出中的多 Agent 观点与综合结论

### CLI 命令

```bash
# 查询行情
astock quote 000001

# 技术分析
astock analyze 000001 -d 100

# 智能选股
astock screen --limit 10

# 策略回测
astock backtest 000001 --strategy ma_cross

# 个性化推荐
astock recommend --user default

# 配置管理
astock config show
astock config set trading_style swing

# 交易风格学习
astock style
# 监控管理
astock watch add 000001
astock alert start
```

### Agent Skills

本工具提供 8 个 Agent Skills，可通过斜杠命令调用：

| Skill | 功能 | 示例 |
|-------|------|------|
| `/quote` | 实时行情查询 | `/quote 000001` |
| `/analyze` | 技术分析 | `/analyze 000001` |
| `/screen` | 智能选股 | `/screen --limit 10` |
| `/backtest` | 策略回测 | `/backtest 000001 --strategy ma_cross` |
| `/recommend` | 个性化推荐 | `/recommend` |
| `/watch` | 监控列表管理 | `/watch add 000001` |
| `/alert` | 监控告警管理 | `/alert start` |
| `/config` | 配置管理 | `/config show` |
| `/style` | 交易风格学习 | `/style` |

### REST API

```bash
# 启动 API 服务
uvicorn astock.api:app --reload --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

## 📊 项目结构

```
├── .claude/skills/          # Agent Skills 定义
│   ├── quote/               # 行情查询 skill
│   │   └── skill.md
│   ├── analyze/             # 技术分析 skill
│   │   └── skill.md
│   ├── screen/              # 智能选股 skill
│   │   └── skill.md
│   ├── backtest/            # 策略回测 skill
│   │   └── skill.md
│   ├── recommend/           # 个性化推荐 skill
│   │   └── skill.md
│   ├── watch/               # 监控管理 skill
│   │   └── skill.md
│   ├── alert/               # 告警管理 skill
│   │   └── skill.md
│   └── config/              # 配置管理 skill
│       └── skill.md
│
├── src/
│   ├── ts/                  # TypeScript 应用层
│   │   ├── index.ts         # CLI 入口
│   │   ├── orchestrator/    # 命令处理器
│   │   │   ├── quote-handler.ts
│   │   │   ├── analyze-handler.ts
│   │   │   ├── screen-handler.ts
│   │   │   ├── backtest-handler.ts
│   │   │   ├── recommend-handler.ts
│   │   │   ├── watch-handler.ts
│   │   │   ├── alert-handler.ts
│   │   │   └── config-handler.ts
│   │   └── utils/           # 工具函数
│   │       └── python-bridge.ts
│   │
│   └── python/astock/       # Python 数据层
│       ├── cli.py           # CLI 入口
│       ├── api.py           # REST API
│       ├── quote/           # 行情服务
│       ├── analysis/        # 技术分析
│       ├── storage/         # 数据存储
│       ├── stock_picker/    # 智能选股
│       ├── backtest/        # 策略回测
│       ├── monitor/         # 监控告警
│       ├── recommend/       # 个性化推荐
│       ├── portfolio/       # 持仓管理
│       ├── config/          # 配置管理
│       ├── learning/        # 风格学习
│       └── utils/           # 工具模块
│
├── docs/plans/              # 设计文档
├── data/                    # 数据目录
├── package.json             # Node.js 配置
└── src/python/pyproject.toml # Python 配置
```

## 🧪 测试

```bash
# Python 测试
cd src/python
pytest astock/ -v --cov

# TypeScript 测试
npm test

# Skill 协作验收测试
npm test -- --run src/ts/orchestrator/__tests__/skill-acceptance.test.ts
```

## 📈 支持的策略

| 策略 | 描述 |
|------|------|
| ma_cross | 双均线交叉策略 |
| macd | MACD 金叉死叉策略 |
| rsi | RSI 超买超卖策略 |
| kdj | KDJ 金叉死叉策略 |
| bollinger | 布林带策略 |
| turtle | 海龟交易策略 |
| dual_thrust | Dual Thrust 策略 |

## 🔔 告警渠道

- 终端输出
- 系统通知
- 企业微信
- 钉钉
- Telegram
- 邮件
- PushPlus

## 📝 开发规范

- Python 代码使用 `ruff` + `black` 格式化
- TypeScript 代码使用 ESLint 检查
- 提交信息遵循 Conventional Commits

## 📄 License

MIT License
