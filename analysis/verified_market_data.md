# Verified Market Data — 分级验证结果

> 数据源: `data/raw_market_data.json`
> as_of: 2026-06-23 | generated_at: 2026-06-23T17:29:52.762233
> 分级规则版本: v1.0
> 总记录数: 86 (A=61, B=23, C=2, 剔除=0)

---

## 一、分级规则定义

### 数据可信级 (L1/L2/L3/L4)

| 级别 | 来源范围 | 示例 |
|---|---|---|
| **L1 (官方/双源交叉)** | 交易所直连接口、主源+次源交叉验证一致、交易所披露统计量 | Tencent qt 实时行情、Tencent×Baidu T1 估值交叉(差≤±5%)、沪深港通北向持仓、交易所融资余额、Baidu 10年PE统计百分位 |
| **L2 (单源/折算/覆盖)** | 非官方主源但可追溯、同业折算得出、主源被次源覆盖(偏离>±5%) | Baidu T1 覆盖的 PE/PB、东财 EM Compare 推算 PS |
| **L3 (缺失/接口异常)** | 应该存在但本次未能获取到有效值 | 北向 not_in_batch / hsgt API TypeError、融资 sse ValueError / szse empty、PE/PB/PE10y 值 null |
| **L4 (纯传闻)** | 非交易所、无可追溯来源、小道消息/聊天截图级 | — (本次抓取未出现) |

### 分级判定矩阵

| 等级 | 判定条件 | 颜色 | 使用权限 |
|---|---|---|---|
| **A 金色** | **两点 L1 交叉 ±5% 通过** → 即 PE 与 PB 均达成 Tencent+Baidu T1 双源交叉验证一致，且≤1 项次要 L3 缺失 | 🟡 金色 | 可直接进入估值模型 (DCF / 可比 / 赔率校准) |
| **B 蓝色** | **一点 L1 交叉 + 一点 L2/L3** → PE 或 PB 任一达成双交叉但另一项被覆盖/降级；或双交叉均通过但次要字段缺失≥2 | 🔵 蓝色 | 标注"需再确认"，必须补充第二个独立交叉源后方可入估值模型 |
| **C 灰色** | **纯 L2/L3，核心字段无交叉** → PE/PB 均未达成 L1×L1 双交叉验证(被覆盖、或为 null) | ⚪ 灰色 | 仅可进入观察池，**严禁**直接作为估值模型输入，仅可用于行业热度 / 拥挤度辅助判断 |
| **L4 剔除** | 全部核心字段不可靠 / 纯传闻级 | ❌ 红 | 从研究池剔除，任何结论不得引用 |

---

## 二、系统性警告 (对所有记录生效)

- `BS_login_failed: 网络接收错误。` — baostock 日线级行情接口本轮登录失败，导致本批次缺失独立的交易所日线第三交叉源。当前所有估值交叉仅依赖 Tencent ↔ Baidu T1 双源，缺少日线级复权价格独立校验。**建议下一轮抓取前修复 baostock 登录链路**，将 PE/PB/returns 的交叉点数从 2 提升至 3。
- `EM_fail` 全线标记 — 东财主接口批量不可用，所有 PS 均退化为 `EM Compare` 同业折算，PS 字段整体视为 L2。对 PS 驱动的估值模型(如光模块 PCB)，需额外以营业收入独立校验。

---

## 三、A 级 · 金色入池 (可直接入估值模型)

共 **61** 只，满足 PE 与 PB 双 L1 交叉 ±5% 且次要字段 L3 缺失 ≤ 1。

