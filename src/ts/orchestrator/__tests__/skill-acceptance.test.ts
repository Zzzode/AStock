import { describe, it, expect, vi, beforeEach } from 'vitest';
import { execa } from 'execa';
import { handleQuote } from '../quote-handler.js';
import { handleAnalyze } from '../analyze-handler.js';
import { handleScreen } from '../screen-handler.js';
import { handleBacktest } from '../backtest-handler.js';
import { handleRecommend } from '../recommend-handler.js';
import { handleWatchList } from '../watch-handler.js';
import { handleAlertStatus } from '../alert-handler.js';
import { handleConfigShow, handleConfigStyle } from '../config-handler.js';
import { handleStyle } from '../style-handler.js';
import {
  getQuote,
  analyzeStock,
  screenStocks,
  getAlertStatus,
} from '../../utils/python-bridge.js';
import { validateSkillOutput } from '../skill-acceptance.js';

vi.mock('execa', () => ({
  execa: vi.fn(),
}));

vi.mock('../../utils/python-bridge.js', () => ({
  getQuote: vi.fn(),
  analyzeStock: vi.fn(),
  screenStocks: vi.fn(),
  startAlertMonitor: vi.fn(),
  stopAlertMonitor: vi.fn(),
  getAlertStatus: vi.fn(),
  getAlertHistory: vi.fn(),
}));

const mockExeca = vi.mocked(execa);
const mockGetQuote = vi.mocked(getQuote);
const mockAnalyzeStock = vi.mocked(analyzeStock);
const mockScreenStocks = vi.mocked(screenStocks);
const mockGetAlertStatus = vi.mocked(getAlertStatus);

beforeEach(() => {
  mockExeca.mockReset();
  mockGetQuote.mockReset();
  mockAnalyzeStock.mockReset();
  mockScreenStocks.mockReset();
  mockGetAlertStatus.mockReset();
});

describe('skill acceptance', () => {
  it('validates quote output', async () => {
    mockGetQuote.mockResolvedValue({
      code: '000001',
      name: '平安银行',
      price: 10.5,
      change_percent: 0.1,
      change: 0.01,
      volume: 1000000,
      amount: 10000000,
      high: 10.6,
      low: 10.4,
      open: 10.5,
      prev_close: 10.49,
    });

    const result = await handleQuote('000001');

    expect(validateSkillOutput('quote', result)).toBe(true);
  });

  it('validates analyze output', async () => {
    mockAnalyzeStock.mockResolvedValue({
      signals: [
        { type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' },
      ],
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
    });

    const result = await handleAnalyze('000001');

    expect(validateSkillOutput('analyze', result)).toBe(true);
  });

  it('validates screen output', async () => {
    mockScreenStocks.mockResolvedValue({
      total: 1,
      results: [
        {
          code: '000001',
          name: '平安银行',
          score: 78.2,
          matched_factors: ['ma_cross'],
          factor_scores: { ma_cross: 78.2 },
          screened_at: '2026-03-09',
        },
      ],
    });

    const result = await handleScreen(['ma_cross'], 10);

    expect(validateSkillOutput('screen', result)).toBe(true);
  });

  it('validates backtest output', async () => {
    mockExeca.mockResolvedValue({
      stdout: JSON.stringify({
        code: '000001',
        strategy: 'ma_cross',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        initial_capital: 100000,
        final_capital: 112000,
        total_return: 12.0,
        annual_return: 12.0,
        max_drawdown: 5.0,
        sharpe_ratio: 1.2,
        win_rate: 60,
        trades: [],
      }),
    } as any);

    const result = await handleBacktest('000001', { strategy: 'ma_cross' });

    expect(validateSkillOutput('backtest', result)).toBe(true);
  });

  it('validates recommend output', async () => {
    mockExeca.mockResolvedValue({
      stdout: JSON.stringify({
        success: true,
        config_used: { trading_style: 'swing', risk_level: 'moderate' },
        recommendations: [
          { code: '000001', name: '平安银行', score: 0.86, reason: '趋势向上' },
        ],
      }),
      failed: false,
    } as any);

    const result = await handleRecommend({ limit: 1 });

    expect(validateSkillOutput('recommend', result)).toBe(true);
  });

  it('validates watch output', async () => {
    mockExeca.mockResolvedValue({
      stdout: JSON.stringify({ items: [{ code: '000001', enabled: true }] }),
      failed: false,
    } as any);

    const result = await handleWatchList();

    expect(validateSkillOutput('watch', result)).toBe(true);
  });

  it('validates alert output', async () => {
    mockGetAlertStatus.mockResolvedValue({
      running: true,
      interval: 60,
      watch_count: 1,
      today_alerts: 0,
    });

    const result = await handleAlertStatus();

    expect(validateSkillOutput('alert', result)).toBe(true);
  });

  it('validates config output', async () => {
    mockExeca.mockResolvedValue({
      stdout: JSON.stringify({ trading_style: 'swing', risk_level: 'moderate' }),
      failed: false,
    } as any);

    const result = await handleConfigShow();

    expect(validateSkillOutput('config', result)).toBe(true);
  });

  it('validates style output', async () => {
    mockExeca.mockResolvedValue({
      stdout: JSON.stringify({
        trading_style: 'swing',
        risk_level: 'moderate',
        confidence: 0.6,
      }),
      failed: false,
    } as any);

    const configResult = await handleConfigStyle();
    const styleResult = await handleStyle();

    expect(validateSkillOutput('style', configResult)).toBe(true);
    expect(validateSkillOutput('style', styleResult)).toBe(true);
  });
});
