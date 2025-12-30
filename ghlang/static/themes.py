"""Chart color themes"""

THEMES: dict[str, dict[str, str]] = {
    "light": {
        "background": "#ffffff",
        "text": "#1a1a1a",
        "secondary": "#666666",
        "legend_bg": "#f5f5f5",
        "fallback": "#cccccc",
    },
    "dark": {
        "background": "#1a1a1a",
        "text": "#f0f0f0",
        "secondary": "#a0a0a0",
        "legend_bg": "#2a2a2a",
        "fallback": "#555555",
    },
    "monokai": {
        "background": "#272822",
        "text": "#f8f8f2",
        "secondary": "#75715e",
        "legend_bg": "#3e3d32",
        "fallback": "#49483e",
    },
}
