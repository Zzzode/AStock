# Data Verification Checklist

## Before ANY number enters the report

- [ ] Source identified (filing number / URL / database)
- [ ] Date of data point recorded
- [ ] Cross-referenced against at least 1 independent source
- [ ] Confidence level assigned (High/Medium/Low)
- [ ] Accounting basis noted (归母 vs 合并, 扣非 vs 非扣非)

## Market Data Specific

- [ ] Stock price date is within 3 trading days of report date
- [ ] Market cap calculated as: current price × total shares (not from old reports)
- [ ] Free-float distinguished from total shares (check for lock-ups)
- [ ] Free-float market cap = price × (total - locked) shares
- [ ] Trading volume is 5-7 day recent average (not 20-day from weeks ago)
- [ ] Northbound holding checked from 深股通/沪股通 actual daily data
- [ ] Lock-up expiry dates confirmed from company announcements (not third-party summaries)

## Financial Data Specific

- [ ] Revenue and profit match the SAME reporting period
- [ ] Growth rate calculated by you: (new - old) / old (don't trust pre-calculated)
- [ ] Profit basis clearly labeled: 归母净利 vs 扣非净利 vs 合并净利
- [ ] If company is in loss, noted as "亏损" not as a negative percentage
- [ ] Segment data (if used) sums to consolidated total

## Known Traps

| Trap | Example | Prevention |
|------|---------|-----------|
| 归母≠合并 | 德赛西威 归母4.61亿 vs 合并7.90亿 | Always label which basis |
| 流通≠总股本 | Many companies have 10-40% locked | Check 流通A股 specifically |
| 北向≈陆股通 but not identical | Some reports mix concepts | Use 深股通/沪股通 持股 data |
| 日均成交额 regime change | Before/after GTC: 35亿→150亿 | Note catalyst and use recent window |
| "解禁18.5%" may be old | May have already partially sold | Check if 已完成 vs 将解禁 |
| 券商一致预期 | Has 50-100% upward bias | Always note bias, use as ceiling not target |
