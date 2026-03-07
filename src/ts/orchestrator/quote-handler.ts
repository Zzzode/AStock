/**
 * /quote 命令处理器
 */

import { getQuote, QuoteResult } from '../utils/python-bridge.js';

export interface QuoteOutput {
  success: boolean;
  data?: QuoteResult;
  error?: string;
}

/**
 * 格式化行情数据为可读字符串
 */
function formatQuote(data: QuoteResult): string {
  const changeIcon = data.change_percent >= 0 ? '🔺' : '🔻';
  const changeColor = data.change_percent >= 0 ? '\x1b[31m' : '\x1b[32m';
  const reset = '\x1b[0m';

  return `
┌─────────────────────────────────────────┐
│        ${data.name} (${data.code})                 │
├─────────────────────────────────────────┤
│  最新价: ${data.price.toFixed(2).padEnd(12)}${changeColor}${changeIcon} ${data.change_percent.toFixed(2)}%${reset}
│  涨跌额: ${data.change >= 0 ? '+' : ''}${data.change.toFixed(2).padEnd(12)}昨收: ${data.prev_close.toFixed(2)}
│  今开: ${data.open.toFixed(2).padEnd(12)}最高: ${data.high.toFixed(2)}
│  最低: ${data.low.toFixed(2).padEnd(12)}成交量: ${(data.volume / 10000).toFixed(0)}万手
│  成交额: ${(data.amount / 100000000).toFixed(2)}亿                        │
└─────────────────────────────────────────┘
`;
}

/**
 * 处理 /quote 命令
 */
export async function handleQuote(code: string): Promise<QuoteOutput> {
  try {
    // 验证股票代码格式
    if (!/^\d{6}$/.test(code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${code}，应为6位数字`,
      };
    }

    const data = await getQuote(code);

    // 输出格式化结果
    console.log(formatQuote(data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取行情失败: ${message}`,
    };
  }
}
