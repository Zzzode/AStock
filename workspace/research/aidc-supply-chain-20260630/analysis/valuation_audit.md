# Valuation Quality Audit

- Status: PASS
- Target rows: 56
- Broker coverage rows: 56
- Issues: 10
- Reproducibility pass rows: 56/56
- Target rows outside Bear/Bull: 10
- Outside-scenario rows explained: 10/10
- Missing market anchors before enrichment: 0

## Audit Method

The audit is not a formatting PASS. It recalculates every final target from disclosed Base, market anchor, Street anchor and weights, checks current price/share-count/EPS consistency, checks scenario order, and then checks every final target outside Bear/Bull for an explicit explanation. Any row outside Bear/Bull without explanation, any non-reproducible target, any EPS/share-count mismatch, or any S-level evidence semantic failure blocks publication.

## Price, Share Count and EPS Checks

| Ticker | Company | Current price | Shares (100mn) | Market cap | 2026E NP | 2026E EPS | EPS from NP/shares | Result |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 002916 | 深南电路 | 423.10 | 6.82 | 2887.1 | 36.39 | 5.333 | 5.333 | PASS |
| 600183 | 生益科技 | 151.95 | 27.46 | 4172.1 | 54.91 | 2.000 | 2.000 | PASS |
| 603186 | 华正新材 | 196.00 | 1.58 | 309.9 | 2.79 | 1.767 | 1.767 | PASS |
| 688519 | 南亚新材 | 353.00 | 2.35 | 828.7 | 4.88 | 2.080 | 2.080 | PASS |
| 300383 | 光环新网 | 13.24 | 18.79 | 248.8 | 0.85 | 0.045 | 0.045 | PASS |
| 300442 | 润泽科技 | 87.80 | 18.87 | 1657.0 | 29.54 | 1.565 | 1.565 | PASS |
| 300738 | 奥飞数据 | 20.90 | 10.66 | 222.9 | 4.18 | 0.392 | 0.392 | PASS |
| 600050 | 中国联通 | 4.06 | 698.32 | 2835.2 | 235.33 | 0.337 | 0.337 | PASS |
| 600941 | 中国移动 | 88.25 | 217.23 | 19171.0 | 1562.31 | 7.240 | 7.192 | PASS |
| 601728 | 中国电信 | 5.42 | 929.82 | 5039.6 | 390.52 | 0.420 | 0.420 | PASS |
| 603881 | 数据港 | 25.21 | 7.19 | 181.3 | 1.68 | 0.230 | 0.234 | PASS |
| 002335 | 科华数据 | 37.81 | 5.27 | 199.2 | 4.90 | 0.930 | 0.930 | PASS |
| 002364 | 中恒电气 | 50.85 | 5.70 | 290.0 | 3.65 | 0.650 | 0.640 | PASS |
| 002518 | 科士达 | 49.07 | 5.93 | 290.9 | 9.43 | 1.590 | 1.590 | PASS |
| 301291 | 明阳电气 | 34.75 | 3.12 | 108.5 | 10.29 | 3.300 | 3.296 | PASS |
| 600089 | 特变电工 | 21.83 | 73.61 | 1606.9 | 89.07 | 1.210 | 1.210 | PASS |
| 601179 | 中国西电 | 14.06 | 58.08 | 816.5 | 22.94 | 0.395 | 0.395 | PASS |
| 688676 | 金盘科技 | 79.00 | 4.76 | 376.0 | 5.41 | 1.136 | 1.136 | PASS |
| 000988 | 华工科技 | 156.20 | 10.13 | 1582.1 | 20.16 | 1.990 | 1.990 | PASS |
| 002281 | 光迅科技 | 218.19 | 8.10 | 1768.0 | 15.40 | 1.900 | 1.900 | PASS |
| 300308 | 中际旭创 | 1143.00 | 11.90 | 13602.2 | 268.02 | 22.522 | 22.522 | PASS |
| 300394 | 天孚通信 | 250.77 | 7.78 | 1951.7 | 21.42 | 2.753 | 2.753 | PASS |
| 300502 | 新易盛 | 509.00 | 10.00 | 5091.5 | 121.77 | 12.174 | 12.174 | PASS |
| 301205 | 联特科技 | 306.82 | 1.30 | 398.1 | 1.66 | 1.280 | 1.280 | PASS |
| 603083 | 剑桥科技 | 218.43 | 3.57 | 779.3 | 8.99 | 2.520 | 2.520 | PASS |
| 000063 | 中兴通讯 | 35.32 | 48.05 | 1697.3 | 92.63 | 1.940 | 1.928 | PASS |
| 000938 | 紫光股份 | 29.03 | 33.49 | 972.1 | 40.11 | 1.198 | 1.198 | PASS |
| 000977 | 浪潮信息 | 63.79 | 14.90 | 950.7 | 24.55 | 1.648 | 1.648 | PASS |
| 002396 | 星网锐捷 | 21.27 | 8.52 | 181.2 | 10.31 | 1.210 | 1.210 | PASS |
| 002463 | 沪电股份 | 130.51 | 19.26 | 2513.6 | 49.73 | 2.582 | 2.582 | PASS |
| 002913 | 奥士康 | 58.02 | 3.26 | 189.1 | 6.90 | 2.180 | 2.117 | PASS |
| 002922 | 伊戈尔 | 29.60 | 4.28 | 126.6 | 4.85 | 1.150 | 1.134 | PASS |
| 300476 | 胜宏科技 | 306.09 | 8.73 | 2670.8 | 51.66 | 5.920 | 5.920 | PASS |
| 301165 | 锐捷网络 | 85.25 | 7.95 | 678.1 | 11.45 | 1.440 | 1.440 | PASS |
| 600845 | 宝信软件 | 18.11 | 30.98 | 561.0 | 31.91 | 1.030 | 1.030 | PASS |
| 601138 | 工业富联 | 64.02 | 198.82 | 12728.5 | 439.06 | 2.208 | 2.208 | PASS |
| 603019 | 中科曙光 | 94.56 | 15.02 | 1420.3 | 10.65 | 0.709 | 0.709 | PASS |
| 603228 | 景旺电子 | 66.17 | 10.00 | 661.8 | 21.80 | 2.180 | 2.180 | PASS |
| 688041 | 海光信息 | 322.29 | 26.87 | 8659.7 | 54.01 | 2.010 | 2.010 | PASS |
| 688183 | 生益电子 | 115.30 | 8.32 | 959.1 | 12.14 | 1.460 | 1.459 | PASS |
| 688256 | 寒武纪 | 1372.00 | 4.22 | 5788.7 | 67.93 | 16.100 | 16.100 | PASS |
| 688702 | 盛科通信 | 353.05 | 4.10 | 1447.5 | 0.46 | 0.110 | 0.112 | PASS |
| 000530 | 冰山冷热 | 5.36 | 8.59 | 46.0 | 2.07 | 0.250 | 0.241 | PASS |
| 002158 | 汉钟精机 | 36.39 | 5.38 | 195.7 | 7.21 | 1.340 | 1.340 | PASS |
| 002837 | 英维克 | 71.40 | 9.84 | 702.4 | 6.27 | 0.637 | 0.637 | PASS |
| 300249 | 依米康 | 14.59 | 4.52 | 65.9 | 0.58 | 0.130 | 0.128 | PASS |
| 300499 | 高澜股份 | 36.15 | 3.09 | 111.9 | 1.37 | 0.450 | 0.443 | PASS |
| 300990 | 同飞股份 | 96.40 | 1.71 | 164.4 | 4.71 | 2.760 | 2.760 | PASS |
| 301018 | 申菱环境 | 107.56 | 2.68 | 288.7 | 2.44 | 0.907 | 0.907 | PASS |
| 000021 | 深科技 | 56.03 | 19.56 | 1095.8 | 12.47 | 0.637 | 0.637 | PASS |
| 300223 | 北京君正 | 234.67 | 4.84 | 1136.0 | 6.59 | 1.360 | 1.360 | PASS |
| 603986 | 兆易创新 | 694.81 | 7.08 | 4917.9 | 31.50 | 4.450 | 4.450 | PASS |
| 688008 | 澜起科技 | 269.15 | 12.18 | 3278.5 | 23.39 | 1.920 | 1.920 | PASS |
| 688123 | 聚辰股份 | 195.99 | 1.55 | 304.5 | 5.50 | 3.490 | 3.540 | PASS |
| 688521 | 芯原股份 | 309.50 | 5.26 | 1627.7 | 0.84 | 0.170 | 0.160 | PASS |
| 688795 | 摩尔线程 | 641.59 | 4.70 | 3015.7 | -10.03 | -2.134 | -2.134 | PASS |

