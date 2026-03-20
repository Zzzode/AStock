"""反馈学习器

从用户反馈中学习，调整分析权重和置信度。
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class FeedbackRecord:
    """反馈记录"""

    code: str                               # 股票代码
    action: str                             # 建议动作
    outcome: str                            # 反馈结果: good/bad
    strategy: Optional[str] = None          # 关联策略/因子
    note: Optional[str] = None              # 补充说明
    signals: Optional[list[str]] = None     # 关联信号
    confidence: Optional[float] = None      # 当时的置信度
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyPerformance:
    """策略表现"""

    strategy: str
    total_count: int = 0
    good_count: int = 0
    bad_count: int = 0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def update(self, outcome: str) -> None:
        """更新统计"""
        self.total_count += 1
        if outcome == "good":
            self.good_count += 1
        else:
            self.bad_count += 1
        self.success_rate = self.good_count / self.total_count if self.total_count > 0 else 0
        self.last_updated = datetime.now()


@dataclass
class SignalPerformance:
    """信号表现"""

    signal_type: str
    total_count: int = 0
    good_count: int = 0
    bad_count: int = 0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def update(self, outcome: str) -> None:
        """更新统计"""
        self.total_count += 1
        if outcome == "good":
            self.good_count += 1
        else:
            self.bad_count += 1
        self.success_rate = self.good_count / self.total_count if self.total_count > 0 else 0
        self.last_updated = datetime.now()


class FeedbackLearner:
    """从用户反馈中学习"""

    def __init__(self, data_path: Optional[Path] = None):
        """初始化反馈学习器

        Args:
            data_path: 数据存储路径，默认为 data/feedback.json
        """
        self.data_path = data_path or Path("data/feedback.json")
        self._records: list[FeedbackRecord] = []
        self._strategy_performance: dict[str, StrategyPerformance] = {}
        self._signal_performance: dict[str, SignalPerformance] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """确保数据已加载"""
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        """从文件加载数据"""
        if not self.data_path.exists():
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 加载记录
            for record_data in data.get("records", []):
                record = FeedbackRecord(
                    code=record_data["code"],
                    action=record_data["action"],
                    outcome=record_data["outcome"],
                    strategy=record_data.get("strategy"),
                    note=record_data.get("note"),
                    signals=record_data.get("signals"),
                    confidence=record_data.get("confidence"),
                    created_at=datetime.fromisoformat(record_data["created_at"])
                    if record_data.get("created_at") else datetime.now(),
                )
                self._records.append(record)

            # 加载策略表现
            for strategy, perf_data in data.get("strategy_performance", {}).items():
                self._strategy_performance[strategy] = StrategyPerformance(
                    strategy=strategy,
                    total_count=perf_data.get("total_count", 0),
                    good_count=perf_data.get("good_count", 0),
                    bad_count=perf_data.get("bad_count", 0),
                    success_rate=perf_data.get("success_rate", 0),
                    last_updated=datetime.fromisoformat(perf_data["last_updated"])
                    if perf_data.get("last_updated") else datetime.now(),
                )

            # 加载信号表现
            for signal, perf_data in data.get("signal_performance", {}).items():
                self._signal_performance[signal] = SignalPerformance(
                    signal_type=signal,
                    total_count=perf_data.get("total_count", 0),
                    good_count=perf_data.get("good_count", 0),
                    bad_count=perf_data.get("bad_count", 0),
                    success_rate=perf_data.get("success_rate", 0),
                    last_updated=datetime.fromisoformat(perf_data["last_updated"])
                    if perf_data.get("last_updated") else datetime.now(),
                )

        except Exception:
            pass

    def _save(self) -> None:
        """保存数据到文件"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "records": [
                {
                    "code": r.code,
                    "action": r.action,
                    "outcome": r.outcome,
                    "strategy": r.strategy,
                    "note": r.note,
                    "signals": r.signals,
                    "confidence": r.confidence,
                    "created_at": r.created_at.isoformat(),
                }
                for r in self._records
            ],
            "strategy_performance": {
                s: {
                    "total_count": p.total_count,
                    "good_count": p.good_count,
                    "bad_count": p.bad_count,
                    "success_rate": p.success_rate,
                    "last_updated": p.last_updated.isoformat(),
                }
                for s, p in self._strategy_performance.items()
            },
            "signal_performance": {
                s: {
                    "total_count": p.total_count,
                    "good_count": p.good_count,
                    "bad_count": p.bad_count,
                    "success_rate": p.success_rate,
                    "last_updated": p.last_updated.isoformat(),
                }
                for s, p in self._signal_performance.items()
            },
        }

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def record_feedback(
        self,
        code: str,
        action: str,
        outcome: str,
        strategy: Optional[str] = None,
        note: Optional[str] = None,
        signals: Optional[list[str]] = None,
        confidence: Optional[float] = None,
    ) -> FeedbackRecord:
        """记录反馈

        Args:
            code: 股票代码
            action: 建议动作
            outcome: 反馈结果
            strategy: 关联策略
            note: 补充说明
            signals: 关联信号
            confidence: 当时的置信度

        Returns:
            反馈记录
        """
        self._ensure_loaded()

        record = FeedbackRecord(
            code=code,
            action=action,
            outcome=outcome,
            strategy=strategy,
            note=note,
            signals=signals,
            confidence=confidence,
        )

        self._records.append(record)

        # 更新策略表现
        if strategy:
            if strategy not in self._strategy_performance:
                self._strategy_performance[strategy] = StrategyPerformance(strategy=strategy)
            self._strategy_performance[strategy].update(outcome)

        # 更新信号表现
        if signals:
            for signal in signals:
                if signal not in self._signal_performance:
                    self._signal_performance[signal] = SignalPerformance(signal_type=signal)
                self._signal_performance[signal].update(outcome)

        self._save()
        return record

    async def get_strategy_weights(self, user_id: str = "default") -> dict[str, float]:
        """获取策略权重

        根据历史反馈计算策略权重，用于调整分析置信度。

        Args:
            user_id: 用户 ID

        Returns:
            策略权重字典
        """
        self._ensure_loaded()

        weights = {}
        for strategy, perf in self._strategy_performance.items():
            if perf.total_count >= 3:  # 至少 3 次反馈才计算权重
                # 权重基于成功率，范围 0.5-1.5
                base_weight = 1.0
                adjustment = (perf.success_rate - 0.5) * 0.5  # -0.25 到 +0.25
                weights[strategy] = base_weight + adjustment
            else:
                weights[strategy] = 1.0

        return weights

    async def get_signal_accuracy(self, signal_type: str) -> Optional[float]:
        """获取信号准确率

        Args:
            signal_type: 信号类型

        Returns:
            准确率，如果没有数据则返回 None
        """
        self._ensure_loaded()

        perf = self._signal_performance.get(signal_type)
        if perf and perf.total_count > 0:
            return perf.success_rate
        return None

    async def adjust_confidence(
        self,
        base_confidence: float,
        signals: list[str],
        strategy: Optional[str] = None,
    ) -> float:
        """调整置信度

        根据历史反馈调整置信度。

        Args:
            base_confidence: 基础置信度
            signals: 信号列表
            strategy: 策略名称

        Returns:
            调整后的置信度
        """
        self._ensure_loaded()

        adjustment = 0.0

        # 根据信号准确率调整
        for signal in signals:
            accuracy = await self.get_signal_accuracy(signal)
            if accuracy is not None:
                # 准确率高于 50% 提升置信度，低于则降低
                adjustment += (accuracy - 0.5) * 0.1

        # 根据策略成功率调整
        if strategy:
            weights = await self.get_strategy_weights()
            strategy_weight = weights.get(strategy, 1.0)
            adjustment += (strategy_weight - 1.0) * 0.1

        # 应用调整，限制在 0-1 范围
        adjusted = base_confidence + adjustment
        return max(0.0, min(1.0, adjusted))

    async def get_feedback_summary(self, user_id: str = "default") -> dict[str, Any]:
        """获取反馈摘要

        Args:
            user_id: 用户 ID

        Returns:
            反馈摘要
        """
        self._ensure_loaded()

        total = len(self._records)
        if total == 0:
            return {
                "total": 0,
                "success_rate": None,
                "strategy_performance": {},
                "signal_performance": {},
            }

        good_count = sum(1 for r in self._records if r.outcome == "good")
        success_rate = good_count / total

        return {
            "total": total,
            "success_rate": round(success_rate, 2),
            "good_count": good_count,
            "bad_count": total - good_count,
            "strategy_performance": {
                s: {
                    "success_rate": round(p.success_rate, 2),
                    "total_count": p.total_count,
                }
                for s, p in self._strategy_performance.items()
                if p.total_count > 0
            },
            "signal_performance": {
                s: {
                    "success_rate": round(p.success_rate, 2),
                    "total_count": p.total_count,
                }
                for s, p in self._signal_performance.items()
                if p.total_count > 0
            },
        }