# Broker Consensus Analysis

## Scope and Method

This note synthesizes the original-PDF broker corpus collected on 2026-07-18 for the Huawei Atlas 950 / SuperPoD / domestic-compute / AIDC chain. It is a source-layer consensus analysis, not an AStock valuation opinion.

The weighted snapshot uses only the latest report from each broker for each ticker. Older same-broker updates remain auditable but receive zero valuation weight. The stale 2024 report for 002261 also receives zero weight. All means and ranges below are derived from broker forecasts in `broker_street_consensus_20260718.json`.

## Coverage Result

- 38 unique original broker PDFs and 38 extracted text files were archived.
- 35 ticker-report rows cover all 14 priority tickers.
- 13 of 14 priority tickers have an original report in the 180-day window.
- 002261 has no fresh report; its 2024 landmark report lacks 2027E forecasts and is excluded from current valuation.
- 30 latest-per-broker rows carry positive valuation weight.
- 4 original rows are retained with zero weight because a later same-broker update supersedes them.
- 1 stale original row and 1 explicit not-found row carry zero weight.
- Only 600183, 002916, and 002025 have visible broker target prices. Eleven priority tickers have no original target-price disclosure in this collection.

## Consensus Direction

All 30 positively weighted broker rows carry a positive rating: buy, outperform, overweight-equivalent, or increase-position. No neutral or bearish broker report was found in the collected window. This is a crowded-positive corpus and should not be interpreted as balanced sentiment evidence.

The repeated positive thesis clusters are:

1. AI-server and high-speed-switch demand supports high-layer PCB, high-speed CCL, optical interconnect, and copper interconnect.
2. Domestic supernode architecture increases bandwidth, connector, line-module, optical-module, and liquid-cooling requirements.
3. Liquid cooling shifts from expectation trading toward shipment and earnings delivery in 2026H2.
4. Domestic compute infrastructure creates incremental demand for integrated servers, data-center power, cooling, and software/application layers.

## Atlas 950 / SuperPoD-Specific Broker Evidence

- The 万联证券 electronic-industry report states that Atlas 950 SuperPoD uses a 64-card cabinet unit and supports up to 8,192 NPU cards.
- The 华鑫证券 航天电器 report states that Atlas 950 SuperPoD is expected in 2026Q4, supports 8,192 Ascend cards, and uses a full-liquid-cooling architecture without an air-cooled option.
- The 山西证券 华丰科技 report states that 910C / 950 / 960 / 970 interconnect bandwidth is 784GB/s / 2TB/s / 2.2TB/s / 4TB/s.

These statements establish the broker demand framework. They do not, by themselves, prove that every covered A-share company is a Huawei supplier.

## Weighted Forecast Snapshot

| Ticker | Company | Brokers | 2026E revenue mean | 2027E revenue mean | 2026E net profit mean | 2027E net profit mean | 2026E EPS mean | 2027E EPS mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 000034 | 神州数码 | 1 | 165,454 | 186,478 | 903 | 1,180 | 1.25 | 1.63 |
| 002261 | 拓维信息 | 0 | NA | NA | NA | NA | NA | NA |
| 000988 | 华工科技 | 2 | 23,574.5 | 35,870 | 2,374 | 3,025.5 | 2.362 | 3.011 |
| 002281 | 光迅科技 | 1 | 15,687 | 19,615 | 1,536 | 1,999 | 1.90 | 2.48 |
| 600183 | 生益科技 | 3 | 39,081 | 50,872.7 | 5,568.3 | 7,967.7 | 2.290 | 3.280 |
| 002916 | 深南电路 | 3 | 31,381 | 39,333.7 | 5,470.6 | 7,354.4 | 8.083 | 10.870 |
| 002463 | 沪电股份 | 6 | 26,333.8 | 37,760.3 | 5,719.8 | 8,676.7 | 2.970 | 4.510 |
| 300476 | 胜宏科技 | 3 | 32,551.7 | 54,737.3 | 8,898 | 15,467.7 | 9.430 | 16.383 |
| 002837 | 英维克 | 2 | 8,883.5 | 13,361 | 1,143 | 1,792.5 | 1.171 | 1.836 |
| 301018 | 申菱环境 | 1 | 6,750 | 10,319 | 428 | 646 | 1.608 | 2.428 |
| 002335 | 科华数据 | 1 | 11,405 | 15,241 | 694.6 | 926.9 | 1.35 | 1.80 |
| 002130 | 沃尔核材 | 1 | 12,150 | 15,896 | 1,880 | 2,565 | 1.49 | 2.04 |
| 002230 | 科大讯飞 | 2 | 32,900 | 39,634.5 | 1,207 | 1,564.5 | 0.510 | 0.665 |
| 002025 | 航天电器 | 4 | 6,828.3 | 8,111 | 379.8 | 570.3 | 0.835 | 1.253 |

