from .static.lang_mapping import TOKOUNT_TO_LINGUIST


def _normalize_language(lang: str) -> str:
    if lang in TOKOUNT_TO_LINGUIST:
        mapped = TOKOUNT_TO_LINGUIST[lang]
        return mapped if mapped is not None else lang
    return lang


def normalize_language_stats(stats: dict[str, int]) -> dict[str, int]:
    """Normalize language names and merge duplicates"""
    normalized: dict[str, int] = {}
    for lang, count in stats.items():
        norm_lang = _normalize_language(lang)
        normalized[norm_lang] = normalized.get(norm_lang, 0) + count
    return normalized
