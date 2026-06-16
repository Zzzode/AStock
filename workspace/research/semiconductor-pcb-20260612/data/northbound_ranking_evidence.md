# Northbound Ranking Evidence

**Source:** AkShare `stock_hsgt_hold_stock_em(market="北向")`.

| Indicator | Core hits | Status / rows |
|---|---:|---|
| 今日排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 3日排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 5日排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 10日排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 月排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 季排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |
| 年排行 | 0 | {'error': 'TypeError("\'NoneType\' object is not subscriptable")'} |

## Notes

- This is a ranking endpoint. If a core ticker is absent, it may be outside the returned ranking window rather than absent from northbound holdings.
- Use official annual-report Hong Kong Securities Clearing rows for point-in-time holder evidence.
