type SkillName =
  | 'quote'
  | 'analyze'
  | 'screen'
  | 'backtest'
  | 'recommend'
  | 'watch'
  | 'alert'
  | 'config'
  | 'style';

type OutputShape = {
  success: boolean;
  data?: unknown;
};

function hasFields(data: unknown, fields: string[]): boolean {
  if (!data || typeof data !== 'object') {
    return false;
  }
  const record = data as Record<string, unknown>;
  return fields.every((field) => field in record);
}

export function validateSkillOutput(skill: SkillName, output: OutputShape): boolean {
  if (!output.success || !output.data) {
    return false;
  }

  switch (skill) {
    case 'quote':
      return hasFields(output.data, ['code', 'name', 'price']);
    case 'analyze': {
      const data = output.data as Record<string, unknown>;
      return Array.isArray(data.signals) && typeof data.latest === 'object';
    }
    case 'screen': {
      const data = output.data as Record<string, unknown>;
      return typeof data.total === 'number' && Array.isArray(data.results);
    }
    case 'backtest':
      return hasFields(output.data, ['strategy', 'total_return', 'trades']);
    case 'recommend': {
      const data = output.data as Record<string, unknown>;
      return Array.isArray(data.recommendations);
    }
    case 'watch': {
      const data = output.data as Record<string, unknown>;
      return Array.isArray(data.items) || Array.isArray(data.watch_list);
    }
    case 'alert':
      return hasFields(output.data, ['running', 'interval', 'watch_count']);
    case 'config':
    case 'style':
      return hasFields(output.data, ['trading_style', 'risk_level']);
    default:
      return false;
  }
}
