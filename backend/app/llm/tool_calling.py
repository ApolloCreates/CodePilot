from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_groq import ChatGroq

from backend.app.tools.filesystem import list_files, read_file
from backend.app.tools.search import search_code


load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)


tools = [
    list_files,
    read_file,
    search_code,
]

tool_registry = {
    tool.name: tool
    for tool in tools
}


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)


workspace = "/home/apollo/Projects/codepilot"

messages = [
    HumanMessage(
        content=f"""
You are CodePilot, an AI debugging agent.

You are investigating this repository:

Workspace:
{workspace}

Task:
Find where the VS Code extension command
"CodePilot: Fix Bug" is implemented.

Use repository tools to investigate the code.
Do not guess.

Keep investigating until you have enough evidence
to answer the task confidently.
"""
    )
]


MAX_TOOL_ROUNDS = 5


for round_number in range(1, MAX_TOOL_ROUNDS + 1):

    print(f"\n========== Tool Round {round_number} ==========")

    response = llm_with_tools.invoke(messages)

    messages.append(response)

    if not response.tool_calls:
        print("\nFinal answer:")
        print(response.content)
        break

    for tool_call in response.tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        print(f"\nTool requested: {tool_name}")
        print(f"Arguments: {tool_args}")

        tool = tool_registry.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Unknown tool requested by LLM: {tool_name}"
            )

        tool_result = tool.invoke(tool_args)

        print("Tool executed successfully.")

        if isinstance(tool_result, list):
            print(f"Result items: {len(tool_result)}")
            print(f"Preview: {tool_result[:5]}")
        else:
            print(f"Result preview: {str(tool_result)[:1000]}")

        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call_id,
            )
        )

else:
    print(
        f"\nAgent stopped after {MAX_TOOL_ROUNDS} tool rounds."
    )