#!/usr/bin/env python3
"""Refresh auditable industry and continuous-inflow capital-flow packets."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
SOURCE_DIR = REFRESH_DIR / "sources" / "market-20260715"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MOBILE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Mobile/15E148"
    )
}

DAILY_URL = "https://fund.eastmoney.com/a/202607143805741620.html"
WEEKLY_URL = "https://fund.eastmoney.com/a/202607103801940931.html"
CONTINUOUS_URL = "https://www.toutiao.com/article/7662319505116267058/"
EXPECTED_INDUSTRIES = {
    "农林牧渔",
    "基础化工",
    "钢铁",
    "有色金属",
    "电子",
    "汽车",
    "家用电器",
    "食品饮料",
    "纺织服饰",
    "轻工制造",
    "医药生物",
    "公用事业",
    "交通运输",
    "房地产",
    "商贸零售",
    "社会服务",
    "银行",
    "非银金融",
    "综合",
    "建筑材料",
    "建筑装饰",
    "电力设备",
    "机械设备",
    "国防军工",
    "计算机",
    "传媒",
    "通信",
    "煤炭",
    "石油石化",
    "环保",
    "美容护理",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=40)
    response.raise_for_status()
    return response.text


def parse_float(value: Any) -> float | None:
    text = str(value or "").strip().replace(",", "").replace("，", "")
    if not text or text in {"-", "—", "null"}:
        return None
    return float(text.replace("%", ""))


def normalized_industry(value: str) -> str:
    return re.sub(r"\s+", "", value)


def parse_industry_table(url: str, raw_name: str, period: str) -> dict[str, Any]:
    raw = fetch(url)
    write_text(SOURCE_DIR / raw_name, raw)
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = " ".join(soup.get_text(" ", strip=True).split())
    date_match = re.search(r"2026年07月(\d{2})日", text)
    if not date_match:
        raise AssertionError(f"{url}: article date is not exposed")
    article_date = f"2026-07-{date_match.group(1)}"
    tables = soup.find_all("table")
    if period == "daily":
        table = next(
            (
                table
                for table in tables
                if "行业" in table.get_text(" ", strip=True)
                and "资金流向" in table.get_text(" ", strip=True)
            ),
            None,
        )
        if table is None:
            raise AssertionError(f"{url}: daily industry table missing")
        rows: list[dict[str, Any]] = []
        for tr in table.find_all("tr")[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
            for offset in (0, 3):
                if len(cells) < offset + 3:
                    continue
                industry = normalized_industry(cells[offset])
                if industry == "-":
                    continue
                rows.append(
                    {
                        "industry": industry,
                        "return_pct": parse_float(cells[offset + 1]),
                        "flow_100mn": parse_float(cells[offset + 2]),
                    }
                )
        if {row["industry"] for row in rows} != EXPECTED_INDUSTRIES:
            raise AssertionError(
                f"{url}: expected 31 industries, got {len(rows)} "
                f"missing={EXPECTED_INDUSTRIES - {row['industry'] for row in rows}}"
            )
        if len(rows) != 31:
            raise AssertionError(f"{url}: duplicate industry rows: {len(rows)}")
        if article_date != "2026-07-14":
            raise AssertionError(f"{url}: expected 2026-07-14, got {article_date}")
        return {
            "schema_version": "astock.industry_flow.daily.v2",
            "source": url,
            "source_type": "DataBao article mirrored by Eastmoney Fund",
            "article_title": title,
            "article_date": article_date,
            "observation_date": article_date,
            "retrieved_at": datetime.now().astimezone().isoformat(),
            "coverage_count": len(rows),
            "coverage_expected": 31,
            "parse_status": "complete",
            "fallback_path": "AkShare Eastmoney push2 endpoint bypassed; public DataBao mirror used",
            "rows": rows,
        }
    table = next(
        (
            table
            for table in tables
            if "行业" in table.get_text(" ", strip=True)
            and "资金流向" in table.get_text(" ", strip=True)
        ),
        None,
    )
    if table is None:
        raise AssertionError(f"{url}: weekly industry table missing")
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        for offset in (0, 3):
            if len(cells) < offset + 3:
                continue
            industry = normalized_industry(cells[offset])
            if industry == "-":
                continue
            rows.append(
                {
                    "industry": industry,
                    "return_pct": parse_float(cells[offset + 1]),
                    "flow_100mn": parse_float(cells[offset + 2]),
                }
            )
    if {row["industry"] for row in rows} != EXPECTED_INDUSTRIES or len(rows) != 31:
        raise AssertionError(f"{url}: expected 31 weekly industries, got {len(rows)}")
    if article_date != "2026-07-10":
        raise AssertionError(f"{url}: expected 2026-07-10, got {article_date}")
    return {
        "schema_version": "astock.industry_flow.weekly.v2",
        "source": url,
        "source_type": "DataBao article mirrored by Eastmoney Fund",
        "article_title": title,
        "article_date": article_date,
        "observation_start": "2026-07-06",
        "observation_end": "2026-07-10",
        "retrieved_at": datetime.now().astimezone().isoformat(),
        "coverage_count": len(rows),
        "coverage_expected": 31,
        "parse_status": "complete",
        "fallback_path": "AkShare Eastmoney push2 endpoint bypassed; public DataBao mirror used",
        "rows": rows,
    }


def parse_continuous() -> dict[str, Any]:
    response = requests.get(
        CONTINUOUS_URL,
        headers=MOBILE_HEADERS,
        timeout=40,
    )
    response.raise_for_status()
    raw = response.text
    write_text(SOURCE_DIR / "toutiao_databao_continuous_inflow_20260714.html", raw)
    soup = BeautifulSoup(html.unescape(raw), "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    article = soup.find("article")
    if article is None:
        raise AssertionError(f"{CONTINUOUS_URL}: article missing")
    article_text = " ".join(article.get_text(" ", strip=True).split())
    if "截至7月14日收盘" not in article_text:
        raise AssertionError(f"{CONTINUOUS_URL}: observation date missing")
    table = article.find("table")
    if table is None:
        raise AssertionError(f"{CONTINUOUS_URL}: continuous table missing")
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if len(cells) != 6:
            continue
        rows.append(
            {
                "ticker": cells[0].zfill(6),
                "company": cells[1],
                "continuous_inflow_days": int(cells[2]),
                "cumulative_inflow_100mn": parse_float(cells[3]),
                "inflow_to_turnover_pct": parse_float(cells[4]),
                "cumulative_return_pct": parse_float(cells[5]),
            }
        )
    if len(rows) != 30:
        raise AssertionError(f"{CONTINUOUS_URL}: expected public top-30 rows, got {len(rows)}")
    if len({row["ticker"] for row in rows}) != 30:
        raise AssertionError(f"{CONTINUOUS_URL}: duplicate ticker rows")
    checks = {
        "002938": (5, 16.98),
        "600988": (9, 15.92),
        "603669": (21, 2.39),
    }
    for ticker, expected in checks.items():
        row = next(row for row in rows if row["ticker"] == ticker)
        if (row["continuous_inflow_days"], row["cumulative_inflow_100mn"]) != expected:
            raise AssertionError(f"{ticker}: cross-check mismatch {row}")
    for row in rows:
        row["stage"] = (
            "quiet_stock_candidate"
            if row["cumulative_return_pct"] <= 6
            else "price_already_reacting"
        )
    rows.sort(
        key=lambda row: (
            row["stage"] != "quiet_stock_candidate",
            -row["continuous_inflow_days"],
            -row["cumulative_inflow_100mn"],
        )
    )
    return {
        "schema_version": "astock.continuous_inflow.v2",
        "source": CONTINUOUS_URL,
        "source_type": "Securities Times/DataBao table syndicated by Toutiao",
        "article_title": title,
        "article_date": "2026-07-14",
        "observation_date": "2026-07-14",
        "retrieved_at": datetime.now().astimezone().isoformat(),
        "coverage_count": len(rows),
        "coverage_expected": 112,
        "public_table_row_count": len(rows),
        "claimed_universe_count": 112,
        "parse_status": "partial",
        "coverage_boundary": "The syndicated page publishes only the top 30 rows while the article claims 112 names.",
        "fallback_path": "AkShare Eastmoney push2 endpoint bypassed; syndicated DataBao table used",
        "rows": rows,
    }


def main() -> None:
    daily = parse_industry_table(
        DAILY_URL, "eastmoney_databao_daily_industry_flow_20260714.html", "daily"
    )
    weekly = parse_industry_table(
        WEEKLY_URL, "eastmoney_databao_weekly_industry_flow_20260710.html", "weekly"
    )
    continuous = parse_continuous()
    write_json(DATA_DIR / "raw_daily_tables_20260714.json", [daily])
    write_json(DATA_DIR / "raw_weekly_tables_20260710_refresh.json", [weekly])
    write_json(DATA_DIR / "raw_continuous_tables_20260714.json", [continuous])
    write_json(
        DATA_DIR / "capital_flow_refresh_manifest_20260715.json",
        {
            "schema_version": "astock.capital_flow_refresh_manifest.v1",
            "data_cutoff": "2026-07-15",
            "industry_daily": "data/raw_daily_tables_20260714.json",
            "industry_weekly": "data/raw_weekly_tables_20260710_refresh.json",
            "continuous_inflow": "data/raw_continuous_tables_20260714.json",
            "daily_observation_date": daily["observation_date"],
            "weekly_observation_end": weekly["observation_end"],
            "continuous_observation_date": continuous["observation_date"],
            "daily_coverage": f"{daily['coverage_count']}/{daily['coverage_expected']}",
            "weekly_coverage": f"{weekly['coverage_count']}/{weekly['coverage_expected']}",
            "continuous_coverage": f"{continuous['coverage_count']}/{continuous['coverage_expected']}",
            "continuous_public_table_status": continuous["parse_status"],
            "parse_status": "industry_complete_continuous_partial",
            "eastmoney_push2_probe": {
                "status": "failed_remote_disconnect",
                "boundary": "probe only; not used as the sole data source",
            },
        },
    )
    print(
        json.dumps(
            {
                "daily": f"{daily['coverage_count']}/31",
                "weekly": f"{weekly['coverage_count']}/31",
                "continuous": f"{continuous['coverage_count']}/112",
                "status": "complete",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
