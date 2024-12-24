from poetry.console.commands import show

from poetry_multiverse_plugin.repositories import lock, locked_pool
from poetry_multiverse_plugin.workspace import Workspace


class ShowCommand(show.ShowCommand):
    name = 'workspace show'
    description = 'List dependencies in the multiverse workspace.'

    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.io.write_error('Unable to locate workspace root')
            return 1

        root = workspace.root
        return_code = lock(root, locked_pool(list(workspace.packages)), env=self.env)
        if return_code != 0:
                self.io.write_error_line('<error>Failed to lock workspace!</>')
                return return_code

        self.set_poetry(root)
        return super().handle()