| 代码 | 名称 | 日期 | 价格 | PE(TTM) | PB | PS(TTM) | 总市值(亿) | L1 验证字段 | 备注 |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| 688187 | 时代电气 | 2026-06-23 | 61.58 | 20.26 | 1.92 | 2.8355991 | 829.92亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300373 | 扬杰科技 | 2026-06-23 | 132.96 | 57.4 | 7.5 | 9.40573393 | 722.44亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603290 | 斯达半导 | 2026-06-23 | 138.8 | 82.02 | 4.86 | 8.39943967 | 332.39亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600011 | 华能国际 | 2026-06-23 | 7.78 | 8.48 | 1.74 | 0.54103603 | 1221.31亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600795 | 国电电力 | 2026-06-23 | 4.81 | 11.98 | 1.4 | 0.5058334 | 857.89亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600900 | 长江电力 | 2026-06-23 | 26.87 | 19.06 | 2.88 | 7.52776026 | 6574.61亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002920 | 德赛西威 | 2026-06-23 | 84.04 | 20.44 | 3.31 | 1.55471897 | 501.56亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603596 | 伯特利 | 2026-06-23 | 26.5 | 18.17 | 3.04 | 1.97397738 | 237.87亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002371 | 北方华创 | 2026-06-23 | 747.49 | 98.12 | 13.79 | 13.06500658 | 5418.05亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688271 | 联影医疗 | 2026-06-23 | 102.52 | 45.2 | 3.85 | 5.93769876 | 844.93亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300760 | 迈瑞医疗 | 2026-06-23 | 139.38 | 20.77 | 4.38 | 5.06003833 | 1689.9亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300274 | 阳光电源 | 2026-06-23 | 152.0 | 23.41 | 6.67 | 3.67674076 | 3151.28亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600995 | 南网储能 | 2026-06-23 | 12.72 | 24.08 | 1.79 | 5.30030283 | 406.53亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 605111 | 新洁能 | 2026-06-23 | 79.91 | 84.32 | 7.79 | 17.06323467 | 331.89亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600027 | 华电国际 | 2026-06-23 | 4.76 | 9.11 | 1.11 | 0.44995568 | 552.72亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603197 | 保隆科技 | 2026-06-23 | 28.73 | 28.91 | 1.94 | 0.67704596 | 61.49亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688037 | 芯源微 | 2026-06-23 | 283.77 | 797.93 | 20.43 | 28.55423051 | 572.16亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688029 | 南微医学 | 2026-06-23 | 71.5 | 23.55 | 3.31 | 4.02325789 | 134.31亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002335 | 科华数据 | 2026-06-23 | 38.41 | 68.68 | 4.61 | 3.96787361 | 287.06亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300750 | 宁德时代 | 2026-06-23 | 392.51 | 25.15 | 5.56 | 3.87927302 | 18159.97亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300014 | 亿纬锂能 | 2026-06-23 | 67.28 | 35.37 | 3.39 | 2.10832503 | 1462.19亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002594 | 比亚迪 | 2026-06-23 | 85.0 | 23.76 | 3.34 | 0.18029724 | 7749.62亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002074 | 国轩高科 | 2026-06-23 | 29.55 | 22.49 | 1.85 | 1.12335495 | 536.1亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002821 | 凯莱英 | 2026-06-23 | 128.7 | 41.0 | 2.59 | 6.69943158 | 464.33亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600276 | 恒瑞医药 | 2026-06-23 | 48.98 | 42.16 | 5.21 | 9.98299816 | 3250.9亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300759 | 康龙化成 | 2026-06-23 | 23.7 | 26.17 | 2.65 | 2.98761917 | 435.44亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603288 | 海天味业 | 2026-06-23 | 34.18 | 28.42 | 5.36 | 6.76052832 | 2000.15亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603693 | 江苏新能 | 2026-06-23 | 13.45 | 23.63 | 1.7 | 5.93496517 | 119.9亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600460 | 士兰微 | 2026-06-23 | 47.04 | 196.41 | 6.42 | 5.76806647 | 782.78亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603916 | 苏博特 | 2026-06-23 | 14.7 | 51.79 | 1.49 | 0.40977864 | 62.67亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300496 | 中科创达 | 2026-06-23 | 63.06 | 64.68 | 2.82 | 3.6134022 | 291.16亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603786 | 科博达 | 2026-06-23 | 45.07 | 21.95 | 3.3 | 2.60659905 | 182.02亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002405 | 四维图新 | 2026-06-23 | 7.04 | 161.16 | 1.89 | 3.94875606 | 166.86亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002284 | 亚太股份 | 2026-06-23 | 10.06 | 15.17 | 2.17 | 1.30293214 | 74.35亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300685 | 艾德生物 | 2026-06-23 | 17.25 | 18.63 | 3.6 | 5.67401054 | 67.29亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002223 | 鱼跃医疗 | 2026-06-23 | 25.05 | 16.95 | 1.92 | 3.18296438 | 251.12亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300003 | 乐普医疗 | 2026-06-23 | 11.94 | 22.88 | 1.34 | 3.42919371 | 220.1亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600886 | 国投电力 | 2026-06-23 | 13.33 | 14.43 | 1.55 | 2.03600602 | 1067.0亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 000690 | 宝新能源 | 2026-06-23 | 4.96 | 10.53 | 0.85 | 1.23314487 | 107.92亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688017 | 绿的谐波 | 2026-06-23 | 378.53 | 557.99 | 19.45 | 113.23999304 | 693.96亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 601689 | 拓普集团 | 2026-06-23 | 58.02 | 36.28 | 4.25 | 3.31216907 | 1008.29亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002050 | 三花智控 | 2026-06-23 | 43.19 | 44.73 | 5.57 | 5.84088576 | 1817.44亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002906 | 华阳集团 | 2026-06-23 | 26.31 | 17.67 | 2.0 | 1.01141487 | 138.11亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300502 | 新易盛 | 2026-06-23 | 552.0 | 80.74 | 39.64 | 6.90643219 | 7696.3亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300763 | 锦浪科技 | 2026-06-23 | 90.43 | 48.43 | 4.02 | 5.25284933 | 359.97亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600406 | 国电南瑞 | 2026-06-23 | 23.17 | 22.48 | 3.48 | 2.78178011 | 1860.96亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688041 | XD海光信 | 2026-06-23 | 317.0 | 289.53 | 31.83 | 46.02122778 | 7368.15亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688261 | 东微半导 | 2026-06-23 | 99.28 | 263.34 | 4.13 | 9.73868569 | 121.69亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002080 | 中材科技 | 2026-06-23 | 76.8 | 70.9 | 6.54 | 164.02646029 | 1288.8亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002463 | 沪电股份 | 2026-06-23 | 138.5 | 69.73 | 16.84 | 12.61847878 | 2665.24亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002916 | 深南电路 | 2026-06-23 | 426.0 | 88.58 | 17.63 | 11.39751565 | 2901.77亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002938 | 鹏鼎控股 | 2026-06-23 | 106.91 | 66.29 | 7.67 | 6.3455317 | 2477.68亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300476 | 胜宏科技 | 2026-06-23 | 338.2 | 77.08 | 21.22 | 12.61847878 | 3323.78亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 300576 | 容大感光 | 2026-06-23 | 51.22 | 175.03 | 12.0 | 18.83117992 | 206.77亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600176 | 中国巨石 | 2026-06-23 | 58.93 | 71.8 | 7.48 | 164.02646029 | 2359.05亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 600183 | 生益科技 | 2026-06-23 | 167.87 | 122.31 | 25.51 | 13.1705469 | 4077.76亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 601138 | 工业富联 | 2026-06-23 | 74.1 | 41.67 | 8.34 | 2.43473466 | 14704.47亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603002 | 宏昌电子 | 2026-06-23 | 23.35 | 748.64 | 7.7 | 7.55280015 | 264.81亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 603228 | 景旺电子 | 2026-06-23 | 72.96 | 58.37 | 5.63 | 12.61847878 | 718.55亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 688630 | 芯碁微装 | 2026-06-23 | 462.89 | 210.33 | 26.21 | 36.28552919 | 609.81亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| 002436 | 兴森科技 | 2026-06-23 | 48.5 | 610.87 | 15.59 | 11.0900152 | 824.34亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |

