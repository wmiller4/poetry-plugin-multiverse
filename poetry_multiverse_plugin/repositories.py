from typing import List, Optional

from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.core.packages.package import Package
from poetry.installation.installer import Installer
from poetry.poetry import Poetry
from poetry.repositories.repository_pool import Priority, RepositoryPool
from poetry.utils.env import Env


def locked_pool(packages: List[Package]) -> RepositoryPool:
    return RepositoryPool.from_packages(packages, None)


def project_pool(*projects: Poetry, locked: Optional[Poetry]) -> RepositoryPool:
    min_priority = Priority.SECONDARY if locked else Priority.DEFAULT
    pool = RepositoryPool([locked.locker.locked_repository()] if locked else [])

    for poetry in projects:
        for repo in poetry.pool.all_repositories:
            priority = max(poetry.pool.get_priority(repo.name), min_priority)
            if not pool.has_repository(repo.name):
                pool.add_repository(repo, priority=priority)

    return pool


def create_installer(
    project: Poetry, 
    pool: RepositoryPool, *,
    env: Env,
    io: Optional[IO] = None
) -> Installer:
    return Installer(
        io or NullIO(),
        env,
        project.package,
        project.locker,
        pool,
        project.config,
        disable_cache=project.disable_cache
    )


def lock(project: Poetry, pool: RepositoryPool, *, env: Env) -> int:
    return create_installer(project, pool, env=env).lock().run()
