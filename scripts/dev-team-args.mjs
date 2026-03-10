export function parseDevTeamArgs(rawArgs) {
  const args = Array.isArray(rawArgs) ? [...rawArgs] : [];
  while (args[0] === '--') {
    args.shift();
  }

  let skipInit = false;
  let timeoutMs = 120000;

  const filtered = [];
  for (let index = 0; index < args.length; index += 1) {
    const token = args[index];
    if (token === '--skip-init') {
      skipInit = true;
      continue;
    }
    if (token === '--timeout') {
      const next = args[index + 1];
      const seconds = Number(next);
      if (Number.isFinite(seconds) && seconds > 0) {
        timeoutMs = Math.round(seconds * 1000);
        index += 1;
      }
      continue;
    }
    filtered.push(token);
  }

  return {
    code: filtered[0] || '000001',
    question: filtered[1] || '现在是否适合介入？',
    days: filtered[2] || '120',
    skipInit,
    timeoutMs,
  };
}
