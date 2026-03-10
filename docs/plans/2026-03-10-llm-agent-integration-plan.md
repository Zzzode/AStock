# LLM Agent 能力集成实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 A股 Agent Team 集成真正的 LLM Agent 能力，支持 GPT-5.2、Kimi-K2.5、GLM-5 多模型切换。

**Architecture:** 基于 LangChain 构建 Agent Runtime，通过 DynamicStructuredTool 封装现有 Python 层能力，使用 SQLite 持久化对话记忆并与 team-feedback 集成。

**Tech Stack:** LangChain, @langchain/openai, @langchain/langgraph, Zod, better-sqlite3

---

## Phase 1: 依赖与配置系统

### Task 1: 安装 LangChain 依赖

**Files:**
- Modify: `package.json`

**Step 1: 添加 LangChain 依赖**

```bash
pnpm add @langchain/core @langchain/openai @langchain/community langchain @langchain/langgraph zod better-sqlite3
pnpm add -D @types/better-sqlite3
```

**Step 2: 验证安装**

Run: `pnpm install`
Expected: 成功安装所有依赖

**Step 3: Commit**

```bash
git add package.json pnpm-lock.yaml
git commit -m "feat: add LangChain and related dependencies"
```

---

### Task 2: 创建配置 Schema

**Files:**
- Create: `src/ts/config/schema.ts`

**Step 1: 编写配置 Schema**

```typescript
// src/ts/config/schema.ts
import { z } from 'zod';

export const AstockConfigSchema = z.object({
  llm: z.object({
    provider: z.enum(['openai', 'kimi', 'glm']).default('kimi'),
    model: z.string().optional(),
    temperature: z.number().min(0).max(2).default(0.7),
    maxTokens: z.number().min(1).max(32000).default(4096),
    mode: z.enum(['single', 'multi']).default('single'),
  }).default({}),

  apiKeys: z.object({
    openai: z.string().optional(),
    kimi: z.string().optional(),
    glm: z.string().optional(),
  }).optional(),

  agent: z.object({
    verbose: z.boolean().default(false),
    maxIterations: z.number().default(10),
    timeoutMs: z.number().default(60000),
  }).default({}),

  memory: z.object({
    maxHistoryLength: z.number().default(50),
    enableLongTermMemory: z.boolean().default(true),
  }).default({}),
});

export type AstockConfig = z.infer<typeof AstockConfigSchema>;
```

**Step 2: 验证 TypeScript 编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/config/schema.ts
git commit -m "feat: add config schema with Zod"
```

---

### Task 3: 创建配置加载器

**Files:**
- Create: `src/ts/config/loader.ts`
- Create: `src/ts/config/__tests__/loader.test.ts`

**Step 1: 编写测试**

```typescript
// src/ts/config/__tests__/loader.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import { loadConfig, CONFIG_PATHS } from '../loader.js';

const TEST_CONFIG_DIR = '/tmp/astock-test-config';

describe('loadConfig', () => {
  beforeEach(() => {
    process.env.OPENAI_API_KEY = 'test-openai-key';
    process.env.KIMI_API_KEY = 'test-kimi-key';
    process.env.GLM_API_KEY = 'test-glm-key';
  });

  afterEach(() => {
    delete process.env.OPENAI_API_KEY;
    delete process.env.KIMI_API_KEY;
    delete process.env.GLM_API_KEY;
  });

  it('should return default config when no config file exists', async () => {
    const config = await loadConfig();
    expect(config.llm.provider).toBe('kimi');
    expect(config.llm.mode).toBe('single');
  });

  it('should load API keys from environment variables', async () => {
    const config = await loadConfig();
    expect(config.apiKeys?.openai).toBe('test-openai-key');
    expect(config.apiKeys?.kimi).toBe('test-kimi-key');
    expect(config.apiKeys?.glm).toBe('test-glm-key');
  });

  it('should validate config schema', async () => {
    process.env.OPENAI_API_KEY = 'valid-key';
    const config = await loadConfig();
    expect(config.llm.temperature).toBeGreaterThanOrEqual(0);
    expect(config.llm.temperature).toBeLessThanOrEqual(2);
  });
});
```

**Step 2: 运行测试验证失败**

Run: `pnpm test src/ts/config/__tests__/loader.test.ts`
Expected: FAIL - loader 模块不存在

**Step 3: 实现配置加载器**

```typescript
// src/ts/config/loader.ts
import fs from 'fs';
import path from 'path';
import { AstockConfig, AstockConfigSchema } from './schema.js';

export const CONFIG_PATHS = [
  path.join(process.env.HOME || '', '.astock', 'config.json'),
  path.join(process.cwd(), '.astrockrc'),
  path.join(process.cwd(), 'astock.config.json'),
];

export async function loadConfig(): Promise<AstockConfig> {
  let fileConfig: Record<string, unknown> = {};

  for (const configPath of CONFIG_PATHS) {
    if (fs.existsSync(configPath)) {
      try {
        const content = fs.readFileSync(configPath, 'utf-8');
        fileConfig = JSON.parse(resolveEnvVars(content));
        break;
      } catch (error) {
        console.warn(`Failed to load config from ${configPath}:`, error);
      }
    }
  }

  const envConfig: Partial<AstockConfig> = {
    apiKeys: {
      openai: process.env.OPENAI_API_KEY || fileConfig.apiKeys?.openai as string | undefined,
      kimi: process.env.KIMI_API_KEY || process.env.MOONSHOT_API_KEY || fileConfig.apiKeys?.kimi as string | undefined,
      glm: process.env.GLM_API_KEY || process.env.ZHIPU_API_KEY || fileConfig.apiKeys?.glm as string | undefined,
    },
  };

  const merged = deepMerge(fileConfig, envConfig) as AstockConfig;
  return AstockConfigSchema.parse(merged);
}

