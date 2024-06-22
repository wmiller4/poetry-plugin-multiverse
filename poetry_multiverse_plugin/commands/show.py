from typing import List
from poetry.core.packages.dependency import Dependency

from poetry_multiverse_plugin.commands.workspace import WorkspaceCommand
from poetry_multiverse_plugin.workspace import Workspace


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
