from cleo.io.io import IO
from poetry.console.commands.command import Command

from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.workspace import Workspace


class PostLockHook(Hook):
    command_names = { 'add', 'lock', 'remove', 'update' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if workspace.config.get('lock') is True:
            command.call('workspace lock', '--no-update')
