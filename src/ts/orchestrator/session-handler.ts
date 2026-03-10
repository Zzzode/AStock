import {
  formatSessionListOutput,
  formatSessionOutput,
  formatStatsOutput,
  getSessionStats,
  listRecentSessions,
  listSessionsByDate,
  loadSession,
  Session,
  SessionListItem,
  SessionStats,
} from './session-store.js';

export interface SessionListOptions {
  date?: string;
  days?: number;
}

export interface SessionShowOptions {
  id: string;
  date?: string;
}

export interface SessionStatsOptions {
  days?: number;
}

export interface SessionListOutput {
  success: boolean;
  data?: SessionListItem[];
  error?: string;
}

export interface SessionShowOutput {
  success: boolean;
  data?: Session;
  error?: string;
}

export interface SessionStatsOutput {
  success: boolean;
  data?: SessionStats;
  error?: string;
}

export async function handleSessionList(
  options: SessionListOptions
): Promise<SessionListOutput> {
  try {
    let sessions;

    if (options.date) {
      sessions = await listSessionsByDate(options.date);
    } else {
      sessions = await listRecentSessions(options.days ?? 7);
    }

    console.log(formatSessionListOutput(sessions));

    return {
      success: true,
      data: sessions,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取会话列表失败: ${message}`,
    };
  }
}

export async function handleSessionShow(
  options: SessionShowOptions
): Promise<SessionShowOutput> {
  try {
    const session = await loadSession(options.id, options.date);

    if (!session) {
      console.log(`未找到会话: ${options.id}`);
      return {
        success: false,
        error: `未找到会话: ${options.id}`,
      };
    }

    console.log(formatSessionOutput(session));

    return {
      success: true,
      data: session,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取会话详情失败: ${message}`,
    };
  }
}

export async function handleSessionStats(
  options: SessionStatsOptions
): Promise<SessionStatsOutput> {
  try {
    const stats = await getSessionStats(options.days ?? 30);

    console.log(formatStatsOutput(stats));

    return {
      success: true,
      data: stats,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `获取会话统计失败: ${message}`,
    };
  }
}
