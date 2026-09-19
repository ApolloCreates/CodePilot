from langgraph.graph import END, START, StateGraph

from backend.app.agent.state import DebugState

from backend.app.llm.repository_agent import investigate_repository

from backend.app.llm.client import get_llm

from langchain_core.messages import HumanMessage

import json
import re

MAX_ITERATIONS = 3

def parse_json_response(content: str) -> dict:
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
        )
        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

    return json.loads(content)


def analyze_bug(state: DebugState):
    print("Analyzing bug...")

    return {
        "status": "analyzing",
    }


def explore_repository(state: DebugState):
    print("Exploring repository...")

    workspace = state["workspace_path"]
    bug_description = state["bug_description"]

    investigation = investigate_repository(
        workspace=workspace,
        task=(
            "Investigate the repository to understand the bug described below. "
            "Identify the most relevant files, functions, classes, or components "
            "related to the bug. Read the relevant source code and gather enough "
            "evidence for a later root-cause analysis.\n\n"
            f"Bug description:\n{bug_description}\n\n"
            "Do not modify any files. "
            "Do not attempt to fix the bug yet."
        ),
    )

    return {
        "status": "exploring",
        "repository_context": investigation,
    }

def diagnose_root_cause(state: DebugState):
    print("Diagnosing root cause...")

    llm = get_llm()

    bug_description = state["bug_description"]
    repository_context = state["repository_context"]

    prompt = f"""
You are the root-cause analysis component of CodePilot.

Analyze the reported bug using ONLY the repository investigation provided below.

Bug description:
{bug_description}

Repository investigation:
{repository_context}

Determine whether the reported bug is actually supported by the repository evidence.

Return ONLY valid JSON in exactly this structure:

{{
    "supported": true,
    "root_cause": "string",
    "evidence": [
        "string"
    ],
    "confidence": 0.0
}}

Rules:

- "supported" must be true only if the repository contains enough evidence
  that the reported bug corresponds to actual code.
- If the relevant functionality does not exist in the repository, set
  "supported" to false.
- If supported is false, root_cause should explain why the bug cannot be
  diagnosed from this repository.
- "evidence" must contain concrete evidence from the repository investigation.
- "confidence" must be a number between 0.0 and 1.0.
- Do not invent files, functions, code, or behavior.
- Do not propose a fix.
- Do not include markdown.
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        diagnosis = parse_json_response(response.content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM returned invalid diagnosis JSON: {response.content}"
        ) from error

    return {
        "status": "diagnosing",
        "diagnosis_supported": bool(
            diagnosis["supported"]
        ),
        "diagnosis_evidence": diagnosis["evidence"],
        "root_cause": diagnosis["root_cause"],
        "confidence": float(
            diagnosis["confidence"]
        ),
    }

def implement_fix(state: DebugState):
    print("Implementing fix...")

    return {
        "status": "implementing",
        "iteration_count": state["iteration_count"] + 1,
    }


def run_validation(state: DebugState):
    print("Running validation...")

    # Temporary simulation.
    # Real test execution will be implemented later.
    return {
        "status": "validating",
        "validation_command": "pytest",
        "validation_output": "Simulated failed test run",
        "validation_passed": False,  # Simulate a failed validation for testing purposes
    }


def verify_fix(state: DebugState):
    print("Verifying fix...")

    return {
        "status": "verified",
        "confidence": 1.0,
    }


def diagnose_failure(state: DebugState):
    print("Diagnosing validation failure...")

    return {
        "status": "diagnosing_failure",
        "errors": [
            state["validation_output"]
        ],
    }

def route_after_diagnosis(state: DebugState):
    if state["diagnosis_supported"]:
        return "create_fix_plan"

    return "stop_unsupported"

def create_fix_plan(state: DebugState):
    print("Creating fix plan...")

    llm = get_llm()

    prompt = f"""
You are the fix-planning component of CodePilot.

Create a precise implementation plan for the diagnosed bug.

Bug:
{state["bug_description"]}

Root cause:
{state["root_cause"]}

Evidence:
{state["diagnosis_evidence"]}

Repository context:
{state["repository_context"]}

Create a minimal fix plan.

Rules:
- Only plan changes supported by the evidence.
- Do not invent files or code.
- Prefer the smallest change that fixes the root cause.
- Do not modify tests unless the existing test is incorrect.
- Do not implement the fix.
- Do not execute commands.

Return ONLY valid JSON:

{{
    "plan": "string",
    "files_to_modify": [
        "relative/path/to/file"
    ],
    "changes": [
        "specific change to make"
    ]
}}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    try:
        plan = parse_json_response(response.content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM returned invalid fix plan JSON: {response.content}"
        ) from error

    return {
        "status": "planning",
        "fix_plan": plan["plan"],
        "proposed_changes": plan["changes"],
        "relevant_files": plan["files_to_modify"],
    }

def stop_unsupported(state: DebugState):
    print("Bug is not supported by the repository.")

    return {
        "status": "unsupported",
        "confidence": state["confidence"],
    }

def route_after_validation(state: DebugState):
    if state["validation_passed"]:
        return "verify_fix"

    if state["iteration_count"] >= MAX_ITERATIONS:
        return "max_iterations"

    return "diagnose_failure"


def stop_after_max_iterations(state: DebugState):
    print("Maximum iterations reached.")

    return {
        "status": "failed",
        "confidence": 0.0,
    }

builder = StateGraph(DebugState)

builder.add_node("analyze_bug", analyze_bug)
builder.add_node("explore_repository", explore_repository)
builder.add_node("diagnose_root_cause", diagnose_root_cause)
builder.add_node("implement_fix", implement_fix)
builder.add_node(
    "create_fix_plan",
    create_fix_plan,
)
builder.add_node("run_validation", run_validation)
builder.add_node("verify_fix", verify_fix)
builder.add_node("diagnose_failure", diagnose_failure)
builder.add_node(
    "stop_after_max_iterations",
    stop_after_max_iterations,
)
builder.add_node(
    "stop_unsupported",
    stop_unsupported,
)

builder.add_edge(START, "analyze_bug")
builder.add_edge("analyze_bug", "explore_repository")
builder.add_edge("explore_repository", "diagnose_root_cause")
builder.add_conditional_edges(
    "diagnose_root_cause",
    route_after_diagnosis,
    {
        "create_fix_plan": "create_fix_plan",
        "stop_unsupported": "stop_unsupported",
    },
)

builder.add_edge(
    "create_fix_plan",
    "implement_fix",
)
builder.add_edge(
    "stop_unsupported",
    END,
)
builder.add_edge("implement_fix", "run_validation")

builder.add_conditional_edges(
    "run_validation",
    route_after_validation,
    {
        "verify_fix": "verify_fix",
        "diagnose_failure": "diagnose_failure",
        "max_iterations": "stop_after_max_iterations",
    },
)

builder.add_edge("verify_fix", END)
builder.add_edge("diagnose_failure", "implement_fix")
builder.add_edge("stop_after_max_iterations", END)

graph = builder.compile()