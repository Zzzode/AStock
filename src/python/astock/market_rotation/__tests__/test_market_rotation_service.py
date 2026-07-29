"""Native tests for the market_rotation.v1 cross-section contract."""

from datetime import datetime, timezone

import pandas as pd
import pytest

from astock.market_rotation import MarketRotationService, verify_rotation_history_evidence
from astock.market_rotation import service as rotation_service
from astock.market_rotation.service import EASTMONEY_BOARD_SOURCE, _multi_horizon_returns


def test_multi_horizon_returns_sorts_dates_deduplicates_and_rejects_future_rows() -> None:
    frame = pd.DataFrame(
        {
            "日期": ["2026-07-28", "2026-07-21", "2026-07-22", "2026-07-22", "2026-07-29"],
            "收盘": [110, 100, 101, 102, 999],
        }
    )

    returns = _multi_horizon_returns(frame, cutoff=datetime(2026, 7, 28).date())

    assert returns["5d"] is None
    assert returns["20d"] is None
    assert returns["60d"] is None


@pytest.mark.asyncio
async def test_cross_section_ranks_full_source_rows_and_keeps_observations_non_investable() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"板块名称": "电力", "板块代码": "BK100", "涨跌幅": 1.5, "上涨家数": 8, "下跌家数": 2, "换手率": 1.2},
                {"板块名称": "创新药", "板块代码": "BK200", "涨跌幅": 3.2, "上涨家数": 7, "下跌家数": 3, "换手率": 2.4},
                {"板块名称": "半导体", "板块代码": "BK300", "涨跌幅": -0.4, "上涨家数": 3, "下跌家数": 7, "换手率": 3.1},
            ]
        )

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"板块名称": "AI", "板块代码": "BK400", "涨跌幅": 2.1},
                {"板块名称": "并购重组", "板块代码": "BK500", "涨跌幅": 0.3},
            ]
        )

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        now=lambda: datetime(2026, 7, 28, 2, 0, tzinfo=timezone.utc),
    ).build_cross_section(observation_limit=1)

    assert result["schema_version"] == "market_rotation.v1"
    assert result["data_quality"] == "realtime"
    assert [row["name"] for row in result["rankings"]["industries"]] == ["创新药", "电力", "半导体"]
    assert result["rankings"]["industries"][0]["rank"] == 1
    assert len(result["observation_pool"]) == 2
    assert {item["status"] for item in result["observation_pool"]} == {"observation"}
    assert "multi-horizon relative strength" in result["observation_pool"][0]["promotion_requirements"]
    assert result["observation_pool"][0]["participation_ratio"] == 0.7
    assert result["observation_pool"][0]["breadth_status"] == "broad"
    assert result["provenance"]["components"]["industries"]["coverage_ratio"] == 1.0


@pytest.mark.asyncio
async def test_cross_section_degrades_when_concept_source_fails() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame([{"板块名称": "电力", "涨跌幅": 1.5}])

    async def concepts() -> pd.DataFrame:
        raise ConnectionError("concept feed unavailable")

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
    ).build_cross_section()

    assert result["data_quality"] == "snapshot"
    assert result["rankings"]["concepts"] == []
    assert result["provenance"]["components"]["concepts"]["status"] == "unavailable"
    assert result["errors"][0]["code"] == "concept_unavailable"


@pytest.mark.asyncio
async def test_cross_section_preserves_public_fallback_provenance() -> None:
    async def industries() -> pd.DataFrame:
        frame = pd.DataFrame([{"板块名称": "电力", "涨跌幅": 1.5}])
        frame.attrs["market_rotation_source"] = EASTMONEY_BOARD_SOURCE
        frame.attrs["market_rotation_fallback_path"] = (EASTMONEY_BOARD_SOURCE,)
        return frame

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame([{"板块名称": "创新药", "涨跌幅": 2.5}])

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
    ).build_cross_section()

    assert result["rankings"]["industries"][0]["source"] == EASTMONEY_BOARD_SOURCE
    assert result["provenance"]["fallback_path"] == [EASTMONEY_BOARD_SOURCE]
    assert result["data_quality"] == "snapshot"
    assert result["warnings"][0]["code"] == "component_fallback_active"


