from poetry_multiverse_plugin.dependencies import Dependencies
from tests import utils
from poetry.core.constraints.version.version import Version
from poetry.core.packages.package import Package

from tests.conftest import ProjectFactory


def test_dependencies(project: ProjectFactory):
    project.packages(Package('click', '7.0.9'))
    root = project(workspace_root=True)
    utils.add(root, 'click=^7')

    package_names = set(dep.name for dep in Dependencies.from_projects(root))
    assert 'click' in package_names


def test_dependencies_conflict(project: ProjectFactory):
    project.packages(
        Package('click', '7.0.9'),
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^7')
    p2 = utils.add(project('p2'), 'click=^8')

    conflicts = list(Dependencies.from_projects(p1, p2).conflicts)
    assert conflicts[0].name == 'click'


def test_dependencies_multiple(project: ProjectFactory):
    project.packages(
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^8.1')
    p2 = utils.add(project('p2'), 'click=^8')

    dependencies = Dependencies.from_projects(p1, p2)
    assert list(dependencies.conflicts) == []

    resolved = dict(
        (dep.complete_name, dep)
        for dep in Dependencies.from_projects(p1, p2)
    )
    constraint = resolved['click'].constraint
    assert constraint.allows(Version.from_parts(8, 1, 2)) is True
    assert constraint.allows(Version.from_parts(8, 0, 9)) is False