function resolveEnvVars(content: string): string {
  return content.replace(/\$\{(\w+)\}/g, (_, name) => process.env[name] || '');
}

function deepMerge<T extends Record<string, unknown>>(base: T, override: Partial<T>): T {
  const result = { ...base } as T;
  for (const key in override) {
    if (override[key] !== undefined) {
      if (
        typeof override[key] === 'object' &&
        override[key] !== null &&
        !Array.isArray(override[key]) &&
        typeof base[key] === 'object' &&
        base[key] !== null
      ) {
        result[key] = deepMerge(
          base[key] as Record<string, unknown>,
          override[key] as Record<string, unknown>
        ) as T[Extract<keyof T, string>];
      } else {
        result[key] = override[key] as T[Extract<keyof T, string>];
      }
    }
  }
  return result;
}
```

**Step 4: 运行测试验证通过**

Run: `pnpm test src/ts/config/__tests__/loader.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ts/config/loader.ts src/ts/config/__tests__/loader.test.ts
git commit -m "feat: add config loader with env var support"
```

---

### Task 4: 创建 config index 导出

**Files:**
- Create: `src/ts/config/index.ts`

**Step 1: 创建导出文件**

```typescript
// src/ts/config/index.ts
export { loadConfig, CONFIG_PATHS } from './loader.js';
export { AstockConfigSchema, type AstockConfig } from './schema.js';
```

**Step 2: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/config/index.ts
git commit -m "feat: add config module exports"
```

---

## Phase 2: 模型网关层

### Task 5: 创建模型网关

**Files:**
- Create: `src/ts/llm/models/index.ts`
- Create: `src/ts/llm/models/__tests__/models.test.ts`

**Step 1: 编写测试**

```typescript
// src/ts/llm/models/__tests__/models.test.ts
import { describe, it, expect } from 'vitest';
import { createChatModel, MODEL_CONFIGS, type ModelProvider, type ModelConfig } from '../index.js';

describe('createChatModel', () => {
  it('should create OpenAI model with correct config', () => {
    const config: ModelConfig = {
      provider: 'openai',
      model: 'gpt-5.2',
      apiKey: 'test-key',
    };
    const model = createChatModel(config);
    expect(model).toBeDefined();
    expect(model.lc_namespace).toContain('langchain');
  });

  it('should create Kimi model with correct base URL', () => {
    const config: ModelConfig = {
      provider: 'kimi',
      model: 'moonshot-k2.5',
      apiKey: 'test-key',
    };
    const model = createChatModel(config);
    expect(model).toBeDefined();
  });

  it('should create GLM model with correct base URL', () => {
    const config: ModelConfig = {
      provider: 'glm',
      model: 'glm-5',
      apiKey: 'test-key',
    };
    const model = createChatModel(config);
    expect(model).toBeDefined();
  });

  it('should use default model when not specified', () => {
    const config: ModelConfig = {
      provider: 'openai',
      apiKey: 'test-key',
    };
    const model = createChatModel(config);
    expect(model).toBeDefined();
  });
});

describe('MODEL_CONFIGS', () => {
  it('should have config for all providers', () => {
    const providers: ModelProvider[] = ['openai', 'kimi', 'glm'];
    providers.forEach((provider) => {
      expect(MODEL_CONFIGS[provider]).toBeDefined();
      expect(MODEL_CONFIGS[provider].defaultModel).toBeDefined();
    });
  });

  it('should have base URL for Kimi and GLM', () => {
    expect(MODEL_CONFIGS.kimi.baseUrl).toBe('https://api.moonshot.cn/v1');
    expect(MODEL_CONFIGS.glm.baseUrl).toBe('https://open.bigmodel.cn/api/paas/v4');
  });
});
```

**Step 2: 运行测试验证失败**

Run: `pnpm test src/ts/llm/models/__tests__/models.test.ts`
Expected: FAIL - 模块不存在

**Step 3: 实现模型网关**

```typescript
// src/ts/llm/models/index.ts
import { ChatOpenAI } from '@langchain/openai';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';

export type ModelProvider = 'openai' | 'kimi' | 'glm';

export interface ModelConfig {
  provider: ModelProvider;
  model?: string;
  apiKey: string;
  baseUrl?: string;
  temperature?: number;
  maxTokens?: number;
}

export const MODEL_CONFIGS: Record<ModelProvider, { baseUrl?: string; defaultModel: string }> = {
  openai: { defaultModel: 'gpt-5.2' },
  kimi: {
    baseUrl: 'https://api.moonshot.cn/v1',
    defaultModel: 'moonshot-k2.5',
  },
  glm: {
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    defaultModel: 'glm-5',
  },
};

export function createChatModel(config: ModelConfig): BaseChatModel {
  const providerConfig = MODEL_CONFIGS[config.provider];
  const modelName = config.model || providerConfig.defaultModel;
  const baseURL = config.baseUrl || providerConfig.baseUrl;

  return new ChatOpenAI({
    modelName,
    openAIApiKey: config.apiKey,
    configuration: baseURL ? { baseURL } : undefined,
    temperature: config.temperature ?? 0.7,
    maxTokens: config.maxTokens ?? 4096,
  });
}
```

