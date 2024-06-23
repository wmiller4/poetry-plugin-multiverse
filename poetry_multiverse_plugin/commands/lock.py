from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
from cleo.helpers import option
from cleo.io.null_io import NullIO
from cleo.io.outputs.section_output import SectionOutput

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
        installer = Installers(workspace, self.io, self.env)
        result = installer.root(locked=self.option('no-update', True)).lock().run()
        if result != 0:
            self.io.write_error_line('<error>Failed to lock workspace!</>')
            return result

        installer.io = NullIO()
        projects = sorted(workspace.projects, key=lambda p: p.package.name)
        sections: Dict[str, SectionOutput] = defaultdict(self.io.section)
        for project in projects:
            sections[project.package.name].overwrite(f'- Locking <info>{project.package.name}</>')
        
        with ThreadPoolExecutor() as executor:
            jobs = {
                executor.submit(installer.project(project).lock().run): project.package.name
                for project in projects
            }
            for future in as_completed(jobs):
                result = max(result, future.result())
                sections[jobs[future]].overwrite(f'- Locking <comment>{jobs[future]}</>')
        return result
