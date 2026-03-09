# Claude Code 运行形态设计 - 多 Agent 技能架构

## 项目概述

本设计将仓库运行形态明确为 **Claude Code 内运行**，用户通过 Claude Code 启动并调用 Skills 来完成行情查询、技术分析、策略回测、监控告警与风格学习。Python 层只提供确定性能力服务，Agent 协作与决策由 Claude Code Skill 体系驱动。

## 目标与边界

### 目标

- Claude Code 是唯一交互入口
- Skill 驱动多 Agent 协作输出
- Python 层作为能力插件，可被 Skills 调用
- 风格画像持续学习并影响最终决策

### 非目标

- 不提供额外 Web UI/本地 UI
- 不要求 Python 层实现 Agent 自身协作

## 运行形态

```
用户进入 Claude Code
  └─ /quote /analyze /backtest /style 等 Skills
      ├─ Market Agent / Analysis Agent / Style Agent / Orchestrator
      └─ 调用 Python 能力层（CLI / API）
```

## 架构方案

采用 **Skill 中心化架构**，Skill 作为唯一入口，Agent 协作由 Skill 内协议与提示词定义，Python 层只负责能力输出。

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skills                   │
├─────────────────────────────────────────────────────────┤
│  /quote  /analyze  /screen  /backtest  /style  /alert    │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│                Multi-Agent 协作层                       │
│  Market Agent | Analysis Agent | Style Agent | Orchestrator
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│                Python 能力层（确定性）                  │
│  行情获取 | 技术指标 | 选股 | 回测 | 风格统计            │
└─────────────────────────────────────────────────────────┘
```

## 组件与数据流

### 组件

- Skill 层：定义输入输出协议与 agent 角色分工
- Agent 协作层：协调多视角输出并综合结论
- Python 能力层：提供结构化数据与可验证计算
- 本地存储：用于缓存与风格画像长期学习

### 数据流

1. 用户输入 `/analyze 000001`
2. Claude Code Skill 解析意图并分发给 Analysis Agent
3. Analysis Agent 调用 Python 技术分析能力
4. Python 返回结构化指标与信号
5. Orchestrator 汇总多 agent 观点并输出建议

## Skill 协议规范

每个 Skill 需满足：

- 输入参数标准化
- 输出结构包含：结论、信号、置信度、建议
- 对错误场景给出可操作提示

## 错误处理与可靠性

- Python 层统一返回结构化错误（code/message/context）
- Skill 输出必须包含可解释失败原因与可替代建议
- 多 agent 输出冲突时必须标明矛盾点与置信度
- 风格学习样本不足时必须提示“置信度低”

## 测试与验收标准

### 能力层验收

- /quote、/analyze、/backtest 返回结构化结果
- 风格画像能更新并持久化

### Skill 验收

- 输入错误可被优雅处理
- 输出包含统一结构与 agent 角色标记

### 协作验收

- Orchestrator 能综合多 agent 结论
- 风格画像对推荐策略产生可见影响

## 落地步骤

1. 统一 Skill 输入输出协议与角色提示词
2. 固化 Python 能力输出格式与错误结构
3. 建立风格画像的持久化与更新机制
4. 为每个 Skill 编写协作验收用例

## 验收示例

- `/quote 000001` → 行情数据
- `/analyze 000001` → 技术信号与结论
- `/backtest 000001 --strategy ma_cross` → 回测结果
- `/style` → 风格画像更新摘要
- Orchestrator 输出综合建议
