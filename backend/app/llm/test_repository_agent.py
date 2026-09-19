from backend.app.llm.repository_agent import investigate_repository


workspace = "/home/apollo/Projects/codepilot"

result = investigate_repository(
    workspace=workspace,
    task=(
        "Locate the implementation of the VS Code command "
        "'CodePilot: Fix Bug'. "
        "Once you have identified the source file and understand "
        "how the command is registered, provide the answer. "
        "Do not investigate unrelated backend files."
    ),
)

print("\nRepository investigation result:")
print(result)