import { existsSync } from 'fs';
import path from 'path';

type ExistsFn = (filePath: string) => boolean;

export function resolvePythonDir(
  baseDir: string,
  cwd: string = process.cwd(),
  exists: ExistsFn = existsSync
): string {
  const candidates = [
    path.resolve(baseDir, '../../python'),
    path.resolve(baseDir, '../../src/python'),
    path.resolve(cwd, 'src/python'),
  ];

  for (const candidate of candidates) {
    if (exists(path.join(candidate, 'pyproject.toml'))) {
      return candidate;
    }
  }

  return candidates[0];
}

export function resolvePythonBinaries(
  cwd: string = process.cwd(),
  env: NodeJS.ProcessEnv = process.env,
  exists: ExistsFn = existsSync
): string[] {
  if (env.ASTOCK_PYTHON_BIN) {
    return [env.ASTOCK_PYTHON_BIN];
  }

  const binaries: string[] = [];
  const venvPython = path.resolve(cwd, '.venv/bin/python');
  if (exists(venvPython)) {
    binaries.push(venvPython);
  }
  binaries.push('python', 'python3');
  return binaries;
}
