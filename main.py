from pathlib import Path
import sys

import click
from dotenv import load_dotenv
from loguru import logger

from github_stats.github_client import GitHubClient
from github_stats.github_client import load_github_colors
from github_stats.visualizers import generate_bar
from github_stats.visualizers import generate_pie


@click.command()
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    required=True,
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--affiliation",
    envvar="GH_AFFILIATION",
    default="owner,collaborator,organization_member",
    help="Which repos to include",
)
@click.option(
    "--visibility",
    envvar="GH_VISIBILITY",
    default="all",
    type=click.Choice(["all", "public", "private"]),
    help="Repo visibility filter",
)
@click.option(
    "--output-dir",
    "-o",
    default="output",
    type=click.Path(path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--top-n",
    default=5,
    type=int,
    help="Number of top languages to show in bar chart",
)
@click.option(
    "--save-data/--no-save-data",
    default=True,
    help="Save API responses as JSON files",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def main(
    token: str,
    affiliation: str,
    visibility: str,
    output_dir: Path,
    top_n: int,
    save_data: bool,
    verbose: bool,
):
    """Generate language statistics and visualizations from your GitHub repositories."""
    # Configure logging
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
    )

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load GitHub colors
        colors_file = output_dir / "github_colors.json" if save_data else None
        colors = load_github_colors(output_file=colors_file)

        if not colors:
            logger.error("Failed to load GitHub colors. Exiting.")
            sys.exit(1)

        # Initialize GitHub client
        client = GitHubClient(token=token, affiliation=affiliation, visibility=visibility)

        # Get language statistics
        output_dir / "repositories.json" if save_data else None
        stats_file = output_dir / "language_stats.json" if save_data else None

        language_stats = client.get_all_language_stats(output_file=stats_file)

        if not language_stats:
            logger.error("No language statistics found. Exiting.")
            sys.exit(1)

        # Generate visualizations
        pie_output = output_dir / "language_pie.png"
        bar_output = output_dir / "language_bar.png"

        generate_pie(language_stats, colors, pie_output)
        generate_bar(language_stats, colors, bar_output, top_n=top_n)

        logger.success(f"\nAll done! Check {output_dir} for outputs.")

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_dotenv()
    main()
