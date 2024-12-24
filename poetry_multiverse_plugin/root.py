from pathlib import Path

from poetry.core.constraints.version.parser import parse_single_constraint
from poetry.core.packages.project_package import ProjectPackage
from poetry.packages.locker import Locker
from poetry.poetry import Poetry

from poetry_multiverse_plugin.dependencies import Dependencies


def root_project(*projects: Poetry, path: Path, context: Poetry) -> Poetry:
    aggregate_project = ProjectPackage('workspace', '0.0.0')

    py_versions = parse_single_constraint('*')
    for project in projects:
        py_versions = py_versions.intersect(project.package.python_constraint)
    aggregate_project.python_versions = str(py_versions)

    for dep in Dependencies.from_projects(*projects):
        aggregate_project.add_dependency(dep)

    return Poetry(
        file=path / 'multiverse.toml',
        local_config=context.local_config,
        package=aggregate_project,
        locker=Locker(path / 'multiverse.lock', context.local_config),
        config=context.config,
        disable_cache=context.disable_cache
    )
