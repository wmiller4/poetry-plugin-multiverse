from pathlib import Path

from poetry_plugin_multiverse.workspace import Workspace
from tests import utils
from poetry.core.constraints.version.version import Version
from poetry.core.packages.package import Package

from tests.conftest import ProjectFactory


def test_no_workspace(tmp_path: Path):
    poetry = utils.project(tmp_path)
    assert Workspace.create(poetry) is None


def test_self_workspace(tmp_path: Path):
    poetry = utils.project(tmp_path)
    (tmp_path / 'multiverse.toml').touch()
    workspace = Workspace.create(poetry) 
    assert workspace is not None
    assert workspace.root.pyproject_path != tmp_path / 'pyproject.toml'


def test_excluded_workspace(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('exclude = ["child"]')
    child = utils.project(tmp_path / 'child')
    workspace = Workspace.create(child) 
    assert workspace is None


def test_parent_workspace(tmp_path: Path):
    (tmp_path / 'multiverse.toml').touch()
    child = utils.project(tmp_path / 'child')
    workspace = Workspace.create(child) 
    assert workspace is not None
    assert workspace.root.pyproject_path != tmp_path / 'pyproject.toml'


def test_non_poetry_parent(tmp_path: Path):
    (tmp_path / 'pyproject.toml').touch()
    child = utils.project(tmp_path / 'child')
    workspace = Workspace.create(child) 
    assert workspace is None


def test_workspace_projects(project: ProjectFactory):
    child = project('child')
    workspace = project.workspace(child)

    projects = list(workspace.projects)
    assert(len(projects) == 1)
    assert projects[0].pyproject_path == child.pyproject_path


def test_dependencies_multiple(project: ProjectFactory):
    project.packages(
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^8.1')
    utils.add(project('p2'), 'click=^8')
    workspace = project.workspace(p1)

    resolved = dict(
        (dep.complete_name, dep)
        for dep in workspace.dependencies
    )
    constraint = resolved['click'].constraint
    assert constraint.allows(Version.from_parts(8, 1, 2)) is True
    assert constraint.allows(Version.from_parts(8, 0, 9)) is False
