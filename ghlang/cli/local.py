import json
from pathlib import Path
import sys

import typer

from ghlang.cli.utils import format_autocomplete
from ghlang.cli.utils import generate_charts
from ghlang.cli.utils import save_json_stats
from ghlang.cli.utils import themes_autocomplete
from ghlang.cloc_client import ClocClient
from ghlang.config import load_config
from ghlang.exceptions import ClocNotFoundError
from ghlang.exceptions import ConfigError
from ghlang.logging import logger
from ghlang.visualizers import normalize_language_stats


def _merge_cloc_stats(all_stats: list[dict[str, dict]]) -> dict[str, dict]:
    """Merge multiple cloc stats dictionaries into one"""
    merged: dict[str, dict] = {}

    for stats in all_stats:
        for lang, data in stats.items():
            if lang == "_summary":
                continue

            if lang not in merged:
                merged[lang] = {"files": 0, "blank": 0, "comment": 0, "code": 0}

            merged[lang]["files"] += data.get("files", 0)
            merged[lang]["blank"] += data.get("blank", 0)
            merged[lang]["comment"] += data.get("comment", 0)
            merged[lang]["code"] += data.get("code", 0)

    return merged


def _get_chart_title(paths: list[Path], custom_title: str | None) -> str:
    """Generate chart title based on paths or custom title"""
    if custom_title:
        return custom_title
    if len(paths) == 1:
        resolved = paths[0].expanduser().resolve()
        return f"Local: {resolved.name}"
    return f"Local: {len(paths)} paths"


def local(
    # TODO (#7): Handle mixed git/non-git directory trees better
    paths: list[Path] | None = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=Path,
        help="Paths to analyze (defaults to current directory)",
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
    """Analyze local files with cloc"""
    if paths is None:
        paths = [Path()]

    if stdout:
        quiet = True
        json_only = True

    try:
        logger.configure(verbose, quiet=quiet)
        cli_overrides = {
            "output_dir": output_dir,
            "verbose": verbose or None,
            "theme": theme,
        }
        cfg = load_config(config_path=config_path, cli_overrides=cli_overrides, require_token=False)
        logger.configure(cfg.verbose, quiet=quiet)

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
        all_stats: list[dict[str, dict]] = []

        for i, path in enumerate(paths, start=1):
            path_name = path.name or path.expanduser().resolve().name or "current"
            detailed_stats = cloc.get_language_stats(
                path,
                stats_output=(
                    cfg.output_dir / f"cloc_stats_{i:02d}_{path_name}.json"
                    if save_json and not stdout and len(paths) > 1
                    else (cfg.output_dir / "cloc_stats.json" if save_json and not stdout else None)
                ),
            )
            all_stats.append(detailed_stats)

        merged_stats = _merge_cloc_stats(all_stats) if len(paths) > 1 else all_stats[0]

        raw_stats = {
            lang: data["code"]
            for lang, data in merged_stats.items()
            if lang != "_summary" and data["code"] > 0
        }
        language_stats = normalize_language_stats(raw_stats)

        if not language_stats:
            logger.error("No code found to analyze, nothing to visualize")
            raise typer.Exit(1)

        if stdout:
            print(json.dumps(language_stats, indent=2))
        elif json_only:
            save_json_stats(language_stats, cfg.output_dir)
        else:
            generate_charts(
                language_stats,
                cfg,
                colors_required=False,
                title=_get_chart_title(paths, title),
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
