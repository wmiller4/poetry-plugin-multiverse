from pathlib import Path

from fastjsonschema import JsonSchemaException
import pytest

from poetry_multiverse_plugin.config import WorkspaceConfiguration


def make_project(path: Path):
    path.mkdir(parents=True)
    (path / 'pyproject.toml').touch()


def test_no_workspace(tmp_path: Path):
    assert WorkspaceConfiguration.find(tmp_path) is None


def test_self_workspace(tmp_path: Path):
    (tmp_path / 'multiverse.toml').touch()
    config = WorkspaceConfiguration.find(tmp_path)
    assert config is not None
    assert config.root == tmp_path


def test_parent_workspace(tmp_path: Path):
    (tmp_path / 'multiverse.toml').touch()
    config = WorkspaceConfiguration.find(tmp_path / 'child' / 'directory')
    assert config is not None
    assert config.root == tmp_path


def test_validate_members(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('members = "*"')
    with pytest.raises(JsonSchemaException):
        WorkspaceConfiguration.find(tmp_path / 'child' / 'directory')


def test_validate_hooks(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('hooks = ["unknown hook"]')
    with pytest.raises(JsonSchemaException):
        WorkspaceConfiguration.find(tmp_path / 'child' / 'directory')


def test_projects_default(tmp_path: Path):
    (tmp_path / 'multiverse.toml').touch()
    make_project(tmp_path / 'project')
    make_project(tmp_path / 'nested' / 'project2')

    config = WorkspaceConfiguration.find(tmp_path)
    assert config is not None
    assert set(config.project_dirs) == {
        tmp_path / 'project',
        tmp_path / 'nested' / 'project2'
    }


def test_projects_members(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('members = ["*"]')
    make_project(tmp_path / 'project')
    make_project(tmp_path / 'nested' / 'project2')

    config = WorkspaceConfiguration.find(tmp_path)
    assert config is not None
    assert set(config.project_dirs) == {
        tmp_path / 'project'
    }


def test_projects_excludes(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('exclude = ["nested/*"]')
    make_project(tmp_path / 'project')
    make_project(tmp_path / 'nested' / 'project2')

    config = WorkspaceConfiguration.find(tmp_path)
    assert config is not None
    assert set(config.project_dirs) == {
        tmp_path / 'project'
    }


def test_hooks_enabled(tmp_path: Path):
    (tmp_path / 'multiverse.toml').touch()
    config = WorkspaceConfiguration.find(tmp_path, {})
    assert config is not None
    assert config.hooks_enabled() is True


def test_hooks_disabled(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('hooks = ["build"]')
    config = WorkspaceConfiguration.find(tmp_path, {
        'MULTIVERSE_DISABLE_HOOKS': '1'
    })
    assert config is not None
    assert config.hooks_enabled() is False
    assert config.hooks_enabled('build') is False


def test_hook_enabled(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('hooks = ["build"]')
    config = WorkspaceConfiguration.find(tmp_path, {})
    assert config is not None
    assert config.hooks_enabled('build') is True
    assert config.hooks_enabled('lock') is False
    assert config.hooks_enabled('build', 'lock') is False


def test_hook_enabled_multiple(tmp_path: Path):
    (tmp_path / 'multiverse.toml').write_text('hooks = ["build", "lock"]')
    config = WorkspaceConfiguration.find(tmp_path, {})
    assert config is not None
    assert config.hooks_enabled('build', 'lock') is True
