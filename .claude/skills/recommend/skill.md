---
name: recommend
description: Use when user needs personalized stock recommendations based on trading style, risk preference, investment strategy, or asks "推荐几只股票". Triggers on patterns like "给我推荐几只股票", "有什么好票推荐", "适合我的股票", "根据我的风格推荐" or when user wants personalized investment suggestions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /recommend - 个性化推荐

根据用户风格生成个性化股票推荐，结合历史反馈和偏好调整推荐结果。

## 自动触发模式

| 用户输入模式 | 触发条件 |
|-------------|---------|
| "给我推荐几只股票" | 推荐请求 |
| "有什么好票推荐" | 通用推荐请求 |
| "适合我风格的股票" | 个性化推荐 |
| "推荐一些适合波段交易的票" | 风格指定推荐 |

## 执行流程

### Step 1: 加载用户画像

读取用户历史反馈和风格配置：

```bash
cat data/team-feedback.json
cat data/config.json
```

从画像中提取：
- 交易风格（日内/波段/趋势/价值）
- 风险偏好（保守/稳健/激进）
- 历史偏好行业
- 策略权重

### Step 2: 调用 Python 生成推荐

使用 Bash 工具执行：

```bash
# 使用用户风格推荐
.venv/bin/python -m astock.cli recommend --limit 5

# 指定风格推荐
.venv/bin/python -m astock.cli recommend --style swing --limit 5
```

### Step 3: 解析推荐结果

从输出中提取推荐股票：
- 股票代码和名称
- 综合得分
- 风格匹配度
- 推荐策略

### Step 4: 输出推荐结果

```
个性化推荐 (基于您的交易风格: 波段交易)

代码     名称          得分    风格匹配  推荐策略
000001   平安银行      3.5     85%       波段交易, 回调买入
600519   贵州茅台      2.8     72%       波段交易, 趋势跟随
000858   五粮液        2.5     68%       波段交易, 突破买入

推荐理由:
1. 平安银行 (000001) - 技术面偏多，近期有金叉信号，适合波段操作
2. 贵州茅台 (600519) - 估值合理，趋势稳定，适合波段持有
3. 五粮液 (000858) - 成交量放大，有突破迹象，可关注
```

### Step 5: 补充说明（可选）

如果用户是新用户，提示风格学习：

```
提示: 系统正在学习您的交易风格。
反馈您的交易结果可以帮助系统提供更精准的推荐。
使用 /config style 可以重新分析您的交易风格。
```

## 推荐因子映射

系统根据用户交易风格自动选择合适的选股因子：

| 交易风格 | 重点因子 | 特点 |
|----------|----------|------|
| 日内交易 (day_trading) | 动量、波动率 | 高频、快进快出 |
| 波段交易 (swing) | 动量、质量、估值 | 中短期、趋势操作 |
| 趋势跟踪 (trend_following) | 动量、质量 | 跟随趋势、止损重要 |
| 价值投资 (value_investing) | 估值、质量 | 长期持有、安全边际 |

## 使用示例

### 示例 1: 自然语言触发

```
用户: 给我推荐几只适合波段交易的股票

Claude: 我来根据波段交易风格为您推荐股票。
[调用 recommend CLI]

波段交易推荐:

1. 平安银行 (000001) 得分 3.5
   风格匹配度: 85%
   推荐策略: 回调买入
   理由: 技术面偏多，有金叉信号，适合波段操作

2. ...
```

### 示例 2: 斜杠命令

```
用户: /recommend --limit 5

Claude:
个性化推荐 (基于您的交易风格: 波段交易)
[推荐列表...]
```

### 示例 3: 新用户

```
用户: 推荐几只股票

Claude: 我来为您生成股票推荐。
[检测到新用户]

您是新用户，系统将使用默认风格（稳健型）推荐。
您可以通过反馈交易结果来帮助系统学习您的偏好。

[推荐结果...]
```

## 相关文件

- `src/python/astock/cli.py` - Python CLI 入口
- `src/python/astock/recommend/recommender.py` - 推荐算法