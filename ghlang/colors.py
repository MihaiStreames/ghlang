import json
from pathlib import Path

import requests
import yaml

from . import constants
from . import log


def load_github_colors(output_file: Path | None = None) -> dict[str, str]:
    """Fetch GitHub's language colors from the linguist YAML.

    Parameters
    ----------
    output_file : Path | None
        If given, write the color map to this path as JSON.

    Returns
    -------
    dict[str, str]
        Mapping of language name to hex color string (e.g. ``"#3572A5"``).
        Empty dict on network failure.
    """
    log.logger.info("Grabbing language colors from GitHub")

    try:
        r = requests.get(constants.LINGUIST_URL, timeout=constants.REQUEST_TIMEOUT)
        r.raise_for_status()

        data = yaml.safe_load(r.text)
        colors: dict[str, str] = {}

        for lang, props in data.items():
            if isinstance(props, dict) and "color" in props:
                colors[lang] = props["color"]
        log.logger.success(f"Loaded {len(colors)} language colors")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w") as f:
                json.dump(colors, f, indent=2)
            log.logger.debug(f"Saved color data to {output_file}")

        return colors

    except Exception as e:
        log.logger.warning(f"Couldn't load GitHub colors: {e}")
        return {}
