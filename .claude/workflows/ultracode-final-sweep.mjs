export const meta = {
  name: 'ultracode-final-sweep',
  description: '全量扫尾：R270 治理幂等 + PCB 观察池后半抓取 + 差异判定 + verified 输出 + 23 PCB worktree 合入 main + 清理 + commit push',
  phases: [
    { title: 'Scan' },
    { title: 'Worktrees' },
    { title: 'Fetch+Verify' },
    { title: 'Governance R270' },
    { title: 'Ultracode v3' },
    { title: 'Commit+Push' },
  ],
}

phase('Scan')
const scan = await parallel([
  () => agent('盘点 /Users/bytedance/Develop/AStock git worktree：git -C /Users/bytedance/Develop/AStock worktree list --porcelain；逐个 cd 跑 git status --short；汇总：总数 / dirty 数 / 非 main 分支数。禁止新创 worktree。', {label:'scan-worktrees', phase:'Scan', effort:'medium'}),
  () => agent('分析 /Users/bytedance/Develop/AStock analysis/ 和 sources/：1) 找 analysis/verified_*.md / market_data_*.md / audit 归档；2) 非 PRIMARY sources/broker-reports 下 PCB 板块标的；3) 输出待抓取 PCB 观察池后半清单。', {label:'scan-pending-fetch', phase:'Scan', effort:'medium'}),
  () => agent('治理基线：ls workspace/governance/；读 core_artifact_checksums.md、root_artifact_inventory*.md（6 twins）、source_registry.md/json、claim_audit_manifest.md/json、verifier.log；对比 R269；列出 P0 修图影响范围。', {label:'scan-governance', phase:'Scan', effort:'high'}),
  () => agent('审查归档盘点：.agents/skills/exhibit-format-reviewer/**.md、workspace/review/ 下 *_R*.md、.agents/templates/reviewer_schema.md（若存在）；列出已完成 lens / 缺失 lens。', {label:'scan-ultracode', phase:'Scan', effort:'medium'}),
])
log('Scan 4 parallel done')

phase('Worktrees')
const wt = await agent(`
基于 scan-worktrees 列表：
FOR each worktree:
  1）cd <wt_path>；有改动 → git add -A；commit -m "chore(pcb): worktree sweep"
     分支非 main → git rebase -X ours main（冲突一律主仓真理）
  2）cd 主仓 /Users/bytedance/Develop/AStock
     分支 == main → merge --ff-only
     else → merge --no-ff --no-edit <wt_branch>
     git worktree remove --force <wt_path>
输出：总数 N / 冲突 M / 清理 P；合并明细 sha。
【硬规则：禁新 worktree；冲突 --theirs（主仓真理）】`,
  {label:'worktree-merge', phase:'Worktrees', effort:'xhigh', isolation:'worktree'})

phase('Fetch+Verify')
const batches = await parallel([
  () => agent(`
PCB 观察池后半 PCB 核心板块：
L1 来源（年报/交易所/IR slides）+ L2 一致预期 + L3 行业交叉。
结构化字段：ticker,name,industry,pe26e,peg,ps,net_growth_26e,driver,risk,sources[{id,level,url}]
严禁重复抓已归档标的。`,
    {label:'fetch-pcb', phase:'Fetch+Verify', effort:'max'}),
])
const verified = await agent(`
把 batches 的抓取结果分级：
A：两点 L1 交叉 ±5% → 金色入池
B：一点 L1 + 一点 L2 → 蓝色标注需再确认
C：纯 L2/L3 → 灰色观察池严禁入估值模型
L4 纯传闻 → 剔除。
写文件：
1）/Users/bytedance/Develop/AStock/analysis/verified_market_data.md
2）/Users/bytedance/Develop/AStock/analysis/market_data_quality_matrix.md
3）/Users/bytedance/Develop/AStock/data/verified_market_data.json（结构化）
输出 {counts_A, counts_B, counts_C, rejected:[tickers]}`,
  {label:'verify-write', phase:'Fetch+Verify', effort:'high',
   schema:{type:'object',required:['counts_A','counts_B','counts_C','rejected']}})

