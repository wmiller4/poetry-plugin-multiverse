from dataclasses import dataclass
import os
from pathlib import Path
from poetry.factory import Factory
from poetry.poetry import Poetry
from typing import Iterable, Optional

from poetry_multiverse_plugin.config import WorkspaceConfig, parse_config
from poetry_multiverse_plugin.dependencies import Dependencies
from poetry_multiverse_plugin.packages import Packages


def workspace_root(poetry: Poetry) -> Optional[Poetry]:
    if parse_config(poetry).get('root') is True:
        return poetry
    try:
        parent_project = Factory().create_poetry(
            poetry.pyproject_path.resolve().parent.parent,
            disable_cache=poetry.disable_cache
        )
        return workspace_root(parent_project)
    except RuntimeError:
        return None


@dataclass
class Workspace:
    root: Poetry

    @staticmethod
    def create(poetry: Poetry) -> Optional['Workspace']:
        root = workspace_root(poetry)
        return Workspace(root) if root else None
    
    @property
    def config(self) -> WorkspaceConfig:
        return parse_config(self.root)
    
    @property
    def project_dirs(self) -> Iterable[Path]:
        project_dirs = self.config.get('projects', ['**'])
        for dir_glob in project_dirs:
            toml_glob = f'{dir_glob.rstrip(os.sep)}{os.sep}pyproject.toml'
            for pyproject in self.root.pyproject_path.parent.glob(toml_glob):
                yield pyproject.parent.resolve(True)
    
    @property
    def projects(self) -> Iterable[Poetry]:
        for project in self.project_dirs:
            if project == self.root.pyproject_path.parent:
                continue
            try:
                yield Factory().create_poetry(
                    project,
                    disable_cache=self.root.disable_cache
                )
            except RuntimeError:
                print(f'Skipping pyproject.toml {project}')
    
    @property
    def dependencies(self) -> Dependencies:
        return Dependencies.from_projects(self.root, *self.projects)
    
    @property
    def packages(self) -> Packages:
        return Packages.from_projects(self.root, *self.projects)