---

## 四、B 级 · 蓝色需再确认 (补充交叉源后方可入模型)

共 **23** 只。分级原因集中在三类：
1. PE 或 PB 其中之一被 `Baidu T1 override` 覆盖(主/次源偏离 >5%)，导致仅单点 L1 交叉
2. 双核心交叉通过但 **北向持仓 + 融资余额** 同时缺失 (L3≥2)
3. PE 或 PB 为 null，仅另一个核心 + 次源 L2 支撑

| 代码 | 名称 | 日期 | 价格 | PE(TTM) | PB | PS(TTM) | 总市值(亿) | L1 验证字段 | 需确认事项 |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| 688326 | 经纬恒润-W | 2026-06-23 | 72.81 | 204.37 | 2.21 | 1.30518403 | 87.33亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688012 | 中微公司 | 2026-06-23 | 371.72 | 129.06 | 13.65 | 26.83080195 | 3521.9亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688072 | 拓荆科技 | 2026-06-23 | 770.0 | 128.6 | 30.32 | 31.44289389 | 2176.74亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688396 | 华润微 | 2026-06-23 | 80.8 | 118.28 | 4.64 | 9.28666735 | 1073.19亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688235 | 百济神州 | 2026-06-23 | 228.0 | 111.11 | 10.64 | 8.63048706 | 3514.44亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 300655 | 晶瑞电材 | 2026-06-23 | 17.16 | 170.88 | 7.55 | 11.65093435 | 193.33亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688521 | 芯原股份 | 2026-06-23 | 285.0 | N/A | 47.63 | 41.65215412 | 1498.86亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| 600905 | 三峡能源 | 2026-06-23 | 4.0 | 49.56 | 1.27 | 4.12532946 | 1143.51亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 300308 | 中际旭创 | 2026-06-23 | 1310.01 | 103.13 | 42.17 | 6.90643219 | 14609.69亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688256 | 寒武纪 | 2026-06-23 | 1413.0 | 326.75 | 72.54 | 107.34279756 | 8877.78亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 600703 | 三安光电 | 2026-06-23 | 19.83 | N/A | 2.83 | 5.97991467 | 989.32亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| 688234 | 天岳先进 | 2026-06-23 | 163.37 | N/A | 11.13 | 55.65991421 | 791.72亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| 002384 | 东山精密 | 2026-06-23 | 255.02 | 242.9 | 20.63 | 12.61847878 | 4670.97亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 002636 | 金安国纪 | 2026-06-23 | 108.64 | 173.51 | 21.24 | 16.54260998 | 790.9亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 301217 | 铜冠铜箔 | 2026-06-23 | 171.81 | 867.2 | 25.89 | 19.95954973 | 1424.33亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 601208 | 东材科技 | 2026-06-23 | 71.85 | 190.81 | 11.92 | 13.21998773 | 725.82亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 603186 | 华正新材 | 2026-06-23 | 231.6 | 131.23 | 15.64 | 7.93976133 | 363.13亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |
| 603256 | 宏和科技 | 2026-06-23 | 247.9 | 720.42 | 82.75 | 164.02646029 | 2242.47亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 300400 | 劲拓股份 | 2026-06-23 | 41.51 | 119.93 | 14.25 | 12.59977874 | 100.71亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |
| 301200 | 大族数控 | 2026-06-23 | 346.44 | 164.41 | 15.39 | 25.03041412 | 1694.12亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 301377 | 鼎泰高科 | 2026-06-23 | 600.0 | 436.55 | 91.07 | 97.40008336 | 2468.48亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688519 | 南亚新材 | 2026-06-23 | 333.0 | 212.04 | 27.81 | 12.82269106 | 783.15亿 | price(Tencent)；returns(Tencent)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 002949 | 华阳国际 | 2026-06-23 | 10.91 | 23.61 | 1.5 | 1.87998775 | 21.39亿 | price(Tencent)；returns(Tencent)；PE(Tencent+Baidu交叉,±5%)；PB(Tencent+Baidu交叉,±5%)；PE10y百分位(Baidu统计) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |

