from packaging.utils import canonicalize_name
from poetry.console.commands.add import AddCommand
from poetry.core.constraints.version.version import Version
from poetry.core.packages.package import Package
from poetry.poetry import Poetry

from poetry_plugin_multiverse.publish import PublishedDependencies
from poetry_plugin_multiverse.workspace import Workspace
from tests import utils
from tests.conftest import ProjectFactory


def add_optional_extra() -> bool:
    return any(
        option.name == 'optional' and not option.is_flag()
        for option in AddCommand.options
    )


def add_optional(workspace: Workspace, project: Poetry, dependency: str, extra: str) -> Poetry:
    if add_optional_extra():
        return utils.add(project, dependency, f'--optional={extra}')

    utils.add(project, dependency, '--optional')
    with project.pyproject_path.open('a') as out:
        out.write(f'''
[tool.poetry.extras]
{extra} = ["{dependency.split('/')[-1]}"]
''')
    return [
        child for child in workspace.projects
        if child.package.name == project.package.name
    ][0]


def test_patch_versions(project: ProjectFactory):
    p1 = project('p1')
    p1.package.version = Version.from_parts(1, 2, 34)

    p2 = utils.add(project('p2'), '../p1')
    PublishedDependencies([p1, p2]).patch_project(p2)

    print(p2.package.all_requires)
    assert p2.package.all_requires[0].name == p1.package.name
    assert p2.package.all_requires[0].constraint.allows(p1.package.version) is True
    assert p2.package.all_requires[0].constraint.allows(Version.from_parts(1, 2, 33)) is False


def test_patch_versions_optional(project: ProjectFactory):
    p1 = project('p1')
    p1.package.version = Version.from_parts(1, 2, 34)

    p2 = add_optional(project.workspace(p1), project('p2'), '../p1', 'test')
    PublishedDependencies([p1, p2]).patch_project(p2)

    dependency = p2.package.extras[canonicalize_name('test')][0]
    assert dependency.name == p1.package.name
    assert dependency.constraint.allows(p1.package.version) is True
    assert dependency.constraint.allows(Version.from_parts(1, 2, 33)) is False
    assert dependency.in_extras == ['test']


def test_ignore_external_deps(project: ProjectFactory):
    project.packages(Package('click', '7.0.9'))
    p1 = utils.add(project('p1'), 'click')
    PublishedDependencies([p1]).patch_project(p1)

    print(p1.package.all_requires)
    assert p1.package.all_requires[0].name == 'click'
    assert p1.package.all_requires[0].constraint.allows(Version.from_parts(7, 0, 9)) is True
    assert p1.package.all_requires[0].constraint.allows(p1.package.version) is False
