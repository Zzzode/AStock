# /watch - 股票监控管理

管理股票监控列表，支持添加、移除和查看监控项。

## 使用方式

```
/watch <command> [options]
```

## 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 添加监控 | `/watch add 000001 --cond "price>10"` |
| `remove` | 移除监控 | `/watch remove 000001` |
| `list` | 查看监控列表 | `/watch list` |

## 示例

### 添加监控

```
/watch add 000001                    # 添加平安银行到监控列表
/watch add 600519 --cond "price>1800"  # 添加贵州茅台，监控价格突破1800
/watch add 000858 --cond "change_percent>5"  # 添加五粮液，监控涨幅超过5%
```

### 移除监控

```
/watch remove 000001    # 移除平安银行的监控
/watch remove 600519    # 移除贵州茅台的监控
```

### 查看监控列表

```
/watch list    # 显示当前所有监控项
```

## 监控条件说明

支持以下监控条件（`--cond` 参数）：

| 条件 | 说明 | 示例 |
|------|------|------|
| `price>X` | 价格超过 X | `--cond "price>100"` |
| `price<X` | 价格低于 X | `--cond "price<50"` |
| `change_percent>X` | 涨幅超过 X% | `--cond "change_percent>5"` |
| `change_percent<X` | 跌幅超过 X% | `--cond "change_percent<-3"` |
| `volume>X` | 成交量超过 X | `--cond "volume>1000000"` |

可以组合多个条件（逗号分隔）：

```
/watch add 000001 --cond "price>10,change_percent>3"
```

## 提醒渠道

监控触发时可通过以下渠道提醒：

- `terminal` - 终端输出（默认）
- `notify` - 系统通知

```
/watch add 000001 --channel terminal --channel notify
```

## 输出格式

### 添加监控成功

```
已添加监控: 平安银行 (000001)
  条件: 价格 > 10.00
  提醒: 终端
```

### 监控列表

```
当前监控列表 (3项)
┌──────────────────────────────────────────────────────────────┐
│  代码     名称          条件                    状态        │
├──────────────────────────────────────────────────────────────┤
│  000001   平安银行      price>10               启用         │
│  600519   贵州茅台      change_percent>5       启用         │
│  000858   五粮液        price>150,volume>1M    启用         │
└──────────────────────────────────────────────────────────────┘
```

## 实现说明

调用 TypeScript 层的 `handleWatch()` 函数，该函数通过 Python 桥接调用监控管理 CLI。

## 相关文件

- `src/ts/orchestrator/watch-handler.ts` - 处理逻辑
- `src/ts/utils/python-bridge.ts` - Python 调用桥接
- `src/python/astock/monitor/watch_cli.py` - Python 监控管理 CLI
- `src/python/astock/storage/models.py` - 数据模型 (WatchItem)