Revenue and net profit are CNY million; EPS is CNY per share.

## Agreement and Divergence

### High agreement

- 600183: 2026E revenue ranges only from CNY39.040bn to CNY39.148bn; 2026E EPS ranges from CNY2.28 to CNY2.30.
- 002463: six brokers place 2026E EPS in a relatively narrow CNY2.76-CNY3.10 range and 2027E EPS in CNY4.25-CNY4.65.
- 002230: two brokers place 2026E revenue at CNY32.315bn-CNY33.485bn and 2027E net profit at CNY1.564bn-CNY1.565bn.

### Material divergence

- 000988: 2027E revenue ranges from CNY30.638bn to CNY41.102bn. The difference reflects materially different assumptions for optical-interconnect volume and ramp speed.
- 002837: 2027E net profit ranges from CNY1.639bn to CNY1.946bn, while 2027E revenue ranges from CNY12.858bn to CNY13.864bn. The profit spread is wider than the revenue spread, indicating disagreement over margin and operating leverage.
- 002025: 2026E EPS ranges from CNY0.53 to CNY1.10; 2027E EPS ranges from CNY0.62 to CNY2.15. This is the widest earnings divergence in the priority set. The latest 国信 update keeps CNY0.85 / CNY1.18 EPS but narrows its target range from CNY67-81 to CNY69-78.

## Valuation Observations

- 600183: 西南证券 assigns CNY103.50 using 45x 2026E target P/E.
- 002916: 招银国际 assigns CNY288 using 38x FY26E P/E, blending 33x PCB peers and 42x substrate peers; the report states 15.1% upside.
- 002025: 国信证券 assigns CNY69-78 in the 2026-06-11 update. The older CNY67-81 range is superseded in weighted consensus.
- 002130 carries the lowest visible 2026E report-price P/E in the priority set at 18.3x.
- High visible 2026E report-price multiples include 002230 at 101.75x-106.61x, 002837 at 86.59x-106.6x, 301018 at 76.2x, and 002025 at 57.8x-149.7x across brokers.

The lack of target prices for 11 of 14 tickers is a publication constraint. Current-price P/E observations are not substitutes for broker target prices.

## Linkage Boundaries

- 002230: official Ascend 950 downstream co-development evidence is tracked outside this broker-report packet. The broker corpus here supports only forecasts, rating, and AI commercialization context.
- 002025: the broker corpus supports high-speed backplane, liquid-cooling interconnect, AI-compute, and Atlas 950 demand exposure. It does not confirm a Huawei-specific supply relationship.
- The PCB, optical, copper-interconnect, power, and cooling reports generally describe sector or customer-demand exposure. Do not convert thematic exposure into named-customer revenue attribution without separate primary evidence.

## Risks Repeated Across the Corpus

- AI-server or data-center demand below expectations.
- Customer qualification or order conversion below expectations.
- Capacity construction, yield ramp, or production release below expectations.
- Raw-material inflation and delayed cost pass-through.
- Optical-module material shortages and other supply constraints.
- Intensified competition and customer self-production or multi-sourcing.
- Liquid-cooling shipment timing slipping beyond 2026H2.

## Remaining Verification Paths

1. Obtain a fresh 002261 report through broker archives or an auditable Wind/Choice/iFinD export.
2. Refresh target-price coverage after the next earnings cycle, especially for 000988, 002463, 300476, 002837, 301018, 002335, 002130, and 002230.
3. Reconcile 002025 earnings assumptions against official order and margin disclosures before assigning valuation credit to the supernode theme.
4. Keep named-customer and Huawei-specific linkage claims in the official-evidence layer, not in the broker-consensus layer.
