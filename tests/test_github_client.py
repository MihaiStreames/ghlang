"""Tests for GitHub client"""

import json
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests

from ghlang.github_client import GitHubClient


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def client() -> GitHubClient:
    """Create a GitHubClient with test token"""
    return GitHubClient(
        token="test_token",
        affiliation="owner",
        visibility="all",
        ignored_repos=[],
    )


@pytest.fixture
def client_with_ignores() -> GitHubClient:
    """Create a GitHubClient with ignored repos"""
    return GitHubClient(
        token="test_token",
        affiliation="owner",
        visibility="all",
        ignored_repos=["user/ignored-repo", "org/*-private"],
    )


@pytest.fixture
def linux_languages() -> dict[str, int]:
    """Load Linux kernel language stats fixture"""
    with (FIXTURES_DIR / "linux_languages.json").open() as f:
        return json.load(f)


@pytest.fixture
def rust_languages() -> dict[str, int]:
    """Load Rust language stats fixture"""
    with (FIXTURES_DIR / "rust_languages.json").open() as f:
        return json.load(f)


@pytest.fixture
def cpython_languages() -> dict[str, int]:
    """Load CPython language stats fixture"""
    with (FIXTURES_DIR / "cpython_languages.json").open() as f:
        return json.load(f)


class TestRepoPatternNormalization:
    """Tests for repo pattern normalization"""

    def test_normalize_https_url(self, client: GitHubClient):
        """Should strip https://github.com/ prefix"""
        result = client._normalize_repo_pattern("https://github.com/torvalds/linux")
        assert result == "torvalds/linux"

    def test_normalize_http_url(self, client: GitHubClient):
        """Should strip http://github.com/ prefix"""
        result = client._normalize_repo_pattern("http://github.com/rust-lang/rust")
        assert result == "rust-lang/rust"

    def test_normalize_github_com_prefix(self, client: GitHubClient):
        """Should strip github.com/ prefix without protocol"""
        result = client._normalize_repo_pattern("github.com/python/cpython")
        assert result == "python/cpython"

    def test_normalize_trailing_slash(self, client: GitHubClient):
        """Should strip trailing slash"""
        result = client._normalize_repo_pattern("https://github.com/user/repo/")
        assert result == "user/repo"

    def test_normalize_plain_name(self, client: GitHubClient):
        """Should leave plain owner/repo unchanged"""
        result = client._normalize_repo_pattern("owner/repo")
        assert result == "owner/repo"


class TestRepoNameValidation:
    """Tests for repo name validation"""

    def test_valid_simple_name(self, client: GitHubClient):
        """Should accept valid owner/repo format"""
        assert client._validate_repo_name("torvalds/linux") is True

    def test_valid_with_hyphens(self, client: GitHubClient):
        """Should accept names with hyphens"""
        assert client._validate_repo_name("rust-lang/rust") is True

    def test_valid_with_dots(self, client: GitHubClient):
        """Should accept names with dots"""
        assert client._validate_repo_name("user/repo.js") is True

    def test_valid_with_underscores(self, client: GitHubClient):
        """Should accept names with underscores"""
        assert client._validate_repo_name("my_org/my_repo") is True

    def test_invalid_no_slash(self, client: GitHubClient):
        """Should reject names without slash"""
        assert client._validate_repo_name("just-repo-name") is False

    def test_invalid_multiple_slashes(self, client: GitHubClient):
        """Should reject names with multiple slashes"""
        assert client._validate_repo_name("owner/repo/extra") is False

    def test_invalid_too_long(self, client: GitHubClient):
        """Should reject names over 100 characters"""
        long_name = "a" * 50 + "/" + "b" * 51
        assert client._validate_repo_name(long_name) is False


class TestRepoIgnoring:
    """Tests for repo ignore patterns"""

    def test_exact_match_ignored(self, client_with_ignores: GitHubClient):
        """Should ignore exact match"""
        assert client_with_ignores._should_ignore_repo("user/ignored-repo") is True

    def test_wildcard_match_ignored(self, client_with_ignores: GitHubClient):
        """Should ignore wildcard match"""
        assert client_with_ignores._should_ignore_repo("org/something-private") is True
        assert client_with_ignores._should_ignore_repo("org/another-private") is True

    def test_non_matching_not_ignored(self, client_with_ignores: GitHubClient):
        """Should not ignore non-matching repos"""
        assert client_with_ignores._should_ignore_repo("user/other-repo") is False
        assert client_with_ignores._should_ignore_repo("org/public-repo") is False

    def test_case_insensitive_match(self, client_with_ignores: GitHubClient):
        """Should match case-insensitively"""
        assert client_with_ignores._should_ignore_repo("USER/IGNORED-REPO") is True
        assert client_with_ignores._should_ignore_repo("User/Ignored-Repo") is True


