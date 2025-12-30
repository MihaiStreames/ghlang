from pathlib import Path
from typing import TYPE_CHECKING

import typer

from ghlang.logging import logger
from ghlang.visualizers import generate_bar
from ghlang.visualizers import generate_pie
from ghlang.visualizers import load_github_colors


if TYPE_CHECKING:
    from ghlang.config import Config


def generate_charts(
    language_stats: dict[str, int],
    cfg: "Config",
    colors_required: bool = True,
    title: str | None = None,
    output: Path | None = None,
    fmt: str | None = None,
) -> None:
    """Load colors and generate pie/bar charts with progress"""
    with logger.progress() as progress:
        task = progress.add_task("Generating charts", total=3)

        progress.update(task, description="Loading language colors...")
        colors_file = cfg.output_dir / "github_colors.json" if cfg.save_json else None
        colors = load_github_colors(output_file=colors_file)
        progress.advance(task)

        if not colors:
            if colors_required:
                logger.error("Couldn't load GitHub colors, can't continue without them")
                raise typer.Exit(1)

            logger.warning("Couldn't load GitHub colors, charts will be gray")
            colors = {}

        # determine output format
        # priority: --format > --output suffix > default png
        if fmt:
            if fmt not in ("png", "svg"):
                logger.warning(f"We only support png and svg, not '{fmt}', using png instead")
                suffix = ".png"
            else:
                suffix = f".{fmt}"
        elif output and output.suffix:
            suffix = output.suffix
        else:
            suffix = ".png"

        if output:
            if output.is_absolute():
                parent = output.parent
            elif str(output.parent) != ".":
                parent = cfg.output_dir / output.parent
            else:
                parent = cfg.output_dir

            stem = output.stem
            pie_output = parent / f"{stem}_pie{suffix}"
            bar_output = parent / f"{stem}_bar{suffix}"
        else:
            pie_output = cfg.output_dir / f"language_pie{suffix}"
            bar_output = cfg.output_dir / f"language_bar{suffix}"

        progress.update(task, description="Generating pie chart...")
        generate_pie(language_stats, colors, pie_output, title=title, theme=cfg.theme)
        progress.advance(task)

        progress.update(task, description="Generating bar chart...")
        generate_bar(
            language_stats,
            colors,
            bar_output,
            top_n=cfg.top_n_languages,
            title=title,
            theme=cfg.theme,
        )
        progress.advance(task)
