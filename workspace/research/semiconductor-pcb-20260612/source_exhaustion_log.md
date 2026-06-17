# Source Exhaustion Log

## Purpose

This log records data-source attempts that failed, were stale, or confirmed that required data is not publicly disclosed. It supports the completion audit by showing that remaining gaps are blocked by data availability rather than unfinished collection work.

## Named Customer / Platform Revenue Split

| Attempt/source | Evidence file | Result | Conclusion |
|---|---|---|---|
| Official annual reports | `workspace/research/semiconductor-pcb-20260612/sources/official-annual-core-20260615/`, `workspace/research/semiconductor-pcb-20260612/sources/official-annual-watchlist-20260615/` | Segment/application revenue and anonymous top customers are disclosed; named customers are not. | Cannot derive NVIDIA/Google/ASIC named revenue split. |
| Official/near-official Q&A | `data/customer_disclosure_boundary_evidence.md` | Issuers cite commercial confidentiality and do not discuss specific customer names/business details. | Named-customer gap is a disclosure boundary. |
| IR records | `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/`, `data/ir_platform_chain_summary.md` | Platform comments are available; exact customer revenue not disclosed. | Useful for platform evidence, insufficient for named revenue split. |
| Shengyi SSE interaction probe | `data/shengyi_sse_interaction_probe.md`; `data/raw_sse_company_600183.html`; `data/raw_shengyi_sse_userfeeds_type_10_page1.html`; `data/raw_shengyi_sse_userfeeds_company_q_page1.html` | SSE company page and recent question feed were archived. The feed contains an M8/M9 investor question, but reply pages returned "近1个月暂无回复"; no issuer reply body was recovered beyond the official SSE IR PDF. | Does not close M8/M9/M10 revenue-share, named customer certification or customer-platform EPS gaps. |
| Public web/social claims | `data/named_customer_rumor_registry.md` | Many claims exist about NVIDIA/Google/ASIC/M9, but sources are unverified or non-official. | Keep isolated as rumor, do not use as confirmed evidence. |
| Re-probe for missing global-broker originals | `data/global_broker_original_pdf_probe_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/jpm-shenghong-probe/`; `goldman-hudian-probe/`; `goldman-shengyi-probe/` | JPM/Shenghong and Goldman/Hudian Hibor detail URLs returned Hibor intelligent-terminal download pages, not reports or PDFs. Goldman/Shengyi public URL was a Sina visible repost, not original PDF. Guohai/Pengding 50-page original PDF was downloaded as fallback evidence. | Does not close UBS/JPM/Goldman original-PDF gap; improves fallback original-PDF depth for Pengding only. |
| Second original-PDF refresh | `data/original_pdf_refresh_20260616.md`; `data/huazheng_cbf_deep_refresh_20260616.md`; `data/huazheng_haitong_intl_refresh_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/broker-original-refresh-20260616/` | New Hibor exact-title IDs for UBS/Pengding and JPM/Shenghong again returned terminal download pages. Sina Goldman/Shengyi markdown is a repost. Eleven valid supplemental original PDFs were downloaded: two CMBI Shengyi updates, four Pengding reports from Tianfeng, Kaiyuan, Minsheng and Xingye, two Hudian reports from Xinda and Tianfeng, one Huazheng annual-review report from Zheshang, one 17-page Huazheng CBF deep report from Zheshang, and one 13-page Haitong International Huazheng high-speed CCL / CBF report. | Still does not close UBS/JPM/Goldman original-PDF gap; improves public original-PDF corpus for Shengyi, Pengding, Hudian and Huazheng. |
| Non-Hibor CMBI / Citi / HSBC probe | `data/cmbi_citi_hsbc_probe_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/broker-cmbi-citi-hsbc-probe-20260616/` | Current Citi/HSBC/CMBI query paths did not expose 2026 original PDFs. CMBI official article pages exposed two historical Shengyi-related official PDFs from 2023 and 2021, which were downloaded and extracted. | Improves official-hosted historical source depth for Shengyi, but does not close current global-broker original-PDF or named-customer gap. |
| Customer-side public source probe | `data/customer_side_public_source_probe_20260616.md`; `data/apple_customer_side_official_probe_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/probe-customer-side-20260616/` | Searched NVIDIA / Google TPU / Microsoft Azure / AWS Trainium supplier-list style public sources and Apple official supply-chain / legacy supplier-list / Newsroom clean-energy paths. Results were official generic supplier-quality or supply-chain responsibility pages, SEO/marketing lists, blogs, reposts and inaccessible third-party mirrors. Apple legacy supplier-list PDF paths redirected to the current supply-chain page. Apple 2023 Newsroom clean-energy article confirms Avary Holding joined Apple Supplier Clean Energy Program in 2020, but no official page discloses PCB product, order value, ASP, shipment, platform allocation or revenue split. | Does not close named platform/customer revenue split; confirms customer-side public pages provide at most relationship/program signals, not the needed revenue model data. |
| Victory Giant customer-side / company-side refresh | `data/customer_side_victory_giant_probe_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/probe-customer-side-20260616/google-envicool-victory-giant-reuters-repost.html`; `workspace/research/semiconductor-pcb-20260612/sources/probe-customer-side-20260616/victory-giant-en-about.html` | Victory Giant official English page states global top-AI-client cooperation and AI computing-power PCB leadership, but does not name NVIDIA/Google or quantify revenue. A Communications Today article citing Reuters states Victory Giant counts Nvidia and Google as clients, but this is a repost/article, not customer official disclosure or original Reuters page. | Improves qualitative source-exhaustion evidence only; no named customer revenue, product allocation, ASP, shipment or EPS input. |
| Customs / bill-of-lading public probe | `data/customs_bol_probe_20260616.md`; `workspace/research/semiconductor-pcb-20260612/sources/probe-customs-bol-20260616/` | ImportGenius pages for WUS and Victory Giant show generic shipment profiles and non-AI or non-platform counterparties; Panjiva Nvidia buyer page exposes only high-level/public profile and gates detailed suppliers; ImportYeti was blocked by Cloudflare. | Does not close named platform/customer revenue split; full BOL data would require paid customs database access and manual entity mapping. |
| Final targeted public web sweep | `data/final_public_source_sweep.md` | Re-tested Hudian, Shenghong, Shennan, Shengyi and Huazheng named-customer/model queries. Results were broker abstracts, reposts, social-media claims, old PDFs or limited previews, not reliable public evidence for named customer revenue. | Does not close the named-customer or bottom-up EPS gap. |

