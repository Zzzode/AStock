# Style Skill Chain Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让 `/style` 通过 TypeScript orchestrator 调用 Python 配置风格分析并返回结构化结果。

**Architecture:** 新增 style handler 作为 /style 入口，内部复用 config-handler 的风格分析能力；CLI 增加 style 命令；补充 TS 测试验证输出结构。

**Tech Stack:** TypeScript (commander, vitest), Python CLI (typer)

---

### Task 1: 新增 /style 命令处理器

**Files:**
- Create: `src/ts/orchestrator/style-handler.ts`
- Modify: `src/ts/orchestrator/index.ts`
- Modify: `src/ts/index.ts`

**Step 1: 写 failing test**

```typescript
import { describe, it, expect } from 'vitest';
import { handleStyle } from '../style-handler.js';

describe('style handler', () => {
  it('returns style analysis output', async () => {
    const result = await handleStyle();
    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('trading_style');
    expect(result.data).toHaveProperty('risk_level');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm test src/ts/orchestrator/__tests__/style-handler.test.ts`
Expected: FAIL with "handleStyle is not defined"

**Step 3: Write minimal implementation**

```typescript
import { handleConfigStyle } from './config-handler.js';

export async function handleStyle() {
  return handleConfigStyle();
}
```

**Step 4: Wire exports and CLI**

- Export `handleStyle` in `orchestrator/index.ts`
- Add CLI command `style` in `src/ts/index.ts` calling `handleStyle`

**Step 5: Run tests**

Run: `pnpm test src/ts/orchestrator/__tests__/style-handler.test.ts`
Expected: PASS

---

### Task 2: 补充文档与验证

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Step 1: 文档补充**

在 Skills 列表与快速开始中补充 `/style` 入口说明。

**Step 2: 验证**

Run: `pnpm run build`
Expected: PASS

Run: `pnpm test`
Expected: PASS

---

### Task 3: 基线异常导出修复

**Files:**
- Modify: `src/python/astock/utils/__init__.py`
- Test: `src/python/astock/utils/__tests__/test_exceptions_export.py`

**Step 1: Run test to verify it fails**

Run: `python -m pytest astock/utils/__tests__/test_exceptions_export.py -vv`
Expected: FAIL with ImportError for AlertError

**Step 2: Export AlertError**

```python
from .exceptions import AlertError
__all__ = [..., "AlertError"]
```

**Step 3: Run test to verify it passes**

Run: `python -m pytest astock/utils/__tests__/test_exceptions_export.py -vv`
Expected: PASS
