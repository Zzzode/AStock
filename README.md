# A股 Agent Team 交易分析系统

这是一个以 **Agent Team 为产品核心** 的 A 股分析与决策项目。  
用户只需提出自然语言问题，系统就会自动组织多个专家 Agent 协作：获取数据、分工分析、交叉讨论、输出建议，并持续学习用户习惯。

Skills 与代码不是产品终点，而是 Agent 团队的执行基础设施。

## 🎯 产品目标

- Agent 主导：由 Orchestrator Agent 统一调度专家团队
- 多专家协作：行情、技术、风控、策略、风格学习并行分析
- 讨论后给建议：先生成多视角结论，再汇总可执行建议
- 持续个性化：根据用户历史行为更新风格画像与推荐参数
- 多入口一致：Claude Skills、TS CLI、Python CLI、REST API 共用同一能力内核

## 🚀 当前能力版图

- 行情查询：实时行情 + 基础指标
- 技术分析：MA / MACD / KDJ / RSI 信号
- 智能选股：多因子评分与排序
- 策略回测：策略执行与绩效指标输出
- 监控告警：自选池 + 告警状态/历史查询
- 配置与风格：用户偏好管理、风格学习、个性化推荐

## 🧠 Agent Team 架构

### 核心原则

1. **Agent 优先**：用户面向的是专家团队，不是单个命令
2. **能力解耦**：TS 编排协作流程，Python 提供确定性能力
3. **统一协议**：跨模块统一结构化输出，便于 Agent 汇总推理
4. **可演进**：可从单 Agent 升级到并行评审和辩论机制

### 分层结构

1. **交互入口层**（Claude Skills / TS CLI / Python CLI / REST API）  
2. **Agent 编排层**（`src/ts/orchestrator/*`）  
3. **能力执行层**（`src/python/astock/*`）  
4. **数据与画像层**（`data/*` + SQLite + 用户配置）

### 入口现状

- **Claude Skills**：8 个能力入口 `quote/analyze/screen/backtest/recommend/watch/alert/config`
- **TypeScript CLI**：接入 `quote`、`analyze`、`init`、`style`
- **Python CLI**：完整命令组（`screen/backtest/recommend/watch/alert/config` 等）
- **REST API**：提供 `/quote`、`/analyze`、`/screen`、`/backtest`、`/recommend`、`/config`

## 📦 安装

```bash
pnpm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python
```

## 🎯 快速开始

完整用户文档见：[docs/user-guide.md](docs/user-guide.md)

### 1) 初始化

```bash
# TypeScript CLI 方式
pnpm run build
node dist/index.js init
node dist/index.js init --refresh-stocks

# Python CLI 方式
.venv/bin/python -m astock.cli init-db
```

### 2) 常用命令

```bash
# 一键构建 + 初始化 + 启动 Agent Team（可传 code/question/days）
pnpm run dev:team -- 000001 "现在是否适合介入？" 120

# 连续调试时可跳过初始化，避免等待
pnpm run dev:team -- 000001 "现在是否适合介入？" 120 --skip-init

# 设置 team 分析阶段提醒阈值（秒），超过后会提示但不会中断
pnpm run dev:team -- 000001 "现在是否适合介入？" 120 --timeout 45

# TypeScript CLI（当前接入命令）
node dist/index.js quote 000001
node dist/index.js analyze 000001 -d 100
node dist/index.js style
node dist/index.js team 000001 -q "现在是否适合介入？" -d 120
node dist/index.js team-feedback 000001 -a watch_buy -o good -s ma_cross -n "回撤后反弹，节奏合适"

# Python CLI（完整能力）
.venv/bin/python -m astock.cli quote 000001
.venv/bin/python -m astock.cli screen --limit 10
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross
.venv/bin/python -m astock.cli recommend generate --user default
.venv/bin/python -m astock.cli config style
.venv/bin/python -m astock.cli alert status
```

`pnpm run dev:team -- 000001 "现在是否适合介入？" 120` 中最后的 `120` 表示技术分析回看天数（days）。
如果运行器自动传入额外的 `--` 分隔符，脚本会自动忽略，不影响参数解析。
支持参数：`--skip-init`（跳过初始化）与 `--timeout <秒>`（仅 team 分析阶段耗时提醒阈值，默认 120 秒，不会强制中断）。
`team` 分析会输出阶段进度：行情获取、技术分析、策略筛选、反馈画像加载、结论汇总。
结果面板包含“推理轨迹”三条可解释依据；若策略筛选超时会自动降级为中性而不是整次失败。

### 3) Claude Code Skills

| Skill | 功能 | 示例 |
|------|------|------|
| `/quote` | 实时行情查询 | `/quote 000001` |
| `/analyze` | 技术分析 | `/analyze 000001` |
| `/screen` | 智能选股 | `/screen --limit 10` |
| `/backtest` | 策略回测 | `/backtest 000001 --strategy ma_cross` |
| `/recommend` | 个性化推荐 | `/recommend` |
| `/watch` | 监控列表管理 | `/watch add 000001` |
| `/alert` | 监控告警管理 | `/alert status` |
| `/config` | 配置管理与风格学习 | `/config style` |

## 🔄 典型协作流程

1. 用户提问（如“现在平安银行是否适合介入？”）
2. Orchestrator Agent 拆解任务并调度相关专家
3. 行情/技术/风控/策略 Agent 并行产出结论
4. Orchestrator 聚合冲突观点并给出最终建议
5. 学习模块记录用户反馈，更新风格画像与配置

## 🧪 Agent Team MVP

- 当前新增 `team` 命令：单次请求触发多专家协作分析
- 专家视角覆盖：Market / Analysis / Strategy / Risk / Style
- 输出结构包含：`summary`、`experts`、`decision`、`counterpoints`
- 决策动作当前支持：`watch_buy`、`wait`、`hold_or_reduce`
- 支持反馈回写：通过 `team-feedback` 记录建议结果，影响风险偏好与策略权重
- 决策解释增强：输出 `decision.influence` 展示权重影响来源
- CLI 面板增强：`team` 命令直接展示基础分、风险扣分、风格偏置、策略权重和最终分

## 🌐 REST API

```bash
uvicorn astock.api:app --reload --port 8000
```

启动后访问 `http://localhost:8000/docs` 查看 OpenAPI 文档。

## 📊 项目结构

```
.
├── .claude/skills/               # Agent 团队调用协议与能力入口
├── src/ts/
│   ├── index.ts                  # TypeScript CLI 入口
│   ├── orchestrator/             # Agent 编排、调用聚合、结果统一
│   └── utils/python-bridge.ts    # Python 能力桥接
├── src/python/astock/
│   ├── cli.py                    # Python CLI 能力入口
│   ├── api.py                    # FastAPI 能力服务入口
│   ├── quote/ analysis/ storage/
│   ├── stock_picker/ backtest/
│   ├── monitor/ recommend/
│   ├── config/ learning/ portfolio/
│   └── utils/
├── data/                         # SQLite、配置、风格学习数据
└── docs/plans/                   # 架构与实现设计文档
```

## 🧪 测试与检查

```bash
# TypeScript
pnpm run build
pnpm test
pnpm test -- --run src/ts/orchestrator/__tests__/skill-acceptance.test.ts

# Python
source .venv/bin/activate
cd src/python
pytest astock/ -v --cov=astock
ruff check astock/
black --check astock/
mypy astock/
```

## 📈 策略说明

- TypeScript 编排层当前对回测策略名做了显式校验：`ma_cross`、`macd`
- Python 能力层可通过 API `/strategies` 查看可用策略集合

## 📄 License

MIT License
