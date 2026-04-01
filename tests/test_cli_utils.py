from ghlang.cli.utils import format_autocomplete
from ghlang.cli.utils import themes_autocomplete
from ghlang.static.themes import THEMES


class TestFormatAutocomplete:
    def test_empty_returns_all(self) -> None:
        assert format_autocomplete("") == ["png", "svg"]

    def test_filters_by_prefix(self) -> None:
        assert format_autocomplete("p") == ["png"]
        assert format_autocomplete("s") == ["svg"]

    def test_no_match_returns_empty(self) -> None:
        assert format_autocomplete("x") == []


class TestThemesAutocomplete:
    def test_returns_builtin_themes(self) -> None:
        result = themes_autocomplete("")
        for theme in THEMES:
            assert theme in result

    def test_filters_by_prefix(self) -> None:
        result = themes_autocomplete("l")
        assert "light" in result
        assert all(t.startswith("l") for t in result)

    def test_no_match_returns_empty(self) -> None:
        assert themes_autocomplete("zzz") == []
