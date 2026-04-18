# 2.1. Terminology

This section defines the vocabulary used throughout the plan. Terms introduced
here are used without further explanation in later sections.

## 2.1.1. Click

### 2.1.1.1. Command

A single named action in a Click CLI, implemented as a decorated Python
function. Has a name, optional help text, and zero or more parameters.
Class: `click.Command`.

### 2.1.1.2. Command group

A command that serves as a container for subcommands. A group can contain both
commands and other groups, forming a hierarchy. Class: `click.Group`.

> This plan uses the short form "group" throughout. In Click 8.2,
> `MultiCommand` was deprecated and merged into `Group`.

### 2.1.1.3. Leaf command

A command that is not a group — i.e., an action at the bottom of the CLI
hierarchy with no subcommands of its own. Used throughout the plan to contrast
with "group" when a distinction matters (e.g., theming rules that apply only
to leaf commands vs. groups).

### 2.1.1.4. Root

The top-level group of a CLI application. It has no parent group and is
typically the entry point decorated with `@click.group()`. Every Click CLI
has exactly one root.

### 2.1.1.5. Argument

A positional parameter, identified by position rather than name.
Example: in `projex config get DATABASE_URL`, `DATABASE_URL` is an argument.

### 2.1.1.6. Option

A named parameter passed with a `--long-name` or `-short` prefix. Options
take a value. Example: `--env staging`.

### 2.1.1.7. Flag

A boolean option that takes no value; its presence toggles a boolean.
Example: `--dry-run`. In Click, a flag is an option with `is_flag=True`.

### 2.1.1.8. Hidden command

A command with `hidden=True`. Click excludes hidden commands from `--help`
output but still allows them to be invoked by name. Typically used for
internal or debug commands.

### 2.1.1.9. Deprecated command

A command with `deprecated=True`. Click still shows the command in `--help`
but prints a deprecation warning when it is invoked.

## 2.1.2. Console / Rich

### 2.1.2.1. TTY

Short for teletypewriter. A TTY is an interactive terminal — the window where
a user types commands and sees output (e.g., Terminal.app, iTerm2, Windows
Terminal).

Programs can detect whether their stdout is connected to a TTY. This
distinction matters because when stdout is a TTY (interactive use), formatting
like colors, styles, and Unicode may be available — depending on the terminal's
capabilities (see Unicode support, Color system below). When stdout is piped to a file
or another process (e.g., `cmd > out.txt`, `cmd | grep ...`), it is not a TTY,
and formatting should be suppressed — the recipient expects plain text.

`rich` performs this detection automatically and disables styling when stdout is
not a TTY.

### 2.1.2.2. ANSI escape codes

Special character sequences embedded in terminal output that control
formatting — bold, dim, italic, colors, and resets. ANSI stands for American
National Standards Institute, which standardized these sequences. For example,
the sequence `\033[1m` turns on bold and `\033[0m` resets all formatting.
The terminal interprets these sequences rather than displaying them. When
output is piped to a file or a process that doesn't understand them, they
appear as garbage characters — which is why styled output is suppressed when
stdout is not a TTY.

`rich` produces these sequences automatically based on the terminal's
capabilities.

### 2.1.2.3. Unicode support

The terminal's ability to render characters beyond ASCII, including box-drawing
glyphs (│, ├, └, ─). Most modern terminals support Unicode.

### 2.1.2.4. Color system

The level of color support available in the terminal. `rich` auto-detects one of
four tiers:

| Tier | Colors | Typical environment |
|---|---|---|
| No color | Monochrome | Piped output, `NO_COLOR` set |
| Standard | 8 base + 8 bright | Older terminals, basic SSH |
| 256-color | 256 indexed colors | Most modern terminals |
| Truecolor | 16.7M (24-bit RGB) | iTerm2, Windows Terminal, most Linux terminals |

### 2.1.2.5. NO_COLOR / FORCE_COLOR

Environment variable conventions for overriding color detection. `NO_COLOR`
(when set and non-empty) suppresses color output; `FORCE_COLOR` forces it even
when stdout is not a TTY. Both are respected by `rich` and widely adopted across
the CLI ecosystem.

### 2.1.2.6. Console width

The number of character columns available in the terminal. Both Click and `rich`
default to 80 columns when the terminal width cannot be detected (e.g., when
piped).

## 2.1.3. Target audience

### 2.1.3.1. Developer

The person who builds and maintains a CLI application using Click. The
developer is the one who would adopt `click-prism` as a dependency. Their
interface is Python code.

### 2.1.3.2. End user

The person who runs the finished CLI application in their terminal. Their
interface is the command line.
