import json
from pathlib import Path
import sys

from loguru import logger
import typer

from ghlang import __version__
from ghlang.cloc_client import ClocClient
from ghlang.config import Config
from ghlang.config import load_config
from ghlang.exceptions import ClocNotFoundError
from ghlang.exceptions import ConfigError
from ghlang.github_client import GitHubClient
from ghlang.visualizers import generate_bar
from ghlang.visualizers import generate_pie
from ghlang.visualizers import load_github_colors
from ghlang.visualizers import normalize_language_stats


app = typer.Typer(help="See what languages you've been coding in", add_completion=True)


def setup_logging(verbose: bool, quiet: bool = False) -> None:
    """Configure loguru logging"""
    logger.remove()
    if quiet:
        logger.add(sys.stderr, format="{message}", level="ERROR")
    else:
        log_level = "DEBUG" if verbose else "INFO"
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level=log_level,
        )


def generate_charts(
    language_stats: dict[str, int],
    cfg: Config,
    colors_required: bool = True,
    title: str | None = None,
    output: Path | None = None,
) -> None:
    """Load colors and generate pie/bar charts"""
    colors_file = cfg.output_dir / "github_colors.json" if cfg.save_json else None
    colors = load_github_colors(output_file=colors_file)

    if not colors:
        if colors_required:
            logger.error("Couldn't load GitHub colors, can't continue without them")
            raise typer.Exit(1)

        logger.warning("Couldn't load GitHub colors, charts will be gray")
        colors = {}

    if output:
        if output.is_absolute():
            parent = output.parent
        elif str(output.parent) != ".":
            parent = cfg.output_dir / output.parent
        else:
            parent = cfg.output_dir

        stem = output.stem
        suffix = output.suffix if output.suffix else ".png"

        pie_output = parent / f"{stem}_pie{suffix}"
        bar_output = parent / f"{stem}_bar{suffix}"
    else:
        pie_output = cfg.output_dir / "language_pie.png"
        bar_output = cfg.output_dir / "language_bar.png"

    generate_pie(language_stats, colors, pie_output, title=title)
    generate_bar(language_stats, colors, bar_output, top_n=cfg.top_n_languages, title=title)


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


@app.command()
def github(
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Use a different config file",
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Where to save the charts",
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=Path,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output path/filename (creates _pie and _bar variants)",
        path_type=Path,
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        "-t",
        help="Custom chart title",
    ),
    top_n: int | None = typer.Option(
        None,
        "--top-n",
        help="How many languages to show in the bar chart",
    ),
    json_only: bool = typer.Option(
        False,
        "--json-only",
        help="Output JSON only, skip chart generation",
    ),
    stdout: bool = typer.Option(
        False,
        "--stdout",
        help="Output stats to stdout instead of files",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress log output (only show errors)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show more details",
    ),
) -> None:
    """Analyze your GitHub repos"""
    # stdout implies quiet and json_only
    if stdout:
        quiet = True
        json_only = True

    try:
        cli_overrides = {
            "output_dir": output_dir,
            "top_n_languages": top_n,
            "verbose": verbose or None,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=True)

    except ConfigError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    setup_logging(cfg.verbose, quiet=quiet)

    if not stdout:
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving to {cfg.output_dir}")

    try:
        client = GitHubClient(
            token=cfg.token,
            affiliation=cfg.affiliation,
            visibility=cfg.visibility,
            ignored_repos=cfg.ignored_repos,
        )

        language_stats = client.get_all_language_stats(
            repos_output=(cfg.output_dir / "repositories.json" if cfg.save_repos and not stdout else None),
            stats_output=(cfg.output_dir / "language_stats.json" if cfg.save_json and not stdout else None),
        )

        if not language_stats:
            logger.error("No language statistics found, nothing to visualize")
            raise typer.Exit(1)

        if stdout:
            print(json.dumps(language_stats, indent=2))
        elif json_only:
            stats_file = cfg.output_dir / "language_stats.json"

            with stats_file.open("w") as f:
                json.dump(language_stats, f, indent=2)

            logger.success(f"Saved stats to {stats_file}")
        else:
            chart_title = title if title else "GitHub Language Stats"
            generate_charts(language_stats, cfg, title=chart_title, output=output)

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        raise typer.Exit(1)


@app.command()
def local(
    path: Path = typer.Argument(
        ".",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Use a different config file",
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Where to save the charts",
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=Path,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output path/filename (creates _pie and _bar variants)",
        path_type=Path,
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        "-t",
        help="Custom chart title",
    ),
    top_n: int | None = typer.Option(
        None,
        "--top-n",
        help="How many languages to show in the bar chart",
    ),
    json_only: bool = typer.Option(
        False,
        "--json-only",
        help="Output JSON only, skip chart generation",
    ),
    stdout: bool = typer.Option(
        False,
        "--stdout",
        help="Output stats to stdout instead of files",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress log output (only show errors)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show more details",
    ),
) -> None:
    """Analyze local files with cloc"""
    # stdout implies quiet and json_only
    if stdout:
        quiet = True
        json_only = True

    try:
        cli_overrides = {
            "output_dir": output_dir,
            "top_n_languages": top_n,
            "verbose": verbose or None,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=False)

    except ConfigError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    setup_logging(cfg.verbose, quiet=quiet)

    try:
        cloc = ClocClient(ignored_dirs=cfg.ignored_dirs)

    except ClocNotFoundError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    if not stdout:
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving to {cfg.output_dir}")

    try:
        detailed_stats = cloc.get_language_stats(
            path,
            stats_output=cfg.output_dir / "cloc_stats.json" if cfg.save_json and not stdout else None,
        )
        raw_stats = {
            lang: data["code"]
            for lang, data in detailed_stats.items()
            if lang != "_summary" and data["code"] > 0
        }
        language_stats = normalize_language_stats(raw_stats)

        if not language_stats:
            logger.error("No code found to analyze, nothing to visualize")
            raise typer.Exit(1)

        if stdout:
            print(json.dumps(language_stats, indent=2))
        elif json_only:
            stats_file = cfg.output_dir / "language_stats.json"

            with stats_file.open("w") as f:
                json.dump(language_stats, f, indent=2)

            logger.success(f"Saved stats to {stats_file}")
        else:
            if title:
                chart_title = title
            else:
                resolved = path.expanduser().resolve()
                chart_title = f"Local: {resolved.name}"

            generate_charts(language_stats, cfg, colors_required=False, title=chart_title, output=output)

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
