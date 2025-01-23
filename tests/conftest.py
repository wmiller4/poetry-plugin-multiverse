from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Iterator, Mapping, Optional

from poetry.core.packages.package import Package
from poetry.poetry import Poetry
from poetry.repositories import Repository, RepositoryPool
import pytest

from poetry_multiverse_plugin.config import MultiverseToml, WorkspaceConfiguration
from poetry_multiverse_plugin.repositories import PoolFactory
from poetry_multiverse_plugin.workspace import Workspace
from tests import utils


@dataclass
class ProjectFactory:
    tmp_path: Path
    pool: RepositoryPool

    def __call__(self, path: Optional[str] = None) -> Poetry:
        return utils.project(
            (self.tmp_path / (path or '.')).resolve(),
            pool=self.pool
        )
    
    def packages(self, *packages: Package) -> None:
        repo = self.pool.repository('mock')
        for pkg in packages:
            repo.add_package(pkg)
    
    def workspace(
        self,
        context: Poetry, *,
        config: Optional[MultiverseToml] = None,
        env: Optional[Mapping[str, str]] = None
    ) -> Workspace:
        if config:
            (self.tmp_path / 'multiverse.toml').write_text('\n'.join(
                f'{key} = {json.dumps(value)}' for key, value in config.items()
            ))
        else:
            (self.tmp_path / 'multiverse.toml').touch()
        return Workspace(
            WorkspaceConfiguration(self.tmp_path, config or {}, env or {})
        )


@contextmanager
def working_dir(path: Path) -> Iterator[Path]:
    old_path = Path.cwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(old_path)


@pytest.fixture
def project(tmp_path: Path) -> Iterator[ProjectFactory]:
    with working_dir(tmp_path):
        with PoolFactory().override(RepositoryPool([Repository('mock')])) as pool:
            yield ProjectFactory(tmp_path, pool)