"""Mock: projex tree (with Rich — custom theme, show_params, bold italic groups)

Custom theme from 1.3.B-C code example:
  Vertical:   guides=bright_black+dim, group_names=green,
              command_names=bright_green, description=dim,
              arguments/options=default (bright_blue / blue)
  Horizontal: title_row=bold, group_rows=bold+italic, command_rows=(none)
"""

from _render import render


def draw(c):
    # Header (title_row: bold)
    c.print("[bold green]projex[/bold green]            [bold dim]Description[/bold dim]                              [bold bright_blue]Arguments[/bold bright_blue]  [bold blue]Options[/bold blue]")
    # Group row (bold+italic)
    c.print("[dim bright_black]├──[/dim bright_black] [bold italic][green]config[/green]        [dim]Manage configuration settings[/dim][/bold italic]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [bright_green]get[/bright_green]        [dim]Get a configuration value[/dim]                [bright_blue]KEY[/bright_blue]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [bright_green]set[/bright_green]        [dim]Set a configuration value[/dim]                [bright_blue]KEY VALUE[/bright_blue]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [bright_green]list[/bright_green]       [dim]List all configuration values[/dim]")
    # Group row (bold+italic)
    c.print("[dim bright_black]├──[/dim bright_black] [bold italic][green]deploy[/green]        [dim]Deployment commands[/dim][/bold italic]")
    c.print("[dim bright_black]│   ├──[/dim bright_black] [bright_green]run[/bright_green]        [dim]Run a deployment[/dim]                                    [blue]--env, --dry-run[/blue]")
    c.print("[dim bright_black]│   ╰──[/dim bright_black] [bright_green]rollback[/bright_green]   [dim]Roll back to a previous version[/dim]                     [blue]--to-version[/blue]")
    c.print("[dim bright_black]├──[/dim bright_black] [bright_green]status[/bright_green]        [dim]Show current project status[/dim]")
    c.print("[dim bright_black]╰──[/dim bright_black] [bright_green]tree[/bright_green]          [dim]Display the command tree[/dim]                             [blue]--depth[/blue]")


render("projex tree", draw)
