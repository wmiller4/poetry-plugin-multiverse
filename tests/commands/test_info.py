from poetry_multiverse_plugin.commands.info import InfoCommand
from tests.conftest import ProjectFactory
from tests.utils import command


def test_workspace_info(project: ProjectFactory):
    root = project(workspace_root=True)
    project('child1')
    project('child2')
    info = command(root, InfoCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert 'workspace' in output
    assert str(root.pyproject_path.parent) in output
    assert 'child1' in output
    assert 'child2' in output
