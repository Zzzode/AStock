#!/usr/bin/env python3
"""Verify local source-manifest paths, byte sizes and SHA-256 digests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]


def main() -> int:
    failures: list[str] = []
    checked = 0
    for manifest_path in sorted(CASE_DIR.glob("sources/*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("source_quality") == "metadata_only_failed_probe":
            if manifest.get("files"):
                failures.append(f"metadata-only probe retains files: {manifest_path}")
            for attempt in manifest.get("attempts", []):
                required_attempt_fields = {
                    "probe_id", "family", "authority", "attempted_at", "url", "http_status",
                    "response_classification", "response_body_retained", "use_boundary",
                }
                missing = sorted(required_attempt_fields.difference(attempt))
                if missing:
                    failures.append(f"metadata-only probe fields missing {missing}: {manifest_path}")
                if attempt.get("response_body_retained") is not False:
                    failures.append(f"metadata-only probe retained body: {manifest_path}")
        freeze = manifest.get("source_freeze")
        if freeze is not None:
            required_freeze = {"schema_version", "sealed_at", "frozen_files", "runtime_provenance"}
            missing_freeze = sorted(required_freeze.difference(freeze))
            if missing_freeze:
                failures.append(f"source-freeze fields missing {missing_freeze}: {manifest_path}")
            frozen_files = freeze.get("frozen_files", [])
            manifest_files = manifest.get("files", [])
            frozen_by_path = {entry.get("path"): entry for entry in frozen_files}
            manifest_by_path = {entry.get("path"): entry for entry in manifest_files}
            if set(frozen_by_path) != set(manifest_by_path):
                failures.append(f"source-freeze path set differs from manifest files: {manifest_path}")
            for path_key in sorted(set(frozen_by_path).intersection(manifest_by_path)):
                frozen_entry = frozen_by_path[path_key]
                manifest_entry = manifest_by_path[path_key]
                if {
                    key: frozen_entry.get(key) for key in ("path", "bytes", "sha256")
                } != {
                    key: manifest_entry.get(key) for key in ("path", "bytes", "sha256")
                }:
                    failures.append(f"source-freeze record differs from manifest file: {manifest_path} {path_key}")
        for entry in manifest.get("files", []):
            if manifest.get("source_quality") == "vendor_documentation":
                required_vendor_fields = {
                    "path", "local_path", "publisher", "title", "url", "document_effective_date",
                    "retrieval_date", "use_boundary", "bytes", "sha256",
                }
                missing = sorted(required_vendor_fields.difference(entry))
                if missing:
                    failures.append(f"vendor manifest fields missing {missing}: {manifest_path}")
                if entry.get("local_path") != entry.get("path"):
                    failures.append(f"vendor local_path mismatch: {manifest_path}")
            path = (REPO_ROOT / entry["path"]).resolve()
            checked += 1
            if not path.is_file():
                failures.append(f"missing: {path}")
                continue
            actual_size = path.stat().st_size
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_size != entry.get("bytes"):
                failures.append(f"size: {path} manifest={entry.get('bytes')} actual={actual_size}")
            if actual_hash != entry.get("sha256"):
                failures.append(f"sha256: {path}")
            if "official-" in str(path.parent) and path.suffix.lower() in {".html", ".htm"}:
                head = path.read_text(encoding="utf-8", errors="ignore")[:1000].lower()
                if "<title>web 应用防火墙" in head or "safeline_bot_challenge" in head:
                    failures.append(f"waf challenge captured as official source: {path}")
        for entry in manifest.get("dependencies", []):
            required_dependency_fields = {
                "path", "bytes", "sha256", "dependency_role", "source_quality", "purpose", "limitations"
            }
            missing_dependency = sorted(required_dependency_fields.difference(entry))
            if missing_dependency:
                failures.append(f"dependency fields missing {missing_dependency}: {manifest_path}")
            path = (REPO_ROOT / entry.get("path", "")).resolve()
            checked += 1
            if not path.is_file():
                failures.append(f"missing dependency: {path}")
                continue
            actual_size = path.stat().st_size
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_size != entry.get("bytes"):
                failures.append(f"dependency size: {path} manifest={entry.get('bytes')} actual={actual_size}")
            if actual_hash != entry.get("sha256"):
                failures.append(f"dependency sha256: {path}")
    source_registry_path = CASE_DIR / "data" / "source_registry.json"
    if source_registry_path.is_file():
        registry = json.loads(source_registry_path.read_text(encoding="utf-8"))
        for source in registry:
            if "sealed_manifest_sha256" not in source:
                continue
            manifest_relative = source.get("sealed_manifest_path")
            if not isinstance(manifest_relative, str):
                failures.append(f"source registry seal path missing: {source.get('source_id')}")
                continue
            path = (REPO_ROOT / manifest_relative).resolve()
            if not path.is_file():
                failures.append(f"source registry seal manifest missing: {path}")
                continue
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_hash != source.get("sealed_manifest_sha256"):
                failures.append(f"source registry seal manifest SHA-256 differs: {path}")
            manifest = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(manifest.get("source_freeze"), dict):
                failures.append(f"source registry seal manifest has no source_freeze: {path}")
    if failures:
        print("SOURCE MANIFEST: FAIL")
        print("\n".join(failures))
        return 1
    print(f"SOURCE MANIFEST: PASS ({checked} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
