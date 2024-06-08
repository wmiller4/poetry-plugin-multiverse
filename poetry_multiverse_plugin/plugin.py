from cleo.commands.command import Command
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.poetry import Poetry

from poetry_multiverse_plugin.workspace import Workspace


class WorkspaceCommand(Command):
    name = 'workspace'

    def __init__(self, poetry: Poetry) -> None:
        super().__init__()
        self.poetry = poetry

    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.line_error('Unable to locate workspace root')
            return 1
        self.line(f'Workspace {workspace.root.package.name}')
        for child in workspace.projects:
            self.line(f'  Project {child.package.name}')
        return 0


class MultiversePlugin(ApplicationPlugin):
    def activate(self, application: Application):
        application.command_loader.register_factory(
            'workspace',
            lambda: WorkspaceCommand(application.poetry)
        )
