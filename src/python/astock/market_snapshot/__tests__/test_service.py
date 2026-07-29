"""Native tests for the MarketSnapshotV1 data contract."""

from datetime import date, datetime, timezone

import pandas as pd
import pytest

from astock.market_snapshot import MarketSnapshotService


@pytest.fixture
def spot_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"代码": "000001", "最新价": 10.0, "涨跌幅": 1.0, "成交额": 100.0, "涨停价": 10.0, "跌停价": 8.0},
            {"代码": "000002", "最新价": 9.0, "涨跌幅": -1.0, "成交额": 200.0, "涨停价": 11.0, "跌停价": 9.0},
            {"代码": "000003", "最新价": 8.0, "涨跌幅": 0.0, "成交额": 300.0, "涨停价": 9.0, "跌停价": 7.0},
        ]
    )


async def _instrument_rows(codes: list[str] | tuple[str, ...]) -> list[dict[str, object]]:
    names = {
        "000001": "上证指数",
        "399001": "深证成指",
        "399006": "创业板指",
        "000688": "科创50",
        "510300": "沪深300ETF",
    }
    return [
        {
            "code": code,
            "name": names[code],
            "market": "sh",
            "price": 3000.0,
            "change_percent": 1.0,
            "change": 30.0,
            "volume": 100.0,
            "amount": 1000.0,
        }
        for code in codes
        if code in names
    ]


async def _trading_days() -> set[date]:
    return {date(2026, 7, 28)}


def test_tencent_fallback_parser_preserves_observation_source_and_requested_codes() -> None:
    def line(
        symbol: str,
        name: str,
        code: str,
        price: str,
        change: str,
        change_pct: str,
        amount: str,
    ) -> str:
        fields = ["1", name, code, price, "1", "1", "100"]
        fields.extend(["0"] * 22)
        fields.extend(["", "20260728161420", change, change_pct, "1", "1", f"{price}/100/{amount}"])
        assert len(fields) == 36
        return f'v_{symbol}="{"~".join(fields)}";'

    body = "\n".join(
        [
            line("sh000001", "上证指数", "000001", "3813.31", "-44.94", "-1.16", "949683080126"),
            line("sz399001", "深证成指", "399001", "13509.68", "-639.05", "-4.52", "1076097521112"),
        ]
    )

    rows = MarketSnapshotService._parse_tencent_instruments(
        body, ["000001", "399001", "399006"]
    )

    assert [row["code"] for row in rows] == ["000001", "399001"]
    assert rows[0]["source"] == "tencent.qt.gtimg"
    assert rows[0]["price"] == 3813.31
    assert rows[1]["change_percent"] == -4.52
    assert rows[1]["amount"] == 1_076_097_521_112.0


@pytest.mark.asyncio
async def test_build_snapshot_returns_stable_full_market_contract(
    spot_frame: pd.DataFrame,
) -> None:
    async def fetch_spot() -> pd.DataFrame:
        return spot_frame

    service = MarketSnapshotService(
        index_fetcher=_instrument_rows,
        spot_fetcher=fetch_spot,
        trading_day_fetcher=_trading_days,
        now=lambda: datetime(2026, 7, 28, 3, 30, tzinfo=timezone.utc),
    )

    result = await service.build_snapshot(etf_codes=["510300"])

    assert result["schema_version"] == "market_snapshot.v1"
    assert result["observed_at"] == "2026-07-28T03:30:00+00:00"
    assert result["market_session"] == {
        "state": "midday_break",
        "calendar_basis": "exchange_calendar",
    }
    assert result["data_quality"] == "realtime"
    assert [item["code"] for item in result["indices"]] == [
        "000001",
        "399001",
        "399006",
        "000688",
    ]
    assert result["breadth"] == {
        "status": "available",
        "scope": "a_share_equities_returned_by_source",
        "universe_count": 3,
        "priced_count": 3,
        "advancers": 1,
        "decliners": 1,
        "unchanged": 1,
        "coverage_ratio": 1.0,
        "limit_up": 1,
        "limit_down": 1,
    }
    assert result["turnover"] == {
        "status": "available",
        "amount": 600.0,
        "currency": "CNY",
        "scope": "a_share_equities_returned_by_source",
    }
    assert result["etfs"][0]["code"] == "510300"
    assert result["industry_observations"] == []
    assert "fund_flow" not in result
    components = result["provenance"]["components"]
    assert components["indices"]["coverage_ratio"] == 1.0
    assert components["indices"]["quality_tier"] == "realtime"
    assert components["breadth"] == {
        "component": "breadth",
        "source": "eastmoney.push2.a_share_spot",
        "status": "available",
        "coverage_ratio": 1.0,
        "quality_tier": "realtime",
        "observed_at": "2026-07-28T03:30:00+00:00",
        "fallback_path": [],
    }


