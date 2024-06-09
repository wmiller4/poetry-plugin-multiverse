from pathlib import Path

from poetry_multiverse_plugin.commands import InfoCommand, ListCommand
from tests.utils import command, project


def test_workspace_info(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    info = command(root, InfoCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert root.package.name in output
    assert str(tmp_path) in output


def test_workspace_list(tmp_path: Path):
    root = project(tmp_path, workspace_root=True)
    project(tmp_path / 'child1')
    project(tmp_path / 'child2')
    info = command(root, ListCommand)
    assert info.execute() == 0

    output = info.io.fetch_output()
    assert root.package.name not in output
    assert 'child1' in output
    assert 'child2' in output
