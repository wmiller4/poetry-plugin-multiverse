from cleo.io.io import IO
from poetry.console.commands.command import Command

from poetry_multiverse_plugin.hooks.hook import Hook
from poetry_multiverse_plugin.publish import PublishedDependencies
from poetry_multiverse_plugin.workspace import Workspace


class PreBuildHook(Hook):
    command_names = { 'build' }

    def run(self, workspace: Workspace, command: Command, io: IO):
        if workspace.config.hooks_enabled('build'):
            PublishedDependencies(workspace.projects).patch_project(command.poetry)