@pytest.mark.asyncio
async def test_build_snapshot_degrades_when_index_source_fails(
    spot_frame: pd.DataFrame,
) -> None:
    async def failing_index_fetcher(_: list[str] | tuple[str, ...]) -> list[dict[str, object]]:
        raise ConnectionError("index feed offline")

    async def fetch_spot() -> pd.DataFrame:
        return spot_frame

    result = await MarketSnapshotService(
        index_fetcher=failing_index_fetcher,
        spot_fetcher=fetch_spot,
        trading_day_fetcher=_trading_days,
    ).build_snapshot()

    assert result["data_quality"] == "snapshot"
    assert result["indices"] == []
    assert result["breadth"]["status"] == "available"
    assert result["errors"][0]["code"] == "indices_unavailable"
    assert result["provenance"]["quality_tier"] == "snapshot"


@pytest.mark.asyncio
async def test_build_snapshot_uses_industry_count_breadth_when_stock_spot_fails() -> None:
    async def failing_spot() -> pd.DataFrame:
        raise ConnectionError("stock spot unavailable")

    async def industry_breadth() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"板块": "电力", "上涨家数": 8, "下跌家数": 2, "总成交额": 100.0},
                {"板块": "半导体", "上涨家数": 3, "下跌家数": 7, "总成交额": 200.0},
            ]
        )

    result = await MarketSnapshotService(
        index_fetcher=_instrument_rows,
        spot_fetcher=failing_spot,
        industry_breadth_fetcher=industry_breadth,
        trading_day_fetcher=_trading_days,
        now=lambda: datetime(2026, 7, 28, 2, 0, tzinfo=timezone.utc),
    ).build_snapshot()

    assert result["data_quality"] == "snapshot"
    assert result["breadth"] == {
        "status": "available",
        "scope": "industry_constituent_counts_aggregated",
        "universe_count": 20,
        "priced_count": 20,
        "advancers": 11,
        "decliners": 9,
        "unchanged": None,
        "coverage_ratio": 1.0,
        "limit_up": None,
        "limit_down": None,
    }
    assert result["turnover"]["amount"] == 300.0
    assert result["provenance"]["components"]["breadth"]["source"] == (
        "akshare.stock_board_industry_summary_ths"
    )
    assert {warning["code"] for warning in result["warnings"]} >= {
        "breadth_stock_spot_fallback_active",
        "industry_breadth_fallback_active",
    }


@pytest.mark.asyncio
async def test_build_snapshot_marks_fallback_components_as_snapshot(
    spot_frame: pd.DataFrame,
) -> None:
    fallback_spot = spot_frame.copy()
    fallback_spot.attrs["market_snapshot_source"] = "sina.market_center.a_share_spot"
    fallback_spot.attrs["market_snapshot_fallback_path"] = ("sina.market_center.a_share_spot",)

    async def fallback_instruments(codes: list[str] | tuple[str, ...]) -> list[dict[str, object]]:
        return [{**row, "source": "akshare.stock_zh_index_spot_em"} for row in await _instrument_rows(codes)]

    async def fetch_spot() -> pd.DataFrame:
        return fallback_spot

    result = await MarketSnapshotService(
        index_fetcher=fallback_instruments,
        spot_fetcher=fetch_spot,
        trading_day_fetcher=_trading_days,
        now=lambda: datetime(2026, 7, 28, 2, 0, tzinfo=timezone.utc),
    ).build_snapshot()

    assert result["data_quality"] == "snapshot"
    assert result["provenance"]["fallback_path"] == [
        "akshare.stock_zh_index_spot_em",
        "sina.market_center.a_share_spot",
    ]
    assert result["provenance"]["components"]["indices"]["quality_tier"] == "snapshot"
    assert result["provenance"]["components"]["breadth"]["quality_tier"] == "snapshot"


@pytest.mark.asyncio
async def test_build_snapshot_marks_price_limits_unavailable_when_source_omits_them() -> None:
    async def fetch_spot() -> pd.DataFrame:
        return pd.DataFrame(
            [{"代码": "000001", "最新价": 10.0, "涨跌幅": 1.0, "成交额": 100.0}]
        )

    result = await MarketSnapshotService(
        index_fetcher=_instrument_rows,
        spot_fetcher=fetch_spot,
        trading_day_fetcher=_trading_days,
    ).build_snapshot(industry_codes=["bad", "510300"])

    assert result["breadth"]["limit_up"] is None
    assert result["breadth"]["limit_down"] is None
    assert {warning["code"] for warning in result["warnings"]} >= {
        "invalid_instrument_code",
        "price_limit_missing",
    }
    assert result["industry_observations"][0]["instrument_type"] == "industry_proxy"


@pytest.mark.asyncio
async def test_exchange_calendar_closes_a_weekday_holiday_and_blocks_unavailable_calendar(
    spot_frame: pd.DataFrame,
) -> None:
    async def fetch_spot() -> pd.DataFrame:
        return spot_frame

    async def holiday() -> set[date]:
        return set()

    result = await MarketSnapshotService(
        index_fetcher=_instrument_rows,
        spot_fetcher=fetch_spot,
        trading_day_fetcher=holiday,
        now=lambda: datetime(2026, 7, 28, 2, 0, tzinfo=timezone.utc),
    ).build_snapshot()

    assert result["market_session"] == {"state": "closed", "calendar_basis": "exchange_calendar"}
