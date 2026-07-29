"""LaunchAgent plan tests; these never call macOS service-management commands."""

import json
import plistlib
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from astock.cli import app
from astock.scheduler.launchd import build_launch_agent_definition, write_launch_agent_plan


def test_launch_agent_plan_is_deterministic_and_not_installed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    output = tmp_path / "com.astock.scheduler.plist"

    result = write_launch_agent_plan(
        output,
        python_executable=Path(sys.executable),
        project_root=project_root,
    )

    with output.open("rb") as stream:
        payload = plistlib.load(stream)
    assert result["installed"] is False
    assert payload["Label"] == "com.astock.scheduler"
    assert payload["ProgramArguments"][-2:] == ["start", "--foreground"]
    assert payload["WorkingDirectory"] == str(project_root.resolve())
    assert "launchctl bootstrap" in result["install_command"]


def test_launch_agent_plan_rejects_invalid_label_or_python(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="label"):
        build_launch_agent_definition(
            python_executable=Path(sys.executable),
            project_root=tmp_path,
            label="not valid",
        )
    with pytest.raises(ValueError, match="Python executable"):
        build_launch_agent_definition(
            python_executable=tmp_path / "missing-python",
            project_root=tmp_path,
        )


def test_scheduler_launchd_plan_cli_generates_but_does_not_install(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    output = tmp_path / "agent.plist"

    result = CliRunner().invoke(
        app,
        [
            "scheduler",
            "launchd-plan",
            "--output",
            str(output),
            "--python-executable",
            sys.executable,
            "--project-root",
            str(project_root),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["installed"] is False
    assert output.exists()


def test_scheduler_launchd_plan_cli_uses_the_astock_root_by_default(tmp_path: Path) -> None:
    output = tmp_path / "agent.plist"

    result = CliRunner().invoke(
        app,
        [
            "scheduler",
            "launchd-plan",
            "--output",
            str(output),
            "--python-executable",
            sys.executable,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    expected_root = Path(__file__).resolve().parents[5]
    assert payload["definition"]["WorkingDirectory"] == str(expected_root)
    assert payload["definition"]["EnvironmentVariables"]["PYTHONPATH"] == str(
        expected_root / "src" / "python"
    )
