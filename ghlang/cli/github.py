import json
from pathlib import Path

from loguru import logger
import typer

from ghlang.cli.utils import generate_charts
from ghlang.cli.utils import setup_logging
from ghlang.config import load_config
from ghlang.exceptions import ConfigError
from ghlang.github_client import GitHubClient


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
        cfg = load_config(
            config_path=config_path, cli_overrides=cli_overrides, require_token=True
        )

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
            repos_output=(
                cfg.output_dir / "repositories.json"
                if cfg.save_repos and not stdout
                else None
            ),
            stats_output=(
                cfg.output_dir / "language_stats.json"
                if cfg.save_json and not stdout
                else None
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
            generate_charts(language_stats, cfg, title=chart_title, output=output)

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        raise typer.Exit(1)