---

## 五、C 级 · 灰色观察池 (严禁入估值模型)

共 **2** 只。PE 与 PB 两个核心指标均未达成 L1×L1 双源 ±5% 交叉，或全部为 L2 覆盖值 / L3 缺失。仅作为行业轮动 / 拥挤度观察的辅助信号，任何估值结论不得引用。

| 代码 | 名称 | 日期 | 价格 | PE(TTM) | PB | PS(TTM) | 总市值(亿) | L1 验证字段 | 降级原因 |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| 300782 | 卓胜微 | 2026-06-23 | 113.92 | N/A | 6.65 | 17.24724469 | 655.03亿 | price(Tencent)；returns(Tencent)；北向持仓(HSGT交易所)；融资余额(交易所) | PE 与 PB 均未达成 L1×L1 双交叉验证 → 灰色观察池，严禁入估值模型；PB 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| 688368 | 晶丰明源 | 2026-06-23 | 207.36 | 537.65 | 13.1 | 22.80243037 | 422.26亿 | price(Tencent)；returns(Tencent)；PE10y百分位(Baidu统计)；融资余额(交易所) | PE 与 PB 均未达成 L1×L1 双交叉验证 → 灰色观察池，严禁入估值模型；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5%；PB 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |

---

## 六、L4 级 · 剔除名单 (纯传闻)

本次 86 条全部为交易所 / 行情源正规渠道抓取，无纯传闻级标的。**L4 剔除 0 只。**

---

## 七、下一轮数据刷新优先事项

1. **修复 baostock 登录链路** → 增加第 3 个 L1 源(日线级复权、TTM 净利润独立计算)，可将 A 级数量预期提升 ≥15 只。
2. **修复 EM(东方财富) ulist / pankou 接口** → 将 PS 从 L2 同业折算升级为 L1 财务口径直取，PCB/光模块行业的 PS 估值模型可直接入池。
3. **北向持仓 HSGT 批次补全** → 标记 `not_in_batch` 的 14 只与 `hsgt_api TypeError` 的 2 只，补全后可将约 8 只 B 级 → A 级。
4. **上交所融资余额 ValueError 修复** → 受影响的 3 只 (603002 宏昌电子 / 603256 宏和科技 / 603186 华正新材) 将从 B→A。
