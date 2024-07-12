from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator
from cleo.io.io import IO
from cleo.io.outputs.section_output import SectionOutput
from poetry.puzzle.provider import Indicator


@contextmanager
def progress(io: IO, message: str) -> Iterator[None]:
    if not io.output.is_decorated() or io.is_debug():
        io.write_line(message)
        yield
    else:
        indicator = Indicator(
            io, '{message}{context}<debug>({elapsed:2s})</debug>'
        )

        with indicator.auto(
            f'<info>{message}</info>',
            f'<info>{message}</info>'
        ):
            yield


UpdateStatus = Callable[[str], None]


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


@contextmanager
def status(io: IO, action: str, name: str) -> Iterator[UpdateStatus]:
    if not io.output.is_decorated() or io.is_debug():
        yield lambda status: io.write_line(status)
    else:
        action_output = Action(io.section(), action, name)
        action_output.update('Pending', color='blue')
        try:
            yield lambda status: action_output.update(status, color='blue')
        except Exception as err:
            action_output.update('Failed', color='red')
            raise err
        action_output.update('Done', color='green')
