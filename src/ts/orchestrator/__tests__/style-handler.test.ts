import { describe, it, expect } from 'vitest';
import { handleStyle } from '../style-handler.js';

describe('style handler', () => {
  it('returns style analysis output', async () => {
    const result = await handleStyle();
    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('trading_style');
    expect(result.data).toHaveProperty('risk_level');
  }, 30000);
});
