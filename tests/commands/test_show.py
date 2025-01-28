from poetry.core.packages.package import Package

from poetry_plugin_multiverse.commands.show import ShowCommand
from tests import utils
from tests.conftest import ProjectFactory


def test_show_no_workspace(project: ProjectFactory):
    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    show = utils.command(p1, ShowCommand)
    assert show.execute() == 1

    output = show.io.fetch_error()
    assert 'workspace root' in output


def test_show(project: ProjectFactory):
    project.packages(Package('click', '8.1.2'))
    p1 = utils.add(project('p1'), 'click=^8.1')

    project.workspace(p1)
    show = utils.command(p1, ShowCommand)
    assert show.execute() == 0

    output = show.io.fetch_output()
    assert 'click' in output
    assert '8.1.2' in output


def test_show_conflict(project: ProjectFactory):
    project.packages(
        Package('click', '7.0.9'),
        Package('click', '8.1.2')
    )
    p1 = utils.add(project('p1'), 'click=^7')
    utils.add(project('p2'), 'click=^8')

    project.workspace(p1)
    show = utils.command(p1, ShowCommand)
    assert show.execute() == 1

    output = show.io.fetch_error()
    assert 'Failed to lock workspace' in output
