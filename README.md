# Poetry Multiverse Plugin

*Workspace support for Poetry.*

This plugin manages dependencies for multi-project workspaces, similar to tools like Cargo, Maven, and PNPM.

## Quick Start

This plugin requires Poetry 1.8 or later.
Poetry must be running on Python 3.8 or later.
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

3.  Check whether projects in the workspace are locked to the same packaeg versions:
    ```
    poetry workspace check
    ```

## Plugin Development

In addition to the runtime dependencies, install:

* Poethepoet
* poetry-dynamic-versioning

The Poe tasks in tasks.toml provide a helper command for testing the plugin.
This means you don't need to build and install the plugin during development.
Instead of running your Poetry commands with `poetry`, use `poe run` instead:

```
poe run workspace check
```
