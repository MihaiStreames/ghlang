#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from ghlang.platforms import platform_tag  # noqa: E402
from ghlang.platforms import tokount_binary_name  # noqa: E402


def main() -> None:
    try:
        tag = platform_tag()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    binary_name = tokount_binary_name()
    source = Path("tokount") / "target" / "release" / binary_name
    if not source.exists():
        raise SystemExit(f"tokount binary not found at {source}")

    destination = Path("ghlang") / "_bin" / tag / binary_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"Copied {source} -> {destination}")


if __name__ == "__main__":
    main()
