import json
from pathlib import Path

import requests
import yaml

from .constants import LINGUIST_URL
from .constants import REQUEST_TIMEOUT
from .logging import logger


def load_github_colors(output_file: Path | None = None) -> dict[str, str]:
    """Fetch GitHub's language colors from linguist YAML"""
    logger.info("Grabbing language colors from GitHub")

    try:
        r = requests.get(LINGUIST_URL, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        data = yaml.safe_load(r.text)
        colors: dict[str, str] = {}

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
        logger.warning(f"Couldn't load GitHub colors: {e}")
        return {}
