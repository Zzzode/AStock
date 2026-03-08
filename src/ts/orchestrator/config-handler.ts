/**
 * /config 命令处理器
 *
 * 管理用户偏好配置
 */

import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = path.resolve(__dirname, '../../python');

export interface ConfigOutput {
  success: boolean;
  data?: any;
  error?: string;
}

/**
 * 调用 Python CLI config 命令
 */
async function callConfig(args: string[]): Promise<string> {
  const result = await execa(
    'python',
    ['-m', 'astock.cli', 'config', ...args, '--json'],
    { cwd: PYTHON_DIR, reject: false }
  );

  if (result.failed) {
    throw new Error(result.stderr || result.stdout);
  }

  return result.stdout;
}

/**
 * 显示当前配置
 */
export async function handleConfigShow(): Promise<ConfigOutput> {
  try {
    const output = await callConfig(['show']);
    const data = JSON.parse(output);

    // 格式化输出
    formatConfigDisplay(data);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `获取配置失败: ${message}` };
  }
}

/**
 * 设置配置项
 */
export async function handleConfigSet(
  key: string,
  value: string
): Promise<ConfigOutput> {
  try {
    const output = await callConfig(['set', key, value]);
    const data = JSON.parse(output);

    console.log(`\x1b[32m配置已更新: ${key} = ${value}\x1b[0m`);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `设置配置失败: ${message}` };
  }
}

/**
 * 分析并学习交易风格
 */
export async function handleConfigStyle(): Promise<ConfigOutput> {
  try {
    console.log('\x1b[33m正在分析交易风格...\x1b[0m');

    const output = await callConfig(['style']);
    const data = JSON.parse(output);

    // 格式化风格分析结果
    formatStyleAnalysis(data);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `风格分析失败: ${message}` };
  }
}

/**
 * 重置为默认配置
 */
export async function handleConfigReset(): Promise<ConfigOutput> {
  try {
    const output = await callConfig(['reset']);
    const data = JSON.parse(output);

    console.log('\x1b[33m配置已重置为默认值\x1b[0m');

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `重置配置失败: ${message}` };
  }
}

/**
 * 统一的配置处理入口
 */
export async function handleConfig(
  action: string,
  key?: string,
  value?: string
): Promise<ConfigOutput> {
  switch (action) {
    case 'show':
      return handleConfigShow();
    case 'set':
      if (!key || !value) {
        return { success: false, error: '用法: /config set <key> <value>' };
      }
      return handleConfigSet(key, value);
    case 'style':
      return handleConfigStyle();
    case 'reset':
      return handleConfigReset();
    default:
      // 默认显示配置
      return handleConfigShow();
  }
}

/**
 * 格式化配置显示
 */
function formatConfigDisplay(data: any): void {
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

  const tradingStyle = data.trading_style || 'swing';
  const riskLevel = data.risk_level || 'moderate';

  console.log(`
\x1b[36m┌─────────────────────────────────────────────────┐\x1b[0m
\x1b[36m│\x1b[0m              用户配置                            \x1b[36m│\x1b[0m
\x1b[36m├─────────────────────────────────────────────────┤\x1b[0m
\x1b[36m│\x1b[0m  \x1b[33m交易风格:\x1b[0m ${styleNames[tradingStyle] || tradingStyle}`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m│\x1b[0m  \x1b[33m风险偏好:\x1b[0m ${riskNames[riskLevel] || riskLevel}`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m│\x1b[0m  \x1b[33m最大持仓:\x1b[0m ${data.max_positions || 10} 只`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m│\x1b[0m  \x1b[33m单只仓位:\x1b[0m ${((data.position_size || 0.1) * 100).toFixed(0)}%`.padEnd(48) + '\x1b[36m│\x1b[0m');

  if (data.min_price || data.max_price) {
    const priceRange = `${data.min_price || '-'} ~ ${data.max_price || '-'}`;
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m价格范围:\x1b[0m ${priceRange} 元`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  console.log(`\x1b[36m│\x1b[0m  \x1b[33m提醒渠道:\x1b[0m ${(data.alert_channels || ['terminal']).join(', ')}`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m│\x1b[0m  \x1b[33m默认资金:\x1b[0m ${(data.default_capital || 100000).toLocaleString()} 元`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m└─────────────────────────────────────────────────┘\x1b[0m`);
}

/**
 * 格式化风格分析结果
 */
function formatStyleAnalysis(data: any): void {
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

  const tradingStyle = data.trading_style || 'swing';
  const riskLevel = data.risk_level || 'moderate';

  console.log(`
\x1b[36m┌─────────────────────────────────────────────────┐\x1b[0m
\x1b[36m│\x1b[0m            交易风格分析结果                      \x1b[36m│\x1b[0m
\x1b[36m├─────────────────────────────────────────────────┤\x1b[0m`);

  if (data.confidence !== undefined) {
    const confidencePercent = (data.confidence * 100).toFixed(0);
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m分析置信度:\x1b[0m ${confidencePercent}%`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  console.log(`\x1b[36m│\x1b[0m  \x1b[33m交易风格:\x1b[0m ${styleNames[tradingStyle] || tradingStyle}`.padEnd(48) + '\x1b[36m│\x1b[0m');
  console.log(`\x1b[36m│\x1b[0m  \x1b[33m风险偏好:\x1b[0m ${riskNames[riskLevel] || riskLevel}`.padEnd(48) + '\x1b[36m│\x1b[0m');

  if (data.trade_frequency !== undefined) {
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m交易频率:\x1b[0m ${data.trade_frequency} 次/月`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  if (data.avg_holding_days !== undefined) {
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m平均持仓:\x1b[0m ${data.avg_holding_days} 天`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  if (data.win_rate !== undefined) {
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m胜率:\x1b[0m ${(data.win_rate * 100).toFixed(1)}%`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  if (data.preferred_sectors && data.preferred_sectors.length > 0) {
    console.log(`\x1b[36m│\x1b[0m  \x1b[33m偏好行业:\x1b[0m ${data.preferred_sectors.join(', ')}`.padEnd(48) + '\x1b[36m│\x1b[0m');
  }

  console.log(`\x1b[36m└─────────────────────────────────────────────────┘\x1b[0m`);

  if (data.confidence !== undefined && data.confidence > 0.5) {
    console.log('\n\x1b[32m配置已根据分析结果自动更新\x1b[0m');
  } else if (data.confidence !== undefined) {
    console.log('\n\x1b[33m数据不足，未更新配置（需要更多交易记录）\x1b[0m');
  }
}
