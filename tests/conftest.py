from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from poetry.core.packages.package import Package
from poetry.poetry import Poetry
from poetry.repositories import Repository, RepositoryPool
import pytest
from poetry_multiverse_plugin.workspace import Workspace
from tests import utils


@dataclass
class ProjectFactory:
    tmp_path: Path
    pool: RepositoryPool = field(default_factory=lambda: RepositoryPool([Repository('mock')]))

    def __call__(
            self,
            path: Optional[str] = None, *,
            workspace_root: bool = False
    ) -> Poetry:
        return utils.project(
            (self.tmp_path / (path or '.')).resolve(),
            workspace_root=workspace_root,
            pool=self.pool
        )
    
    def packages(self, *packages: Package) -> None:
        repo = self.pool.repository('mock')
        for pkg in packages:
            repo.add_package(pkg)
    
    def workspace(self, poetry: Optional[Poetry] = None) -> Workspace:
        workspace = Workspace.create(poetry or self(workspace_root=True)) 
        assert workspace is not None
        return workspace


@pytest.fixture
def project(tmp_path: Path) -> ProjectFactory:
    return ProjectFactory(tmp_path)