from pathlib import Path
from typing import Optional, Type
from cleo.testers.command_tester import CommandTester
from poetry.console.application import Application
from poetry.console.commands.add import AddCommand
from poetry.console.commands.command import Command
from poetry.console.commands.env_command import EnvCommand
from poetry.console.commands.installer_command import InstallerCommand
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories import RepositoryPool
from poetry.utils.env.mock_env import MockEnv


class MockApplication(Application):
    def __init__(self, poetry: Poetry) -> None:
        super().__init__()
        self._poetry = poetry

    def reset_poetry(self) -> None:
        assert self._poetry is not None
        self._poetry = Factory().create_poetry(self._poetry.pyproject_path.parent)


def command(poetry: Poetry, factory: Type[Command]) -> CommandTester:
    cmd = factory()
    cmd.set_application(MockApplication(poetry))
    tester = CommandTester(cmd)
    if isinstance(cmd, EnvCommand):
        path = (poetry.pyproject_path / '..' / ".venv").resolve()
        path.mkdir(parents=True, exist_ok=True)
        cmd.set_env(MockEnv(path=path, is_venv=True))
    if isinstance(cmd, InstallerCommand):
        Application.configure_installer_for_command(cmd, tester.io)
    cmd.set_poetry(poetry)
    return tester


def project(
        path: Path, *,
        workspace_root: bool = False,
        pool: Optional[RepositoryPool] = None
) -> Poetry:
    assert CommandTester(Application().find('new')).execute(str(path)) == 0
    if workspace_root:
        with (path / 'pyproject.toml').open('a') as file:
            file.write('''
                [tool.multiverse]
                root = true
            ''')
    poetry = Factory().create_poetry(path)
    poetry.set_pool(pool or RepositoryPool([]))
    return poetry

    
def add(poetry: Poetry, *requirements: str):
    assert command(poetry, AddCommand).execute(f'--lock {" ".join(requirements)}') == 0
