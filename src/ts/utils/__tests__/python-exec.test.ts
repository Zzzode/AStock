import path from 'path';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { execa } from 'execa';
import { runPython } from '../python-exec.js';

vi.mock('execa', () => ({
  execa: vi.fn(),
}));

const mockExeca = vi.mocked(execa);

describe('runPython', () => {
  beforeEach(() => {
    mockExeca.mockReset();
    delete process.env.ASTOCK_PYTHON_BIN;
  });

  it('falls back to python3 when python is unavailable', async () => {
    mockExeca
      .mockRejectedValueOnce({ code: 'ENOENT', message: 'venv python not found' })
      .mockRejectedValueOnce({ code: 'ENOENT', message: 'python not found' })
      .mockResolvedValueOnce({ stdout: 'ok', failed: false } as any);

    const result = await runPython(['-m', 'astock.cli', 'quote', '000001'], {
      cwd: '/tmp',
      reject: true,
    });

    expect(result.stdout).toBe('ok');
    expect(mockExeca).toHaveBeenCalledTimes(3);
    expect(mockExeca).toHaveBeenNthCalledWith(
      1,
      path.resolve(process.cwd(), '.venv/bin/python'),
      ['-m', 'astock.cli', 'quote', '000001'],
      { cwd: '/tmp', reject: true }
    );
    expect(mockExeca).toHaveBeenNthCalledWith(
      2,
      'python',
      ['-m', 'astock.cli', 'quote', '000001'],
      { cwd: '/tmp', reject: true }
    );
    expect(mockExeca).toHaveBeenNthCalledWith(
      3,
      'python3',
      ['-m', 'astock.cli', 'quote', '000001'],
      { cwd: '/tmp', reject: true }
    );
  });

  it('uses ASTOCK_PYTHON_BIN when provided', async () => {
    process.env.ASTOCK_PYTHON_BIN = 'python3';
    mockExeca.mockResolvedValueOnce({ stdout: 'ok', failed: false } as any);

    await runPython(['-m', 'astock.cli', 'quote', '000001'], {
      cwd: '/tmp',
      reject: true,
    });

    expect(mockExeca).toHaveBeenCalledTimes(1);
    expect(mockExeca).toHaveBeenCalledWith(
      'python3',
      ['-m', 'astock.cli', 'quote', '000001'],
      { cwd: '/tmp', reject: true }
    );
  });
});
