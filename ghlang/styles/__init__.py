"""Chart rendering styles"""

from collections.abc import Callable


STYLES: tuple[str, ...] = ("pixel", "pie", "bar")


def get_style_registry() -> dict[str, Callable[..., None]]:
    """Return the built-in style name to generator function mapping.

    Imports are deferred so matplotlib is not loaded until a chart is
    actually requested.

    Returns
    -------
    dict[str, Callable[..., None]]
        Style name to chart generator callable.
    """
    from .bar import generate_bar  # noqa: PLC0415
    from .pie import generate_pie  # noqa: PLC0415
    from .pixel import generate_pixel  # noqa: PLC0415

    return {
        "pixel": generate_pixel,
        "pie": generate_pie,
        "bar": generate_bar,
    }
