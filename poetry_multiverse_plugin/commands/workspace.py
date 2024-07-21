from contextlib import _GeneratorContextManager, contextmanager
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Callable, Iterator, Optional
from cleo.io.io import IO
from poetry.console.commands.installer_command import InstallerCommand

from poetry_multiverse_plugin.cli.progress import progress
from poetry_multiverse_plugin.cli.status import OutputQueue, StatusConfig, WorkspaceStatus
from poetry_multiverse_plugin.workspace import Workspace


@dataclass
class CliUtils:
    workspace: Workspace
    io: IO

    def progress(self, message: str) -> _GeneratorContextManager[None]:
        return progress(self.io, message)
    
    @contextmanager
    def status(self, header: Optional[str], action: str) -> Iterator[WorkspaceStatus]:
        q: Queue[Optional[Callable[[], None]]] = Queue()

        def process():
            while task := q.get():
                task()

        io_thread = Thread(target=process)
        try:
            io_thread.start()
            yield WorkspaceStatus(
                OutputQueue(q.put, self.io.section),
                self.workspace.projects,
                StatusConfig(header, StatusConfig.default_template(action))
            )
        finally:
            q.put(None)
            io_thread.join()


class WorkspaceCommand(InstallerCommand):
    @property
    def cli(self) -> CliUtils:
        workspace = Workspace.create(self.poetry)
        assert workspace is not None
        return CliUtils(workspace, self.io)

    def handle_workspace(self, workspace: Workspace) -> int:
        raise NotImplementedError
    
    def handle(self) -> int:
        workspace = Workspace.create(self.poetry)
        if not workspace:
            self.line_error('Unable to locate workspace root')
            return 1
        return self.handle_workspace(workspace)
