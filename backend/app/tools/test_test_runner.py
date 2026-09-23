from backend.app.tools.test_runner import run_tests


workspace = "/home/apollo/Projects/codepilot"
try:
    run_tests.invoke({
        "workspace": workspace,
        "command": "rm -rf /",
    })
except Exception as error:
    print(f"Blocked successfully: {error}")
result = run_tests.invoke({
    "workspace": workspace,
    "command": "pytest backend/app/demo_target/test_calculator.py -k nonexistent",
})

print("Test result:")
print(result)