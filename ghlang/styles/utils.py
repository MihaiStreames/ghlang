import io
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw

from .constants import HIDE_THRESHOLD
from .constants import PNG_DPI
from .constants import ROUNDED_CORNER_RADIUS


def build_display_segments(
    language_stats: dict[str, int],
    top_n: int,
) -> list[tuple[str, float]]:
    """Build (name, pct) segments applying top_n + HIDE_THRESHOLD, remainder into 'Other'"""
    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total = sum(language_stats.values()) or 1

    shown: list[tuple[str, float]] = []
    others_pct = 0.0

    for i, (name, count) in enumerate(items):
        pct = count / total * 100
        if i < top_n and pct >= HIDE_THRESHOLD:
            shown.append((name, pct))
        else:
            others_pct += pct

    if others_pct > 0:
        shown.append(("Other", round(others_pct, 1)))

    return shown


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB hex string to (R, G, B) tuple"""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def add_rounded_corners(img: Image.Image, radius: int = ROUNDED_CORNER_RADIUS) -> Image.Image:
    """Add rounded corners to an image"""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    img.putalpha(mask)
    return img


def save_matplotlib_chart(output: Path, background_color: str) -> None:
    """Save matplotlib figure to PNG with rounded corners"""
    # TODO: re-enable SVG support once PNG pipeline is stable
    output.parent.mkdir(parents=True, exist_ok=True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=PNG_DPI, bbox_inches="tight", facecolor=background_color)
    plt.close()
    buf.seek(0)

    img = Image.open(buf)

    rounded = add_rounded_corners(img)
    rounded.save(output)
