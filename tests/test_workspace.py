from pathlib import Path
from poetry.console.application import Application
from poetry.factory import Factory
from poetry.poetry import Poetry
from cleo.commands.command import Command
from cleo.testers.command_tester import CommandTester

from poetry_multiverse_plugin.workspace import Workspace


class PoetryInstance:
    def __init__(self, *commands: Command) -> None:
        self.application = Application()
        for cmd in commands:
            self.application.add(cmd)
    
    def run(self, command: str, args: str) -> int:
        return CommandTester(self.application.find(command)).execute(args)


def project(path: Path, *, workspace_root: bool = False) -> Poetry:
    assert PoetryInstance().run('new', str(path)) == 0
    if workspace_root:
        with (path / 'pyproject.toml').open('a') as file:
            file.write('''
                [tool.multiverse]
                root = true
            ''')
    return Factory().create_poetry(path)


def test_no_workspace(tmp_path: Path):
    poetry = project(tmp_path)
    assert Workspace.create(poetry) is None


def test_self_workspace(tmp_path: Path):
    poetry = project(tmp_path, workspace_root=True)
    workspace = Workspace.create(poetry) 
    assert workspace is not None
    assert workspace.root.pyproject_path == tmp_path / 'pyproject.toml'


def test_parent_workspace(tmp_path: Path):
    parent = project(tmp_path, workspace_root=True)
    child = project(tmp_path / 'project')
    workspace = Workspace.create(child) 
    assert workspace is not None
    assert workspace.root.pyproject_path == parent.pyproject_path


def test_workspace_projects(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    child = project(tmp_path / 'project')
    workspace = Workspace.create(root) 
    assert workspace is not None

    projects = list(workspace.projects)
    assert(len(projects) == 1)
    assert projects[0].pyproject_path == child.pyproject_path
