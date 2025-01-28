import pytest
from poetry_plugin_multiverse.commands.lock import LockCommand
from tests.conftest import ProjectFactory
from tests.utils import command
from tests import utils
from poetry.core.packages.package import Package
from poetry.puzzle.exceptions import SolverProblemError


def test_dependencies_conflict(project: ProjectFactory):
    project.packages(
        Package('click', '7.0.9'),
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^7')
    utils.add(project('p2'), 'click=^8')

    project.workspace(p1)
    lock = command(p1, LockCommand)
    with pytest.raises(SolverProblemError):
        lock.execute()


def test_align_versions(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    project.workspace(p1)
    lock = command(p1, LockCommand)
    assert lock.execute('--no-update') == 0

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]


def test_update_versions(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    project.workspace(p1)
    lock = command(p1, LockCommand)
    assert lock.execute() == 0

    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]

    assert p2.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]
