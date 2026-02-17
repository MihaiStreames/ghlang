import typer

from ghlang import __version__

from .config import config
from .github import github
from .local import local


app = typer.Typer(help="See what languages you've been coding in", add_completion=True)
app.command()(config)
app.command()(github)
app.command()(local)


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
