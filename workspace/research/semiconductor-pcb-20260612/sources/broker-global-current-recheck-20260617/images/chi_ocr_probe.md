# Chinese OCR Probe for Repost Images

**Run date:** 2026-06-17

**Tooling:** Local Tesseract with downloaded `chi_sim.traineddata` stored under `workspace/research/semiconductor-pcb-20260612/tools/tessdata/`.

| Image | Text chars | CJK chars | Digits | Preview |
|---|---:|---:|---:|---|
| jpm-shenghong-sina-04.jpg | 0 | 0 | 0 |  |
| jpm-shenghong-sina-05.jpg | 0 | 0 | 0 |  |
| citi-shengyi-sina-04.jpg | 0 | 0 | 0 |  |
| citi-shengyi-sina-00.png | 0 | 0 | 0 |  |
| goldman-shengyi-sina-00.png | 0 | 0 | 0 |  |
| jpm-shenghong-sina-01.png | 0 | 0 | 0 |  |
| jpm-shenghong-sina-00.png | 0 | 0 | 0 |  |
| citi-shengyi-sina-01.png | 0 | 0 | 0 |  |
| citi-shengyi-sina-03.jpg | 0 | 0 | 0 |  |
| jpm-shenghong-sina-02.png | 0 | 0 | 0 |  |
| jpm-shenghong-sina-03.png | 0 | 0 | 0 |  |
| citi-shengyi-sina-02.png | 0 | 0 | 0 |  |

## Useful OCR Findings

- `jpm-shenghong-sina-03.png` yields a readable JPM revenue-assumption table for Shenghong/Victory Giant, including MLPCB, HDI, FPC, other revenue lines and 2026E--2028E totals.
- Several repost images are duplicated article header or subscription images and do not add usable model data.
- OCR remains imperfect and should be used only as supplemental evidence against the already archived article text, not as a substitute for the original PDF.
