# A股交易策略分析工具

基于 Agent Skills 的多 Agent A股交易策略分析工具。

## 快速开始

```bash
# 安装依赖
npm install
pip install -e src/python

# 初始化数据库
npm run init-db

# 使用 Skills
/quote 000001      # 查询平安银行行情
/analyze 000001    # 分析技术指标
/style
```

## Claude Code 运行方式

1) 打开 Claude Code
2) 通过斜杠命令调用 Skills
3) 关注输出中的多 Agent 观点与综合结论

## Skills

| Skill | 功能 | 示例 |
|-------|------|------|
| /quote | 实时行情查询 | `/quote 000001` |
| /analyze | 技术分析 | `/analyze 000001` |
| /screen | 智能选股 | `/screen --limit 10` |
| /backtest | 策略回测 | `/backtest 000001 --strategy ma_cross` |
| /recommend | 个性化推荐 | `/recommend` |
| /watch | 监控管理 | `/watch list` |
| /alert | 监控告警 | `/alert status` |
| /config | 配置管理 | `/config show` |
| /style | 交易风格学习 | `/style` |

## 项目结构

```
src/
├── ts/           # TypeScript 应用层
└── python/       # Python 数据层
```

## 开发规范

- TypeScript 代码放在 `src/ts/`
- Python 代码放在 `src/python/astock/`
- 测试与源码同级 `__tests__/` 目录
