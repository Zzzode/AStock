# A股 Agent Team 用户使用文档

本文面向第一次使用本项目的用户，目标是让你在 5-10 分钟内完成安装并跑通一次 Agent Team 分析。

## 1. 先回答你的问题：`120` 是什么

命令：

```bash
pnpm run dev:team -- 000001 "现在是否适合介入？" 120

# 跳过初始化（适合连续调试）
pnpm run dev:team -- 000001 "现在是否适合介入？" 120 --skip-init

# 设置分析超时 45 秒（避免长时间无响应）
pnpm run dev:team -- 000001 "现在是否适合介入？" 120 --timeout 45
```

参数含义如下：

- `000001`：股票代码（6 位数字）
- `"现在是否适合介入？"`：你想问 Agent Team 的问题
- `120`：技术分析回看天数（`days`），即分析最近 120 个交易日数据

一般建议：

- 短线：`60~120`
- 波段：`120~250`
- 中长期：`250+`

## 2. 什么叫“启用 AI Agents”

这个项目的 Agent 是“按请求触发”的，不需要单独启动 AI 服务进程。

你执行以下任一命令时，都会自动启用 Agent 协作：

- `node dist/index.js team ...`
- `pnpm run dev:team -- ...`

其中 Orchestrator 会自动调度：

- Market Agent（行情）
- Analysis Agent（技术指标）
- Strategy Agent（策略筛选）
- Risk Agent（风险评估）
- Style Agent（风格/偏好）

## 3. 环境准备

```bash
cd /Users/zzzode/Develop/AStock

pnpm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python
```

## 4. 一键跑通（推荐）

```bash
pnpm run dev:team -- 000001 "现在是否适合介入？" 120
```

该命令会按顺序自动执行：

1. `pnpm run build`
2. `node dist/index.js init`
3. `node dist/index.js team <code> -q <question> -d <days>`

## 5. 分步运行（可控）

```bash
pnpm run build
node dist/index.js init
node dist/index.js team 000001 -q "现在是否适合介入？" -d 120
```

## 6. 反馈学习（让建议越来越个性化）

当你执行了建议后，可以把结果回写给系统：

```bash
node dist/index.js team-feedback 000001 -a watch_buy -o good -s ma_cross -n "回撤后反弹，节奏合适"
```

参数说明：

- `-a, --action`：当时系统给出的动作（`watch_buy` / `wait` / `hold_or_reduce`）
- `-o, --outcome`：结果好坏（`good` / `bad`）
- `-s, --strategy`：对应策略名（如 `ma_cross`）
- `-n, --note`：补充说明

## 7. 常见问题

### Q1: 不传参数可以吗？

可以：

```bash
pnpm run dev:team --
```

默认值：

- code: `000001`
- question: `现在是否适合介入？`
- days: `120`

### Q2: 为什么每次都初始化，感觉慢？

`dev:team` 设计目标是“新手一键跑通”，所以会先做初始化。  
如果你在连续调试，建议加 `--skip-init` 或直接用分步命令里的 `team` 命令。

### Q3: 命令看起来“卡住”了怎么办？

先看终端是否停在“步骤 3/3: 执行 Agent Team 分析”。  
分析阶段会持续输出进度：

- 正在获取行情数据
- 正在进行技术分析
- 正在进行策略筛选
- 正在加载用户反馈画像
- 正在汇总多专家结论

完成后会输出“推理轨迹”三条依据，便于你复核决策来源。

如果是网络/数据源慢导致等待，可以：

```bash
pnpm run dev:team -- 600589 "现在是否适合介入？" 20 --skip-init --timeout 45
```

当超过超时时间会打印提醒，但不会强制中断分析流程。  
如果策略筛选阶段超时，会自动降级为中性观点并继续给出结论。

### Q4: 我只想看分析，不想写反馈？

完全可以。`team-feedback` 不是必需步骤，只在你想让模型更贴近你的风格时使用。

## 8. 命令速查

```bash
# 一键分析
pnpm run dev:team -- 000001 "现在是否适合介入？" 120

# 指定分析
node dist/index.js team 600519 -q "是加仓还是等待？" -d 200

# 写入反馈
node dist/index.js team-feedback 600519 -a wait -o good -s ma_cross -n "等待后回撤更合理"
```
