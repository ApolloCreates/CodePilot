from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="CodePilot Backend",
    version="0.1.0",
)


class DebugRequest(BaseModel):
    bug_description: str
    workspace_path: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "codepilot-backend",
    }

@app.post("/api/debug")
def debug(request: DebugRequest):
    from backend.app.agent.graph import graph

    initial_state = {
        "bug_description": request.bug_description,
        "workspace_path": request.workspace_path,
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
        "status": "",
        "proposed_file": "",
        "proposed_old_text": "",
        "proposed_new_text": "",
        "approval_status": "pending",
    }

    result = graph.invoke(initial_state)

    return {
        "status": result["status"],
        "bug_description": result["bug_description"],
        "root_cause": result["root_cause"],
        "fix_plan": result["fix_plan"],
        "proposed_file": result["proposed_file"],
        "proposed_old_text": result["proposed_old_text"],
        "proposed_new_text": result["proposed_new_text"],
        "approval_status": result["approval_status"],
        "confidence": result["confidence"],
    }