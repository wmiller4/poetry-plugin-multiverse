from contextlib import contextmanager
from typing import Iterator
from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.console.commands.command import Command
from poetry.console.commands.installer_command import InstallerCommand
from poetry.console.commands.lock import LockCommand
from poetry.poetry import Poetry

from poetry_multiverse_plugin.cli.progress import progress
from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.repositories import create_installer, lock, locked_pool, project_pool, workspace_pool
from poetry_multiverse_plugin.workspace import Workspace


@contextmanager
def poetry_target(poetry: Poetry, command: Command) -> Iterator[Command]:
    old_poetry = command.poetry
    try:
        command.set_poetry(poetry)
        yield command
    finally:
        command.set_poetry(old_poetry)


@contextmanager
def no_install(io: IO) -> Iterator[IO]:
    if io.input.has_option('lock'):
        old_value = io.input.option('lock')
        try:
            io.input.set_option('lock', True)
            yield io
        finally:
            io.input.set_option('lock', old_value)
    else:
        yield io


class PreLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if not workspace.config.hooks_enabled('lock'):
            return
        if not isinstance(command, InstallerCommand):
            return

        root = workspace.root
        with progress(io, 'Preparing workspace...'):
            lock(root, locked_pool(list(workspace.packages)))

        root.set_pool(workspace_pool(*workspace.projects, locked=root))
        command.set_installer(create_installer(
            root,
            root.pool
        ))
        with poetry_target(root, command) as cmd:
            with no_install(io) as lock_io:
                cmd.execute(NullIO(lock_io.input))

        sources = [] if isinstance(command, LockCommand) else [command.poetry]
        command.poetry.set_pool(project_pool(*sources, locked=root))
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
