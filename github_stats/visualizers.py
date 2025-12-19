from pathlib import Path

from loguru import logger
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


def generate_pie(
    language_stats: dict[str, int],
    colors: dict[str, str],
    output: Path,
    min_percentage: float = 1.5,
) -> None:
    """Generate a pie chart showing language distribution

    Args:
        language_stats: Dictionary mapping language names to byte counts
        colors: Dictionary mapping language names to hex colors
        output: Path where the image should be saved
        min_percentage: Minimum percentage to show label (default: 1.5%)
    """
    logger.info(f"Generating pie chart with {len(language_stats)} languages...")

    # Sort by size
    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(language_stats.values()) or 1

    labels = [lang for lang, _ in items]
    sizes = [count for _, count in items]
    chart_colors = [colors.get(lang, "#cccccc") for lang in labels]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Create pie chart without labels on the chart itself
    wedges, texts, autotexts = ax.pie(
        sizes,
        colors=chart_colors,
        autopct=lambda p: f"{p:.1f}%" if p >= min_percentage else "",
        startangle=90,
        pctdistance=0.85,
    )

    # Style percentage text
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(9)
        autotext.set_weight("bold")

    # Create legend with all languages
    legend_labels = [f"{lang} ({count / total_bytes * 100:.1f}%)" for lang, count in items]
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
        "Language Distribution (GitHub Linguist)",
        fontsize=16,
        weight="bold",
        pad=20,
    )

    # Save
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
    min_label_width: float = 0.05,
) -> None:
    """Generate a horizontal segmented bar chart showing top N languages

    Args:
        language_stats: Dictionary mapping language names to byte counts
        colors: Dictionary mapping language names to hex colors
        output: Path where the image should be saved
        top_n: Number of top languages to show individually (default: 5)
        min_label_width: Minimum segment width to show percentage label (default: 0.05)
    """
    logger.info(f"Generating segmented bar chart (top {top_n} languages)...")

    # Sort by size and get top N
    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(language_stats.values()) or 1

    top = items[:top_n]
    other_bytes = total_bytes - sum(count for _, count in top)

    # Add "Other" if there are remaining languages
    segments = top + ([("Other", other_bytes)] if other_bytes > 0 else [])

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 4))

    # Draw horizontal bar
    left = 0
    bar_height = 0.6

    for lang, byte_count in segments:
        width = byte_count / total_bytes
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

        # Add percentage label if segment is large enough
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

    # Create legend
    legend_elements = [
        mpatches.Patch(
            color=colors.get(lang, "#cccccc"),
            label=f"{lang} ({byte_count / total_bytes * 100:.1f}%)",
        )
        for lang, byte_count in segments
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
        f"Top {top_n} Languages",
        fontsize=14,
        weight="bold",
        pad=15,
    )

    # Save
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=200, bbox_inches="tight")
    plt.close()

    logger.success(f"Saved segmented bar chart to {output}")
