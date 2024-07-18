from poetry_multiverse_plugin.commands.run import RunCommand
from tests.conftest import ProjectFactory
from tests.utils import command


def test_run_success(project: ProjectFactory):
    root = project(workspace_root=True)
    p1 = project('p1')
    p2 = project('p2')

    lock = command(root, RunCommand)
    assert lock.execute('touch file.txt') == 0
    assert (p1.pyproject_path.parent / 'file.txt').is_file()
    assert (p2.pyproject_path.parent / 'file.txt').is_file()


def test_run_fail(project: ProjectFactory):
    root = project(workspace_root=True)
    p1 = project('p1')
    project('p2')

    (p1.pyproject_path.parent / 'file.txt').touch()

    lock = command(root, RunCommand)
    assert lock.execute('cat file.txt') != 0
