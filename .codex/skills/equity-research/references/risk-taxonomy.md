# Risk Taxonomy Reference

## Standard 22-Factor Framework (A-F × L2-L4)

### Severity Levels

| Level | Meaning | Portfolio Impact | Probability Threshold | Action Required |
|-------|---------|-----------------|----------------------|-----------------|
| L4 (Extreme) | Can cause >30% loss | Catastrophic | Any probability | Must have hedge/exit plan |
| L3 (High) | 15-30% loss on affected names | Severe | >30% annual probability | Must monitor weekly |
| L2 (Medium) | 5-15% loss | Manageable | >20% | Monthly review sufficient |

### Category A: Technology & Commercialization

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| A1: Commercialization pace slower than narrative | L3 | Coalition member count; POC→production conversion rate |
| A2: Model accuracy insufficient for industrial use | L3 | MLCommons benchmark rankings; customer case studies |
| A3: Sim-to-Real gap unexpectedly large | L2 | Robot task success rate in field vs sim |
| A4: Hardware capacity ramp delay | L3 | NVIDIA official production guidance; lead times |

### Category B: Competition

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| B1: Domestic substitute (Huawei/昇腾) captures share | L3 | Quarterly domain controller market share reports |
| B2: Closed ecosystem (Tesla) doesn't spill over | L2 | Optimus teardown reports; supplier disclosures |
| B3: Domestic component substitution too fast | L2 | 华经情报网 market share data |
| B4: Open-source competitors replicate capabilities | L2 | GitHub activity; academic paper reproduction times |

### Category C: Macro & Policy

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| C1: US-China Jetson/DRIVE export ban | **L4** | BIS federal register; diplomatic signals |
| C2: Domestic procurement mandate acceleration | L2 | 信创 bidding proportion; government policy documents |
| C3: A-share liquidity contraction | L3 | DR007; northbound weekly net flow; margin balance |
| C4: Regulatory crackdown on concept stocks | L3 | Exchange inquiry letter count; 立案 announcements |

### Category D: Earnings & Valuation

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| D1: Q2 core holdings miss consensus | L3 | Pre-announcement dates; channel checks |
| D2: Full-year profit below expectations | L3 | Q2 trajectory slope; management guidance |
| D3: Sentiment PE mean-reversion (valuation kill) | **L4** | PE percentile >95th; sector turnover rate declining |
| D4: Order-to-revenue conversion slower than PPT | L2 | Announced orders vs confirmed revenue gap |

### Category E: Capital & Flows

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| E1: July-September lock-up expiry wave | **L4** | 解禁 calendar; pre-announcement reduction filings |
| E2: Northbound continuous selling | L3 | 5-day cumulative >100亿 net outflow |
| E3: Institutional rebalancing (e.g., for IPO subscription) | L2 | Quarterly fund reports top-10 changes |
| E4: Block trade panic (large discounts) | L3 | Block trade discount >15% |

### Category F: Execution (Investor's Own Control)

| Factor | Typical Level | Key Indicators |
|--------|--------------|----------------|
| F1: Single-position concentration >20% | L3 | Your own portfolio allocation |
| F2: Buying in bubble zone (>Bull target +10%) | **L4** | Entry price vs three-tier targets |
| F3: Failure to stop-loss (narrative breaks but hold) | L3 | Position below Bear target for >5 days |
| F4: Catalyst timing misjudgment | L2 | Announced timeline vs actual delivery |

## ESG Hard Red Flag (HRF) Quick Reference

| # | Category | Trigger | Consequence |
|---|----------|---------|-------------|
| 1 | E-Fine | Single environmental penalty ≥1M RMB (3yr) | Prohibited |
| 2 | E-Incident | Major/extraordinary environmental event (5yr) | Prohibited |
| 3 | S-Safety | ≥3 fatalities (3yr) or wage blacklist | Prohibited |
| 4 | S-Data | Data security fine ≥5M RMB | Prohibited |
| 5 | G-Audit | Adverse/disclaimer/going concern opinion | Prohibited |
| 6 | G-Fraud | CSRC-confirmed financial fraud (5yr) | Prohibited |
| 7 | G-Criminal | Controller arrested/detained/留置 | Prohibited |
| 8 | G-Pledge | Controller pledge ≥80% AND at margin call | Prohibited |
| 9 | G-Litigation | ≥3 securities false statement suits + adverse judgment | Prohibited |
| 10 | G-Investigation | Active CSRC investigation against company | Prohibited |

## Emergency Response Protocol

| Trigger | Severity | Immediate Action | Observation Period | Recovery Signal |
|---------|----------|-----------------|-------------------|----------------|
| BIS ban on Jetson/DRIVE | L4 | Cut NVIDIA-linked 70%; cash to 40% | Monitor diplomacy | Ban lifted OR domestic alternative verified 6mo |
| Sector -8% single day + 2× volume | L4 | Exit high-PE; cut core 30% | 3 days | 3-day stabilization + NB net inflow |
| Major lock-up + block discount >15% | L3 | Exit affected name; reduce related 50% | 10 days | Discount normalizes to <5% |
| NB sells >100B in 5 days | L3 | Cut A-grade 20%; raise defense to 30% | Weekly | NB net buy for 3 consecutive days |
| ≥3 exchange inquiry letters | L3 | Exit concept stocks; cut high-PE 30% | 1 month | Regulatory tone softens |
| 2+ core holdings miss Q2 | L3 | Cut miss names 50%; preemptive cut same-layer 15% | Next quarter | Company provides clear recovery timeline |
| Key catalyst fails (e.g., Optimus delayed to 2028) | L2 | Cut related path 40% | Until new catalyst | New catalyst confirmed + consensus not revised down |
| Huawei gains +5pct domain controller share | L2 | Cut Desay 20%; add Huawei-chain hedge | Next quarter | Share stops growing + new Desay design wins |
