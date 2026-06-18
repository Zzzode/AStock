# Global Broker Image OCR Evidence

**Run date:** 2026-06-17

**Source directory:** `workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/`

**Boundary:** OCR is supplemental evidence from repost images. It is not a substitute for original JPM / Citi PDFs and should not be used to infer named customer/platform revenue split.

| ID | Company | Broker | Source image | Evidence added | Boundary |
|---|---|---|---|---|---|
| JPM-SHENGHONG-FINANCIAL-HIGHLIGHTS-OCR | 胜宏科技 | JPMorgan / 摩根大通 | `jpm-shenghong-sina-01.png` | OCR recovered Table 1 financial highlights: 2023/2024/2025/1Q26 revenue 7.931/10.731/19.292/5.519bn RMB; gross margin 20.7%/22.7%/35.2%/34.5%; net profit 0.671/1.154/4.312/1.288bn RMB; 2025 revenue +80% and net profit +274%. | OCR from repost image; numeric formatting has minor OCR artifacts and must be cross-checked against original PDF if obtained. |
| JPM-SHENGHONG-REVENUE-ASSUMPTIONS-OCR | 胜宏科技 | JPMorgan / 摩根大通 | `jpm-shenghong-sina-03.png` | OCR recovered Table 2 revenue assumptions: MLPCB revenue 2026E/2027E/2028E 15.744/28.226/40.658bn RMB; HDI 16.082/27.785/39.287bn RMB; total revenue 35.450/59.955/84.226bn RMB; 2026E--2028E total growth 84%/69%/40%; HDI contribution about 45%/46%/47%. | OCR from repost image; does not disclose named NVIDIA/Google/Rubin customer revenue split, only product-line revenue assumptions. |
| CITI-SHENGYI-CCL-GM-OCR | 生益科技 | Citi / 花旗 | `citi-shengyi-sina-01.png` | OCR recovered Figure 1 title indicating Shengyi CCL gross-margin trend with 2026--2028E projection above the prior 2021 peak. Exact yearly data labels are not machine-reliable from OCR. | OCR confirms chart topic but not precise values beyond article text. |
| CITI-SHENGYI-EGLASS-ASP-OCR | 生益科技 | Citi / 花旗 | `citi-shengyi-sina-02.png` | OCR recovered Figure 2 title and key labels: e-glass fabric ASP surge YTD, with 1080 series +95% YTD, 2116 series +91% YTD and 7628 series +60% YTD. | OCR from repost image; useful for material-cost / pricing context, not company-specific revenue split. |

## OCR files

- `image_ocr_evidence.md` contains the full OCR excerpts for useful images.
- `stdout_ocr_manifest.json` records coverage and usefulness flags.
- `chi_ocr_probe.md` records the initial Chinese OCR setup and boundaries.
