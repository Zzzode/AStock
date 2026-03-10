# Agent Team Orchestrator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在现有仓库上落地一个可运行的 Agent Team 编排最小闭环，让用户通过单次请求获得多专家观点与综合建议。

**Architecture:** 复用现有 TypeScript Orchestrator 与 Python 能力层，不重建基础设施。新增 `team` 编排处理器作为主控 Agent，内部并行调度 Market/Analysis/Strategy/Risk/Style 逻辑，统一生成结构化结论。先实现单标的 MVP，再按阶段扩展会话协议、冲突仲裁和学习闭环。

**Tech Stack:** TypeScript, Commander.js, Vitest, Node.js, Python CLI Bridge

---

### Task 1: 定义 Agent Team 输出协议

**Files:**
- Create: `src/ts/orchestrator/agent-team-handler.ts`
- Test: `src/ts/orchestrator/__tests__/agent-team-handler.test.ts`

**Step 1: 写 failing test（协议结构）**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { handleAgentTeam } from '../agent-team-handler.js';
import { getQuote, analyzeStock, screenStocks } from '../../utils/python-bridge.js';

vi.mock('../../utils/python-bridge.js', () => ({
  getQuote: vi.fn(),
  analyzeStock: vi.fn(),
  screenStocks: vi.fn(),
}));

describe('agent team handler', () => {
  it('returns aggregated multi-expert output', async () => {
    vi.mocked(getQuote).mockResolvedValueOnce({
      code: '000001',
      name: '平安银行',
      price: 10.5,
      change_percent: 1.2,
      change: 0.12,
      volume: 1000000,
      amount: 10000000,
      high: 10.6,
      low: 10.3,
      open: 10.4,
      prev_close: 10.38,
    });
    vi.mocked(analyzeStock).mockResolvedValueOnce({
      signals: [{ type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' }],
      latest: {
        close: 10.5, ma5: 10.3, ma10: 10.2, ma20: 10.0,
        macd: 0.2, macd_signal: 0.1, macd_hist: 0.1,
        kdj_k: 62, kdj_d: 55, kdj_j: 76, rsi6: 58,
      },
    });
    vi.mocked(screenStocks).mockResolvedValueOnce({
      total: 1,
      results: [{
        code: '000001',
        name: '平安银行',
        score: 82,
        matched_factors: ['ma_cross'],
        factor_scores: { ma_cross: 82 },
        screened_at: '2026-03-10T00:00:00Z',
      }],
    });

    const result = await handleAgentTeam({ code: '000001', question: '现在是否适合介入？' });

    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('summary');
    expect(result.data).toHaveProperty('experts');
    expect(result.data).toHaveProperty('decision');
    expect(result.data.experts).toHaveProperty('market');
    expect(result.data.experts).toHaveProperty('analysis');
    expect(result.data.experts).toHaveProperty('strategy');
    expect(result.data.experts).toHaveProperty('risk');
    expect(result.data.experts).toHaveProperty('style');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: FAIL with "Cannot find module '../agent-team-handler.js'" or missing export

**Step 3: 写最小实现（仅返回协议骨架）**

- 创建 `handleAgentTeam`，返回 `{ success, data }` 结构
- data 至少包含 `summary/experts/decision`

**Step 4: Run test to verify it passes**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: PASS

### Task 2: 实现多专家并行调度与聚合

**Files:**
- Modify: `src/ts/orchestrator/agent-team-handler.ts`
- Test: `src/ts/orchestrator/__tests__/agent-team-handler.test.ts`

**Step 1: 写 failing test（聚合规则）**

- 增加用例：bullish 信号为主且风险中低时，`decision.action` 应为 `watch_buy`
- 增加用例：bearish 信号或高风险时，`decision.action` 应为 `hold_or_reduce`

**Step 2: Run test to verify it fails**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: FAIL on decision assertion mismatch

**Step 3: 写最小实现**

- 并行调用 `getQuote`、`analyzeStock`、`screenStocks`
- 计算专家观点：
  - Market: 当前涨跌幅和波动
  - Analysis: bullish/bearish 信号占比
  - Strategy: 是否在选股结果中、得分区间
  - Risk: 由 RSI/KDJ/短期涨幅生成风险等级
  - Style: 默认读取用户风格占位结果（MVP 可返回 `moderate`）
- 生成综合决策：`action`、`confidence`、`rationale[]`、`counterpoints[]`

**Step 4: Run test to verify it passes**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: PASS

### Task 3: 接入 CLI 与导出入口

**Files:**
- Modify: `src/ts/orchestrator/index.ts`
- Modify: `src/ts/index.ts`
- Test: `src/ts/orchestrator/__tests__/agent-team-handler.test.ts`

**Step 1: 写 failing test（CLI 路由）**

- 为 `src/ts/index.ts` 增加命令存在性测试或最小 smoke test
- 断言 `team <code>` 命令调用 `handleAgentTeam`

**Step 2: Run test to verify it fails**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: FAIL with missing command or missing export

**Step 3: 写最小实现**

- `orchestrator/index.ts` 导出 `handleAgentTeam`
- `index.ts` 增加 `team <code>` 命令和 `--question`、`--days` 参数
- 失败时输出错误并退出码 1

**Step 4: Run test to verify it passes**

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/agent-team-handler.test.ts`
Expected: PASS

### Task 4: 文档与验收

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Step 1: 文档补充**

- 增加 `team` 命令示例
- 说明 Agent Team MVP 当前能力边界

**Step 2: 运行验证**

Run: `pnpm run build`
Expected: PASS

Run: `pnpm test`
Expected: PASS

Run: `pnpm test -- --run src/ts/orchestrator/__tests__/skill-acceptance.test.ts`
Expected: PASS

### Task 5: 后续迭代计划（非本次实现）

**Files:**
- Modify: `docs/plans/2026-03-09-claude-code-agent-runtime-design.md`

**Step 1: 增加下阶段事项**

- 会话协议持久化（task tree / evidence / conclusion）
- 专家冲突仲裁器（置信度学习）
- 用户反馈采集与在线参数更新

**Step 2: 记录验收指标**

- 多专家结论一致性
- 决策解释完整度
- 用户反馈闭环转化率
