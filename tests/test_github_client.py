import json
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ghlang import exceptions
from ghlang.net.github import GitHubClient


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_language_fixture(filename: str) -> dict[str, int]:
    with (FIXTURES_DIR / filename).open() as f:
        return cast(dict[str, int], json.load(f))


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
    return _load_language_fixture("linux_languages.json")


@pytest.fixture
def rust_languages() -> dict[str, int]:
    """Load Rust language stats fixture"""
    return _load_language_fixture("rust_languages.json")


@pytest.fixture
def cpython_languages() -> dict[str, int]:
    """Load CPython language stats fixture"""
    return _load_language_fixture("cpython_languages.json")


class TestRepoPatternNormalization:
    """Tests for repo pattern normalization"""

    def test_normalize_https_url(self, client: GitHubClient) -> None:
        """Should strip https://github.com/ prefix"""
        result = client._normalize_repo_pattern("https://github.com/torvalds/linux")
        assert result == "torvalds/linux"

    def test_normalize_http_url(self, client: GitHubClient) -> None:
        """Should strip http://github.com/ prefix"""
        result = client._normalize_repo_pattern("http://github.com/rust-lang/rust")
        assert result == "rust-lang/rust"

    def test_normalize_github_com_prefix(self, client: GitHubClient) -> None:
        """Should strip github.com/ prefix without protocol"""
        result = client._normalize_repo_pattern("github.com/python/cpython")
        assert result == "python/cpython"

    def test_normalize_trailing_slash(self, client: GitHubClient) -> None:
        """Should strip trailing slash"""
        result = client._normalize_repo_pattern("https://github.com/user/repo/")
        assert result == "user/repo"


class TestRepoNameValidation:
    """Tests for repo name validation"""

    def test_valid_simple_name(self, client: GitHubClient) -> None:
        """Should accept valid owner/repo format"""
        assert client._validate_repo_name("torvalds/linux") is True

    @pytest.mark.parametrize(
        "name",
        ["rust-lang/rust", "user/repo.js", "my_org/my_repo"],
        ids=["hyphens", "dots", "underscores"],
    )
    def test_valid_with_special_chars(self, client: GitHubClient, name: str) -> None:
        """Should accept names with hyphens, dots, and underscores"""
        assert client._validate_repo_name(name) is True

    def test_invalid_no_slash(self, client: GitHubClient) -> None:
        """Should reject names without slash"""
        assert client._validate_repo_name("just-repo-name") is False

    def test_invalid_multiple_slashes(self, client: GitHubClient) -> None:
        """Should reject names with multiple slashes"""
        assert client._validate_repo_name("owner/repo/extra") is False

    def test_invalid_too_long(self, client: GitHubClient) -> None:
        """Should reject names over 100 characters"""
        long_name = "a" * 50 + "/" + "b" * 51
        assert client._validate_repo_name(long_name) is False


class TestRepoIgnoring:
    """Tests for repo ignore patterns"""

    def test_exact_match_ignored(self, client_with_ignores: GitHubClient) -> None:
        """Should ignore exact match"""
        assert client_with_ignores._should_ignore_repo("user/ignored-repo") is True

    def test_wildcard_match_ignored(self, client_with_ignores: GitHubClient) -> None:
        """Should ignore wildcard match"""
        assert client_with_ignores._should_ignore_repo("org/something-private") is True
        assert client_with_ignores._should_ignore_repo("org/another-private") is True

    def test_non_matching_not_ignored(self, client_with_ignores: GitHubClient) -> None:
        """Should not ignore non-matching repos"""
        assert client_with_ignores._should_ignore_repo("user/other-repo") is False
        assert client_with_ignores._should_ignore_repo("org/public-repo") is False

    def test_case_insensitive_match(self, client_with_ignores: GitHubClient) -> None:
        """Should match case-insensitively"""
        assert client_with_ignores._should_ignore_repo("USER/IGNORED-REPO") is True
        assert client_with_ignores._should_ignore_repo("User/Ignored-Repo") is True


class TestMockedAPIRequests:
    """Tests with mocked HTTP responses"""

    def test_get_repo_languages_success(
        self, client: GitHubClient, linux_languages: dict[str, int]
    ) -> None:
        """Should parse language response correctly"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = linux_languages
        mock_response.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        with patch.object(client._session, "get", return_value=mock_response):
            result = client.get_repo_languages("torvalds/linux")

        assert result == linux_languages
        assert result["C"] == linux_languages["C"]

    def test_list_repos_filters_ignored(self, client_with_ignores: GitHubClient) -> None:
        """Should filter ignored repos from the list"""
        page_1 = [
            {"full_name": "user/good-repo"},
            {"full_name": "user/ignored-repo"},
            {"full_name": "org/something-private"},
        ]

        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = page_1
        mock_response_1.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = []
        mock_response_2.headers = {"X-RateLimit-Remaining": "4998", "X-RateLimit-Limit": "5000"}

        with patch.object(
            client_with_ignores._session,
            "get",
            side_effect=[mock_response_1, mock_response_2],
        ):
            repos = client_with_ignores.list_repos()

        assert len(repos) == 1
        assert repos[0]["full_name"] == "user/good-repo"

    def test_fetch_specific_repos_skips_not_found(self, client: GitHubClient) -> None:
        """Should skip repos that return 404"""
        good_response = MagicMock()
        good_response.status_code = 200
        good_response.json.return_value = {"full_name": "user/good"}
        good_response.headers = {"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"}

        not_found = exceptions.HTTPError(MagicMock(status_code=404, url="user/gone"))

        with patch.object(client._session, "get", side_effect=[good_response, not_found]):
            repos = client.fetch_specific_repos(["user/good", "user/gone"])

        assert len(repos) == 1
        assert repos[0]["full_name"] == "user/good"
