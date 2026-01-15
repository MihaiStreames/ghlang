#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from ghlang.platforms import platform_tag  # noqa: E402
from ghlang.platforms import tokount_binary_name  # noqa: E402


def _platform_tag_from_cibw_build(build: str) -> str | None:
    if "manylinux_x86_64" in build or "linux_x86_64" in build or "musllinux_x86_64" in build:
        return "linux-x86_64"
    if "manylinux_aarch64" in build or "linux_aarch64" in build or "musllinux_aarch64" in build:
        return "linux-aarch64"
    if "win_amd64" in build:
        return "windows-x86_64"
    return None


def main() -> None:
    tag = os.environ.get("GHLANG_PLATFORM_TAG")
    if not tag:
        build = os.environ.get("CIBW_BUILD", "")
        tag = _platform_tag_from_cibw_build(build) if build else None
    if not tag:
        try:
            tag = platform_tag()
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

    binary_name = tokount_binary_name()
    cargo_target = os.environ.get("CARGO_BUILD_TARGET")
    if cargo_target:
        source = Path("tokount") / "target" / cargo_target / "release" / binary_name
    else:
        source = Path("tokount") / "target" / "release" / binary_name
    if not source.exists():
        raise SystemExit(f"tokount binary not found at {source}")

    destination = Path("ghlang") / "_bin" / tag / binary_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"Copied {source} -> {destination}")


if __name__ == "__main__":
    main()
