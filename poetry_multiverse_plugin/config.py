from typing import Any, List, Optional, TypedDict
from poetry.poetry import Poetry

def resolve(doc: Any, *path: str) -> Optional[Any]:
    if not path:
        return doc
    if not isinstance(doc, dict):
        return None
    return resolve(doc.get(path[0]), *path[1:])


class WorkspaceConfig(TypedDict, total=False):
    root: bool
    projects: List[str]


def parse_config(poetry: Poetry) -> WorkspaceConfig:
    return WorkspaceConfig(
        resolve(poetry.pyproject.data.unwrap(), 'tool', 'multiverse') or {}
    )
