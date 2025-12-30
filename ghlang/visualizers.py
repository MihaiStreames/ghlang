from importlib import resources
import json
from pathlib import Path

from loguru import logger
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import requests
import yaml


LINGUIST_LANGUAGES_URL = (
    "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"
)


def _load_cloc_mapping() -> dict[str, str | None]:
    content = resources.files("ghlang.static").joinpath("lang_mapping.json").read_text()
    return dict(json.loads(content))


CLOC_TO_LINGUIST: dict[str, str | None] = _load_cloc_mapping()


def normalize_language(lang: str) -> str | None:
    """Normalize cloc language name to GitHub linguist name"""
    if lang in CLOC_TO_LINGUIST:
        return CLOC_TO_LINGUIST[lang]
    return lang


def normalize_language_stats(stats: dict[str, int]) -> dict[str, int]:
    """Normalize language names and merge duplicates"""
    normalized: dict[str, int] = {}

    for lang, count in stats.items():
        norm_lang = normalize_language(lang)

        if norm_lang is None:
            continue

        normalized[norm_lang] = normalized.get(norm_lang, 0) + count

    return normalized


def load_github_colors(output_file: Path | None = None) -> dict[str, str]:
    """Fetch GitHub's language colors from linguist YAML"""
    logger.info("Grabbing language colors from GitHub")

    try:
        r = requests.get(LINGUIST_LANGUAGES_URL, timeout=10)
        r.raise_for_status()
        data = yaml.safe_load(r.text)
        colors = {}

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


def generate_pie(
    language_stats: dict[str, int],
    colors: dict[str, str],
    output: Path,
    title: str | None = None,
    min_percentage: float = 1.5,
) -> None:
    """Generate a pie chart showing language distribution"""
    title = title if title else "Language Distribution"
    logger.debug(f"Generating pie chart with {len(language_stats)} languages...")

    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total = sum(language_stats.values()) or 1

    labels = [lang for lang, _ in items]
    sizes = [count for _, count in items]
    chart_colors = [colors.get(lang, "#cccccc") for lang in labels]

    fig, ax = plt.subplots(figsize=(14, 10))

    wedges, texts, autotexts = ax.pie(  # type: ignore[misc]
        sizes,
        colors=chart_colors,
        autopct=lambda p: f"{p:.1f}%" if p >= min_percentage else "",
        startangle=90,
        pctdistance=0.85,
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(9)
        autotext.set_weight("bold")  # type: ignore[union-attr]

    legend_labels = [f"{lang} ({count / total * 100:.1f}%)" for lang, count in items]
    ax.legend(
        wedges,
        legend_labels,
        title="Languages",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9,
        title_fontsize=11,
    )

    ax.set_title(
        title,
        fontsize=16,
        weight="bold",
        pad=20,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=200, bbox_inches="tight")
    plt.close()

    logger.success(f"Saved pie chart to {output}")


def generate_bar(
    language_stats: dict[str, int],
    colors: dict[str, str],
    output: Path,
    top_n: int = 5,
    title: str | None = None,
    min_label_width: float = 0.05,
) -> None:
    """Generate a horizontal segmented bar chart showing top N languages"""
    title = title if title else f"Top {top_n} Languages"
    logger.debug(f"Generating segmented bar chart (top {top_n} languages)...")

    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total = sum(language_stats.values()) or 1

    top = items[:top_n]
    other_count = total - sum(count for _, count in top)

    segments = top + ([("Other", other_count)] if other_count > 0 else [])

    fig, ax = plt.subplots(figsize=(12, 4))

    left = 0.0
    bar_height = 0.6

    for lang, count in segments:
        width = count / total
        color = colors.get(lang, "#cccccc")

        ax.barh(
            0,
            width,
            bar_height,
            left=left,
            color=color,
            edgecolor="white",
            linewidth=2,
        )

        if width >= min_label_width:
            ax.text(
                left + width / 2,
                0,
                f"{width * 100:.1f}%",
                ha="center",
                va="center",
                color="white",
                fontsize=11,
                weight="bold",
            )

        left += width

    legend_elements = [
        mpatches.Patch(
            color=colors.get(lang, "#cccccc"),
            label=f"{lang} ({count / total * 100:.1f}%)",
        )
        for lang, count in segments
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=min(len(segments), 3),
        frameon=False,
        fontsize=10,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 0.5)
    ax.axis("off")

    ax.set_title(
        title,
        fontsize=14,
        weight="bold",
        pad=15,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=200, bbox_inches="tight")
    plt.close()

    logger.success(f"Saved segmented bar chart to {output}")