**Step 4: 运行测试验证通过**

Run: `pnpm test src/ts/llm/models/__tests__/models.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ts/llm/models/index.ts src/ts/llm/models/__tests__/models.test.ts
git commit -m "feat: add model gateway for multi-provider support"
```

---

## Phase 3: 工具层

### Task 6: 创建基础工具定义

**Files:**
- Create: `src/ts/llm/tools/index.ts`

**Step 1: 创建工具定义**

```typescript
// src/ts/llm/tools/index.ts
import { DynamicStructuredTool } from '@langchain/core/tools';
import { z } from 'zod';
import {
  getQuote,
  analyzeStock,
  screenStocks,
  runBacktest,
} from '../../utils/python-bridge.js';

// 行情查询工具
export const quoteTool = new DynamicStructuredTool({
  name: 'get_stock_quote',
  description:
    '获取股票实时行情，包括价格、涨跌幅、成交量等。当用户询问股票价格或市场状态时调用。',
  schema: z.object({
    code: z.string().describe('6位股票代码，如 000001'),
  }),
  func: async ({ code }) => {
    const result = await getQuote(code);
    return JSON.stringify(result);
  },
});

// 技术分析工具
export const analyzeTool = new DynamicStructuredTool({
  name: 'analyze_stock_technical',
  description:
    '对股票进行技术分析，包括MA均线、MACD、KDJ、RSI等指标。当用户需要技术面分析时调用。',
  schema: z.object({
    code: z.string().describe('6位股票代码'),
    days: z.number().optional().default(120).describe('分析周期天数'),
  }),
  func: async ({ code, days }) => {
    const result = await analyzeStock(code, days);
    return JSON.stringify(result);
  },
});

// 智能选股工具
export const screenTool = new DynamicStructuredTool({
  name: 'screen_stocks',
  description:
    '根据技术指标条件筛选股票。当用户需要选股或查找符合条件的股票时调用。',
  schema: z.object({
    limit: z.number().optional().default(10).describe('返回数量限制'),
    codes: z.array(z.string()).optional().describe('指定筛选范围，不填则全市场'),
  }),
  func: async ({ limit, codes }) => {
    const result = await screenStocks(undefined, limit, codes);
    return JSON.stringify(result);
  },
});

// 策略回测工具
export const backtestTool = new DynamicStructuredTool({
  name: 'backtest_strategy',
  description:
    '对股票进行策略回测，评估历史表现。当用户需要验证策略或了解历史收益时调用。',
  schema: z.object({
    code: z.string().describe('股票代码'),
    strategy: z
      .enum(['ma_cross', 'macd_cross', 'rsi_reversal'])
      .describe('策略类型'),
  }),
  func: async ({ code, strategy }) => {
    const result = await runBacktest(code, strategy);
    return JSON.stringify(result);
  },
});

// 用户风格获取工具
export const getUserStyleTool = new DynamicStructuredTool({
  name: 'get_user_style',
  description: '获取用户的历史交易风格和偏好。在给出个性化建议前调用。',
  schema: z.object({
    code: z.string().optional().describe('股票代码，获取该标的级别偏好'),
  }),
  func: async ({ code }) => {
    const { loadTeamFeedbackProfile, loadGlobalFeedbackProfile } = await import(
      '../../orchestrator/team-feedback-store.js'
    );
    const global = await loadGlobalFeedbackProfile();
    const stock = code ? await loadTeamFeedbackProfile(code) : null;
    return JSON.stringify({ global, stock });
  },
});

// 反馈记录工具
export const recordFeedbackTool = new DynamicStructuredTool({
  name: 'record_feedback',
  description: '记录用户对分析结果的反馈。在用户表达满意或不满意时调用。',
  schema: z.object({
    code: z.string().describe('股票代码'),
    action: z.enum(['watch_buy', 'wait', 'hold_or_reduce']).describe('建议操作'),
    outcome: z.enum(['good', 'bad', 'neutral']).describe('结果评价'),
    strategy: z.string().optional().describe('涉及策略'),
    notes: z.string().optional().describe('用户备注'),
  }),
  func: async ({ code, action, outcome, strategy, notes }) => {
    const { appendTeamFeedback } = await import(
      '../../orchestrator/team-feedback-store.js'
    );
    await appendTeamFeedback({
      code,
      action,
      outcome,
      strategy: strategy || 'unknown',
      notes: notes || '',
    });
    return JSON.stringify({ success: true, message: '反馈已记录' });
  },
});

// 导出所有工具
export const allTools = [
  quoteTool,
  analyzeTool,
  screenTool,
  backtestTool,
  getUserStyleTool,
  recordFeedbackTool,
];
```