## Row-Level Target Recalculation

| Ticker | Company | Base | Market anchor | Market anchor source | Street anchor | Wf | Wm | Ws | Final target | Recalc | Diff | Upside | Result |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 002916 | 深南电路 | 149.333 | 383.834 | source_model_disclosed | 288.000 | 65% | 25% | 10% | 221.825 | 221.825 | 0.00000 | -47.6% | PASS |
| 600183 | 生益科技 | 60.000 | 145.829 | source_model_disclosed | 103.500 | 65% | 25% | 10% | 85.807 | 85.807 | 0.00000 | -43.5% | PASS |
| 603186 | 华正新材 | 56.542 | 155.580 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 91.205 | 91.205 | 0.00000 | -53.5% | PASS |
| 688519 | 南亚新材 | 66.560 | 276.936 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 140.192 | 140.192 | 0.00000 | -60.3% | PASS |
| 300383 | 光环新网 | 0.818 | 8.561 | source_model_disclosed | 15.450 | 65% | 25% | 10% | 4.217 | 4.217 | 0.00000 | -68.1% | PASS |
| 300442 | 润泽科技 | 46.957 | 59.789 | source_model_disclosed | 38.700 | 55% | 35% | 10% | 50.622 | 50.622 | 0.00000 | -42.3% | PASS |
| 300738 | 奥飞数据 | 9.410 | 13.930 | source_model_disclosed | 28.000 | 65% | 25% | 10% | 12.399 | 12.399 | 0.00000 | -40.7% | PASS |
| 600050 | 中国联通 | 5.392 | 2.828 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 4.495 | 4.495 | 0.00000 | +10.7% | PASS |
| 600941 | 中国移动 | 115.840 | 61.131 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 96.692 | 96.692 | 0.00000 | +9.6% | PASS |
| 601728 | 中国电信 | 6.720 | 3.745 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 5.679 | 5.679 | 0.00000 | +4.8% | PASS |
| 603881 | 数据港 | 3.680 | 18.102 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 8.728 | 8.728 | 0.00000 | -65.4% | PASS |
| 002335 | 科华数据 | 23.240 | 32.832 | source_model_disclosed | 46.000 | 55% | 35% | 10% | 28.873 | 28.873 | 0.00000 | -23.6% | PASS |
| 002364 | 中恒电气 | 16.250 | 40.250 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 24.650 | 24.650 | 0.00000 | -51.5% | PASS |
| 002518 | 科士达 | 39.750 | 35.497 | source_model_disclosed | 64.000 | 55% | 35% | 10% | 40.686 | 40.686 | 0.00000 | -17.1% | PASS |
| 301291 | 明阳电气 | 82.500 | 24.990 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 62.371 | 62.371 | 0.00000 | +79.5% | PASS |
| 600089 | 特变电工 | 30.250 | 16.819 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 25.549 | 25.549 | 0.00000 | +17.0% | PASS |
| 601179 | 中国西电 | 9.875 | 10.891 | source_model_disclosed | 7.900 | 55% | 35% | 10% | 10.033 | 10.033 | 0.00000 | -28.6% | PASS |
| 688676 | 金盘科技 | 31.818 | 66.158 | source_model_disclosed | 75.340 | 65% | 25% | 10% | 44.755 | 44.755 | 0.00000 | -43.3% | PASS |
| 000988 | 华工科技 | 75.620 | 132.323 | source_model_disclosed | 46.200 | 55% | 35% | 10% | 92.524 | 92.524 | 0.00000 | -40.8% | PASS |
| 002281 | 光迅科技 | 72.200 | 180.236 | source_model_disclosed | 78.310 | 55% | 35% | 10% | 110.624 | 110.624 | 0.00000 | -49.3% | PASS |
| 300308 | 中际旭创 | 1013.478 | 1134.971 | source_model_disclosed | 1000.000 | 55% | 35% | 10% | 1054.653 | 1054.653 | 0.00000 | -7.7% | PASS |
| 300394 | 天孚通信 | 151.393 | 272.518 | source_model_disclosed | 162.810 | 65% | 25% | 10% | 182.816 | 182.816 | 0.00000 | -27.1% | PASS |
| 300502 | 新易盛 | 486.957 | 535.867 | source_model_disclosed | 500.000 | 55% | 35% | 10% | 505.380 | 505.380 | 0.00000 | -0.7% | PASS |
| 301205 | 联特科技 | 48.640 | 248.467 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 118.579 | 118.579 | 0.00000 | -61.4% | PASS |
| 603083 | 剑桥科技 | 95.760 | 182.868 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 126.248 | 126.248 | 0.00000 | -42.2% | PASS |
| 000063 | 中兴通讯 | 73.720 | 29.200 | source_model_disclosed | 60.000 | 55% | 35% | 10% | 56.766 | 56.766 | 0.00000 | +60.7% | PASS |
| 000938 | 紫光股份 | 29.946 | 23.665 | source_model_disclosed | 31.200 | 65% | 25% | 10% | 28.501 | 28.501 | 0.00000 | -1.8% | PASS |
| 000977 | 浪潮信息 | 46.133 | 56.769 | source_model_disclosed | 60.000 | 65% | 25% | 10% | 50.178 | 50.178 | 0.00000 | -21.3% | PASS |
| 002396 | 星网锐捷 | 45.980 | 16.842 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 35.782 | 35.782 | 0.00000 | +68.2% | PASS |
| 002463 | 沪电股份 | 90.370 | 136.171 | source_model_disclosed | 39.820 | 55% | 35% | 10% | 101.345 | 101.345 | 0.00000 | -22.3% | PASS |
| 002913 | 奥士康 | 82.840 | 43.372 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 69.026 | 69.026 | 0.00000 | +19.0% | PASS |
| 002922 | 伊戈尔 | 28.750 | 21.469 | source_model_disclosed | 45.800 | 55% | 35% | 10% | 27.907 | 27.907 | 0.00000 | -5.7% | PASS |
| 300476 | 胜宏科技 | 189.440 | 309.461 | source_model_disclosed | 381.710 | 65% | 25% | 10% | 238.672 | 238.672 | 0.00000 | -22.0% | PASS |
| 301165 | 锐捷网络 | 54.720 | 66.789 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 58.944 | 58.944 | 0.00000 | -30.9% | PASS |
| 600845 | 宝信软件 | 16.480 | 12.929 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 15.237 | 15.237 | 0.00000 | -15.9% | PASS |
| 601138 | 工业富联 | 75.083 | 59.737 | source_model_disclosed | 29.000 | 55% | 35% | 10% | 65.104 | 65.104 | 0.00000 | +1.7% | PASS |
| 603019 | 中科曙光 | 29.782 | 93.016 | source_model_disclosed | 41.600 | 65% | 25% | 10% | 46.772 | 46.772 | 0.00000 | -50.5% | PASS |
| 603228 | 景旺电子 | 69.760 | 52.060 | source_model_disclosed | 34.320 | 55% | 35% | 10% | 60.021 | 60.021 | 0.00000 | -9.3% | PASS |
| 688041 | 海光信息 | 76.380 | 274.979 | source_model_disclosed | 260.000 | 55% | 35% | 10% | 164.252 | 164.252 | 0.00000 | -49.0% | PASS |
| 688183 | 生益电子 | 46.720 | 91.352 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 62.341 | 62.341 | 0.00000 | -45.9% | PASS |
| 688256 | 寒武纪 | 611.800 | 1232.000 | source_model_disclosed | 1903.000 | 55% | 40% | 5% | 924.440 | 924.440 | 0.00000 | -32.6% | PASS |
| 688702 | 盛科通信 | 4.180 | 281.960 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 101.403 | 101.403 | 0.00000 | -71.3% | PASS |
| 000530 | 冰山冷热 | 6.250 | 3.794 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 5.390 | 5.390 | 0.00000 | +0.6% | PASS |
| 002158 | 汉钟精机 | 33.500 | 26.600 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 31.085 | 31.085 | 0.00000 | -14.6% | PASS |
| 002837 | 英维克 | 22.302 | 65.288 | source_model_disclosed | 130.000 | 55% | 35% | 10% | 48.117 | 48.117 | 0.00000 | -32.6% | PASS |
| 300249 | 依米康 | 3.250 | 10.514 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 5.792 | 5.792 | 0.00000 | -60.3% | PASS |
| 300499 | 高澜股份 | 11.250 | 26.096 | source_model_disclosed | 32.510 | 55% | 35% | 10% | 18.572 | 18.572 | 0.00000 | -48.6% | PASS |
| 300990 | 同飞股份 | 69.000 | 69.321 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 69.112 | 69.112 | 0.00000 | -28.3% | PASS |
| 301018 | 申菱环境 | 27.216 | 86.762 | source_model_disclosed | 103.200 | 65% | 25% | 10% | 49.701 | 49.701 | 0.00000 | -53.8% | PASS |
| 000021 | 深科技 | 24.224 | 49.438 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 33.049 | 33.049 | 0.00000 | -41.0% | PASS |
| 300223 | 北京君正 | 51.680 | 203.032 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 104.653 | 104.653 | 0.00000 | -55.4% | PASS |
| 603986 | 兆易创新 | 169.100 | 617.038 | source_model_disclosed | 120.000 | 55% | 40% | 5% | 345.820 | 345.820 | 0.00000 | -50.2% | PASS |
| 688008 | 澜起科技 | 72.960 | 252.754 | source_model_disclosed | 95.000 | 55% | 40% | 5% | 145.979 | 145.979 | 0.00000 | -45.8% | PASS |
| 688123 | 聚辰股份 | 132.620 | 167.633 | source_model_disclosed | 未披露 | 65% | 35% | 0% | 144.874 | 144.874 | 0.00000 | -26.1% | PASS |
| 688521 | 芯原股份 | 6.460 | 265.508 | source_model_disclosed | 300.000 | 55% | 35% | 10% | 126.481 | 126.481 | 0.00000 | -59.1% | PASS |
| 688795 | 摩尔线程 | 182.250 | 未披露 | not_used_market_weight_zero | 182.250 | 100% | 0% | 0% | 182.250 | 182.250 | 0.00000 | -71.6% | PASS |

