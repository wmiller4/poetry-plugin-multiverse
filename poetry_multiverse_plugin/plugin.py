from typing import Type
from cleo.commands.command import Command
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_multiverse_plugin.commands.check import CheckCommand
from poetry_multiverse_plugin.commands.info import InfoCommand
from poetry_multiverse_plugin.commands.lock import LockCommand
from poetry_multiverse_plugin.commands.run import RunCommand
from poetry_multiverse_plugin.commands.show import ShowCommand


def register(application: Application, *commands: Type[Command]):
    for cmd in commands:
        assert cmd.name is not None
        application.command_loader.register_factory(cmd.name, cmd)


class MultiversePlugin(ApplicationPlugin):
    def activate(self, application: Application):
        register(application, CheckCommand, InfoCommand, LockCommand, RunCommand, ShowCommand)
