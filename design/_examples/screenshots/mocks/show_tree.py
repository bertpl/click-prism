"""Mock: show_tree(cli) — standalone, includes hidden commands"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("├── config        Manage configuration settings")
    c.print("│   ├── get        Get a configuration value")
    c.print("│   ├── set        Set a configuration value")
    c.print("│   ╰── list       List all configuration values")
    c.print("├── deploy        Deployment commands")
    c.print("│   ├── run        Run a deployment")
    c.print("│   ╰── rollback   Roll back to a previous version")
    c.print("├── status        Show current project status")
    c.print("╰── debug         Show debug information")


render("show_tree(cli)", draw)
