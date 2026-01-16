"""Shared pytest fixtures"""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Create a temporary config file"""
    config_file = tmp_path / "config.toml"
    return config_file


@pytest.fixture
def valid_config_content() -> str:
    """Valid TOML config content"""
    return """
[github]
token = "ghp_test_token_12345"
affiliation = "owner"
visibility = "public"
ignored_repos = ["test-repo", "another-repo"]

[tokount]
ignored_dirs = ["node_modules", ".git"]

[output]
directory = "~/test-output"

[preferences]
verbose = true
theme = "dark"
"""


@pytest.fixture
def minimal_config_content() -> str:
    """Minimal valid config with just a token"""
    return """
[github]
token = "ghp_test_token_12345"
"""
