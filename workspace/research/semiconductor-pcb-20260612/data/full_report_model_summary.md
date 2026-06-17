# Full Report Model Summary

**Source:** PDFs downloaded to `workspace/research/semiconductor-pcb-20260612/sources/broker-core-20260615/`, `workspace/research/semiconductor-pcb-20260612/sources/broker-extra-20260615/`, and `workspace/research/semiconductor-pcb-20260612/sources/broker-supplemental-20260615/`; extracted with `pdftotext`.
**Use:** Replace weak public-summary evidence with full-report model evidence where available.

| Ticker | Broker | Report date | Key operating evidence | 2026E revenue | 2027E revenue | 2028E revenue | 2026E NPP | 2027E NPP | 2028E NPP | 2026E EPS | 2027E EPS | 2028E EPS | 2026E PE | 2027E PE | 2028E PE |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 中邮证券 | 2026-04-24 | 2025数通PCB收入146.56亿元，高速交换机81.69亿元，AI服务器/HPC 30.06亿元；2/3/4月累计宣布投资156亿元扩产AI服务器/高速通信板。 | 267亿元 | 378亿元 | 527亿元 | 58亿元 | 89亿元 | 129亿元 | 2.99 | 4.61 | 6.72 | 34.55x | 22.38x | 15.37x |
| 300476 | 开源证券 | 2026-04-30 | 2026Q1收入55.19亿元、归母净利12.88亿元、毛利率34.46%；具备100层以上高多层板、6阶24层HDI量产，布局10阶30层HDI与16层任意互联HDI；AI Data Center UBB和交换机市场份额全球领先。 | 328.16亿元 | 549.70亿元 | 769.30亿元 | 91.19亿元 | 154.41亿元 | 222.88亿元 | 9.28 | 15.71 | 22.68 | 33.7x | 19.9x | 13.8x |
| 002916 | 太平洋 | 2026-03-26 | 2025 PCB收入143.59亿元、毛利率35.53%；AI服务器及配套产品订单同比显著增加；封装基板收入41.48亿元、毛利率22.58%，FC-BGA 22层及以下量产、24层及以上推进。 | 315.98亿元 | N/A | N/A | 55.46亿元 | 75.45亿元 | 97.25亿元 | 8.14 | 11.08 | 14.28 | 28.87x | 21.22x | 16.46x |
| 600183 | 太平洋 | 2026-05-27 | 2026Q1毛利率28.10%，同比+3.50pct、环比+2.32pct；公司发力AI服务器高频高速材料和封装基板材料。 | 391.48亿元 | 514.85亿元 | 629.84亿元 | 55.70亿元 | 78.56亿元 | 101.69亿元 | 2.29 | 3.23 | 4.19 | 47.10x | 33.40x | 25.80x |
| 603186 | 浙商证券 | 2026-01-27 | 覆铜板产品结构高端化，CBF膜、BT封装材料打开增量；珠海高等级覆铜板项目满产后预计年销售收入约30亿元。 | 73.43亿元 | 95.53亿元 | N/A | 5.73亿元 | 8.03亿元 | N/A | 4.04 | 5.65 | N/A | 17.61x | 12.58x | N/A |

## Remaining Gaps

- Full company model is available in downloaded PDFs for all five core names. 603186 has now been upgraded with a 2026-01-27 Zheshang deep report covering 2025E-2027E, though it still lacks 2028E.
- Customer-chain revenue split is still partial: Hudian has AI server/HPC, high-speed switch/router and 2025 application mix; Shennan has PCB/substrate and broker-stated AI data-center exposure; Shenghong has official ASIC/GPU/TPU progress language but not exact customer revenue split; Shengyi has material direction but not M8/M9/M10 revenue share.
- Full EPS sensitivity still requires editable model assumptions, not only broker forecast tables.

## Extra technical valuation bridge: high-speed CCL

**Source:** 西南证券, `600183-xinan-high-speed-ccl.pdf`.

| Item | Extracted assumption |
|---|---|
| AI server CCL value | CNY 4,000-5,000 per server |
| GPU board group CCL value | about CNY 3,000 per server |
| CPU motherboard CCL value | about CNY 1,300 per server |
| OAM CCL value | about CNY 1,745 per server |
| UBB CCL value | about CNY 1,364 per server |
| OAM process assumption | 5-stage 20-layer process |
| UBB process assumption | 20-layer through-hole board |
| H100 GPU board group material | M6/M7+ high-speed CCL |

This is one of the strongest public bridges from AI server platform structure to CCL value content found in the current workflow.

## Extra Huazheng 2026 deep report

**Source:** `workspace/research/semiconductor-pcb-20260612/sources/broker-supplemental-20260615/01-603186-浙商证券-二十余载躬耕不辍-AI时代厚积薄发.pdf`.

The 41-page Zheshang deep report replaces the earlier limited preview for model purposes. It forecasts 2025E/2026E/2027E revenue of 42.19/73.43/95.53亿元, NPP of 3.00/5.73/8.03亿元, EPS of 2.12/4.04/5.65, and PE of 33.60/17.61/12.58. It improves Huazheng model coverage but still does not disclose named customer/platform revenue or a 2028E line.

## Supplemental original-report checks

**Source:** `data/supplemental_report_archive_summary.md`.

- 002463: 中泰证券 adds second-source 2026E-2028E revenue/NPP/EPS and confirms 2025 high-speed switch/router revenue 81.69亿元, AI server/HPC revenue 30.06亿元, next-generation GPU platform certification and 1.6T small-batch delivery.
- 300476: 国盛证券 adds 2025E-2027E revenue/NPP/EPS and official IR confirms large-customer/ASIC progress plus GPU accelerator and TPU board supply expansion.
- 002916: CMBI adds TP RMB288, 2026E-2028E revenue/NPP/EPS and broker-stated AI data-center demand at roughly 25% of PCB revenue.
- 600183: 国海证券 adds a 51-page CCL deep report with high-frequency/high-speed material architecture and GB200 PCB value table reference; model period is 2024E-2026E, so it supplements but does not replace the newer Pacific 2026E-2028E model.