phase('Governance R270')
const gov = await agent(`
/Users/bytedance/Develop/AStock 主仓（禁 worktree）：
R270 幂等刷新。已知影响范围：
- workspace/research/ai-storage-supply-chain-20260623/sections/ch0{2,3,4,5,6,8,10}_*.tex
- main.pdf
- .agents/templates/preamble.tex
- analysis/verified_market_data.md
- data/verified_market_data.json
- analysis/market_data_quality_matrix.md
顺序纪律严格：
1) 若存在 scripts/source_governance/polling_refresh.sh → 执行 --idempotent
2) 否则手动：
   a. core_artifact_checksums.md → 对受影响文件重 sha256sum，未受影响行不变
   b. 6× root_artifact_inventory twins → 更新 AI 存储条目；追加 PCB data 条目（新增）
   c. source_registry → 若新增 L1 源分配 S/L-XX 号；不变则不动
   d. claim_audit_manifest → BLOCK 门控 + S-ID 可追溯；C 级 claim 禁入
   e. verifier → 必 PASS=X/0/Y（冲突=0） gate=PUBLISH
   f. 提交信息模板：R270 polling refresh — N SR + N CA + N core checksums + 6x inventory twins + verifier PASS=X/0/Y gate=PUBLISH
白名单硬规则：data/*.md/json / completion_audit_manifest.* / _r<N>_* 绝对不许进入修改；sources/broker-reports/ PRIMARY 不可变。`,
  {label:'r270', phase:'Governance R270', effort:'max', isolation:'worktree'})

phase('Ultracode v3')
const lensList = ['correctness','bias','compliance','valuation','visual','narrative']
const reviews = await parallel(
  lensList.map(function(l){ return function(){
    return agent(`
审查 AI 存储产业链研报 /Users/bytedance/Develop/AStock/workspace/research/ai-storage-supply-chain-20260623/（sections/*.tex + preamble）。
审查 lens = ${l}。
结构化 Schema 输出：
{
  review_lens:"${l}",
  overall: "PASS" or "CONDITIONAL" or "BLOCK",
  severity_counts:{P:int,A:int,B:int,C:int},
  findings:[{id:"F-${l}-nn", severity:"P|A|B|C", file:"sections/chXX_xxx.tex:Ln", claim:"≤30字", why:"", evidence:"", suggestion:"", block_if_unfixed:bool}],
  signature: "",
  gate: "PUBLISH" or "REVISE" or "BLOCK"
}
规则：P=BLOCK（阻止发布）/A 严重/B 中/C 轻。BLOCK 必须至少 1 P 级 finding block_if_unfixed=true。独立审查。`,
      {label:`review-${l}`, phase:'Ultracode v3', effort:'xhigh',
       schema:{type:'object',required:['review_lens','overall','severity_counts','findings','signature','gate'],
               properties:{review_lens:{type:'string'},
                           overall:{enum:['PASS','CONDITIONAL','BLOCK']},
                           severity_counts:{type:'object',required:['P','A','B','C']},
                           findings:{type:'array'},
                           signature:{type:'string'},
                           gate:{enum:['PUBLISH','REVISE','BLOCK']}}}})
  }})
)

phase('Commit+Push')
const cp = await agent(`
/Users/bytedance/Develop/AStock 主仓：
1）git status --porcelain；白名单违规范畴：data/*.md/json / completion_audit_manifest.* / _r<N>_* / sources/broker-reports/ → 若出现，报错并列清单，不进 commit
2）合法改动 → git add
3）commit message（两段式）：
   标题：R270 polling refresh（治理）+ 扫尾合入 + verified 输出 + Ultracode v3
   正文：
   - governance(ai-storage): R270 polling refresh — <取 gov 输出的 SR/CA/core checksums/6 twins/verifier 数字>
   - data(pcb): A 级 <counts_A> 只 / B 级 <counts_B> 只 / C 级 <counts_C> 只 / 剔除 L4 <rejected 列表>
   - chore(worktree): <worktrees 数> 个 worktree 全量合入 main + 清理；冲突 M 处主仓真理
   - review(ultracode-v3): 6 lens review 完成；总体 gate=取最严 BLOCK/REVISE/PUBLISH
   若任 lens gate=BLOCK → 正文加 ⚠ GATE=BLOCK 原因 + finding IDs
4）git commit
5）git fetch origin main；commit parent ≠ origin/main → git rebase -X ours origin/main
6）git push --force-with-lease origin main（禁 --force）
7）git fetch 后断言 HEAD sha == origin/main sha
输出：{sha, origin_sha, sync:bool, gate_summary:{worst, by_lens:{correctness,...,narrative}}, whitelist_violations:[], stats:{files, additions, deletions}}`,
  {label:'commit-push', phase:'Commit+Push', effort:'high',
   schema:{type:'object',required:['sha','origin_sha','sync','gate_summary','whitelist_violations','stats']}})

return {scan, worktrees: wt, verified, governance: gov, reviews: reviews, commit_push: cp}
