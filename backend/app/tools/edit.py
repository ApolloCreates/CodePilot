from pathlib import Path

from langchain_core.tools import tool


class WorkspaceError(Exception):
    pass


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
def edit_file(
    workspace: str,
    relative_path: str,
    old_text: str,
    new_text: str,
) -> str:
    """Replace an exact piece of text in a UTF-8 text file inside the workspace."""

    path = _safe_path(workspace, relative_path)

    if not path.is_file():
        raise WorkspaceError(
            f"File does not exist: {relative_path}"
        )

    content = path.read_text(encoding="utf-8")

    occurrences = content.count(old_text)

    if occurrences == 0:
        raise WorkspaceError(
            f"Target text was not found in {relative_path}"
        )

    if occurrences > 1:
        raise WorkspaceError(
            f"Target text occurs {occurrences} times in {relative_path}; "
            "refusing ambiguous edit."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1,
    )

    path.write_text(
        updated_content,
        encoding="utf-8",
    )

    return (
        f"Successfully modified {relative_path}. "
        "Exactly one occurrence was replaced."
    )