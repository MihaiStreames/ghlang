from pathlib import Path
import sys

import click
from loguru import logger

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


def setup_logging(verbose: bool) -> None:
    """Configure loguru logging"""
    logger.remove()
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
) -> None:
    """Load colors and generate pie/bar charts"""
    colors_file = cfg.output_dir / "github_colors.json" if cfg.save_json else None
    colors = load_github_colors(output_file=colors_file)

    if not colors:
        if colors_required:
            logger.error("Couldn't load GitHub colors, can't continue without them")
            sys.exit(1)
        else:
            logger.warning("Couldn't load GitHub colors, charts will be gray")
            colors = {}

    pie_output = cfg.output_dir / "language_pie.png"
    bar_output = cfg.output_dir / "language_bar.png"

    generate_pie(language_stats, colors, pie_output)
    generate_bar(language_stats, colors, bar_output, top_n=cfg.top_n_languages)


@click.group()
@click.version_option()
def cli():
    """See what languages you've been coding in"""
    pass


@cli.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Use a different config file",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Where to save the charts",
)
@click.option(
    "--top-n",
    type=int,
    help="How many languages to show in the bar chart",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show more details",
)
def github(
    config_path: Path | None,
    output_dir: Path | None,
    top_n: int | None,
    verbose: bool,
):
    """Analyze your GitHub repos"""
    try:
        cli_overrides = {
            "output_dir": output_dir,
            "top_n_languages": top_n,
            "verbose": verbose or None,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=True)

    except ConfigError as e:
        logger.error(str(e))
        sys.exit(1)

    setup_logging(cfg.verbose)
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
            repos_output=cfg.output_dir / "repositories.json" if cfg.save_repos else None,
            stats_output=cfg.output_dir / "language_stats.json" if cfg.save_json else None,
        )

        if not language_stats:
            logger.error("No language statistics found, nothing to visualize")
            sys.exit(1)

        generate_charts(language_stats, cfg)

    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        sys.exit(1)


@cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, path_type=Path),
    default=".",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Use a different config file",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Where to save the charts",
)
@click.option(
    "--top-n",
    type=int,
    help="How many languages to show in the bar chart",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show more details",
)
def local(
    path: Path,
    config_path: Path | None,
    output_dir: Path | None,
    top_n: int | None,
    verbose: bool,
):
    """Analyze local files with cloc"""
    try:
        cli_overrides = {
            "output_dir": output_dir,
            "top_n_languages": top_n,
            "verbose": verbose or None,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=False)

    except ConfigError as e:
        logger.error(str(e))
        sys.exit(1)

    setup_logging(cfg.verbose)

    try:
        cloc = ClocClient(ignored_dirs=cfg.ignored_dirs)

    except ClocNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving to {cfg.output_dir}")

    try:
        detailed_stats = cloc.get_language_stats(
            path,
            stats_output=cfg.output_dir / "cloc_stats.json" if cfg.save_json else None,
        )
        raw_stats = {
            lang: data["code"]
            for lang, data in detailed_stats.items()
            if lang != "_summary" and data["code"] > 0
        }
        language_stats = normalize_language_stats(raw_stats)

        if not language_stats:
            logger.error("No code found to analyze, nothing to visualize")
            sys.exit(1)

        generate_charts(
            language_stats,
            cfg,
            colors_required=False,
        )

    except Exception as e:
        logger.exception(f"Something went wrong: {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
