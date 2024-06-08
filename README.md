# Poetry Multiverse Plugin

*Workspace support for Poetry.*

This plugin manages depedencies for multi-project workspaces, similar to tools like Cargo, Maven, and PNPM.

## Quick Start

This plugin requires Poetry 1.8 or later.
Poetry must be running on Python 3.8 or later.
(This is not necessarily the same as your project's Python version.)

1.  Install the plugin:
    ```
    poetry self add poetry-multiverse-plugin
    ```

2.  Run the plugin:
    ```
    poetry workspace
    ```

## Plugin Development

In addition to the runtime dependencies, install Poethepoet.

The Poe tasks in tasks.toml provide a sandbox environment for testing the plugin.
This means you don't need to build and install the plugin during development.
Instead of running your Poetry commands with `poetry`, use `poe run` instead:

```
poe run workspace
```
