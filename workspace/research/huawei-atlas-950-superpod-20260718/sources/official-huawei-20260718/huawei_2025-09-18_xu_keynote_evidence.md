# Huawei 2025-09-18 Atlas 950 and UnifiedBus Evidence Capture

## Source metadata

- Publisher: Huawei Technologies Co., Ltd.
- Source type: official executive keynote transcript; primary source for Huawei's own roadmap and product claims.
- Publication date: 2025-09-18.
- Retrieval date: 2026-07-18.
- Original URL: https://www.huawei.com/cn/news/2025/9/hc-xu-keynote-speech
- English mirror: https://www.huawei.com/en/news/2025/9/hc-xu-keynote-speech
- Quality: Tier 1 / official primary for what Huawei announced. Forward-looking availability, performance comparisons, reliability claims, and roadmap specifications remain vendor claims rather than independent validation.

## Captured product facts

### Ascend 950 series

- Ascend 950PR and Ascend 950DT share the Ascend 950 die.
- Huawei stated that the series supports FP8, MXFP8, MXFP4, and proprietary HiF8 formats and provides 1 PFLOPS FP8 and 2 PFLOPS FP4 per chip.
- Huawei described two proprietary HBM variants: HiBL 1.0 for Ascend 950PR and HiZQ 2.0 for Ascend 950DT.
- Ascend 950DT is positioned for decode-stage inference and training. Huawei stated 144 GB memory capacity, 4 TB/s memory bandwidth, and 2 TB/s interconnect bandwidth, with availability planned for 2026 Q4.
- The identity of the HBM wafer manufacturer, logic-base-die manufacturer, packaging provider, production yield, and volume-production status was not disclosed.

### Atlas 900 A3 / CloudMatrix384 baseline

- Huawei described Atlas 900 A3 as supporting 384 Ascend 910C chips and up to 300 PFLOPS.
- Huawei stated that CloudMatrix384 is a Huawei Cloud service instance built on Atlas 900 A3 SuperPoDs.
- Huawei stated that more than 300 Atlas 900 A3 units had been deployed for more than 20 customers across internet, telecom, manufacturing, and other sectors.
- These disclosures are evidence of Atlas 900 A3 deployment, not Atlas 950 delivery and not evidence of orders for any upstream listed company.

### Atlas 950 SuperPoD roadmap

- Huawei said Atlas 950 is built with Ascend 950DT.
- Maximum design configuration: 8,192 Ascend 950DT cards/chips.
- Full configuration: 128 compute cabinets and 32 interconnect cabinets, or 160 cabinets in total, over approximately 1,000 square metres, with all-optical inter-cabinet connectivity.
- Announced aggregate specifications: 8 EFLOPS FP8, 16 EFLOPS FP4, approximately 1,152 TB memory, and approximately 16 PB/s interconnect bandwidth.
- Planned commercial availability: 2026 Q4.
- Huawei's comparison with NVIDIA NVL144 and NVL576 is a Huawei vendor comparison against peer roadmaps. It is not an independently normalized benchmark because precision, sparsity, workload, software maturity, availability status, and system boundary are not held constant.

### UnifiedBus and scale boundary

- Huawei formally announced UnifiedBus and said UnifiedBus 2.0 would be opened as a technical specification.
- Atlas 900 A3 uses UnifiedBus 1.0; Atlas 950 is designed around UnifiedBus 2.0.
- Huawei described the architecture as having six attributes: bus-grade interconnect, peer coordination, resource pooling, a unified protocol, large-scale networking, and high availability.
- Huawei's engineering claims included more than 200 metres optical reach, 2.1 microseconds interconnect latency, and a 100-fold improvement in optical-interconnect reliability. These are vendor claims and were not independently verified in this capture.
- UBoE carries UnifiedBus over Ethernet. Huawei said Atlas 950 SuperCluster supports both UBoE and RoCE and asserted that UBoE can use existing Ethernet switches with fewer switches and optical modules than RoCE.

### SuperPoD versus SuperCluster

- One Atlas 950 SuperPoD has a maximum roadmap scale of 8,192 NPUs.
- Atlas 950 SuperCluster is a separate scale-out design comprising 64 Atlas 950 SuperPoDs, more than 520,000 Ascend 950DT chips, more than 10,000 cabinets, and 524 EFLOPS FP8, planned for 2026 Q4.
- The 500,000-plus-card SuperCluster must not be described as one physical Atlas 950 SuperPoD.

## Evidence boundary

This source establishes Huawei's architecture, roadmap, intended product specifications, and prior Atlas 900 deployment claims. It does not establish:

- a physically delivered 8,192-card Atlas 950 system;
- independent benchmark parity or superiority versus NVIDIA or AMD systems;
- named Atlas 950 customers, signed contracts, price, backlog, acceptance, or revenue;
- the identity, qualification, allocation, ASP, capacity, utilization, yield, or margin of any A-share supplier.

