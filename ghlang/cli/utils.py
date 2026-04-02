from __future__ import annotations

from collections.abc import Iterator
import contextlib
from contextlib import contextmanager
import json
from pathlib import Path
from typing import TYPE_CHECKING

import typer

from ghlang import config
from ghlang import log
from ghlang import styles
from ghlang.static import themes as static_themes


if TYPE_CHECKING:
    from ghlang.config import Config


def get_config_dir() -> Path:
    """Get the config directory path"""
    return config.get_config_path().parent


def get_active_theme() -> str:
    """Get the currently active theme name"""
    try:
        return config.load_config(require_token=False).theme
    except Exception:
        return "light"


def load_themes_by_source(
    config_dir: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Return (built-in, remote, custom) theme dicts loaded independently"""
    built_in: dict[str, dict[str, str]] = dict(static_themes.THEMES)

    remote: dict[str, dict[str, str]] = {}
    remote_path = config_dir / "themes.json"
    if remote_path.exists():
        with contextlib.suppress(Exception):
            remote = json.loads(remote_path.read_text())

    custom: dict[str, dict[str, str]] = {}
    custom_path = config_dir / "custom_themes.json"
    if custom_path.exists():
        with contextlib.suppress(Exception):
            custom = json.loads(custom_path.read_text())

    return built_in, remote, custom


def format_autocomplete(incomplete: str) -> list[str]:
    """Callback for output formats"""
    return [f for f in ["png", "svg"] if f.startswith(incomplete)]


def themes_autocomplete(incomplete: str) -> list[str]:
    """Callback for theme names"""
    themes = list(static_themes.THEMES.keys())

    config_path = config.get_config_path()
    remote_path = config_path.parent / "themes.json"
    if remote_path.exists():
        try:
            with remote_path.open() as f:
                remote = json.load(f)
            themes.extend(remote.keys())

        except Exception:
            pass

    return [t for t in themes if t.startswith(incomplete)]


def styles_autocomplete(incomplete: str) -> list[str]:
    """Callback for chart styles"""
    return [s for s in styles.STYLES if s.startswith(incomplete)]


def setup_cli_environment(
    config_path: Path | None,
    output_dir: Path | None,
    verbose: bool,
    theme: str | None,
    stdout: bool,
    quiet: bool,
    require_token: bool,
) -> tuple[Config, bool, bool]:
    """Common CLI setup tasks"""
    if stdout:
        quiet = True
        json_only = True
    else:
        json_only = False

    log.logger.configure(verbose, quiet=quiet)

    cli_overrides = {
        "output_dir": output_dir,
        "verbose": verbose or None,
        "theme": theme,
    }

    cfg = config.load_config(
        config_path=config_path,
        cli_overrides=cli_overrides,
        require_token=require_token,
    )

    log.logger.configure(cfg.verbose, quiet=quiet)

    if not stdout:
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        log.logger.info(f"Saving to {cfg.output_dir}")

    return cfg, quiet, json_only


@contextmanager
def handle_cli_errors() -> Iterator[None]:
    """Context manager for handling CLI exceptions"""
    try:
        yield
    except typer.Exit:
        raise
    except Exception as e:
        log.logger.exception(f"Something went wrong: {e}")
        raise typer.Exit(1)
