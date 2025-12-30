import json
from pathlib import Path
import sys

import typer

from ghlang.cli.utils import generate_charts
from ghlang.cloc_client import ClocClient
from ghlang.config import load_config
from ghlang.exceptions import ClocNotFoundError
from ghlang.exceptions import ConfigError
from ghlang.logging import logger
from ghlang.visualizers import normalize_language_stats


def local(
    # TODO (#8): Add support for multiple paths in one command
    # TODO (#7): Handle mixed git/non-git directory trees better
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
        help="Custom output path/filename",
        path_type=Path,
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        "-t",
        help="Custom chart title",
    ),
    top_n: int = typer.Option(
        5,
        "--top-n",
        help="How many languages to show in the bar chart",
    ),
    save_json: bool = typer.Option(
        False,
        "--save-json",
        help="Save raw stats as JSON files",
    ),
    json_only: bool = typer.Option(
        False,
        "--json-only",
        help="Output JSON only, skip chart generation",
    ),
    stdout: bool = typer.Option(
        False,
        "--stdout",
        help="Output stats to stdout instead of files (implies --json-only --quiet)",
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
    follow_links: bool = typer.Option(
        False,
        "--follow-links",
        help="Follow symlinks when analyzing (unix only)",
    ),
    theme: str | None = typer.Option(
        None,
        "--theme",
        help="Chart theme (default: light)",
    ),
    fmt: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format, overrides --output extension (png or svg)",
    ),
) -> None:
    """Analyze local files with cloc"""
    if stdout:
        quiet = True
        json_only = True

    logger.configure(verbose, quiet=quiet)

    try:
        cli_overrides = {
            "output_dir": output_dir,
            "verbose": verbose or None,
            "theme": theme,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=False)

    except ConfigError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    if follow_links and sys.platform == "win32":
        logger.warning("--follow-links is not supported on Windows, ignoring")
        follow_links = False

    try:
        cloc = ClocClient(ignored_dirs=cfg.ignored_dirs, follow_links=follow_links)

    except ClocNotFoundError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    if not stdout:
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving to {cfg.output_dir}")

    try:
        detailed_stats = cloc.get_language_stats(
            path,
            stats_output=(
                cfg.output_dir / "cloc_stats.json" if save_json and not stdout else None
            ),
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

            generate_charts(
                language_stats,
                cfg,
                colors_required=False,
                title=chart_title,
                output=output,
                fmt=fmt,
                top_n=top_n,
                save_json=save_json,
            )

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        raise typer.Exit(1)
