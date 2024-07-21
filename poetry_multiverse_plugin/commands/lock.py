from concurrent.futures import ThreadPoolExecutor, as_completed
from cleo.helpers import option
from cleo.io.null_io import NullIO
from poetry.poetry import Poetry

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
        return_code = 0

        with self.cli.progress('Locking workspace...'):
            return_code = installer.root(locked=self.option('no-update', True)).lock().run()
            if return_code != 0:
                self.io.write_error_line('<error>Failed to lock workspace!</>')
                return return_code

        with self.cli.status(None, 'Updating') as status:
            def run(project: Poetry) -> int:
                status(project).update('Locking...')
                return installer.project(project).lock().run()

            with ThreadPoolExecutor() as executor:
                jobs = {
                    executor.submit(lambda: run(project)): project
                    for project in workspace.projects
                }
                for future in as_completed(jobs):
                    project = jobs[future]
                    result = status(project).complete(future)
                    return_code = max(return_code, result if result is not None else 1)
        
        return return_code
