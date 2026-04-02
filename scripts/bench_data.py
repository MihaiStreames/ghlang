import json
from pathlib import Path
from sys import argv


STATS = {
    "Python": 45000,
    "Rust": 30000,
    "JavaScript": 20000,
    "TypeScript": 15000,
    "Go": 10000,
    "C": 8000,
    "Shell": 5000,
    "TOML": 3000,
    "Markdown": 2000,
    "YAML": 1000,
}

COLORS = {
    "Python": "#3572A5",
    "Rust": "#dea584",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Go": "#00ADD8",
    "C": "#555555",
    "Shell": "#89e051",
    "TOML": "#9c4221",
    "Markdown": "#083fa1",
    "YAML": "#cb171e",
}


def main() -> None:
    out_dir = Path(argv[1]) if len(argv) > 1 else Path("/tmp")
    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "stats.json").open("w") as f:
        json.dump(STATS, f)
    with (out_dir / "colors.json").open("w") as f:
        json.dump(COLORS, f)

    print(out_dir)


if __name__ == "__main__":
    main()
