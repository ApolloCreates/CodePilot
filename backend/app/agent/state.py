from typing import TypedDict


class DebugState(TypedDict):
    bug_description: str
    workspace_path: str

    diagnostics: list[str]

    relevant_files: list[str]
    repository_context: str

    diagnosis_supported: bool
    diagnosis_evidence: list[str]

    root_cause: str
    fix_plan: str

    proposed_changes: list[str]
    modified_files: list[str]

    validation_command: str
    validation_output: str
    errors: list[str]

    validation_passed: bool

    iteration_count: int
    confidence: float
    status: str