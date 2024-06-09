from poetry.console.commands.env_command import EnvCommand

from poetry_multiverse_plugin.workspace import Workspace


class WorkspaceCommand(EnvCommand):
    def handle_workspace(self, workspace: Workspace) -> int:
        raise NotImplementedError
    
    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.line_error('Unable to locate workspace root')
            return 1
        return self.handle_workspace(workspace)


class InfoCommand(WorkspaceCommand):
    name = 'workspace info'
    description = 'Describe the multiverse workspace.'

    def handle_workspace(self, workspace: Workspace) -> int:
        self.line(f'Workspace {workspace.root.package.name}')
        self.line(f'  Directory: {workspace.root.pyproject_path.parent}')
        return 0


class ListCommand(WorkspaceCommand):
    name = 'workspace list'
    description = 'List projects in the multiverse workspace.'

    def handle_workspace(self, workspace: Workspace) -> int:
        for child in workspace.projects:
            self.line(f'{child.package.name}')
        return 0


class ShowCommand(WorkspaceCommand):
    name = 'workspace show'
    description = 'List dependendies in the multiverse workspace.'

    def handle_workspace(self, workspace: Workspace) -> int:
        for dep in workspace.dependencies:
            print(f'{dep.complete_pretty_name} {dep.pretty_constraint}')
        return 0
