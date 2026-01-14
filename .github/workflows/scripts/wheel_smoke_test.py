#!/usr/bin/env python3
from importlib import resources
from pathlib import Path
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
    resource = resources.files("ghlang").joinpath("_bin", tag, binary_name)

    with resources.as_file(resource) as binary_path:
        if not binary_path.exists():
            raise SystemExit(f"Missing tokount binary at {binary_path}")

    print("smoke test ok")


if __name__ == "__main__":
    main()
