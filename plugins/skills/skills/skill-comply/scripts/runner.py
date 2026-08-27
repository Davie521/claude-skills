"""Run scenarios via claude -p and parse tool calls from stream-json output."""

from __future__ import annotations

import json
import logging
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from scripts.parser import ObservationEvent
from scripts.scenario_generator import Scenario

logger = logging.getLogger(__name__)

SANDBOX_BASE = Path("/tmp/skill-comply-sandbox")
ALLOWED_MODELS = frozenset({"haiku", "sonnet", "opus"})

# setup_commands come from an LLM (scenario_generator) — never execute them
# blindly. shlex + no shell already keeps pipes and redirection inert; the
# allowlist below closes what remains: bad command names, paths that reach
# outside the sandbox, and git subcommands that touch the network or global
# config.
SETUP_COMMAND_ALLOWLIST = frozenset(
    {"mkdir", "touch", "git", "cp", "mv", "ln", "cat", "echo", "printf", "tee"}
)
GIT_SAFE_SUBCOMMANDS = frozenset(
    {"init", "add", "commit", "status", "branch", "checkout", "switch", "tag", "config", "rm", "mv"}
)


class SandboxSetupError(RuntimeError):
    """Sandbox setup failed — the scenario must not run in a half-built sandbox."""


def _reject_setup_command(parts: list[str], sandbox_dir: Path) -> str | None:
    """Return the reason a generated setup command may not run, or None to allow it."""
    if not parts:
        return "empty command"
    if parts[0] not in SETUP_COMMAND_ALLOWLIST:
        return f"{parts[0]!r} is not an allowlisted setup command"
    if parts[0] == "git":
        sub = next((a for a in parts[1:] if not a.startswith("-")), "")
        if sub not in GIT_SAFE_SUBCOMMANDS:
            return f"git subcommand {sub!r} is not allowed during setup"
        if "--global" in parts or "--system" in parts:
            return "git --global/--system writes outside the sandbox"
    base = sandbox_dir.resolve()
    for arg in parts[1:]:
        if arg.startswith("-"):
            continue
        if ".." in Path(arg).parts:
            return f"path traversal in {arg!r}"
        if arg.startswith("/") and not Path(arg).resolve().is_relative_to(base):
            return f"absolute path outside sandbox: {arg!r}"
    return None


@dataclass(frozen=True)
class ScenarioRun:
    scenario: Scenario
    observations: tuple[ObservationEvent, ...]
    sandbox_dir: Path


def run_scenario(
    scenario: Scenario,
    model: str = "sonnet",
    max_turns: int = 30,
    timeout: int = 300,
) -> ScenarioRun:
    """Execute a scenario and extract tool calls from stream-json output."""
    if model not in ALLOWED_MODELS:
        raise ValueError(f"Unknown model: {model!r}. Allowed: {ALLOWED_MODELS}")

    sandbox_dir = _safe_sandbox_dir(scenario.id)
    _setup_sandbox(sandbox_dir, scenario)

    result = subprocess.run(
        [
            "claude", "-p", scenario.prompt,
            "--model", model,
            "--max-turns", str(max_turns),
            "--add-dir", str(sandbox_dir),
            "--allowedTools", "Read,Write,Edit,Bash,Glob,Grep",
            "--output-format", "stream-json",
            "--verbose",
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=sandbox_dir,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (rc={result.returncode}): {result.stderr[:500]}"
        )

    observations = _parse_stream_json(result.stdout)

    return ScenarioRun(
        scenario=scenario,
        observations=tuple(observations),
        sandbox_dir=sandbox_dir,
    )


def _safe_sandbox_dir(scenario_id: str) -> Path:
    """Sanitize scenario ID and ensure path stays within sandbox base."""
    safe_id = re.sub(r"[^a-zA-Z0-9\-_]", "_", scenario_id)
    path = SANDBOX_BASE / safe_id
    # Validate path stays within sandbox base (raises ValueError on traversal)
    path.resolve().relative_to(SANDBOX_BASE.resolve())
    return path


def _setup_sandbox(sandbox_dir: Path, scenario: Scenario) -> None:
    """Create sandbox directory and run setup commands."""
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)
    sandbox_dir.mkdir(parents=True)

    result = subprocess.run(["git", "init"], cwd=sandbox_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise SandboxSetupError(
            f"git init failed (rc={result.returncode}): {result.stderr.strip()[:500]}"
        )

    for cmd in scenario.setup_commands:
        parts = shlex.split(cmd)
        reason = _reject_setup_command(parts, sandbox_dir)
        if reason is not None:
            logger.warning("setup command blocked (%s): %s", reason, cmd)
            continue
        result = subprocess.run(parts, cwd=sandbox_dir, capture_output=True, text=True)
        if result.returncode != 0:
            raise SandboxSetupError(
                f"setup command failed (rc={result.returncode}): {cmd}\n"
                f"{result.stderr.strip()[:500]}"
            )


def _parse_stream_json(stdout: str) -> list[ObservationEvent]:
    """Parse claude -p stream-json output into ObservationEvents.

    Stream-json format:
    - type=assistant with content[].type=tool_use → tool call (name, input)
    - type=user with content[].type=tool_result → tool result (output)
    """
    events: list[ObservationEvent] = []
    pending: dict[str, dict] = {}
    event_counter = 0

    for line in stdout.strip().splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type = msg.get("type")

        if msg_type == "assistant":
            content = msg.get("message", {}).get("content", [])
            for block in content:
                if block.get("type") == "tool_use":
                    tool_use_id = block.get("id", "")
                    tool_input = block.get("input", {})
                    input_str = (
                        json.dumps(tool_input)[:5000]
                        if isinstance(tool_input, dict)
                        else str(tool_input)[:5000]
                    )
                    pending[tool_use_id] = {
                        "tool": block.get("name", "unknown"),
                        "input": input_str,
                        "order": event_counter,
                    }
                    event_counter += 1

        elif msg_type == "user":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    tool_use_id = block.get("tool_use_id", "")
                    if tool_use_id in pending:
                        info = pending.pop(tool_use_id)
                        output_content = block.get("content", "")
                        if isinstance(output_content, list):
                            output_str = json.dumps(output_content)[:5000]
                        else:
                            output_str = str(output_content)[:5000]

                        events.append(ObservationEvent(
                            timestamp=f"T{info['order']:04d}",
                            event="tool_complete",
                            tool=info["tool"],
                            session=msg.get("session_id", "unknown"),
                            input=info["input"],
                            output=output_str,
                        ))

    for _tool_use_id, info in pending.items():
        events.append(ObservationEvent(
            timestamp=f"T{info['order']:04d}",
            event="tool_complete",
            tool=info["tool"],
            session="unknown",
            input=info["input"],
            output="",
        ))

    return sorted(events, key=lambda e: e.timestamp)
