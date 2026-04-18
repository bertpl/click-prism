"""Mock: projex tree (with Rich — default theme, bold group rows)

Default theme:
  Vertical:   guides=bright_black+dim, group_names=cyan, command_names=cyan,
              description=dim
  Horizontal: title_row=bold, group_rows=bold, command_rows=(none)
"""

from _render import render


def draw(c):
    c.print("[bold cyan]projex[/bold cyan]")
    c.print("[dim bright_black]├──[/dim bright_black] [bold][cyan]config[/cyan]        [dim]Manage configuration settings[/dim][/bold]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]get[/cyan]        [dim]Get a configuration value[/dim]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]set[/cyan]        [dim]Set a configuration value[/dim]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [cyan]list[/cyan]       [dim]List all configuration values[/dim]")
    c.print("[dim bright_black]├──[/dim bright_black] [bold][cyan]deploy[/cyan]        [dim]Deployment commands[/dim][/bold]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]run[/cyan]        [dim]Run a deployment[/dim]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [cyan]rollback[/cyan]   [dim]Roll back to a previous version[/dim]")
    c.print("[dim bright_black]├──[/dim bright_black] [cyan]status[/cyan]        [dim]Show current project status[/dim]")
    c.print("[dim bright_black]╰──[/dim bright_black] [cyan]tree[/cyan]          [dim]Display the command tree[/dim]")


render("projex tree", draw)
