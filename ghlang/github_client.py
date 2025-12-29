from collections import defaultdict
import fnmatch
import json
from pathlib import Path
import time

from loguru import logger
import requests


class GitHubClient:
    """Client for interacting with GitHub API"""

    def __init__(
        self,
        token: str,
        affiliation: str,
        visibility: str,
        ignored_repos: list[str],
    ):
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
        self.ignored_repos = ignored_repos
        self.per_page = 100

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        """Make a GET request with rate limit handling"""
        r = self.session.get(url, params=params)

        if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers.get("X-RateLimit-Reset", "0"))
            sleep_for = max(0, reset - int(time.time()) + 2)
            logger.warning(f"Rate limited, sleeping for {sleep_for}s...")
            time.sleep(sleep_for)
            r = self.session.get(url, params=params)

        r.raise_for_status()
        return r

    def _normalize_repo_pattern(self, pattern: str) -> str:
        """Strip GitHub URL prefix from pattern if present"""
        prefixes = ["https://github.com/", "http://github.com/", "github.com/"]

        for prefix in prefixes:
            if pattern.startswith(prefix):
                return pattern[len(prefix) :].rstrip("/")

        return pattern

    def _should_ignore_repo(self, full_name: str) -> bool:
        """Check if a repo should be ignored based on ignore patterns"""
        for pattern in self.ignored_repos:
            normalized = self._normalize_repo_pattern(pattern)

            if fnmatch.fnmatch(full_name, normalized):
                return True
            if fnmatch.fnmatch(full_name.lower(), normalized.lower()):
                return True

        return False

    def list_repos(self, output_file: Path | None = None) -> list[dict]:
        """List all repos accessible to the authenticated user"""
        logger.info("Fetching repos")
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
        ignored_count = 0

        for repo in repos:
            fn = repo["full_name"]

            if fn in seen:
                continue

            seen.add(fn)

            if self._should_ignore_repo(fn):
                logger.debug(f"Ignoring repo: {fn}")
                ignored_count += 1
                continue

            unique_repos.append(repo)

        logger.info(f"Found {len(unique_repos)} repos ({ignored_count} ignored)")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w") as f:
                json.dump(unique_repos, f, indent=2)

            logger.debug(f"Saved repository data to {output_file}")

        return unique_repos

    def get_repo_languages(self, full_name: str) -> dict[str, int]:
        """Get language breakdown for a specific repo"""
        r = self._get(f"{self.api}/repos/{full_name}/languages")
        return r.json()

    def get_all_language_stats(
        self,
        repos_output: Path | None = None,
        stats_output: Path | None = None,
    ) -> dict[str, int]:
        """Get aggregated language statistics across all repos"""
        repos = self.list_repos(output_file=repos_output)
        if not repos:
            logger.warning("No repositories found, nothing to do")
            return {}

        totals = defaultdict(int)
        processed = 0
        skipped = 0

        logger.info("Fetching language stats for each repo")

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
