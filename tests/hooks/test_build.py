import pkginfo

from cleo.events.console_command_event import ConsoleCommandEvent
from poetry.console.commands.build import BuildCommand
from poetry.console.commands.version import VersionCommand
from poetry.core.constraints.version.version import Version
from poetry.core.packages.dependency import Dependency

from poetry_plugin_multiverse.hooks.build import PreBuildHook
from poetry_plugin_multiverse.hooks.hook import HookContext
from tests import utils
from tests.conftest import ProjectFactory
from tests.utils import command


def test_versions_disabled(project: ProjectFactory):
    p1 = project('p1')
    project.workspace(p1)
    version = command(p1, VersionCommand)
    assert version.execute('1.2.34') == 0

    p2 = utils.add(project('p2'), '../p1')
    build = command(p2, BuildCommand)

    context = HookContext.create(ConsoleCommandEvent(build.command, build.io))
    assert context is not None
    context.run(PreBuildHook)
    assert build.execute() == 0

    packaged_wheel = list((p2.pyproject_path.parent / 'dist').glob('*.whl'))[0]
    metadata = pkginfo.get_metadata(str(packaged_wheel))
    assert metadata is not None
    dependency = Dependency.create_from_pep_508(metadata.requires_dist[0])
    assert dependency.is_directory()


def test_run_hook(project: ProjectFactory):
    p1 = project('p1')
    project.workspace(p1, config={ 'hooks': ['build'] })
    version = command(p1, VersionCommand)
    assert version.execute('1.2.34') == 0

    p2 = utils.add(project('p2'), '../p1')
    build = command(p2, BuildCommand)

    context = HookContext.create(ConsoleCommandEvent(build.command, build.io))
    assert context is not None
    context.run(PreBuildHook)
    assert build.execute() == 0

    packaged_wheel = list((p2.pyproject_path.parent / 'dist').glob('*.whl'))[0]
    metadata = pkginfo.get_metadata(str(packaged_wheel))
    assert metadata is not None
    dependency = Dependency.create_from_pep_508(metadata.requires_dist[0])
    assert dependency.name == p1.package.name
    assert dependency.constraint.allows(Version.from_parts(1, 2, 34)) is True
    assert dependency.constraint.allows(Version.from_parts(1, 2, 33)) is False
