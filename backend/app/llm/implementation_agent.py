from langchain_core.messages import HumanMessage, ToolMessage

from backend.app.llm.client import get_llm
from backend.app.tools.edit import edit_file


TOOLS = [
    edit_file,
]

TOOL_REGISTRY = {
    tool.name: tool
    for tool in TOOLS
}


def implement_changes(
    workspace: str,
    bug_description: str,
    root_cause: str,
    fix_plan: str,
    relevant_files: list[str],
    repository_context: str,
    max_rounds: int = 3,
) -> list[str]:
    """Use the LLM to implement a diagnosed fix safely."""

    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [
        HumanMessage(
            content=f"""
You are the implementation component of CodePilot.

You must implement the diagnosed bug fix.

Workspace:
{workspace}

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

- Only modify files listed in Relevant files.
- Do not modify tests unless explicitly required by the fix plan.
- Use the edit_file tool to make changes.
- Do not invent files.
- Do not use paths outside the workspace.
- Make the smallest change necessary.
- The edit_file tool requires an exact old_text and new_text.
- The old_text must match the source file exactly, including
  parameter names, type annotations, whitespace, and syntax.
- Read the existing code from the repository context provided in the task.
- If an edit_file call fails, inspect the exact error and correct
  the edit arguments.
- Do not repeat the same failed edit.
- Never invent source code.
- Stop once the required change has been successfully applied.
- Do not run tests yourself.
- Use the repository evidence as the source of truth for existing code.
- When constructing old_text, copy the existing code exactly.
- Preserve parameter names, type annotations, indentation, and syntax.
- Do not invent or rename identifiers.
- The old_text passed to edit_file must exactly match the repository source.
- If edit_file fails, inspect the error and correct the edit instead of repeating it.
"""
        )
    ]

    modified_files: list[str] = []

    for round_number in range(1, max_rounds + 1):

        print(
            f"\n--- Implementation Round {round_number} ---"
        )

        response = llm_with_tools.invoke(messages)

        messages.append(response)

        if not response.tool_calls:
            print("LLM returned without requesting an edit.")
            break

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            print(f"LLM requested: {tool_name}")
            print(f"Arguments: {tool_args}")

            tool = TOOL_REGISTRY.get(tool_name)

            if tool is None:
                raise ValueError(
                    f"Unknown implementation tool: {tool_name}"
                )

            try:
                result = tool.invoke(tool_args)

                tool_result = str(result)

                relative_path = tool_args.get(
                    "relative_path"
                )

                if (
                    relative_path
                    and relative_path not in modified_files
                ):
                    modified_files.append(relative_path)

            except Exception as error:
                tool_result = (
                    f"Tool execution failed: "
                    f"{type(error).__name__}: {error}"
                )

                print(f"Tool failed: {tool_result}")

            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call_id,
                )
            )

    return modified_files