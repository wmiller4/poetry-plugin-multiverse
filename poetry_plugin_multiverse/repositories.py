from contextlib import contextmanager
from typing import Iterator, List, Optional

from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.core.packages.package import Package
from poetry.installation.installer import Installer
from poetry.poetry import Poetry
from poetry.repositories.repository_pool import Priority, RepositoryPool
from poetry.utils.env import Env

from poetry_plugin_multiverse.root import root_env
from poetry_plugin_multiverse.utils import Singleton


def locked_pool(packages: List[Package]) -> RepositoryPool:
    return RepositoryPool.from_packages(packages, None)


def workspace_pool(*projects: Poetry, locked: Optional[Poetry] = None, priority: Optional[Priority] = None) -> RepositoryPool:
    pool = RepositoryPool([locked.locker.locked_repository()] if locked else [])

    min_priority = priority or (Priority.SECONDARY if locked else Priority.DEFAULT)
    for poetry in projects:
        for repo in poetry.pool.all_repositories:
            priority = max(poetry.pool.get_priority(repo.name), min_priority)
            if not pool.has_repository(repo.name):
                pool.add_repository(repo, priority=priority)

    return pool


def create_installer(
    project: Poetry, 
    pool: RepositoryPool, *,
    env: Optional[Env] = None,
    io: Optional[IO] = None
) -> Installer:
    return Installer(
        io or NullIO(),
        env or root_env(project),
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
