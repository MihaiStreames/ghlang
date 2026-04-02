import json
from pathlib import Path

import typer

from ghlang import exceptions
from ghlang import github_client
from ghlang import log

from . import charts
from . import utils


def github(
    repos: list[str] | None = typer.Argument(
        None,
        help="Specific repos to analyze (owner/repo format, defaults to all your repos)",
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        help="Use a different config file",
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Where to save the charts",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output path/filename",
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
        autocompletion=utils.themes_autocomplete,
    ),
    style: str = typer.Option(
        "pixel",
        "--style",
        "-s",
        help="Chart style (default: pixel)",
        autocompletion=utils.styles_autocomplete,
    ),
) -> None:
    """Analyze your GitHub repos"""
    try:
        cfg, quiet, json_only = utils.setup_cli_environment(
            config_path=config_path,
            output_dir=output_dir,
            verbose=verbose,
            theme=theme,
            stdout=stdout,
            quiet=quiet,
            require_token=True,
        )

    except exceptions.ConfigError as e:
        log.logger.error(str(e))
        raise typer.Exit(1)

    with utils.handle_cli_errors():
        client = github_client.GitHubClient(
            token=cfg.token,
            affiliation=cfg.affiliation,
            visibility=cfg.visibility,
            ignored_repos=cfg.ignored_repos,
        )

        language_stats = client.get_all_language_stats(
            repos_output=charts.get_output_path(
                cfg.output_dir, "repositories.json", save_json, stdout
            ),
            stats_output=charts.get_output_path(
                cfg.output_dir, "language_stats.json", save_json, stdout
            ),
            specific_repos=repos,
        )

        if not language_stats:
            log.logger.error("No language statistics found, nothing to visualize")
            raise typer.Exit(1)

        if stdout:
            print(json.dumps(language_stats, indent=2))
        elif json_only:
            charts.save_json_stats(language_stats, cfg.output_dir)
        else:
            charts.generate_charts(
                language_stats,
                cfg,
                title=charts.get_chart_title(repos, title, "GitHub"),
                output=output,
                style=style,
                top_n=top_n,
                save_json=save_json,
            )
