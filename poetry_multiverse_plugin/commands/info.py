from typing import List
from poetry.poetry import Poetry

from poetry_multiverse_plugin.commands.workspace import WorkspaceCommand
from poetry_multiverse_plugin.workspace import Workspace


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
