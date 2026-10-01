import json
import re

from langchain_core.messages import HumanMessage

from backend.app.llm.client import get_llm


def parse_json_response(content: str) -> dict:
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
        )
        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

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

- Do not modify any files.
- Do not execute commands.
- Use the repository evidence as the source of truth.
- The file must be one of the relevant files.
- old_text must exactly match existing source code.
- Preserve parameter names, type annotations, indentation,
  whitespace, and unrelated code.
- Make the smallest possible change.
- Do not invent source code.
- Do not modify tests.

Return ONLY valid JSON:

{{
    "file": "relative/path/to/file",
    "old_text": "exact existing source text",
    "new_text": "replacement source text"
}}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        return parse_json_response(response.content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM returned invalid proposed edit: "
            f"{response.content}"
        ) from error