from dataclasses import dataclass
from typing import Callable, List, Type
from cleo.commands.command import Command as CleoCommand
from cleo.events.console_events import COMMAND
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_multiverse_plugin.commands.check import CheckCommand
from poetry_multiverse_plugin.commands.info import InfoCommand
from poetry_multiverse_plugin.commands.lock import LockCommand
from poetry_multiverse_plugin.commands.run import RunCommand
from poetry_multiverse_plugin.commands.show import ShowCommand
from poetry_multiverse_plugin.hooks.build import PreBuildHook
from poetry_multiverse_plugin.hooks.hook import Hook, HookContext


@dataclass
class PluginConfig:
    commands: List[Type[CleoCommand]]
    pre_hooks: List[Callable[[], Hook]]

    def configure(self, application: Application):
        for cmd in self.commands:
            assert cmd.name is not None
            application.command_loader.register_factory(cmd.name, cmd)

        if application.event_dispatcher:
            application.event_dispatcher.add_listener(COMMAND, self._before_command)
    
    def _before_command(self, event: Event, kind: str, dispatcher: EventDispatcher) -> None:
        if context := HookContext.create(event):
            context.run(*self.pre_hooks)


class MultiversePlugin(ApplicationPlugin):
    def activate(self, application: Application):
        PluginConfig(
            commands=[
                CheckCommand,
                InfoCommand,
                LockCommand,
                RunCommand,
                ShowCommand
            ],
            pre_hooks=[
                PreBuildHook
            ]
        ).configure(application)
