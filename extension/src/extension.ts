import * as vscode from 'vscode';

interface DebugResponse {
    status: string;
    bug_description: string;
    workspace_path: string;
    message: string;
}

function parseDebugResponse(data: unknown): DebugResponse {
    if (
        typeof data === 'object' &&
        data !== null &&
        'status' in data &&
        'bug_description' in data &&
        'workspace_path' in data &&
        'message' in data &&
        typeof data.status === 'string' &&
        typeof data.bug_description === 'string' &&
        typeof data.workspace_path === 'string' &&
        typeof data.message === 'string'
    ) {
        return data as DebugResponse;
    }

    throw new Error('Invalid response from CodePilot backend');
}

export function activate(context: vscode.ExtensionContext) {
    const fixBugCommand = vscode.commands.registerCommand(
        'codepilot.fixBug',
        async () => {
            const bugDescription = await vscode.window.showInputBox({
                prompt: 'Describe the bug you want CodePilot to investigate',
                placeHolder: 'Example: Login crashes when password is empty'
            });

            if (!bugDescription) {
                return;
            }

            const workspaceFolder =
                vscode.workspace.workspaceFolders?.[0];

            if (!workspaceFolder) {
                vscode.window.showErrorMessage(
                    'CodePilot: No workspace is open.'
                );
                return;
            }

            try {
                const response = await fetch(
                    'http://127.0.0.1:8000/api/debug',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            bug_description: bugDescription,
                            workspace_path: workspaceFolder.uri.fsPath
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        `Backend returned ${response.status}`
                    );
                }

                const result = parseDebugResponse(await response.json());

                vscode.window.showInformationMessage(
                    `CodePilot: ${result.message}`
                );
            } catch (error) {
                vscode.window.showErrorMessage(
                    `CodePilot backend unavailable: ${error}`
                );
            }
        }
    );

    context.subscriptions.push(fixBugCommand);
}

export function deactivate() {}