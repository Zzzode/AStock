import { describe, it, expect, vi, beforeEach } from 'vitest';
import { handleAgentTeam } from '../agent-team-handler.js';
import { getQuote, analyzeStock, screenStocks } from '../../utils/python-bridge.js';
import {
  loadTeamFeedbackProfile,
  loadGlobalFeedbackProfile,
} from '../team-feedback-store.js';

vi.mock('../../utils/python-bridge.js', () => ({
  getQuote: vi.fn(),
  analyzeStock: vi.fn(),
  screenStocks: vi.fn(),
}));

vi.mock('../team-feedback-store.js', () => ({
  loadTeamFeedbackProfile: vi.fn(),
  loadGlobalFeedbackProfile: vi.fn(),
}));

const mockGetQuote = vi.mocked(getQuote);
const mockAnalyzeStock = vi.mocked(analyzeStock);
const mockScreenStocks = vi.mocked(screenStocks);
const mockLoadTeamFeedbackProfile = vi.mocked(loadTeamFeedbackProfile);
const mockLoadGlobalFeedbackProfile = vi.mocked(loadGlobalFeedbackProfile);

describe('agent team handler', () => {
  beforeEach(() => {
    mockGetQuote.mockReset();
    mockAnalyzeStock.mockReset();
    mockScreenStocks.mockReset();
    mockLoadTeamFeedbackProfile.mockReset();
    mockLoadGlobalFeedbackProfile.mockReset();
    mockLoadTeamFeedbackProfile.mockResolvedValue({
      sample_count: 0,
      aggressiveness: 0,
      caution: 0,
    });
    mockLoadGlobalFeedbackProfile.mockResolvedValue({
      sample_count: 0,
      risk_appetite: 0,
      strategy_weights: {},
    });
  });

  it('returns aggregated multi-expert output', async () => {
    mockGetQuote.mockResolvedValueOnce({
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

    mockAnalyzeStock.mockResolvedValueOnce({
      signals: [
        { type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' },
        { type: 'momentum', name: 'MACD金叉', description: '动能转强', bias: 'bullish' },
      ],
      latest: {
        close: 10.5,
        ma5: 10.3,
        ma10: 10.2,
        ma20: 10.0,
        macd: 0.2,
        macd_signal: 0.1,
        macd_hist: 0.1,
        kdj_k: 62,
        kdj_d: 55,
        kdj_j: 76,
        rsi6: 58,
      },
    });

    mockScreenStocks.mockResolvedValueOnce({
      total: 1,
      results: [
        {
          code: '000001',
          name: '平安银行',
          score: 82,
          matched_factors: ['ma_cross'],
          factor_scores: { ma_cross: 82 },
          screened_at: '2026-03-10T00:00:00Z',
        },
      ],
    });

    const result = await handleAgentTeam({
      code: '000001',
      question: '现在是否适合介入？',
      days: 120,
    });

    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('summary');
    expect(result.data).toHaveProperty('experts');
    expect(result.data).toHaveProperty('decision');
    expect(result.data?.experts).toHaveProperty('market');
    expect(result.data?.experts).toHaveProperty('analysis');
    expect(result.data?.experts).toHaveProperty('strategy');
    expect(result.data?.experts).toHaveProperty('risk');
    expect(result.data?.experts).toHaveProperty('style');
    expect(result.data?.decision.action).toBe('watch_buy');
    expect(result.data?.decision).toHaveProperty('influence');
    expect(result.data?.decision.influence).toHaveProperty('base_score');
  });

  it('returns hold_or_reduce when bearish and risk is high', async () => {
    mockGetQuote.mockResolvedValueOnce({
      code: '000001',
      name: '平安银行',
      price: 10.5,
      change_percent: -2.8,
      change: -0.3,
      volume: 1000000,
      amount: 10000000,
      high: 10.8,
      low: 10.2,
      open: 10.7,
      prev_close: 10.8,
    });

    mockAnalyzeStock.mockResolvedValueOnce({
      signals: [
        { type: 'trend', name: '均线空头', description: '趋势走弱', bias: 'bearish' },
      ],
      latest: {
        close: 10.5,
        ma5: 10.3,
        ma10: 10.4,
        ma20: 10.6,
        macd: -0.3,
        macd_signal: -0.2,
        macd_hist: -0.1,
        kdj_k: 88,
        kdj_d: 82,
        kdj_j: 95,
        rsi6: 78,
      },
    });

    mockScreenStocks.mockResolvedValueOnce({
      total: 0,
      results: [],
    });

    const result = await handleAgentTeam({
      code: '000001',
      question: '要不要继续持有？',
    });

    expect(result.success).toBe(true);
    expect(result.data?.decision.action).toBe('hold_or_reduce');
    expect(result.data?.experts.risk.level).toBe('high');
  });

  it('applies feedback profile to increase buy confidence', async () => {
    mockLoadTeamFeedbackProfile.mockResolvedValueOnce({
      sample_count: 8,
      aggressiveness: 0.6,
      caution: 0.1,
    });

    mockGetQuote.mockResolvedValueOnce({
      code: '000001',
      name: '平安银行',
      price: 10.5,
      change_percent: 0.6,
      change: 0.06,
      volume: 1000000,
      amount: 10000000,
      high: 10.6,
      low: 10.3,
      open: 10.4,
      prev_close: 10.44,
    });

    mockAnalyzeStock.mockResolvedValueOnce({
      signals: [
        { type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' },
      ],
      latest: {
        close: 10.5,
        ma5: 10.4,
        ma10: 10.3,
        ma20: 10.2,
        macd: 0.05,
        macd_signal: 0.04,
        macd_hist: 0.01,
        kdj_k: 52,
        kdj_d: 50,
        kdj_j: 56,
        rsi6: 54,
      },
    });

    mockScreenStocks.mockResolvedValueOnce({
      total: 1,
      results: [
        {
          code: '000001',
          name: '平安银行',
          score: 73,
          matched_factors: ['ma_cross'],
          factor_scores: { ma_cross: 73 },
          screened_at: '2026-03-10T00:00:00Z',
        },
      ],
    });

    const result = await handleAgentTeam({
      code: '000001',
      question: '是否可以买入？',
    });

    expect(result.success).toBe(true);
    expect(mockLoadTeamFeedbackProfile).toHaveBeenCalledWith('000001');
    expect(mockLoadGlobalFeedbackProfile).toHaveBeenCalled();
    expect(result.data?.decision.action).toBe('watch_buy');
    expect(result.data?.decision.confidence).toBeGreaterThan(0.7);
    expect(result.data?.decision.influence.style_bias).toBeGreaterThan(0);
  });

  it('applies global strategy weight to decision influence', async () => {
    mockLoadGlobalFeedbackProfile.mockResolvedValueOnce({
      sample_count: 12,
      risk_appetite: 0.2,
      strategy_weights: { ma_cross: 0.9 },
    });

    mockGetQuote.mockResolvedValueOnce({
      code: '000001',
      name: '平安银行',
      price: 10.5,
      change_percent: 0.3,
      change: 0.03,
      volume: 1000000,
      amount: 10000000,
      high: 10.6,
      low: 10.3,
      open: 10.4,
      prev_close: 10.47,
    });

    mockAnalyzeStock.mockResolvedValueOnce({
      signals: [
        { type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' },
      ],
      latest: {
        close: 10.5,
        ma5: 10.4,
        ma10: 10.3,
        ma20: 10.2,
        macd: 0.05,
        macd_signal: 0.03,
        macd_hist: 0.02,
        kdj_k: 50,
        kdj_d: 48,
        kdj_j: 54,
        rsi6: 52,
      },
    });

    mockScreenStocks.mockResolvedValueOnce({
      total: 1,
      results: [
        {
          code: '000001',
          name: '平安银行',
          score: 75,
          matched_factors: ['ma_cross'],
          factor_scores: { ma_cross: 75 },
          screened_at: '2026-03-10T00:00:00Z',
        },
      ],
    });

    const result = await handleAgentTeam({
      code: '000001',
      question: '策略偏好会如何影响建议？',
    });

    expect(result.success).toBe(true);
    expect(result.data?.decision.influence.strategy_weight).toBeGreaterThan(0);
    expect(result.data?.decision.influence.risk_appetite).toBeGreaterThan(0);
  });

  it('prints influence breakdown in cli panel', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    try {
      mockLoadGlobalFeedbackProfile.mockResolvedValueOnce({
        sample_count: 10,
        risk_appetite: 0.3,
        strategy_weights: { ma_cross: 0.5 },
      });

      mockGetQuote.mockResolvedValueOnce({
        code: '000001',
        name: '平安银行',
        price: 10.5,
        change_percent: 0.8,
        change: 0.08,
        volume: 1000000,
        amount: 10000000,
        high: 10.6,
        low: 10.3,
        open: 10.4,
        prev_close: 10.42,
      });

      mockAnalyzeStock.mockResolvedValueOnce({
        signals: [{ type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' }],
        latest: {
          close: 10.5,
          ma5: 10.4,
          ma10: 10.3,
          ma20: 10.2,
          macd: 0.05,
          macd_signal: 0.03,
          macd_hist: 0.02,
          kdj_k: 50,
          kdj_d: 48,
          kdj_j: 54,
          rsi6: 52,
        },
      });

      mockScreenStocks.mockResolvedValueOnce({
        total: 1,
        results: [{
          code: '000001',
          name: '平安银行',
          score: 75,
          matched_factors: ['ma_cross'],
          factor_scores: { ma_cross: 75 },
          screened_at: '2026-03-10T00:00:00Z',
        }],
      });

      await handleAgentTeam({
        code: '000001',
        question: '影响权重是什么？',
      });

      const output = logSpy.mock.calls.map((call) => String(call[0] ?? '')).join('\n');
      expect(output).toContain('影响权重');
      expect(output).toContain('基础分');
      expect(output).toContain('最终分');
      expect(output).toContain('推理轨迹');
      expect(output).toContain('1)');
    } finally {
      logSpy.mockRestore();
    }
  });

  it('prints progress stages during team analysis', async () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    try {
      mockGetQuote.mockResolvedValueOnce({
        code: '000001',
        name: '平安银行',
        price: 10.5,
        change_percent: 0.8,
        change: 0.08,
        volume: 1000000,
        amount: 10000000,
        high: 10.6,
        low: 10.3,
        open: 10.4,
        prev_close: 10.42,
      });
      mockAnalyzeStock.mockResolvedValueOnce({
        signals: [{ type: 'trend', name: '均线多头', description: '趋势向上', bias: 'bullish' }],
        latest: {
          close: 10.5,
          ma5: 10.4,
          ma10: 10.3,
          ma20: 10.2,
          macd: 0.05,
          macd_signal: 0.03,
          macd_hist: 0.02,
          kdj_k: 50,
          kdj_d: 48,
          kdj_j: 54,
          rsi6: 52,
        },
      });
      mockScreenStocks.mockResolvedValueOnce({ total: 0, results: [] });

      await handleAgentTeam({
        code: '000001',
        question: '现在是否适合介入？',
      });

      const output = logSpy.mock.calls.map((call) => String(call[0] ?? '')).join('\n');
      expect(output).toContain('正在获取行情数据');
      expect(output).toContain('正在进行技术分析');
      expect(output).toContain('正在进行策略筛选');
      expect(output).toContain('正在汇总多专家结论');
    } finally {
      logSpy.mockRestore();
    }
  });
});
