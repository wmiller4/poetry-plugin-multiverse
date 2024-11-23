from pathlib import Path

from cleo.testers.application_tester import ApplicationTester
from poetry.console.commands.command import Command

from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.plugin import PluginConfig
from poetry_multiverse_plugin.workspace import Workspace
from tests.conftest import ProjectFactory
from tests.utils import MockApplication


class BrokenHook(Hook):
    def run(self, workspace: Workspace, command: Command):
        raise Exception('BrokenHook is broken!')
    
    @staticmethod
    def with_command_names(*names: str) -> 'BrokenHook':
        class HookImpl(BrokenHook):
            command_names = set(names)

        return HookImpl()


def test_no_workspace(project: ProjectFactory):
    tester = ApplicationTester(MockApplication(project()))
    assert tester.execute('workspace info') == 1
    assert 'workspace root' in tester.io.fetch_error()


def test_workspace(project: ProjectFactory):
    root = project(workspace_root=True)
    p1 = project('p1')
    tester = ApplicationTester(MockApplication(root))
    assert tester.execute('workspace info') == 0
    assert p1.package.name in tester.io.fetch_output()


def test_non_poetry_parent(project: ProjectFactory, tmp_path: Path):
    (tmp_path / 'pyproject.toml').touch()
    tester = ApplicationTester(MockApplication(project('p1')))
    assert tester.execute('lock') == 0


def test_hook_exception_handler(project: ProjectFactory):
    def broken_hook() -> BrokenHook:
        return BrokenHook.with_command_names('lock')

    project(workspace_root=True)
    p1 = project('p1')
    app = MockApplication(p1)
    PluginConfig(commands=[], pre_hooks=[broken_hook]).configure(app)
    tester = ApplicationTester(app)

    assert tester.execute('lock') == 0
    assert 'Multiverse' in tester.io.fetch_error()
