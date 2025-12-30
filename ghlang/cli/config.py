import os
from pathlib import Path
import platform
import subprocess

from rich.console import Console
from rich.table import Table
import typer

from ghlang.config import create_default_config
from ghlang.config import get_config_path
from ghlang.config import load_config


def _open_in_editor(path: Path) -> None:
    """Open file in default editor"""
    editor = os.environ.get("EDITOR")

    if editor:
        subprocess.run([editor, str(path)], check=False)
    elif platform.system() == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    elif platform.system() == "Windows":
        os.startfile(str(path))
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def _format_value(value: object) -> str:
    """Format a config value for display"""
    if isinstance(value, bool):
        return "[green]true[/green]" if value else "[red]false[/red]"

    if isinstance(value, list):
        if not value:
            return "[dim][][/dim]"

        return ", ".join(str(v) for v in value)

    if isinstance(value, Path):
        return str(value)

    return str(value)


def _print_config_table(config_path: Path) -> None:
    """Print config as a formatted table"""
    console = Console()

    try:
        cfg = load_config(config_path=config_path, require_token=False)

    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"\n[bold]Config:[/bold] {config_path}\n")

    # GitHub section
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    console.print("[bold yellow]GitHub[/bold yellow]")
    table.add_row("token", cfg.token if cfg.token else "[dim]not set[/dim]")
    table.add_row("affiliation", cfg.affiliation)
    table.add_row("visibility", cfg.visibility)
    table.add_row("ignored_repos", _format_value(cfg.ignored_repos))
    console.print(table)
    console.print()

    # Cloc section
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    console.print("[bold yellow]Cloc[/bold yellow]")
    table.add_row("ignored_dirs", _format_value(cfg.ignored_dirs))
    console.print(table)
    console.print()

    # Output section
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    console.print("[bold yellow]Output[/bold yellow]")
    table.add_row("directory", str(cfg.output_dir))
    table.add_row("save_json", _format_value(cfg.save_json))
    table.add_row("save_repos", _format_value(cfg.save_repos))
    table.add_row("top_n_languages", str(cfg.top_n_languages))
    console.print(table)
    console.print()

    # Preferences section
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    console.print("[bold yellow]Preferences[/bold yellow]")
    table.add_row("verbose", _format_value(cfg.verbose))
    console.print(table)
    console.print()


def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Print config as formatted table",
    ),
    path: bool = typer.Option(
        False,
        "--path",
        help="Print config file path",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print raw config file contents",
    ),
) -> None:
    """Manage config file"""
    config_path = get_config_path()

    if path:
        print(config_path)
        return

    if raw:
        if not config_path.exists():
            typer.echo(f"Config file doesn't exist yet: {config_path}")
            raise typer.Exit(1)

        print(config_path.read_text())
        return

    if show:
        if not config_path.exists():
            typer.echo(f"Config file doesn't exist yet: {config_path}")
            raise typer.Exit(1)

        _print_config_table(config_path)
        return

    if not config_path.exists():
        create_default_config(config_path)
        typer.echo(f"Created config at {config_path}")

    _open_in_editor(config_path)
