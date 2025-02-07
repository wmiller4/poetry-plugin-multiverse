from pathlib import Path

from poetry.config.config import Config
from poetry.core.constraints.version.parser import parse_single_constraint
from poetry.core.packages.project_package import ProjectPackage
from poetry.packages.locker import Locker
from poetry.poetry import Poetry
from poetry.factory import Factory

from poetry_plugin_multiverse.dependencies import Dependencies


def root_project(*projects: Poetry, path: Path) -> Poetry:
    aggregate_project = ProjectPackage('workspace', '0.0.0')
    local_config = {}

    py_versions = parse_single_constraint('*')
    for project in projects:
        py_versions = py_versions.intersect(project.package.python_constraint)
    aggregate_project.python_versions = str(py_versions)

    for dep in Dependencies.from_projects(*projects):
        aggregate_project.add_dependency(dep)

    pyproject = path / 'workspace.toml'
    pyproject.write_text(Factory.create_pyproject_from_package(aggregate_project).as_string())
    return Poetry(
        file=pyproject,
        local_config=local_config,
        package=aggregate_project,
        locker=Locker(path / 'workspace.lock', local_config),
        config=Config.create()
    )
