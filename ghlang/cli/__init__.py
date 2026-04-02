"""CLI entry point and command registration"""

import typer

from ghlang import __version__

from . import config as config_mod
from . import github as github_mod
from . import local as local_mod
from . import theme as theme_mod


app = typer.Typer(help="See what languages you've been coding in", add_completion=True)
app.command()(config_mod.config)
app.command()(github_mod.github)
app.command()(local_mod.local)
app.command()(theme_mod.theme)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"ghlang v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    pass


if __name__ == "__main__":
    app()