**Step 2: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/llm/tools/index.ts
git commit -m "feat: add LangChain tools for Python layer integration"
```

---

### Task 7: 编写工具测试

**Files:**
- Create: `src/ts/llm/tools/__tests__/tools.test.ts`

**Step 1: 编写测试**

```typescript
// src/ts/llm/tools/__tests__/tools.test.ts
import { describe, it, expect } from 'vitest';
import {
  quoteTool,
  analyzeTool,
  screenTool,
  backtestTool,
  getUserStyleTool,
  recordFeedbackTool,
  allTools,
} from '../index.js';

describe('Tools', () => {
  it('should have correct tool names', () => {
    expect(quoteTool.name).toBe('get_stock_quote');
    expect(analyzeTool.name).toBe('analyze_stock_technical');
    expect(screenTool.name).toBe('screen_stocks');
    expect(backtestTool.name).toBe('backtest_strategy');
    expect(getUserStyleTool.name).toBe('get_user_style');
    expect(recordFeedbackTool.name).toBe('record_feedback');
  });

  it('should have descriptions for all tools', () => {
    allTools.forEach((tool) => {
      expect(tool.description).toBeTruthy();
      expect(tool.description.length).toBeGreaterThan(10);
    });
  });

  it('should have valid Zod schemas', () => {
    allTools.forEach((tool) => {
      expect(tool.schema).toBeDefined();
    });
  });

  it('should export exactly 6 tools', () => {
    expect(allTools.length).toBe(6);
  });
});
```

**Step 2: 运行测试**

Run: `pnpm test src/ts/llm/tools/__tests__/tools.test.ts`
Expected: PASS

**Step 3: Commit**

```bash
git add src/ts/llm/tools/__tests__/tools.test.ts
git commit -m "test: add tool definition tests"
```

---

## Phase 4: Agent Runtime

### Task 8: 创建 Agent Prompts

**Files:**
- Create: `src/ts/llm/agents/prompts.ts`

**Step 1: 编写 Prompt 定义**

```typescript
// src/ts/llm/agents/prompts.ts
import { ChatPromptTemplate, MessagesPlaceholder } from '@langchain/core/prompts';

export const EXPERT_ROLES_PROMPT = `你是 A 股交易分析团队的主控调度官，负责协调以下专家进行股票分析：

## 专家团队

### Market Agent（行情专家）
- 职责：解读实时行情数据，判断市场动能和资金流向
- 输出：涨跌原因、短期趋势判断

### Analysis Agent（技术专家）
- 职责：分析技术指标（MA/MACD/KDJ/RSI），识别买卖信号
- 输出：技术面结论、支撑压力位

### Strategy Agent（策略专家）
- 职责：评估策略匹配度，提供回测数据支撑
- 输出：策略推荐、历史胜率

### Risk Agent（风控专家）
- 职责：评估风险暴露，给出仓位和止损建议
- 输出：风险等级、仓位建议

### Style Agent（风格顾问）
- 职责：结合用户历史偏好，提供个性化建议
- 输出：风格匹配度、个性化调整

## 工作流程

1. 接收用户问题，判断需要哪些专家参与
2. 调用相应工具获取数据
3. 以各专家视角进行分析
4. 整合观点，输出综合建议

## 输出格式

每次回复必须包含：
- **综合结论**：买入/观望/减仓
- **专家观点**：各专家的独立分析
- **风险提示**：关键风险点
- **反方观点**：不看好的理由（如有）

## 语言要求

始终使用中文回复用户。`;

export function createAgentPrompt() {
  return ChatPromptTemplate.fromMessages([
    ['system', EXPERT_ROLES_PROMPT],
    new MessagesPlaceholder('chat_history'),
    ['human', '{input}'],
    new MessagesPlaceholder('agent_scratchpad'),
  ]);
}

// 多 Agent 模式的专家专用 Prompt
export const MARKET_EXPERT_PROMPT = `你是 Market Agent（行情专家）。
你的职责是解读实时行情数据，判断市场动能和资金流向。
你需要：
1. 调用 get_stock_quote 获取行情数据
2. 分析涨跌幅、成交量、换手率等指标
3. 输出简洁的行情解读和趋势判断
始终使用中文回复。`;

export const ANALYSIS_EXPERT_PROMPT = `你是 Analysis Agent（技术专家）。
你的职责是分析技术指标（MA/MACD/KDJ/RSI），识别买卖信号。
你需要：
1. 调用 analyze_stock_technical 获取技术分析结果
2. 解读各指标含义和信号
3. 输出技术面结论和支撑压力位
始终使用中文回复。`;

export const STRATEGY_EXPERT_PROMPT = `你是 Strategy Agent（策略专家）。
你的职责是评估策略匹配度，提供回测数据支撑。
你需要：
1. 调用 backtest_strategy 获取回测数据（如适用）
2. 评估当前形态与历史策略的匹配度
3. 输出策略推荐和预期表现
始终使用中文回复。`;

export const RISK_EXPERT_PROMPT = `你是 Risk Agent（风控专家）。
你的职责是评估风险暴露，给出仓位和止损建议。
你需要：
1. 综合行情和技术分析结果
2. 评估潜在风险点
3. 输出风险等级和仓位建议
始终使用中文回复。`;

export const ORCHESTRATOR_PROMPT = `你是 Orchestrator Agent（主控调度官）。
你的职责是整合各专家观点，输出最终决策建议。
你需要：
1. 综合各专家的分析结果
2. 处理观点冲突，给出权衡建议
3. 输出综合结论、风险提示和反方观点
始终使用中文回复。`;
```

**Step 2: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/llm/agents/prompts.ts
git commit -m "feat: add agent system prompts"
```

