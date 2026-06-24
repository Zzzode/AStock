# Market Data Quality Matrix
> 数据源: `data/raw_market_data.json` (as_of 2026-06-23, 总记录 86 条)
> 分级规则: v1.0 — 基于 L1/L2/L3 数据源交叉验证，详见 `verified_market_data.md`

## 分级统计

| 等级 | 定义 | 数量 | 占比 | 入池权限 |
|---|---|---:|---:|---|
| A 金色 | PE/PB 双 L1 交叉 ±5% 通过 | 61 | 70.9% | 可直接进入估值模型 |
| B 蓝色 | 单 L1 交叉 + 降级项，或双交叉但次要缺失 | 23 | 26.7% | 标注需再确认，二次验证后可用 |
| C 灰色 | 核心字段未达成 L1 双交叉 / 降级覆盖 | 2 | 2.3% | 观察池，严禁入估值模型 |
| L4 剔除 | 纯传闻，核心字段全不可用 | 0 | 0.0% | 从研究池剔除 |

## 系统性警告
所有 86 条记录均存在 `BS_login_failed:网络接收错误。`，意味着 baostock 日线流本次抓取失败，已退化为 Tencent 行情 + Baidu T1 估值交叉 + 交易所单边融资/北向接口。下一轮刷新需修复 baostock 登录链路，增加第 3 点交叉源。

## 逐条质量矩阵
| Grade | 代码 | 名称 | L1数 | L2数 | L3数 | L1字段 | L2字段 | L3字段 | 分级判定 |
|---|---|---|---:|---:|---:|---|---|---|---|
| A | 000690 | 宝新能源 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002050 | 三花智控 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002074 | 国轩高科 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002080 | 中材科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002223 | 鱼跃医疗 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002284 | 亚太股份 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002335 | 科华数据 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002371 | 北方华创 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002405 | 四维图新 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002436 | 兴森科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002463 | 沪电股份 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002594 | 比亚迪 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002821 | 凯莱英 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002906 | 华阳集团 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002916 | 深南电路 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002920 | 德赛西威 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 002938 | 鹏鼎控股 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300003 | 乐普医疗 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300014 | 亿纬锂能 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300274 | 阳光电源 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300373 | 扬杰科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300476 | 胜宏科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300496 | 中科创达 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300502 | 新易盛 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300576 | 容大感光 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300685 | 艾德生物 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300750 | 宁德时代 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300759 | 康龙化成 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300760 | 迈瑞医疗 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 300763 | 锦浪科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600011 | 华能国际 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600027 | 华电国际 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600176 | 中国巨石 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600183 | 生益科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600276 | 恒瑞医药 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600406 | 国电南瑞 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600460 | 士兰微 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600795 | 国电电力 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600886 | 国投电力 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600900 | 长江电力 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 600995 | 南网储能 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 601138 | 工业富联 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 601689 | 拓普集团 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603002 | 宏昌电子 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所) | PS(EMCompare折算) | 融资余额(交易所异常) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603197 | 保隆科技 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603228 | 景旺电子 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603288 | 海天味业 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603290 | 斯达半导 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603596 | 伯特利 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603693 | 江苏新能 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603786 | 科博达 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 603916 | 苏博特 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 605111 | 新洁能 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688017 | 绿的谐波 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688029 | 南微医学 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688037 | 芯源微 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688041 | XD海光信 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688187 | 时代电气 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688261 | 东微半导 | 8 | 1 | 1 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688271 | 联影医疗 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| A | 688630 | 芯碁微装 | 9 | 1 | 0 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | - | PE 与 PB 均通过 L1×L1 交叉 ±5% 验证 (L1核心交叉点数=4) |
| B | 002384 | 东山精密 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 002636 | 金安国纪 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 002949 | 华阳国际 | 7 | 1 | 2 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计) | PS(EMCompare折算) | 北向持仓(API错误)、融资余额(交易所异常) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |
| B | 300308 | 中际旭创 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 300400 | 劲拓股份 | 7 | 1 | 2 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计) | PS(EMCompare折算) | 北向持仓(API错误)、融资余额(交易所异常) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |
| B | 300655 | 晶瑞电材 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 301200 | 大族数控 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 301217 | 铜冠铜箔 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 301377 | 鼎泰高科 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 600703 | 三安光电 | 6 | 1 | 2 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | PE(null)、PE10y(null) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| B | 600905 | 三峡能源 | 6 | 2 | 1 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 601208 | 东材科技 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 603186 | 华正新材 | 7 | 1 | 2 | price(Tencent)、returns(Tencent)、PE(Tencent+Baidu交叉,±5%)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计) | PS(EMCompare折算) | 北向持仓(API错误)、融资余额(交易所异常) | PE 与 PB 双交叉 OK，但有 2 项次要字段缺失/降级→需确认 |
| B | 603256 | 宏和科技 | 6 | 2 | 1 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所) | PE(Baidu-override)、PS(EMCompare折算) | 融资余额(交易所异常) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688012 | 中微公司 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688072 | 拓荆科技 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688234 | 天岳先进 | 6 | 1 | 2 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | PE(null)、PE10y(null) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| B | 688235 | 百济神州 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688256 | 寒武纪 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688326 | 经纬恒润-W | 6 | 2 | 1 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688396 | 华润微 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688519 | 南亚新材 | 7 | 2 | 0 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、PE10y百分位(Baidu统计)、北向持仓(HSGT交易所)、融资余额(交易所) | PE(Baidu-override)、PS(EMCompare折算) | - | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| B | 688521 | 芯原股份 | 6 | 1 | 2 | price(Tencent)、returns(Tencent)、PB(Tencent+Baidu交叉,±5%)、北向持仓(HSGT交易所)、融资余额(交易所) | PS(EMCompare折算) | PE(null)、PE10y(null) | PE 非 L1 双交叉(被覆盖或缺)，仅 PB 双交叉通过 → 需再确认 |
| C | 300782 | 卓胜微 | 4 | 2 | 2 | price(Tencent)、returns(Tencent)、北向持仓(HSGT交易所)、融资余额(交易所) | PB(Baidu-override)、PS(EMCompare折算) | PE(null)、PE10y(null) | PE 与 PB 均未达成 L1×L1 双交叉验证 → 灰色观察池，严禁入估值模型；PB 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |
| C | 688368 | 晶丰明源 | 4 | 3 | 1 | price(Tencent)、returns(Tencent)、PE10y百分位(Baidu统计)、融资余额(交易所) | PE(Baidu-override)、PB(Baidu-override)、PS(EMCompare折算) | 北向持仓(not_in_batch) | PE 与 PB 均未达成 L1×L1 双交叉验证 → 灰色观察池，严禁入估值模型；PE 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5%；PB 被 Baidu T1 覆盖，Tencent 与 Baidu 偏离 >5% |

## 被剔除标的 (L4 纯传闻)
无 (本次批次全部为交易所行情，非传闻级)
