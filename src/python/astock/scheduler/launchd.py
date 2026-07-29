"""macOS LaunchAgent plan generation for the non-executing desk scheduler."""

from __future__ import annotations

import os
import plistlib
import re
from pathlib import Path
from typing import Any


DEFAULT_LAUNCHD_LABEL = "com.astock.scheduler"
_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def build_launch_agent_definition(
    *,
    python_executable: Path,
    project_root: Path,
    label: str = DEFAULT_LAUNCHD_LABEL,
    logs_directory: Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic LaunchAgent property list without installing it."""
    normalized_label = label.strip()
    if not _LABEL_PATTERN.fullmatch(normalized_label):
        raise ValueError("launchd label may contain only letters, numbers, dots, dashes, and underscores")

    python_path = python_executable.expanduser().resolve()
    root_path = project_root.expanduser().resolve()
    log_path = (logs_directory or root_path / "data" / "logs").expanduser().resolve()
    if not python_path.is_file():
        raise ValueError(f"Python executable does not exist: {python_path}")
    if not root_path.is_dir():
        raise ValueError(f"Project root does not exist: {root_path}")

    return {
        "Label": normalized_label,
        "ProgramArguments": [
            str(python_path),
            "-m",
            "astock.cli",
            "scheduler",
            "start",
            "--foreground",
        ],
        "WorkingDirectory": str(root_path),
        "EnvironmentVariables": {"PYTHONPATH": str(root_path / "src" / "python")},
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
        "ProcessType": "Background",
        "ThrottleInterval": 30,
        "StandardOutPath": str(log_path / "scheduler.launchd.stdout.log"),
        "StandardErrorPath": str(log_path / "scheduler.launchd.stderr.log"),
    }


def write_launch_agent_plan(
    output_path: Path,
    *,
    python_executable: Path,
    project_root: Path,
    label: str = DEFAULT_LAUNCHD_LABEL,
    logs_directory: Path | None = None,
) -> dict[str, Any]:
    """Write an auditable LaunchAgent plan; never run ``launchctl``."""
    definition = build_launch_agent_definition(
        python_executable=python_executable,
        project_root=project_root,
        label=label,
        logs_directory=logs_directory,
    )
    target = output_path.expanduser().resolve()
    if target.suffix != ".plist":
        raise ValueError("LaunchAgent plan output must use a .plist suffix")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as stream:
        plistlib.dump(definition, stream, sort_keys=True)

    uid = os.getuid()
    return {
        "success": True,
        "schema_version": "scheduler.launchd_plan.v1",
        "installed": False,
        "label": definition["Label"],
        "plist_path": str(target),
        "definition": definition,
        "install_command": f"launchctl bootstrap gui/{uid} {target}",
        "uninstall_command": f"launchctl bootout gui/{uid}/{definition['Label']}",
        "warning": "Plan generation does not install or start a system service.",
    }
