# Broker Source Exhaustion Log — 2026-08-11

| Ticker / scope | Probe result | Next verification path | Consequence |
|---|---|---|---|
| 002432 | Preferred-window public directory returned zero rows. | Licensed Wind/Choice/iFinD export or broker portal. | `not_found`, valuation weight 0. |
| 000623 | Preferred-window public directory returned zero rows. | Licensed Wind/Choice/iFinD export or broker portal. | `not_found`, valuation weight 0. |
| 600739 | Preferred-window public directory returned zero rows. | Licensed Wind/Choice/iFinD export or broker portal. | `not_found`, valuation weight 0. |
| 600150 | The current detail-page refetch did not expose parseable `zwinfo` / PDF URL. A July original PDF/text was already locally archived and has been re-scoped. | Retry the public page or broker portal. | Forecast evidence retained; no target in original, weight 0. |
| 300390 | The preferred directory probe was empty and the direct detail refetch did not expose an attach URL. A June original PDF/text was already locally archived and has been re-scoped. | Retry the public page or broker portal. | Forecast evidence retained; no target in original, weight 0. |
| 300014 Dongwu | Original PDF downloaded, but the current runtime lacks a PDF text extractor; revenue is not visible in the free abstract. | Run a supported PDF extractor. | CNY103 target, 30x 2026E P/E and NP forecasts are visible; zero-weight until revenue is recovered. |
| 000685 / 600150 / 301308 / 002240 / 300390 | No explicit target in the selected original report. | Future broker update or structured licensed target table. | Forecast-only, weight 0. |

**Runtime limitation:** `.venv/bin/python` is absent, so the required `astock.cli index-report` command could not be run. Existing matching extracted texts were re-scoped; every archive path is still recorded in the normalized consensus packet.
