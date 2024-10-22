# Poetry Multiverse Plugin

*Workspace support for Poetry.*

This plugin manages dependencies for multi-project workspaces, similar to tools like Cargo, Maven, and PNPM.

## Quick Start

This plugin requires Poetry 1.8 or later.
Poetry must be running on Python 3.9 or later.
(This is not necessarily the same as your project's Python version.)

1.  Install the plugin:
    ```
    poetry self add poetry-multiverse-plugin
    ```

2.  Create a Poetry project in the root of your workspace with the following configuration in pyproject.toml:
    ```toml
    [tool.multiverse]
    root = true
    ```

3.  Check whether projects in the workspace are locked to the same package versions:
    ```
    poetry workspace check
    ```

## Plugin Development

In addition to the runtime dependencies, install:

* [Poe the Poet](https://poethepoet.natn.io)
* [poetry-dynamic-versioning[plugin]](https://github.com/mtkennerly/poetry-dynamic-versioning)
