from typing import List
from poetry.console.commands.env_command import EnvCommand
from poetry.core.packages.dependency import Dependency
from poetry.poetry import Poetry

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
        root = workspace.root
        projects = sorted(workspace.projects, key=lambda p: p.package.name)

        def format_row(project: Poetry) -> List[str]:
            return [
                f'<b>{project.package.name}</>',
                str(project.pyproject_path.parent.relative_to(root.pyproject_path.parent))
            ]

        self.table(style='compact') \
            .set_headers([f'{root.package.name}', str(root.pyproject_path.parent)]) \
            .set_rows([format_row(project) for project in projects]) \
            .render()
        return 0


class ShowCommand(WorkspaceCommand):
    name = 'workspace show'
    description = 'List dependencies in the multiverse workspace.'

    def handle_workspace(self, workspace: Workspace) -> int:
        dependencies = sorted(workspace.dependencies, key=lambda dep: dep.complete_pretty_name)

        def format_row(dep: Dependency) -> List[str]:
            return [
                f'<fg=cyan>{dep.complete_pretty_name}</>',
                '<error>Conflict</>' if dep.constraint.is_empty() else f'<b>{dep.pretty_constraint}</>',
            ]
        
        self.table(
            style='compact',
            rows=[format_row(dep) for dep in dependencies]
        ).render()
        return 0
