"""Tests for runner sandbox guard rails — allowlist, path escape, fail-loud setup."""

from pathlib import Path

import pytest

from scripts.runner import SandboxSetupError, _reject_setup_command, _setup_sandbox
from scripts.scenario_generator import Scenario


def _scenario(setup_commands: tuple[str, ...]) -> Scenario:
    return Scenario(
        id="runner-guard-test",
        level=1,
        level_name="supportive",
        description="guard-rail test scenario",
        prompt="unused",
        setup_commands=setup_commands,
    )


class TestRejectSetupCommand:
    def test_allows_relative_file_commands(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["mkdir", "-p", "src/tests"], tmp_path) is None
        assert _reject_setup_command(["touch", "src/a.py"], tmp_path) is None

    def test_allows_absolute_path_inside_sandbox(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["mkdir", "-p", str(tmp_path / "src")], tmp_path) is None

    def test_blocks_commands_outside_allowlist(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["curl", "http://example.com"], tmp_path) is not None
        assert _reject_setup_command(["rm", "-rf", "src"], tmp_path) is not None
        assert _reject_setup_command(["sh", "-c", "echo hi"], tmp_path) is not None

    def test_blocks_absolute_path_outside_sandbox(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["touch", "/etc/evil"], tmp_path) is not None

    def test_blocks_path_traversal(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["touch", "../escape.txt"], tmp_path) is not None

    def test_git_subcommands_are_filtered(self, tmp_path: Path) -> None:
        assert _reject_setup_command(["git", "add", "."], tmp_path) is None
        assert _reject_setup_command(["git", "clone", "https://example.com/x.git"], tmp_path) is not None
        assert _reject_setup_command(["git", "config", "--global", "user.email", "x@y"], tmp_path) is not None


class TestSetupSandbox:
    def test_runs_allowed_commands(self, tmp_path: Path) -> None:
        sandbox = tmp_path / "sb"
        _setup_sandbox(sandbox, _scenario(("mkdir -p src", "touch src/a.py")))
        assert (sandbox / "src" / "a.py").exists()

    def test_blocked_command_is_skipped_but_run_continues(self, tmp_path: Path) -> None:
        sandbox = tmp_path / "sb"
        _setup_sandbox(sandbox, _scenario(("curl http://example.com", "touch ok.txt")))
        assert (sandbox / "ok.txt").exists()

    def test_failed_command_raises(self, tmp_path: Path) -> None:
        sandbox = tmp_path / "sb"
        with pytest.raises(SandboxSetupError, match="setup command failed"):
            _setup_sandbox(sandbox, _scenario(("cp does-not-exist.txt dest.txt",)))
