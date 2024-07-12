from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Dict, Iterable
from cleo.helpers import option
from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.poetry import Poetry

from poetry_multiverse_plugin import cli
from poetry_multiverse_plugin.commands.workspace import WorkspaceCommand
from poetry_multiverse_plugin.installers import Installers
from poetry_multiverse_plugin.workspace import Workspace


class LockCommand(WorkspaceCommand):
    name = 'workspace lock'
    description = 'Compute dependencies for the multiverse workspace.'

    options = [
        option(
            "no-update", None, "Reuse packages in project lock files."
        )
    ]

    help = """
The <info>workspace lock</info> command updates the <comment>poetry.lock</>
file for each project in the workspace such that dependencies required by
multiple projects are locked to the same version.

<info>poetry workspace lock</info>
"""

    def handle_workspace(self, workspace: Workspace) -> int:
        installer = Installers(workspace, NullIO(), self.env)
        with cli.progress(self.io, 'Loading workspace...'):
            result = installer.root(locked=self.option('no-update', True)).lock().run()
            if result != 0:
                self.io.write_error_line('<error>Failed to lock workspace!</>')
                return result

        projects = sorted(workspace.projects, key=lambda p: p.package.name)
        status = WorkspaceStatus(self.io, projects)

        with ThreadPoolExecutor() as executor:
            jobs = {
                executor.submit(installer.project(project).lock().run): project
                for project in projects
            }
            for future in as_completed(jobs):
                result = max(result, future.result())
                status.complete(jobs[future], future)
        return result


class WorkspaceStatus:
    def __init__(self, io: IO, projects: Iterable[Poetry]) -> None:
        self.sections: Dict[Poetry, cli.Action] = {
            project: cli.Action(io.section(), 'Updating', project.package.name)
            for project in projects
        }
        for project in projects:
            self.sections[project].update('Pending', color='blue')
    
    def progress(self, project: Poetry, status: str):
        self.sections[project].update(status, color='blue')
    
    def complete(self, project: Poetry, result: Future):
        assert result.done()
        action = self.sections[project]
        if result.cancelled():
            action.update('Canceled', color='gray')
        elif result.exception():
            action.update('Failed', color='red')
        else:
            action.update('Done', color='green')
