from pathlib import Path
import tomllib

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Create a temporary config file"""
    config_file = tmp_path / "config.toml"
    return config_file


@pytest.fixture
def valid_config_content() -> str:
    """Valid TOML config content"""
    configs = tomllib.loads((FIXTURES_DIR / "configs.toml").read_text())
    return configs["valid"]["content"]


@pytest.fixture
def minimal_config_content() -> str:
    """Minimal valid config with just a token"""
    configs = tomllib.loads((FIXTURES_DIR / "configs.toml").read_text())
    return configs["minimal"]["content"]
