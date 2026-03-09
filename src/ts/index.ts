#!/usr/bin/env node
/**
 * A股交易策略分析工具 - CLI 入口
 */

import { Command } from 'commander';
import { handleQuote } from './orchestrator/quote-handler.js';
import { handleAnalyze } from './orchestrator/analyze-handler.js';
import { handleStyle } from './orchestrator/style-handler.js';
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
  .action(async () => {
    console.log('正在初始化数据库...');
    await initDatabase();
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

program.parse();
