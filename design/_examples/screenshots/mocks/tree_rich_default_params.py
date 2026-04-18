"""Mock: projex tree (with Rich — default theme, show_params)

Default theme with all 6 columns visible:
  Vertical:   guides=bright_black+dim, group_names=cyan, command_names=cyan,
              description=dim, arguments=bright_blue, options=blue
  Horizontal: title_row=bold, group_rows=bold, command_rows=(none)
"""

from _render import render


def draw(c):
    # Header (title_row: bold)
    c.print("[bold cyan]projex[/bold cyan]            [bold dim]Description[/bold dim]                              [bold bright_blue]Arguments[/bold bright_blue]  [bold blue]Options[/bold blue]")
    # Group row (bold)
    c.print("[dim bright_black]├──[/dim bright_black] [bold][cyan]config[/cyan]        [dim]Manage configuration settings[/dim][/bold]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]get[/cyan]        [dim]Get a configuration value[/dim]                [bright_blue]KEY[/bright_blue]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]set[/cyan]        [dim]Set a configuration value[/dim]                [bright_blue]KEY VALUE[/bright_blue]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [cyan]list[/cyan]       [dim]List all configuration values[/dim]")
    # Group row (bold)
    c.print("[dim bright_black]├──[/dim bright_black] [bold][cyan]deploy[/cyan]        [dim]Deployment commands[/dim][/bold]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [cyan]run[/cyan]        [dim]Run a deployment[/dim]                                    [blue]--env, --dry-run[/blue]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [cyan]rollback[/cyan]   [dim]Roll back to a previous version[/dim]                     [blue]--to-version[/blue]")
    c.print("[dim bright_black]├──[/dim bright_black] [cyan]status[/cyan]        [dim]Show current project status[/dim]")
    c.print("[dim bright_black]╰──[/dim bright_black] [cyan]tree[/cyan]          [dim]Display the command tree[/dim]                             [blue]--depth[/blue]")


render("projex tree", draw)
