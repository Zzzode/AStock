#!/usr/bin/env node
/**
 * A股交易策略分析工具 - CLI 入口
 */

import { Command } from 'commander';
import path from 'path';
import { fileURLToPath } from 'url';
import { handleQuote } from './orchestrator/quote-handler.js';
import { handleAnalyze } from './orchestrator/analyze-handler.js';
import { handleStyle } from './orchestrator/style-handler.js';
import { handleAgentTeam } from './orchestrator/agent-team-handler.js';
import { appendTeamFeedback } from './orchestrator/team-feedback-store.js';
import { initDatabase } from './utils/python-bridge.js';
import { handleScreen } from './orchestrator/screen-handler.js';
import { handleBacktest } from './orchestrator/backtest-handler.js';
import { handleRecommend } from './orchestrator/recommend-handler.js';
import {
  handleWatchAdd,
  handleWatchRemove,
  handleWatchList,
} from './orchestrator/watch-handler.js';
import { handleAlert } from './orchestrator/alert-handler.js';
import { handleConfig } from './orchestrator/config-handler.js';
import {
  handleSessionList,
  handleSessionShow,
  handleSessionStats,
} from './orchestrator/session-handler.js';

type TeamAction = 'watch_buy' | 'wait' | 'hold_or_reduce';
type TeamOutcome = 'good' | 'bad';

interface CliDeps {
  handleQuote: typeof handleQuote;
  handleAnalyze: typeof handleAnalyze;
  handleStyle: typeof handleStyle;
  handleAgentTeam: typeof handleAgentTeam;
  appendTeamFeedback: typeof appendTeamFeedback;
  initDatabase: typeof initDatabase;
  handleScreen: typeof handleScreen;
  handleBacktest: typeof handleBacktest;
  handleRecommend: typeof handleRecommend;
  handleWatchAdd: typeof handleWatchAdd;
  handleWatchRemove: typeof handleWatchRemove;
  handleWatchList: typeof handleWatchList;
  handleAlert: typeof handleAlert;
  handleConfig: typeof handleConfig;
  handleSessionList: typeof handleSessionList;
  handleSessionShow: typeof handleSessionShow;
  handleSessionStats: typeof handleSessionStats;
}

const defaultDeps: CliDeps = {
  handleQuote,
  handleAnalyze,
  handleStyle,
  handleAgentTeam,
  appendTeamFeedback,
  initDatabase,
  handleScreen,
  handleBacktest,
  handleRecommend,
  handleWatchAdd,
  handleWatchRemove,
  handleWatchList,
  handleAlert,
  handleConfig,
  handleSessionList,
  handleSessionShow,
  handleSessionStats,
};

