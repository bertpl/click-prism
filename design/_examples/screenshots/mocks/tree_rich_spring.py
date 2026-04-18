"""Mock: projex tree (with Rich — "spring" built-in theme, show_params)

Spring theme using RGB colors:
  Vertical:   guides=#86817B (Stone 4) +dim, group_names=#5E9F6C (Fern 5),
              command_names=#84C691 (Fern 7), description=#8FAACC (Cornflower),
              arguments=#D4C09A (Golden Wheat), options=#B5A78C (Warm Earth)
  Horizontal: title_row=bold, group_rows=bold, command_rows=(none)
"""

from _render import render

# Palette colors
GUIDE = "#86817B"       # Stone 4
GROUP = "#5E9F6C"       # Fern 5
CMD = "#84C691"         # Fern 7
DESC = "#8FAACC"        # Cornflower
ARG = "#D4C09A"         # Golden Wheat
OPT = "#B5A78C"         # Warm Earth


def draw(c):
    # Header (title_row: bold)
    c.print(f"[bold {GROUP}]projex[/bold {GROUP}]            [bold {DESC}]Description[/bold {DESC}]                              [bold {ARG}]Arguments[/bold {ARG}]  [bold {OPT}]Options[/bold {OPT}]")
    # Group row (bold)
    c.print(f"[dim {GUIDE}]├──[/dim {GUIDE}] [bold][{GROUP}]config[/{GROUP}]        [{DESC}]Manage configuration settings[/{DESC}][/bold]")
    c.print(f"[dim {GUIDE}]│   ├──[/dim {GUIDE}] [{CMD}]get[/{CMD}]        [{DESC}]Get a configuration value[/{DESC}]                [{ARG}]KEY[/{ARG}]")
    c.print(f"[dim {GUIDE}]│   ├──[/dim {GUIDE}] [{CMD}]set[/{CMD}]        [{DESC}]Set a configuration value[/{DESC}]                [{ARG}]KEY VALUE[/{ARG}]")
    c.print(f"[dim {GUIDE}]│   ╰──[/dim {GUIDE}] [{CMD}]list[/{CMD}]       [{DESC}]List all configuration values[/{DESC}]")
    # Group row (bold)
    c.print(f"[dim {GUIDE}]├──[/dim {GUIDE}] [bold][{GROUP}]deploy[/{GROUP}]        [{DESC}]Deployment commands[/{DESC}][/bold]")
    c.print(f"[dim {GUIDE}]│   ├──[/dim {GUIDE}] [{CMD}]run[/{CMD}]        [{DESC}]Run a deployment[/{DESC}]                                    [{OPT}]--env, --dry-run[/{OPT}]")
    c.print(f"[dim {GUIDE}]│   ╰──[/dim {GUIDE}] [{CMD}]rollback[/{CMD}]   [{DESC}]Roll back to a previous version[/{DESC}]                     [{OPT}]--to-version[/{OPT}]")
    c.print(f"[dim {GUIDE}]├──[/dim {GUIDE}] [{CMD}]status[/{CMD}]        [{DESC}]Show current project status[/{DESC}]")
    c.print(f"[dim {GUIDE}]╰──[/dim {GUIDE}] [{CMD}]tree[/{CMD}]          [{DESC}]Display the command tree[/{DESC}]                             [{OPT}]--depth[/{OPT}]")


render("projex tree", draw)
