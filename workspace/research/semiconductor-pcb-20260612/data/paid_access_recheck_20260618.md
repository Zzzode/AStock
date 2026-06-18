# Paid Access Recheck 2026-06-18

**Purpose:** Refresh local paid/semi-paid market-data SDK, environment variable and home-config availability after the 2026-06-17 audit.

## SDK / Module Result

| Provider | Status | Evidence |
|---|---|---|
| akshare | available | 1.18.41 |
| baostock | available | 00.8.90 |
| tushare | unavailable | not installed / not found |
| WindPy | unavailable | not installed / not found |
| iFinDPy | unavailable | not installed / not found |
| choice | unavailable | not installed / not found |
| jqdatasdk | unavailable | not installed / not found |
| rqdatac | unavailable | not installed / not found |
| datayes | unavailable | not installed / not found |
| xbbg | unavailable | not installed / not found |
| blpapi | unavailable | not installed / not found |
| eikon | unavailable | not installed / not found |
| refinitiv | unavailable | not installed / not found |

## Environment / Config Search

- No environment keys containing Tushare, Wind, iFinD, Choice, JQData, RQData, Datayes, Bloomberg, Refinitiv, Eikon, Panjiva, ImportGenius, Volza, customs or BOL were found.
- Home-directory config search found no market-data or customs/BOL credential files. Matches were false positives such as `WindowManager`, `tailwind`, `unwind` or theme files.

## Boundary

AkShare and Baostock remain available public-data libraries. Paid terminal SDKs/credentials for Tushare, Wind/iFinD/Choice/JQData/RQData/Datayes/Bloomberg/Refinitiv/Eikon and paid BOL/customs providers remain unavailable in the current environment.
