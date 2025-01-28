from cleo.io.buffered_io import BufferedIO
from cleo.io.outputs.output import Verbosity

from poetry_plugin_multiverse.errors import error_boundary


def test_error_boundary():
    io = BufferedIO()
    with error_boundary(io):
        io.write('Hello world')

    assert io.fetch_error() == ''
    assert io.fetch_output() == 'Hello world'


def test_error_boundary_exception():
    io = BufferedIO()
    with error_boundary(io):
        raise Exception('Descriptive error message')

    error_output = io.fetch_error()
    assert 'Descriptive error message' in error_output
    assert 'error_boundary' not in error_output


def test_error_boundary_verbose():
    io = BufferedIO()
    io.set_verbosity(Verbosity.VERBOSE)  # type:ignore
    with error_boundary(io):
        raise Exception('Descriptive error message')

    error_output = io.fetch_error()
    assert 'Descriptive error message' in error_output
    assert 'error_boundary' in error_output
