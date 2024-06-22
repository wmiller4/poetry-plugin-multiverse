from pathlib import Path
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from cleo.io.io import IO
from dataclasses import dataclass, field
from poetry.core.packages.project_package import ProjectPackage
from poetry.installation.installer import Installer
from poetry.poetry import Poetry
from poetry.packages.locker import Locker
from poetry.repositories.repository_pool import RepositoryPool
from poetry.utils.env import Env

from poetry_multiverse_plugin.workspace import Workspace


@dataclass
class Installers:
    workspace: Workspace
    io: IO
    env: Env
    lock_file: _TemporaryFileWrapper = field(default_factory=lambda: NamedTemporaryFile(suffix='.lock'))

    @property
    def locker(self) -> Locker:
        return Locker(Path(self.lock_file.name), {})

    def root(self, *, locked: bool) -> Installer:
        root = self.workspace.root
        aggregate_project = ProjectPackage(root.package.name, root.package.version)
        aggregate_project.python_versions = root.package.python_versions

        for dep in self.workspace.dependencies:
            aggregate_project.add_dependency(dep)

        return Installer(
            self.io,
            self.env,
            aggregate_project,
            self.locker,
            self.workspace.packages.repository_pool if locked else root.pool,
            root.config,
            disable_cache=root.disable_cache
        )
    
    def project(self, poetry: Poetry) -> Installer:
        root = self.workspace.root
        repository = self.locker.locked_repository()
        pool = RepositoryPool([repository])

        return Installer(
            self.io,
            self.env,
            poetry.package,
            poetry.locker,
            pool,
            poetry.config,
            disable_cache=root.disable_cache
        )
