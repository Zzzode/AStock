"""Team data packet service

Provides a shared data packet for the Team skill on the Python side.
Does not output buy/sell conclusions or expert stances.
Trading analysis, decisions, and textual reasoning are handled by the Agent layer above.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..config import ConfigManager, UserConfig
from ..memory import FeedbackLearner
from ..quote import QuoteService
from ..stock_picker import StockScreener
from ..storage import Database
from .analysis_service import AnalysisService

DEFAULT_QUESTION = "Is now a good time to enter?"
DEFAULT_SESSIONS_DIR = Path(__file__).resolve().parents[4] / "data" / "sessions"
CORE_AGENT_SPECS: list[dict[str, Any]] = [
    {
        "id": "market-regime-analyst",
        "label": "Market Regime Analyst",
        "mission": "Constrain target-level risk using the separately supplied whole-market state.",
        "required_packet_keys": ["data_quality", "warnings", "question"],
    },
    {
        "id": "market-analyst",
        "label": "Market Analyst",
        "mission": "Interpret target momentum, volume-price structure, and key levels.",
        "required_packet_keys": ["quote", "analysis", "data_quality"],
    },
    {
        "id": "fundamental-analyst",
        "label": "Fundamental Analyst",
        "mission": "Supplement with valuation, earnings, business quality, and order flow logic.",
        "required_packet_keys": ["analysis", "screen", "config"],
    },
    {
        "id": "industry-analyst",
        "label": "Industry Analyst",
        "mission": "Supplement with industry policy, regulatory changes, and macro constraints.",
        "required_packet_keys": ["analysis", "warnings", "question"],
    },
    {
        "id": "risk-analyst",
        "label": "Risk Analyst",
        "mission": "Provide position sizing, stop-loss/take-profit levels, and risk exposure boundaries.",
        "required_packet_keys": ["quote", "analysis", "data_quality"],
    },
    {
        "id": "contrarian-analyst",
        "label": "Contrarian Analyst",
        "mission": "Present counterarguments and failure scenarios to challenge the main thesis.",
        "required_packet_keys": ["quote", "analysis", "screen", "warnings"],
    },
    {
        "id": "data-verifier",
        "label": "Data Verifier",
        "mission": "Block unsupported or stale facts from target-level conclusions.",
        "required_packet_keys": ["quote", "analysis", "data_quality", "warnings"],
    },
]
EXPANSION_ROLE_SPECS: dict[str, list[dict[str, Any]]] = {
    "short_term": [
        {
            "id": "short-term-trader",
            "label": "Short-Term Trader",
            "mission": "Provide conditional 1-10 day entry timing and exit conditions.",
            "required_packet_keys": ["quote", "analysis", "data_quality"],
        },
        {
            "id": "execution-liquidity-analyst",
            "label": "Execution & Liquidity Analyst",
            "mission": "Assess A-share tradability, T+1, price-limit, and liquidity constraints.",
            "required_packet_keys": ["quote", "analysis", "screen"],
        },
    ],
    "swing": [
        {
            "id": "swing-trend-analyst",
            "label": "Swing Trend Analyst",
            "mission": "Provide a 3-10 day swing plan with position pacing.",
            "required_packet_keys": ["analysis", "screen", "data_quality"],
        }
    ],
    "long_term": [
        {
            "id": "valuation-specialist",
            "label": "Valuation Specialist",
            "mission": "Assess long-term margin of safety and holding rationale.",
            "required_packet_keys": ["screen", "config", "profiles"],
        }
    ],
    "sentiment": [
        {
            "id": "sector-rotation-analyst",
            "label": "Sector Rotation Analyst",
            "mission": "Assess sector relative strength, crowding, and theme durability.",
            "required_packet_keys": ["quote", "analysis", "warnings"],
        }
    ],
    "portfolio": [
        {
            "id": "portfolio-manager",
            "label": "Portfolio Manager",
            "mission": "Merge only non-vetoed target conclusions into a conditional paper-plan allocation view.",
            "required_packet_keys": ["quote", "analysis", "config", "data_quality"],
        },
        {
            "id": "quant-risk-modeler",
            "label": "Quant Risk Modeler",
            "mission": "Review concentration, scenario, and model-risk limits before allocation.",
            "required_packet_keys": ["quote", "analysis", "data_quality", "warnings"],
        },
        {
            "id": "execution-liquidity-analyst",
            "label": "Execution & Liquidity Analyst",
            "mission": "Review A-share liquidity, T+1, price-limit, and suspension constraints.",
            "required_packet_keys": ["quote", "analysis", "data_quality"],
        },
        {
            "id": "compliance-officer",
            "label": "Compliance Officer",
            "mission": "Confirm source disclosure and research-only boundary compliance.",
            "required_packet_keys": ["data_quality", "warnings", "question"],
        },
    ],
}


@dataclass
class TeamAnalysisResult:
    """Team data packet result"""

    code: str
    question: str
    name: Optional[str] = None
    summary: str = ""
    recommended_roles: list[str] = field(default_factory=lambda: ["core"])
    data_quality: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    orchestration: dict[str, Any] = field(default_factory=dict)
    packet: dict[str, Any] = field(default_factory=dict)
    session_path: Optional[str] = None
    analyzed_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


class TeamAnalysisService:
    """Team data packet service"""

    def __init__(
        self,
        db: Database,
        quote_service: Optional[QuoteService] = None,
        analysis_service: Optional[AnalysisService] = None,
        screener: Optional[StockScreener] = None,
        config_manager: Optional[ConfigManager] = None,
        feedback_learner: Optional[FeedbackLearner] = None,
        sessions_dir: Optional[Path] = None,
    ):
        self.db = db
        self._quote_service = quote_service
        self._analysis_service = analysis_service
        self._screener = screener
        self._config_manager = config_manager
        self._feedback_learner = feedback_learner
        self.sessions_dir = sessions_dir or DEFAULT_SESSIONS_DIR

    @property
    def quote_service(self) -> QuoteService:
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    @property
    def analysis_service(self) -> AnalysisService:
        if not self._analysis_service:
            self._analysis_service = AnalysisService(
                self.db,
                quote_service=self.quote_service,
            )
        return self._analysis_service

    @property
    def screener(self) -> StockScreener:
        if not self._screener:
            self._screener = StockScreener(self.quote_service)
        return self._screener

    @property
    def config_manager(self) -> ConfigManager:
        if not self._config_manager:
            self._config_manager = ConfigManager()
        return self._config_manager

    @property
    def feedback_learner(self) -> FeedbackLearner:
        if not self._feedback_learner:
            self._feedback_learner = FeedbackLearner()
        return self._feedback_learner

    async def analyze(
        self,
        code: str,
        question: str = DEFAULT_QUESTION,
        days: int = 100,
        user_id: str = "default",
    ) -> TeamAnalysisResult:
        """Generate the Team shared data packet"""
        normalized_code = self._normalize_code(code)
        normalized_question = question.strip() or DEFAULT_QUESTION
        config = UserConfig()

        try:
            config = self.config_manager.load(user_id)
            analysis_result = await self.analysis_service.analyze(
                normalized_code,
                days=days,
            )
            if analysis_result.error:
                raise RuntimeError(analysis_result.error)

            quote = analysis_result.quote.copy() if analysis_result.quote else {}
            if not quote:
                quote = await self.quote_service.get_realtime(normalized_code)

            screen_payload = await self._get_screen_payload(normalized_code)
            stock_profile = await self.feedback_learner.get_team_feedback_profile(
                normalized_code
            )
            global_profile = await self.feedback_learner.get_global_profile(
                user_id=user_id
            )

            name = quote.get("name") or analysis_result.name
            if name and not quote.get("name"):
                quote["name"] = name

            data_quality = self._build_data_quality(
                quote=quote,
                analysis_result=analysis_result,
                screen_payload=screen_payload,
                stock_profile=stock_profile,
            )
            warnings = self._build_warnings(
                data_quality=data_quality,
                screen_payload=screen_payload,
                stock_profile=stock_profile,
            )
            recommended_roles = self._recommend_roles(normalized_question)
            orchestration = self._build_orchestration_plan(
                code=normalized_code,
                question=normalized_question,
                recommended_roles=recommended_roles,
                warnings=warnings,
                packet_ready=True,
            )
            packet = {
                "quote": quote,
                "analysis": self.analysis_service.to_dict(analysis_result),
                "screen": screen_payload,
                "config": self._config_to_dict(config),
                "profiles": {
                    "stock": stock_profile,
                    "global": global_profile,
                },
                "question": normalized_question,
                "data_quality": data_quality,
                "warnings": warnings,
                "recommended_roles": recommended_roles,
                "orchestration": orchestration,
            }

            result = TeamAnalysisResult(
                code=normalized_code,
                question=normalized_question,
                name=name,
                summary="Data packet ready, awaiting Agent team reasoning",
                recommended_roles=recommended_roles,
                data_quality=data_quality,
                warnings=warnings,
                orchestration=orchestration,
                packet=packet,
            )
            result.session_path = str(self._save_session_report(result, config))
            return result

        except Exception as exc:
            fallback_roles = self._recommend_roles(normalized_question)
            fallback_warnings = [str(exc)]
            fallback_orchestration = self._build_orchestration_plan(
                code=normalized_code,
                question=normalized_question,
                recommended_roles=fallback_roles,
                warnings=fallback_warnings,
                packet_ready=False,
            )
            result = TeamAnalysisResult(
                code=normalized_code,
                question=normalized_question,
                summary="Data packet generation failed",
                recommended_roles=fallback_roles,
                warnings=fallback_warnings,
                orchestration=fallback_orchestration,
                packet={
                    "question": normalized_question,
                    "warnings": fallback_warnings,
                    "orchestration": fallback_orchestration,
                },
                error=str(exc),
            )
            try:
                result.session_path = str(self._save_session_report(result, config))
            except Exception:
                pass
            return result

    def _normalize_code(self, code: str) -> str:
        """Normalize stock code"""
        digits = "".join(ch for ch in str(code) if ch.isdigit())
        if len(digits) != 6:
            raise ValueError(f"Invalid stock code format: {code}")
        return digits

    async def _get_screen_payload(self, code: str) -> dict[str, Any]:
        """Get single-stock strategy evaluation result (data point only, no conclusions)"""
        try:
            results = await self.screener.screen(codes=[code], limit=1)
        except Exception as exc:
            return {
                "mode": "single_stock",
                "data_quality": "unavailable",
                "total": 0,
                "results": [],
                "error": str(exc),
            }

        return {
            "mode": "single_stock",
            "data_quality": "daily_only",
            "total": len(results),
            "results": [self._serialize_screen_result(result) for result in results],
        }

    def _serialize_screen_result(self, result) -> dict[str, Any]:
        """Serialize ScreenResult"""
        return {
            "code": result.code,
            "name": result.name,
            "matched_factors": result.matched_factors,
            "matched_factor_count": result.matched_factor_count,
            "factor_checks": result.factor_checks,
            "data": result.data,
            "screened_at": result.screened_at.isoformat(),
        }

    def _recommend_roles(self, question: str) -> list[str]:
        """Recommend dynamic role expansion based on question intent"""
        lowered = question.lower()
        roles = ["core"]
        role_keywords = {
            "short_term": [
                "short-term",
                "scalp",
                "intraday",
                "day trade",
                "overnight",
                "t+0",
                "短线",
                "日内",
                "隔夜",
            ],
            "swing": [
                "swing",
                "pullback",
                "rebound",
                "trend recovery",
                "波段",
                "回调",
                "反弹",
            ],
            "long_term": [
                "long-term",
                "value",
                "fundamentals",
                "valuation",
                "earnings",
                "dividend",
                "长期",
                "价值",
                "基本面",
                "估值",
                "业绩",
                "分红",
            ],
            "sentiment": [
                "sentiment",
                "hot topic",
                "theme",
                "capital flow",
                "news",
                "public opinion",
                "情绪",
                "热点",
                "题材",
                "资金",
                "新闻",
            ],
            "portfolio": [
                "portfolio",
                "position size",
                "cash",
                "allocation",
                "risk budget",
                "仓位",
                "组合",
                "现金",
                "配置",
                "风险预算",
            ],
        }

        for role, keywords in role_keywords.items():
            if any(keyword in lowered for keyword in keywords):
                roles.append(role)

        return roles

    def _build_orchestration_plan(
        self,
        code: str,
        question: str,
        recommended_roles: list[str],
        warnings: list[str],
        packet_ready: bool,
    ) -> dict[str, Any]:
        """Build runtime multi-agent orchestration plan"""
        core_agents = [
            self._build_agent_spec(spec, packet_ready) for spec in CORE_AGENT_SPECS
        ]
        expansion_agents: list[dict[str, Any]] = []
        for role in recommended_roles:
            if role == "core":
                continue
            for spec in EXPANSION_ROLE_SPECS.get(role, []):
                expansion_agents.append(self._build_agent_spec(spec, packet_ready))

        active_agents = core_agents + expansion_agents
        return {
            "version": "v2-data-only",
            "strategy": "packet_only_agent_reasoning",
            "source": "astock.capabilities.build_team_packet",
            "packet_ready": packet_ready,
            "code": code,
            "question": question,
            "recommended_roles": recommended_roles,
            "core_agents": core_agents,
            "expansion_agents": expansion_agents,
            "active_agent_ids": [agent["id"] for agent in active_agents],
            "merge_order": [
                "market-regime-analyst",
                "market-analyst",
                "fundamental-analyst",
                "industry-analyst",
                "risk-analyst",
                "contrarian-analyst",
                "data-verifier",
            ]
            + [agent["id"] for agent in expansion_agents],
            "lead_rules": [
                "Python only provides the data packet; it does not output final research conclusions.",
                "Consume the packet first, then decide whether to fetch missing data.",
                "Final analysis, opportunity conclusions, and monitoring triggers are generated by the Agent team.",
            ],
            "warnings": warnings,
        }

    def _build_agent_spec(
        self, spec: dict[str, Any], packet_ready: bool
    ) -> dict[str, Any]:
        """Build execution config for a single role"""
        return {
            "id": spec["id"],
            "label": spec["label"],
            "mission": spec["mission"],
            "required_packet_keys": spec["required_packet_keys"],
            "allow_data_fetch": not packet_ready,
            "max_fetch_attempts": 1,
        }

    def _build_data_quality(
        self,
        quote: dict[str, Any],
        analysis_result,
        screen_payload: dict[str, Any],
        stock_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Aggregate data quality labels"""
        return {
            "quote": quote.get("data_quality", "unavailable"),
            "analysis": analysis_result.data_quality,
            "screen": {
                "mode": screen_payload.get("mode", "single_stock"),
                "data_quality": screen_payload.get("data_quality", "unavailable"),
            },
            "feedback": {
                "sample_count": int(stock_profile.get("sample_count", 0) or 0),
                "quality": (
                    "learned" if stock_profile.get("sample_count", 0) else "cold_start"
                ),
            },
        }

    def _build_warnings(
        self,
        data_quality: dict[str, Any],
        screen_payload: dict[str, Any],
        stock_profile: dict[str, Any],
    ) -> list[str]:
        """Build degradation and risk warnings"""
        warnings: list[str] = []
        quote_quality = data_quality.get("quote")
        if quote_quality == "daily_only":
            warnings.append(
                "Real-time quote degraded to latest trading day daily snapshot."
            )
        elif quote_quality == "snapshot_degraded":
            warnings.append(
                "Real-time quote is a degraded snapshot; order book fields may be incomplete."
            )
        elif quote_quality == "unavailable":
            warnings.append(
                "Real-time quote unavailable; analysis based on historical data only."
            )

        if screen_payload.get("error"):
            warnings.append(
                "Strategy screening failed; only basic quote and technical data available."
            )

        if int(stock_profile.get("sample_count", 0) or 0) == 0:
            warnings.append(
                "User feedback profile is empty; no personalized preference adjustment applied."
            )

        return warnings

    def _config_to_dict(self, config: UserConfig) -> dict[str, Any]:
        """Serialize user configuration"""
        return {
            "user_id": config.user_id,
            "risk_level": config.risk_level.value,
            "trading_style": config.trading_style.value,
            "max_positions": config.max_positions,
            "position_size": config.position_size,
            "default_strategy": config.default_strategy,
        }

    def _save_session_report(
        self,
        result: TeamAnalysisResult,
        config: UserConfig,
    ) -> Path:
        """Save Team Markdown data packet report"""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        report_path = (
            self.sessions_dir / f"team-{result.code}-{result.analyzed_at:%Y%m%d}.md"
        )

        quote = result.packet.get("quote", {})
        observations = result.packet.get("analysis", {}).get("indicators", {})

        lines = [
            f"# {result.name or result.code} ({result.code}) Team Data Packet",
            "",
            f"Generated at: {result.analyzed_at:%Y-%m-%d %H:%M:%S}",
            "",
            "## Task Info",
            "",
            f"- Question: `{result.question}`",
            f"- Status: `{result.summary}`",
            f"- Trading style: `{config.trading_style.value}`",
            f"- Risk level: `{config.risk_level.value}`",
            f"- Recommended expansion: `{', '.join(result.recommended_roles)}`",
            f"- Active roles: `{', '.join(result.orchestration.get('active_agent_ids', [])) or 'core'}`",
            "",
            "## Core Data Snapshot",
            "",
            f"- Latest price: `{float(quote.get('price', 0.0) or 0.0):.2f}`",
            f"- Change percent: `{float(quote.get('change_percent', 0.0) or 0.0):+.2f}%`",
            f"- Daily open/high/low/close: `{observations.get('open', 'n/a')}` / `{observations.get('high', 'n/a')}` / `{observations.get('low', 'n/a')}` / `{observations.get('close', 'n/a')}`",
            f"- Daily volume / amount: `{observations.get('volume', 'n/a')}` / `{observations.get('amount', 'n/a')}`",
            "",
            "## Notes",
            "",
            "- Python is responsible only for data fetching and structured computation; it does not output buy/sell conclusions.",
            "- The upper-layer Agent should generate bull/bear arguments, position sizing, and risk control recommendations based on the packet.",
            "",
            "## Risk Warnings",
            "",
        ]

        if result.warnings:
            lines.extend([f"- {warning}" for warning in result.warnings])
        else:
            lines.append("- No additional degradation warnings at this time.")

        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    def _clean_for_json(self, obj: Any) -> Any:
        """Clean result to ensure JSON-serializable output"""
        if isinstance(obj, dict):
            return {key: self._clean_for_json(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._clean_for_json(value) for value in obj]
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    def to_dict(self, result: TeamAnalysisResult) -> dict[str, Any]:
        """Convert to serializable dictionary"""
        raw = {
            "code": result.code,
            "question": result.question,
            "name": result.name,
            "summary": result.summary,
            "recommended_roles": result.recommended_roles,
            "data_quality": result.data_quality,
            "warnings": result.warnings,
            "orchestration": result.orchestration,
            "packet": result.packet,
            "session_path": result.session_path,
            "analyzed_at": result.analyzed_at.isoformat(),
            "error": result.error,
        }
        return self._clean_for_json(raw)
