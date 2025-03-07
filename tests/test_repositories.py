from poetry.core.packages.package import Package
from poetry.utils.env import NullEnv

from poetry_plugin_multiverse.repositories import lock, locked_pool, workspace_pool
from tests import utils
from tests.conftest import ProjectFactory


def test_locked_pool(project: ProjectFactory):
    pool = locked_pool(project('p1'), packages=[Package('click', '8.1.2')], strict=True)
    assert pool.search('click') == [
        Package('click', '8.1.2')
    ]


def test_workspace_pool(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p2 = utils.add(project('p2'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    pool = workspace_pool(p1, p2)
    assert pool.search('click') == [
        Package('click', '8.0.9'),
        Package('click', '8.1.2'),
        Package('click', '8.1.4')
    ]


def test_workspace_pool_locked(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    p2 = utils.add(project('p2'), 'click=^8.1')

    project.packages(Package('click', '8.1.4'))

    pool = locked_pool(p1, p2, packages=p2.locker.locked_repository().packages, strict=True)
    assert pool.search('click') == [
        Package('click', '8.1.2')
    ]


def test_project_pool_urls(project: ProjectFactory):
    project.packages(Package('click', '8.1.2'))
    p2 = utils.add(project('p2'), 'click=^8.1')

    pool = locked_pool(p2, packages=p2.locker.locked_repository().packages, strict=True)
    links = pool.repository('mock').find_links_for_package(pool.search('click')[0])
    assert len(links) > 0


def test_lock(project: ProjectFactory):
    project.packages(Package('click', '8.0.9'))
    p1 = utils.add(project('p1'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    project.packages(Package('click', '8.1.4'))

    pool = locked_pool(p1, packages=[Package('click', '8.1.2')], strict=True)
    assert lock(p1, pool, env=NullEnv()) == 0
    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]
