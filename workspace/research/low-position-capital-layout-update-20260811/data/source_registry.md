# Source Registry

The paired JSON is the source of record. This registry makes the evidence boundary explicit rather than silently mixing the three source classes used in the update.

| Source ID | Scope | Quality | Key boundary |
|---|---|---|---|
| MKT-RAW | 13-name 8/10 completed-session close, price-position and turnover packet; 8/11 pre-open separately labelled | High, public-endpoint fallback | 8/10 close is the valuation price; 8/11 was pre-open. |
| FIN-RAW | FY2025/Q1/H1 official packet | Primary filings / mixed H1 | Nine H1 values are previews, not actuals. |
| F-000703-H1 | 恒逸 actual H1 | Primary official report | Restated comparative and negative H1 OCF. |
| F-002379-H1 | 宏桥 H1 range | Official preview | No H1 revenue/OCF in selected disclosure. |
| F-300014-H1 | 亿纬 H1 range | Official preview | No actual H1 cash-flow evidence at cutoff. |
| F-002497-H1 | 雅化 H1 range | Official preview | H2 needs to validate the full-year denominator. |
| F-301308-H1 | 江波龙 actual H1 | Primary official report | Profit is positive while OCF remains negative. |
| PROBE-H1 | 600739/600150 H1 status | Official search probe | Unavailable is not a negative earnings claim. |
| BRK-RAW | 13-name broker catalog | Original PDF plus explicit gaps | Not a vendor consensus. |
| B-000703 | 国信 | Original PDF | Target range is below current close. |
| B-002379 | 招银国际 | Original PDF | Uses adjusted NP, not directly reconciled statutory NP. |
| B-300014-DW / B-300014-QY | 东吴 / 群益 | Original PDFs | CNY103 and CNY77 are deliberately not averaged. |
| B-002497 | 东吴 | Original PDF | CNY42 is a 16x 2026E P/E anchor, not a guarantee. |
| B-002812 | 东吴 | Original PDF | CNY103 uses a 2027E denominator and remains a sensitivity. |
| PREDECESSOR-0715 / -0722 | Historical research cases | Internal case record | Used only for delta comparison, never as current price evidence. |

Raw source files, URLs, retrieval metadata and warnings are preserved in the linked evidence packets under `data/` and `sources/`.
