from .static import lang_mapping


def _normalize_language(lang: str) -> str:
    if lang in lang_mapping.TOKOUNT_TO_LINGUIST:
        mapped = lang_mapping.TOKOUNT_TO_LINGUIST[lang]
        return mapped if mapped is not None else lang
    return lang


def normalize_language_stats(stats: dict[str, int]) -> dict[str, int]:
    """Normalize language names and merge duplicates.

    Map tokount language names to their GitHub Linguist equivalents and
    sum counts for names that collapse into the same canonical form.

    Parameters
    ----------
    stats : dict[str, int]
        Raw language name to count mapping.

    Returns
    -------
    dict[str, int]
        Normalized language name to merged count.
    """
    normalized: dict[str, int] = {}
    for lang, count in stats.items():
        norm_lang = _normalize_language(lang)
        normalized[norm_lang] = normalized.get(norm_lang, 0) + count
    return normalized
