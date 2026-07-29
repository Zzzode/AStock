"""Source-labelled inputs for the portfolio structural-risk engine."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timezone
from typing import Any, Mapping

import pandas as pd

from ..data_provenance import DataProvenance, QualityTier
from ..quote import AkShareClient
from .factor_governance import validate_factor_risk_context

DailyFetcher = Callable[[str], Awaitable[pd.DataFrame]]


class PortfolioRiskInputBuilder:
    """Build reproducible correlation and liquidity inputs from daily bars."""

    def __init__(
        self,
        *,
        daily_fetcher: DailyFetcher | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._daily_fetcher = daily_fetcher or self._fetch_daily
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def build(
        self,
        codes: Sequence[str],
        *,
        lookback: int = 60,
        factor_risk_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a ``portfolio_risk_inputs.v1`` packet for supplied codes.

        Factor exposures and scenarios remain empty unless a separately
        governed ``portfolio-factor-risk-context.v1`` packet is supplied.
        """
        normalized = list(dict.fromkeys(_normalize_code(code) for code in codes))
        observed_at = self._now().astimezone(timezone.utc).isoformat()
        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        results = await asyncio.gather(*(self._daily_fetcher(code) for code in normalized), return_exceptions=True)
        series: dict[str, pd.DataFrame] = {}
        health: dict[str, dict[str, Any]] = {}
        for code, result in zip(normalized, results, strict=True):
            if isinstance(result, Exception):
                errors.append({"code": "daily_history_unavailable", "message": f"Daily history unavailable for {code}.", "source": "akshare.daily", "details": {"error_type": type(result).__name__, "message": str(result)}})
                health[code] = {"status": "unavailable", "sample_count": 0}
                continue
            try:
                frame = _normalized_history(result, lookback=lookback)
            except ValueError as error:
                warnings.append({"code": "daily_history_invalid", "message": f"Daily history is unusable for {code}: {error}", "source": "akshare.daily"})
                health[code] = {"status": "unavailable", "sample_count": 0}
                continue
            series[code] = frame
            health[code] = {"status": "available", "sample_count": len(frame), "as_of": frame.index[-1].isoformat()}

        positions: dict[str, dict[str, Any]] = {}
        for code, frame in series.items():
            amounts = frame["amount"].dropna()
            positions[code] = {
                "average_daily_turnover": round(float(amounts.mean()), 2) if not amounts.empty else None,
                "turnover_sample_count": len(amounts),
                "return_sample_count": len(frame["return"].dropna()),
            }
            if amounts.empty:
                warnings.append({"code": "turnover_unavailable", "message": f"Daily turnover unavailable for {code}.", "source": "akshare.daily"})
        correlations: dict[str, float] = {}
        codes_with_series = sorted(series)
        for left_index, left in enumerate(codes_with_series):
            for right in codes_with_series[left_index + 1:]:
                aligned = pd.concat([series[left]["return"], series[right]["return"]], axis=1, join="inner").dropna()
                if len(aligned) < 20:
                    warnings.append({"code": "correlation_sample_insufficient", "message": f"Correlation samples are insufficient for {left}|{right}.", "source": "akshare.daily"})
                    continue
                correlations[f"{left}|{right}"] = round(float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1])), 8)
        quality = QualityTier.SNAPSHOT if series else QualityTier.UNAVAILABLE
        provenance = DataProvenance(
            source="portfolio_risk_inputs_v1",
            timestamp=observed_at,
            quality_tier=quality,
            warnings=warnings,
            errors=errors,
        ).to_dict()
        provenance["components"] = health
        factor_inputs: dict[str, Any] = {
            "factor_exposures": {},
            "stress_scenarios": {},
            "factor_governance": {"status": "missing"},
        }
        if factor_risk_context is not None:
            try:
                context = validate_factor_risk_context(
                    factor_risk_context, required_codes=normalized, now=self._now()
                )
                factor_inputs = {**context.to_risk_inputs(), "factor_governance": {"status": "approved", **context.to_risk_inputs()["factor_governance"]}}
            except ValueError as error:
                warnings.append({
                    "code": "factor_risk_context_invalid",
                    "message": f"Factor risk context cannot support a portfolio decision: {error}",
                    "source": "portfolio.factor_governance",
                })
                factor_inputs["factor_governance"] = {"status": "invalid", "reason": str(error)}
        return {
            "schema_version": "portfolio_risk_inputs.v1",
            "observed_at": observed_at,
            "data_quality": quality.value,
            "lookback_sessions": lookback,
            "positions": positions,
            "correlations": correlations,
            **factor_inputs,
            "warnings": warnings,
            "errors": errors,
            "provenance": provenance,
        }

    async def _fetch_daily(self, code: str) -> pd.DataFrame:
        return await AkShareClient().get_daily_quotes(code, days=180)


def _normalized_history(frame: pd.DataFrame, *, lookback: int) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("empty frame")
    required = {"date", "close", "amount"}
    if not required.issubset(frame.columns):
        raise ValueError("required date, close, and amount columns are missing")
    data = frame[["date", "close", "amount"]].copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data = data.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date").tail(lookback + 1)
    if len(data) < 21:
        raise ValueError("fewer than 21 usable sessions")
    data["return"] = data["close"].pct_change()
    return data.set_index("date")


def _normalize_code(value: str) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    if len(digits) != 6:
        raise ValueError(f"invalid A-share code: {value!r}")
    return digits
