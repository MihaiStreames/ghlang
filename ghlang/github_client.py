from collections import defaultdict
import json
from pathlib import Path
import time

from loguru import logger
import requests
import yaml


class GitHubClient:
    """Client for interacting with GitHub API"""

    def __init__(
        self,
        token: str,
        affiliation: str = "owner,collaborator,organization_member",
        visibility: str = "all",
    ):
        """Initialize GitHub API client

        Args:
            token: GitHub personal access token
            affiliation: Comma-separated list of affiliations to filter repos
            visibility: Repository visibility filter ('all', 'public', or 'private')
        """
        self.api = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        self.affiliation = affiliation
        self.visibility = visibility
        self.per_page = 100

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        """Make a GET request with rate limit handling

        Args:
            url: API endpoint URL
            params: Optional query parameters

        Returns:
            Response object from the API

        Raises:
            requests.HTTPError: If the request fails after rate limit handling
        """
        r = self.session.get(url, params=params)

        if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers.get("X-RateLimit-Reset", "0"))
            sleep_for = max(0, reset - int(time.time()) + 2)
            logger.warning(f"Rate limited. Sleeping for {sleep_for} seconds...")
            time.sleep(sleep_for)
            r = self.session.get(url, params=params)

        r.raise_for_status()
        return r

    def list_repos(self, output_file: Path | None = None) -> list[dict]:
        """List all repos accessible to the authenticated user

        Args:
            output_file: Optional path to save repository list as JSON

        Returns:
            List of repository dictionaries from GitHub API
        """
        logger.info("Fetching repositories...")
        repos = []
        page = 1

        while True:
            logger.debug(f"Fetching page {page}...")
            r = self._get(
                f"{self.api}/user/repos",
                params={
                    "per_page": self.per_page,
                    "page": page,
                    "affiliation": self.affiliation,
                    "visibility": self.visibility,
                    "sort": "pushed",
                    "direction": "desc",
                },
            )

            batch = r.json()
            if not batch:
                break

            repos.extend(batch)
            page += 1

        seen = set()
        unique_repos = []
        for repo in repos:
            fn = repo["full_name"]  # dedup by full_name
            if fn not in seen:
                seen.add(fn)
                unique_repos.append(repo)

        logger.info(f"Found {len(unique_repos)} unique repositories")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("w") as f:
                json.dump(unique_repos, f, indent=2)
            logger.debug(f"Saved repository data to {output_file}")

        return unique_repos

    def get_repo_languages(self, full_name: str) -> dict[str, int]:
        """Get language breakdown for a specific repo

        Args:
            full_name: Full repository name (owner/repo)

        Returns:
            Dictionary mapping language names to byte counts
        """
        r = self._get(f"{self.api}/repos/{full_name}/languages")
        return r.json()

    def get_all_language_stats(
        self,
        repos_output: Path | None = None,
        stats_output: Path | None = None,
    ) -> dict[str, int]:
        """Get aggregated language statistics across all repos

        Args:
            repos_output: Optional path to save repository list as JSON
            stats_output: Optional path to save language stats as JSON

        Returns:
            Dictionary mapping language names to total byte counts
        """
        repos = self.list_repos(output_file=repos_output)
        if not repos:
            logger.warning("No repositories found")
            return {}

        totals = defaultdict(int)
        processed = 0
        skipped = 0

        logger.info("Fetching language statistics for each repository...")
        for repo in repos:
            full_name = repo["full_name"]
            try:
                langs = self.get_repo_languages(full_name)
                for lang, bytes_count in langs.items():
                    totals[lang] += int(bytes_count)
                processed += 1
                logger.debug(f"Processed {full_name}")
            except requests.HTTPError as e:
                skipped += 1
                logger.warning(f"Skipped {full_name}: {e}")

        logger.success(f"Processed {processed} repositories ({skipped} skipped)")

        result = dict(totals)
        if stats_output:
            stats_output.parent.mkdir(parents=True, exist_ok=True)
            with stats_output.open("w") as f:
                json.dump(result, f, indent=2)
            logger.debug(f"Saved language statistics to {stats_output}")

        return result


def load_github_colors(output_file: Path | None = None) -> dict[str, str]:
    """Fetch and parse GitHub's language colors from linguist YAML

    Args:
        output_file: Optional path to save color data as JSON

    Returns:
        Dictionary mapping language names to hex color codes
    """
    url = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"

    logger.info("Loading GitHub language colors...")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = yaml.safe_load(r.text)
        colors = {}

        for lang, props in data.items():
            if isinstance(props, dict) and "color" in props:
                colors[lang] = props["color"]

        logger.success(f"Loaded {len(colors)} language colors")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("w") as f:
                json.dump(colors, f, indent=2)
            logger.debug(f"Saved color data to {output_file}")

        return colors

    except Exception as e:
        logger.error(f"Could not load GitHub colors: {e}")
        return {}
