from contextlib import contextmanager
from typing import Iterator
from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.console.commands.command import Command
from poetry.console.commands.installer_command import InstallerCommand

from poetry_multiverse_plugin.cli.progress import progress
from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.installers import Installers
from poetry_multiverse_plugin.workspace import Workspace


@contextmanager
def workspace_target(workspace: Workspace, command: Command) -> Iterator[Command]:
    old_poetry = command.poetry
    try:
        command.set_poetry(workspace.root)
        yield command
    finally:
        command.set_poetry(old_poetry)


class PreLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if workspace.config.get('lock') is not True:
            return
        if not isinstance(command, InstallerCommand):
            return

        installer = Installers(workspace, NullIO(), command.env)
        with progress(io, 'Preparing workspace...'):
            installer.root(locked=True).lock().run()
            with workspace_target(workspace, command) as cmd:
                cmd.run(io)

        installer.io = io
        command.set_installer(installer.project(command.poetry))
        command.poetry.set_pool(installer.repository_pool(command.poetry))


class PostLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if workspace.config.get('lock') is True:
            command.call('workspace lock', '--no-update')
