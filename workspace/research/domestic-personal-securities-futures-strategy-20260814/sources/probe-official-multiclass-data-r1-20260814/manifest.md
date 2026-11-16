# 官方多资产类别数据可得性探测：原始文件清单

- 批次：`probe-official-multiclass-data-r1-20260814`
- 本地提取时间：`2026-08-14T22:01:10.474430491+08:00` 至
  `2026-08-14T22:03:37.386485645+08:00`
- 方法：未登录的只读 HTTPS GET；使用通用浏览器标识和相应官方页面作为
  Referer；未使用凭证、账户、购买、规避访问限制或任何交易动作。
- 目的：跨 ETF、A 股、公募 REIT、交易所债券、场内期权和商品期货，验证少量
  第一方/交易所接口在本次访问中是否实际响应。
- 结论边界：本目录只证明**在本地提取时**这些 URL 返还了下列小样本；不证明
  历史 `available_at`、版本链、完整覆盖、数据权利、正式回放资格或策略可用性。
  `q=0` 保持不变。

## 已保存的响应

| 文件 | 类别 | 本次响应的有限事实 | 字节 / SHA-256 |
|---|---|---|---|
| `sse_etf_master_current_5.jsonp` | ETF | 当前主表查询的前五行；载荷报告 `pageHelp.total=893` | 4,020 / `df6b0d3619f4af66f917255b6db4446cd5c93496c60e139a22e6c45f026c7563` |
| `sse_reits_master_current_5.jsonp` | 公募 REIT | 当前主表查询的前五行；载荷报告 `pageHelp.total=61` | 4,428 / `6cbae7525e83c2bce508dee2e996d2550d3c65217d9313517197f3740501b680` |
| `sse_astock_master_current_5.jsonp` | A 股 | 指定页面过滤条件下当前主表的前五行；载荷报告 `pageHelp.total=1699` | 6,387 / `c2fb0c66364644ea2ac0076cf0c57f659ab639fa8e59fa359b71e7a18c2e89c6` |
| `sse_etf_dayk_510300_begin0_end5.jsonp` | ETF | `510300` 的索引 0--4 五条日线行；载荷报告 `total=3456` | 311 / `12ed7443143b663043585c7ca8b616e7143fd85e6575d325ea495e065151c0ed` |
| `sse_etf_dayk_510300_begin100_end105.jsonp` | ETF | 同一代码的索引 100--104 五条日线行，显示本次样本中 `begin/end` 非零窗口有效 | 314 / `5c27bbc9e65a67b07a4d26b90ba367b143a60cd8108276b1e85073134f15301a` |
| `sse_astock_dayk_600000_begin0_end5.jsonp` | A 股 | `600000` 的索引 0--4 五条日线行；载荷报告 `total=6368` | 326 / `2b259997477068330963896c227fa17d437045dbb316d6c1ad0a2c88d901de81` |
| `sse_reit_dayk_508000_begin0_end5.jsonp` | 公募 REIT | `508000` 的索引 0--4 五条日线行；载荷报告 `total=1250` | 302 / `e8be7f579292d8f0b589cb7be2509ad919e4e169d920b6f8d5da659fab205a81` |
| `sse_bond_dayk_019766_begin0_end5.jsonp` | 交易所债券 | `019766` 的索引 0--4 五条日线行；载荷报告 `total=238` | 317 / `2b9822a424f943a9463d9ef54029d245ac6d052c2f180eed6c2a4ce7c3565e65` |
| `sse_options_current_contracts_5.jsonp` | 场内期权 | 当前合约查询前五行；载荷报告 `pageHelp.total=754` | 8,877 / `134dbe4ac684078bc132c2b2ebe5ed507b825abfb68f841a8b08dabe813f1cc3` |
| `sse_options_listing_adjust_20250814.jsonp` | 场内期权 | 对 `2025-08-14` 的回溯挂牌调整查询返还八项；`isPagination=false` 下的 `pageHelp.total=0` 不能解释为总体数 | 7,125 / `787fbc528d38cbbc98422136448c0255fc00d7cca95fe7daebbdcc5d6a64bcd3` |
| `shfe_actual_contract_daily_20260814.json` | 商品期货 | 上期所单日实际合约文件，返还 333 个 `o_curinstrument` 行 | 123,300 / `9fbc438bf246a83470e6ce8a73d96edc2bf4011e3534c95b104c241da65357ae` |

每个成功 URL 已在当日复查为 HTTP 200：上交所 JSONP 接口为
`application/json;charset=UTF-8`，上期所日文件为 `application/json`。完整 URL、
Referer、字段和本地提取时间位于机器可读版 [manifest.json](manifest.json)。

## 未成功的单一金融期货入口试探

`https://www.cffex.com.cn/lssjfw/` 在 `2026-08-14T22:03:37+08:00` 的连接在 8 秒后
超时（curl exit 28、HTTP 0）；没有保留响应体。这个环境内的失败不说明中金所
不存在或存在可用历史数据，也不使金融期货进入数据包或回放。

## 不可推定的内容

以上样本没有提供可验证的历史 `available_at`、修订/版本谱系、完整历史人口和
缺页对账、数据保存/归一化/回放/衍生分析/独立复核的书面权利，或完整执行与成本
账本。它们同样未提供 ETF 的 NAV/IOPV 和事件全账本、股票公司行动/终止上市全链、
REIT 运营与现金流、债券应计/票息/信用事件、期权完整生命周期/行权指派，或期货
历史保证金/费率/涨跌停/交割规则。因此不得据此得出产品、资格、配置、持有、交易、
下单或绩效结论。
