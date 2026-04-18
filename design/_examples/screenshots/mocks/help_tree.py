"""Mock: projex --help (tree-as-help on root)"""

from _render import render


def draw(c):
    c.print("Usage: projex [OPTIONS] COMMAND [ARGS]...")
    c.print()
    c.print("  Projex \u2014 a project management tool.")
    c.print()
    c.print("Options:")
    c.print("  --version    Show the version and exit.")
    c.print("  --help-json  Output CLI structure as JSON and exit.")
    c.print("  --help       Show this message and exit.")
    c.print()
    c.print("Commands:")
    c.print("  projex")
    c.print("  ├── config        Manage configuration settings")
    c.print("  │   ├── get        Get a configuration value")
    c.print("  │   ├── set        Set a configuration value")
    c.print("  │   ╰── list       List all configuration values")
    c.print("  ├── deploy        Deployment commands")
    c.print("  │   ├── run        Run a deployment")
    c.print("  │   ╰── rollback   Roll back to a previous version")
    c.print("  ╰── status        Show current project status")


render("projex --help", draw)
