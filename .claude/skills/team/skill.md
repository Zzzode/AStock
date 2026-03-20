---
name: team
description: Use when user asks whether a stock is worth buying, selling, holding, or entering now, wants timing or position advice, or needs a multi-factor A-share decision with bull/bear arguments and risk assessment. Trigger on phrases like "适合买吗", "现在能不能买", "要不要卖", "怎么看仓位", or "综合分析下值不值得参与". Do not use for simple quote requests or pure technical-indicator interpretation when the user is not asking for a broader decision.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /team - 多专家协作分析

多专家 Agent 协作分析，综合市场、技术、策略、风险、风格五个维度，为用户生成交易决策建议。

> 边界说明：价格与行情快照问题优先使用 `/quote`，纯技术指标与走势研判优先使用 `/analyze`，本技能只用于买卖时机、持有判断、仓位建议和多维度综合决策。

## 自动触发模式

当用户输入匹配以下模式时，Claude Code 会自动识别并触发此 skill：

| 用户输入模式 | 触发条件 |
|-------------|---------|
| "平安银行现在适合买吗" | 包含股票名称/代码 + 交易决策问题 |
| "000001怎么操作" | 6位股票代码 + 操作建议请求 |
| "贵州茅台现在值得买入吗" | 买入时机判断 + 股票名称 |
| "茅台这只股票要不要止盈" | 卖出/止盈时机判断 |
| "现在能买平安银行吗" | 买入时机判断 |

## 执行流程

### Phase 1: 解析意图

首先从用户输入中提取：
- **股票代码**: 6位数字（如 000001）或股票名称（需转换为代码）
- **问题类型**: 买入时机/卖出时机/持仓判断/综合分析
- **分析深度**: 默认 120 天历史数据

如果用户未明确提供股票代码，使用 AskUserQuestion 工具询问。

### Phase 2: 数据收集

使用 Bash 工具并行调用 Python 获取数据：

```bash
# 获取实时行情
.venv/bin/python -m astock.cli quote 000001

# 获取技术分析
.venv/bin/python -m astock.cli analyze 000001 --days 120

# 策略筛选
.venv/bin/python -m astock.cli screen --codes 000001
```

### Phase 3: 加载用户画像

读取用户历史反馈画像：

```bash
cat data/team-feedback.json
```

如果文件不存在或为空，使用默认中性画像。

### Phase 4: 角色扮演分析

作为 Orchestrator，整合以下专家视角进行推理：

**Market Agent 视角**：
- 分析行情数据的短期动能
- 判断涨跌幅的市场含义
- 评估成交量的资金关注度

**Analysis Agent 视角**：
- 解读技术指标信号
- 识别金叉/死叉/超买/超卖状态
- 评估趋势强度

**Strategy Agent 视角**：
- 检查是否符合选股因子
- 评估策略匹配得分
- 判断策略层面的支持度

**Risk Agent 视角**：
- 识别当前风险等级（高/中/低）
- 评估 RSI、KDJ 指标的风险信号
- 计算潜在回撤风险

**Style Agent 视角**：
- 结合用户历史反馈偏好
- 调整建议的激进/保守程度
- 应用用户的风险偏好

### Phase 5: 综合决策

基于五维度分析，生成最终决策：

| 决策 | 条件 |
|------|------|
| **建议关注并分批试探** | 多数专家看多，风险可控，符合用户风格 |
| **建议等待更清晰信号** | 信号分歧较大，风险中等 |
| **建议观望或减仓控制风险** | 多数专家看空，风险偏高 |

### Phase 6: 输出结论

输出格式：

```
┌──────────────────────────────────────────────────────────────┐
│ Agent Team 综合结论                                           │
├──────────────────────────────────────────────────────────────┤
│ 标的: 000001   问题: 现在是否适合介入？                        │
│ 结论: 建议关注并分批试探                                       │
│ 置信度: 65%                                                   │
├──────────────────────────────────────────────────────────────┤
│ Market:   市场动能偏强，涨跌幅 +2.34%                         │
│ Analysis: 技术信号偏多（多头 3，空头 1）                        │
│ Strategy: 策略筛选通过，综合得分 78.5                         │
│ Risk:     风险中性（RSI6 58.2，KDJ-J 65.3）                   │
├──────────────────────────────────────────────────────────────┤
│ 风险提示:                                                     │
│ - 短期波动风险较高，追涨需谨慎                                  │
│ - 用户历史反馈偏谨慎，建议控制仓位                              │
└──────────────────────────────────────────────────────────────┘
```

## 交互示例

### 示例 1: 自然语言触发

```
用户: 平安银行现在适合买吗？

Claude: 我来为您进行多专家综合分析。
[调用 quote/analyze/screen CLI]
[读取用户画像]

根据多维度分析，平安银行(000001)当前：
- 市面动能偏强，今日涨跌幅 +2.34%
- 技术信号偏多，检测到 MA5 金叉 MA20
- 策略筛选得分 78.5，进入候选池
- 风险等级中等，RSI6 为 58.2

综合建议：建议关注并分批试探（置信度 65%）
```

### 示例 2: 明确代码

```
用户: 000001 现在能不能加仓？

Claude: 我来分析平安银行(000001)的加仓时机。
[执行分析流程]

当前不建议加仓，原因：
- 技术指标显示短期超买迹象
- 风险 Agent 提示回调风险
- 建议：等待更清晰信号
```

## 用户反馈闭环

分析完成后，询问用户反馈：

```
这个分析对您有帮助吗？您可以反馈：
- "执行后效果很好" - 会学习并增强此类建议
- "不太准确" - 会调整后续分析权重
```

使用 CLI 记录反馈：

```bash
.venv/bin/python -m astock.cli team-feedback 000001 --action watch_buy --outcome good --strategy ma_cross --note "执行后收益符合预期"
```

查看用户画像：

```bash
.venv/bin/python -m astock.cli feedback
.venv/bin/python -m astock.cli feedback 000001
```

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/analysis/` - Python 技术分析服务
- `src/python/astock/stock_picker/` - 选股器
- `data/team-feedback.json` - 用户反馈存储