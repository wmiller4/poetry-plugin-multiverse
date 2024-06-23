from typing import Type
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_multiverse_plugin.commands.check import CheckCommand
from poetry_multiverse_plugin.commands.info import InfoCommand
from poetry_multiverse_plugin.commands.lock import LockCommand
from poetry_multiverse_plugin.commands.show import ShowCommand
from poetry_multiverse_plugin.commands.workspace import WorkspaceCommand


def register(application: Application, *commands: Type[WorkspaceCommand]):
    for cmd in commands:
        assert cmd.name is not None
        application.command_loader.register_factory(cmd.name, cmd)


class MultiversePlugin(ApplicationPlugin):
    def activate(self, application: Application):
        register(application, CheckCommand, InfoCommand, LockCommand, ShowCommand)
