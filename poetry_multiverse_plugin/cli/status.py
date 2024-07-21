from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, TypeVar
from cleo.io.outputs.section_output import SectionOutput
from poetry.poetry import Poetry


ResultT = TypeVar('ResultT')


@dataclass
class OutputQueue:
    submit: Callable[[Callable[[], None]], None]
    section: Callable[[], SectionOutput]


@dataclass
class StatusConfig:
    header: Optional[str]
    template: str

    @staticmethod
    def default_template(action: str) -> str:
        return ' '.join([
            '  <fg={color};options=bold>-</>',
            action,
            '<fg=cyan>{project}</>',
            '(<fg={color}>{status}</>)'
        ])


@dataclass
class StatusOutput:
    submit: Callable[[Callable[[], None]], None]
    summary_section: SectionOutput
    log_section: SectionOutput

    def summary(self, message: str):
        self.submit(lambda: self.summary_section.overwrite(message))

    def log(self, message: str):
        self.submit(lambda: self.log_section.write(message))


@dataclass
class ProjectStatus:
    writer: StatusOutput
    template: str
    name: str

    def log(self, message: str, *, error: bool = False):
        fmt = '<error>' if error else '<debug>'
        message = f'{fmt}[{self.name}]</> {message.rstrip()}'
        self.writer.log(message)

    def update(self, status: str, *, color: str = 'blue'):
        message = self.template.format(status=status, color=color, project=self.name)
        self.writer.summary(message)
    
    def complete(self, result: Future[int]) -> Optional[int]:
        assert result.done()
        if result.cancelled():
            self.update('Canceled', color='gray')
        elif result.exception():
            self.update('Error', color='red')
        else:
            code = result.result()
            if code != 0:
                self.update('Failed', color='red')
            else:
                self.update('Done', color='green')
            return code
        return None


class WorkspaceStatus:
    def __init__(self, output: OutputQueue, projects: Iterable[Poetry], config: StatusConfig) -> None:
        self.log_section = output.section()
        if config.header:
            self.header_section = output.section()
            self.header_section.overwrite(config.header)
        self.sections: Dict[Path, ProjectStatus] = {
            project.pyproject_path: ProjectStatus(
                StatusOutput(output.submit, output.section(), self.log_section),
                config.template,
                project.package.name
            )
            for project in sorted(projects, key=lambda p: p.package.name)
        }
        for action in self.sections.values():
            action.update('Pending', color='blue')
    
    def __call__(self, project: Poetry) -> ProjectStatus:
        return self.sections[project.pyproject_path]
