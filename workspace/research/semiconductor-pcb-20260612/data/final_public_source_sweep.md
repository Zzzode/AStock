# Final Public Source Sweep

**Run date:** 2026-06-15
**Purpose:** Re-test whether public web sources can close the remaining top-tier gaps after official filings, downloaded broker PDFs, IR records, AkShare, Baostock, Yahoo, Baidu valuation, Sina holder data, CNInfo and Eastmoney public endpoints were already used.

## Search Targets

| Target | Query focus | Public-source result | Treatment |
|---|---|---|---|
| 002463 | NVIDIA / Google ASIC / AI server / HPC revenue split | Search results include broker abstract/repost pages and social-media style claims. They repeat AI server, HPC and high-speed switch themes, but do not provide issuer-confirmed named-customer revenue by NVIDIA, Google, ASIC or optical platform. | Keep confirmed Hudian data-communication PCB, high-speed switch/router and AI server/HPC revenue from official/report evidence. Do not use named-customer claims as confirmed. |
| 300476 | NVIDIA / Google TPU / ASIC / UBB / switch revenue share | Search results are mainly Xueqiu, Eastmoney wealth-account reposts and article summaries. They include specific customer/platform share claims, but the accessible pages are not official filings, official IR transcripts, customer disclosures or fully attributable original broker PDFs. | Keep as rumor/broker-stated where attribution is clear. Exclude from EPS model. |
| 002916 | AI server / optical module / FC-BGA customer revenue split | Search results include third-party PDF and social-media summaries with AI PCB, optical module and ABF/FC-BGA language. They do not provide reliable named-customer revenue or customer-by-platform split. | Use official segment and downloaded full-report data only. |
| 600183 | M8/M9/M10 CCL revenue share and customer certification | Search results include Datayes/robo feed, Eastmoney wealth-account and Xueqiu claims about N-customer, M9 certification and AI-CCL shipment share. The strongest official source remains SSE-hosted IR language confirming GPU/AI project cooperation and batch supply, without customer names or M8/M9 revenue share. | Treat named certification/share claims as unverified unless an original broker PDF or issuer disclosure is obtained. |
| 603186 | Current 2026 Huazheng CBF/BT/CCL model | Search results include social-media commentary, an older DZH PDF and a limited 2026 preview. No complete current model table replacing the existing archived evidence was publicly accessible. | Keep Huazheng as watchlist/aggressive status with weak model coverage. |

## Conclusion

The final sweep did not close the three unresolved requirements:

1. Named platform/customer revenue split remains unavailable from reliable public evidence.
2. Bottom-up customer/platform EPS assumptions remain unavailable because the public sources do not disclose customer revenue, ASP, shipment, platform margin, depreciation and working-capital assumptions.
3. All-ticker real-time fund-flow remains unavailable because tested public APIs are partial or failing; public search does not replace a data terminal.

This file supports the final boundary in `completion_audit_manifest.md` and the unresolved blocker list in `unresolved_requirements.json`.
