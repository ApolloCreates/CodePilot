import * as vscode from 'vscode';
import * as path from 'path';

interface DebugResponse {
    status: string;
    bug_description: string;
    root_cause: string;
    workspace_path: string;
    fix_plan: string;
    proposed_file: string;
    proposed_old_text: string;
    proposed_new_text: string;
    approval_status: string;
    confidence: number;
}

function parseDebugResponse(data: unknown): DebugResponse {
    if (
        typeof data === 'object' &&
        data !== null &&
        'status' in data &&
        'bug_description' in data &&
        'root_cause' in data &&
        'fix_plan' in data &&
        'proposed_file' in data &&
        'proposed_old_text' in data &&
        'proposed_new_text' in data &&
        'approval_status' in data &&
        'confidence' in data &&
        typeof data.status === 'string' &&
        typeof data.bug_description === 'string' &&
        typeof data.root_cause === 'string' &&
        typeof data.fix_plan === 'string' &&
        typeof data.proposed_file === 'string' &&
        typeof data.proposed_old_text === 'string' &&
        typeof data.proposed_new_text === 'string' &&
        typeof data.approval_status === 'string' &&
        typeof data.confidence === 'number'
    ) {
        return data as DebugResponse;
    }

    throw new Error('Invalid response from CodePilot backend');
}

function escapeHtml(value: string): string {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function showResultPanel(
    context: vscode.ExtensionContext,
    result: DebugResponse
) {
    const panel = vscode.window.createWebviewPanel(
        'codepilotResult',
        'CodePilot',
        vscode.ViewColumn.Beside,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    const oldText = escapeHtml(result.proposed_old_text);
    const newText = escapeHtml(result.proposed_new_text);

    panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background: var(--vscode-editor-background);
                    padding: 24px;
                    line-height: 1.5;
                }

                h1 {
                    font-size: 24px;
                    margin-bottom: 8px;
                }

                .status {
                    color: var(--vscode-testing-iconPassed);
                    margin-bottom: 24px;
                }

                .section {
                    margin-top: 24px;
                }

                .section-title {
                    font-size: 13px;
                    font-weight: bold;
                    text-transform: uppercase;
                    opacity: 0.7;
                    margin-bottom: 8px;
                }

                .card {
                    background: var(--vscode-textCodeBlock-background);
                    border-radius: 6px;
                    padding: 14px;
                }

                pre {
                    white-space: pre-wrap;
                    overflow-x: auto;
                    margin: 0;
                }

                .old {
                    border-left: 3px solid var(--vscode-testing-iconFailed);
                    padding-left: 12px;
                }

                .new {
                    border-left: 3px solid var(--vscode-testing-iconPassed);
                    padding-left: 12px;
                    margin-top: 12px;
                }

                .file {
                    font-family: var(--vscode-editor-font-family);
                    margin-bottom: 12px;
                }

                .buttons {
                    display: flex;
                    gap: 10px;
                    margin-top: 28px;
                }

                button {
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    cursor: pointer;
                    color: var(--vscode-button-foreground);
                    background: var(--vscode-button-background);
                }

                button:hover {
                    background: var(--vscode-button-hoverBackground);
                }

                .reject {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
            </style>
        </head>

        <body>
            <h1>CodePilot</h1>

            <div class="status">
                ✓ Fix proposed
            </div>

            <div class="section">
                <div class="section-title">Root Cause</div>

                <div class="card">
                    ${escapeHtml(result.root_cause)}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Fix Plan</div>

                <div class="card">
                    ${escapeHtml(result.fix_plan)}
                </div>
            </div>

            <div class="section">
                <div class="section-title">File</div>

                <div class="file">
                    ${escapeHtml(result.proposed_file)}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Proposed Change</div>

                <div class="card">
                    <div class="old">
                        <pre>- ${oldText}</pre>
                    </div>

                    <div class="new">
                        <pre>+ ${newText}</pre>
                    </div>
                </div>
            </div>

            <div class="buttons">
                <button id="apply">
                    Apply Fix
                </button>

                <button id="reject" class="reject">
                    Reject
                </button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                document
                    .getElementById('apply')
                    .addEventListener('click', () => {
                        vscode.postMessage({
                            command: 'apply'
                        });
                    });

                document
                    .getElementById('reject')
                    .addEventListener('click', () => {
                        vscode.postMessage({
                            command: 'reject'
                        });
                    });
            </script>
        </body>
        </html>
    `;

    panel.webview.onDidReceiveMessage(
        async message => {
            if (message.command === 'reject') {
                vscode.window.showInformationMessage(
                    'CodePilot: Proposed fix rejected.'
                );

                panel.dispose();
            }

            if (message.command === 'apply') {
                try {
                    const response = await fetch(
                        'http://127.0.0.1:8000/api/apply',
                        {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                workspace_path: result.workspace_path,
                                proposed_file: result.proposed_file,
                                proposed_old_text: result.proposed_old_text,
                                proposed_new_text: result.proposed_new_text
                            })
                        }
                    );

                    const applyResult = await response.json() as {
                        status?: string;
                        message?: string;
                        detail?: string;
                    };

                    if (!response.ok || applyResult.status !== 'applied') {
                        throw new Error(
                            applyResult.detail ||
                            applyResult.message ||
                            `Failed to apply fix (HTTP ${response.status})`
                        );
                    }

                    vscode.window.showInformationMessage(
                        `CodePilot: Fix applied to ${result.proposed_file}`
                    );

                    panel.dispose();

                } catch (error) {
                    vscode.window.showErrorMessage(
                        `CodePilot: Failed to apply fix: ${error}`
                    );
                }
            }
        },
        undefined,
        context.subscriptions
    );
}

export function activate(context: vscode.ExtensionContext) {
    vscode.window.showInformationMessage(
        'CodePilot extension activated!'
    );

    console.log('CodePilot activate() called');
    console.log(
        'CodePilot workspace:',
        vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
    );
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

            const extensionPath = path.resolve(context.extensionPath);

            let workspacePath = workspaceFolder?.uri.fsPath;

            if (
                !workspacePath ||
                path.resolve(workspacePath) === extensionPath
            ) {
                workspacePath = path.dirname(extensionPath);
            }

            console.log('CodePilot workspace:', workspacePath);

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
                            workspace_path: workspacePath
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        `Backend returned ${response.status}`
                    );
                }

                const result = parseDebugResponse(await response.json());

                showResultPanel(context, result);
            } catch (error) {
                vscode.window.showErrorMessage(
                    `CodePilot backend unavailable: ${error}`
                );
            }
        }
    );

    context.subscriptions.push(fixBugCommand);
}

export function deactivate() { }