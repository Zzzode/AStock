---
name: quote
description: Use when user needs to query real-time stock prices, market data, current trading information, or check how a stock is performing today. Triggers on patterns like "XX股票现在多少钱", "平安银行行情", "查一下茅台价格", "000001现在怎么样" or when user mentions a stock with price/market context.
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
- 如果是股票名称，需要转换为代码（常见股票：平安银行=000001, 贵州茅台=600519, 五粮液=000858）

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

如果用户问的是"涨了吗"或"现在怎么样"，提供简短解读：
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

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/quote/` - Python 行情服务