from poetry_plugin_multiverse.commands.info import InfoCommand
from tests.conftest import ProjectFactory
from tests.utils import command


def test_workspace_info(project: ProjectFactory):
    p1 = project('child1')
    project('child2')
    workspace = project.workspace(p1)
    info = command(p1, InfoCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert 'workspace' in output
    assert str(workspace.config.root) in output
    assert 'child1' in output
    assert 'child2' in output
