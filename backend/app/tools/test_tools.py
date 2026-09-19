from backend.app.tools.filesystem import (
    WorkspaceError,
    list_files,
    read_file,
)
from backend.app.tools.search import search_code


workspace = "/home/apollo/Projects/codepilot"


print("Files:")
for file in list_files.invoke({
    "workspace": workspace
})[:10]:
    print(f"  {file}")


print("\nReading package.json:")
print(read_file.invoke({
    "workspace": workspace,
    "relative_path": "extension/package.json"
})[:500])


print("\nSearching for 'CodePilot':")
for result in search_code.invoke({
    "workspace": workspace,
    "query": "CodePilot"
})[:10]:
    print(result)


print("\nTesting workspace boundary:")

try:
    read_file.invoke({
        "workspace": workspace,
        "relative_path": "../../etc/passwd"
    })
except WorkspaceError as error:
    print(f"Blocked successfully: {error}")