---

### Task 9: 创建单 LLM Agent

**Files:**
- Create: `src/ts/llm/agents/single-agent.ts`
- Create: `src/ts/llm/agents/__tests__/single-agent.test.ts`

**Step 1: 编写测试**

```typescript
// src/ts/llm/agents/__tests__/single-agent.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createSingleAgentExecutor } from '../single-agent.js';
import { ChatOpenAI } from '@langchain/openai';
import { BufferMemory } from 'langchain/memory';
import { allTools } from '../../tools/index.js';

vi.mock('@langchain/openai', () => ({
  ChatOpenAI: vi.fn().mockImplementation(() => ({
    invoke: vi.fn().mockResolvedValue({ content: 'test response' }),
    lc_namespace: ['langchain', 'chat_models', 'openai'],
  })),
}));

describe('createSingleAgentExecutor', () => {
  it('should create agent executor with correct config', async () => {
    const model = new ChatOpenAI({ openAIApiKey: 'test-key' });
    const memory = new BufferMemory({
      memoryKey: 'chat_history',
      returnMessages: true,
    });

    const executor = await createSingleAgentExecutor(model, allTools, memory);

    expect(executor).toBeDefined();
    expect(executor.tools).toHaveLength(6);
  });
});
```

**Step 2: 运行测试验证失败**

Run: `pnpm test src/ts/llm/agents/__tests__/single-agent.test.ts`
Expected: FAIL - 模块不存在

**Step 3: 实现单 LLM Agent**

```typescript
// src/ts/llm/agents/single-agent.ts
import { AgentExecutor, createToolCallingAgent } from 'langchain/agents';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { BaseTool } from '@langchain/core/tools';
import { BufferMemory } from 'langchain/memory';
import { createAgentPrompt } from './prompts.js';

export async function createSingleAgentExecutor(
  model: BaseChatModel,
  tools: BaseTool[],
  memory: BufferMemory
): Promise<AgentExecutor> {
  const prompt = createAgentPrompt();

  const agent = await createToolCallingAgent({
    llm: model,
    tools,
    prompt,
  });

  return AgentExecutor.fromAgentAndTools({
    agent,
    tools,
    memory,
    verbose: false,
    maxIterations: 10,
    handleParsingErrors: true,
  });
}
```

**Step 4: 运行测试验证通过**

Run: `pnpm test src/ts/llm/agents/__tests__/single-agent.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ts/llm/agents/single-agent.ts src/ts/llm/agents/__tests__/single-agent.test.ts
git commit -m "feat: add single LLM agent executor"
```

---

### Task 10: 创建 Agent 工厂

**Files:**
- Create: `src/ts/llm/agents/index.ts`

**Step 1: 创建 Agent 工厂**

```typescript
// src/ts/llm/agents/index.ts
import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { BaseTool } from '@langchain/core/tools';
import { BufferMemory } from 'langchain/memory';
import { createSingleAgentExecutor } from './single-agent.js';

export type AgentMode = 'single' | 'multi';

export interface AgentRuntimeOptions {
  mode: AgentMode;
  model: BaseChatModel;
  tools: BaseTool[];
  memory: BufferMemory;
  verbose?: boolean;
}

export interface SingleAgentRuntime {
  type: 'single';
  executor: Awaited<ReturnType<typeof createSingleAgentExecutor>>;
}

// Multi-agent 模式将在后续 Task 实现
export interface MultiAgentRuntime {
  type: 'multi';
  // graph: CompiledGraph; // LangGraph 类型
  model: BaseChatModel;
  tools: BaseTool[];
  memory: BufferMemory;
}

export type AgentRuntime = SingleAgentRuntime | MultiAgentRuntime;

export async function createAgentRuntime(
  options: AgentRuntimeOptions
): Promise<AgentRuntime> {
  if (options.mode === 'single') {
    const executor = await createSingleAgentExecutor(
      options.model,
      options.tools,
      options.memory
    );
    return { type: 'single', executor };
  }

  // Multi 模式暂返回占位实现
  return {
    type: 'multi',
    model: options.model,
    tools: options.tools,
    memory: options.memory,
  };
}

export { createSingleAgentExecutor } from './single-agent.js';
export * from './prompts.js';
```

**Step 2: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/llm/agents/index.ts
git commit -m "feat: add agent factory with mode selection"
```

---

## Phase 5: 记忆存储

### Task 11: 创建持久化记忆存储

**Files:**
- Create: `src/ts/llm/memory/store.ts`
- Create: `src/ts/llm/memory/__tests__/store.test.ts`

**Step 1: 编写测试**

```typescript
// src/ts/llm/memory/__tests__/store.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import { PersistentMemory } from '../store.js';

const TEST_DB_DIR = '/tmp/astock-test-memory';
const TEST_DB_PATH = path.join(TEST_DB_DIR, 'memory.db');

