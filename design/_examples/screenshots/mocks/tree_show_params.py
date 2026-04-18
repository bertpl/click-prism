"""Mock: projex tree with show_params — 4-column layout"""

from _render import render


def draw(c):
    c.print("projex            Description                              Arguments  Options")
    c.print("├── config        Manage configuration settings")
    c.print("│   ├── get        Get a configuration value                KEY")
    c.print("│   ├── set        Set a configuration value                KEY VALUE")
    c.print("│   ╰── list       List all configuration values")
    c.print("├── deploy        Deployment commands")
    c.print("│   ├── run        Run a deployment                                    --env, --dry-run")
    c.print("│   ╰── rollback   Roll back to a previous version                     --to-version")
    c.print("├── status        Show current project status")
    c.print("╰── tree          Display the command tree                             --depth")


render("projex tree", draw)