export function createProgram(overrides: Partial<CliDeps> = {}): Command {
  const deps: CliDeps = {
    ...defaultDeps,
    ...overrides,
  };
  const program = new Command();

  program
    .name('astock')
    .description('A股交易策略分析工具')
    .version('0.1.0');

  program
    .command('quote <code>')
    .description('获取股票实时行情')
    .action(async (code: string) => {
      const result = await deps.handleQuote(code);
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
      const result = await deps.handleAnalyze(code, parseInt(options.days, 10));
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
      await deps.initDatabase({ skipRefresh: !options.refreshStocks });
      console.log('数据库初始化完成');
    });

  program
    .command('style')
    .description('分析并学习交易风格')
    .action(async () => {
      const result = await deps.handleStyle();
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
      const result = await deps.handleAgentTeam({
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

      const saved = await deps.appendTeamFeedback({
        code,
        action: options.action as TeamAction,
        outcome: options.outcome as TeamOutcome,
        strategy: options.strategy,
        note: options.note,
      });

      console.log(`反馈已记录: ${saved.code} ${saved.action} ${saved.outcome}`);
    });

  program
    .command('screen [factors]')
    .description('智能选股')
    .option('-n, --limit <limit>', '返回数量', '10')
    .action(async (factors: string | undefined, options: { limit: string }) => {
      const factorList = factors
        ? factors.split(',').map((item) => item.trim()).filter(Boolean)
        : undefined;
      const result = await deps.handleScreen(factorList, parseInt(options.limit, 10));
      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('backtest <code>')
    .description('策略回测')
    .option('-s, --strategy <strategy>', '策略名称', 'ma_cross')
    .option('--start-date <startDate>', '回测开始日期，格式 YYYY-MM-DD')
    .option('--end-date <endDate>', '回测结束日期，格式 YYYY-MM-DD')
    .option('-c, --capital <capital>', '初始资金')
    .action(async (code: string, options: { strategy: string; startDate?: string; endDate?: string; capital?: string }) => {
      const capital = options.capital ? parseFloat(options.capital) : undefined;
      const result = await deps.handleBacktest(code, {
        strategy: options.strategy,
        startDate: options.startDate,
        endDate: options.endDate,
        capital,
      });
      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('recommend')
    .description('个性化推荐')
    .option('-n, --limit <limit>', '返回数量')
    .option('--style <style>', '交易风格')
    .option('--risk <risk>', '风险等级')
    .option('--min-price <minPrice>', '最低价格')
    .option('--max-price <maxPrice>', '最高价格')
    .action(async (options: { limit?: string; style?: string; risk?: string; minPrice?: string; maxPrice?: string }) => {
      const result = await deps.handleRecommend({
        limit: options.limit ? parseInt(options.limit, 10) : undefined,
        style: options.style,
        risk: options.risk,
        minPrice: options.minPrice ? parseFloat(options.minPrice) : undefined,
        maxPrice: options.maxPrice ? parseFloat(options.maxPrice) : undefined,
      });
      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('watch <action> [code]')
    .description('监控列表管理')
    .option('--signals <signals>', '监控信号，逗号分隔')
    .option('--channels <channels>', '通知渠道，逗号分隔')
    .action(async (action: string, code: string | undefined, options: { signals?: string; channels?: string }) => {
      let result;
      if (action === 'add') {
        if (!code) {
          console.error('用法: watch add <code> [--signals ...] [--channels ...]');
          process.exit(1);
        }
        result = await deps.handleWatchAdd(code, {
          signals: options.signals,
          channels: options.channels,
        });
      } else if (action === 'remove') {
        if (!code) {
          console.error('用法: watch remove <code>');
          process.exit(1);
        }
        result = await deps.handleWatchRemove(code);
      } else if (action === 'list') {
        result = await deps.handleWatchList();
      } else {
        console.error(`未知的 watch 动作: ${action}，可用: add/remove/list`);
        process.exit(1);
      }

      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('alert <action> [code]')
    .description('监控告警管理')
    .option('-i, --interval <interval>', '扫描间隔(秒)', '60')
    .option('-n, --limit <limit>', '历史告警数量', '10')
    .action(async (action: string, code: string | undefined, options: { interval: string; limit: string }) => {
      const result = await deps.handleAlert(action, {
        code,
        interval: parseInt(options.interval, 10),
        limit: parseInt(options.limit, 10),
      });
      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('config [action] [key] [value]')
    .description('配置管理与风格学习')
    .action(async (action: string | undefined, key?: string, value?: string) => {
      const result = await deps.handleConfig(action ?? 'show', key, value);
      if (!result.success) {
        console.error(result.error);
        process.exit(1);
      }
    });

  program
    .command('session <action>')
    .description('会话管理')
    .option('-i, --id <id>', '会话ID')
    .option('-d, --date <date>', '日期 (YYYY-MM-DD)')
    .option('--days <days>', '查询天数', '7')
    .action(async (action: string, options: { id?: string; date?: string; days: string }) => {
      if (action === 'list') {
        const result = await deps.handleSessionList({
          date: options.date,
          days: parseInt(options.days, 10),
        });
        if (!result.success) {
          console.error(result.error);
          process.exit(1);
        }
      } else if (action === 'show') {
        if (!options.id) {
          console.error('用法: session show -i <session-id>');
          process.exit(1);
        }
        const result = await deps.handleSessionShow({
          id: options.id,
          date: options.date,
        });
        if (!result.success) {
          console.error(result.error);
          process.exit(1);
        }
      } else if (action === 'stats') {
        const result = await deps.handleSessionStats({
          days: parseInt(options.days, 10),
        });
        if (!result.success) {
          console.error(result.error);
          process.exit(1);
        }
      } else {
        console.error(`未知的 session 动作: ${action}，可用: list/show/stats`);
        process.exit(1);
      }
    });

  return program;
}

function isDirectExecution(): boolean {
  if (!process.argv[1]) {
    return false;
  }
  const currentFile = fileURLToPath(import.meta.url);
  return path.resolve(currentFile) === path.resolve(process.argv[1]);
}

if (isDirectExecution()) {
  void createProgram().parseAsync();
}
