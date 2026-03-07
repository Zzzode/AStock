/**
 * Python 调用桥接
 */

import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = path.resolve(__dirname, '../../python');

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
  args: string[] = []
): Promise<string> {
  const result = await execa(
    'python',
    ['-m', 'astock.cli', command, ...args, '--json'],
    {
      cwd: PYTHON_DIR,
      reject: true,
    }
  );
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
export async function initDatabase(): Promise<void> {
  await callPython('init-db');
}
