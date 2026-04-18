"""Example CLI with click-help-colors integration.

Demonstrates colorized help output via HelpColorsGroup.
"""

import click
from click_help_colors import HelpColorsGroup


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
@click.version_option("1.0.0")
def cli():
    """Projex — a project management tool."""


# --- config group ---


@cli.group()
def config():
    """Manage configuration settings."""


@config.command()
@click.argument("key")
def get(key):
    """Get a configuration value."""
    click.echo(f"{key}=example_value")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a configuration value."""
    click.echo(f"Set {key}={value}")


@config.command(name="list")
def list_():
    """List all configuration values."""
    click.echo("key1=value1\nkey2=value2")


# --- deploy group ---


@cli.group()
def deploy():
    """Deployment commands."""


@deploy.command()
@click.option("--env", type=click.Choice(["staging", "production"]), required=True)
@click.option("--dry-run", is_flag=True, help="Simulate without making changes.")
def run(env, dry_run):
    """Run a deployment."""
    click.echo(f"Deploying to {env}{'(dry run)' if dry_run else ''}")


@deploy.command()
@click.option("--to-version", help="Target version to roll back to.")
def rollback(to_version):
    """Roll back to a previous version."""
    click.echo(f"Rolling back to {to_version or 'previous version'}")


# --- top-level commands ---


@cli.command()
def status():
    """Show current project status."""
    click.echo("All systems operational.")


@cli.command(hidden=True)
def debug():
    """Show debug information."""
    click.echo("Debug info...")


if __name__ == "__main__":
    cli()
