from cleo.events.console_command_event import ConsoleCommandEvent
from poetry.console.commands.lock import LockCommand
from poetry.core.packages.package import Package

from poetry_multiverse_plugin.commands.lock import LockCommand as WorkspaceLockCommand
from poetry_multiverse_plugin.hooks.hook import HookContext
from poetry_multiverse_plugin.hooks.lock import PostLockHook
from tests import utils
from tests.conftest import ProjectFactory
from tests.utils import command


def test_lock_disabled(project: ProjectFactory):
    project(workspace_root=True, lock=False)

    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    lock = command(p1, LockCommand, deps=[WorkspaceLockCommand])
    assert lock.execute() == 0

    context = HookContext.create(ConsoleCommandEvent(lock.command, lock.io))
    assert context is not None
    context.run(PostLockHook)

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.0.9')
    ]


def test_post_lock_hook(project: ProjectFactory):
    project(workspace_root=True, lock=True)

    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    lock = command(p1, LockCommand, deps=[WorkspaceLockCommand])
    assert lock.execute() == 0

    context = HookContext.create(ConsoleCommandEvent(lock.command, lock.io))
    assert context is not None
    context.run(PostLockHook)

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]
