from abc import abstractmethod
from dataclasses import dataclass
import json
import os
from typing import Callable, ClassVar, Mapping, Optional, Set
from cleo.events.event import Event
from cleo.events.console_command_event import ConsoleCommandEvent
from poetry.console.commands.command import Command

from poetry_multiverse_plugin.workspace import Workspace


class Hook:
    command_names: ClassVar[Set[str]]

    @abstractmethod
    def run(self, workspace: Workspace, command: Command):
        raise NotImplementedError()


@dataclass
class HookContext:
    workspace: Workspace
    command: Command

    def run(self, *hooks: Callable[[], Hook]):
        for hook in hooks:
            hook_instance = hook()
            if self.command.name in hook_instance.command_names:
                hook_instance.run(self.workspace, self.command)

    @staticmethod
    def create(event: Event, env: Optional[Mapping[str, str]] = None) -> Optional['HookContext']:
        if json.loads((env or os.environ).get('MULTIVERSE_DISABLE_HOOKS') or 'false'):
            return None
        if not isinstance(event, ConsoleCommandEvent):
            return None
        if not isinstance(event.command, Command):
            return None
        if workspace := Workspace.create(event.command.poetry):
            return HookContext(workspace, event.command)
