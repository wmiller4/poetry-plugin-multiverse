from poetry_multiverse_plugin.runner import has_cycle, project_graph
from tests.conftest import ProjectFactory
from tests.utils import add


def test_dependencies_local(project: ProjectFactory):
    workspace = project.workspace()
    project('p1')
    add(project('p2'), '../p1')

    assert has_cycle(project_graph(workspace.projects)) is False


def test_dependencies_local_cycle(project: ProjectFactory):
    workspace = project.workspace()
    p1 = project('p1')
    p2 = project('p2')
    add(p2, '../p1')
    add(p1, '../p2')

    assert has_cycle(project_graph(workspace.projects)) is False
