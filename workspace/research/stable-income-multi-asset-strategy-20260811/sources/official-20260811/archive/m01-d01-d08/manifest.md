# M01 and D01--D08 Source-Archive Attempt

- Retrieval batch: `2026-08-11T19:11:14+08:00`
- Status: **PARTIAL**
- Machine record: `manifest.json`

| Source | Result | Local immutable record | Boundary |
|---|---|---|---|
| M01 | failed | structured snapshot only | Original GB18030 raw bytes were not retained; a real-time endpoint cannot recreate them. |
| D01 | success | `D01.source` + headers | PDF response, SHA recorded in JSON. |
| D02 | success | `D02_ssl.raw` | Full HTTP response with a PDF body; legacy-TLS-compatible capture. |
| D03 | success | `D03.source` + headers | PDF response, SHA recorded in JSON. |
| D04 | success | `D04.source` + headers | PDF response, SHA recorded in JSON. |
| D05 | failed | none | Official host did not accept a TLS connection. |
| D06 | success | `D06.source` + headers | PDF response, SHA recorded in JSON. |
| D07 | partial | interim PDF only | The final SSE URL returned a bot-denial HTML response, retained separately as failure evidence. |
| D08 | success | `D08.source` + headers | PDF response, SHA recorded in JSON. |

The direct-stock observation remains non-decisive. This batch must not be treated as a complete source archive or as execution evidence.
