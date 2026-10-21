
import json
import re
from pathlib import Path

from langchain_core.messages import HumanMessage

from backend.app.llm.client import get_llm


def parse_json_response(content: str) -> dict:
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    return json.loads(content)


def generate_proposed_change(
    workspace: str,
    bug_description: str,
    root_cause: str,
    fix_plan: str,
    relevant_files: list[str],
    repository_context: str,
) -> dict:
    llm = get_llm()

    prompt = f"""
You are the implementation planning component of CodePilot.

Generate the exact code change required to fix the diagnosed bug.

Bug:
{bug_description}

Root cause:
{root_cause}

Fix plan:
{fix_plan}

Relevant files:
{relevant_files}

Repository evidence:
{repository_context}

Rules:
- Do not modify files or execute commands.
- Use repository evidence as the source of truth.
- The file must be one of the relevant files.
- old_text must exactly match existing source code.
- Preserve indentation, whitespace, and unrelated code.
- Make the smallest possible change.
- Do not invent source code or modify tests.
- Identify and fix the root cause in the most appropriate source file.
- Prefer fixing the module responsible for the incorrect behavior instead of adding a workaround in its caller.
- Use the repository evidence and call relationships to determine where the bug originates.
- Do not hardcode a correction in a caller if the underlying function is responsible for the incorrect result.
- Keep the change minimal and preserve unrelated behavior.
- Do not modify tests to make them pass.
- Before choosing a file, trace the relevant function calls using the repository evidence.
- Select the file that owns the incorrect behavior, not merely a file that calls it.
- For this bug, inspect whether calculate_total() itself omits the service fee before considering changes to create_order().
- Do not add a workaround in a caller when the underlying function is responsible for the incorrect result.
- The proposed change must be consistent with the stated root cause and fix plan.
- If the evidence does not establish which file should change, do not invent a fix.

Return ONLY valid JSON:
{{
    "file": "relative/path/to/file",
    "old_text": "exact existing source text",
    "new_text": "replacement source text"
}}
"""
    
    root = Path(workspace).resolve()
    relevant_set = set(relevant_files)

    for attempt in range(2):
        response = llm.invoke([HumanMessage(content=prompt)])

        try:
            proposal = parse_json_response(response.content)
        except json.JSONDecodeError as error:
            if attempt == 0:
                prompt += "\nReturn valid JSON only, without Markdown fences."
                continue
            raise ValueError(
                "LLM returned invalid proposed-edit JSON."
            ) from error

        required = {"file", "old_text", "new_text"}
        if not isinstance(proposal, dict) or not required.issubset(proposal):
            if attempt == 0:
                prompt += "\nReturn JSON containing file, old_text, and new_text."
                continue
            raise ValueError(
                "Proposal must contain file, old_text, and new_text."
            )

        relative_path = proposal["file"]
        old_text = proposal["old_text"]
        new_text = proposal["new_text"]

        if not all(
            isinstance(value, str) and value
            for value in (relative_path, old_text, new_text)
        ):
            raise ValueError("Proposal contains missing or empty text fields.")

        if relative_path not in relevant_set:
            raise ValueError(
                "Proposed file is not in the relevant-files list."
            )

        target = (root / relative_path).resolve()

        try:
            target.relative_to(root)
        except ValueError as error:
            raise ValueError(
                "Proposed file is outside the workspace."
            ) from error

        if not target.is_file():
            raise ValueError(
                f"Proposed file does not exist: {relative_path}"
            )

        current_text = target.read_text(encoding="utf-8")
        occurrences = current_text.count(old_text)

        if occurrences == 1:
            return proposal

        if attempt == 0:
            prompt += f"""

The previous proposal was invalid: old_text matched {occurrences}
times in {relative_path}.

Use a verbatim substring from the exact current file below.
Preserve indentation and whitespace.

<FILE path="{relative_path}">
{current_text}
</FILE>

Generate a corrected, minimal patch. Do not modify files or tests.
Return only valid JSON with file, old_text, and new_text.
"""
            continue

        raise ValueError(
            f"Could not generate a valid patch for {relative_path}: "
            f"old_text matched {occurrences} times after retry."
        )

    raise ValueError("Could not generate a valid patch.")

