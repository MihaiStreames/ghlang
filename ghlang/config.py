from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib

from loguru import logger


@dataclass
class Config:
    """Configuration for GitHub language stats"""

    # GitHub settings
    token: str
    affiliation: str = "owner,collaborator,organization_member"
    visibility: str = "all"

    # Output settings
    output_dir: Path = Path("~/Documents/ghlang-stats")
    save_json: bool = True
    save_repos: bool = True
    top_n_languages: int = 5

    # Preferences
    verbose: bool = False


class ConfigError(Exception):
    """Raised when config is invalid or missing"""


def get_config_path() -> Path:
    """Get the path to the config file

    Returns:
        Path to the platform-specific config file location
    """
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".config"

    return base / "ghlang" / "config.toml"


def create_default_config(config_path: Path) -> None:
    """Create a default config file with instructions

    Args:
        config_path: Path where the config file should be created
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_content = """
[github]
token = "YOUR_TOKEN_HERE"
affiliation = "owner,collaborator,organization_member"
visibility = "all"

[output]
directory = "~/Documents/ghlang-stats"
save_json = false
save_repos = false
top_n_languages = 5

[preferences]
verbose = false
"""

    config_path.write_text(default_content)
    logger.info(f"Created default config at: {config_path}")


def load_config(config_path: Path | None = None, cli_overrides: dict | None = None) -> Config:
    """Load config from TOML file with optional CLI overrides

    Args:
        config_path: Optional custom config path. Defaults to platform-specific location
        cli_overrides: Optional dict of CLI arguments to override config values

    Returns:
        Loaded configuration object

    Raises:
        ConfigError: If config doesn't exist or token is invalid
    """
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        create_default_config(config_path)
        raise ConfigError(
            f"Config file created at: {config_path}\n"
            "Please edit it and add your GitHub token, then run ghlang again"
        )

    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in config file: {e}") from e

    if "github" not in data:
        raise ConfigError("Missing [github] section in config")

    github = data["github"]
    output = data.get("output", {})
    preferences = data.get("preferences", {})

    token = github.get("token", "")
    if not token or token == "YOUR_TOKEN_HERE":
        raise ConfigError(
            f"Please set your GitHub token in: {config_path}\n"
            "Get a token from: https://github.com/settings/tokens"
        )

    config = Config(
        token=token,
        affiliation=github.get("affiliation", Config.affiliation),
        visibility=github.get("visibility", Config.visibility),
        output_dir=Path(output.get("directory", "~/Documents/ghlang-stats")).expanduser(),
        save_json=output.get("save_json", True),
        save_repos=output.get("save_repos", True),
        top_n_languages=output.get("top_n_languages", 5),
        verbose=preferences.get("verbose", False),
    )

    if cli_overrides:
        for key, value in cli_overrides.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

    return config
