import { execa } from 'execa';
import { parseDevTeamArgs } from './dev-team-args.mjs';

const { code, question, days, skipInit, timeoutMs } = parseDevTeamArgs(process.argv.slice(2));

const run = async (command, commandArgs, options = {}) => {
  const subprocess = execa(command, commandArgs, {
    stdio: 'inherit',
    reject: false,
  });
  const warningSeconds = Math.round((options.timeout ?? 0) / 1000);
  const warningTimer = options.timeout && options.timeout > 0
    ? setTimeout(() => {
      console.log(`执行已超过 ${warningSeconds}s，仍在运行：${command} ${commandArgs.join(' ')}`);
    }, options.timeout)
    : null;
  const result = await subprocess;
  if (warningTimer) {
    clearTimeout(warningTimer);
  }
  if (result.exitCode !== 0) {
    console.error(`命令执行失败（exit ${result.exitCode}）：${command} ${commandArgs.join(' ')}`);
    process.exit(result.exitCode ?? 1);
  }
};

console.log(`准备分析: code=${code}, days=${days}`);
console.log('步骤 1/3: 构建 TypeScript CLI');
await run('pnpm', ['run', 'build']);

if (!skipInit) {
  console.log('步骤 2/3: 初始化数据库');
  await run('node', ['dist/index.js', 'init']);
} else {
  console.log('步骤 2/3: 跳过初始化（--skip-init）');
}

if (timeoutMs > 0) {
  console.log(`步骤 3/3: 执行 Agent Team 分析（超过 ${Math.round(timeoutMs / 1000)}s 将提示）`);
} else {
  console.log('步骤 3/3: 执行 Agent Team 分析');
}
await run('node', ['dist/index.js', 'team', code, '-q', question, '-d', days], {
  timeout: timeoutMs,
});
