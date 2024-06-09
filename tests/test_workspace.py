from pathlib import Path
from poetry_multiverse_plugin.workspace import Workspace
from tests.utils import project
from poetry.core.constraints.version.version import Version


def test_no_workspace(tmp_path: Path):
    poetry = project(tmp_path)
    assert Workspace.create(poetry) is None


def test_self_workspace(tmp_path: Path):
    poetry = project(tmp_path, workspace_root=True)
    workspace = Workspace.create(poetry) 
    assert workspace is not None
    assert workspace.root.pyproject_path == tmp_path / 'pyproject.toml'


def test_parent_workspace(tmp_path: Path):
    parent = project(tmp_path, workspace_root=True)
    child = project(tmp_path / 'project')
    workspace = Workspace.create(child) 
    assert workspace is not None
    assert workspace.root.pyproject_path == parent.pyproject_path


def test_workspace_projects(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    child = project(tmp_path / 'project')
    workspace = Workspace.create(root) 
    assert workspace is not None

    projects = list(workspace.projects)
    assert(len(projects) == 1)
    assert projects[0].pyproject_path == child.pyproject_path


def test_dependencies(tmp_path: Path):
    root = project(tmp_path, workspace_root=True, dependencies=['click=^7'])
    workspace = Workspace.create(root) 
    assert workspace is not None

    package_names = set(dep.name for dep in workspace.dependencies)
    assert 'click' in package_names


def test_dependencies_conflict(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    project(tmp_path / 'p1', dependencies=['click=^7'])
    project(tmp_path / 'p2', dependencies=['click=^8'])
    workspace = Workspace.create(root) 
    assert workspace is not None

    conflicts = set(
        dep.complete_name for dep in workspace.dependencies
        if dep.constraint.is_empty()
    )
    assert 'click' in conflicts


def test_dependencies_multiple(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    project(tmp_path / 'p1', dependencies=['click=^8.1'])
    project(tmp_path / 'p2', dependencies=['click=^8'])
    workspace = Workspace.create(root) 
    assert workspace is not None

    resolved = dict(
        (dep.complete_name, dep)
        for dep in workspace.dependencies
    )
    constraint = resolved['click'].constraint
    assert constraint.allows(Version.from_parts(8, 1, 2)) is True
    assert constraint.allows(Version.from_parts(8, 0, 9)) is False
