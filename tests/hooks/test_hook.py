
from cleo.events.console_command_event import ConsoleCommandEvent
from poetry.console.commands.command import Command

from poetry_multiverse_plugin.hooks.hook import Hook, HookContext
from poetry_multiverse_plugin.workspace import Workspace
from tests.conftest import ProjectFactory
from tests.utils import command


class SimpleCommand(Command):
    name = 'testcmd'
    description = 'A no-op command for testing hooks.'

    def handle(self) -> int:
        return 0


class SimpleHook(Hook):
    def __init__(self) -> None:
        super().__init__()
        self.was_run = False

    def run(self, workspace: Workspace, command: Command):
        resolved = Workspace.create(command.poetry)
        assert resolved is not None
        assert workspace.root.pyproject_path.resolve() == resolved.root.pyproject_path.resolve()
        assert command.name in self.command_names
        self.was_run = True
    
    @staticmethod
    def with_command_names(*names: str) -> 'SimpleHook':
        class HookImpl(SimpleHook):
            command_names = set(names)

        return HookImpl()


def test_no_workspace(project: ProjectFactory):
    root = project()
    info = command(root, SimpleCommand)

    context = HookContext.create(ConsoleCommandEvent(info.command, info.io))
    assert context is None


def test_disabled_hooks(project: ProjectFactory):
    root = project(workspace_root=True)
    info = command(root, SimpleCommand)

    context = HookContext.create(
        ConsoleCommandEvent(info.command, info.io),
        { 'MULTIVERSE_DISABLE_HOOKS': 'true' }
    )
    assert context is None


def test_enabled_hooks(project: ProjectFactory):
    root = project(workspace_root=True)
    info = command(root, SimpleCommand)

    context = HookContext.create(
        ConsoleCommandEvent(info.command, info.io),
        { 'MULTIVERSE_DISABLE_HOOKS': 'false' }
    )
    assert context is not None


def test_skip_hook_name(project: ProjectFactory):
    root = project(workspace_root=True)
    project('child1')
    info = command(root, SimpleCommand)

    context = HookContext.create(ConsoleCommandEvent(info.command, info.io))
    assert context is not None

    hook = SimpleHook.with_command_names('acmd', 'anothercmd')
    context.run(lambda: hook)
    assert hook.was_run is False


def test_run_hook(project: ProjectFactory):
    root = project(workspace_root=True)
    project('child1')
    info = command(root, SimpleCommand)

    context = HookContext.create(ConsoleCommandEvent(info.command, info.io))
    assert context is not None

    hook = SimpleHook.with_command_names('testcmd', 'anothercmd')
    context.run(lambda: hook)
    assert hook.was_run is True