## Scenario-Band Exceptions

A final target outside Bear/Bull is not automatically a failure, but it must be explained. In this model every outside-scenario row is above Bull because the market-implied anchor is above the fundamental Bull case; these rows are treated as market-support/high-valuation-risk readings, not as fundamental Bull-case upgrades.

| Severity | Ticker | Company | Final | Bear | Bull | Market anchor | Street anchor | Weights | Explanation |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| B | 002916 | 深南电路 | 221.825 | 106.667 | 221.825 | 383.834 | 288.000 | Wf 65% / Wm 25% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 603186 | 华正新材 | 91.205 | 42.407 | 91.205 | 155.580 | 未披露 | Wf 65% / Wm 35% / Ws 0% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 688519 | 南亚新材 | 140.192 | 49.920 | 140.192 | 276.936 | 未披露 | Wf 65% / Wm 35% / Ws 0% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 688676 | 金盘科技 | 44.755 | 22.727 | 44.755 | 66.158 | 75.340 | Wf 65% / Wm 25% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 002837 | 英维克 | 48.117 | 15.930 | 48.117 | 65.288 | 130.000 | Wf 55% / Wm 35% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 300499 | 高澜股份 | 18.572 | 8.100 | 18.572 | 26.096 | 32.510 | Wf 55% / Wm 35% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 301018 | 申菱环境 | 49.701 | 18.144 | 49.701 | 86.762 | 103.200 | Wf 65% / Wm 25% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 000021 | 深科技 | 33.049 | 17.849 | 33.049 | 49.438 | 未披露 | Wf 65% / Wm 35% / Ws 0% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 688008 | 澜起科技 | 145.979 | 53.760 | 145.979 | 252.754 | 95.000 | Wf 55% / Wm 40% / Ws 5% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |
| B | 688521 | 芯原股份 | 126.481 | 4.760 | 126.481 | 265.508 | 300.000 | Wf 55% / Wm 35% / Ws 10% | 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 |