class TestLanguageStatsParsing:
    """Tests for language stats processing with real fixture data"""

    def test_linux_languages_structure(self, linux_languages: dict[str, int]):
        """Linux fixture should have expected structure"""
        assert "C" in linux_languages
        assert "Assembly" in linux_languages
        assert "Rust" in linux_languages
        assert isinstance(linux_languages["C"], int)
        assert linux_languages["C"] > 1_000_000_000

    def test_rust_languages_structure(self, rust_languages: dict[str, int]):
        """Rust fixture should have expected structure"""
        assert "Rust" in rust_languages
        assert "HTML" in rust_languages
        assert isinstance(rust_languages["Rust"], int)
        assert rust_languages["Rust"] > 100_000_000

    def test_cpython_languages_structure(self, cpython_languages: dict[str, int]):
        """CPython fixture should have expected structure"""
        assert "Python" in cpython_languages
        assert "C" in cpython_languages
        assert isinstance(cpython_languages["Python"], int)
        assert cpython_languages["Python"] > 30_000_000


class TestMockedAPIRequests:
    """Tests with mocked HTTP responses"""

    def test_get_repo_languages_success(
        self, client: GitHubClient, linux_languages: dict[str, int]
    ):
        """Should parse language response correctly"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = linux_languages
        mock_response.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        with patch.object(client._session, "get", return_value=mock_response):
            result = client._get_repo_languages("torvalds/linux")

        assert result == linux_languages
        assert result["C"] == linux_languages["C"]

    def test_get_repo_languages_rate_limit_recovery(self, client: GitHubClient):
        """Should recover from rate limit"""
        rate_limited_response = MagicMock()
        rate_limited_response.status_code = 403
        rate_limited_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "0",
        }

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"Python": 1000}
        success_response.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        with (
            patch.object(
                client._session, "get", side_effect=[rate_limited_response, success_response]
            ),
            patch("time.sleep"),
        ):
            result = client._get_repo_languages("user/repo")

        assert result == {"Python": 1000}

    def test_get_repo_languages_retry_on_500(self, client: GitHubClient):
        """Should retry on server errors"""
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.headers = {}

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"JavaScript": 5000}
        success_response.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        with (
            patch.object(client._session, "get", side_effect=[error_response, success_response]),
            patch("time.sleep"),
        ):
            result = client._get_repo_languages("user/repo")

        assert result == {"JavaScript": 5000}


class TestStatsAggregation:
    """Tests for aggregating stats from multiple repos"""

    def test_aggregate_multiple_repos(
        self,
        client: GitHubClient,
        linux_languages: dict[str, int],
        rust_languages: dict[str, int],
        cpython_languages: dict[str, int],
    ):
        """Should correctly aggregate language bytes across repos"""
        repos = [
            {"full_name": "torvalds/linux"},
            {"full_name": "rust-lang/rust"},
            {"full_name": "python/cpython"},
        ]

        def mock_get_languages(full_name: str) -> dict[str, int]:
            if full_name == "torvalds/linux":
                return linux_languages
            if full_name == "rust-lang/rust":
                return rust_languages
            if full_name == "python/cpython":
                return cpython_languages
            return {}

        with (
            patch.object(client, "_list_repos", return_value=repos),
            patch.object(client, "_get_repo_languages", side_effect=mock_get_languages),
        ):
            result = client.get_all_language_stats()

        expected_c = linux_languages["C"] + rust_languages["C"] + cpython_languages["C"]
        assert result["C"] == expected_c

        expected_rust = linux_languages["Rust"] + rust_languages["Rust"]
        assert result["Rust"] == expected_rust

        expected_python = (
            linux_languages["Python"] + rust_languages["Python"] + cpython_languages["Python"]
        )
        assert result["Python"] == expected_python

    def test_aggregate_empty_repos(self, client: GitHubClient):
        """Should return empty dict when no repos found"""
        with patch.object(client, "_list_repos", return_value=[]):
            result = client.get_all_language_stats()

        assert result == {}

    def test_aggregate_skips_failed_repos(
        self, client: GitHubClient, linux_languages: dict[str, int]
    ):
        """Should skip repos that fail and continue with others"""
        repos = [
            {"full_name": "torvalds/linux"},
            {"full_name": "private/repo"},
        ]

        def mock_get_languages(full_name: str) -> dict[str, int]:
            if full_name == "torvalds/linux":
                return linux_languages
            raise requests.HTTPError("Access denied")

        with (
            patch.object(client, "_list_repos", return_value=repos),
            patch.object(client, "_get_repo_languages", side_effect=mock_get_languages),
        ):
            result = client.get_all_language_stats()

        assert result["C"] == linux_languages["C"]
