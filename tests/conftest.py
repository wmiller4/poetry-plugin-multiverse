from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from poetry.poetry import Poetry
import pytest
from poetry_multiverse_plugin.workspace import Workspace
from tests import utils


@dataclass
class ProjectFactory:
    tmp_path: Path

    def __call__(
            self,
            path: Optional[str] = None, *,
            workspace_root: bool = False,
            dependencies: Optional[list[str]] = None
    ) -> Poetry:
        return utils.project(
            (self.tmp_path / (path or '.')).resolve(),
            workspace_root=workspace_root,
            dependencies=dependencies
        )
    
    def workspace(self, poetry: Optional[Poetry] = None) -> Workspace:
        workspace = Workspace.create(poetry or self(workspace_root=True)) 
        assert workspace is not None
        return workspace


@pytest.fixture
def project(tmp_path: Path) -> ProjectFactory:
    return ProjectFactory(tmp_path)