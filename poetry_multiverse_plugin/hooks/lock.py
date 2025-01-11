from contextlib import contextmanager
from typing import Iterator
from cleo.io.io import IO
from poetry.console.commands.command import Command
from poetry.console.commands.installer_command import InstallerCommand
from poetry.poetry import Poetry

from poetry_multiverse_plugin.cli.progress import progress
from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.repositories import create_installer, lock, locked_pool, project_pool
from poetry_multiverse_plugin.workspace import Workspace


@contextmanager
def poetry_target(poetry: Poetry, command: Command) -> Iterator[Command]:
    old_poetry = command.poetry
    try:
        command.set_poetry(poetry)
        yield command
    finally:
        command.set_poetry(old_poetry)


class PreLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if not workspace.config.hooks_enabled('lock'):
            return
        if not isinstance(command, InstallerCommand):
            return

        root = workspace.root
        with progress(io, 'Preparing workspace...'):
            lock(root, locked_pool(list(workspace.packages)), env=command.env)
            with poetry_target(root, command) as cmd:
                cmd.run(io)
        
        command.poetry.set_pool(project_pool(locked=root))
        command.set_installer(create_installer(
            command.poetry,
            command.poetry.pool,
            env=command.env,
            io=io
        ))


class PostLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if workspace.config.hooks_enabled('lock'):
            command.call('workspace lock', '--no-update')