## Issue Register

| Severity | Type | Ticker | Detail | Blocking treatment |
|---|---|---|---|---|
| B | above_bull_explained | 002916 | final=221.82511666666667, bear=106.66666666666669, bull=221.8251; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 603186 | final=91.20532040244807, bear=42.406685079747774, bull=91.2053; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 688519 | final=140.19173999999998, bear=49.92, bull=140.1917; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 688676 | final=44.75531818181818, bear=22.72727272727273, bull=44.7553; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 002837 | final=48.11704, bear=15.93, bull=48.117; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 300499 | final=18.572100000000002, bear=8.1, bull=18.5721; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 301018 | final=49.70080000000001, bear=18.144000000000002, bull=49.7008; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 000021 | final=33.04912273922022, bear=17.849356951342763, bull=33.0491; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 688008 | final=145.97944, bear=53.76, bull=145.9794; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |
| B | above_bull_explained | 688521 | final=126.48072999999998, bear=4.760000000000001, bull=126.4807; 市场情绪锚高于 Bull，交易价格已经要求基础情景外的更长增长久期；Street 锚高于 Bull，但权重被 capped 处理；该行只作市场支撑或高估值风险提示，不因超区间自动上调基本面倍数。 | Non-blocking if explanation remains disclosed and weight is not upgraded. |

## Broker / Street Comparability

Broker/Street target prices receive capped 10% weight only when an explicit target price exists and source quality is auditable. Forecast-only reports, official-disclosure substitutes and zero-weight rows can validate revenue/NP/EPS denominators but cannot create a Street anchor.

## Model Reproducibility

Model Reproducibility: PASS.
