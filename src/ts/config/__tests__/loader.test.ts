// src/ts/config/__tests__/loader.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { loadConfig, CONFIG_PATHS } from '../loader.js';

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
    expect(config.llm?.provider).toBe('kimi');
    expect(config.llm?.mode).toBe('single');
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
    expect(config.llm?.temperature).toBeGreaterThanOrEqual(0);
    expect(config.llm?.temperature).toBeLessThanOrEqual(2);
  });
});
