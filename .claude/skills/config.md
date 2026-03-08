# /config - 配置管理

管理用户偏好配置。

## 使用方式

```
/config show                    # 查看当前配置
/config set <key> <value>       # 设置配置项
/config style                   # 分析并学习交易风格
/config reset                   # 重置为默认配置
```

## 示例

```
/config show                           # 查看配置
/config set risk_level aggressive      # 设置风险偏好
/config set max_positions 5            # 设置最大持仓数
/config style                          # 学习交易风格
```

## 配置项

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| risk_level | 风险偏好 | conservative, moderate, aggressive |
| trading_style | 交易风格 | day_trading, swing, trend_following, value_investing |
| max_positions | 最大持仓数 | 1-20 |
| position_size | 单只仓位比例 | 0.05-0.3 |
| alert_channels | 提醒渠道 | terminal, system, wechat, dingtalk |
| min_price | 最低价格 | 数值 |
| max_price | 最高价格 | 数值 |
| default_capital | 默认资金 | 数值 |
| default_strategy | 默认策略 | ma_cross, macd |

## 交易风格学习

`/config style` 命令会分析您的历史交易记录，自动推断：
- 交易风格（日内/波段/趋势/价值）
- 风险偏好（保守/稳健/激进）
- 行业偏好

## 相关文件

- `src/ts/orchestrator/config-handler.ts`
- `src/python/astock/config/`
- `src/python/astock/learning/style_analyzer.py`