describe('PersistentMemory', () => {
  let memory: PersistentMemory;

  beforeEach(() => {
    // 确保测试目录存在
    if (!fs.existsSync(TEST_DB_DIR)) {
      fs.mkdirSync(TEST_DB_DIR, { recursive: true });
    }
    memory = new PersistentMemory('test-session', TEST_DB_PATH);
  });

  afterEach(() => {
    // 清理测试数据库
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
  });

  it('should create empty memory', async () => {
    const vars = await memory.loadMemoryVariables();
    expect(vars.chat_history).toEqual([]);
  });

  it('should save and load messages', async () => {
    await memory.saveContext(
      { input: '你好' },
      { output: '你好！有什么可以帮你的？' }
    );

    const vars = await memory.loadMemoryVariables();
    expect(vars.chat_history).toHaveLength(2);
    expect(vars.chat_history[0].content).toBe('你好');
    expect(vars.chat_history[1].content).toBe('你好！有什么可以帮你的？');
  });

  it('should persist messages across instances', async () => {
    await memory.saveContext(
      { input: '测试消息' },
      { output: '收到' }
    );

    const newMemory = new PersistentMemory('test-session', TEST_DB_PATH);
    const vars = await newMemory.loadMemoryVariables();
    expect(vars.chat_history).toHaveLength(2);
  });

  it('should limit history length', async () => {
    // 添加 60 条消息
    for (let i = 0; i < 30; i++) {
      await memory.saveContext(
        { input: `问题 ${i}` },
        { output: `回答 ${i}` }
      );
    }

    const vars = await memory.loadMemoryVariables();
    // 30 轮对话 = 60 条消息，应该被限制
    expect(vars.chat_history.length).toBeLessThanOrEqual(50);
  });
});
```

**Step 2: 运行测试验证失败**

Run: `pnpm test src/ts/llm/memory/__tests__/store.test.ts`
Expected: FAIL - 模块不存在

**Step 3: 实现持久化记忆**

```typescript
// src/ts/llm/memory/store.ts
import { BaseChatMemory, InputValues, MemoryVariables } from 'langchain/memory';
import { BaseMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

interface ConversationRecord {
  id: number;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  metadata?: string;
}

export class PersistentMemory extends BaseChatMemory {
  private db: Database.Database;
  private sessionId: string;
  private dbPath: string;
  private maxHistoryLength: number;

  constructor(
    sessionId?: string,
    dbPath?: string,
    maxHistoryLength: number = 50
  ) {
    super();
    this.sessionId = sessionId || this.generateSessionId();
    this.maxHistoryLength = maxHistoryLength;

    this.dbPath =
      dbPath || path.join(process.env.HOME || '', '.astock', 'data', 'memory.db');
    this.db = this.initDatabase();
  }

  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initDatabase(): Database.Database {
    const dir = path.dirname(this.dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const db = new Database(this.dbPath);

    db.exec(`
      CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
      );

      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
      );

      CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id);
    `);

    // 确保会话存在
    const sessionExists = db
      .prepare('SELECT 1 FROM sessions WHERE id = ?')
      .get(this.sessionId);

    if (!sessionExists) {
      db.prepare(
        'INSERT INTO sessions (id) VALUES (?)'
      ).run(this.sessionId);
    }

    return db;
  }

  async loadMemoryVariables(): Promise<MemoryVariables> {
    const rows = this.db
      .prepare(
        `
      SELECT role, content FROM conversations
      WHERE session_id = ?
      ORDER BY created_at DESC
      LIMIT ?
    `
      )
      .all(this.sessionId, this.maxHistoryLength) as ConversationRecord[];

    // 反转顺序，从旧到新
    const chatHistory = rows.reverse().map((row) => {
      if (row.role === 'user') {
        return new HumanMessage(row.content);
      }
      return new AIMessage(row.content);
    });

    return { chat_history: chatHistory };
  }

  async saveContext(
    input: InputValues,
    output: Record<string, unknown>
  ): Promise<void> {
    const userInput = String(input.input || '');
    const aiOutput = String(output.output || '');

    const insertStmt = this.db.prepare(`
      INSERT INTO conversations (session_id, role, content, metadata)
      VALUES (?, ?, ?, ?)
    `);

    const updateStmt = this.db.prepare(`
      UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE id = ?
    `);

    // 使用事务
    const transaction = this.db.transaction(() => {
      insertStmt.run(this.sessionId, 'user', userInput, '{}');
      insertStmt.run(this.sessionId, 'assistant', aiOutput, '{}');
      updateStmt.run(this.sessionId);
    });

    transaction();
  }

  getSessionId(): string {
    return this.sessionId;
  }

  clear(): void {
    this.db.prepare('DELETE FROM conversations WHERE session_id = ?').run(
      this.sessionId
    );
  }

  close(): void {
    this.db.close();
  }
}
```

**Step 4: 运行测试验证通过**

Run: `pnpm test src/ts/llm/memory/__tests__/store.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ts/llm/memory/store.ts src/ts/llm/memory/__tests__/store.test.ts
git commit -m "feat: add persistent memory with SQLite storage"
```

---

### Task 12: 创建记忆管理模块

**Files:**
- Create: `src/ts/llm/memory/session.ts`
- Create: `src/ts/llm/memory/feedback-integration.ts`
- Create: `src/ts/llm/memory/index.ts`

**Step 1: 创建会话管理**

```typescript
// src/ts/llm/memory/session.ts
import { PersistentMemory } from './store.js';

export interface SessionOptions {
  sessionId?: string;
  stockCode?: string;
  clearHistory?: boolean;
  maxHistoryLength?: number;
}

export interface Session {
  memory: PersistentMemory;
  sessionId: string;
}

export async function createSession(options: SessionOptions = {}): Promise<Session> {
  const sessionId = options.sessionId || generateSessionId();
  const memory = new PersistentMemory(
    sessionId,
    undefined,
    options.maxHistoryLength
  );

  if (options.clearHistory) {
    memory.clear();
  }

  return { memory, sessionId };
}

export function generateSessionId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 11);
  return `sess_${timestamp}_${random}`;
}
```

**Step 2: 创建 feedback 集成**

```typescript
// src/ts/llm/memory/feedback-integration.ts
import {
  loadGlobalFeedbackProfile,
  loadTeamFeedbackProfile,
  type FeedbackProfile,
  type GlobalFeedbackProfile,
} from '../../orchestrator/team-feedback-store.js';

