# Named Customer Rumor Registry

**Purpose:** Track public named-customer claims that are not confirmed by official filings or downloaded broker PDFs. These items must not be used as confirmed evidence in the main investment thesis.

| Ticker | Claim | Source type | Evidence status | Treatment |
|---|---|---|---|---|
| 002463 | Claims that Hudian is a core NVIDIA AI server PCB supplier or has high NVIDIA/Rubin share. | Xueqiu / Eastmoney wealth account / news repost search results | Unverified / market rumor | Do not use as confirmed. Use only official AI server/HPC revenue and IR 800G/CPO comments. |
| 002463 | Claims of Google ASIC / TPU supply position. | Social media / secondary commentary | Unverified / market rumor | Do not use as confirmed. |
| 300476 | Claims of NVIDIA Blackwell/Rubin/Rubin Ultra direct beneficiary and Google TPU/ASIC exposure. | Public article reposts and social media; JPM article excerpt is broker-stated but not customer-confirmed | Broker-stated / unverified depending source | Use only as broker-stated platform-chain exposure, not confirmed customer revenue. |
| 300476 | Claims of specific Rubin/UBB/OAM share percentages. | Social media / wealth account | Unverified / market rumor | Exclude from valuation model. |
| 002916 | Claims of NVIDIA/AMD/Meta/Cisco customer shares. | Social media / third-party commentary | Unverified / market rumor | Exclude; use official data-center product language and IR comments instead. |
| 600183 | Claims of NVIDIA M9/M10 certification, GB300/Rubin supply and yield percentages. | Xueqiu, OFweek, Datayes/robo feed, social media | Unverified unless original broker/company source is obtained | Exclude from confirmed thesis; use official high-speed/low-loss material and downloaded CCL report framework. |

## Rule

Named customer claims require one of: company filing, official IR transcript, original broker PDF with explicit analyst attribution, or customer/supplier disclosure. Otherwise classify as `market-rumor / unverified`.
