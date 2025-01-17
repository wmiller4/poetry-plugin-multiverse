import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Mapping, Optional

from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories.repository_pool import RepositoryPool

from poetry_multiverse_plugin.config import WorkspaceConfiguration
from poetry_multiverse_plugin.dependencies import Dependencies
from poetry_multiverse_plugin.packages import Packages
from poetry_multiverse_plugin.root import root_project


class Workspace:
    def __init__(
        self,
        config: WorkspaceConfiguration,
        context: Poetry, *,
        disable_cache: bool = False,
        pool: Optional[RepositoryPool] = None
    ) -> None:
        self.config = config
        self.context = context
        self.disable_cache = disable_cache
        self.pool = pool
        self.root_project = TemporaryDirectory()

    @staticmethod
    def create(
        poetry: Poetry, *,
        pool: Optional[RepositoryPool] = None, 
        env: Mapping[str, str] = os.environ
    ) -> Optional['Workspace']:
        if config := WorkspaceConfiguration.find(poetry.pyproject_path.parent, env):
            if poetry.pyproject_path.parent in config.project_dirs:
                return Workspace(
                    config,
                    poetry,
                    disable_cache=poetry.disable_cache,
                    pool=pool
                )
            return None
    
    @property
    def root(self) -> Poetry:
        project = root_project(
            *self.projects,
            path=Path(self.root_project.name),
            context=self.context
        )
        if pool := self.pool:
            project.set_pool(pool)
        return project
    
    @property
    def projects(self) -> Iterable[Poetry]:
        for project in self.config.project_dirs:
            if project == self.config.root:
                continue
            try:
                project = Factory().create_poetry(
                    project,
                    disable_cache=self.disable_cache
                )
                if pool := self.pool:
                    project.set_pool(pool)
                yield project
            except RuntimeError:
                print(f'Skipping pyproject.toml {project}')
    
    @property
    def dependencies(self) -> Dependencies:
        return Dependencies.from_projects(*self.projects)
    
    @property
    def packages(self) -> Packages:
        return Packages.from_projects(*self.projects)
