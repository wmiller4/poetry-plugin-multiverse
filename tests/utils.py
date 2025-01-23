from pathlib import Path
from typing import List, Optional, Type

from cleo.commands.command import Command as CleoCommand
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from cleo.testers.command_tester import CommandTester
from poetry.console.application import Application
from poetry.console.commands.add import AddCommand
from poetry.console.commands.command import Command
from poetry.console.commands.env_command import EnvCommand
from poetry.console.commands.installer_command import InstallerCommand
from poetry.console.commands.self.self_command import SelfCommand
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories import RepositoryPool
from poetry.utils.env.mock_env import MockEnv


def set_env(command: CleoCommand):
    if not isinstance(command, EnvCommand) or isinstance(command, SelfCommand):
        return
    if command._env is not None:
        return
    path = (command.poetry.pyproject_path / '..' / ".venv").resolve()
    path.mkdir(parents=True, exist_ok=True)
    command.set_env(MockEnv(path=path, is_venv=True))


class MockApplication(Application):
    def __init__(self, poetry: Poetry) -> None:
        super().__init__()
        self._poetry = poetry

    def reset_poetry(self) -> None:
        assert self._poetry is not None
        self._poetry = Factory().create_poetry(self._poetry.pyproject_path.parent)
    
    def configure_env(self, event: Event, event_name: str, _: EventDispatcher) -> None:
        from poetry.console.commands.env_command import EnvCommand

        if not isinstance(event, ConsoleCommandEvent):
            return
        command = event.command
        if not isinstance(command, EnvCommand) or isinstance(command, SelfCommand):
            return
        set_env(command)


def command(
    poetry: Poetry,
    factory: Type[CleoCommand], *,
    deps: Optional[List[Type[CleoCommand]]] = None
) -> CommandTester:
    app = MockApplication(poetry)
    for dep in deps or []:
        app.add(dep())
    cmd = factory()
    cmd.set_application(app)
    tester = CommandTester(cmd)
    set_env(cmd)
    if isinstance(cmd, InstallerCommand):
        Application.configure_installer_for_command(cmd, tester.io)
    if isinstance(cmd, Command):
        cmd.set_poetry(poetry)
    return tester


def project(
    path: Path, *,
    pool: Optional[RepositoryPool] = None
) -> Poetry:
    assert CommandTester(Application().find('new')).execute(str(path)) == 0
    poetry = Factory().create_poetry(path)
    poetry.set_pool(pool or RepositoryPool([]))
    return poetry

    
def add(poetry: Poetry, *requirements: str) -> Poetry:
    assert command(poetry, AddCommand).execute(f'--lock {" ".join(requirements)}') == 0
    return poetry
