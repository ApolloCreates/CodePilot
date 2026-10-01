from langchain_core.messages import HumanMessage, ToolMessage

from backend.app.llm.client import get_llm
from backend.app.tools.filesystem import list_files, read_file
from backend.app.tools.search import search_code
from backend.app.tools.edit import edit_file


TOOLS = [
    list_files,
    read_file,
    search_code,
]


TOOL_REGISTRY = {
    tool.name: tool
    for tool in TOOLS
}


def investigate_repository(
    workspace: str,
    task: str,
    max_rounds: int = 4,
) -> str:
    """Use the LLM and repository tools to investigate a workspace."""

    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [
        HumanMessage(
            content=f"""
You are CodePilot, an AI debugging agent.

You are investigating this repository:

Workspace:
{workspace}

Investigation task:
{task}

Use the available repository tools to investigate the code.

Important rules:
- Do not guess.
- Use repository evidence.
- Start with search_code when you know a symbol, function, class, or command name.
- Read only the most relevant source files.
- Prefer source files over generated files.
- Do not inspect compiled or generated files when source is available.
- Once you have enough evidence, stop using tools and provide your conclusion.
- Do not modify files.

Tool usage:
- Tool arguments must exactly match the provided schemas.
- File paths must be relative to the workspace.
- Never include the workspace path inside relative_path.
"""
        )
    ]

    evidence = []

    for round_number in range(1, max_rounds + 1):

        print(f"\n--- Investigation Round {round_number} ---")

        # Prevent the conversation from growing indefinitely.
        if len(messages) > 7:
            messages = [
                messages[0],
                *messages[-6:],
            ]

        response = llm_with_tools.invoke(messages)

        messages.append(response)

        if not response.tool_calls:
            print("LLM returned a final response.")
            return response.content

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            print(f"LLM requested: {tool_name}")
            print(f"Arguments: {tool_args}")

            tool = TOOL_REGISTRY.get(tool_name)

            if tool is None:
                raise ValueError(
                    f"Unknown tool requested by LLM: {tool_name}"
                )

            try:
                result = tool.invoke(tool_args)
                tool_result = str(result)

            except Exception as error:
                tool_result = (
                    f"Tool execution failed: "
                    f"{type(error).__name__}: {error}"
                )

            # Keep a separate compact evidence record.
            evidence.append(
                f"""
Tool: {tool_name}
Arguments: {tool_args}
Result:
{tool_result}
"""
            )

            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call_id,
                )
            )

    # The exploration limit was reached.
    # Give the model one final opportunity to synthesize
    # the evidence already collected, without tools.

    evidence_text = "\n".join(evidence)

    final_prompt = f"""
You are completing a CodePilot repository investigation.

Investigation task:
{task}

Repository workspace:
{workspace}

The repository exploration phase has reached its maximum
number of tool-call rounds.

Do NOT request any more tools.

Use ONLY the repository evidence collected below.

Repository evidence:
{evidence_text}

Provide a concise investigation conclusion.

Include:

1. Relevant file paths
2. Relevant function or class names
3. The relevant implementation details
4. Evidence supporting the diagnosis

Do not guess.

If the evidence is insufficient, explicitly state what
information is missing.
"""

    final_response = llm.invoke(
        [HumanMessage(content=final_prompt)]
    )

    return final_response.content