@pytest.mark.asyncio
async def test_industry_fetch_uses_tonghuashun_public_backup_when_direct_board_list_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def secondary() -> pd.DataFrame:
        return pd.DataFrame([{"板块": "电力", "涨跌幅": 1.5}])

    service = MarketRotationService()
    monkeypatch.setattr(
        service,
        "_fetch_eastmoney_board_list",
        lambda _expression: (_ for _ in ()).throw(ConnectionError("eastmoney unavailable")),
    )
    monkeypatch.setattr(
        rotation_service, "_fetch_tonghuashun_industry_summary", secondary
    )

    frame = await service._fetch_industries()

    assert frame.attrs["market_rotation_source"] == rotation_service.THS_INDUSTRY_SOURCE
    assert frame.attrs["market_rotation_fallback_path"] == (
        rotation_service.THS_INDUSTRY_SOURCE,
    )


def test_tonghuashun_fallback_suppresses_third_party_progress_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = rotation_service.stock_board_industry_ths
    original_factory = module.get_tqdm

    def fake_summary() -> pd.DataFrame:
        assert list(module.get_tqdm()(range(2), desc="progress")) == [0, 1]
        return pd.DataFrame([{"板块": "电力", "涨跌幅": 1.5}])

    monkeypatch.setattr(module, "stock_board_industry_summary_ths", fake_summary)

    frame = rotation_service._fetch_tonghuashun_industry_summary()

    assert frame.iloc[0]["板块"] == "电力"
    assert module.get_tqdm is original_factory


@pytest.mark.asyncio
async def test_concept_fetch_uses_direct_public_board_list_without_akshare_progress_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = MarketRotationService()
    monkeypatch.setattr(
        service,
        "_fetch_eastmoney_board_list",
        lambda expression: pd.DataFrame(
            [{"板块代码": "BK001", "板块名称": "AI", "涨跌幅": 2.0}]
        ),
    )
    monkeypatch.setattr(
        rotation_service.ak,
        "stock_board_concept_name_em",
        lambda: (_ for _ in ()).throw(AssertionError("progress adapter must not run")),
    )

    frame = await service._fetch_concepts()

    assert frame.attrs["market_rotation_source"] == EASTMONEY_BOARD_SOURCE
    assert frame.attrs["market_rotation_fallback_path"] == ()


@pytest.mark.asyncio
async def test_cross_section_normalizes_tonghuashun_industry_schema() -> None:
    async def industries() -> pd.DataFrame:
        frame = pd.DataFrame(
            [{"板块": "电力", "涨跌幅": 1.5, "上涨家数": 8, "下跌家数": 2}]
        )
        frame.attrs["market_rotation_source"] = rotation_service.THS_INDUSTRY_SOURCE
        frame.attrs["market_rotation_fallback_path"] = (
            rotation_service.THS_INDUSTRY_SOURCE,
        )
        return frame

    result = await MarketRotationService(industry_fetcher=industries).build_cross_section(
        include_concepts=False
    )

    assert result["rankings"]["industries"][0]["name"] == "电力"
    assert result["rankings"]["industries"][0]["source"] == rotation_service.THS_INDUSTRY_SOURCE
    assert result["data_quality"] == "snapshot"
    assert result["observation_pool"][0]["subject_type"] == "industry"


