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

@tool
def search_code(
    workspace: str,
    query: str,
    max_results: int = 20,
) -> list[dict[str, str | int]]:
    """Search source files inside the workspace for a text query.

    Returns at most max_results matching lines.
    """

    workspace_path = Path(workspace).resolve()

    if not workspace_path.is_dir():
        raise ValueError(
            f"Workspace does not exist: {workspace}"
        )

    results = []

    for path in workspace_path.rglob("*"):
        if not path.is_file():
            continue

        if any(
            part in DEFAULT_IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            if query.lower() in line.lower():
                results.append(
                    {
                        "file": str(
                            path.relative_to(workspace_path)
                        ),
                        "line": line_number,
                        "content": line.strip(),
                    }
                )

                if len(results) >= max_results:
                    return results

    return results