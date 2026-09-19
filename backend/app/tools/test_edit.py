from pathlib import Path

from backend.app.tools.edit import edit_file


workspace = "/home/apollo/Projects/codepilot"

test_file = Path(
    workspace,
    "backend/app/demo_target/edit_test.txt",
)

test_file.write_text(
    "hello world\n",
    encoding="utf-8",
)

result = edit_file.invoke({
    "workspace": workspace,
    "relative_path": "backend/app/demo_target/edit_test.txt",
    "old_text": "hello world",
    "new_text": "hello CodePilot",
})

print(result)

print(
    test_file.read_text(
        encoding="utf-8"
    )
)

try:
    edit_file.invoke({
        "workspace": workspace,
        "relative_path": "../../etc/passwd",
        "old_text": "root",
        "new_text": "hacked",
    })
except Exception as error:
    print(f"Blocked successfully: {error}")

test_file.unlink()