@pytest.mark.asyncio
async def test_cross_section_only_claims_history_for_rows_it_validates() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"板块名称": "创新药", "涨跌幅": 3.0},
                {"板块名称": "电力", "涨跌幅": 2.0},
            ]
        )

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame()

    async def history(
        component: str, name: str, _start: object, _end: object
    ) -> pd.DataFrame:
        assert component == "industry"
        assert name == "创新药"
        return pd.DataFrame({"日期": pd.date_range(end="2026-07-28", periods=70), "收盘": list(range(100, 170))})

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        history_fetcher=history,
    ).build_cross_section(
        include_concepts=False,
        observation_limit=2,
        history_validation_limit=1,
    )

    top, second = result["rankings"]["industries"]
    assert top["history_validation_status"] == "verified"
    assert top["multi_horizon_return_pct"]["5d"] == 3.04878
    assert second.get("multi_horizon_return_pct") is None
    history_validation = result["ranking_basis"]["history_validation"]
    assert history_validation["status"] == "available"
    assert history_validation["scope"] == "selected"
    assert history_validation["requested_count"] == 1
    assert history_validation["verified_count"] == 1
    assert history_validation["coverage_ratio"] == 1.0
    assert history_validation["full_cross_section_ready"] is False
    assert history_validation["lookbacks"] == [5, 20, 60]
    assert history_validation["source_record_count"] == 1
    assert verify_rotation_history_evidence(result)["status"] == "pass"


@pytest.mark.asyncio
async def test_history_evidence_rejects_return_tampering() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame([{"板块名称": "创新药", "涨跌幅": 3.0}])

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame()

    async def history(
        _component: str, _name: str, _start: object, _end: object
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "日期": pd.date_range(end="2026-07-28", periods=70),
                "收盘": list(range(100, 170)),
            }
        )

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        history_fetcher=history,
    ).build_cross_section(include_concepts=False, history_validation_limit=1)
    result["rankings"]["industries"][0]["multi_horizon_return_pct"]["5d"] = 999.0

    evidence = verify_rotation_history_evidence(result)

    assert evidence["status"] == "blocked"
    assert any("does not match source records" in failure for failure in evidence["failures"])


@pytest.mark.asyncio
async def test_full_history_scope_covers_every_row_before_claiming_full_cross_section() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"板块名称": "创新药", "涨跌幅": 3.0, "换手率": 2.0},
                {"板块名称": "电力", "涨跌幅": 2.0, "换手率": 1.0},
            ]
        )

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame([{"板块名称": "AI", "涨跌幅": 1.0, "换手率": 3.0}])

    async def history(
        _component: str, _name: str, _start: object, _end: object
    ) -> pd.DataFrame:
        return pd.DataFrame({"日期": pd.date_range(end="2026-07-28", periods=70), "收盘": list(range(100, 170))})

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        history_fetcher=history,
    ).build_cross_section(history_scope="full", history_concurrency=2)

    history_validation = result["ranking_basis"]["history_validation"]
    assert history_validation["scope"] == "full"
    assert history_validation["requested_count"] == 3
    assert history_validation["verified_60d_count"] == 3
    assert history_validation["full_cross_section_ready"] is True
    assert all(
        row["history_validation_status"] == "verified"
        for rows in result["rankings"].values()
        for row in rows
    )
    assert result["ranking_basis"]["crowding_evidence"]["decision_weight"] == 0
    assert result["ranking_basis"]["turnover_attention"]["components"]["industries"]["coverage_ratio"] == 1.0


@pytest.mark.asyncio
async def test_full_history_scope_stays_partial_when_any_universe_row_fails() -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame(
            [{"板块名称": "创新药", "涨跌幅": 3.0}, {"板块名称": "电力", "涨跌幅": 2.0}]
        )

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame()

    async def history(
        _component: str, name: str, _start: object, _end: object
    ) -> pd.DataFrame:
        if name == "电力":
            raise ConnectionError("history unavailable")
        return pd.DataFrame({"日期": pd.date_range(end="2026-07-28", periods=70), "收盘": list(range(100, 170))})

    result = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        history_fetcher=history,
    ).build_cross_section(include_concepts=False, history_scope="full")

    history_validation = result["ranking_basis"]["history_validation"]
    assert history_validation["status"] == "partial"
    assert history_validation["full_cross_section_ready"] is False
    assert history_validation["coverage_60d_ratio"] == 0.5
    assert result["warnings"][-1]["code"] == "history_validation_unavailable"
