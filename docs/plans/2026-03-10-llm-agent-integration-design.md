# LLM Agent 能力集成设计

## 概述

本文档描述如何为 A股 Agent Team 交易分析系统集成真正的 LLM Agent 能力，使其从规则引擎升级为智能分析系统。

## 背景

当前 `agent-team-handler.ts` 中的 "Agent Team" 实际上是确定性函数，使用固定的 if-else 逻辑生成分析结论。本次设计目标是引入 LLM，实现真正的智能推理和多专家协作。

## 需求总结

| 维度 | 选择 |
|------|------|
| 模型支持 | GPT-5.2、Kimi-K2.5、GLM-5（多模型切换） |
| API Key 配置 | 环境变量优先，fallback 配置文件 |
| Agent 调用模式 | 可配置（单 LLM 编排 / 多 LLM 并行） |
| 工具调用 | LLM 原生 Tool Use |
| 对话记忆 | 持久化记忆 + team-feedback 集成 |
| 降级策略 | 直接报错退出 |

## 技术选型

### 框架选择：LangChain

选择 LangChain 作为 Agent 框架，理由：
- 业界标准，社区活跃
- 内置多模型支持、工具调用、记忆管理
- LangGraph 支持多 Agent 编排
- 与现有 Python 层通过 Tools 集成，无需修改底层

### 依赖引入

```json
{
  "dependencies": {
    "@langchain/core": "^0.3.x",
    "@langchain/openai": "^0.3.x",
    "@langchain/community": "^0.3.x",
    "langchain": "^0.3.x",
    "@langchain/langgraph": "^0.2.x",
    "zod": "^3.x",
    "better-sqlite3": "^11.x"
  }
}
```

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI 入口层                             │
│  agent | config | sessions (新增) + 现有命令                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   配置系统 (Config Loader)                    │
│  多模型配置 | API Key 管理 | Agent 行为配置                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   模型网关 (Model Gateway)                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                │
│  │ ChatOpenAI│ │ ChatKimi  │ │ ChatGLM   │                │
│  │ (GPT-5.2) │ │(Kimi-K2.5)│ │ (GLM-5)   │                │
│  └───────────┘ └───────────┘ └───────────┘                │
│  统一 BaseChatModel 接口，OpenAI 兼容协议                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   Agent Runtime                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Single Agent    │    │ Multi Agent     │                │
│  │ (单LLM编排)     │    │ (LangGraph并行) │                │
│  │                 │    │                 │                │
│  │ 1个LLM调用      │    │ 5+个LLM调用     │                │
│  │ 低成本、快速    │    │ 高成本、深度    │                │
│  └─────────────────┘    └─────────────────┘                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   Tools Layer                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │QuoteTool │ │AnalyzeTool│ │ScreenTool│ │BacktestTool│     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  DynamicStructuredTool + Zod Schema                         │
│  ↓ 调用 python-bridge.ts                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ execa
┌──────────────────────────┴──────────────────────────────────┐
│                   Python 层 (现有，无需修改)                  │
│  quote | analysis | screen | backtest | monitor ...         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   记忆存储 (Memory Store)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SQLite (~/.astrack/data/memory.db)                  │   │
│  │ - conversations: 对话历史                           │   │
│  │ - sessions: 会话元数据                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ team-feedback 集成 (data/team-feedback.json)        │   │
│  │ - 用户反馈 → 长期偏好 → System Prompt 注入          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 模块详细设计

### 1. 模型网关层 (Model Gateway)

**文件**: `src/ts/llm/models/index.ts`

**职责**:
- 统一模型创建接口
- 支持多提供商配置
- OpenAI 兼容协议支持 Kimi 和 GLM

**关键代码**:
```typescript
export type ModelProvider = 'openai' | 'kimi' | 'glm';

export interface ModelConfig {
  provider: ModelProvider;
  model: string;
  apiKey: string;
  baseUrl?: string;
  temperature?: number;
  maxTokens?: number;
}

const MODEL_CONFIGS: Record<ModelProvider, { baseUrl?: string; defaultModel: string }> = {
  openai: { defaultModel: 'gpt-5.2' },
  kimi: { baseUrl: 'https://api.moonshot.cn/v1', defaultModel: 'moonshot-k2.5' },
  glm: { baseUrl: 'https://open.bigmodel.cn/api/paas/v4', defaultModel: 'glm-5' },
};

export function createChatModel(config: ModelConfig): BaseChatModel {
  const providerConfig = MODEL_CONFIGS[config.provider];
  return new ChatOpenAI({
    modelName: config.model || providerConfig.defaultModel,
    openAIApiKey: config.apiKey,
    configuration: { baseURL: config.baseUrl || providerConfig.baseUrl },
    temperature: config.temperature ?? 0.7,
    maxTokens: config.maxTokens ?? 4096,
  });
}
```

### 2. 工具层 (Tools Layer)

**文件**: `src/ts/llm/tools/index.ts`

**职责**:
- 封装 Python 层能力为 LangChain Tools
- 定义 Zod Schema 供 LLM 理解参数

**工具清单**:

| Tool | 调用时机 | Python 能力 |
|------|----------|-------------|
| `get_stock_quote` | 查询价格/行情 | `getQuote()` |
| `analyze_stock_technical` | 技术分析 | `analyzeStock()` |
| `screen_stocks` | 选股筛选 | `screenStocks()` |
| `backtest_strategy` | 策略回测 | `runBacktest()` |
| `get_user_style` | 用户风格 | `loadTeamFeedbackProfile()` |
| `record_feedback` | 记录反馈 | `appendTeamFeedback()` |

