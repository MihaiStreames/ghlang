import json
from pathlib import Path
from sys import argv


def main() -> None:
    style = argv[1]
    data_dir = Path(argv[2])

    stats = json.loads((data_dir / "stats.json").read_text())
    colors = json.loads((data_dir / "colors.json").read_text())

    from ghlang.styles import get_style_registry

    registry = get_style_registry()
    registry[style](stats, colors, data_dir / f"{style}.png", "Benchmark", "light")


if __name__ == "__main__":
    main()
