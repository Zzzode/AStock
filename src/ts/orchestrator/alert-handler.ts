/**
 * /alert 命令处理器
 */

import {
  startAlertMonitor,
  stopAlertMonitor,
  getAlertStatus,
  getAlertHistory,
  AlertStatus,
  AlertHistory,
} from '../utils/python-bridge.js';

export interface AlertOutput {
  success: boolean;
  data?: AlertStatus | AlertHistory | { status: string; interval?: number; watch_count?: number };
  error?: string;
}

/**
 * 格式化监控状态
 */
function formatStatus(data: AlertStatus): string {
  const statusText = data.running ? '运行中' : '已停止';
  const statusColor = data.running ? '\x1b[32m' : '\x1b[90m';
  const reset = '\x1b[0m';

  return `
┌─────────────────────────────────────────┐
│         监控服务状态                      │
├─────────────────────────────────────────┤
│  状态: ${statusColor}${statusText.padEnd(20)}${reset}
│  扫描间隔: ${String(data.interval).padEnd(20)}秒
│  监控股票: ${String(data.watch_count).padEnd(20)}只
│  今日告警: ${String(data.today_alerts).padEnd(20)}条
└─────────────────────────────────────────┘
`;
}

/**
 * 格式化历史告警
 */
function formatHistory(data: AlertHistory, code?: string): string {
  const alerts = data.alerts;

  if (alerts.length === 0) {
    return '暂无告警记录';
  }

  const title = code ? `历史告警 (${code})` : '历史告警记录';
  let output = `
┌──────────────────────────────────────────────────────────────────┐
│  ${title.padEnd(60)}│
├──────────────────────────────────────────────────────────────────┤
│  时间            股票        信号类型      描述                    │
├──────────────────────────────────────────────────────────────────┤
`;

  for (const alert of alerts) {
    const date = new Date(alert.triggered_at);
    const timeStr = `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    const signalName = alert.signal_name.padEnd(10);
    const message = alert.message.length > 20 ? alert.message.slice(0, 20) + '...' : alert.message;
    output += `│  ${timeStr}    ${alert.code}    ${signalName}  ${message.padEnd(20)}│\n`;
  }

  output += `└──────────────────────────────────────────────────────────────────┘\n`;

  return output;
}

/**
 * 启动监控服务
 */
export async function handleAlertStart(interval: number = 60): Promise<AlertOutput> {
  try {
    const data = await startAlertMonitor(interval);

    console.log(`\x1b[32m监控服务已启动\x1b[0m`);
    console.log(`扫描间隔: ${data.interval}秒`);
    console.log(`监控股票: ${data.watch_count}只`);

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `启动监控服务失败: ${message}`,
    };
  }
}

/**
 * 停止监控服务
 */
export async function handleAlertStop(): Promise<AlertOutput> {
  try {
    const data = await stopAlertMonitor();

    if (data.status === 'stopped') {
      console.log(`\x1b[33m监控服务已停止\x1b[0m`);
    } else {
      console.log(`\x1b[90m监控服务未运行\x1b[0m`);
    }

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `停止监控服务失败: ${message}`,
    };
  }
}

/**
 * 查看监控状态
 */
export async function handleAlertStatus(): Promise<AlertOutput> {
  try {
    const data = await getAlertStatus();

    console.log(formatStatus(data));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取监控状态失败: ${message}`,
    };
  }
}

/**
 * 查看历史告警
 */
export async function handleAlertHistory(
  code?: string,
  limit: number = 10
): Promise<AlertOutput> {
  try {
    const data = await getAlertHistory(code, limit);

    console.log(formatHistory(data, code));

    return {
      success: true,
      data,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取历史告警失败: ${message}`,
    };
  }
}

/**
 * 统一处理 /alert 命令
 */
export async function handleAlert(
  command: string,
  args?: { code?: string; interval?: number; limit?: number }
): Promise<AlertOutput> {
  switch (command) {
    case 'start':
      return handleAlertStart(args?.interval ?? 60);
    case 'stop':
      return handleAlertStop();
    case 'status':
      return handleAlertStatus();
    case 'history':
      return handleAlertHistory(args?.code, args?.limit ?? 10);
    default:
      return {
        success: false,
        error: `未知的 alert 命令: ${command}`,
      };
  }
}
