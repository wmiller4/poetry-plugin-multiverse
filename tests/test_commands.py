
from poetry_multiverse_plugin.commands import InfoCommand, ListCommand
from tests.conftest import ProjectFactory
from tests.utils import command


def test_workspace_info(project: ProjectFactory):
    root = project(workspace_root=True)
    info = command(root, InfoCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert root.package.name in output
    assert str(root.pyproject_path.parent) in output


def test_workspace_list(project: ProjectFactory):
    root = project(workspace_root=True)
    project('child1')
    project('child2')
    info = command(root, ListCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert root.package.name not in output
    assert 'child1' in output
    assert 'child2' in output
