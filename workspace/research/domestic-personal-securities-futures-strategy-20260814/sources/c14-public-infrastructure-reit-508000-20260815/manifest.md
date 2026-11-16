# C14 公募基础设施 REITs 一手来源清单

- 批次：`c14-public-infrastructure-reit-508000-20260815`
- 抓取时间：`2026-08-14T19:36:22.838413+00:00`
- 方法：对列明的证监会、上交所和基金管理人披露文件及上交所公开查询接口进行匿名、只读 HTTPS 请求。
- 边界：文件哈希只用于本地完整性核验；它们不证明时点可得性、净总回报、个人账户权限、费税、成交或任何外部行动。

| 文件 | 发布者 | 日期／覆盖 | SHA-256 |
|---|---|---|---|
| csrc_public_infrastructure_reit_guideline_announcement_20200807.html | China Securities Regulatory Commission | 2020-08-07 | `4c53ea43ebff29c6f1a07482701de1ba49a145486a0d88dfeb72676b4072cfcf` |
| sse_public_infrastructure_reit_business_rules_20210129.html | Shanghai Stock Exchange | 2021-01-29 | `d26722a02d71873389897bcbdf57c3b970e82b2b2bc8b46c117d44a8a8993ab8` |
| sse_first_public_reits_listing_20210621.html | Shanghai Stock Exchange | 2021-06-21 | `0ad9ae138afee70b05b0ca9987f00f72b3b1aec9804183f52f7f59f9020c4bf0` |
| 508000_updated_prospectus_20241104.pdf | Shanghai Stock Exchange disclosure / Huaan Fund Management | 2024-11-04 | `6b5e9403bc6477b1cc3bc2b423e057ad11022a5a6affca61da1973a4d33fccf2` |
| 508000_product_summary_20240628.pdf | Shanghai Stock Exchange disclosure / Huaan Fund Management | 2024-06-28 | `19c4a57c0bf7992d29948468c338627a4839c1cde60823a9b342810a603c6cb1` |
| 508000_2025_annual_report_20260327.pdf | Shanghai Stock Exchange disclosure / Huaan Fund Management | 2026-03-27 | `3260395947ebac589887a110d9dfb1fd161c1a3c386afe9ccc5aa323037f0a9a` |
| 508000_2024_distribution_announcement_20250415.pdf | Shanghai Stock Exchange disclosure / Huaan Fund Management | 2025-04-15 | `ea634b1c06452af0a4b38a9c4d2904ff126700c40377099e86d00e9084b219b8` |
| sse_508000_daily_market_price_begin0_end5000.jsonp | Shanghai Stock Exchange | 20210621–20260814（1250 行） | `fd3b91c7414124889dfc952918c64e2d7c12636e7584e81cad516d49bcaac00c` |
| sse_508000_distribution_history_page1.jsonp | Shanghai Stock Exchange | 2022-04-13–2026-04-17（9 行） | `fa049720bd92f9d7c5b77cfcb72811184e070e355b8a8e25bca6a1e40e4bea11` |
| sse_508000_nav_history_page1.jsonp | Shanghai Stock Exchange | retrospective response captured 20260815 | `263be42ee97ae28e147d91de3e22e8731db7bc1aa6a7f0d7e1d93619bfb7e37c` |

`tools/verify_source_manifests.py` 会逐一核验本批保留文件的路径、字节数和 SHA-256。公开行情或分配记录不等于可审计的个人净回报或实际成交记录。
