from pathlib import Path
import subprocess

from langchain_core.tools import tool


class TestRunnerError(Exception):
    pass


ALLOWED_COMMANDS = {
    "pytest",
}


@tool
def run_tests(
    workspace: str,
    command: str,
    timeout_seconds: int = 60,
) -> dict:
    """Run an allowed test command inside the workspace and capture its result."""

    workspace_path = Path(workspace).resolve()

    if not workspace_path.is_dir():
        raise TestRunnerError(
            f"Workspace does not exist: {workspace}"
        )

    command_parts = command.split()

    if not command_parts:
        raise TestRunnerError(
            "Test command cannot be empty."
        )

    executable = command_parts[0]

    if executable not in ALLOWED_COMMANDS:
        raise TestRunnerError(
            f"Command is not allowed: {executable}"
        )

    try:
        completed = subprocess.run(
            command_parts,
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        
    except subprocess.TimeoutExpired as error:
        return {
            "passed": False,
            "exit_code": -1,
            "stdout": error.stdout or "",
            "stderr": (
                error.stderr or ""
                if isinstance(error.stderr, str)
                else ""
            ),
            "error": "Test command timed out.",
        }

    return {
        "passed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "error": "",
    }