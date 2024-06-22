from cleo.io.null_io import NullIO
from poetry.core.packages.package import Package
from poetry.utils.env import NullEnv

from poetry_multiverse_plugin.installers import Installers
from tests import utils
from tests.conftest import ProjectFactory


def test_root_multiple_versions(project: ProjectFactory):
    root = project(workspace_root=True)

    project.packages(Package('click', '8.0.9'))
    utils.add(project('p2'), 'click=^8')

    project.packages(Package('click', '8.1.2'))
    utils.add(project('p1'), 'click=^8.1')

    # Ensure installer uses lock files, not remote repository
    project.pool.repositories[0].remove_package(Package('click', '8.0.9'))
    project.pool.repositories[0].remove_package(Package('click', '8.1.2'))

    installer = Installers(project.workspace(root), NullIO(), NullEnv())
    assert installer.root(locked=True).lock().run() == 0
    assert installer.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]


def test_root_update(project: ProjectFactory):
    root = project(workspace_root=True)
    project.packages(Package('click', '8.1.2'))
    utils.add(project('p1'), 'click=^8.1')

    project.pool.repositories[0].remove_package(Package('click', '8.1.2'))
    project.pool.repositories[0].add_package(Package('click', '8.1.4'))

    installer = Installers(project.workspace(root), NullIO(), NullEnv())
    assert installer.root(locked=False).lock().run() == 0
    assert installer.locker.locked_repository().search('click') == [
        Package('click', '8.1.4')
    ]


def test_project_installer(project: ProjectFactory):
    root = project(workspace_root=True)
    project.packages(
        Package('click', '8.0.9'),
        Package('click', '8.1.2')
    )

    p1 = utils.add(project('p1'), 'click=^8')
    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.1.2')
    ]

    utils.add(project('p2'), 'click<8.1')

    installer = Installers(project.workspace(root), NullIO(), NullEnv())
    assert installer.root(locked=True).lock().run() == 0

    assert installer.project(p1).lock().run() == 0
    assert p1.locker.locked_repository().search('click') == [
        Package('click', '8.0.9')
    ]
    