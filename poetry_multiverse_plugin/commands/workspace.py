from poetry.console.commands.installer_command import InstallerCommand

from poetry_multiverse_plugin.workspace import Workspace


class WorkspaceCommand(InstallerCommand):
    def handle_workspace(self, workspace: Workspace) -> int:
        raise NotImplementedError
    
    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.line_error('Unable to locate workspace root')
            return 1
        return self.handle_workspace(workspace)
