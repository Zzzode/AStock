#!/usr/bin/env python3
"""Independently audit whether the frozen C18 source batch is test-ready.

This is a read-focused source-feasibility audit.  It deliberately does not
import the C18 feasibility note, select a bond, calculate a result, infer a
person's access, or create an external action.  A PASS therefore means only
that the audit can verify the frozen files and its bounded observations; the
route can still be not_testable when required historical inputs are absent.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c18-official-sse-company-bond-feasibility-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r06_independent_c18_source_preflight_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r06_independent_c18_source_preflight_audit_20260815.md"

EXPECTED_MANIFEST_SHA256 = "0ef9a473ae98c5fafcb6f4cb92e8785ab5a2eb220f3c7c0ce41e42617872b908"
EXPECTED_SOURCE_KEYS = {
    "sse_company_bond_listing_rule",
    "sse_bond_investor_suitability_rule",
    "csrc_company_bond_administration_measure",
    "sse_company_bond_credit_risk_rule",
    "sse_bond_information_portal",
}
REQUIRED_MANIFEST_LIMITATIONS = (
    "historical bond master",
    "transaction tape",
    "full-price record",
    "coupon schedule",
    "rating history",
    "credit-event record",
    "broker route",
    "settlement evidence",
)


class _HTMLText(HTMLParser):
    """Collect visible and embedded text without adding a parser dependency."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object: {path}")
    return data


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _html_text(path: Path) -> str:
    parser = _HTMLText()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    return _normalise(" ".join(parser.parts))


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        raw = archive.read("word/document.xml")
    root = ET.fromstring(raw)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
        words = [node.text or "" for node in paragraph.iter(f"{namespace}t")]
        text = "".join(words).strip()
        if text:
            paragraphs.append(text)
    return _normalise(" ".join(paragraphs))


