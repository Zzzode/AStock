import { describe, expect, it, vi } from 'vitest';

describe('ts cli command registration', () => {
  it('registers full orchestrator command set', async () => {
    const mod = await import('../index.js');

    const program = mod.createProgram({
      handleQuote: vi.fn().mockResolvedValue({ success: true }),
      handleAnalyze: vi.fn().mockResolvedValue({ success: true }),
      handleStyle: vi.fn().mockResolvedValue({ success: true }),
      handleAgentTeam: vi.fn().mockResolvedValue({ success: true }),
      appendTeamFeedback: vi.fn().mockResolvedValue({
        code: '000001',
        action: 'wait',
        outcome: 'good',
      }),
      initDatabase: vi.fn().mockResolvedValue(undefined),
      handleScreen: vi.fn().mockResolvedValue({ success: true }),
      handleBacktest: vi.fn().mockResolvedValue({ success: true }),
      handleRecommend: vi.fn().mockResolvedValue({ success: true }),
      handleWatchAdd: vi.fn().mockResolvedValue({ success: true }),
      handleWatchRemove: vi.fn().mockResolvedValue({ success: true }),
      handleWatchList: vi.fn().mockResolvedValue({ success: true }),
      handleAlert: vi.fn().mockResolvedValue({ success: true }),
      handleConfig: vi.fn().mockResolvedValue({ success: true }),
    });

    const commandNames = program.commands.map((c: { name: () => string }) => c.name());

    expect(commandNames).toEqual(
      expect.arrayContaining([
        'quote',
        'analyze',
        'init',
        'style',
        'team',
        'team-feedback',
        'screen',
        'backtest',
        'recommend',
        'watch',
        'alert',
        'config',
      ])
    );
  });

  it('routes screen command to handler with parsed factors and limit', async () => {
    const mod = await import('../index.js');
    const handleScreen = vi.fn().mockResolvedValue({ success: true });

    const program = mod.createProgram({
      handleQuote: vi.fn().mockResolvedValue({ success: true }),
      handleAnalyze: vi.fn().mockResolvedValue({ success: true }),
      handleStyle: vi.fn().mockResolvedValue({ success: true }),
      handleAgentTeam: vi.fn().mockResolvedValue({ success: true }),
      appendTeamFeedback: vi.fn().mockResolvedValue({ code: '000001', action: 'wait', outcome: 'good' }),
      initDatabase: vi.fn().mockResolvedValue(undefined),
      handleScreen,
      handleBacktest: vi.fn().mockResolvedValue({ success: true }),
      handleRecommend: vi.fn().mockResolvedValue({ success: true }),
      handleWatchAdd: vi.fn().mockResolvedValue({ success: true }),
      handleWatchRemove: vi.fn().mockResolvedValue({ success: true }),
      handleWatchList: vi.fn().mockResolvedValue({ success: true }),
      handleAlert: vi.fn().mockResolvedValue({ success: true }),
      handleConfig: vi.fn().mockResolvedValue({ success: true }),
    });

    await program.parseAsync(['node', 'astock', 'screen', 'ma_cross,rsi_oversold', '--limit', '12']);

    expect(handleScreen).toHaveBeenCalledWith(['ma_cross', 'rsi_oversold'], 12);
  });
});
