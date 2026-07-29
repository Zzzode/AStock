"""Reproducible whole-market snapshot assembly.

The service deliberately reports observed market data only.  It does not infer
fund flows, trading signals, or sector conclusions from a spot snapshot.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Mapping, Sequence
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from ..data_provenance import DataProvenance, QualityTier
from ..market_data import (
    EASTMONEY_A_SHARE_SPOT_SOURCE,
    fetch_eastmoney_a_share_spot,
    fetch_sina_a_share_spot,
    SINA_A_SHARE_SPOT_SOURCE,
)

IndexFetcher = Callable[[Sequence[str]], Awaitable[list[dict[str, Any]]]]
SpotFetcher = Callable[[], Awaitable[pd.DataFrame]]
IndustryBreadthFetcher = Callable[[], Awaitable[pd.DataFrame]]
TradingDayFetcher = Callable[[], Awaitable[set[date]]]

SCHEMA_VERSION = "market_snapshot.v1"
DEFAULT_INDEX_CODES = ("000001", "399001", "399006", "000688")
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
TENCENT_INSTRUMENT_SOURCE = "tencent.qt.gtimg"


class MarketSnapshotService:
    """Build a source-labelled snapshot of A-share market conditions.

    ``index_fetcher`` and ``spot_fetcher`` are injectable to make the contract
    deterministic under the project's native test framework.
    """

    def __init__(
        self,
        *,
        index_fetcher: IndexFetcher | None = None,
        spot_fetcher: SpotFetcher | None = None,
        industry_breadth_fetcher: IndustryBreadthFetcher | None = None,
        trading_day_fetcher: TradingDayFetcher | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._index_fetcher = index_fetcher or self._fetch_eastmoney_instruments
        self._spot_fetcher = spot_fetcher or self._fetch_a_share_spot
        self._industry_breadth_fetcher = (
            industry_breadth_fetcher or self._fetch_industry_breadth
        )
        self._trading_day_fetcher = trading_day_fetcher or self._fetch_trading_days
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def build_snapshot(
        self,
        *,
        etf_codes: Sequence[str] = (),
        industry_codes: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Return the stable ``market_snapshot.v1`` JSON contract.

        ``industry_codes`` are market-traded industry proxies supplied by the
        caller (for example, an index or sector ETF).  They are not presented as
        a complete industry ranking, because this service has no auditable
        all-industry source adapter yet.
        """
        observed_datetime = self._now().astimezone(timezone.utc)
        observed_at = observed_datetime.isoformat()
        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        requested_etfs = self._normalize_codes(etf_codes, "etf", warnings)
        requested_industries = self._normalize_codes(
            industry_codes, "industry", warnings
        )
        requested_indices = list(DEFAULT_INDEX_CODES)
        instrument_codes = [
            *requested_indices,
            *requested_etfs,
            *requested_industries,
        ]

        index_rows: list[dict[str, Any]] = []
        spot_frame: pd.DataFrame | None = None
        results = await asyncio.gather(
            self._index_fetcher(instrument_codes),
            self._spot_fetcher(),
            self._trading_day_fetcher(),
            return_exceptions=True,
        )
        index_result, spot_result, calendar_result = results
        if isinstance(index_result, Exception):
            errors.append(
                self._issue(
                    "indices_unavailable",
                    "Index and requested instrument source was unavailable.",
                    "eastmoney.push2.ulist",
                    error=index_result,
                )
            )
        else:
            index_rows = index_result
        spot_error: Exception | None = None
        if isinstance(spot_result, Exception):
            spot_error = spot_result
        else:
            spot_frame = spot_result
        industry_breadth_frame: pd.DataFrame | None = None
        if spot_frame is None:
            try:
                industry_breadth_frame = await self._industry_breadth_fetcher()
            except Exception as error:
                errors.append(
                    self._issue(
                        "breadth_unavailable",
                        "A-share spot universe source was unavailable.",
                        EASTMONEY_A_SHARE_SPOT_SOURCE,
                        error=spot_error,
                    )
                )
                errors.append(
                    self._issue(
                        "industry_breadth_unavailable",
                        "Industry constituent-breadth fallback was unavailable.",
                        "akshare.stock_board_industry_summary_ths",
                        error=error,
                    )
                )
            else:
                warnings.append(
                    self._issue(
                        "breadth_stock_spot_fallback_active",
                        "A-share spot universe source was unavailable; industry constituent counts are used as a degraded breadth fallback.",
                        "akshare.stock_board_industry_summary_ths",
                        error=spot_error,
                    )
                )
        calendar_days: set[date] | None
        if isinstance(calendar_result, Exception):
            calendar_days = None
            errors.append(self._issue("trading_calendar_unavailable", "Exchange trading-day calendar source was unavailable.", "akshare.tool_trade_date_hist_sina", error=calendar_result))
        else:
            calendar_days = calendar_result

        instruments = {str(row.get("code")): row for row in index_rows}
        indices = self._select_instruments(
            requested_indices, instruments, "index", warnings
        )
        etfs = self._select_instruments(
            requested_etfs, instruments, "etf", warnings
        )
        industries = self._select_instruments(
            requested_industries, instruments, "industry_proxy", warnings
        )
        spot_source = (
            str(
                spot_frame.attrs.get(
                    "market_snapshot_source", EASTMONEY_A_SHARE_SPOT_SOURCE
                )
            )
            if spot_frame is not None
            else EASTMONEY_A_SHARE_SPOT_SOURCE
        )
        spot_fallback_path = (
            tuple(str(value) for value in spot_frame.attrs.get("market_snapshot_fallback_path", ()))
            if spot_frame is not None
            else ()
        )
        if spot_frame is not None:
            breadth, turnover = self._build_breadth(
                spot_frame, warnings, source=spot_source
            )
        elif industry_breadth_frame is not None:
            spot_source = "akshare.stock_board_industry_summary_ths"
            breadth, turnover = self._build_industry_breadth(
                industry_breadth_frame, warnings, source=spot_source
            )
        else:
            breadth, turnover = self._build_breadth(None, warnings, source=spot_source)

        index_health = self._instrument_health(
            component="indices",
            requested_count=len(requested_indices),
            instruments=indices,
            primary_source="eastmoney.push2.ulist",
            observed_at=observed_at,
        )
        etf_health = self._instrument_health(
            component="etfs",
            requested_count=len(requested_etfs),
            instruments=etfs,
            primary_source="eastmoney.push2.ulist",
            observed_at=observed_at,
        )
        industry_health = self._instrument_health(
            component="industry_observations",
            requested_count=len(requested_industries),
            instruments=industries,
            primary_source="eastmoney.push2.ulist",
            observed_at=observed_at,
        )
        breadth_health = self._breadth_health(
            breadth,
            source=spot_source,
            observed_at=observed_at,
        )
        quality = self._quality_tier(
            index_health=index_health,
            breadth_health=breadth_health,
        )
        source_components = {
            "trading_calendar": {
                "source": "akshare.tool_trade_date_hist_sina",
                "status": "available" if calendar_days is not None else "unavailable",
                "quality_tier": QualityTier.REALTIME.value if calendar_days is not None else QualityTier.UNAVAILABLE.value,
                "observed_at": observed_at,
            },
            "indices": index_health,
            "breadth": breadth_health,
            "turnover": {
                "source": spot_source,
                "status": str(turnover["status"]),
                "quality_tier": breadth_health["quality_tier"],
                "observed_at": observed_at,
            },
            "etfs": etf_health if requested_etfs else None,
            "industry_observations": industry_health if requested_industries else None,
        }
        fallback_path = tuple(
            dict.fromkeys(
                [
                    *index_health["fallback_path"],
                    *breadth_health["fallback_path"],
                    *spot_fallback_path,
                ]
            )
        )
        provenance = DataProvenance(
            source="market_snapshot_v1",
            timestamp=observed_at,
            quality_tier=quality,
            fallback_path=fallback_path,
            warnings=warnings,
            errors=errors,
        ).to_dict()
        provenance["components"] = source_components

        return {
            "schema_version": SCHEMA_VERSION,
            "observed_at": observed_at,
            "market_session": self._market_session(observed_datetime, calendar_days),
            "data_quality": quality.value,
            "indices": indices,
            "breadth": breadth,
            "turnover": turnover,
            "etfs": etfs,
            "industry_observations": industries,
            "warnings": warnings,
            "errors": errors,
            "provenance": provenance,
        }

    @staticmethod
    def _normalize_codes(
        codes: Sequence[str],
        label: str,
        warnings: list[dict[str, Any]],
    ) -> list[str]:
        normalized: list[str] = []
        for raw_code in codes:
            code = "".join(character for character in str(raw_code) if character.isdigit())
            if len(code) != 6:
                warnings.append(
                    {
                        "code": "invalid_instrument_code",
                        "message": f"Ignored invalid {label} code {raw_code!r}; expected 6 digits.",
                        "source": "market_snapshot_v1",
                    }
                )
                continue
            if code not in normalized:
                normalized.append(code)
        return normalized

    @staticmethod
    def _issue(
        code: str,
        message: str,
        source: str,
        *,
        error: Exception | None = None,
    ) -> dict[str, Any]:
        issue: dict[str, Any] = {"code": code, "message": message, "source": source}
        if error is not None:
            issue["details"] = {"error_type": type(error).__name__, "message": str(error)}
        return issue

    @staticmethod
    def _market_for_code(code: str) -> str:
        # The supported broad-market ``000xxx`` index family is Shanghai;
        # exchange-traded funds are identifiable from their usual 5/6 and 1
        # prefixes.  Callers should use listed proxies for industry observation.
        return "sh" if code.startswith(("000", "5", "6")) else "sz"

    async def _fetch_eastmoney_instruments(
        self, codes: Sequence[str]
    ) -> list[dict[str, Any]]:
        if not codes:
            return []
        return await asyncio.to_thread(self._fetch_eastmoney_instruments_sync, codes)

    def _fetch_eastmoney_instruments_sync(
        self, codes: Sequence[str]
    ) -> list[dict[str, Any]]:
        secids = ",".join(
            f"{1 if self._market_for_code(code) == 'sh' else 0}.{code}" for code in codes
        )
        query = urlencode(
            {
                "fltt": "2",
                "fields": "f12,f13,f14,f2,f3,f4,f5,f6",
                "secids": secids,
            }
        )
        request = Request(
            f"https://push2.eastmoney.com/api/qt/ulist.np/get?{query}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        try:
            with urlopen(request, timeout=8) as response:  # nosec B310 - fixed HTTPS host
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
            rows = payload.get("data", {}).get("diff", [])
            if not isinstance(rows, list) or not rows:
                raise ValueError("East Money instrument response has no row list")
            return [
                {
                    "code": str(row.get("f12") or ""),
                    "name": str(row.get("f14") or ""),
                    "market": "sh" if str(row.get("f13")) == "1" else "sz",
                    "price": self._safe_float(row.get("f2")),
                    "change_percent": self._safe_float(row.get("f3")),
                    "change": self._safe_float(row.get("f4")),
                    "volume": self._safe_float(row.get("f5")),
                    "amount": self._safe_float(row.get("f6")),
                    "source": "eastmoney.push2.ulist",
                }
                for row in rows
                if isinstance(row, Mapping)
            ]
        except Exception as primary_error:
            try:
                return self._fetch_akshare_index_spot(codes)
            except Exception as akshare_error:
                try:
                    return self._fetch_tencent_instruments(codes)
                except Exception as tencent_error:
                    raise RuntimeError(
                        "Instrument fetch failed via East Money, AkShare index spot, and Tencent: "
                        f"{type(primary_error).__name__}; {type(akshare_error).__name__}; "
                        f"{type(tencent_error).__name__}"
                    ) from tencent_error

    def _fetch_akshare_index_spot(self, codes: Sequence[str]) -> list[dict[str, Any]]:
        frame = ak.stock_zh_index_spot_em()
        code_column = self._first_column(frame, "代码", "code")
        if code_column is None:
            raise ValueError("AkShare index spot response has no code column")
        normalized = frame[code_column].map(
            lambda value: str(value).zfill(6) if str(value).isdigit() else str(value)
        )
        selected = frame[normalized.isin(codes)]
        return [
            {
                "code": str(row[code_column]).zfill(6),
                "name": str(row.get(self._first_column(frame, "名称", "name") or "") or ""),
                "market": self._market_for_code(str(row[code_column]).zfill(6)),
                "price": self._safe_float(row.get(self._first_column(frame, "最新价", "price") or "")),
                "change_percent": self._safe_float(row.get(self._first_column(frame, "涨跌幅", "change_percent") or "")),
                "change": self._safe_float(row.get(self._first_column(frame, "涨跌额", "change") or "")),
                "volume": self._safe_float(row.get(self._first_column(frame, "成交量", "volume") or "")),
                "amount": self._safe_float(row.get(self._first_column(frame, "成交额", "amount") or "")),
                "source": "akshare.stock_zh_index_spot_em",
            }
            for _, row in selected.iterrows()
        ]

    def _fetch_tencent_instruments(self, codes: Sequence[str]) -> list[dict[str, Any]]:
        """Fetch index and listed-proxy observations from Tencent as a fallback.

        This source is observation-only: the surrounding health contract marks
        it as a fallback ``snapshot`` rather than a primary decision source.
        """
        symbols = ",".join(
            f"{self._market_for_code(code)}{code}" for code in codes
        )
        request = Request(
            f"https://qt.gtimg.cn/q={symbols}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urlopen(request, timeout=8) as response:  # nosec B310 - fixed HTTPS host
            body = response.read().decode("gbk", errors="replace")
        rows = self._parse_tencent_instruments(body, codes)
        if not rows:
            raise ValueError("Tencent instrument response has no usable requested quotes")
        return rows

    @classmethod
    def _parse_tencent_instruments(
        cls, body: str, codes: Sequence[str]
    ) -> list[dict[str, Any]]:
        requested = {str(code) for code in codes}
        rows: list[dict[str, Any]] = []
        for match in re.finditer(r'v_([a-z]+\d+)="([^"]*)"', body):
            symbol, payload = match.groups()
            fields = payload.split("~")
            if len(fields) < 36:
                continue
            code = str(fields[2] or "").strip()
            if code not in requested:
                continue
            price = cls._safe_float(fields[3])
            if price is None or price <= 0:
                continue
            amount = 0.0
            amount_parts = str(fields[35]).split("/")
            if len(amount_parts) >= 3:
                amount = cls._safe_float(amount_parts[2]) or 0.0
            rows.append(
                {
                    "code": code,
                    "name": str(fields[1] or "").strip(),
                    "market": "sh" if symbol.startswith("sh") else "sz",
                    "price": price,
                    "change_percent": cls._safe_float(fields[32]),
                    "change": cls._safe_float(fields[31]),
                    "volume": cls._safe_float(fields[6]),
                    "amount": amount,
                    "source": TENCENT_INSTRUMENT_SOURCE,
                }
            )
        return rows

    async def _fetch_a_share_spot(self) -> pd.DataFrame:
        try:
            frame = await asyncio.to_thread(fetch_eastmoney_a_share_spot)
            frame.attrs["market_snapshot_source"] = EASTMONEY_A_SHARE_SPOT_SOURCE
            frame.attrs["market_snapshot_fallback_path"] = ()
            return frame
        except Exception as primary_error:
            try:
                frame = await asyncio.to_thread(fetch_sina_a_share_spot)
                frame.attrs["market_snapshot_source"] = SINA_A_SHARE_SPOT_SOURCE
                frame.attrs["market_snapshot_fallback_path"] = (SINA_A_SHARE_SPOT_SOURCE,)
                return frame
            except Exception as fallback_error:
                raise RuntimeError(
                    "A-share spot fetch failed via direct East Money and Sina: "
                    f"{type(primary_error).__name__}; {type(fallback_error).__name__}"
                ) from fallback_error

    async def _fetch_industry_breadth(self) -> pd.DataFrame:
        """Fetch public industry constituent counts for degraded breadth only."""
        return await asyncio.wait_for(
            asyncio.to_thread(ak.stock_board_industry_summary_ths), timeout=12
        )

    async def _fetch_trading_days(self) -> set[date]:
        return await asyncio.to_thread(self._fetch_trading_days_sync)

    @staticmethod
    def _fetch_trading_days_sync() -> set[date]:
        frame = ak.tool_trade_date_hist_sina()
        column = MarketSnapshotService._first_column(frame, "trade_date", "日期", "date")
        if column is None:
            raise ValueError("Trading calendar response has no date column")
        days = {pd.to_datetime(value, errors="coerce").date() for value in frame[column] if not pd.isna(pd.to_datetime(value, errors="coerce"))}
        if not days:
            raise ValueError("Trading calendar response has no usable dates")
        return days

    def _select_instruments(
        self,
        codes: Sequence[str],
        instruments: Mapping[str, Mapping[str, Any]],
        instrument_type: str,
        warnings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for code in codes:
            row = instruments.get(code)
            if row is None:
                warnings.append(
                    {
                        "code": "instrument_unavailable",
                        "message": f"No current quote returned for requested {instrument_type} {code}.",
                        "source": "eastmoney.push2.ulist",
                        "details": {"instrument_type": instrument_type, "code": code},
                    }
                )
                continue
            selected.append({"instrument_type": instrument_type, **dict(row)})
        return selected

    @staticmethod
    def _component_source(
        instruments: Sequence[Mapping[str, Any]], default: str
    ) -> str:
        sources = sorted(
            {
                str(instrument["source"])
                for instrument in instruments
                if instrument.get("source")
            }
        )
        return ",".join(sources) if sources else default

    @staticmethod
    def _instrument_health(
        *,
        component: str,
        requested_count: int,
        instruments: Sequence[Mapping[str, Any]],
        primary_source: str,
        observed_at: str,
    ) -> dict[str, Any]:
        returned_count = len(instruments)
        sources = sorted(
            {
                str(instrument.get("source"))
                for instrument in instruments
                if instrument.get("source")
            }
        )
        fallback_path = [source for source in sources if source != primary_source]
        status = (
            "not_requested"
            if requested_count == 0
            else ("available" if returned_count == requested_count else ("partial" if returned_count else "unavailable"))
        )
        quality = (
            QualityTier.REALTIME.value
            if status == "available" and not fallback_path
            else (QualityTier.SNAPSHOT.value if returned_count else QualityTier.UNAVAILABLE.value)
        )
        return {
            "component": component,
            "source": ",".join(sources) if sources else primary_source,
            "status": status,
            "requested_count": requested_count,
            "returned_count": returned_count,
            "coverage_ratio": round(returned_count / requested_count, 6) if requested_count else 1.0,
            "quality_tier": quality,
            "observed_at": observed_at,
            "fallback_path": fallback_path,
        }

    @staticmethod
    def _breadth_health(
        breadth: Mapping[str, Any],
        *,
        source: str,
        observed_at: str,
    ) -> dict[str, Any]:
        status = str(breadth.get("status") or "unavailable")
        coverage = float(breadth.get("coverage_ratio") or 0.0)
        fallback_path = [source] if source != EASTMONEY_A_SHARE_SPOT_SOURCE else []
        quality = (
            QualityTier.REALTIME.value
            if status == "available" and coverage >= 0.98 and not fallback_path
            else (QualityTier.SNAPSHOT.value if status in {"available", "partial"} else QualityTier.UNAVAILABLE.value)
        )
        return {
            "component": "breadth",
            "source": source,
            "status": status,
            "coverage_ratio": coverage,
            "quality_tier": quality,
            "observed_at": observed_at,
            "fallback_path": fallback_path,
        }

    @staticmethod
    def _market_session(observed_at: datetime, trading_days: set[date] | None) -> dict[str, str]:
        local = observed_at.astimezone(SHANGHAI_TZ)
        if trading_days is None:
            return {"state": "closed", "calendar_basis": "unavailable"}
        if local.date() not in trading_days:
            return {"state": "closed", "calendar_basis": "exchange_calendar"}
        local_time = local.time()
        if local_time < datetime.strptime("09:15", "%H:%M").time():
            state = "pre_open"
        elif local_time < datetime.strptime("09:25", "%H:%M").time():
            state = "open_auction"
        elif local_time < datetime.strptime("11:30", "%H:%M").time():
            state = "continuous_morning"
        elif local_time < datetime.strptime("13:00", "%H:%M").time():
            state = "midday_break"
        elif local_time <= datetime.strptime("15:00", "%H:%M").time():
            state = "continuous_afternoon"
        else:
            state = "after_close"
        return {"state": state, "calendar_basis": "exchange_calendar"}

    def _build_breadth(
        self,
        spot_frame: pd.DataFrame | None,
        warnings: list[dict[str, Any]],
        *,
        source: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        unavailable_breadth = {
            "status": "unavailable",
            "scope": "a_share_equities_returned_by_source",
            "universe_count": 0,
            "priced_count": 0,
            "advancers": None,
            "decliners": None,
            "unchanged": None,
            "coverage_ratio": 0.0,
            "limit_up": None,
            "limit_down": None,
        }
        unavailable_turnover = {
            "status": "unavailable",
            "amount": None,
            "currency": "CNY",
            "scope": "a_share_equities_returned_by_source",
        }
        if spot_frame is None or spot_frame.empty:
            return unavailable_breadth, unavailable_turnover

        frame = spot_frame.copy()
        change_column = self._first_column(frame, "涨跌幅", "change_percent")
        price_column = self._first_column(frame, "最新价", "price")
        amount_column = self._first_column(frame, "成交额", "amount")
        upper_limit_column = self._first_column(frame, "涨停价", "upper_limit")
        lower_limit_column = self._first_column(frame, "跌停价", "lower_limit")
        universe_count = len(frame)

        if change_column is None:
            warnings.append(
                {
                    "code": "breadth_change_missing",
                    "message": "Spot source did not provide change-percent data; breadth is unavailable.",
                    "source": source,
                }
            )
            return unavailable_breadth, self._turnover(frame, amount_column)

        change = frame[change_column].map(self._safe_float_or_none)
        valid_change = change.dropna()
        priced_count = len(valid_change)
        breadth: dict[str, Any] = {
            "status": "available" if priced_count == universe_count else "partial",
            "scope": "a_share_equities_returned_by_source",
            "universe_count": universe_count,
            "priced_count": priced_count,
            "advancers": int((valid_change > 0).sum()),
            "decliners": int((valid_change < 0).sum()),
            "unchanged": int((valid_change == 0).sum()),
            "coverage_ratio": round(priced_count / universe_count, 6) if universe_count else 0.0,
            "limit_up": None,
            "limit_down": None,
        }
        if price_column and upper_limit_column and lower_limit_column:
            price = frame[price_column].map(self._safe_float_or_none)
            upper = frame[upper_limit_column].map(self._safe_float_or_none)
            lower = frame[lower_limit_column].map(self._safe_float_or_none)
            comparable_upper = price.notna() & upper.notna() & (upper > 0)
            comparable_lower = price.notna() & lower.notna() & (lower > 0)
            breadth["limit_up"] = int((price[comparable_upper] >= upper[comparable_upper] - 0.0001).sum())
            breadth["limit_down"] = int((price[comparable_lower] <= lower[comparable_lower] + 0.0001).sum())
        else:
            warnings.append(
                {
                    "code": "price_limit_missing",
                    "message": "Spot source lacks exact upper/lower limit prices; limit-up/down counts are unavailable.",
                    "source": source,
                }
            )
        return breadth, self._turnover(frame, amount_column)

    def _build_industry_breadth(
        self,
        industry_frame: pd.DataFrame,
        warnings: list[dict[str, Any]],
        *,
        source: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Aggregate industry constituent counts without claiming a stock-level feed."""
        if industry_frame.empty:
            return self._build_breadth(None, warnings, source=source)
        advances_column = self._first_column(industry_frame, "上涨家数", "advances")
        declines_column = self._first_column(industry_frame, "下跌家数", "declines")
        if advances_column is None or declines_column is None:
            warnings.append(
                {
                    "code": "industry_breadth_columns_missing",
                    "message": "Industry fallback lacks constituent advance/decline counts; market breadth is unavailable.",
                    "source": source,
                }
            )
            return self._build_breadth(None, warnings, source=source)
        advances = industry_frame[advances_column].map(self._safe_float_or_none)
        declines = industry_frame[declines_column].map(self._safe_float_or_none)
        valid = advances.notna() & declines.notna() & (advances >= 0) & (declines >= 0)
        if not valid.any():
            return self._build_breadth(None, warnings, source=source)
        total_advances = int(advances[valid].sum())
        total_declines = int(declines[valid].sum())
        total_constituents = total_advances + total_declines
        warnings.append(
            {
                "code": "industry_breadth_fallback_active",
                "message": "Market breadth is aggregated from public industry constituent counts; unchanged, price-limit, and individual-stock coverage are unavailable.",
                "source": source,
            }
        )
        breadth = {
            "status": "available" if bool(valid.all()) else "partial",
            "scope": "industry_constituent_counts_aggregated",
            "universe_count": total_constituents,
            "priced_count": total_constituents,
            "advancers": total_advances,
            "decliners": total_declines,
            "unchanged": None,
            "coverage_ratio": round(float(valid.sum()) / len(industry_frame), 6),
            "limit_up": None,
            "limit_down": None,
        }
        turnover = self._turnover(
            industry_frame,
            self._first_column(industry_frame, "总成交额", "amount"),
        )
        turnover["scope"] = "industry_constituent_counts_aggregated"
        return breadth, turnover

    def _turnover(self, frame: pd.DataFrame, amount_column: str | None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": "unavailable",
            "amount": None,
            "currency": "CNY",
            "scope": "a_share_equities_returned_by_source",
        }
        if amount_column is None:
            return result
        values = frame[amount_column].map(self._safe_float_or_none).dropna()
        if values.empty:
            return result
        result["status"] = "available"
        result["amount"] = float(values.sum())
        return result

    @staticmethod
    def _first_column(frame: pd.DataFrame, *candidates: str) -> str | None:
        return next((candidate for candidate in candidates if candidate in frame.columns), None)

    @staticmethod
    def _safe_float(value: Any) -> float:
        parsed = MarketSnapshotService._safe_float_or_none(value)
        return parsed if parsed is not None else 0.0

    @staticmethod
    def _safe_float_or_none(value: Any) -> float | None:
        if value is None or isinstance(value, bool):
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return None
        return parsed if pd.notna(parsed) else None

    @staticmethod
    def _quality_tier(
        *, index_health: Mapping[str, Any], breadth_health: Mapping[str, Any]
    ) -> QualityTier:
        if (
            index_health.get("quality_tier") == QualityTier.REALTIME.value
            and breadth_health.get("quality_tier") == QualityTier.REALTIME.value
        ):
            return QualityTier.REALTIME
        if (
            index_health.get("status") in {"available", "partial"}
            or breadth_health.get("status") in {"available", "partial"}
        ):
            return QualityTier.SNAPSHOT
        return QualityTier.UNAVAILABLE
