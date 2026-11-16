# S09-S16 official-source archive manifest

Retrieved with HTTPS `curl`; every response body and its response headers are retained in this directory. SHA-256 values are calculated over the locally retained body.

| Source | Status | HTTP | Content type | Local path (relative to case) | SHA-256 | Retrieved (UTC) | Response metadata |
|---|---|---:|---|---|---|---|---|
| S09 | success | 200 | text/html | `sources/official-20260811/archive/s09-s16/S09.original.html` | `035da7797dfb76921a974bbf0808f889eec2bf22fdb136a1ba90aa16a02e01ea` | 2026-08-11T11:08:33Z | `S09.response-headers.txt` |
| S10 | success | 200 | application/pdf | `sources/official-20260811/archive/s09-s16/S10.original.pdf` | `c2bcd8d0f97355fa8b1545e59b3dca724473388f55cdf65ff37c5ba8a787aade` | 2026-08-11T11:08:33Z | `S10.response-headers.txt` |
| S11 | success | 200 | application/pdf | `sources/official-20260811/archive/s09-s16/S11.original.pdf` | `5c70da7174bdb195b7aac523b6138a40be532b16d9b27ecb99806f787858ca1d` | 2026-08-11T11:08:34Z | `S11.response-headers.txt` |
| S12 | success | 200 | application/pdf | `sources/official-20260811/archive/s09-s16/S12.original.pdf` | `267dc356556ee69aec8f27435bde19838273c70d41342b39a0afabd892a71e8a` | 2026-08-11T11:08:34Z | `S12.response-headers.txt` |
| S13 | success | 200 | text/html | `sources/official-20260811/archive/s09-s16/S13.original.html` | `bfc0314612749daa6ed88f856f2b629561f6713c490b36688ed9a95818cd857c` | 2026-08-11T11:08:33Z | `S13.response-headers.txt` |
| S14 | failed | 200 | text/html | `sources/official-20260811/archive/s09-s16/S14.retry-waf-challenge.html` | `8a3cde6952dbae38e711a67eb2629ed2a7be4ef51c70590af3f0279ee5151cde` | 2026-08-11T11:10:48Z | `S14.retry.response-headers.txt` |
| S15 | success | 200 | text/html | `sources/official-20260811/archive/s09-s16/S15.original.html` | `e7e369b1921885676bb27dfc193969c45e9c13e84dee04844e26d265ec9a7ce0` | 2026-08-11T11:08:33Z | `S15.response-headers.txt` |
| S16 | success | 200 | application/pdf | `sources/official-20260811/archive/s09-s16/S16.original.pdf` | `88e4b1b1cf2a4478409a97bf7be9e1eab94b7ac70fd3bffc6eac0a1853222ab7` | 2026-08-11T11:09:22Z | `S16.response-headers.txt` |

S14 is not a successful archive despite HTTP 200: both requests returned the SHFE SafeLine human-verification page rather than the requested product-rule HTML. The two challenge responses and their headers are retained as failure evidence; no source original is claimed.