**示例**:
```typescript
export const quoteTool = new DynamicStructuredTool({
  name: 'get_stock_quote',
  description: '获取股票实时行情，包括价格、涨跌幅、成交量等。当用户询问股票价格或市场状态时调用。',
  schema: z.object({
    code: z.string().describe('6位股票代码，如 000001'),
  }),
  func: async ({ code }) => {
    const result = await getQuote(code);
    return JSON.stringify(result);
  },
});
```

### 3. Agent Runtime

**文件**: `src/ts/llm/agents/`

**职责**:
- 支持单 LLM 编排和多 LLM 并行两种模式
- 管理 Agent 执行生命周期

#### 3.1 单 LLM 编排模式（默认）

使用 `createToolCallingAgent` + `AgentExecutor`，System Prompt 中定义 6 个专家角色，一次 LLM 调用完成所有推理。

**优点**: 成本低、响应快
**缺点**: 专家独立性较弱

#### 3.2 多 LLM 并行模式（可选）

使用 `LangGraph` 编排多个专家节点并行执行，每个专家独立调用 LLM，最后由 Orchestrator 汇总。

**优点**: 专家真正独立推理，结论更全面
**缺点**: 成本高、响应慢

### 4. 记忆存储 (Memory Store)

**文件**: `src/ts/llm/memory/`

**职责**:
- 持久化对话历史
- 与 team-feedback 集成
- 支持长期偏好注入

**存储结构**:
```sql
-- 对话历史
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,  -- 'user' | 'assistant'
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT  -- JSON: { tools_used, stock_code, decision }
);

-- 会话元数据
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT  -- JSON: { stock_codes, decisions }
);
```

**team-feedback 集成**:
- 用户历史反馈转换为偏好画像
- 作为长期记忆注入 System Prompt
- Style Agent 可直接引用用户偏好

### 5. 配置系统

**文件**: `src/ts/config/`

**配置文件位置** (`~/.astrack/config.json`):
```json
{
  "llm": {
    "provider": "kimi",
    "model": "moonshot-k2.5",
    "temperature": 0.7,
    "mode": "single"
  },
  "apiKeys": {
    "openai": "${OPENAI_API_KEY}",
    "kimi": "${KIMI_API_KEY}",
    "glm": "${GLM_API_KEY}"
  },
  "agent": {
    "verbose": false,
    "maxIterations": 10,
    "timeoutMs": 60000
  },
  "memory": {
    "maxHistoryLength": 50,
    "enableLongTermMemory": true
  }
}
```

**环境变量优先级**:
1. 环境变量 `OPENAI_API_KEY` / `KIMI_API_KEY` / `GLM_API_KEY`
2. 配置文件中的 `apiKeys` 字段
3. 配置文件中的环境变量引用 `${VAR_NAME}`

### 6. CLI 集成

**新增命令**:

| 命令 | 说明 | 示例 |
|------|------|------|
| `agent <code>` | LLM Agent 分析 | `node dist/index.js agent 000001 -q "适合介入吗？"` |
| `config` | 配置管理 | `node dist/index.js config --show` |
| `sessions` | 会话管理 | `node dist/index.js sessions --list` |

**与现有命令的关系**:
- `team` 命令保持不变（规则引擎，无 LLM 调用）
- `agent` 命令为新增（LLM Agent，有 LLM 调用）

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| API Key 未配置 | 报错退出，提示配置方式 |
| API 调用超时 | 报错退出，提示稍后重试 |
| 配额用尽 | 报错退出，提示检查配额 |
| 模型返回格式错误 | 报错退出，记录原始响应 |
| Python 层错误 | Tool 内捕获，返回错误信息给 LLM |

## 测试策略

### 单元测试
- 配置加载器测试
- 工具 Schema 验证测试
- 记忆存储 CRUD 测试

### 集成测试
- 模型调用 Mock 测试
- Agent 执行流程测试
- Tool 调用链测试

### E2E 测试
- 使用 Mock LLM 验证完整流程
- 可选：真实 API 调用测试（CI 中跳过）

## 实现阶段

### Phase 1: 基础框架
- 引入 LangChain 依赖
- 实现模型网关层
- 实现配置系统
- 验证：能成功调用各模型 API

### Phase 2: 工具层
- 实现 Tools 封装
- 验证：Tool 能正确调用 Python 层

### Phase 3: Agent Runtime
- 实现单 LLM 编排模式
- 实现多 LLM 并行模式
- 验证：Agent 能自主调用工具并输出结论

### Phase 4: 记忆与集成
- 实现持久化记忆
- 集成 team-feedback
- 完善 CLI 命令
- 验证：多轮对话和长期记忆生效

## 文件结构

```
src/ts/
├── llm/                          # 新增目录
│   ├── models/
│   │   └── index.ts              # 模型网关
│   ├── tools/
│   │   └── index.ts              # Tools 定义
│   ├── agents/
│   │   ├── index.ts              # Agent 工厂
│   │   ├── single-agent.ts       # 单 LLM 模式
│   │   ├── multi-agent.ts        # 多 LLM 模式
│   │   └── prompts.ts            # System Prompts
│   └── memory/
│       ├── store.ts              # 持久化存储
│       ├── session.ts            # 会话管理
│       └── feedback-integration.ts
├── config/
│   ├── schema.ts                 # Zod Schema
│   └── loader.ts                 # 配置加载
├── orchestrator/                  # 现有目录，保持不变
└── index.ts                       # CLI 入口，扩展新命令
```

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| API 成本过高 | 默认使用单 LLM 模式，多 LLM 模式需显式开启 |
| 响应速度慢 | 设置合理 timeout，提示用户等待 |
| 模型幻觉 | Tool 调用结果为事实数据，减少幻觉可能 |
| API Key 泄露 | 环境变量优先，配置文件权限控制 |
