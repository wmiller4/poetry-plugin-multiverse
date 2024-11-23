from pathlib import Path

from cleo.testers.application_tester import ApplicationTester

from tests.conftest import ProjectFactory
from tests.utils import MockApplication


def test_no_workspace(project: ProjectFactory):
    tester = ApplicationTester(MockApplication(project()))
    assert tester.execute('workspace info') == 1
    assert 'workspace root' in tester.io.fetch_error()


def test_workspace(project: ProjectFactory):
    root = project(workspace_root=True)
    p1 = project('p1')
    tester = ApplicationTester(MockApplication(root))
    assert tester.execute('workspace info') == 0
    assert p1.package.name in tester.io.fetch_output()


def test_non_poetry_parent(project: ProjectFactory, tmp_path: Path):
    (tmp_path / 'pyproject.toml').touch()
    tester = ApplicationTester(MockApplication(project('p1')))
    assert tester.execute('lock') == 0
    assert 'Multiverse' in tester.io.fetch_error()
