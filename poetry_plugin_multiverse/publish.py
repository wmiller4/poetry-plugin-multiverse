from typing import Iterable, Optional
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.path_dependency import PathDependency
from poetry.poetry import Poetry


class PublishedDependencies:
    def __init__(self, projects: Iterable[Poetry]) -> None:
        self.projects = {
            project.pyproject_path.parent.resolve(): project
            for project in projects
        }

    def __call__(self, dep: Dependency) -> Optional[Dependency]:
        if isinstance(dep, PathDependency):
            if project := self.projects.get(dep.full_path):
                return Dependency(
                    dep.name,
                    f'^{project.package.version}',
                    optional=dep.is_optional(),
                    groups=dep.groups,
                    extras=dep.extras
                )
        return None
    
    def patch_project(self, poetry: Poetry):
        for group_name in poetry.package.dependency_group_names(True):
            group = poetry.package.dependency_group(group_name)
            for index, dep in enumerate(group.dependencies):
                if published := self(dep):
                    group.dependencies[index] = published
