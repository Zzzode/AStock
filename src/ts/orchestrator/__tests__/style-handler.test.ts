import { describe, it, expect, vi } from 'vitest';
import { handleStyle } from '../style-handler.js';
import { handleConfigStyle } from '../config-handler.js';

vi.mock('../config-handler.js', () => ({
  handleConfigStyle: vi.fn(),
}));

describe('style handler', () => {
  it('delegates to config style handler', async () => {
    vi.mocked(handleConfigStyle).mockResolvedValueOnce({
      success: true,
      data: {
        trading_style: 'swing',
        risk_level: 'moderate',
      },
    });

    const result = await handleStyle();

    expect(handleConfigStyle).toHaveBeenCalledTimes(1);
    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('trading_style');
    expect(result.data).toHaveProperty('risk_level');
  }, 30000);
});
