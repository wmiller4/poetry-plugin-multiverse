from poetry_multiverse_plugin.packages import Packages
from tests import utils
from poetry.core.packages.package import Package

from tests.conftest import ProjectFactory


def test_packages_multiple(project: ProjectFactory):
    project.packages(
        Package('click', '8.0.9')
    )
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^8.1')

    packages = Packages.from_projects(p1, p2)
    assert set(packages) == {
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    }


def test_packages_pool(project: ProjectFactory):
    project.packages(
        Package('click', '8.0.9')
    )
    p2 = utils.add(project('p2'), 'click=^8')

    project.packages(
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^8.1')

    pool = Packages.from_projects(p1, p2).repository_pool
    assert set(pool.search('click')) == {
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    }
