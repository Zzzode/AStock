import { describe, expect, it } from 'vitest';

describe('dev team args parser', () => {
  it('parses args when pnpm injects leading separator', async () => {
    const mod = await import('../../../../scripts/dev-team-args.mjs');
    const parsed = mod.parseDevTeamArgs(['--', '600589', '现在是否适合介入？', '20']);
    expect(parsed.code).toBe('600589');
    expect(parsed.question).toBe('现在是否适合介入？');
    expect(parsed.days).toBe('20');
  });

  it('parses skip-init and timeout options', async () => {
    const mod = await import('../../../../scripts/dev-team-args.mjs');
    const parsed = mod.parseDevTeamArgs([
      '--',
      '600589',
      '现在是否适合介入？',
      '20',
      '--skip-init',
      '--timeout',
      '45',
    ]);
    expect(parsed.skipInit).toBe(true);
    expect(parsed.timeoutMs).toBe(45000);
  });
});
