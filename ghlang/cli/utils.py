from pathlib import Path
import sys

from loguru import logger
import typer

from ghlang.config import Config
from ghlang.visualizers import generate_bar
from ghlang.visualizers import generate_pie
from ghlang.visualizers import load_github_colors


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
    generate_bar(
        language_stats, colors, bar_output, top_n=cfg.top_n_languages, title=title
    )
