from poetry_multiverse_plugin.commands.check import CheckCommand
from tests.conftest import ProjectFactory
from tests.utils import command
from tests import utils
from poetry.core.packages.package import Package


def test_dependencies_conflict(project: ProjectFactory):
    root = project(workspace_root=True)
    project.packages(
        Package('click', '7.0.9'),
        Package('click', '8.1.2')
    )
    utils.add(project('p1'), 'click=^7')
    utils.add(project('p2'), 'click=^8')

    check = command(root, CheckCommand)
    assert check.execute() == 1

    output = check.io.fetch_output()
    assert 'click' in output
    assert '^7' in output
    assert '^8' in output


def test_multiple_versions(project: ProjectFactory):
    root = project(workspace_root=True)

    project.packages(
        Package('click', '8.0.9')
    )
    utils.add(project('p2'), 'click=^8')

    project.packages(
        Package('click', '8.1.2')
    )
    utils.add(project('p1'), 'click=^8.1')

    check = command(root, CheckCommand)
    assert check.execute() == 1

    output = check.io.fetch_output()
    assert 'click' in output
    assert '8.0.9' in output
    assert '8.1.2' in output


def test_no_issues(project: ProjectFactory):
    root = project(workspace_root=True)

    project.packages(
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    )
    utils.add(project('p1'), 'click=^8.1')
    utils.add(project('p2'), 'click=^8')

    check = command(root, CheckCommand)
    assert check.execute() == 0
