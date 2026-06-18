# Repost Image Archive and OCR Probe

**Run date:** 2026-06-17

**Purpose:** Archive embedded images from visible JPM/Goldman/Citi repost pages and test whether local OCR can recover additional table evidence.

**OCR boundary:** Local Tesseract has only `eng`, `osd`, and `snum`; no Chinese OCR model is installed. OCR is therefore not reliable for Chinese tables. Images are archived as raw visual evidence.

| Source | Image | Size | File info | OCR usable preview |
|---|---|---:|---|---|
| jpm-shenghong-sina.html | `jpm-shenghong-sina-00.png` | 27250 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-00.png: PNG image data, 750 x 412, 8-bit/color RGBA, non-interlaced | N/A |
| jpm-shenghong-sina.html | `jpm-shenghong-sina-01.png` | 52056 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-01.png: PNG image data, 1056 x 291, 8-bit/color RGB, non-interlaced | N/A |
| jpm-shenghong-sina.html | `jpm-shenghong-sina-02.png` | 27250 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-02.png: PNG image data, 750 x 412, 8-bit/color RGBA, non-interlaced | N/A |
| jpm-shenghong-sina.html | `jpm-shenghong-sina-03.png` | 104075 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-03.png: PNG image data, 987 x 606, 8-bit/color RGB, non-interlaced | N/A |
| jpm-shenghong-sina.html | `jpm-shenghong-sina-04.jpg` | 23360 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-04.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 750x412, components 3 | N/A |
| jpm-shenghong-sina.html | `jpm-shenghong-sina-05.jpg` | 500387 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/jpm-shenghong-sina-05.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 1002x3896, components 3 | N/A |
| goldman-shengyi-sina.html | `goldman-shengyi-sina-00.png` | 27250 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/goldman-shengyi-sina-00.png: PNG image data, 750 x 412, 8-bit/color RGBA, non-interlaced | N/A |
| goldman-shengyi-sina.html | https://k.sinaimg.cn/n/spider20260613/362/w750h412/20260613/5745-1c75fb6c8f95279bbe6e4e7f9e9594d7.png | N/A | ERROR | <HTTPError 400: 'Bad Request'> |
| goldman-shengyi-sina.html | https://k.sinaimg.cn/n/spider20260613/369/w846h323/20260613/0682-b67069732b223840d288ee16d9686f95.png | N/A | ERROR | <HTTPError 400: 'Bad Request'> |
| goldman-shengyi-sina.html | https://k.sinaimg.cn/n/spider20260613/794/w1080h514/20260613/3a8e-9417f8082d71e58673eca3d360a34507.png | N/A | ERROR | <HTTPError 400: 'Bad Request'> |
| citi-shengyi-sina.html | `citi-shengyi-sina-00.png` | 27250 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/citi-shengyi-sina-00.png: PNG image data, 750 x 412, 8-bit/color RGBA, non-interlaced | N/A |
| citi-shengyi-sina.html | `citi-shengyi-sina-01.png` | 57282 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/citi-shengyi-sina-01.png: PNG image data, 836 x 438, 8-bit/color RGB, non-interlaced | N/A |
| citi-shengyi-sina.html | `citi-shengyi-sina-02.png` | 74373 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/citi-shengyi-sina-02.png: PNG image data, 846 x 521, 8-bit/color RGB, non-interlaced | N/A |
| citi-shengyi-sina.html | `citi-shengyi-sina-03.jpg` | 23360 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/citi-shengyi-sina-03.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 750x412, components 3 | N/A |
| citi-shengyi-sina.html | `citi-shengyi-sina-04.jpg` | 500387 | workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/citi-shengyi-sina-04.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 1002x3896, components 3 | N/A |

## Conclusion

- Embedded images were archived locally for future manual/visual review.
- Local OCR cannot reliably extract Chinese tables because Chinese language data is unavailable.
- No additional machine-readable customer/platform revenue split was recovered from OCR in this pass.
