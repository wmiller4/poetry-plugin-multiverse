from contextlib import contextmanager
from typing import Iterator, List, Optional

from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.core.packages.package import Package
from poetry.core.packages.utils.link import Link
from poetry.installation.installer import Installer
from poetry.repositories.lockfile_repository import LockfileRepository
from poetry.poetry import Poetry
from poetry.repositories.repository import Repository
from poetry.repositories.repository_pool import Priority, RepositoryPool
from poetry.utils.env import Env
from poetry.utils.env.null_env import NullEnv

from poetry_multiverse_plugin.utils import Singleton


class LockedRepository(Repository):
    def __init__(self, parent: LockfileRepository, pool: RepositoryPool) -> None:
        super().__init__(parent.name, parent.packages)
        self.pool = pool
    
    def find_links_for_package(self, package: Package) -> List[Link]:
        if links := super().find_links_for_package(package):
            return links
        for source in self.pool.repositories:
            if links := source.find_links_for_package(package):
                return links
        return []


def locked_pool(packages: List[Package]) -> RepositoryPool:
    return RepositoryPool.from_packages(packages, None)


def workspace_pool(*projects: Poetry, locked: Optional[Poetry] = None) -> RepositoryPool:
    pool = RepositoryPool([locked.locker.locked_repository()] if locked else [])

    min_priority = Priority.SECONDARY if locked else Priority.DEFAULT
    for poetry in projects:
        for repo in poetry.pool.all_repositories:
            priority = max(poetry.pool.get_priority(repo.name), min_priority)
            if not pool.has_repository(repo.name):
                pool.add_repository(repo, priority=priority)

    return pool


def project_pool(*projects: Poetry, locked: Poetry) -> RepositoryPool:
    return RepositoryPool([
        LockedRepository(locked.locker.locked_repository(), workspace_pool(*projects))
    ])


def create_installer(
    project: Poetry, 
    pool: RepositoryPool, *,
    env: Optional[Env] = None,
    io: Optional[IO] = None
) -> Installer:
    return Installer(
        io or NullIO(),
        env or NullEnv(),
        project.package,
        project.locker,
        pool,
        project.config,
        disable_cache=project.disable_cache
    )


def lock(project: Poetry, pool: RepositoryPool, *, env: Optional[Env] = None) -> int:
    return create_installer(project, pool, env=env).lock().run()


class PoolFactory(metaclass=Singleton):
    def __init__(self, pool: Optional[RepositoryPool] = None):
        self._pool = pool

    def get(self) -> Optional[RepositoryPool]:
        return self._pool
    
    @contextmanager
    def override(self, pool: RepositoryPool) -> Iterator[RepositoryPool]:
        old_pool = self._pool
        try:
            self._pool = pool
            yield pool
        finally:
            self._pool = old_pool
