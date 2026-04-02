from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import fnmatch
import json
from pathlib import Path
import re
import time

import requests

from . import constants
from . import log


class GitHubClient:
    """Client for interacting with the GitHub REST API.

    Attributes
    ----------
    _api : str
        Base URL for the GitHub API.
    _session : requests.Session
        Authenticated HTTP session with GitHub headers.
    _affiliation : str
        Repo affiliation filter.
    _visibility : str
        Repo visibility filter.
    _ignored_repos : list[str]
        Glob patterns for repos to skip.
    """

    def __init__(
        self,
        token: str,
        affiliation: str,
        visibility: str,
        ignored_repos: list[str],
    ):
        self._api = constants.API_URL
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": constants.API_VERSION,
            }
        )
        self._affiliation = affiliation
        self._visibility = visibility
        self._ignored_repos = ignored_repos
        self._per_page = constants.API_PER_PAGE
        self._max_retries = constants.API_MAX_RETRIES
        self._base_delay = constants.API_BASE_DELAY

    def _log_rate_limit(self, response: requests.Response) -> None:
        """Log remaining API rate limit from response headers"""
        remaining = response.headers.get("X-RateLimit-Remaining")
        limit = response.headers.get("X-RateLimit-Limit")

        if remaining and limit:
            log.logger.debug(f"Rate limit: {remaining}/{limit} remaining")

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        """Send GET request with retry and rate-limit handling"""
        r = None
        for attempt in range(self._max_retries):
            r = self._session.get(url, params=params)
            self._log_rate_limit(r)

            if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(r.headers.get("X-RateLimit-Reset", "0"))
                sleep_for = max(0, reset - int(time.time()) + 2)
                log.logger.warning(f"Rate limit hit, waiting {sleep_for}s until reset...")
                time.sleep(sleep_for)
                continue

            if r.status_code in (429, 500, 502, 503, 504):
                delay = self._base_delay * (2**attempt)
                log.logger.warning(
                    f"Got {r.status_code}, retrying in {delay}s "
                    f"(attempt {attempt + 1}/{self._max_retries})..."
                )
                time.sleep(delay)
                continue

            r.raise_for_status()
            return r

        if r is not None:
            r.raise_for_status()
        return r  # type: ignore[return-value]

    def _normalize_repo_pattern(self, pattern: str) -> str:
        """Strip GitHub URL prefixes to get owner/repo"""
        prefixes = ["https://github.com/", "http://github.com/", "github.com/"]

        for prefix in prefixes:
            if pattern.startswith(prefix):
                return pattern[len(prefix) :].rstrip("/")

        return pattern

    def _validate_repo_name(self, repo_name: str) -> bool:
        """Check that repo_name matches owner/repo format"""
        pattern = r"^[\w\-\.]+/[\w\-\.]+$"
        return bool(re.match(pattern, repo_name)) and len(repo_name) <= 100

    def _should_ignore_repo(self, full_name: str) -> bool:
        """Return True if full_name matches any ignored-repo glob"""
        for pattern in self._ignored_repos:
            normalized = self._normalize_repo_pattern(pattern)

            if fnmatch.fnmatch(full_name, normalized):
                return True
            if fnmatch.fnmatch(full_name.lower(), normalized.lower()):
                return True

        return False

    def _get_repo_info(self, full_name: str) -> dict:
        """Fetch metadata for a single repo"""
        if not self._validate_repo_name(full_name):
            raise ValueError(f"Invalid repository name format: {full_name}")
        r = self._get(f"{self._api}/repos/{full_name}")
        return dict(r.json())

    def _list_repos(self, output_file: Path | None = None) -> list[dict]:
        """Paginate all repos matching affiliation/visibility filters"""
        log.logger.info("Fetching repos")
        repos = []
        page = 1

        with log.logger.spinner() as progress:
            task = progress.add_task("Fetching repos...", total=None)

            while True:
                progress.update(task, description=f"Fetching repos (page {page})...")

                r = self._get(
                    f"{self._api}/user/repos",
                    params={
                        "per_page": self._per_page,
                        "page": page,
                        "affiliation": self._affiliation,
                        "visibility": self._visibility,
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
                log.logger.debug(f"Ignoring repo: {fn}")
                ignored_count += 1
                continue

            unique_repos.append(repo)

        log.logger.info(f"Found {len(unique_repos)} repos ({ignored_count} ignored)")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w") as f:
                json.dump(unique_repos, f, indent=2)

            log.logger.debug(f"Saved repository data to {output_file}")

        return unique_repos

    def _get_repo_languages(self, full_name: str) -> dict[str, int]:
        """Fetch byte-count language breakdown for a single repo"""
        r = self._get(f"{self._api}/repos/{full_name}/languages")
        return dict(r.json())

    def _fetch_specific_repos(self, specific_repos: list[str]) -> list[dict]:
        """Resolve a list of owner/repo strings to repo dicts"""
        repos = []
        for repo_name in specific_repos:
            normalized = self._normalize_repo_pattern(repo_name)

            try:
                repo = self._get_repo_info(normalized)
                repos.append(repo)
                log.logger.debug(f"Found repo: {normalized}")

            except ValueError as e:
                log.logger.warning(str(e))
            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response else None

                if status_code == 404:
                    log.logger.warning(f"Repository not found: {normalized}")
                elif status_code == 403:
                    log.logger.warning(f"Access denied to {normalized} (check permissions)")
                else:
                    log.logger.warning(f"Failed to fetch {normalized}: {e}")
            except requests.RequestException as e:
                log.logger.warning(f"Network error fetching {normalized}: {e}")

        return repos

    def get_all_language_stats(
        self,
        repos_output: Path | None = None,
        stats_output: Path | None = None,
        specific_repos: list[str] | None = None,
    ) -> dict[str, int]:
        """Aggregate language byte counts across all repos or specific ones

        Parameters
        ----------
        repos_output : Path | None
            If given, write the repo list JSON to this path.
        stats_output : Path | None
            If given, write the aggregated stats JSON to this path.
        specific_repos : list[str] | None
            Explicit owner/repo names. When *None*, all repos matching the
            client's affiliation/visibility filters are used.

        Returns
        -------
        dict[str, int]
            Language name to total byte count. Empty dict when no repos found.
        """
        if specific_repos:
            log.logger.info(f"Fetching {len(specific_repos)} specific repos")
            repos = self._fetch_specific_repos(specific_repos)

            if repos_output:
                repos_output.parent.mkdir(parents=True, exist_ok=True)

                with repos_output.open("w") as f:
                    json.dump(repos, f, indent=2)

                log.logger.debug(f"Saved repository data to {repos_output}")
        else:
            repos = self._list_repos(output_file=repos_output)

        if not repos:
            log.logger.warning("No repositories found, nothing to do")
            return {}

        totals: defaultdict[str, int] = defaultdict(int)
        processed = 0
        skipped = 0

        # 10x speedup, no need for more
        # could be made configurable later if needed
        num_workers = min(constants.API_MAX_WORKERS, len(repos))
        log.logger.debug(f"Using {num_workers} concurrent workers for {len(repos)} repos")

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_repo = {
                executor.submit(self._get_repo_languages, repo["full_name"]): repo for repo in repos
            }

            with log.logger.progress() as progress:
                task = progress.add_task("Processing repos", total=len(repos))

                for future in as_completed(future_to_repo):
                    repo = future_to_repo[future]
                    full_name = repo["full_name"]

                    try:
                        langs = future.result()

                        for lang, bytes_count in langs.items():
                            totals[lang] += int(bytes_count)

                        processed += 1
                        log.logger.debug(f"Processed {full_name}")

                    except requests.HTTPError as e:
                        skipped += 1
                        log.logger.warning(f"Skipped {full_name}: {e}")
                    except Exception as e:
                        skipped += 1
                        log.logger.warning(f"Skipped {full_name}: {e}")

                    progress.advance(task)

        log.logger.success(f"Processed {processed} repositories ({skipped} skipped)")

        result = dict(totals)
        if stats_output:
            stats_output.parent.mkdir(parents=True, exist_ok=True)

            with stats_output.open("w") as f:
                json.dump(result, f, indent=2)

            log.logger.debug(f"Saved language statistics to {stats_output}")

        return result
