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
# 克隆仓库
git clone https://github.com/veloz-agents/astock-analyzer.git
cd astock-analyzer

# 安装 Python 依赖
pip install -e src/python

# 安装 Node.js 依赖
npm install

# 初始化数据库
npm run init-db
```

## 🎯 快速开始

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
```

### Agent Skills

```bash
/quote 000001      # 查询行情
/analyze 000001    # 技术分析
/screen            # 智能选股
/backtest 000001   # 策略回测
/recommend         # 个性化推荐
```

### REST API

```bash
# 启动 API 服务
uvicorn astock.api:app --reload --port 8000

# 访问 API 文档
open http://localhost:8000/docs
```

## 📊 项目结构

```
src/
├── ts/                    # TypeScript 应用层
│   ├── index.ts          # CLI 入口
│   ├── orchestrator/     # 命令处理器
│   └── utils/            # 工具函数
│
└── python/astock/        # Python 数据层
    ├── quote/            # 行情服务
    ├── analysis/         # 技术分析
    ├── storage/          # 数据存储
    ├── stock_picker/     # 智能选股
    ├── backtest/         # 策略回测
    ├── monitor/          # 监控告警
    ├── recommend/        # 个性化推荐
    ├── portfolio/        # 持仓管理
    ├── config/           # 配置管理
    └── utils/            # 工具模块
```

## 🧪 测试

```bash
# Python 测试
cd src/python
pytest astock/ -v --cov

# TypeScript 测试
npm test
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
