import { describe, it, expect, beforeEach, vi } from 'vitest';
import { initDatabase, getQuote, analyzeStock, screenStocks } from '../python-bridge.js';
import { runPython } from '../python-exec.js';

vi.mock('../python-exec.js', () => ({
  runPython: vi.fn(),
}));

describe('Python Bridge', () => {
  beforeEach(() => {
    vi.mocked(runPython).mockReset();
  });

  it('should get quote', async () => {
    vi.mocked(runPython).mockResolvedValueOnce({
      stdout: JSON.stringify({
        code: '000001',
        name: '平安银行',
        price: 10.5,
      }),
      stderr: '',
      failed: false,
    });

    const result = await getQuote('000001');

    expect(result).toHaveProperty('code', '000001');
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('price');
    expect(typeof result.price).toBe('number');
    expect(runPython).toHaveBeenCalledWith(
      ['-m', 'astock.cli', 'quote', '000001', '--json'],
      { cwd: expect.stringContaining('/src/python'), reject: true }
    );
  });

  it('should analyze stock', async () => {
    vi.mocked(runPython).mockResolvedValueOnce({
      stdout: JSON.stringify({
        signals: [],
        latest: {
          close: 10.5,
          ma5: 10.3,
          ma10: 10.1,
          ma20: 9.9,
          macd: 0.2,
          macd_signal: 0.1,
          macd_hist: 0.1,
          kdj_k: 60,
          kdj_d: 55,
          kdj_j: 70,
          rsi6: 55,
        },
      }),
      stderr: '',
      failed: false,
    });

    const result = await analyzeStock('000001');

    expect(result).toHaveProperty('signals');
    expect(result).toHaveProperty('latest');
    expect(Array.isArray(result.signals)).toBe(true);
    expect(result.latest).toHaveProperty('close');
    expect(result.latest).toHaveProperty('ma5');
    expect(result.latest).toHaveProperty('macd');
    expect(runPython).toHaveBeenCalledWith(
      ['-m', 'astock.cli', 'analyze', '000001', '--days', '100', '--json'],
      { cwd: expect.stringContaining('/src/python'), reject: true }
    );
  });

  it('should initialize database with skip refresh', async () => {
    vi.mocked(runPython).mockResolvedValueOnce({
      stdout: '',
      stderr: '',
      failed: false,
    });

    await initDatabase({ skipRefresh: true });

    expect(runPython).toHaveBeenCalledWith(
      ['-m', 'astock.cli', 'init-db', '--skip-refresh'],
      { cwd: expect.stringContaining('/src/python'), reject: true }
    );
  });

  it('should initialize database with skip refresh by default', async () => {
    vi.mocked(runPython).mockResolvedValueOnce({
      stdout: '',
      stderr: '',
      failed: false,
    });

    await initDatabase();

    expect(runPython).toHaveBeenCalledWith(
      ['-m', 'astock.cli', 'init-db', '--skip-refresh'],
      { cwd: expect.stringContaining('/src/python'), reject: true }
    );
  });

  it('should screen target stock codes only', async () => {
    vi.mocked(runPython).mockResolvedValueOnce({
      stdout: JSON.stringify({
        total: 1,
        results: [
          {
            code: '600589',
            name: '大位科技',
            score: 70,
            matched_factors: ['ma_cross'],
            factor_scores: { ma_cross: 70 },
            screened_at: '2026-03-10T00:00:00.000Z',
          },
        ],
      }),
      stderr: '',
      failed: false,
    });

    const result = await screenStocks(undefined, 1, ['600589']);

    expect(result.total).toBe(1);
    expect(runPython).toHaveBeenCalledWith(
      ['-m', 'astock.cli', 'screen', '--limit', '1', '--codes', '600589', '--json'],
      { cwd: expect.stringContaining('/src/python'), reject: true }
    );
  });
});
