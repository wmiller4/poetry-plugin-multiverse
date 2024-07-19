import asyncio
from asyncio import create_subprocess_exec, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import List
from cleo.helpers import argument, option
from poetry.poetry import Poetry

from poetry_multiverse_plugin.commands.workspace import WorkspaceCommand
from poetry_multiverse_plugin.workspace import Workspace


class RunCommand(WorkspaceCommand):
    name = 'workspace run'
    description = 'Execute a command in every project in the workspace.'

    arguments = [
        argument(
            'program',
            description="The command to run in each project's environment",
            multiple=True
        )
    ]

    options = [
        option(
            'parallel', 'p',
            description='The maximum number of processes to run in parallel',
            flag=False
        )
    ]

    def handle_workspace(self, workspace: Workspace) -> int:
        command: List[str] = self.argument('program')
        parallel = self.option('parallel')

        projects = sorted(workspace.projects, key=lambda p: p.package.name)

        with self.cli.status() as status:
            async def run(project: Poetry) -> int:
                status.update(project, 'Running...')
                proc = await create_subprocess_exec(
                    *command,
                    cwd=project.pyproject_path.parent,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return await proc.wait()

            with ThreadPoolExecutor(int(parallel) if parallel else None) as executor:
                jobs = {
                    executor.submit(partial(lambda p: asyncio.run(run(p)), project)): project
                    for project in reversed(projects)
                }

                return_code = 0

                for future in as_completed(jobs):
                    project = jobs[future]
                    result = status.complete(project, future)
                    return_code = max(return_code, result if result is not None else 1)
            
                return return_code
