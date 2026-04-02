import os
from pathlib import Path
import platform
import subprocess

import typer

from ghlang.config import create_default_config
from ghlang.config import get_config_path
from ghlang.config import load_config
from ghlang.display.config import print_config
from ghlang.display.config import print_raw_config


def _open_in_editor(path: Path) -> None:
    """Open file in default editor"""
    editor = os.environ.get("EDITOR")

    if editor:
        subprocess.run([editor, str(path)], check=False)
    elif platform.system() == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    elif platform.system() == "Windows":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


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

        print_raw_config(config_path)
        return

    if show:
        if not config_path.exists():
            typer.echo(f"Config file doesn't exist yet: {config_path}")
            raise typer.Exit(1)

        try:
            cfg = load_config(config_path=config_path, require_token=False)
        except Exception as e:
            typer.echo(f"Error loading config: {e}")
            raise typer.Exit(1)

        print_config(cfg, config_path)
        return

    if not config_path.exists():
        create_default_config(config_path)
        typer.echo(f"Created config at {config_path}")

    _open_in_editor(config_path)
