"""Stock screener - supports parallel processing and error handling"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import asyncio
import pandas as pd
import numpy as np

from .factors import Factor, FactorType, FACTORS, get_factor
from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer
from ..utils import get_logger, DataSourceError, ValidationError

logger = get_logger("screener")


@dataclass
class ScreenResult:
    """Stock screening data snapshot"""

    code: str  # Stock code
    name: Optional[str]  # Stock name
    matched_factors: list[str]  # List of matched factors
    matched_factor_count: int  # Number of matched factors
    factor_checks: dict[str, dict[str, Any]]  # Factor match details
    data: dict[str, Any]  # Raw data
    screened_at: datetime  # Screening timestamp


class StockScreener:
    """Stock screener - supports parallel processing"""

    def __init__(self, quote_service: QuoteService, max_concurrent: int = 3):
        """
        Args:
            quote_service: Quote service instance
            max_concurrent: Max concurrency (default 3, to avoid mini-racer crashes)
        """
        self.quote_service = quote_service
        self.max_concurrent = max_concurrent
        self._stock_names: dict[str, str] = {}  # Stock name cache
        logger.debug(f"Screener initialized, max concurrency: {max_concurrent}")

    async def screen(
        self,
        factors: Optional[list[str]] = None,
        codes: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[ScreenResult]:
        """Execute stock screening data collection (parallel processing)

        Args:
            factors: List of factor keys; uses all factors if empty
            codes: List of stock codes; uses all A-shares if empty
            limit: Result count limit

        Returns:
            Screening results list, in scan order, containing only stocks matching at least one factor
        """
        # Get factor list
        factor_list = self._get_factor_list(factors)

        if not factor_list:
            logger.warning("No available factors")
            return []

        # Get stock list
        stock_codes = self._normalize_codes(codes) if codes else await self._get_all_codes()
        logger.info(
            f"Starting screening, stock count: {len(stock_codes)}, factor count: {len(factor_list)}"
        )

        await self._prime_stock_names(stock_codes, preload_all=not bool(codes))

        # Execute screening sequentially (to avoid mini-racer concurrency crashes)
        # Note: akshare internally uses mini-racer (V8 engine); concurrent initialization causes crashes
        # This is a known issue with Python 3.14 + mini-racer
        valid_results: list[ScreenResult] = []
        errors = 0

        for i, code in enumerate(stock_codes):
            try:
                result = await self._screen_stock(code, factor_list)
                if result and result.matched_factor_count > 0:
                    valid_results.append(result)
            except Exception as e:
                errors += 1
                logger.debug(f"Screening {code} failed: {e}")

            # Progress update (every 200 stocks)
            if (i + 1) % 200 == 0:
                logger.info(f"Processed {i + 1}/{len(stock_codes)} stocks, valid: {len(valid_results)}")

        if errors:
            logger.warning(f"Encountered {errors} errors during screening")

        logger.info(f"Screening complete, valid results: {len(valid_results)}")
        return valid_results[:limit]

    def _normalize_codes(self, codes: Optional[list[str]]) -> list[str]:
        """Deduplicate and normalize stock code list"""
        if not codes:
            return []

        normalized: list[str] = []
        seen: set[str] = set()
        for code in codes:
            digits = "".join(ch for ch in str(code) if ch.isdigit())
            if len(digits) != 6 or digits in seen:
                continue
            normalized.append(digits)
            seen.add(digits)
        return normalized

    async def _prime_stock_names(self, codes: list[str], preload_all: bool) -> None:
        """Prime stock name cache

        Preloads the full stock list for market-wide screening; queries only needed codes for small sets.
        """
        if preload_all:
            try:
                stock_list = await self.quote_service.client.get_stock_list()
                for _, row in stock_list.iterrows():
                    self._stock_names[str(row["code"])] = row.get("name", "")
                return
            except Exception as e:
                logger.warning(f"Failed to load stock names: {e}")
                return

        for code in codes:
            try:
                info = await self.quote_service.get_stock_info(code, allow_remote=False)
                if isinstance(info, dict) and info.get("name"):
                    self._stock_names[code] = str(info["name"])
            except Exception as e:
                logger.debug(f"Failed to load name for stock {code}: {e}")

    async def _screen_stock(
        self, code: str, factors: list[Factor]
    ) -> Optional[ScreenResult]:
        """Screen a single stock

        Args:
            code: Stock code
            factors: Factor list

        Returns:
            Screening result
        """
        try:
            # Get stock data
            data = await self._get_stock_data(code)

            if not data:
                return None

            # Only compute deterministic factor match details; no composite scoring or ranking decisions
            factor_checks = self._evaluate_factors(data, factors)
            matched_factors = [
                factor.key
                for factor in factors
                if factor_checks.get(factor.key, {}).get("matched")
            ]

            return ScreenResult(
                code=code,
                name=data.get("name"),
                matched_factors=matched_factors,
                matched_factor_count=len(matched_factors),
                factor_checks=factor_checks,
                data=data,
                screened_at=datetime.now(),
            )

        except DataSourceError as e:
            logger.debug(f"Failed to fetch data for {code}: {e}")
            return None
        except Exception as e:
            logger.debug(f"Screening {code} failed: {e}")
            return None

    async def _get_stock_data(self, code: str) -> Optional[dict[str, Any]]:
        """Get stock data

        Args:
            code: Stock code

        Returns:
            Stock data dictionary
        """
        try:
            # Get daily data - only fetch last 90 days to reduce data volume
            df = await self.quote_service.get_daily(code, save=False, limit=90)

            if df.empty or len(df) < 30:
                logger.debug(f"Stock {code} has insufficient data")
                return None

            # Compute technical indicators
            analyzer = TechnicalAnalyzer(df)
            df_with_indicators = analyzer.add_all()

            # Get latest data
            latest = df_with_indicators.iloc[-1]
            prev = (
                df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest
            )

            # Compute additional indicators
            vol_ma5 = df_with_indicators["volume"].rolling(5).mean().iloc[-1]
            volatility_20 = (
                df_with_indicators["close"].pct_change().rolling(20).std().iloc[-1]
            )

            # Get PE, PB from daily data (supported by Baostock)
            pe_value = latest.get("pe") if "pe" in latest else None
            pb_value = latest.get("pb") if "pb" in latest else None

            # Use cached stock name
            name = self._stock_names.get(code, "")

            return {
                "code": code,
                "name": name,
                "close": float(latest["close"]),
                "open": float(latest["open"]),
                "high": float(latest["high"]),
                "low": float(latest["low"]),
                "volume": float(latest["volume"]),
                "amount": float(latest["amount"]) if "amount" in latest else 0,
                "pe": float(pe_value) if pe_value is not None and pe_value != 0 else None,
                "pb": float(pb_value) if pb_value is not None and pb_value != 0 else None,
                "turnover_rate": float(latest.get("turn", 0)) if latest.get("turn") else None,
                "ma5": float(latest.get("ma5", 0)),
                "ma10": float(latest.get("ma10", 0)),
                "ma20": float(latest.get("ma20", 0)),
                "ma60": float(latest.get("ma60", 0)),
                "macd": float(latest.get("macd", 0)),
                "macd_signal": float(latest.get("macd_signal", 0)),
                "macd_hist": float(latest.get("macd_hist", 0)),
                "kdj_k": float(latest.get("kdj_k", 0)),
                "kdj_d": float(latest.get("kdj_d", 0)),
                "kdj_j": float(latest.get("kdj_j", 0)),
                "rsi6": float(latest.get("rsi6", 0)),
                "prev_ma5": float(prev.get("ma5", 0)),
                "prev_ma20": float(prev.get("ma20", 0)),
                "vol_ma5": float(vol_ma5),
                "vol_ma5_2x": float(vol_ma5 * 2),
                "volatility_20": float(volatility_20),
            }

        except Exception as e:
            logger.debug(f"Failed to fetch data for {code}: {e}")
            return None

    def _evaluate_factors(
        self, data: dict[str, Any], factors: list[Factor]
    ) -> dict[str, dict[str, Any]]:
        """Generate factor match details"""
        evaluations: dict[str, dict[str, Any]] = {}

        for factor in factors:
            value = data.get(factor.field)
            reference_value = (
                data.get(factor.threshold) if isinstance(factor.threshold, str) else factor.threshold
            )
            previous_value = data.get(f"prev_{factor.field}")
            previous_reference_value = (
                data.get(f"prev_{factor.threshold}")
                if isinstance(factor.threshold, str)
                else factor.threshold
            )
            evaluations[factor.key] = {
                "name": factor.name,
                "type": factor.type.value,
                "description": factor.description,
                "field": factor.field,
                "operator": factor.operator,
                "threshold": factor.threshold,
                "value": value,
                "reference_value": reference_value,
                "previous_value": previous_value,
                "previous_reference_value": previous_reference_value,
                "weight": factor.weight,
                "matched": self._check_condition(data, factor),
            }

        return evaluations

    def _check_condition(self, data: dict[str, Any], factor: Factor) -> bool:
        """Check whether a condition is satisfied"""
        # Get field value
        value = data.get(factor.field)
        if value is None:
            return False

        # Get threshold
        threshold = factor.threshold

        # If threshold is a string, it references another field
        if isinstance(threshold, str):
            threshold = data.get(threshold)
            if threshold is None:
                return False

        # Handle special operators
        if factor.operator == "cross_up":
            prev_value = data.get(f"prev_{factor.field}")
            prev_threshold_key = (
                f"prev_{factor.threshold}"
                if isinstance(factor.threshold, str)
                else None
            )
            prev_threshold = (
                data.get(prev_threshold_key) if prev_threshold_key else threshold
            )

            if prev_value is None or prev_threshold is None:
                return False

            return bool(value > threshold and prev_value <= prev_threshold)

        if factor.operator == "cross_down":
            prev_value = data.get(f"prev_{factor.field}")
            prev_threshold_key = (
                f"prev_{factor.threshold}"
                if isinstance(factor.threshold, str)
                else None
            )
            prev_threshold = (
                data.get(prev_threshold_key) if prev_threshold_key else threshold
            )

            if prev_value is None or prev_threshold is None:
                return False

            return bool(value < threshold and prev_value >= prev_threshold)

        # Handle regular operators
        return self._compare_values(value, factor.operator, threshold)

    def _compare_values(self, value: Any, operator: str, threshold: Any) -> bool:
        """Compare values"""
        try:
            if operator == "lt":
                return bool(value < threshold)
            elif operator == "le":
                return bool(value <= threshold)
            elif operator == "gt":
                return bool(value > threshold)
            elif operator == "ge":
                return bool(value >= threshold)
            elif operator == "eq":
                return bool(value == threshold)
            else:
                return False
        except (TypeError, ValueError):
            return False

    def _get_factor_list(self, factor_keys: Optional[list[str]]) -> list[Factor]:
        """Get factor list"""
        if not factor_keys:
            return list(FACTORS.values())

        factors = []
        for key in factor_keys:
            factor = get_factor(key)
            if factor:
                factors.append(factor)

        return factors

    async def _get_all_codes(self) -> list[str]:
        """Get all A-share stock codes"""
        try:
            df = await self.quote_service.client.get_stock_list()
            codes = [str(code) for code in df["code"].tolist()]
            # Filter out non-main-board stocks (NEEQ, STAR market, etc. can be adjusted as needed)
            # Keep main board, ChiNext, and STAR market
            valid_codes = [
                c for c in codes
                if c.startswith(('0', '3', '6'))
            ]
            return valid_codes
        except Exception as e:
            logger.warning(f"Failed to get stock list: {e}, using default list")
            # Return a more complete default list (partial CSI 300 constituents)
            return [
                # Banks
                "600036", "601166", "601398", "601288", "601988", "600000", "601328",
                # Insurance
                "601318", "601601", "601628",
                # Securities
                "600030", "601211", "600837",
                # Energy
                "600028", "601088", "600019", "601857",
                # Consumer
                "600519", "000858", "000568", "600887",
                # Technology
                "000063", "002415", "300750", "600900",
                # Pharmaceuticals
                "000661", "600276", "300760",
                # Real Estate
                "000002", "600048",
                # Other blue chips
                "600585", "600033", "601668", "600309",
            ]
