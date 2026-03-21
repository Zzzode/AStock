---
name: quote
description: Use when user asks for a stock's latest price, intraday change, volume, turnover, today's performance, or a current market snapshot. Trigger on phrases like "现在多少钱", "最新价", "今日涨跌", "行情", "成交额", or "今天涨了吗". Do not use for technical analysis, indicator interpretation, or buy/sell decision questions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /quote - 实时行情查询

获取 A股股票的实时行情数据，包括价格、涨跌幅、成交量等关键信息。

## 自动触发模式

| 用户输入模式 | 触发条件 |
|-------------|---------|
| "平安银行现在多少钱" | 股票名称 + 价格查询 |
| "000001行情" | 股票代码 + 行情关键词 |
| "查一下茅台价格" | 价格查询请求 |
| "贵州茅台今天涨了吗" | 涨跌状态查询 |

## 执行流程

### Step 1: 提取股票代码

从用户输入中提取股票代码：
- 如果是6位数字，直接使用
- 如果是股票名称，先尝试常见映射，否则使用 AskUserQuestion 询问

**常见股票映射**：
| 名称 | 代码 |
|------|------|
| 平安银行 | 000001 |
| 贵州茅台 | 600519 |
| 五粮液 | 000858 |
| 中国平安 | 601318 |
| 中国电建 | 601669 |

如果无法确定股票代码，使用 AskUserQuestion 询问。

### Step 2: 调用 Python 获取行情

使用 Bash 工具执行：

```bash
.venv/bin/python -m astock.cli quote 000001
```

### Step 3: 解析并呈现数据

从输出中提取关键数据，以用户友好的方式呈现：

```
平安银行 (000001)
最新价: 10.50    涨跌幅: +2.34%
涨跌额: +0.24    昨收: 10.26
今开: 10.28      最高: 10.68
最低: 10.22      成交量: 1523万手
成交额: 1.58亿
```

### Step 4: 补充解读（可选）

如果用户问的是"涨了吗"或"今日表现如何"，提供简短解读：
- 涨跌幅 > 2%: "今日表现较强，上涨 X%"
- 涨跌幅 < -2%: "今日承压，下跌 X%"
- 其他: "今日波动较小，涨跌幅 X%"

## 使用示例

### 示例 1: 自然语言查询

```
用户: 平安银行现在多少钱？

Claude:
平安银行 (000001)
最新价: 10.50    涨跌幅: +2.34%
今日表现较强，上涨 2.34%
```

### 示例 2: 斜杠命令

```
用户: /quote 600519

Claude:
贵州茅台 (600519)
最新价: 1850.00    涨跌幅: -0.85%
今日小幅回调
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 股票代码不存在 | 提示用户确认代码 |
| 数据源超时 | 重试1次，失败则提示稍后再试 |
| 非交易时间 | 显示最后交易日数据并标注 |
| JSON 解析失败 | 尝试正则提取关键字段 |

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/quote/` - Python 行情服务