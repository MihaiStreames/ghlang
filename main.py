from pathlib import Path
import sys

import click
from loguru import logger

from ghlang.config import ConfigError
from ghlang.config import load_config
from ghlang.github_client import GitHubClient
from ghlang.github_client import load_github_colors
from ghlang.visualizers import generate_bar
from ghlang.visualizers import generate_pie


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: ~/.config/ghlang/config.toml)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Override output directory from config",
)
@click.option(
    "--top-n",
    type=int,
    help="Override number of top languages in bar chart",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def main(
    config: Path | None,
    output_dir: Path | None,
    top_n: int | None,
    verbose: bool,
):
    """Generate language statistics and visualizations from your GitHub repositories

    Args:
        config: Optional path to custom config file
        output_dir: Optional override for output directory
        top_n: Optional override for number of top languages
        verbose: Enable verbose logging if True
    """
    try:
        # Load config with CLI overrides
        cli_overrides = {
            "output_dir": output_dir,
            "top_n_languages": top_n,
            "verbose": verbose or None,  # Only override if flag is set
        }
        cfg = load_config(config_path=config, cli_overrides=cli_overrides)

    except ConfigError as e:
        logger.error(str(e))
        sys.exit(1)

    # Configure logging
    logger.remove()
    log_level = "DEBUG" if cfg.verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
    )

    # Create output directory
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {cfg.output_dir}")

    try:
        # Load GitHub colors
        colors_file = cfg.output_dir / "github_colors.json" if cfg.save_json else None
        colors = load_github_colors(output_file=colors_file)

        if not colors:
            logger.error("Failed to load GitHub colors. Exiting.")
            sys.exit(1)

        # Initialize GitHub client
        client = GitHubClient(
            token=cfg.token,
            affiliation=cfg.affiliation,
            visibility=cfg.visibility,
        )

        # Get language statistics
        repos_file = cfg.output_dir / "repositories.json" if cfg.save_repos else None
        stats_file = cfg.output_dir / "language_stats.json" if cfg.save_json else None

        language_stats = client.get_all_language_stats(
            repos_output=repos_file,
            stats_output=stats_file,
        )

        if not language_stats:
            logger.error("No language statistics found. Exiting.")
            sys.exit(1)

        # Generate visualizations
        pie_output = cfg.output_dir / "language_pie.png"
        bar_output = cfg.output_dir / "language_bar.png"

        generate_pie(language_stats, colors, pie_output)
        generate_bar(language_stats, colors, bar_output, top_n=cfg.top_n_languages)

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
