"""JSON-backed market relationship mapping for A-share subjects."""

from __future__ import annotations

import json
import builtins
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias, cast

from .industry import StockIndustry

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONDict: TypeAlias = dict[str, JSONValue]

SCHEMA_VERSION = 1
DEFAULT_MARKET_MAP_PATH = (
    Path(__file__).resolve().parents[4] / "data" / "market-map.json"
)


def normalize_stock_code(code: str | int) -> str:
    """Normalize a stock code into the canonical six-digit A-share code."""
    digits = "".join(ch for ch in str(code).strip() if ch.isdigit())
    if not digits:
        raise ValueError("stock code must contain at least one digit")
    if len(digits) >= 6:
        return digits[-6:]
    return digits.zfill(6)


def _clean_text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _optional_text(value: object) -> str | None:
    text = _clean_text(value)
    return text or None


def _dedupe_strings(values: Iterable[object] | None) -> list[str]:
    if values is None:
        return []

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clean_text(value)
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _list_from_value(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return _dedupe_strings([value])
    if isinstance(value, Iterable):
        return _dedupe_strings(value)
    return _dedupe_strings([value])


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(cast(float | int | str, value))
    except (TypeError, ValueError):
        return None


def _mapping_from_value(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    return {}


@dataclass
class IndustryChainNode:
    """One stock's role in an industry chain."""

    chain: str
    stage: str
    role: str = ""
    upstream: list[str] = field(default_factory=list)
    downstream: list[str] = field(default_factory=list)
    related_industries: list[str] = field(default_factory=list)
    weight: float | None = None
    source_refs: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.chain = _clean_text(self.chain)
        self.stage = _clean_text(self.stage)
        self.role = _clean_text(self.role)
        self.upstream = _dedupe_strings(self.upstream)
        self.downstream = _dedupe_strings(self.downstream)
        self.related_industries = _dedupe_strings(self.related_industries)
        self.source_refs = _dedupe_strings(self.source_refs)

    def to_dict(self) -> JSONDict:
        return {
            "chain": self.chain,
            "stage": self.stage,
            "role": self.role,
            "upstream": list(self.upstream),
            "downstream": list(self.downstream),
            "related_industries": list(self.related_industries),
            "weight": self.weight,
            "source_refs": list(self.source_refs),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "IndustryChainNode":
        return cls(
            chain=_clean_text(data.get("chain")),
            stage=_clean_text(data.get("stage")),
            role=_clean_text(data.get("role")),
            upstream=_list_from_value(data.get("upstream")),
            downstream=_list_from_value(data.get("downstream")),
            related_industries=_list_from_value(data.get("related_industries")),
            weight=_optional_float(data.get("weight")),
            source_refs=_list_from_value(data.get("source_refs")),
        )


@dataclass
class MarketSubjectMapping:
    """A deterministic relationship packet for one A-share stock."""

    code: str
    name: str = ""
    industry: str = ""
    industry_code: str | None = None
    sectors: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    industry_chain: list[IndustryChainNode] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.code = normalize_stock_code(self.code)
        self.name = _clean_text(self.name)
        self.industry = _clean_text(self.industry)
        self.industry_code = _optional_text(self.industry_code)
        self.sectors = _dedupe_strings(self.sectors)
        self.themes = _dedupe_strings(self.themes)
        self.concepts = _dedupe_strings(self.concepts)
        self.industry_chain = [
            (
                node
                if isinstance(node, IndustryChainNode)
                else IndustryChainNode.from_dict(_mapping_from_value(node))
            )
            for node in self.industry_chain
        ]
        self.source_refs = _dedupe_strings(self.source_refs)
        self.updated_at = _clean_text(self.updated_at)

    @classmethod
    def from_stock_industry(
        cls,
        stock: StockIndustry,
        *,
        sectors: Iterable[object] | None = None,
        themes: Iterable[object] | None = None,
        concepts: Iterable[object] | None = None,
        industry_chain: (
            Iterable[IndustryChainNode | Mapping[str, object]] | None
        ) = None,
        source_refs: Iterable[object] | None = None,
        updated_at: str = "",
    ) -> "MarketSubjectMapping":
        return cls(
            code=stock.code,
            name=stock.name,
            industry=stock.industry,
            industry_code=stock.industry_code,
            sectors=_dedupe_strings(sectors),
            themes=_dedupe_strings(themes),
            concepts=_dedupe_strings(concepts),
            industry_chain=[
                (
                    node
                    if isinstance(node, IndustryChainNode)
                    else IndustryChainNode.from_dict(node)
                )
                for node in industry_chain or []
            ],
            source_refs=_dedupe_strings(source_refs),
            updated_at=updated_at,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "MarketSubjectMapping":
        chain_items: list[IndustryChainNode] = []
        raw_chain = data.get("industry_chain", [])
        if isinstance(raw_chain, Iterable) and not isinstance(raw_chain, str):
            for item in raw_chain:
                if isinstance(item, IndustryChainNode):
                    chain_items.append(item)
                else:
                    chain_items.append(
                        IndustryChainNode.from_dict(_mapping_from_value(item))
                    )

        return cls(
            code=_clean_text(data.get("code")),
            name=_clean_text(data.get("name")),
            industry=_clean_text(data.get("industry")),
            industry_code=_optional_text(data.get("industry_code")),
            sectors=_list_from_value(data.get("sectors")),
            themes=_list_from_value(data.get("themes")),
            concepts=_list_from_value(data.get("concepts")),
            industry_chain=chain_items,
            source_refs=_list_from_value(data.get("source_refs")),
            updated_at=_clean_text(data.get("updated_at")),
        )

    def to_dict(self) -> JSONDict:
        return {
            "code": self.code,
            "name": self.name,
            "industry": self.industry,
            "industry_code": self.industry_code,
            "sectors": list(self.sectors),
            "themes": list(self.themes),
            "concepts": list(self.concepts),
            "industry_chain": [node.to_dict() for node in self.industry_chain],
            "source_refs": list(self.source_refs),
            "updated_at": self.updated_at,
        }

    def to_packet(self, *, found: bool = True) -> JSONDict:
        return _packet_for_mapping(self, found=found)


MappingInput: TypeAlias = MarketSubjectMapping | StockIndustry | Mapping[str, object]


class MarketMapStore:
    """Persistent relationship store for agent-facing market maps."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else DEFAULT_MARKET_MAP_PATH
        self._mappings: dict[str, MarketSubjectMapping] | None = None

    def create(self, mapping: MappingInput) -> MarketSubjectMapping:
        normalized = self._coerce_mapping(mapping)
        mappings = self._ensure_loaded()
        if normalized.code in mappings:
            raise ValueError(f"market mapping already exists for {normalized.code}")
        mappings[normalized.code] = normalized
        self._save()
        return normalized

    def upsert(self, mapping: MappingInput) -> MarketSubjectMapping:
        normalized = self._coerce_mapping(mapping)
        mappings = self._ensure_loaded()
        mappings[normalized.code] = normalized
        self._save()
        return normalized

    def get(self, code: str | int) -> MarketSubjectMapping | None:
        return self._ensure_loaded().get(normalize_stock_code(code))

    def list(self) -> builtins.list[MarketSubjectMapping]:
        mappings = self._ensure_loaded()
        return [mappings[code] for code in sorted(mappings)]

    def list_mappings(self) -> builtins.list[MarketSubjectMapping]:
        return self.list()

    def filter(
        self,
        *,
        industry: str | None = None,
        sector: str | None = None,
        theme: str | None = None,
        concept: str | None = None,
        chain: str | None = None,
        stage: str | None = None,
    ) -> builtins.list[MarketSubjectMapping]:
        industry_filter = _optional_text(industry)
        sector_filter = _optional_text(sector)
        theme_filter = _optional_text(theme)
        concept_filter = _optional_text(concept)
        chain_filter = _optional_text(chain)
        stage_filter = _optional_text(stage)

        return [
            mapping
            for mapping in self.list()
            if _matches_filter(
                mapping,
                industry=industry_filter,
                sector=sector_filter,
                theme=theme_filter,
                concept=concept_filter,
                chain=chain_filter,
                stage=stage_filter,
            )
        ]

    def resolve(self, code: str | int) -> JSONDict:
        normalized_code = normalize_stock_code(code)
        mapping = self.get(normalized_code)
        if mapping is None:
            return _missing_packet(normalized_code)
        return mapping.to_packet()

    def _coerce_mapping(self, mapping: MappingInput) -> MarketSubjectMapping:
        if isinstance(mapping, MarketSubjectMapping):
            return mapping
        if isinstance(mapping, StockIndustry):
            return MarketSubjectMapping.from_stock_industry(mapping)
        return MarketSubjectMapping.from_dict(mapping)

    def _ensure_loaded(self) -> dict[str, MarketSubjectMapping]:
        if self._mappings is None:
            self._mappings = self._load()
        return self._mappings

    def _load(self) -> dict[str, MarketSubjectMapping]:
        if not self.path.exists():
            return {}

        with self.path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        if not isinstance(raw, Mapping):
            raise ValueError(f"invalid market map file: {self.path}")

        raw_mappings = raw.get("mappings", {})
        if not isinstance(raw_mappings, Mapping):
            raise ValueError(f"invalid market map mappings: {self.path}")

        mappings: dict[str, MarketSubjectMapping] = {}
        for item in raw_mappings.values():
            mapping = MarketSubjectMapping.from_dict(_mapping_from_value(item))
            mappings[mapping.code] = mapping
        return mappings

    def _save(self) -> None:
        mappings = self._ensure_loaded()
        payload: JSONDict = {
            "schema_version": SCHEMA_VERSION,
            "mappings": {code: mappings[code].to_dict() for code in sorted(mappings)},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2, sort_keys=True)
            file.write("\n")
        temp_path.replace(self.path)


def _matches_filter(
    mapping: MarketSubjectMapping,
    *,
    industry: str | None,
    sector: str | None,
    theme: str | None,
    concept: str | None,
    chain: str | None,
    stage: str | None,
) -> bool:
    if industry and industry not in {mapping.industry, mapping.industry_code}:
        return False
    if sector and sector not in mapping.sectors:
        return False
    if theme and theme not in mapping.themes:
        return False
    if concept and concept not in mapping.concepts:
        return False
    if (chain or stage) and not any(
        (chain is None or node.chain == chain)
        and (stage is None or node.stage == stage)
        for node in mapping.industry_chain
    ):
        return False
    return True


def _packet_for_mapping(mapping: MarketSubjectMapping, *, found: bool) -> JSONDict:
    return {
        "packet_type": "market_subject_mapping",
        "schema_version": SCHEMA_VERSION,
        "found": found,
        "code": mapping.code,
        "name": mapping.name,
        "mapping": mapping.to_dict() if found else None,
        "relationships": {
            "industry": {
                "name": mapping.industry,
                "code": mapping.industry_code,
            },
            "sectors": list(mapping.sectors),
            "themes": list(mapping.themes),
            "concepts": list(mapping.concepts),
            "industry_chain": [node.to_dict() for node in mapping.industry_chain],
        },
        "source_refs": list(mapping.source_refs),
        "updated_at": mapping.updated_at,
        "warnings": [],
    }


def _missing_packet(code: str) -> JSONDict:
    return {
        "packet_type": "market_subject_mapping",
        "schema_version": SCHEMA_VERSION,
        "found": False,
        "code": code,
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