export async function buildUserContextMemory(
  stockCode?: string
): Promise<string> {
  const globalProfile = await loadGlobalFeedbackProfile();
  const stockProfile = stockCode
    ? await loadTeamFeedbackProfile(stockCode)
    : null;

  if (globalProfile.sample_count === 0) {
    return '用户暂无历史反馈记录，使用默认中等风险偏好。';
  }

  const lines: string[] = ['## 用户历史偏好画像\n'];

  lines.push('### 风险偏好');
  lines.push(`- 风险承受度: ${(globalProfile.risk_appetite * 100).toFixed(0)}%`);
  lines.push(`- 样本数量: ${globalProfile.sample_count}`);
  lines.push('');

  if (Object.keys(globalProfile.strategy_weights).length > 0) {
    lines.push('### 策略权重');
    for (const [strategy, weight] of Object.entries(
      globalProfile.strategy_weights
    )) {
      lines.push(`- ${strategy}: ${(weight * 100).toFixed(0)}%`);
    }
    lines.push('');
  }

  if (stockProfile && stockProfile.sample_count > 0) {
    lines.push(`### 标的 ${stockCode} 偏好`);
    lines.push(`- 进攻偏好: ${(stockProfile.aggressiveness * 100).toFixed(0)}%`);
    lines.push(`- 防御偏好: ${(stockProfile.caution * 100).toFixed(0)}%`);
  }

  return lines.join('\n');
}

export async function enrichSystemPrompt(
  basePrompt: string,
  stockCode?: string
): Promise<string> {
  const userContext = await buildUserContextMemory(stockCode);
  return `${basePrompt}\n\n${userContext}`;
}
```

**Step 3: 创建导出**

```typescript
// src/ts/llm/memory/index.ts
export { PersistentMemory } from './store.js';
export { createSession, generateSessionId, type Session, type SessionOptions } from './session.js';
export { buildUserContextMemory, enrichSystemPrompt } from './feedback-integration.js';
```

**Step 4: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 5: Commit**

```bash
git add src/ts/llm/memory/session.ts src/ts/llm/memory/feedback-integration.ts src/ts/llm/memory/index.ts
git commit -m "feat: add memory session and feedback integration"
```

---

## Phase 6: CLI 集成

### Task 13: 扩展 CLI 命令

**Files:**
- Modify: `src/ts/index.ts`

**Step 1: 在 index.ts 中添加 agent 命令**

在现有 `team` 命令之后添加：

```typescript
// 在文件顶部添加导入
import { loadConfig } from './config/index.js';
import { createChatModel } from './llm/models/index.js';
import { allTools } from './llm/tools/index.js';
import { createAgentRuntime, type AgentMode } from './llm/agents/index.js';
import { createSession } from './llm/memory/index.js';

// 在 team 命令之后添加 agent 命令
program
  .command('agent <code>')
  .description('使用 LLM Agent 进行智能分析')
  .option('-q, --question <text>', '分析问题', '当前是否适合介入？')
  .option('-m, --mode <mode>', 'Agent 模式: single | multi', 'single')
  .option('-s, --session <id>', '继续已有会话')
  .option('-v, --verbose', '显示详细推理过程')
  .action(async (code: string, options: { question: string; mode: AgentMode; session?: string; verbose?: boolean }) => {
    try {
      if (!/^\d{6}$/.test(code)) {
        console.error(`错误: 无效的股票代码格式: ${code}，应为6位数字`);
        process.exit(1);
      }

      const config = await loadConfig();
      const provider = config.llm.provider;
      const apiKey = config.apiKeys?.[provider];

      if (!apiKey) {
        console.error(`错误: 未配置 ${provider} API Key`);
        console.error('');
        console.error('请通过以下方式之一配置:');
        console.error(`  1. 设置环境变量: ${provider.toUpperCase()}_API_KEY=xxx`);
        console.error('  2. 在 ~/.astock/config.json 中配置 apiKeys 字段');
        process.exit(1);
      }

      console.log(`\n📊 分析标的: ${code}`);
      console.log(`🤖 模型: ${config.llm.provider}`);
      console.log(`🔧 Agent 模式: ${options.mode}`);
      console.log(`📝 问题: ${options.question}\n`);

      const model = createChatModel({
        provider,
        model: config.llm.model,
        apiKey,
        temperature: config.llm.temperature,
        maxTokens: config.llm.maxTokens,
      });

      const { memory, sessionId } = await createSession({
        sessionId: options.session,
        stockCode: code,
      });

      console.log(`📋 会话 ID: ${sessionId}\n`);

      const runtime = await createAgentRuntime({
        mode: options.mode,
        model,
        tools: allTools,
        memory,
        verbose: options.verbose,
      });

      if (runtime.type === 'single') {
        const result = await runtime.executor.invoke({
          input: `${options.question}\n\n股票代码: ${code}`,
        });

        console.log('\n' + '='.repeat(60));
        console.log('Agent 分析结论');
        console.log('='.repeat(60));
        console.log(result.output);
      } else {
        console.log('Multi-agent 模式即将推出...');
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`\n❌ Agent 分析失败: ${message}`);
      process.exit(1);
    }
  });

