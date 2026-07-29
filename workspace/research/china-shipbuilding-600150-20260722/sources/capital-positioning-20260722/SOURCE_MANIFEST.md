# Capital-positioning source manifest

Collection context: 2026-07-22 after-market research update. URLs, query parameters, reporting dates and quality tiers are recorded in `../../data/capital_positioning_20260722.md`; files below are unmodified raw provider responses.

| File | SHA-256 | Purpose | Quality |
|---|---|---|---|
| `sse_margin_600150_20260622_20260721.json` | `864a5ab3ab2fdca5e149944360387e6e1e0c8739ac00900abb2f12860de62854` | SSE 22-trading-day margin-trading detail | Tier 1 |
| `eastmoney_margin_600150_20260722.json` | `62c7350d36d67b92223ad8ab6484ff26916cd9c193b08534ec393a77e6975d17` | Lending-value and total-balance supplement | Tier 2 |
| `sse_shsc_holdings_600150_20260630.json` | `99887ef567fbbc08526ddab9bea7b3bf91803740f1bc5e96e4052d779fe90129` | Official Shanghai Connect 2026Q2 holding quantity | Tier 1 |
| `sse_shsc_holdings_600150_20260331.json` | `d737304748e71220a06153d416ebad1f9d390cb654728f6a02d6b4bf3aa034ee` | Official Shanghai Connect 2026Q1 holding quantity | Tier 1 |
| `sse_shsc_holdings_600150_20251231.json` | `d257e16fd94e8e4d0bab867f6cee4e7391acf760bce32a40c0d38209b39c4733` | Official Shanghai Connect 2025Q4 holding quantity | Tier 1 |
| `eastmoney_kline_600150_20260630.json` | `4c8cba1ee7543f76f0a86759bb177d9028beb9fbc0721f2975b80dd055766566` | 2026-06-30 reference close for a disclosed holding-date valuation | Tier 2 |
| `eastmoney_kline_600150_20260331.json` | `b679425f3caecbe0114e88ece9a649588ae9866b584c029ee3741d1eb8f57d44` | 2026-03-31 reference close for a disclosed holding-date valuation | Tier 2 |
| `eastmoney_northbound_daily_600150_20260721_unavailable.json` | `ea6528a2204b61a7ee34683a73ca00f8afdc86aadf3f765d4dae39bbfb19dbe7` | Negative response for attempted daily Shanghai Connect holding query | Boundary evidence |
| `eastmoney_fund_holdings_20260630_page1.json` | `8189d8327c4c72410f826632f6a51a4d56e6892bb33565f45c52f332979ec761` | Latest public-fund holding aggregate; includes 600150 row | Tier 2 |
| `eastmoney_fund_holdings_20260331_page1.json` | `faca68380bea98a78d8643a12ae1ac3e6c681bdac1b093725ab8444062197c62` | Prior public-fund holding aggregate for cross-check | Tier 2 |
| `eastmoney_lhb_near_one_year_20260722.json` | `b39072d368e23d13f4ca3d6ebab781e6fe54b6b582d6a8f5c6476d697dd345aa` | Near-one-year Dragon-Tiger aggregate response | Tier 2 |
| `eastmoney_lhb_dates_600150_all_history.json` | `72fecee338a359163e14310e60bb2fd8c9706a53aeb1d77861572ce60b42dd46` | Ticker-specific Dragon-Tiger dates; newest is 2021-09-02 | Tier 2 |

The daily Shanghai Connect negative response only establishes that this attempted public structured query did not provide a 2026-07-21 record. It does not prove zero buying or selling and is not used to calculate a 5/20-day net flow.
