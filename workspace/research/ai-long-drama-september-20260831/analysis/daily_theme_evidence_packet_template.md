# Daily Theme Evidence Packet Template

Use one file per close, named `data/daily_theme_packet-YYYYMMDD.json`. The packet must preserve source ID, timestamp and warning fields. A missing required value is logged as `null` with `gate_status: incomplete`; it must not be imputed.

```json
{
  "as_of": "YYYY-MM-DDT15:00:00+08:00",
  "catalysts": [{"source_id":"Sxx","published_at":"...","event_type":"...","primary":true}],
  "members": [{"ticker":"...","name":"...","board":"mainboard_or_gem","mapping_tier":"project_direct_or_platform_exposure_or_broad_content_or_satellite","mapping_source_id":"Sxx","open":null,"high":null,"low":null,"close":null,"prior_close":null,"change_pct":null,"amount_cny":null,"amount_rank_in_direct_tier":null,"limit_status":"...","board_count":null,"trading_status":"..."}],
  "market": {"breadth_source_id":"...","risk_release":null,"execution_block":null,"warnings":[]},
  "gate_results": [{"gate":"...","status":"pass_or_fail_or_incomplete","evidence_ids":["Sxx"],"reason":"..."}],
  "decision_state": "WATCH_or_REJECTED_or_CONDITIONAL_PAPER_RESEARCH"
}
```

Source priority: exchange/company/platform original materials first; licensed same-date market data second; media is a cross-check only. Only `project_direct` rows can satisfy the main-board ladder and capacity gates; `platform_exposure` and `broad_content` rows document context or diffusion. D+1 closes the first decision window; D+2 is the confirmation window. The `open/high/low/close`, `amount_rank_in_direct_tier`, limit-state and board-count fields support the D+1--D+5 table; missing fields keep the daily conclusion at observation.
