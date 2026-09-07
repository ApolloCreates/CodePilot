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
    return {
        "status": "received",
        "bug_description": request.bug_description,
        "workspace_path": request.workspace_path,
        "message": "CodePilot received the debugging request.",
    }