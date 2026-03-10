import { execa } from 'execa';
import { resolvePythonBinaries } from './python-runtime.js';

export interface RunPythonOptions {
  cwd: string;
  reject?: boolean;
}

export async function runPython(
  args: string[],
  options: RunPythonOptions
): Promise<{ stdout: string; stderr: string; failed: boolean }> {
  const candidates = resolvePythonBinaries();

  let lastError: unknown;
  for (const candidate of candidates) {
    try {
      return await execa(candidate, args, options);
    } catch (error) {
      const code = error && typeof error === 'object' && 'code' in error
        ? String((error as { code?: unknown }).code)
        : '';
      if (code === 'ENOENT') {
        lastError = error;
        continue;
      }
      throw error;
    }
  }

  throw lastError ?? new Error('未找到可用的 Python 可执行文件');
}
