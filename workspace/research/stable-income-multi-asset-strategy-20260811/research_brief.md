# Research Brief — 稳健多资产配置策略

- Case ID: stable-income-multi-asset-strategy-20260811
- Scope ID: strategic-allocation-etf-first-v2-20260811
- Report type: 条件性战略资产配置研究
- Objective: 以固定CNY200,000全额投资本金，建立可复核的流动性、利率债、红利权益ETF与非杠杆黄金风险预算；不把历史分红或某日价格转化为收益承诺。
- Language: 中文报告
- Data cutoff: 2026-08-11；当前策略范围不使用个股价格或历史股息率快照。

## Designated model implementation

The model targets are CNY40,000 eligible protected liquidity, CNY10,000 staging cash, CNY70,000 511010, CNY30,000 510880, conditional CNY30,000 512890, and CNY20,000 518880. Public REITs and direct stocks remain CNY0 at launch. They are conditional model notionals, not live broker orders; no price, share quantity, entry timing or return forecast is asserted.

The required execution-eligibility policy is data/execution_eligibility_policy_20260812.json. Its status is not_run: no current ETF is marked eligible. It requires current-session source/timestamp fields, product/trading documentation, price/IOPV, premium/discount, spread, liquidity, account/lot feasibility and, for 512890, dated combined holdings. The model controls are absolute premium/discount at most 1.00%, quoted spread at most 0.50% of mid, and tranche size at most 10% of recorded same-session traded value or executable depth.

The fallback is deterministic. A failed or missing ETF check produces no trade and routes only the affected notional to eligible protected liquidity. Staging cash never exceeds CNY10,000; no failure automatically increases 511010, a correlated ETF, REITs or direct stocks. A later allocation needs a fresh pass at the next scheduled tranche or rebalance.

## 范围冻结

本案采用ETF/资产层优先的基准稳健核心版。直接高股息股票的初始配置为0%，且当前没有指定个股；只有在独立完成估值、现金流、集中度、流动性和税务核验后，才可从红利权益ETF桶中替换，合计不超过15%、单一发行人不超过5%。直接股票不构成组合收益模型。

## 基准稳健核心版

| 资产层 | 权重 | 固定CNY200,000金额 | 组合角色 |
|---|---:|---:|---|
| 组合内受保障流动性 | 20% | CNY40,000 | 防守与用途匹配；唯一承接未通过ETF核验的余额。 |
| 交易现金 | 5% | CNY10,000 | 分批实施和再平衡缓冲；硬上限CNY10,000，不等同于存款保险。 |
| 高质量人民币利率债 | 35% | CNY70,000 | 指定511010；仅在执行日q=1时建立。 |
| 红利权益ETF | 30% | CNY60,000 | 指定510880和条件性512890；后者未通过穿透时保持0。 |
| 非杠杆黄金ETF | 10% | CNY20,000 | 指定518880；仅在执行日q=1时分批。 |
| 公募REITs | 0% | CNY0 | 只有三只独立项目均通过审查时，才可从利率债桶转入最多5%。 |
| 直接高股息股票 | 0% | CNY0 | 无指定个股；未来只能在独立研究后替换红利权益ETF暴露。 |
| 合计 | 100% | CNY200,000 |  |

## 回报、现金与风险口径

- 长期规划区间为年化3%--6%的公式敏感性；r是税费、交易成本和基金费用之前的假设名义总回报参数，不是预测或现金分配率。
- D0只记录过去12个月实际税后、扣费后到账现金，并要求到账日、来源、税费、净额和凭证。r不预测D0，D0也不来自公式案例。
- 基准稳健核心的12个月共同承压情景为-16.30%，固定本金下约CNY32,600；它是情景算术，不是最大损失或回撤触发。
- 实际控制只使用账户价值、外部现金流调整和高水位记录计算的DD_t；已记录DD_t达到-12%/-18%才分别触发复核/处理。

## 适用条件与排除项

- 资金期限至少五年，且可承受权益、利率与黄金同时承压；三年内确定用途的资金不应自动套用本模型。
- 报告不提供个股目标价、短线择时、下单价格/数量/通道、保证收益或自动交易；它定义的是条件性模型标的、金额、计划顺序、资格包和失败资金位置。
- 在完成实施日资格包和独立复核前，报告只是研究草案，不是交易、适当性或对外投资建议依据。
