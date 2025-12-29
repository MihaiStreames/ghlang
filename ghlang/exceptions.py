class GhlangError(Exception):
    """Base exception for ghlang"""


class ConfigError(GhlangError):
    """Raised when config is invalid or missing"""


class MissingTokenError(ConfigError):
    """Raised when GitHub token is not configured"""

    def __init__(self, config_path: str | None = None):
        msg = "It looks like your GitHub token isn't set up yet!\n"

        if config_path:
            msg += f"Add it to: {config_path}\n"

        msg += "Generate one at: https://github.com/settings/tokens"
        super().__init__(msg)


class ClocNotFoundError(GhlangError):
    """Raised when cloc is not installed"""

    def __init__(self):
        super().__init__(
            "It seems cloc is missing...\nInstall it from: https://github.com/AlDanial/cloc"
        )
