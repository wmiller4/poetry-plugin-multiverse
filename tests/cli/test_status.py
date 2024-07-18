from asyncio import Future
from queue import Queue
from unittest.mock import MagicMock
from cleo.io.io import IO
import pytest

from poetry_multiverse_plugin.cli.status import WorkspaceStatus
from tests.conftest import ProjectFactory


def test_complete_success(project: ProjectFactory):
    p1 = project('p1')
    status = WorkspaceStatus(MagicMock(IO), [p1], Queue())
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = None
    future.result.return_value = 0
    assert status.complete(p1, future) == 0


def test_complete_fail(project: ProjectFactory):
    p1 = project('p1')
    status = WorkspaceStatus(MagicMock(IO), [p1], Queue())
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = None
    future.result.return_value = 1
    assert status.complete(p1, future) == 1


def test_complete_error(project: ProjectFactory):
    p1 = project('p1')
    status = WorkspaceStatus(MagicMock(IO), [p1], Queue())
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = IOError()
    future.result.side_effect = IOError()
    assert status.complete(p1, future) is None


def test_complete_canceled(project: ProjectFactory):
    p1 = project('p1')
    status = WorkspaceStatus(MagicMock(IO), [p1], Queue())
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = True
    future.exception.return_value = AssertionError()
    future.result.side_effect = AssertionError()
    assert status.complete(p1, future) is None


def test_complete_not_done(project: ProjectFactory):
    p1 = project('p1')
    status = WorkspaceStatus(MagicMock(IO), [p1], Queue())
    future = MagicMock(Future)
    future.done.return_value = False
    with pytest.raises(AssertionError):
        status.complete(p1, future)
