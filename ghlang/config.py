from dataclasses import dataclass
from dataclasses import field
from importlib import resources
from pathlib import Path
import sys
import tomllib

from loguru import logger

from ghlang.exceptions import ConfigError
from ghlang.exceptions import MissingTokenError


DEFAULT_IGNORED_DIRS = ["node_modules", "vendor", ".git", "dist", "build", "__pycache__"]
DEFAULT_OUTPUT_DIR = "~/Documents/ghlang-stats"


@dataclass
class Config:
    """Configuration for the language stats"""

    # GitHub settings
    token: str = ""
    affiliation: str = "owner,collaborator,organization_member"
    visibility: str = "all"
    ignored_repos: list[str] = field(default_factory=list)

    # Cloc settings
    ignored_dirs: list[str] = field(default_factory=lambda: DEFAULT_IGNORED_DIRS.copy())

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path(DEFAULT_OUTPUT_DIR))
    save_json: bool = True
    save_repos: bool = True
    top_n_languages: int = 5

    # Preferences
    verbose: bool = False
    theme: str = "light"


def get_config_path() -> Path:
    """Get the platform-specific config file path"""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".config"

    return base / "ghlang" / "config.toml"


def create_default_config(config_path: Path) -> None:
    """Create a default config file from template"""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_content = resources.files("ghlang.static").joinpath("default_config.toml").read_text()

    config_path.write_text(default_content)
    logger.debug(f"Created default config at: {config_path}")


def load_config(
    config_path: Path | None = None,
    cli_overrides: dict | None = None,
    require_token: bool = True,
) -> Config:
    """Load config from TOML file with optional CLI overrides"""
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        create_default_config(config_path)

        if require_token:
            raise MissingTokenError(str(config_path))

        logger.debug(f"Config file created at: {config_path}")

    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)

    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in config file: {e}") from e

    github = data.get("github", {})
    cloc = data.get("cloc", {})
    output = data.get("output", {})
    preferences = data.get("preferences", {})

    token = github.get("token", "")

    if require_token and (not token or token == "YOUR_TOKEN_HERE"):
        raise MissingTokenError()

    config = Config(
        token=token if token != "YOUR_TOKEN_HERE" else "",
        affiliation=github.get("affiliation", Config.affiliation),
        visibility=github.get("visibility", Config.visibility),
        ignored_repos=github.get("ignored_repos", []),
        ignored_dirs=cloc.get("ignored_dirs", DEFAULT_IGNORED_DIRS.copy()),
        output_dir=Path(output.get("directory", DEFAULT_OUTPUT_DIR)).expanduser(),
        save_json=output.get("save_json", Config.save_json),
        save_repos=output.get("save_repos", Config.save_repos),
        top_n_languages=output.get("top_n_languages", Config.top_n_languages),
        verbose=preferences.get("verbose", Config.verbose),
        theme=preferences.get("theme", Config.theme),
    )

    if cli_overrides:
        for key, value in cli_overrides.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

    return config