def _pdf_text(path: Path) -> str:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise RuntimeError("pdftotext is unavailable for independent PDF text inspection")
    completed = subprocess.run(
        [executable, "-enc", "UTF-8", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {completed.stderr.strip()}")
    return _normalise(completed.stdout)


def _all_terms_present(text: str, terms: tuple[str, ...]) -> tuple[bool, list[str]]:
    # PDF layout extraction can insert spaces inside Chinese phrases.  The
    # audit is checking terminology, not typography, so compare compact text.
    compact = re.sub(r"\s+", "", text)
    missing = [term for term in terms if term not in compact]
    return not missing, missing


def _write(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _collect_source_integrity(manifest: dict[str, Any], failures: list[str]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    records = manifest.get("records")
    if not isinstance(records, list):
        failures.append("manifest records are not a list")
        return {}, []

    source_by_key: dict[str, dict[str, Any]] = {}
    integrity_rows: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            failures.append("manifest contains a non-object record")
            continue
        key = str(record.get("source_key") or "")
        if not key:
            failures.append("manifest record lacks source_key")
            continue
        if key in source_by_key:
            failures.append(f"duplicate source_key: {key}")
            continue
        source_by_key[key] = record
        path = REPO_ROOT / str(record.get("path") or "")
        row: dict[str, Any] = {
            "source_key": key,
            "path": str(record.get("path") or ""),
            "expected_bytes": record.get("bytes"),
            "actual_bytes": None,
            "expected_sha256": record.get("sha256"),
            "actual_sha256": None,
            "status": "FAIL",
        }
        if not path.is_file():
            failures.append(f"missing raw source: {key}")
            integrity_rows.append(row)
            continue
        raw = path.read_bytes()
        row["actual_bytes"] = len(raw)
        row["actual_sha256"] = hashlib.sha256(raw).hexdigest()
        if row["actual_bytes"] != record.get("bytes"):
            failures.append(f"byte size mismatch: {key}")
        if row["actual_sha256"] != record.get("sha256"):
            failures.append(f"raw hash mismatch: {key}")
        if row["actual_bytes"] == record.get("bytes") and row["actual_sha256"] == record.get("sha256"):
            row["status"] = "PASS"
        integrity_rows.append(row)
    actual_keys = set(source_by_key)
    if actual_keys != EXPECTED_SOURCE_KEYS:
        failures.append("source-key set differs from the frozen C18 preflight")
    return source_by_key, integrity_rows


def _record_path(source_by_key: dict[str, dict[str, Any]], key: str) -> Path:
    return REPO_ROOT / str(source_by_key[key]["path"])


def _content_observations(source_by_key: dict[str, dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    required_keys = {
        "sse_bond_investor_suitability_rule",
        "csrc_company_bond_administration_measure",
        "sse_bond_information_portal",
        "sse_company_bond_listing_rule",
        "sse_company_bond_credit_risk_rule",
    }
    if not required_keys.issubset(source_by_key):
        failures.append("cannot inspect content because a required source record is absent")
        return {}

    suitability = _docx_text(_record_path(source_by_key, "sse_bond_investor_suitability_rule"))
    administration = _pdf_text(_record_path(source_by_key, "csrc_company_bond_administration_measure"))
    portal_path = _record_path(source_by_key, "sse_bond_information_portal")
    portal = _html_text(portal_path)
    listing_path = _record_path(source_by_key, "sse_company_bond_listing_rule")
    listing = _html_text(listing_path)
    credit_path = _record_path(source_by_key, "sse_company_bond_credit_risk_rule")
    credit = _html_text(credit_path)

    suitability_ok, suitability_missing = _all_terms_present(
        suitability,
        ("普通投资者", "专业投资者", "第九条", "证券经营机构", "交易权限"),
    )
    administration_ok, administration_missing = _all_terms_present(
        administration,
        ("普通投资者", "专业投资者", "投资者适当性管理", "信用评级", "登记结算"),
    )
    portal_ok, portal_missing = _all_terms_present(
        portal,
        ("债券简称", "最新成交价", "交易日期", "成交量"),
    )
    listing_ok, listing_missing = _all_terms_present(listing, ("公司债券上市规则", "详见附件"))
    credit_ok, credit_missing = _all_terms_present(credit, ("信用风险管理", "详见附件"))
    checks = {
        "suitability_rule_text": {"ok": suitability_ok, "missing_terms": suitability_missing},
        "administration_measure_text": {"ok": administration_ok, "missing_terms": administration_missing},
        "portal_snapshot_fields": {"ok": portal_ok, "missing_terms": portal_missing},
        "listing_rule_publication_page": {"ok": listing_ok, "missing_terms": listing_missing},
        "credit_risk_publication_page": {"ok": credit_ok, "missing_terms": credit_missing},
    }
    for name, check in checks.items():
        if not check["ok"]:
            failures.append(f"bounded text observation unavailable: {name}: {check['missing_terms']}")

    linked_rule_attachments = {
        "listing_rule_docx_links": re.findall(r"href=[\"']([^\"']+\.docx)[\"']", listing_path.read_text(encoding="utf-8", errors="replace"), flags=re.IGNORECASE),
        "credit_risk_rule_docx_links": re.findall(r"href=[\"']([^\"']+\.docx)[\"']", credit_path.read_text(encoding="utf-8", errors="replace"), flags=re.IGNORECASE),
    }
    captured_names = {Path(str(record.get("path") or "")).name for record in source_by_key.values()}
    linked_attachment_names = {
        Path(link).name
        for links in linked_rule_attachments.values()
        for link in links
    }
    missing_linked_attachments = sorted(name for name in linked_attachment_names if name not in captured_names)
    if not linked_attachment_names:
        failures.append("rule-publication pages no longer expose their linked document attachments")

    return {
        "extraction_methods": {
            "sse_bond_investor_suitability_rule": "DOCX word/document.xml",
            "csrc_company_bond_administration_measure": "PDF pdftotext UTF-8",
            "sse_bond_information_portal": "captured HTML text",
            "sse_company_bond_listing_rule": "captured HTML publication page",
            "sse_company_bond_credit_risk_rule": "captured HTML publication page",
        },
        "checks": checks,
        "bounded_findings": [
            {
                "finding": "适当性规则在规则层面区分普通投资者与专业投资者，并要求证券经营机构管理交易权限。",
                "source_keys": ["sse_bond_investor_suitability_rule", "csrc_company_bond_administration_measure"],
                "boundary": "这只证明存在分类和权限管理，不证明任何人对任何具体债券在任何日期具有资格或权限。",
            },
            {
                "finding": "适当性不是一个通用标签：债券类别、投资者分类、证券经营机构的权限管理和披露后调整都会影响可参与范围。",
                "source_keys": ["sse_bond_investor_suitability_rule", "csrc_company_bond_administration_measure"],
                "boundary": "本审计将其限定为逐债券、逐时点、逐投资者核验事项；本批次没有该类逐项记录。",
            },
            {
                "finding": "门户页包含债券简称、最新成交价、成交量和交易日期等页面字段。",
                "source_keys": ["sse_bond_information_portal"],
                "boundary": "单次门户页存档不是逐债券、跨历史区间的全价、成交和状态数据库。",
            },
            {
                "finding": "两份交易所规则来源在本批次中是公告页；页面指向的规则正文附件没有作为该批次的独立原始文件保存。",
                "source_keys": ["sse_company_bond_listing_rule", "sse_company_bond_credit_risk_rule"],
                "boundary": "因此不得把未入库附件中的细则当作本审计已经核验的逐债或历史数据。",
            },
        ],
        "linked_rule_attachment_control": {
            "linked_attachment_filenames": sorted(linked_attachment_names),
            "linked_attachment_files_captured_in_this_batch": [],
            "linked_attachment_files_not_captured_in_this_batch": missing_linked_attachments,
            "bounded_interpretation": "公告页与适当性办法可以支持规则层面边界；未保存的附件不能补足历史数据或逐债资格记录。",
        },
        "portal_capture": {
            "raw_path": _relative(portal_path),
            "one_captured_html_document": True,
            "page_field_labels_verified": ["债券简称", "最新成交价", "成交量", "交易日期"],
            "bounded_interpretation": "字段标签和一次页面存档不能替代历史可复算数据集。",
        },
    }


def _historical_input_matrix() -> list[dict[str, str | bool]]:
    """List only the inputs that would be required for a valid historical test."""

    return [
        {
            "input": "逐时点的上交所公开公司债总体与上市/终止状态",
            "captured_in_c18_batch": False,
            "reason": "五份存档中没有逐债券、逐日期的历史总体或状态表。",
        },
        {
            "input": "逐债券历史全价与应计口径",
            "captured_in_c18_batch": False,
            "reason": "门户页的一次字段展示不是历史全价序列；清单也明确排除 full-price record。",
        },
        {
            "input": "逐债券历史成交、成交量、无成交与停牌状态",
            "captured_in_c18_batch": False,
            "reason": "没有逐日交易明细或可复算的历史成交带。",
        },
        {
            "input": "票息条款、支付确认与到期/赎回事件账本",
            "captured_in_c18_batch": False,
            "reason": "没有募集说明书、条款表、支付确认或逐债券事件账本。",
        },
        {
            "input": "评级历史与逐债券信用事件时间线",
            "captured_in_c18_batch": False,
            "reason": "规则可说明信用风险治理，不是评级历史或信用事件记录。",
        },
        {
            "input": "日期明确的券商费用、交易单位、报价和成交处理规则",
            "captured_in_c18_batch": False,
            "reason": "没有券商费率文件、订单回执或逐时点成交处理证据。",
        },
        {
            "input": "逐债券、逐时点的登记结算与税费处理证据",
            "captured_in_c18_batch": False,
            "reason": "监管办法提及登记结算框架，但本批次没有按债券和日期可复算的结算数据。",
        },
        {
            "input": "逐债券、逐时点、逐投资者的适当性与权限状态",
            "captured_in_c18_batch": False,
            "reason": "规则说明分类和权限管理；本批次没有个人记录、账户权限或逐债资格历史。",
        },
    ]


def _audit() -> dict[str, Any]:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"missing frozen source manifest: {MANIFEST_PATH}")
    actual_manifest_sha256 = _sha256(MANIFEST_PATH)
    if actual_manifest_sha256 != EXPECTED_MANIFEST_SHA256:
        failures.append("frozen C18 manifest hash changed")
    manifest = _read_json(MANIFEST_PATH)
    if manifest.get("schema_version") != "c18_sse_company_bond_feasibility_source_manifest.v1":
        failures.append("unexpected C18 manifest schema version")
    source_by_key, integrity_rows = _collect_source_integrity(manifest, failures)
    limitations = " ".join(str(value) for value in manifest.get("limitations", []) if isinstance(value, str))
    missing_limitations = [phrase for phrase in REQUIRED_MANIFEST_LIMITATIONS if phrase not in limitations]
    if missing_limitations:
        failures.append(f"manifest limitation coverage changed: {missing_limitations}")
    content = _content_observations(source_by_key, failures)
    input_matrix = _historical_input_matrix()
    not_captured = [row["input"] for row in input_matrix if row["captured_in_c18_batch"] is False]

    return {
        "schema_version": "independent_c18_source_preflight_audit.v1",
        "artifact_id": "D5PT-R06-v1",
        "as_of": "2026-08-15",
        "review_mode": "read_focused_independent_source_feasibility_audit",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_control": {
            "manifest_path": _relative(MANIFEST_PATH),
            "expected_manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "actual_manifest_sha256": actual_manifest_sha256,
            "source_record_count": len(integrity_rows),
            "raw_file_integrity": integrity_rows,
            "all_raw_hashes_verified": bool(integrity_rows) and all(row["status"] == "PASS" for row in integrity_rows),
        },
        "bounded_source_findings": content,
        "historical_input_coverage": input_matrix,
        "route_assessment": {
            "route": "direct SSE-listed company-bond ladder",
            "route_status": "not_testable",
            "evidence_supports_bond_selection": False,
            "evidence_supports_historical_backtest": False,
            "evidence_supports_ordinary_investor_access_inference": False,
            "evidence_supports_performance_calculation": False,
            "evidence_supports_external_action": False,
            "reason": "规则与门户页快照没有提供逐债券、逐时点、可复算的总体、价格、成交、票息、兑付、评级、信用事件、费用和结算输入。",
            "not_captured_inputs": not_captured,
        },
        "allowed_use": [
            "记录规则层面的适当性、信用风险与信息入口边界。",
            "把适当性记录为逐债券、逐时点、逐投资者的后续核验要求。",
            "把缺失数据登记为历史测试的阻断项。",
        ],
        "not_allowed": [
            "从规则文本、债券名称、评级、上市状态或门户页单次字段推断任何人可买入。",
            "选择债券、形成直接债券梯、计算历史表现、推导收益或作出外部动作。",
            "将本审计的 PASS 解读为 C18 路线可测试、可使用或可产生任何回报。",
        ],
        "next_research_gate": "仅在获得逐债券、逐时点、具有数据权利且可独立复核的历史总体、全价、成交、现金流条款与事件、评级/信用事件、费用和结算数据后，才可另行冻结测试协议；该数据获取本身不构成选债或外部动作。",
    }


def _markdown(audit: dict[str, Any]) -> str:
    source_control = audit["source_control"]
    route = audit["route_assessment"]
    findings = audit.get("bounded_source_findings", {}).get("bounded_findings", [])
    input_rows = audit["historical_input_coverage"]
    lines = [
        "# R06 C18 公司债来源可行性独立审计",
        "",
        "## 审计结论",
        "",
        f"- 来源完整性审计：`{audit['result']}`。",
        f"- 直接上交所上市公司债梯路线：`{route['route_status']}`。",
        "- `PASS`只表示冻结清单及原始文件的完整性和本审计的有限观察通过；它不表示路线可测试、可使用或能产生任何回报。",
        "- 本审计只读、研究用途；未选择债券、未计算表现、未推断任何人的权限，也未形成外部动作。",
        "",
        "## 原始文件核验",
        "",
        f"- 冻结清单：`{source_control['manifest_path']}`。",
        f"- 清单 SHA-256：`{source_control['actual_manifest_sha256']}`（预期值匹配：`{source_control['actual_manifest_sha256'] == source_control['expected_manifest_sha256']}`）。",
        f"- 原始文件：{source_control['source_record_count']} 份，逐份字节数与 SHA-256 均已核验：`{source_control['all_raw_hashes_verified']}`。",
        "",
        "| source_key | 文件完整性 |",
        "|---|---|",
    ]
    for row in source_control["raw_file_integrity"]:
        lines.append(f"| `{row['source_key']}` | `{row['status']}` |")
    lines.extend(["", "## 有限规则观察", ""])
    for index, finding in enumerate(findings, start=1):
        lines.append(f"{index}. {finding['finding']}（来源：`{', '.join(finding['source_keys'])}`）")
        lines.append(f"   - 边界：{finding['boundary']}")
    lines.extend([
        "",
        "适当性必须按债券、时点和投资者分别核验。本批次没有逐债资格历史、任何账户权限记录或个人适当性材料，因此不能将规则类别误读为实际可交易性。",
        "",
        "## 历史测试输入覆盖",
        "",
        "| 所需输入 | 本批次是否捕获 | 审计理由 |",
        "|---|---:|---|",
    ])
    for row in input_rows:
        captured = "是" if row["captured_in_c18_batch"] else "否"
        lines.append(f"| {row['input']} | {captured} | {row['reason']} |")
    lines.extend([
        "",
        "## 结论边界",
        "",
        "这批一手规则和门户存档足以说明研究必须面对适当性、信用风险和信息入口边界；不足以建立历史母体、选择债券或进行直接公司债梯的回测。历史全价/成交、票息与到期兑付、评级与信用事件、券商费用及结算资料均未以逐债、逐时点、可复算形式捕获。",
        "",
        "因此 C18 当前正确状态是 `not_testable`。只有补齐受数据权利约束、可独立复核的历史输入后，才可以另行冻结测试协议；这并不预先承诺测试结果。",
        "",
        "## 不允许的推断",
        "",
    ])
    for item in audit["not_allowed"]:
        lines.append(f"- {item}")
    if audit["failures"]:
        lines.extend(["", "## 审计失败项", ""])
        for failure in audit["failures"]:
            lines.append(f"- {failure}")
    return "\n".join(lines) + "\n"


def main() -> int:
    audit = _audit()
    _write(OUTPUT_JSON, json.dumps(audit, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(audit))
    print(f"R06 INDEPENDENT C18 SOURCE PREFLIGHT AUDIT: {audit['result']}")
    print(f"- route_status: {audit['route_assessment']['route_status']}")
    for failure in audit["failures"]:
        print(f"- {failure}")
    return 0 if audit["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
