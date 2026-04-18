"""Mock: projex tree with click-aliases"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("├── config (cfg, conf)    Manage configuration settings")
    c.print("│   ├── get                Get a configuration value")
    c.print("│   ├── set                Set a configuration value")
    c.print("│   ╰── list               List all configuration values")
    c.print("├── deploy (dp)           Deployment commands")
    c.print("│   ├── run                Run a deployment")
    c.print("│   ╰── rollback           Roll back to a previous version")
    c.print("├── status                Show current project status")
    c.print("╰── tree                  Display the command tree")


render("projex tree", draw)
