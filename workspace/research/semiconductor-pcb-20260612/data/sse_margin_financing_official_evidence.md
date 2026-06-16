# SSE Official Margin Financing Evidence

**Source:** Shanghai Stock Exchange `query.sse.com.cn/commonSoaQuery.do`, `sqlId=RZRQ_MX_INFO`.

**Window queried:** 2025-03-20 to 2026-06-16; raw JSON archived under `data/raw_sse_margin/`.

## Official margin-financing detail

| Ticker | Name | Records | Window | Latest financing balance | Latest financing buy | Latest financing repay | Latest securities-lending balance | Window net financing buy |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 600183 | 生益科技 | 300 | 20250320 to 20260615 | 42.21亿元 | 11.44亿元 | 9.68亿元 | 308,300股 | 35.39亿元 |
| 603186 | 华正新材 | 0 | empty | 0.00亿元 | 0.00亿元 | 0.00亿元 | 0股 | 0.00亿元 |
| 688519 | 南亚新材 | 300 | 20250320 to 20260615 | 7.11亿元 | 2.90亿元 | 3.37亿元 | 36,754股 | 6.14亿元 |
| 688630 | 芯碁微装 | 300 | 20250320 to 20260615 | 9.72亿元 | 2.32亿元 | 2.89亿元 | 38,554股 | 7.02亿元 |

## Interpretation

- SSE official data confirms margin-financing records for Shengyi Technology, Nanya New Material and Circuit Fabology Microelectronics Equipment over the queried window.
- SSE official data returns no detail rows for Huazheng New Materials (`603186`) over the same query window. This upgrades the prior third-party empty result into an official-source boundary for this dataset.
- This is exchange official margin-financing detail, but it is still a leverage / crowding proxy, not institutional ownership, beneficial-owner positioning, active/passive fund classification or realtime order flow.

## Boundary

- The SSE page states that detail information includes only current margin-financing target securities. Empty detail rows therefore cannot be converted into a zero-position conclusion without checking target-eligibility history.
- This evidence improves historical financing coverage for Shanghai-listed names only. Shenzhen-listed names still require SZSE-compatible official detail data or existing public proxies.
