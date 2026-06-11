"""Market relationship map tests."""

from pathlib import Path
from typing import cast

import pytest

from ..industry import StockIndustry
from ..market_map import (
    IndustryChainNode,
    MarketMapStore,
    MarketSubjectMapping,
    normalize_stock_code,
)


def test_upsert_get_and_list_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "market-map.json"
    store = MarketMapStore(path)

    mapping = MarketSubjectMapping(
        code="000001.SZ",
        name="Ping An Bank",
        industry="Banking",
        industry_code="BK0477",
        sectors=["Finance", "Finance", ""],
        themes=["High dividend"],
        concepts=["Retail banking"],
        industry_chain=[
            IndustryChainNode(
                chain="Banking services",
                stage="Core financial services",
                role="Commercial bank",
                upstream=["Deposits", "Deposits"],
                downstream=["Retail loans"],
            )
        ],
        source_refs=["manual_seed"],
        updated_at="2026-06-12T09:30:00",
    )

    saved = store.upsert(mapping)
    assert saved.code == "000001"
    assert saved.sectors == ["Finance"]

    reloaded = MarketMapStore(path)
    result = reloaded.get("SZ000001")

    assert result is not None
    assert result.code == "000001"
    assert result.name == "Ping An Bank"
    assert result.industry == "Banking"
    assert result.industry_chain[0].upstream == ["Deposits"]
    assert [item.code for item in reloaded.list()] == ["000001"]


def test_theme_lookup_returns_matching_codes(tmp_path: Path) -> None:
    store = MarketMapStore(tmp_path / "market-map.json")
    store.create(
        {
            "code": "1",
            "name": "Ping An Bank",
            "industry": "Banking",
            "themes": ["Dividend yield", "State-owned reform"],
        }
    )
    store.create(
        {
            "code": "600519",
            "name": "Kweichow Moutai",
            "industry": "Baijiu",
            "themes": ["Consumption upgrade"],
        }
    )

    matches = store.filter(theme="Dividend yield")
    relationships = cast(dict[str, object], matches[0].to_packet()["relationships"])

    assert [mapping.code for mapping in matches] == ["000001"]
    assert relationships["themes"] == [
        "Dividend yield",
        "State-owned reform",
    ]


def test_industry_chain_lookup_returns_matching_subjects(tmp_path: Path) -> None:
    store = MarketMapStore(tmp_path / "market-map.json")
    store.upsert(
        MarketSubjectMapping(
            code="300750",
            name="CATL",
            industry="Battery",
            industry_chain=[
                IndustryChainNode(
                    chain="New energy vehicle",
                    stage="Power battery",
                    role="Cell manufacturer",
                    downstream=["Automaker"],
                    related_industries=["Lithium battery"],
                )
            ],
        )
    )
    store.upsert(
        MarketSubjectMapping(
            code="600519",
            name="Kweichow Moutai",
            industry="Baijiu",
            industry_chain=[
                IndustryChainNode(chain="Alcohol consumption", stage="Premium baijiu")
            ],
        )
    )

    matches = store.filter(chain="New energy vehicle", stage="Power battery")

    assert [mapping.code for mapping in matches] == ["300750"]
    assert matches[0].industry_chain[0].related_industries == ["Lithium battery"]


def test_resolve_missing_mapping_returns_stable_packet(tmp_path: Path) -> None:
    store = MarketMapStore(tmp_path / "market-map.json")

    packet = store.resolve("1")

    assert packet == {
        "packet_type": "market_subject_mapping",
        "schema_version": 1,
        "found": False,
        "code": "000001",
        "name": "",
        "mapping": None,
        "relationships": {
            "industry": {
                "name": "",
                "code": None,
            },
            "sectors": [],
            "themes": [],
            "concepts": [],
            "industry_chain": [],
        },
        "source_refs": [],
        "updated_at": "",
        "warnings": ["mapping_not_found"],
    }


def test_code_normalization_and_stock_industry_input(tmp_path: Path) -> None:
    assert normalize_stock_code("SZ000001") == "000001"
    assert normalize_stock_code("1") == "000001"
    assert normalize_stock_code(600519) == "600519"
    with pytest.raises(ValueError):
        normalize_stock_code("SZ")

    store = MarketMapStore(tmp_path / "market-map.json")
    stock = StockIndustry(
        code="sh600036",
        name="China Merchants Bank",
        industry="Banking",
        industry_code="BK0477",
    )

    mapping = MarketSubjectMapping.from_stock_industry(
        stock,
        sectors=["Finance", "Finance"],
        themes=["High dividend", "High dividend"],
    )
    store.upsert(mapping)

    result = store.resolve("600036.SH")
    relationships = cast(dict[str, object], result["relationships"])

    assert result["found"] is True
    assert result["code"] == "600036"
    assert relationships["sectors"] == ["Finance"]
    assert relationships["themes"] == ["High dividend"]