// 添加 config 命令
program
  .command('config')
  .description('管理配置')
  .option('--show', '显示当前配置')
  .option('--set-provider <provider>', '设置默认模型提供商')
  .option('--set-mode <mode>', '设置 Agent 模式')
  .action(async (options: { show?: boolean; setProvider?: string; setMode?: string }) => {
    const config = await loadConfig();

    if (options.show) {
      // 隐藏 API Key 的敏感部分
      const safeConfig = {
        ...config,
        apiKeys: Object.fromEntries(
          Object.entries(config.apiKeys || {}).map(([k, v]) => [
            k,
            v ? `${v.substring(0, 8)}...` : undefined,
          ])
        ),
      };
      console.log(JSON.stringify(safeConfig, null, 2));
      return;
    }

    if (options.setProvider || options.setMode) {
      console.log('配置修改功能将在后续版本实现');
    }
  });
```

**Step 2: 验证编译**

Run: `pnpm run build`
Expected: 无错误

**Step 3: Commit**

```bash
git add src/ts/index.ts
git commit -m "feat: add agent and config CLI commands"
```

---

### Task 14: 更新 CLAUDE.md 文档

**Files:**
- Modify: `CLAUDE.md`

**Step 1: 更新项目说明**

在现有内容后添加：

```markdown
## LLM Agent 模式

### 新增命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `agent <code>` | LLM Agent 智能分析 | `node dist/index.js agent 000001 -q "适合介入吗？"` |
| `config` | 配置管理 | `node dist/index.js config --show` |

### 配置 API Key

方式一：环境变量
```bash
export KIMI_API_KEY="sk-xxx"
export OPENAI_API_KEY="sk-xxx"
export GLM_API_KEY="xxx"
```

方式二：配置文件 `~/.astock/config.json`
```json
{
  "llm": {
    "provider": "kimi",
    "model": "moonshot-k2.5",
    "mode": "single"
  },
  "apiKeys": {
    "kimi": "${KIMI_API_KEY}",
    "openai": "${OPENAI_API_KEY}",
    "glm": "${GLM_API_KEY}"
  }
}
```

### Agent 模式对比

| 模式 | 说明 | API 调用 | 成本 |
|------|------|----------|------|
| single | 单 LLM 编排（默认） | 1-3 次 | 低 |
| multi | 多 LLM 并行 | 5+ 次 | 高 |

### 命令对比

| 命令 | `team` | `agent` |
|------|--------|---------|
| LLM 调用 | ❌ 无 | ✅ 有 |
| 推理能力 | 规则引擎 | 智能推理 |
| 个性化 | 基础 | 深度学习 |
| 适用场景 | 快速判断 | 复杂分析 |
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with LLM Agent usage"
```

---

### Task 15: 最终验证

**Step 1: 运行所有测试**

Run: `pnpm test`
Expected: 所有测试通过

**Step 2: 验证构建**

Run: `pnpm run build`
Expected: 无错误

**Step 3: 运行 lint**

Run: `pnpm eslint src/ts --ext .ts`
Expected: 无错误

**Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: complete LLM Agent integration

- Add multi-provider model gateway (GPT-5.2, Kimi-K2.5, GLM-5)
- Implement LangChain tools for Python layer integration
- Create single-agent runtime with tool calling
- Add persistent memory with SQLite storage
- Integrate team-feedback for user preference learning
- Add agent and config CLI commands"
```

---

## 实现检查清单

- [ ] Phase 1: 依赖与配置系统
  - [ ] Task 1: 安装 LangChain 依赖
  - [ ] Task 2: 创建配置 Schema
  - [ ] Task 3: 创建配置加载器
  - [ ] Task 4: 创建 config index 导出

- [ ] Phase 2: 模型网关层
  - [ ] Task 5: 创建模型网关

- [ ] Phase 3: 工具层
  - [ ] Task 6: 创建基础工具定义
  - [ ] Task 7: 编写工具测试

- [ ] Phase 4: Agent Runtime
  - [ ] Task 8: 创建 Agent Prompts
  - [ ] Task 9: 创建单 LLM Agent
  - [ ] Task 10: 创建 Agent 工厂

- [ ] Phase 5: 记忆存储
  - [ ] Task 11: 创建持久化记忆存储
  - [ ] Task 12: 创建记忆管理模块

- [ ] Phase 6: CLI 集成
  - [ ] Task 13: 扩展 CLI 命令
  - [ ] Task 14: 更新 CLAUDE.md 文档
  - [ ] Task 15: 最终验证
