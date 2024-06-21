from dataclasses import dataclass
from poetry.factory import Factory
from poetry.poetry import Poetry
from typing import Any, Iterable, Optional

from poetry_multiverse_plugin.dependencies import Dependencies
from poetry_multiverse_plugin.packages import Packages


def resolve(doc: Any, *path: str) -> Optional[Any]:
    if not path:
        return doc
    if not isinstance(doc, dict):
        return None
    return resolve(doc.get(path[0]), *path[1:])


def workspace_root(poetry: Poetry) -> Optional[Poetry]:
    if resolve(poetry.pyproject.data.unwrap(), 'tool', 'multiverse', 'root') is True:
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
    def projects(self) -> Iterable[Poetry]:
        for pyproject in self.root.pyproject_path.parent.rglob('pyproject.toml'):
            if pyproject == self.root.pyproject_path:
                continue
            try:
                yield Factory().create_poetry(
                    pyproject.parent,
                    disable_cache=self.root.disable_cache
                )
            except RuntimeError:
                print(f'Skipping pyproject.toml {pyproject}')
    
    @property
    def dependencies(self) -> Dependencies:
        return Dependencies.from_projects(self.root, *self.projects)
    
    @property
    def packages(self) -> Packages:
        return Packages.from_projects(self.root, *self.projects)
