/**
 * Python 桥接测试
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { initDatabase, getQuote, analyzeStock } from '../python-bridge.js';

describe('Python Bridge', () => {
  beforeAll(async () => {
    // 初始化数据库
    process.env.ASTOCK_OFFLINE = '1';
    await initDatabase({ skipRefresh: true });
  }, 30000);

  it('should get quote', async () => {
    const result = await getQuote('000001');

    expect(result).toHaveProperty('code', '000001');
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('price');
    expect(typeof result.price).toBe('number');
  }, 30000);

  it('should analyze stock', async () => {
    const result = await analyzeStock('000001');

    expect(result).toHaveProperty('signals');
    expect(result).toHaveProperty('latest');
    expect(Array.isArray(result.signals)).toBe(true);
    expect(result.latest).toHaveProperty('close');
    expect(result.latest).toHaveProperty('ma5');
    expect(result.latest).toHaveProperty('macd');
  }, 30000);
});
