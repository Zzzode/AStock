/**
 * /screen 命令处理器
 */

import { screenStocks, ScreenOutput, ScreenResult } from '../utils/python-bridge.js';

export interface ScreenHandlerOutput {
  success: boolean;
  data?: ScreenOutput;
  error?: string;
}

/**
 * 格式化选股结果为可读字符串
 */
function formatScreenResult(data: ScreenOutput): string {
  if (data.total === 0) {
    return '\n[dim]未找到符合条件的股票[/dim]\n';
  }

  const lines: string[] = [
    '',
    `\x1b[1m选股结果 (共 ${data.total} 只)\x1b[0m`,
    '─'.repeat(60),
  ];

  // 表头
  lines.push(
    '  排名  代码      名称        得分    匹配因子'
  );
  lines.push('─'.repeat(60));

  // 数据行
  data.results.forEach((r: ScreenResult, i: number) => {
    const factorsStr = r.matched_factors.slice(0, 3).join(',');
    const more = r.matched_factors.length > 3 ? '...' : '';
    lines.push(
      `   ${String(i + 1).padStart(2)}   ${r.code}   ${(r.name || '-').padEnd(10)}   ${r.score.toFixed(1).padStart(5)}   ${factorsStr}${more}`
    );
  });

  lines.push('─'.repeat(60));
  lines.push('');

  return lines.join('\n');
}

/**
 * 处理 /screen 命令
 */
export async function handleScreen(
  factors?: string[],
  limit: number = 10
): Promise<ScreenHandlerOutput> {
  try {
    // 验证因子格式
    if (factors) {
      for (const factor of factors) {
        if (!/^[a-z0-9_]+$/.test(factor)) {
          return {
            success: false,
            error: `无效的因子名称: ${factor}，应为小写字母、数字和下划线`,
          };
        }
      }
    }

    // 验证 limit
    if (limit < 1 || limit > 100) {
      return {
        success: false,
        error: `limit 应在 1-100 之间，当前: ${limit}`,
      };
    }

    const data = await screenStocks(factors, limit);

    // 输出格式化结果
    console.log(formatScreenResult(data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `选股失败: ${message}`,
    };
  }
}
