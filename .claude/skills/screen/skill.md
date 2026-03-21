---
name: screen
description: Use when user needs to screen or filter stocks based on technical indicators, valuation factors, or custom criteria. Triggers on patterns like "帮我选股", "筛选一下股票", "找一些低估值的股票", "哪些股票符合MA金叉", "选几只股票" or when user asks for stock recommendations based on specific conditions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /screen - 智能选股

根据技术指标因子筛选符合条件的股票，支持估值、动量、质量、波动等多维度筛选。

## 自动触发模式

| 用户输入模式 | 触发条件 |
|-------------|---------|
| "帮我选几只股票" | 选股请求 |
| "筛选一下低估值股票" | 筛选条件 + 股票 |
| "哪些股票有MA金叉" | 技术条件筛选 |
| "找一些放量突破的票" | 动量条件筛选 |

## 执行流程

### Step 1: 解析筛选条件

从用户输入中识别筛选条件：

| 条件关键词 | 对应因子 |
|-----------|---------|
| 低估值、便宜 | pe_low, pb_low |
| MA金叉、均线金叉 | ma5_cross_ma20 |
| 站上均线、突破均线 | ma20_above |
| 放量、成交量放大 | high_volume |
| 低波动、稳定 | low_volatility |

如果用户未指定条件，使用默认的全因子筛选。

### Step 2: 调用 Python 执行选股

使用 Bash 工具执行：

```bash
# 使用指定因子
.venv/bin/python -m astock.cli screen ma_cross,rsi_oversold --limit 10

# 全因子筛选
.venv/bin/python -m astock.cli screen --limit 10
```

### Step 3: 解析选股结果

从输出中提取筛选结果，包括：
- 股票代码和名称
- 综合得分
- 匹配的因子列表

### Step 4: 输出筛选结果

```
选股结果 (共 10 只)

排名  代码      名称        得分    匹配因子
 1   000001   平安银行     4.5    ma20_above, ma5_cross_ma20
 2   600519   贵州茅台     3.0    pe_low, pb_low
 3   000858   五粮液       2.5    high_volume, ma20_above
 ...

筛选条件: 全因子筛选
数据时间: 2026-03-20
```

### Step 5: 补充解读（可选）

如果用户询问"为什么选这些"，提供因子解读：

```
平安银行 (000001) 得分 4.5
- 站上20日线：价格突破短期压力位
- MA5金叉MA20：短期趋势转强信号
- 综合判断：技术面偏多，可关注
```

## 可用因子

| 因子键名 | 名称 | 类型 | 描述 | 权重 |
|---------|------|------|------|------|
| pe_low | 低市盈率 | 估值 | 市盈率小于30倍 | 1.0 |
| pb_low | 低市净率 | 估值 | 市净率小于3倍 | 1.0 |
| ma20_above | 站上20日线 | 动量 | 收盘价站上20日均线 | 1.5 |
| ma5_cross_ma20 | MA5金叉MA20 | 动量 | 5日均线上穿20日均线 | 2.0 |
| high_volume | 放量 | 质量 | 成交量大于5日均量2倍 | 1.0 |
| low_volatility | 低波动 | 波动 | 20日波动率小于3% | 1.0 |

## 使用示例

### 示例 1: 自然语言触发

```
用户: 帮我选几只低估值、有金叉信号的股票

Claude: 我来根据您的条件筛选股票。
[调用 screen CLI]

筛选条件: pe_low, pb_low, ma5_cross_ma20
找到 5 只符合条件的股票：

1. 平安银行 (000001) 得分 3.5
   匹配: 低估值, MA金叉

2. ...
```

### 示例 2: 斜杠命令

```
用户: /screen --limit 20

Claude:
选股结果 (共 20 只)
[结果列表...]
```

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/stock_picker/screener.py` - 选股器实现
- `src/python/astock/stock_picker/factors.py` - 因子定义

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| CLI 执行失败 | 重试1次，失败则减少因子数量重试 |
| 无匹配结果 | 扩大筛选范围或提示用户放宽条件 |
| 因子名称无效 | 列出可用因子，提示用户选择 |
| 数据源超时 | 使用缓存数据并标注 |