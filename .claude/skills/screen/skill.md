---
name: screen
description: Use when user needs to screen or filter stocks based on technical indicators, valuation factors, or custom criteria
---

# /screen - 股票选股

根据技术指标因子筛选符合条件的股票。

## 使用方式

```
/screen [factors] [--limit N]
```

## 示例

```
/screen                           # 使用所有因子选股，返回前10只
/screen ma20_above,high_volume    # 使用指定因子选股
/screen --limit 20                # 返回前20只股票
/screen pe_low,pb_low --limit 30  # 低估值因子选股，返回前30只
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

## 输出格式

```
┌──────────────────────────────────────────────────────────┐
│                    选股结果 (共 10 只)                    │
├──────────────────────────────────────────────────────────┤
│  排名  代码      名称        得分    匹配因子              │
│   1   000001   平安银行     4.5    ma20_above,ma5_cross   │
│   2   600519   贵州茅台     3.0    pe_low,pb_low          │
│   ...                                                    │
└──────────────────────────────────────────────────────────┘
```

## 实现说明

1. 调用 TypeScript 层的 `handleScreen()` 函数
2. 该函数通过 Python 桥接调用 StockScreener 执行选股
3. 选股结果按综合得分降序排列

## 相关文件

- `src/ts/orchestrator/screen-handler.ts` - 处理逻辑
- `src/ts/utils/python-bridge.ts` - Python 调用桥接
- `src/python/astock/stock_picker/screener.py` - 选股器实现
- `src/python/astock/stock_picker/factors.py` - 因子定义
