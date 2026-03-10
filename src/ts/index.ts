#!/usr/bin/env node
/**
 * A股交易策略分析工具 - CLI 入口
 */

import { Command } from 'commander';
import { handleQuote } from './orchestrator/quote-handler.js';
import { handleAnalyze } from './orchestrator/analyze-handler.js';
import { handleStyle } from './orchestrator/style-handler.js';
import { handleAgentTeam } from './orchestrator/agent-team-handler.js';
import { appendTeamFeedback } from './orchestrator/team-feedback-store.js';
import { initDatabase } from './utils/python-bridge.js';

const program = new Command();

program
  .name('astock')
  .description('A股交易策略分析工具')
  .version('0.1.0');

program
  .command('quote <code>')
  .description('获取股票实时行情')
  .action(async (code: string) => {
    const result = await handleQuote(code);
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('analyze <code>')
  .description('技术分析')
  .option('-d, --days <days>', '分析天数', '100')
  .action(async (code: string, options: { days: string }) => {
    const result = await handleAnalyze(code, parseInt(options.days, 10));
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('init')
  .description('初始化数据库')
  .option('--refresh-stocks', '初始化时刷新全量股票列表（可能较慢）', false)
  .action(async (options: { refreshStocks: boolean }) => {
    console.log('正在初始化数据库...');
    if (!options.refreshStocks) {
      console.log('已启用快速模式（跳过股票列表刷新），如需全量刷新请使用 --refresh-stocks');
    }
    await initDatabase({ skipRefresh: !options.refreshStocks });
    console.log('数据库初始化完成');
  });

program
  .command('style')
  .description('分析并学习交易风格')
  .action(async () => {
    const result = await handleStyle();
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('team <code>')
  .description('Agent Team 多专家协作分析')
  .option('-q, --question <question>', '用户问题', '当前是否适合介入？')
  .option('-d, --days <days>', '分析天数', '100')
  .action(async (code: string, options: { question: string; days: string }) => {
    const result = await handleAgentTeam({
      code,
      question: options.question,
      days: parseInt(options.days, 10),
    });
    if (!result.success) {
      console.error(result.error);
      process.exit(1);
    }
  });

program
  .command('team-feedback <code>')
  .description('记录 Agent Team 建议反馈，用于后续偏好学习')
  .requiredOption(
    '-a, --action <action>',
    '建议动作，支持 watch_buy/wait/hold_or_reduce'
  )
  .requiredOption('-o, --outcome <outcome>', '反馈结果，支持 good/bad')
  .option('-s, --strategy <strategy>', '关联策略/因子，如 ma_cross')
  .option('-n, --note <note>', '补充说明')
  .action(async (code: string, options: { action: string; outcome: string; strategy?: string; note?: string }) => {
    if (!/^\d{6}$/.test(code)) {
      console.error(`无效的股票代码格式: ${code}，应为6位数字`);
      process.exit(1);
    }

    if (!['watch_buy', 'wait', 'hold_or_reduce'].includes(options.action)) {
      console.error(`无效 action: ${options.action}`);
      process.exit(1);
    }

    if (!['good', 'bad'].includes(options.outcome)) {
      console.error(`无效 outcome: ${options.outcome}`);
      process.exit(1);
    }

    const saved = await appendTeamFeedback({
      code,
      action: options.action as 'watch_buy' | 'wait' | 'hold_or_reduce',
      outcome: options.outcome as 'good' | 'bad',
      strategy: options.strategy,
      note: options.note,
    });

    console.log(`反馈已记录: ${saved.code} ${saved.action} ${saved.outcome}`);
  });

program.parse();
