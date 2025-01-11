from dataclasses import dataclass, field
import os
from typing import Iterable, Mapping, Optional

from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories.repository_pool import RepositoryPool

from poetry_multiverse_plugin.config import WorkspaceConfiguration
from poetry_multiverse_plugin.dependencies import Dependencies
from poetry_multiverse_plugin.packages import Packages
from poetry_multiverse_plugin.root import root_project


@dataclass
class Workspace:
    config: WorkspaceConfiguration
    context: Poetry
    disable_cache: bool = field(kw_only=True, default=False)
    pool: Optional[RepositoryPool] = field(kw_only=True, default=None)

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
            path=self.config.root,
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
