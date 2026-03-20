# A股 Agent Team 交易分析系统

本项目是一个基于 Claude Code 的智能股票分析系统。通过 Skills 自动触发，直接调用 Python 脚本获取数据，Claude 进行智能推理分析。

## 快速开始

```bash
# 安装 Python 依赖
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python

# 初始化数据库
.venv/bin/python -m astock.cli init-db

# 直接在 Claude Code 中使用自然语言
# 不需要单独的 CLI，Claude Code 就是用户界面
```

## 使用方式

### 直接对话（推荐）

在 Claude Code 中用自然语言对话，Skills 会自动触发：

```
用户: 平安银行现在适合买吗？
Claude: 我来为您进行多专家综合分析...
[调用 Python 获取数据]
- 市场动能偏强，涨跌幅 +2.34%
- 技术信号偏多，检测到 MA5 金叉 MA20
- 综合建议：建议关注并分批试探（置信度 65%）

用户: 帮我选几只低估值、有金叉信号的股票
Claude: 我来根据您的条件筛选股票...
[调用 Python screen 命令]

用户: 回测一下 MA 策略在平安银行上的效果
Claude: 我来回测 MA 均线策略...
[调用 Python backtest 命令]
```

### 斜杠命令

也可以使用斜杠命令：

```
/quote 000001           # 查询行情
/analyze 000001         # 技术分析
/screen --limit 20      # 智能选股
/team 000001            # 多专家协作
```

## Skills

| Skill | 功能 | 自然语言触发示例 |
|-------|------|-----------------|
| /team | 多专家协作分析 | "平安银行现在适合买吗" |
| /quote | 实时行情查询 | "平安银行现在多少钱" |
| /analyze | 技术分析 | "分析一下茅台技术指标" |
| /screen | 智能选股 | "帮我选几只股票" |
| /backtest | 策略回测 | "回测一下MA策略" |
| /recommend | 个性化推荐 | "给我推荐几只股票" |
| /config | 配置管理 | `/config style` |

## Agent Team 工作流程

当您询问股票交易决策时，系统会自动协作：

```
用户输入: "平安银行现在适合买吗？"
    ↓
Claude 解析意图，识别股票代码和问题类型
    ↓
调用 Python 脚本获取数据：
├── .venv/bin/python -m astock.cli quote 000001     # 行情
├── .venv/bin/python -m astock.cli analyze 000001   # 技术分析
├── .venv/bin/python -m astock.cli screen --codes 000001  # 策略筛选
└── cat data/team-feedback.json                      # 用户画像
    ↓
Claude 进行智能推理：
├── Market Agent: 分析市场动能
├── Analysis Agent: 解读技术信号
├── Strategy Agent: 评估策略匹配
├── Risk Agent: 识别风险等级
└── Style Agent: 结合用户偏好
    ↓
输出决策建议、风险提示、反面论据
```

## 用户反馈闭环

分析完成后，您可以反馈效果：

```
Claude: 这个分析对您有帮助吗？您可以反馈：
- "执行后效果很好" - 会学习并增强此类建议
- "不太准确" - 会调整后续分析权重
```

记录反馈：
```bash
.venv/bin/python -m astock.cli team-feedback 000001 --action watch_buy --outcome good --strategy ma_cross --note "执行后收益符合预期"
```

## 项目结构

```
src/python/astock/          # Python 能力层（核心）
├── cli.py                  # CLI 入口
├── quote/                  # 行情服务
├── analysis/               # 技术分析
├── stock_picker/           # 选股器
├── backtest/               # 回测引擎
├── recommend/              # 推荐系统
└── monitor/                # 监控服务

.claude/skills/             # Skill 定义文件
├── team/skill.md           # 多专家协作
├── quote/skill.md          # 行情查询
├── analyze/skill.md        # 技术分析
├── screen/skill.md         # 智能选股
├── backtest/skill.md       # 策略回测
└── recommend/skill.md      # 个性化推荐

data/                       # 数据存储
├── team-feedback.json      # 用户反馈
└── sessions/               # 会话记录
```

## Skill 文件说明

每个 Skill 是一个可执行指令文件：
- `description` 字段用于自然语言意图匹配
- `<SUBAGENT-STOP>` 指令防止嵌套调用
- 明确的执行流程和 Python CLI 调用方式

## 开发规范

- Python 代码放在 `src/python/astock/`
- Skills 是指导 Claude 行为的指令文件
- 所有操作通过 Claude Code 完成，不需要单独 CLI