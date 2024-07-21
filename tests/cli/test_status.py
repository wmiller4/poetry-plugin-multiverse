from asyncio import Future
from unittest.mock import MagicMock
import pytest

from poetry_multiverse_plugin.cli.status import ProjectStatus, StatusOutput


def test_complete_success():
    status = ProjectStatus(MagicMock(StatusOutput), 'template', 'project')
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = None
    future.result.return_value = 0
    assert status.complete(future) == 0


def test_complete_fail():
    status = ProjectStatus(MagicMock(StatusOutput), 'template', 'project')
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = None
    future.result.return_value = 1
    assert status.complete(future) == 1


def test_complete_error():
    status = ProjectStatus(MagicMock(StatusOutput), 'template', 'project')
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = False
    future.exception.return_value = IOError()
    future.result.side_effect = IOError()
    assert status.complete(future) is None


def test_complete_canceled():
    status = ProjectStatus(MagicMock(StatusOutput), 'template', 'project')
    future = MagicMock(Future)
    future.done.return_value = True
    future.cancelled.return_value = True
    future.exception.return_value = AssertionError()
    future.result.side_effect = AssertionError()
    assert status.complete(future) is None


def test_complete_not_done():
    status = ProjectStatus(MagicMock(StatusOutput), 'template', 'project')
    future = MagicMock(Future)
    future.done.return_value = False
    with pytest.raises(AssertionError):
        status.complete(future)
