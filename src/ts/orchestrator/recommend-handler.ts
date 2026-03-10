/**
 * /recommend 命令处理器
 *
 * 根据用户风格生成个性化股票推荐
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { runPython } from '../utils/python-exec.js';
import { resolvePythonDir } from '../utils/python-runtime.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = resolvePythonDir(__dirname);

export interface RecommendOutput {
  success: boolean;
  data?: any;
  error?: string;
}

/**
 * 调用 Python CLI recommend 命令
 */
async function callRecommend(options: {
  limit?: number;
  style?: string;
  risk?: string;
  minPrice?: number;
  maxPrice?: number;
  json?: boolean;
}): Promise<string> {
  const args = ['recommend'];

  if (options.limit) {
    args.push('--limit', String(options.limit));
  }
  if (options.style) {
    args.push('--style', options.style);
  }
  if (options.risk) {
    args.push('--risk', options.risk);
  }
  if (options.minPrice !== undefined) {
    args.push('--min-price', String(options.minPrice));
  }
  if (options.maxPrice !== undefined) {
    args.push('--max-price', String(options.maxPrice));
  }
  args.push('--json');

  const result = await runPython(
    ['-m', 'astock.cli', ...args],
    { cwd: PYTHON_DIR, reject: false }
  );

  if (result.failed) {
    throw new Error(result.stderr || result.stdout);
  }

  return result.stdout;
}

/**
 * 生成个性化推荐
 */
export async function handleRecommend(options?: {
  limit?: number;
  style?: string;
  risk?: string;
  minPrice?: number;
  maxPrice?: number;
}): Promise<RecommendOutput> {
  try {
    console.log('\x1b[33m正在生成个性化推荐...\x1b[0m');

    const output = await callRecommend(options || {});
    const data = JSON.parse(output);

    if (data.success && data.recommendations) {
      formatRecommendations(data);
    }

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `推荐生成失败: ${message}` };
  }
}

/**
 * 格式化推荐结果显示
 */
function formatRecommendations(data: any): void {
  const config = data.config_used || {};

  const styleNames: Record<string, string> = {
    day_trading: '日内交易',
    swing: '波段交易',
    trend_following: '趋势跟踪',
    value_investing: '价值投资',
  };

  const riskNames: Record<string, string> = {
    conservative: '保守型',
    moderate: '稳健型',
    aggressive: '激进型',
  };

  const style = styleNames[config.trading_style || 'swing'] || '波段交易';
  const risk = riskNames[config.risk_level || 'moderate'] || '稳健型';

  console.log(`
\x1b[36m┌──────────────────────────────────────────────────────────────────────┐\x1b[0m
\x1b[36m│\x1b[0m  \x1b[1m个性化推荐\x1b[0m                                                          \x1b[36m│\x1b[0m
\x1b[36m│\x1b[0m  交易风格: ${style}  风险偏好: ${risk}`.padEnd(71) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m├──────────────────────────────────────────────────────────────────────┤\x1b[0m`);

  if (!data.recommendations || data.recommendations.length === 0) {
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m暂无符合条件的推荐股票\x1b[0m`.padEnd(71) + '\x1b[36m│\x1b[0m');
    console.log(`\x1b[36m└──────────────────────────────────────────────────────────────────────┘\x1b[0m`);
    return;
  }

  console.log(`\x1b[36m│\x1b[0m  \x1b[33m代码\x1b[0m     \x1b[33m名称\x1b[0m          \x1b[33m得分\x1b[0m    \x1b[33m风格匹配\x1b[0m  \x1b[33m推荐策略\x1b[0m`.padEnd(71) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m├──────────────────────────────────────────────────────────────────────┤\x1b[0m`);

  for (const rec of data.recommendations) {
    const code = (rec.code || '').padEnd(8);
    const name = (rec.name || '-').padEnd(12);
    const score = typeof rec.score === 'number' ? rec.score.toFixed(1) : '-';
    const match = typeof rec.style_match === 'number'
      ? (rec.style_match * 100).toFixed(0) + '%'
      : '-';
    const strategies = (rec.suggested_strategies || []).slice(0, 2).join(', ');

    const line = `  ${code} ${name} ${String(score).padStart(4)}    ${String(match).padStart(6)}    ${strategies}`;
    console.log(`\x1b[36m│\x1b[0m${line}`.padEnd(71) + '\x1b[36m│\x1b[0m');
  }

  console.log(`\x1b[36m└──────────────────────────────────────────────────────────────────────┘\x1b[0m`);

  // 显示匹配因子信息
  if (data.recommendations.length > 0 && data.recommendations[0].matched_factors) {
    console.log('\n\x1b[90m匹配因子说明:\x1b[0m');
    const factors = new Set<string>();
    for (const rec of data.recommendations) {
      for (const f of rec.matched_factors || []) {
        factors.add(f);
      }
    }
    if (factors.size > 0) {
      console.log(`\x1b[90m  ${Array.from(factors).join(', ')}\x1b[0m`);
    }
  }
}
