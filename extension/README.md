# CodePilot

CodePilot is an AI-powered debugging agent for Visual Studio Code. It investigates reported bugs, analyzes relevant workspace files, and proposes code changes for developer review.

## Features

- Repository-aware code investigation
- AI-powered root-cause analysis
- Targeted code-fix proposals
- Review, apply, or reject proposed changes
- Workspace-bounded file modifications

## Requirements

- Visual Studio Code 1.135.0 or later
- Python 3.12+
- Node.js and npm
- A Groq API key
- The CodePilot Python backend running locally

## Getting Started

1. Clone the [CodePilot repository](https://github.com/ApolloCreates/CodePilot).
2. Follow the backend setup and API-key configuration instructions in the main repository README.
3. Start the backend at `http://127.0.0.1:8000`.
4. Install the CodePilot VSIX extension in VS Code.
5. Open the project you want to debug.
6. Run **CodePilot: Fix Bug** from the Command Palette and describe the problem.
7. Review the proposed fix before applying it.

## Important Notes

- The backend must be running for the extension to work.
- Relevant code context may be sent to the configured LLM provider.
- Review proposed changes and run your tests before relying on a fix.
- CodePilot is an active development project; some behavior may change.

## License

See the repository for license information.
