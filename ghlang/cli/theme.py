from rich.console import Console
from rich.table import Table
import typer

from ghlang.cli.utils import get_active_theme
from ghlang.cli.utils import get_config_dir
from ghlang.cli.utils import handle_cli_errors
from ghlang.cli.utils import load_themes_by_source
from ghlang.static.themes import THEMES
from ghlang.themes import load_all_themes


def theme(
    list_themes: bool = typer.Option(
        False,
        "--list",
        help="List all available themes",
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help="Force-refresh remote themes (bypass 1-day cache)",
    ),
    info: str | None = typer.Option(
        None,
        "--info",
        help="Show details for a theme",
    ),
) -> None:
    """Manage themes"""
    with handle_cli_errors():
        console = Console()
        config_dir = get_config_dir()

        if refresh:
            themes = load_all_themes(config_dir, force_refresh=True)
            remote_count = len(themes) - len(THEMES)
            console.print(
                f"[green]Refreshed[/green] remote themes - {remote_count} remote theme(s) loaded"
            )
            return

        active = get_active_theme()
        built_in, remote, custom = load_themes_by_source(config_dir)

        if info and not list_themes:
            all_themes: dict[str, dict[str, str]] = {**built_in, **remote, **custom}
            if info not in all_themes:
                console.print(f"[red]Theme '{info}' not found[/red]")
                raise typer.Exit(1)

            colors = all_themes[info]

            if info in custom:
                source = "custom"
            elif info in remote:
                source = "remote"
            else:
                source = "built-in"

            active_tag = "  [green]*active[/green]" if info == active else ""
            console.print(f"\n[bold cyan]{info}[/bold cyan]  [dim]({source})[/dim]{active_tag}\n")

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="cyan")
            table.add_column("Hex")
            table.add_column("Swatch")

            for key, hex_val in colors.items():
                swatch = f"[on {hex_val}]   [/on {hex_val}]"
                table.add_row(key, hex_val, swatch)

            console.print(table)
            console.print()
            return

        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
        table.add_column("Theme", style="cyan")
        table.add_column("Source")
        table.add_column("")

        for source_label, themes_dict in [
            ("built-in", built_in),
            ("remote", remote),
            ("custom", custom),
        ]:
            for theme_name in sorted(themes_dict):
                marker = "[green]*[/green]" if theme_name == active else ""
                table.add_row(theme_name, source_label, marker)

        console.print()
        console.print(table)
        console.print(f"\n  [dim]* = active theme ({active})[/dim]\n")
