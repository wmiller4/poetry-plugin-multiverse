from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Callable, Dict, Iterable, Optional, TypeVar
from cleo.io.io import IO
from cleo.io.outputs.section_output import SectionOutput
from poetry.poetry import Poetry


ResultT = TypeVar('ResultT')


@dataclass
class Action:
    section: SectionOutput
    action: str
    name: str

    def update(self, status: str, *, color: str):
        self.section.overwrite(' '.join([
            f'  <fg={color};options=bold>-</>',
            self.action,
            f'<fg=cyan>{self.name}</>',
            f'(<fg={color}>{status}</>)'
        ]))


class WorkspaceStatus:
    def __init__(self, io: IO, projects: Iterable[Poetry], q: Queue[Optional[Callable[[], None]]]) -> None:
        self.q = q
        self.sections: Dict[Path, Action] = {
            project.pyproject_path: Action(io.section(), 'Updating', project.package.name)
            for project in sorted(projects, key=lambda p: p.package.name)
        }
        for project in projects:
            self.update(project, 'Pending', color='blue')
    
    def update(self, project: Poetry, status: str, *, color: str = 'blue'):
        self.q.put(lambda: self.sections[project.pyproject_path].update(status, color=color))
    
    def complete(self, project: Poetry, result: Future[int]) -> Optional[int]:
        assert result.done()
        if result.cancelled():
            self.update(project, 'Canceled', color='gray')
        elif result.exception():
            self.update(project, 'Error', color='red')
        else:
            return_code = result.result()
            if return_code:
                self.update(project, 'Failed', color='red')
            else:
                self.update(project, 'Done', color='green')
            return return_code
        return None
