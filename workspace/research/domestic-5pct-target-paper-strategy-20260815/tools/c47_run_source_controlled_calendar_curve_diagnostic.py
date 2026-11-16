#!/usr/bin/env python3
"""Run C46 after the C45 five-family source-control preflight.

The C44 implementation is reused only as deterministic calculation machinery.
C47 replaces its protocol, readiness dependency, and outputs before execution;
the void C44 artifact is never read as a result.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
C44_TOOL = CASE_DIR / "tools" / "c44_run_actual_contract_calendar_curve_diagnostic.py"
C45_PATH = CASE_DIR / "analysis" / "c45_five_family_actual_contract_source_readiness_20260815.json"
C46_PATH = CASE_DIR / "analysis" / "c46_actual_contract_calendar_curve_source_control_protocol_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c47_source_controlled_calendar_curve_diagnostic_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c47_source_controlled_calendar_curve_diagnostic_20260815.md"
EXPECTED_C45_SHA256 = "4b8b7cb02eed1ce92722199e080d7d6520c798270fb39e0f9ae1723fb153d36e"
EXPECTED_C46_SHA256 = "a36d715b12d70ef557bd4fc1bb2f2185d848e23b704cd760d208bd988ae52444"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_c44_engine() -> ModuleType:
    spec = importlib.util.spec_from_file_location("c44_calendar_curve_engine", C44_TOOL)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load C44 calculation engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _preflight() -> None:
    if _sha256(C45_PATH) != EXPECTED_C45_SHA256:
        raise ValueError("C45 source-readiness hash changed")
    if _sha256(C46_PATH) != EXPECTED_C46_SHA256:
        raise ValueError("C46 frozen protocol hash changed")
    readiness = json.loads(C45_PATH.read_text(encoding="utf-8"))
    protocol = json.loads(C46_PATH.read_text(encoding="utf-8"))
    if readiness.get("result") != "PASS" or readiness.get("research_only") is not True:
        raise ValueError("C45 is not a passing research-only source-readiness audit")
    if protocol.get("status") != "FROZEN_BEFORE_CALCULATION" or protocol.get("research_only") is not True:
        raise ValueError("C46 is not a frozen research-only protocol")
    amendment = protocol.get("source_control_amendment", {})
    if amendment.get("source_readiness_sha256") != EXPECTED_C45_SHA256 or amendment.get("source_readiness_result") != "PASS":
        raise ValueError("C46 does not bind C45")


def main() -> int:
    _preflight()
    engine = _load_c44_engine()
    engine.PROTOCOL_PATH = C46_PATH
    engine.READINESS_PATH = C45_PATH
    engine.OUTPUT_JSON = OUTPUT_JSON
    engine.OUTPUT_MD = OUTPUT_MD
    engine.EXPECTED_PROTOCOL_SHA256 = EXPECTED_C46_SHA256
    engine.EXPECTED_READINESS_SHA256 = EXPECTED_C45_SHA256
    result = engine._run()
    result["schema_version"] = "c47_source_controlled_calendar_curve_diagnostic.v1"
    result["artifact_id"] = "D5PT-C47-v1"
    result["source_control_preflight"] = {
        "C45_path": str(C45_PATH.relative_to(REPO_ROOT)),
        "C45_sha256": EXPECTED_C45_SHA256,
        "C45_result": "PASS",
        "C46_path": str(C46_PATH.relative_to(REPO_ROOT)),
        "C46_sha256": EXPECTED_C46_SHA256,
    }
    if str(result["status"]).startswith("NOT_DECIDABLE"):
        markdown = "\n".join(
            [
                "# C47 实际合约期限结构诊断",
                "",
                f"- 状态：`{result['status']}`；`portfolio_q=0`；当前动作：`NO_ACTION`。",
                "- 结论：在 C46 冻结的五家族、期限窗口、同合约历史、成交量与持仓量条件下，暖机完成后出现月度配对不完整，因而不能生成连续的毛额结算价诊断。",
                f"- 暖机完成信号日：{result.get('warmup_complete_signal_date')}；停止信号日：{result.get('incomplete_signal', {}).get('signal_date')}。",
                "- 处置：不得替换品种、放松阈值、沿用旧配对、填补数据或假定成交；本路线不产生表现结论或外部操作。",
                "",
                "停止时各家族的配对状态：",
                "",
                "| 家族 | 状态 | 合格近期候选 | 合格远期候选 |",
                "|---|---|---:|---:|",
            ]
            + [
                f"| {family} | `{selection.get('status')}` | {selection.get('near_candidate_count', 'n/a')} | {selection.get('deferred_candidate_count', 'n/a')} |"
                for family, selection in result.get("incomplete_signal", {}).get("families", {}).items()
            ]
            + [
                "",
                "该结论仅说明冻结的实际合约研究条件没有形成连续可计算配对；它不等同于任何个人成交、净结果或未来表现，也不授权任何期货、证券或其他外部动作。",
                "",
            ]
        )
    else:
        markdown = engine._render_markdown(result).replace("# C44", "# C47").replace("依据 C43 冻结规则", "依据 C46 冻结规则")
    engine._write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    engine._write(OUTPUT_MD, markdown)
    print(f"{result['status']}: {OUTPUT_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
