# Skill Routing Design: quote / analyze / team

## Goal

Reduce trigger overlap among the three highest-traffic stock skills so routing is more stable, cheaper, and easier to predict.

## Current problems

1. `team` is too broad and overlaps with both `quote` and `analyze`.
2. `analyze` currently captures generic prompts like “分析一下XX”, which also match comprehensive decision requests.
3. `quote` includes vague prompts like “现在怎么样”, which can mean price, technical trend, or buy/sell judgment.

## Recommended boundary

### `quote`
Use only for real-time market snapshot requests:
- latest price
- intraday change
- volume / turnover
- today’s performance
- simple market status questions clearly tied to price action

Do not use it for:
- technical indicator interpretation
- buy/sell decisions
- multi-factor investment judgment

Exact description replacement:
> Use when user asks for a stock’s latest price, intraday change, volume, turnover, today’s performance, or a current market snapshot. Trigger on phrases like “现在多少钱”, “最新价”, “今日涨跌”, “行情”, “成交额”, or “今天涨了吗”. Do not use for technical analysis, indicator interpretation, or buy/sell decision questions.

### `analyze`
Use only for technical analysis requests:
- MA / MACD / KDJ / RSI
- golden cross / death cross
- overbought / oversold
- trend strength / structure
- technical buy/sell signals

Do not use it for:
- simple price lookup
- comprehensive investment decisions involving multiple perspectives
- portfolio or position-sizing advice

Exact description replacement:
> Use when user asks for technical analysis of a stock, including MA, MACD, KDJ, RSI, golden cross, death cross, trend strength, support/resistance, or technical entry/exit signals from a chart perspective. Trigger on phrases like “技术分析”, “分析一下XX”, “均线”, “MACD”, “RSI”, “金叉”, “死叉”, or “趋势怎么看”. Do not use for simple price lookup or broader buy/sell decision advice involving position sizing or multi-factor judgment.

### `team`
Use only for comprehensive decision support:
- whether a stock is worth buying or selling now
- entry / exit timing from a decision perspective
- position sizing
- multi-factor judgment
- pros vs cons / bull vs bear case
- cross-discipline A-share analysis

Do not use it for:
- simple quote requests
- pure technical indicator interpretation unless the user clearly wants a broader decision

Exact description replacement:
> Use when user asks whether a stock is worth buying, selling, holding, or entering now, wants timing or position advice, or needs a multi-factor A-share decision with bull/bear arguments and risk assessment. Trigger on phrases like “适合买吗”, “现在能不能买”, “要不要卖”, “怎么看仓位”, or “综合分析下值不值得参与”. Do not use for simple quote requests or pure technical-indicator interpretation when the user is not asking for a broader decision.

## Ambiguous phrasing policy

- “分析一下XX” defaults to `analyze`, because it is the least expensive interpretation and most naturally maps to technical analysis.
- “XX现在怎么样” is too ambiguous to be a trigger example in any of the three skills. It should be removed from all three descriptions and example trigger lists. If the user only says this, the assistant should clarify whether they want行情、技术面，还是买卖判断。

## Editing plan

1. Update frontmatter `description` in `quote`, `analyze`, and `team` to reflect the new boundaries.
2. Tighten the body examples and auto-trigger patterns so they reinforce the same split.
3. Remove “分析一下XX” from `team` and keep it as an `analyze` pattern.
4. Remove “XX现在怎么样” from `quote`, `analyze`, and `team`, because it is ambiguous and should lead to clarification instead of direct routing.
5. Keep wording natural and close to real user phrasing.

## Intended result

- `quote` handles market snapshot questions.
- `analyze` handles technical-analysis questions.
- `team` handles decision-oriented comprehensive analysis.
- Fewer false triggers, lower routing ambiguity, and more consistent behavior.
