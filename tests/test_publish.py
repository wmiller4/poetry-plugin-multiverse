from poetry.core.constraints.version.version import Version
from poetry.core.packages.package import Package

from poetry_plugin_multiverse.publish import PublishedDependencies
from tests import utils
from tests.conftest import ProjectFactory


def test_patch_versions(project: ProjectFactory):
    p1 = project('p1')
    p1.package.version = Version.from_parts(1, 2, 34)

    p2 = utils.add(project('p2'), '../p1')
    PublishedDependencies([p1, p2]).patch_project(p2)

    print(p2.package.all_requires)
    assert p2.package.all_requires[0].name == p1.package.name
    assert p2.package.all_requires[0].constraint.allows(p1.package.version) is True
    assert p2.package.all_requires[0].constraint.allows(Version.from_parts(1, 2, 33)) is False


def test_ignore_external_deps(project: ProjectFactory):
    project.packages(Package('click', '7.0.9'))
    p1 = utils.add(project('p1'), 'click')
    PublishedDependencies([p1]).patch_project(p1)

    print(p1.package.all_requires)
    assert p1.package.all_requires[0].name == 'click'
    assert p1.package.all_requires[0].constraint.allows(Version.from_parts(7, 0, 9)) is True
    assert p1.package.all_requires[0].constraint.allows(p1.package.version) is False
