import json
from pathlib import Path

import typer

from ghlang.cli.utils import format_autocomplete
from ghlang.cli.utils import generate_charts
from ghlang.cli.utils import themes_autocomplete
from ghlang.config import load_config
from ghlang.exceptions import ConfigError
from ghlang.github_client import GitHubClient
from ghlang.logging import logger


def github(
    # TODO (#9): Add --exclude flag to filter patterns from CLI
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
    theme: str | None = typer.Option(
        None,
        "--theme",
        help="Chart theme (default: light)",
        autocompletion=themes_autocomplete,
    ),
    fmt: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format, overrides --output extension (png or svg)",
        autocompletion=format_autocomplete,
    ),
) -> None:
    """Analyze your GitHub repos"""
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
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=True)

    except ConfigError as e:
        logger.error(str(e))
        raise typer.Exit(1)

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
            repos_output=(
                cfg.output_dir / "repositories.json" if save_json and not stdout else None
            ),
            stats_output=(
                cfg.output_dir / "language_stats.json" if save_json and not stdout else None
            ),
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
            generate_charts(
                language_stats,
                cfg,
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
