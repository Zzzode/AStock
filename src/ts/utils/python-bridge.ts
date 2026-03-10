/**
 * Python 调用桥接
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { runPython } from './python-exec.js';
import { resolvePythonDir } from './python-runtime.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = resolvePythonDir(__dirname);

export interface QuoteResult {
  code: string;
  name: string;
  price: number;
  change_percent: number;
  change: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
}

export interface AnalysisResult {
  signals: Array<{
    type: string;
    name: string;
    description: string;
    bias: 'bullish' | 'bearish';
  }>;
  latest: {
    close: number;
    ma5: number;
    ma10: number;
    ma20: number;
    macd: number;
    macd_signal: number;
    macd_hist: number;
    kdj_k: number;
    kdj_d: number;
    kdj_j: number;
    rsi6: number;
  };
}

/**
 * 调用 Python CLI
 */
async function callPython(
  command: string,
  args: string[] = [],
  options: { json?: boolean } = {}
): Promise<string> {
  const json = options.json !== false;
  const commandArgs = ['-m', 'astock.cli', command, ...args];
  if (json) {
    commandArgs.push('--json');
  }
  const result = await runPython(commandArgs, {
    cwd: PYTHON_DIR,
    reject: true,
  });
  return result.stdout;
}

/**
 * 获取实时行情
 */
export async function getQuote(code: string): Promise<QuoteResult> {
  const output = await callPython('quote', [code]);
  return JSON.parse(output);
}

/**
 * 获取技术分析
 */
export async function analyzeStock(
  code: string,
  days: number = 100
): Promise<AnalysisResult> {
  const output = await callPython('analyze', [code, '--days', String(days)]);
  return JSON.parse(output);
}

/**
 * 初始化数据库
 */
export interface InitDatabaseOptions {
  skipRefresh?: boolean;
}

export async function initDatabase(
  options: InitDatabaseOptions = {}
): Promise<void> {
  const skipRefresh = options.skipRefresh ?? true;
  const args = skipRefresh ? ['--skip-refresh'] : [];
  await callPython('init-db', args, { json: false });
}

// ============ Alert 相关接口 ============

export interface AlertStatus {
  running: boolean;
  interval: number;
  watch_count: number;
  today_alerts: number;
}

export interface AlertRecord {
  id: number;
  code: string;
  signal_type: string;
  signal_name: string;
  message: string;
  level: number;
  triggered_at: string;
  status: string;
}

export interface AlertHistory {
  alerts: AlertRecord[];
}

/**
 * 启动监控服务
 */
export async function startAlertMonitor(interval: number = 60): Promise<{
  status: string;
  interval: number;
  watch_count: number;
}> {
  const result = await runPython(
    ['-m', 'astock.cli', 'alert', 'start', '--interval', String(interval), '--json'],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return JSON.parse(result.stdout);
}

/**
 * 停止监控服务
 */
export async function stopAlertMonitor(): Promise<{
  status: string;
}> {
  const result = await runPython(
    ['-m', 'astock.cli', 'alert', 'stop', '--json'],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return JSON.parse(result.stdout);
}

/**
 * 获取监控服务状态
 */
export async function getAlertStatus(): Promise<AlertStatus> {
  const result = await runPython(
    ['-m', 'astock.cli', 'alert', 'status', '--json'],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return JSON.parse(result.stdout);
}

/**
 * 获取历史告警
 */
export async function getAlertHistory(
  code?: string,
  limit: number = 10
): Promise<AlertHistory> {
  const args = ['alert', 'history', '--limit', String(limit), '--json'];
  if (code) {
    args.splice(2, 0, code);
  }

  const result = await runPython(
    ['-m', 'astock.cli', ...args],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return JSON.parse(result.stdout);
}


// ============ Screen 选股相关接口 ============

export interface ScreenResult {
  code: string;
  name: string;
  score: number;
  matched_factors: string[];
  factor_scores: Record<string, number>;
  screened_at: string;
}

export interface ScreenOutput {
  total: number;
  results: ScreenResult[];
}

/**
 * 执行选股
 */
export async function screenStocks(
  factors?: string[],
  limit: number = 10,
  codes?: string[]
): Promise<ScreenOutput> {
  const args = ['screen'];

  if (factors && factors.length > 0) {
    args.push(factors.join(','));
  }

  args.push('--limit', String(limit));
  if (codes && codes.length > 0) {
    args.push('--codes', codes.join(','));
  }
  args.push('--json');

  const result = await runPython(
    ['-m', 'astock.cli', ...args],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
  return JSON.parse(result.stdout);
}
