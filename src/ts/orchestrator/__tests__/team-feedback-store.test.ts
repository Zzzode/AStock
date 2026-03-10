import { afterEach, describe, expect, it } from 'vitest';
import { mkdtemp, rm } from 'fs/promises';
import path from 'path';
import os from 'os';
import {
  appendTeamFeedback,
  loadGlobalFeedbackProfile,
  loadTeamFeedbackProfile,
} from '../team-feedback-store.js';

let tempDir = '';

afterEach(async () => {
  delete process.env.ASTOCK_TEAM_FEEDBACK_FILE;
  if (tempDir) {
    await rm(tempDir, { recursive: true, force: true });
    tempDir = '';
  }
});

describe('team feedback store', () => {
  it('loads empty profile when no feedback exists', async () => {
    tempDir = await mkdtemp(path.join(os.tmpdir(), 'astock-feedback-'));
    process.env.ASTOCK_TEAM_FEEDBACK_FILE = path.join(tempDir, 'team-feedback.json');

    const profile = await loadTeamFeedbackProfile('000001');

    expect(profile.sample_count).toBe(0);
    expect(profile.aggressiveness).toBe(0);
    expect(profile.caution).toBe(0);
  });

  it('builds profile from feedback records', async () => {
    tempDir = await mkdtemp(path.join(os.tmpdir(), 'astock-feedback-'));
    process.env.ASTOCK_TEAM_FEEDBACK_FILE = path.join(tempDir, 'team-feedback.json');

    await appendTeamFeedback({
      code: '000001',
      action: 'watch_buy',
      outcome: 'good',
      note: '买入后走势符合预期',
    });
    await appendTeamFeedback({
      code: '000001',
      action: 'watch_buy',
      outcome: 'good',
      note: '回撤可控',
    });
    await appendTeamFeedback({
      code: '000001',
      action: 'hold_or_reduce',
      outcome: 'bad',
      note: '减仓后错失反弹',
    });

    const profile = await loadTeamFeedbackProfile('000001');

    expect(profile.sample_count).toBe(3);
    expect(profile.aggressiveness).toBeGreaterThan(0.5);
    expect(profile.caution).toBeLessThan(0);
  });

  it('builds global profile with risk appetite and strategy weights', async () => {
    tempDir = await mkdtemp(path.join(os.tmpdir(), 'astock-feedback-'));
    process.env.ASTOCK_TEAM_FEEDBACK_FILE = path.join(tempDir, 'team-feedback.json');

    await appendTeamFeedback({
      code: '000001',
      action: 'watch_buy',
      outcome: 'good',
      strategy: 'ma_cross',
      note: '突破后上涨',
    });
    await appendTeamFeedback({
      code: '000002',
      action: 'watch_buy',
      outcome: 'bad',
      strategy: 'macd',
      note: '追高回落',
    });
    await appendTeamFeedback({
      code: '000003',
      action: 'hold_or_reduce',
      outcome: 'bad',
      strategy: 'kdj_reversal',
      note: '减仓后踏空',
    });

    const profile = await loadGlobalFeedbackProfile();

    expect(profile.sample_count).toBe(3);
    expect(profile.risk_appetite).toBeGreaterThan(0);
    expect(profile.strategy_weights.ma_cross).toBeGreaterThan(0);
    expect(profile.strategy_weights.macd).toBeLessThan(0);
  });
});
