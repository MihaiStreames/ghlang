"""
This entire file exists to force platform-tagged wheels so cibuildwheel doesn't reject the build,
making this the most hacky workaround I could come up with given hatchling's plugin system.

Will update if hatchling adds a better way to do this in the future.

LAST UPDATE: 2026-01-14
"""

from __future__ import annotations

from typing import Any

from hatchling.builders.hooks.plugin.interface import (  # type: ignore[import-not-found]
    BuildHookInterface,
)


class PlatformWheelHook(BuildHookInterface):
    PLUGIN_NAME = "platform-wheel"

    def initialize(self, _version: str, build_data: dict[str, Any]) -> None:
        # force a platform tag so cibuildwheel accepts the wheel
        build_data["pure_python"] = False
        build_data["infer_tag"] = True


def get_build_hook() -> type[BuildHookInterface]:
    return PlatformWheelHook
