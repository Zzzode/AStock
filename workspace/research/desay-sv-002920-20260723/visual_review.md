# PDF Visual Review

- Rendered file: `main.pdf`, compiled with XeLaTeX on 2026-07-23 after the Physical AI risk-adjusted-option valuation update.
- Page count: 46 (`pdfinfo`). SHA-256: `8736d0edc2a49ffbabbc300984243bbbb2b173c690c744958a183401154b79bc`.
- Rendered update set: `rendered/physical-ai-option-valuation/` contains 160-dpi sampling pages for the revised IC dashboard, Physical AI chapter and the new risk-adjusted-option valuation table.
- Pages inspected: PDF pages 5 (IC dashboard: CNY86.4 base + CNY2.49 option = CNY88.9), 15 (Physical AI evidence and two-layer framing), 20 (valuation method and new option section), and 21 (FY2028 probability-weighted option table).
- Result: PASS. No clipped CJK glyphs, overlapping frames, table overflow, missing page headers or unreadable dense table was observed. The option table remains readable at normal A4 scale and its probability, conditional value, present value and weighted value columns are distinct.
- Font check: `pdffonts` reports all eight listed fonts as embedded and subsetted where applicable.
- Intentional whitespace: the final disclaimer page remains intentionally sparse and is a standalone disclosure page.
