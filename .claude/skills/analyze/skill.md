---
name: analyze
description: Use when user needs technical analysis for stocks including MA, MACD, KDJ, RSI indicators, detecting trading signals like golden cross and death cross, or understanding technical trends. Triggers on patterns like "分析一下XX股票", "XX技术指标怎么样", "000001技术分析", "茅台MACD" or when user asks about buy/sell signals.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /analyze - 技术分析

对股票进行技术分析，包括均线系统、MACD、KDJ、RSI 等指标，识别交易信号。

## 自动触发模式

| 用户输入模式 | 触发条件 |
|-------------|---------|
| "分析一下平安银行" | 分析请求 + 股票名称 |
| "000001技术指标" | 股票代码 + 技术指标关键词 |
| "茅台MACD怎么样" | 股票名称 + 指标名称 |
| "帮我看看XX的金叉死叉" | 信号分析请求 |

## 执行流程

### Step 1: 提取参数

从用户输入中提取：
- **股票代码**: 6位数字或股票名称
- **分析天数**: 默认 100 天，用户可指定如"分析200天数据"

### Step 2: 调用 Python 获取技术分析

使用 Bash 工具执行：

```bash
.venv/bin/python -m astock.cli analyze 000001 --days 120
```

### Step 3: 解析技术指标

从输出中提取关键指标：

| 指标 | 说明 | 关键阈值 |
|------|------|---------|
| MA5/MA10/MA20/MA60 | 均线系统 | 金叉/死叉 |
| MACD (DIF/DEA/柱) | 趋势动量 | 金叉/死叉/柱状变化 |
| KDJ (K/D/J) | 超买超卖 | J>80 超买, J<20 超卖 |
| RSI6 | 相对强弱 | >70 超买, <30 超卖 |

### Step 4: 解读信号

根据检测到的信号进行解读：

| 信号 | 含义 | 操作建议 |
|------|------|---------|
| MA金叉 | 短期均线上穿长期均线 | 看多信号 |
| MA死叉 | 短期均线下穿长期均线 | 看空信号 |
| MACD金叉 | MACD柱状线由负转正 | 看多信号 |
| MACD死叉 | MACD柱状线由正转负 | 看空信号 |
| KDJ超卖 | J值<20，可能反弹 | 关注买入机会 |
| KDJ超买 | J值>80，可能回调 | 注意风险 |
| RSI超卖 | RSI<30，可能反弹 | 关注买入机会 |
| RSI超买 | RSI>70，可能回调 | 注意风险 |

### Step 5: 输出分析结果

```
技术分析 - 平安银行 (000001)

价格指标
收盘价: 10.50
MA5: 10.32   MA10: 10.28   MA20: 10.15

MACD
DIF: 0.052   DEA: 0.041   柱: 0.011

KDJ
K: 72.5   D: 65.3   J: 86.9

RSI
RSI6: 58.2

检测到的信号
- MA5 上穿 MA20 (金叉) - 看多信号
- MACD柱状线由负转正 (MACD金叉) - 看多信号

综合判断: 技术面偏多，短期趋势向上
```

## 使用示例

### 示例 1: 自然语言触发

```
用户: 分析一下平安银行的技术指标

Claude: 我来分析平安银行(000001)的技术指标。
[调用 analyze CLI]

技术分析结果：
- 均线系统：MA5 上穿 MA20，形成金叉
- MACD：DIF 0.052 > DEA 0.041，金叉确认
- KDJ：J值 86.9，接近超买区域
- RSI：58.2，处于正常区间

综合判断：技术面偏多，但 KDJ 接近超买，注意短期回调风险。
```

### 示例 2: 斜杠命令

```
用户: /analyze 600519 --days 200

Claude:
技术分析 - 贵州茅台 (600519)
[分析结果...]
```

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/analysis/` - Python 技术分析服务