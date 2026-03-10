import path from 'path';
import { describe, it, expect } from 'vitest';
import { resolvePythonBinaries, resolvePythonDir } from '../python-runtime.js';

describe('python runtime', () => {
  it('prefers project venv python when available', () => {
    const cwd = '/project';
    const binaries = resolvePythonBinaries(
      cwd,
      {},
      (filePath) => filePath === path.resolve(cwd, '.venv/bin/python')
    );

    expect(binaries[0]).toBe('/project/.venv/bin/python');
  });

  it('resolves src/python for dist runtime layout', () => {
    const baseDir = '/project/dist/utils';
    const resolved = resolvePythonDir(
      baseDir,
      '/project',
      (filePath) => filePath === '/project/src/python/pyproject.toml'
    );

    expect(resolved).toBe('/project/src/python');
  });
});
