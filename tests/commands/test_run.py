from poetry_multiverse_plugin.commands.run import RunCommand
from tests.conftest import ProjectFactory
from tests.utils import command


def test_run_success(project: ProjectFactory):
    p1 = project('p1')
    p2 = project('p2')

    project.workspace(p1)
    lock = command(p1, RunCommand)
    assert lock.execute('touch file.txt') == 0
    assert (p1.pyproject_path.parent / 'file.txt').is_file()
    assert (p2.pyproject_path.parent / 'file.txt').is_file()


def test_run_fail(project: ProjectFactory):
    p1 = project('p1')
    project('p2')

    (p1.pyproject_path.parent / 'file.txt').touch()

    project.workspace(p1)
    lock = command(p1, RunCommand)
    assert lock.execute('cat file.txt') != 0
