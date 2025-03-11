from cleo.events.console_command_event import ConsoleCommandEvent
from poetry.console.commands.lock import LockCommand
from poetry.core.packages.package import Package

from poetry_plugin_multiverse.commands.lock import LockCommand as WorkspaceLockCommand, explicit_regenerate
from poetry_plugin_multiverse.hooks.hook import HookContext
from poetry_plugin_multiverse.hooks.lock import PostLockHook, PreLockHook
from tests import utils
from tests.conftest import ProjectFactory
from tests.utils import command


REGENERATE = '--regenerate' if explicit_regenerate() else ''


def test_lock_disabled(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=<8.1')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.4'))

    project.workspace(p1)
    lock = command(p1, LockCommand, deps=[WorkspaceLockCommand])
    context = HookContext.create(ConsoleCommandEvent(lock.command, lock.io))
    assert context is not None

    context.run(PreLockHook)
    assert lock.execute(REGENERATE) == 0
    context.run(PostLockHook)

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.0.9')
    ]


def test_pre_lock_hook(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=<8.1')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.4'))

    project.workspace(p1, config={ 'hooks': ['lock'] })
    lock = command(p1, LockCommand, deps=[WorkspaceLockCommand])
    context = HookContext.create(ConsoleCommandEvent(lock.command, lock.io))
    assert context is not None

    context.run(PreLockHook)
    assert lock.execute(REGENERATE) == 0

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.0.9')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.0.9')
    ]


def test_post_lock_hook(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    project.workspace(p1, config={ 'hooks': ['lock'] })
    lock = command(p1, LockCommand, deps=[WorkspaceLockCommand])
    context = HookContext.create(ConsoleCommandEvent(lock.command, lock.io))
    assert context is not None

    assert lock.execute(REGENERATE) == 0
    context.run(PostLockHook)

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]
