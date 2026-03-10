/**
 * /backtest 命令处理器
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { runPython } from '../utils/python-exec.js';
import { resolvePythonDir } from '../utils/python-runtime.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = resolvePythonDir(__dirname);

export interface BacktestResult {
  code: string;
  strategy: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  annual_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  win_rate: number;
  trades: Array<{
    date: string;
    signal: string;
    price: number;
    shares: number;
    value: number;
    commission: number;
  }>;
}

export interface BacktestOptions {
  strategy: string;
  startDate?: string;
  endDate?: string;
  capital?: number;
}

export interface BacktestOutput {
  success: boolean;
  data?: BacktestResult;
  error?: string;
}

/**
 * 格式化回测结果
 */
function formatBacktest(code: string, data: BacktestResult): string {
  const returnSign = data.total_return >= 0 ? '+' : '';
  const returnColor = data.total_return >= 0 ? 'green' : 'red';
  const annualSign = data.annual_return >= 0 ? '+' : '';
  const annualColor = data.annual_return >= 0 ? 'green' : 'red';

  let output = `
┌─────────────────────────────────────────┐
│        回测结果 - ${code}                   │
├─────────────────────────────────────────┤
│  策略: ${data.strategy.padEnd(20)}        │
│  回测区间: ${data.start_date} ~ ${data.end_date} │
│                                         │
│  收益指标                               │
│  总收益率: ${returnSign}${data.total_return.toFixed(2)}%                   │
│  年化收益: ${annualSign}${data.annual_return.toFixed(2)}%                   │
│  最大回撤: -${data.max_drawdown.toFixed(2)}%                    │
│  夏普比率: ${data.sharpe_ratio.toFixed(2)}                         │
│                                         │
│  交易统计                               │
│  初始资金: ${data.initial_capital.toLocaleString()} 元              │
│  最终资金: ${data.final_capital.toLocaleString()} 元              │
│  交易次数: ${data.trades.length} 次                        │
│  胜率: ${data.win_rate.toFixed(1)}%                            │
├─────────────────────────────────────────┤
`;

  if (data.trades.length > 0) {
    output += `│  最近交易记录                           │\n`;
    const recentTrades = data.trades.slice(-5);
    for (const trade of recentTrades) {
      const signal = trade.signal === 'buy' ? '买入' : '卖出';
      output += `│  ${trade.date}  ${signal}  ${trade.shares}股  @${trade.price.toFixed(2)}元     │\n`;
    }
    if (data.trades.length > 5) {
      output += `│  ... 共 ${data.trades.length} 条记录                      │\n`;
    }
  }

  output += `└─────────────────────────────────────────┘\n`;

  return output;
}

/**
 * 处理 /backtest 命令
 */
export async function handleBacktest(
  code: string,
  options: BacktestOptions
): Promise<BacktestOutput> {
  try {
    // 验证股票代码格式
    if (!/^\d{6}$/.test(code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${code}，应为6位数字`,
      };
    }

    // 验证策略名称
    const validStrategies = ['ma_cross', 'macd'];
    if (!validStrategies.includes(options.strategy)) {
      return {
        success: false,
        error: `未知的策略名称: ${options.strategy}，可用策略: ${validStrategies.join(', ')}`,
      };
    }

    // 构建 CLI 参数
    const args = [
      '-m', 'astock.cli', 'backtest', 'run', code,
      '--strategy', options.strategy,
    ];

    if (options.startDate) {
      args.push('--start-date', options.startDate);
    }

    if (options.endDate) {
      args.push('--end-date', options.endDate);
    }

    if (options.capital) {
      args.push('--capital', String(options.capital));
    }

    args.push('--json');

    // 调用 Python CLI
    const result = await runPython(args, {
      cwd: PYTHON_DIR,
      reject: true,
    });

    const data: BacktestResult = JSON.parse(result.stdout);

    // 输出格式化结果
    console.log(formatBacktest(code, data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `回测失败: ${message}`,
    };
  }
}
