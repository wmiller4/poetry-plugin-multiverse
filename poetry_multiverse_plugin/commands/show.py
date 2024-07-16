from cleo.io.null_io import NullIO
from poetry.console.commands import show

from poetry_multiverse_plugin.installers import Installers
from poetry_multiverse_plugin.workspace import Workspace


class ShowCommand(show.ShowCommand):
    name = 'workspace show'
    description = 'List dependencies in the multiverse workspace.'

    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.io.write_error('Unable to locate workspace root')
            return 1

        installer = Installers(workspace, NullIO(), self.env)
        installer.root(locked=True).lock().run()
        self.set_poetry(workspace.root)
        for dep in workspace.dependencies:
            self.poetry.package.add_dependency(dep)
        self.poetry.set_locker(installer.locker)
        return super().handle()
