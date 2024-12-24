from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Iterable, Optional

from poetry.core.pyproject.exceptions import PyProjectException
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories.repository_pool import RepositoryPool

from poetry_multiverse_plugin.config import WorkspaceConfig, parse_config
from poetry_multiverse_plugin.dependencies import Dependencies
from poetry_multiverse_plugin.packages import Packages
from poetry_multiverse_plugin.root import root_project


def workspace_root(poetry: Poetry) -> Optional[Poetry]:
    if parse_config(poetry).get('root') is True:
        return poetry
    try:
        parent_project = Factory().create_poetry(
            poetry.pyproject_path.resolve().parent.parent,
            disable_cache=poetry.disable_cache
        )
        return workspace_root(parent_project)
    except (PyProjectException, RuntimeError):
        return None


@dataclass
class Workspace:
    path: Path
    config: WorkspaceConfig
    disable_cache: bool = field(kw_only=True, default=False)
    pool: Optional[RepositoryPool] = field(kw_only=True, default=None)

    @staticmethod
    def create(poetry: Poetry, *, pool: Optional[RepositoryPool] = None) -> Optional['Workspace']:
        if root := workspace_root(poetry):
            return Workspace(
                root.pyproject_path.parent,
                parse_config(root),
                disable_cache=poetry.disable_cache,
                pool=pool
            )
        return None
    
    @property
    def root(self) -> Poetry:
        project = root_project(
            *self.projects,
            path=self.path,
            context=Factory().create_poetry(self.path, disable_cache=self.disable_cache)
        )
        if pool := self.pool:
            project.set_pool(pool)
        return project
    
    @property
    def project_dirs(self) -> Iterable[Path]:
        project_dirs = self.config.get('projects', ['**'])
        for dir_glob in project_dirs:
            toml_glob = f'{dir_glob.rstrip(os.sep)}{os.sep}pyproject.toml'
            for pyproject in self.path.glob(toml_glob):
                yield pyproject.parent.resolve(True)
    
    @property
    def projects(self) -> Iterable[Poetry]:
        for project in self.project_dirs:
            if project == self.path:
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
