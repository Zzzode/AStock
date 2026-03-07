/**
 * /analyze 命令处理器
 */

import { analyzeStock, AnalysisResult } from '../utils/python-bridge.js';

export interface AnalyzeOutput {
  success: boolean;
  data?: AnalysisResult;
  error?: string;
}

/**
 * 格式化分析结果
 */
function formatAnalysis(code: string, data: AnalysisResult): string {
  const latest = data.latest;
  const signals = data.signals;

  let output = `
┌─────────────────────────────────────────┐
│        技术分析 - ${code}                   │
├─────────────────────────────────────────┤
│  价格指标                               │
│  收盘价: ${latest.close.toFixed(2)}                         │
│  MA5: ${latest.ma5.toFixed(2)}   MA10: ${latest.ma10.toFixed(2)}  MA20: ${latest.ma20.toFixed(2)} │
│                                         │
│  MACD                                   │
│  DIF: ${latest.macd.toFixed(4)}   DEA: ${latest.macd_signal.toFixed(4)}   柱: ${latest.macd_hist.toFixed(4)}   │
│                                         │
│  KDJ                                    │
│  K: ${latest.kdj_k.toFixed(2)}   D: ${latest.kdj_d.toFixed(2)}   J: ${latest.kdj_j.toFixed(2)}           │
│                                         │
│  RSI                                    │
│  RSI6: ${latest.rsi6.toFixed(2)}                            │
├─────────────────────────────────────────┤
`;

  if (signals.length > 0) {
    output += `│  检测到的信号                           │\n`;
    for (const signal of signals) {
      const icon = signal.bias === 'bullish' ? '🟢' : '🔴';
      output += `│  ${icon} ${signal.name}: ${signal.description.padEnd(20)}│\n`;
    }
  } else {
    output += `│  暂无明显信号                           │\n`;
  }

  output += `└─────────────────────────────────────────┘\n`;

  return output;
}

/**
 * 处理 /analyze 命令
 */
export async function handleAnalyze(
  code: string,
  days: number = 100
): Promise<AnalyzeOutput> {
  try {
    // 验证股票代码格式
    if (!/^\d{6}$/.test(code)) {
      return {
        success: false,
        error: `无效的股票代码格式: ${code}，应为6位数字`,
      };
    }

    const data = await analyzeStock(code, days);

    // 输出格式化结果
    console.log(formatAnalysis(code, data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `技术分析失败: ${message}`,
    };
  }
}
