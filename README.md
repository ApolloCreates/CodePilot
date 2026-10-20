# CodePilot — AI-Powered Debugging Agent for VS Code

CodePilot is an AI-powered debugging assistant that investigates code repositories, identifies potential root causes, and proposes targeted code fixes directly within Visual Studio Code.

Unlike a conventional chat interface, CodePilot uses repository-aware tools and an agent workflow to gather code context before generating a proposed patch. Developers remain in control through an explicit review and approval process.

## Features

* **Repository investigation:** Search and read relevant source files to gather evidence.
* **Root-cause analysis:** Use an LLM-powered agent to diagnose reported bugs.
* **Targeted patch proposals:** Generate proposed code changes with old and new text.
* **Human approval:** Review, apply, or reject proposed changes.
* **IDE integration:** Interact with CodePilot through a VS Code extension.
* **Workspace-bounded file operations:** Restrict file modifications to the selected workspace.
* **Backend API:** Connect the extension to a FastAPI service.
* **Automated tests:** Verify patch application and rejection of unsafe or invalid changes.

## Architecture

```text
Developer
    |
    v
VS Code Extension (TypeScript)
    |
    v
FastAPI Backend (Python)
    |
    v
LangGraph Agent
    |
    +--> Repository Investigation Tools
    |
    +--> LLM-Based Diagnosis
    |
    +--> Proposed Code Change
              |
              v
       Human Review
          /     \
       Apply    Reject
```

## Technology Stack

* Python
* TypeScript
* Visual Studio Code Extension API
* FastAPI
* LangGraph
* LangChain
* Groq-hosted LLM
* pytest

## Current Workflow

1. Describe a bug in the VS Code extension.
2. CodePilot investigates relevant repository files.
3. The agent generates a root-cause explanation and proposed fix.
4. Review the proposed change.
5. Apply or reject the change.
6. Run the project's tests manually to verify the result.

**Note:** Test execution and post-fix verification are currently manual. Autonomous test-and-repair loops are not yet implemented.

## Development Setup

### Prerequisites

* Python 3.12+
* Node.js and npm
* Visual Studio Code
* A Groq API key

### Backend

From the repository root:

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

Create `backend/.env` and configure the required environment variable:

```text
GROQ_API_KEY=your_api_key_here
```

Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

The health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

### Extension

```bash
cd extension
npm install
npm run compile
```

Open the repository in VS Code and launch the extension development host using the project's debug configuration.

## Tests

From the repository root:

```bash
PYTHONPATH=. pytest -q
```

## Security and Privacy

CodePilot uses repository tools to inspect source code and may send relevant code context to the configured LLM provider. Avoid using it with confidential repositories unless you understand and approve the provider's data-handling terms.

Review all proposed changes before applying them. Never commit API keys or other credentials.

## Roadmap

* Stronger patch-safety and regression tests
* Better diagnosis and patch-quality evaluation
* Improved diagnostics integration
* Controlled test execution and verification
* Extension packaging and public distribution

## Status

CodePilot is an active development project. Features and APIs may change as reliability and safety improve.

## License

A license will be added before the public release.
