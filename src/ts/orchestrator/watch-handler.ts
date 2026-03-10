/**
 * /watch 命令处理器
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { runPython } from '../utils/python-exec.js';
import { resolvePythonDir } from '../utils/python-runtime.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = resolvePythonDir(__dirname);

export interface WatchOutput {
  success: boolean;
  data?: any;
  error?: string;
}

async function callWatch(args: string[]): Promise<string> {
  const result = await runPython(
    ['-m', 'astock.monitor.watch_cli', ...args, '--json'],
    { cwd: PYTHON_DIR, reject: true }
  );
  return result.stdout;
}

export async function handleWatchAdd(
  code: string,
  options?: { signals?: string; channels?: string }
): Promise<WatchOutput> {
  try {
    const args = ['add', code];
    if (options?.signals) args.push('--signals', options.signals);
    if (options?.channels) args.push('--channels', options.channels);

    const output = await callWatch(args);
    const data = JSON.parse(output);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `添加监控失败: ${message}` };
  }
}

export async function handleWatchRemove(code: string): Promise<WatchOutput> {
  try {
    const output = await callWatch(['remove', code]);
    const data = JSON.parse(output);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `移除监控失败: ${message}` };
  }
}

export async function handleWatchList(): Promise<WatchOutput> {
  try {
    const output = await callWatch(['list']);
    const data = JSON.parse(output);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `获取监控列表失败: ${message}` };
  }
}
