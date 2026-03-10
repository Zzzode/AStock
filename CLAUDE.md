# A股 Agent Team 交易分析系统

本项目的核心是一个可协作的专家 Agent 团队。  
Skills 与代码是 Agent Team 的执行基础设施，用于支撑分工分析、交叉讨论、综合建议与用户习惯学习。

## 快速开始

```bash
# 安装依赖
pnpm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python

# 构建 TypeScript CLI
pnpm run build

# 初始化数据库（两种方式任选其一）
node dist/index.js init
node dist/index.js init --refresh-stocks
.venv/bin/python -m astock.cli init-db

# 使用 Skills
/quote 000001      # 查询平安银行行情
/analyze 000001    # 分析技术指标
/config style      # 学习交易风格

# Agent Team CLI（MVP）
node dist/index.js team 000001 -q "现在是否适合介入？" -d 120
node dist/index.js team-feedback 000001 -a watch_buy -o good -s ma_cross -n "执行后收益符合预期"
```

## Claude Code 运行方式

1) 打开 Claude Code
2) 用自然语言提问或通过斜杠命令触发任务
3) Orchestrator Agent 自动调度专家 Agent 协作
4) 查看综合结论、风险提示，并持续反馈

## Skills

| Skill | 功能 | 示例 |
|-------|------|------|
| /quote | 实时行情查询 | `/quote 000001` |
| /analyze | 技术分析 | `/analyze 000001` |
| /screen | 智能选股 | `/screen --limit 10` |
| /backtest | 策略回测 | `/backtest 000001 --strategy ma_cross` |
| /recommend | 个性化推荐 | `/recommend` |
| /watch | 监控管理 | `/watch list` |
| /alert | 监控告警 | `/alert status` |
| /config | 配置管理与风格学习 | `/config style` |

## Agent Team 角色

- Orchestrator Agent：意图解析、任务拆解、专家调度、结论整合
- Market Agent：行情获取、市场状态判断
- Analysis Agent：技术指标与信号分析
- Risk Agent：仓位与风险暴露评估
- Strategy Agent：策略筛选、回测解释、执行建议
- Style Agent：用户风格学习与配置更新

## CLI 现状

- TypeScript CLI 当前接入命令：`quote`、`analyze`、`init`、`style`、`team`、`team-feedback`
- Python CLI 提供完整命令组：`quote`、`analyze`、`screen`、`backtest`、`recommend`、`watch`、`alert`、`config`

## 项目结构

```
src/
├── ts/           # Agent 编排层与 CLI
└── python/       # 确定性能力层（cli/api/策略能力）
```

## 开发规范

- TypeScript 代码放在 `src/ts/`
- Python 代码放在 `src/python/astock/`
- 测试与源码同级 `__tests__/` 目录
- 运行 `npm test` 或 `pnpm test` 时必须启用自动退出（如 `vitest --run`）
