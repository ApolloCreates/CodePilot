from pathlib import Path
from langchain_core.tools import tool

DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "out",
    "dist",
    "build",
}

class WorkspaceError(Exception):
    """Raised when a filesystem operation violates the workspace boundary."""


def _safe_path(workspace: str, relative_path: str) -> Path:
    workspace_path = Path(workspace).resolve()
    requested_path = (workspace_path / relative_path).resolve()

    try:
        requested_path.relative_to(workspace_path)
    except ValueError as exc:
        raise WorkspaceError(
            f"Path is outside workspace: {relative_path}"
        ) from exc

    return requested_path

@tool
def list_files(workspace: str) -> list[str]:
    """List all files inside the specified workspace."""
    workspace_path = Path(workspace).resolve()

    if not workspace_path.is_dir():
        raise WorkspaceError(
            f"Workspace does not exist: {workspace}"
        )

    files = []

    for path in workspace_path.rglob("*"):
        if not path.is_file():
            continue

        if any(
            part in DEFAULT_IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        files.append(
            str(path.relative_to(workspace_path))
        )

    return sorted(files)


@tool
def read_file(
    workspace: str,
    relative_path: str,
    start_line: int = 1,
    max_lines: int = 200,
) -> str:
    """Read a bounded range of lines from a UTF-8 text file inside the workspace."""

    path = _safe_path(workspace, relative_path)

    if not path.is_file():
        raise WorkspaceError(
            f"File does not exist: {relative_path}"
        )

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    start_index = max(start_line - 1, 0)
    end_index = start_index + max_lines

    selected_lines = lines[start_index:end_index]

    return "\n".join(
        f"{start_index + index + 1}: {line}"
        for index, line in enumerate(selected_lines)
    )