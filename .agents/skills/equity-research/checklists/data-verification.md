# Data Verification Checklist

## Before ANY number enters the report

- [ ] `gate_manifest.md/json` declares the data cutoff, required data artifacts, owner skills, and pass conditions
- [ ] `artifact_contract.md/json` declares the schema for every data, source, model, review, and sign-off artifact
- [ ] Source identified (filing number / URL / database)
- [ ] Date of data point recorded
- [ ] Cross-referenced against at least 1 independent source
- [ ] Confidence level assigned (High/Medium/Low)
- [ ] Accounting basis noted (归母 vs 合并, 扣非 vs 非扣非)

## Supply-Chain Evidence Specific

- [ ] Full industry-chain reports start from `data/full_chain_universe_<YYYYMMDD>.md/json`, not a short concept-stock table
- [ ] Every full-chain universe row has `node_type` (`listed`, `overseas`, `private`, `demand_anchor`, `low_purity`, or `unavailable`)
- [ ] Core valuation pool, satellite watch pool, demand anchors, low-purity names, and unavailable nodes are separated in `analysis/core_vs_satellite_universe.md`
- [ ] Missing chain blocks, private/overseas sources, customer evidence, or valuation blockers are listed in `analysis/coverage_gap_matrix.md`
- [ ] Named customer/platform/order/certification/capacity claims have source path, original URL, source type, date, and confidence
- [ ] Revenue exposure is official-disclosed, broker-stated, inferred, or explicitly `not disclosed`
- [ ] Capacity is not converted to revenue without utilization, qualification, order, or price evidence
- [ ] Demand anchors are separated from supplier revenue evidence
- [ ] `analysis/value_chain_economics.md` covers value amount/proxy, ASP or price proxy, margin pool, supply/demand, capacity/utilization/yield, certification/customer qualification, order visibility, and valuation credit

## Growth Earnings Evidence Specific

- [ ] High-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP claims have a completed `growth-earnings-model` gate when used for valuation credit
- [ ] Unit volume, order value, backlog, capacity utilization, shipment schedule, customer allocation, ASP or price proxy, recognized revenue ratio, gross margin, opex, tax, shares, and EPS contribution each have a source or an explicit `not disclosed` label
- [ ] Base business and growth segment data are separated before applying high-growth multiples
- [ ] Current-price-implied growth is recalculated from current market data and not copied from broker narrative
- [ ] Generic AI demand, downstream TAM, capacity, or one strong quarter is not used as direct revenue, EPS, or target-price support without conversion evidence
- [ ] Value-chain economics supports any EPS credit; otherwise the growth driver is marked `watchlist only / insufficient economics`

## Source Quality Specific

- [ ] `data/source_registry.md/json`, `data/claim_audit.md/json`, and `source_exhaustion_log.md/json` exist and are synchronized
- [ ] Broker evidence is labeled as `original_broker_pdf`, `broker_official_page`, `broker_abstract`, `media_repost`, `third_party_preview`, `search_snippet`, `corpus_gap`, or `not_found`
- [ ] Abstracts, reposts, previews, and search snippets are not presented as full Street consensus
- [ ] Failed source probes include reason unresolved and next verification path

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
- [ ] `analysis/valuation_audit.md` contains `Model Reproducibility: PASS` before any valuation table enters the published report

## Known Traps

| Trap | Example | Prevention |
|------|---------|-----------|
| 归母≠合并 | 德赛西威 归母4.61亿 vs 合并7.90亿 | Always label which basis |
| 流通≠总股本 | Many companies have 10-40% locked | Check 流通A股 specifically |
| 北向≈陆股通 but not identical | Some reports mix concepts | Use 深股通/沪股通 持股 data |
| 日均成交额 regime change | Before/after GTC: 35亿→150亿 | Note catalyst and use recent window |
| "解禁18.5%" may be old | May have already partially sold | Check if 已完成 vs 将解禁 |
| 券商一致预期 | Has 50-100% upward bias | Always note bias, use as ceiling not target |
