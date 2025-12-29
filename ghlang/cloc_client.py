import json
from pathlib import Path
import shutil
import subprocess

from loguru import logger

from ghlang.exceptions import ClocNotFoundError


class ClocClient:
    """Client for running cloc on local files/directories"""

    def _check_cloc_installed(self) -> None:
        """Check if cloc is installed and accessible"""
        if shutil.which("cloc") is None:
            raise ClocNotFoundError()

    def __init__(self, ignored_dirs: list[str]):
        self.ignored_dirs = ignored_dirs
        self._check_cloc_installed()

    def _is_git_repo(self, path: Path) -> bool:
        """Check if path is inside a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=False,
                cwd=path if path.is_dir() else path.parent,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0

        except Exception:
            return False

    def _build_cloc_command(self, path: Path) -> list[str]:
        """Build the cloc command with appropriate flags"""
        cmd = ["cloc", "--json"]

        if self.ignored_dirs:
            cmd.append(f"--exclude-dir={','.join(self.ignored_dirs)}")

        # TODO: handle symlinks
        # cmd.append("--follow-links") (only on unix)
        
        # TODO: handle mixed tree types (git + non-git)
        # will have to figure out how to recursively check each subdir
        # (we can probably skip this for now since most use cases are simple)
        # we'd pass the paths using a temp file and --list-file=<tempfile>
        
        if path.is_dir() and self._is_git_repo(path):
            cmd.append("--vcs=git")
            cmd.append(str(path))
        else:
            cmd.append(str(path))

        return cmd

    def analyze_path(self, path: Path) -> dict:
        """Run cloc on a file or directory and return raw JSON output"""
        path = path.resolve()

        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        cmd = self._build_cloc_command(path)
        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            cwd=path if path.is_dir() else path.parent,
        )

        if result.returncode != 0:
            logger.debug(f"cloc stderr: {result.stderr}")
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

        try:
            return json.loads(result.stdout)

        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse cloc output: {result.stdout[:500]}")
            raise ValueError(f"Invalid JSON from cloc: {e}") from e

    def get_language_stats(
        self,
        path: Path,
        stats_output: Path | None = None,
    ) -> dict[str, dict]:
        """Get language statistics for a path"""
        logger.info(f"Analyzing {path}")

        raw_output = self.analyze_path(path)

        if stats_output:
            stats_output.parent.mkdir(parents=True, exist_ok=True)

            with stats_output.open("w") as f:
                json.dump(raw_output, f, indent=2)

            logger.debug(f"Saved raw cloc output to {stats_output}")

        stats = {}
        for key, value in raw_output.items():
            if key == "SUM":
                stats["_summary"] = {
                    "files": value.get("nFiles", 0),
                    "blank": value.get("blank", 0),
                    "comment": value.get("comment", 0),
                    "code": value.get("code", 0),
                }
            else:
                stats[key] = {
                    "files": value.get("nFiles", 0),
                    "blank": value.get("blank", 0),
                    "comment": value.get("comment", 0),
                    "code": value.get("code", 0),
                }

        total_code = stats.get("_summary", {}).get("code", 0)
        total_files = stats.get("_summary", {}).get("files", 0)
        logger.success(f"Analyzed {total_files} files, {total_code} lines of code")

        return stats
