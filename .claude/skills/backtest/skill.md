---
name: backtest
description: Use when user needs to backtest trading strategies, evaluate strategy performance, or analyze historical trading results
---

# /backtest - 策略回测

对交易策略进行历史回测，评估策略表现。

## 使用方式

```
/backtest <股票代码> --strategy <策略> [--start-date <日期>] [--end-date <日期>] [--capital <金额>]
```

## 示例

```
/backtest 000001 --strategy ma_cross                    # 使用 MA 均线交叉策略回测
/backtest 000001 --strategy macd                        # 使用 MACD 策略回测
/backtest 000001 --strategy ma_cross --start-date 2024-01-01 --end-date 2024-12-31
/backtest 000001 --strategy ma_cross --capital 100000   # 指定初始资金 10 万
```

## 可用策略

| 策略 | 名称 | 说明 |
|------|------|------|
| ma_cross | MA均线交叉 | 短期均线上穿长期均线买入，下穿卖出 |
| macd | MACD金叉死叉 | MACD柱状线由负转正买入，由正转负卖出 |

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| --strategy | 必填 | 策略名称 |
| --start-date | 一年前 | 回测开始日期 |
| --end-date | 今天 | 回测结束日期 |
| --capital | 100000 | 初始资金（元） |

## 输出格式

```
┌─────────────────────────────────────────┐
│        回测结果 - 平安银行 (000001)      │
├─────────────────────────────────────────┤
│  策略: MA均线交叉                        │
│  回测区间: 2024-01-01 ~ 2024-12-31      │
│                                         │
│  收益指标                               │
│  总收益率: +15.2%                       │
│  年化收益: +16.8%                       │
│  最大回撤: -8.3%                        │
│  夏普比率: 1.25                         │
│                                         │
│  交易统计                               │
│  交易次数: 12 次                        │
│  胜率: 58.3%                            │
│  盈亏比: 2.1                            │
│  手续费: 356.80 元                      │
├─────────────────────────────────────────┤
│  最近交易记录                           │
│  2024-12-15  买入  1000股  @10.50元     │
│  2024-12-20  卖出  1000股  @11.20元     │
└─────────────────────────────────────────┘
```

## 实现说明

调用 TypeScript 层的 `runBacktest()` 函数，该函数通过 Python 桥接获取历史数据并执行回测。

## 相关文件

- `src/ts/orchestrator/backtest-handler.ts` - 处理逻辑
- `src/ts/utils/python-bridge.ts` - Python 调用桥接
- `src/python/astock/backtest/` - Python 回测服务
