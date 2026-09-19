from langchain_core.messages import HumanMessage, ToolMessage

from backend.app.llm.client import get_llm
from backend.app.tools.filesystem import list_files, read_file
from backend.app.tools.search import search_code


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
    max_rounds: int = 8,
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
- Keep tool results focused.
- Start with search_code when you know a symbol, command, class, or function name.
- Read only the most relevant source files.
- Prefer source files over generated files such as extension/out.
- Do not inspect compiled or generated files when the corresponding source file is available.
- You may use multiple tools when necessary.
- Once you have enough evidence to answer the investigation task confidently, STOP using tools and provide your conclusion.
- Do not keep searching for additional confirmation once the relevant implementation has been established.
- Do not modify files.

Tool usage:
- Tool arguments must exactly match the provided tool schemas.
- For file paths, always provide paths relative to the workspace.
- Never include the workspace path inside relative_path.
- If a tool reports an error, use the error information to correct your next tool call.
"""
        )
    ]

    for round_number in range(1, max_rounds + 1):

        print(f"\n--- Investigation Round {round_number} ---")

        response = llm_with_tools.invoke(messages)

        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                print(
                    f"LLM requested: {tool_call['name']}"
                )
                print(
                    f"Arguments: {tool_call['args']}"
                )
        else:
            print("LLM returned a final response.")

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

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
                    f"Tool execution failed: {type(error).__name__}: {error}"
                )

            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call_id,
                )
            )

    return "Repository investigation stopped after reaching the tool-call limit."