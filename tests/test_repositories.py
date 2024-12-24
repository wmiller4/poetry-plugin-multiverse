from poetry.core.packages.package import Package
from poetry.utils.env import NullEnv

from poetry_multiverse_plugin.repositories import lock, locked_pool, project_pool
from tests import utils
from tests.conftest import ProjectFactory


def test_locked_pool():
    pool = locked_pool([Package('click', '8.1.2')])
    assert pool.search('click') == [
        Package('click', '8.1.2')
    ]


def test_project_pool(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p2 = utils.add(project('p2'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    pool = project_pool(p1, p2, locked=None)
    assert pool.search('click') == [
        Package('click', '8.0.9'),
        Package('click', '8.1.2'),
        Package('click', '8.1.4')
    ]


def test_project_pool_locked(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p2 = utils.add(project('p2'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    pool = project_pool(p1, p2, locked=p2)
    assert pool.search('click') == [
        Package('click', '8.1.2'),
        Package('click', '8.0.9'),
        Package('click', '8.1.2'),
        Package('click', '8.1.4')
    ]


def test_lock(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    project.packages(Package('click', '8.1.4'))

    pool = locked_pool([Package('click', '8.1.2')])
    assert lock(p1, pool, env=NullEnv()) == 0
    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]
