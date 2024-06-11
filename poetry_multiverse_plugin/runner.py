from collections import defaultdict
from typing import Iterable
from poetry.poetry import Poetry


ProjectGraph = dict[Poetry, set[Poetry]]


def project_graph(projects: Iterable[Poetry]) -> ProjectGraph:
    graph: dict[Poetry, set[Poetry]] = defaultdict(set)
    lookup = dict((p.package.complete_name, p) for p in projects)
    for project in lookup.values():
        for dep in project.package.all_requires:
            if poetry := lookup.get(dep.complete_name):
                graph[project].add(poetry)
    return graph


def has_cycle(graph: ProjectGraph) -> bool:
    if not graph:
        return True
    
    runnable = [project for project, deps in graph.items() if not deps]
    if not runnable:
        return False
    
    return has_cycle(dict(
        (project, set(dep for dep in deps if dep not in runnable))
        for project, deps in graph.items() if deps
    ))