## Institutional Holdings / Flow

| Attempt/source | Evidence file | Result | Conclusion |
|---|---|---|---|
| Official annual-report holders | `data/official_holder_supplier_summary.md` | Top-ten holder proxies available. | Covered as official point-in-time proxy. |
| Sina fund holders / circulating holders | `data/advanced_holder_evidence.md`, `data/watchlist_holder_evidence.md` | Fund holder and circulating holder data available for core/watchlist names. | Covered as public holder proxy. |
| CNInfo holder concentration | `data/advanced_holder_evidence.md` | Holder count and per-holder share concentration available for multiple periods. | Covered as ownership concentration proxy. |
| Eastmoney important institution holdings | `data/important_institution_holding_evidence.md`, `data/important_institution_detail_evidence.md` | Important institution aggregate and detail rows available where disclosed. | Covered as quarterly institution proxy. |
| AkShare category holder endpoint | `data/institutional_holding_evidence.md` | `stock_report_fund_hold` returned TypeError in current environment. | Unusable. |
| Eastmoney northbound detail | `data/advanced_holder_evidence.md`, `data/northbound_ranking_evidence.md` | Direct API returned stale 2024 window; current periods empty. HKEX changed disclosure to quarterly from 2024-08-19. | Daily northbound is not a current public-source requirement. |
| Eastmoney individual fund-flow daykline | `data/eastmoney_fund_flow_evidence.md` | Retry through `curl` with browser user-agent succeeded for all 5 core and 6 watchlist tickers, each with 30 rows through 2026-06-15. | Public dayline flow proxy covered; not terminal-grade institutional positioning. |
| SSE official margin-financing detail | `data/sse_margin_financing_official_evidence.md`; `data/raw_sse_margin/` | Shanghai Stock Exchange `RZRQ_MX_INFO` official interface returned 300 rows each for 600183, 688519 and 688630 from 2025-03-20 to 2026-06-15; 603186 returned zero rows. | Improves official financing/leverage proxy for Shanghai-listed names and confirms Huazheng empty detail on the official interface, but still not institutional ownership or order flow. |
| SZSE official margin-financing probe | `data/szse_margin_financing_probe_20260616.md` | AkShare source identified official SZSE wrappers and endpoint parameters for detail, summary and underlying-info downloads. Direct page, xlsx and repeated JSON archival calls to `www.szse.cn` failed with empty responses or `Connection reset by peer` in this local environment. | Does not close Shenzhen-listed margin-financing gaps such as 300400; retry from a stable SZSE-access network or use paid terminal data. |
| Sina margin-financing page for Huazheng | `data/huazheng_haitong_intl_refresh_20260616.md` | `vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/rzrq/index.phtml?symbol=sh603186&edate=2026-06-16` returned the financing/securities-lending table shell but no detail rows for Huazheng in this request. | Not used as valid financing, holding or flow evidence. |
| Eastmoney market-wide clist fund-flow | `data/eastmoney_fund_flow_evidence.md`, `data/main_fund_flow_ranking_evidence.md` | HTTP 502 across all tested market universes. | Unusable in current environment. |
| Eastmoney targeted ulist fund-flow | `data/eastmoney_fund_flow_evidence.md` | HTTP 502 / remote disconnected across tested hosts. | Unusable in current environment. |

## Paid / Terminal Data

| Attempt/source | Evidence file | Result | Conclusion |
|---|---|---|---|
| Tushare SDK/token | `data/paid_data_access_audit.md` | SDK not installed; no token found. | Unavailable. |
| WindPy | `data/paid_data_access_audit.md` | SDK not installed. | Unavailable. |
| iFinD / 同花顺 | `data/paid_data_access_audit.md` | SDK not installed. | Unavailable. |
| Choice | `data/paid_data_access_audit.md` | SDK not installed. | Unavailable. |

## Final Boundary

The remaining unresolved data requires at least one of:

1. Company IR or customer/supplier confirmation that discloses named platform revenue.
2. Paid terminal access for full holdings/flows and customer-chain datasets.
3. Direct industry-chain interviews or non-public sell-side channel checks.
