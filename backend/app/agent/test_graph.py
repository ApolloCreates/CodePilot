from backend.app.agent.graph import graph


initial_state = {
    "bug_description": (
    "calculate_discount returns the wrong value when "
    "the discount percentage is 20"
),
    "workspace_path": "/home/apollo/Projects/codepilot",

    "diagnostics": [],

    "relevant_files": [],
    "repository_context": "",

    "diagnosis_supported": False,
    "diagnosis_evidence": [],

    "root_cause": "",
    "fix_plan": "",

    "proposed_changes": [],
    "modified_files": [],

    "validation_command": "",
    "validation_output": "",
    "errors": [],
    
    "validation_passed": False,

    "iteration_count": 0,
    "confidence": 0.0,
    "status": "started",
}


result = graph.invoke(initial_state)

print("\nFinal state:")
print(result)