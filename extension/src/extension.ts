import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const fixBugCommand = vscode.commands.registerCommand(
        'codepilot.fixBug',
        () => {
            vscode.window.showInformationMessage(
                'CodePilot is ready to debug your project.'
            );
        }
    );

    context.subscriptions.push(fixBugCommand);
}

export function deactivate() {}