from functools import partial
from typing import Type
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_multiverse_plugin.commands import InfoCommand, ListCommand, WorkspaceCommand


def register(application: Application, *commands: Type[WorkspaceCommand]):
    for cmd in commands:
        assert cmd.name is not None
        application.command_loader.register_factory(
            cmd.name,
            partial(cmd, application.poetry)
        )


class MultiversePlugin(ApplicationPlugin):
    def activate(self, application: Application):
        register(application, InfoCommand, ListCommand)
