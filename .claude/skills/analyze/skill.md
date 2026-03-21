---
name: analyze
description: Use when user asks for technical analysis of a stock, including MA, MACD, KDJ, RSI, golden cross, death cross, trend strength, support/resistance, or technical entry/exit signals from a chart perspective. Trigger on phrases like "技术分析", "分析一下XX", "均线", "MACD", "RSI", "金叉", "死叉", or "趋势怎么看". Do not use for simple price lookup or broader buy/sell decision advice involving position sizing or multi-factor judgment.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /analyze - 技术分析

对股票进行技术分析。Python 提供原始数据和信号检测，**由你进行动态推理分析**。

## 执行流程

### Step 1: 调用 Python 获取数据

```bash
.venv/bin/python -m astock.cli analyze <CODE> --json --days 100
```

### Step 2: 阅读输出数据

Python 输出包含：

| 字段 | 说明 |
|------|------|
| `indicators` | 当前技术指标数值 |
| `prev_indicators` | 前一日指标（用于对比） |
| `signals` | 检测到的信号（类型、当前值、倾向） |
| `signal_stats` | 信号统计（多/空数量） |
| `history` | 近期分析历史 |
| `feedback_stats` | 用户反馈统计（成功率） |
| `quote` | 实时行情 |

### Step 3: 进行推理分析

**你负责进行真正的分析推理，而不是套用模板。**

分析要点：
1. **指标解读** - 当前数值意味着什么？与前一日对比有什么变化？
2. **信号分析** - 检测到的信号可靠吗？是否需要结合其他指标确认？
3. **历史对比** - 近期出现过类似信号吗？当时走势如何？
4. **反馈参考** - 用户对类似信号的反馈成功率如何？
5. **风险评估** - 有哪些潜在风险？
6. **操作建议** - 给出具体的操作建议和理由

### Step 4: 输出分析报告

输出专业、详实的分析报告，格式自由但需包含：
- 行情概览
- 技术指标分析
- 信号解读（你的推理，不是预定义文字）
- 综合判断
- 操作建议
- 风险提示

## 分析示例

```
用户: 分析一下平安银行

Claude:
[调用 Python 获取数据]

平安银行(000001) 技术分析

行情概览：
最新价 10.77 元，跌幅 -1.01%，成交额 12.3 亿

技术指标分析：

均线系统：收盘价 10.77，低于 MA5(10.91)、MA10(10.89)、MA20(10.87)，
说明当前价格处于均线下方，短期趋势偏弱。三条均线粘合在一起（都在 10.87-10.91 区间），
表明近期处于震荡整理状态。

MACD：DIF -0.039，DEA -0.052，柱状线 0.013。MACD 在零轴下方运行，
说明整体趋势偏弱，但柱状线刚刚转正，可能是短期动能转强的信号。

KDJ：K 35.75，D 52.03，J 3.18。J 值只有 3.18，已经进入深度超卖区域。
历史来看，J 值跌到这个位置往往会有技术性反弹，但也可能持续超卖。

RSI：RSI6 为 33.24，接近超卖线 30，处于偏弱区间。

检测到的信号：
- KDJ超卖（J=3.18）- 理论上看多信号，但需谨慎

综合判断：
技术面整体偏弱，价格低于均线，MACD 在零轴下方。但 KDJ 的 J 值已经深度超卖，
短期可能出现技术性反弹。不过这种反弹的可靠性不高，需要放量配合才能确认。

操作建议：
- 空仓投资者：暂时观望，等待更明确的企稳信号（如放量阳线突破 MA5）
- 轻仓投资者：可以小仓位试探，但需严格止损
- 重仓投资者：暂时持有，关注 10.50 附近支撑

风险提示：
1. 深度超卖后可能继续超卖，不宜盲目抄底
2. 均线粘合后可能选择向下突破
3. 需关注大盘整体走势
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| CLI 执行失败 | 重试1次，失败则用 `--days 60` 降级 |
| JSON 解析失败 | 尝试正则提取关键指标 |
| 股票代码无效 | 提示用户确认代码 |
| 数据不足 | 标注数据缺失，继续可用部分分析 |

## 重要提醒

1. **你是分析师** - Python 只提供数据，分析和判断由你完成
2. **不要套模板** - 根据实际数据动态推理，不要用预定义的解读文字
3. **要有逻辑** - 分析要有逻辑链条，结论要有依据
4. **保持客观** - 指出正反两方面的因素，不要只说一边
5. **风险意识** - 任何判断都有不确定性，要提示风险