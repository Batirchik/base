"""Russian retelling.

Russian lines from the public descriptions stay Russian. English lines are
translated to Russian. The result is not a verbatim copy of a description.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "data" / "en-ru-cache.json"

# A few English idioms Argos maps to the wrong Russian sense.
BEFORE = (
    (re.compile(r"\byou have been lied to about\b", re.I), "you were misinformed about"),
    (re.compile(r"\byou've been lied to about\b", re.I), "you were misinformed about"),
    (re.compile(r"\byou’ve been lied to about\b", re.I), "you were misinformed about"),
)

EXACT = {
    "Throw a clove in your coffee and this is what happens": "Бросьте гвоздику в кофе и посмотрите, что произойдёт",
    "GERD and Gastritis: A Remedy That Restores the Mucous Membrane": "ГЭРБ и гастрит: средство, которое восстанавливает слизистую оболочку",
}

AFTER = (
    ("Шкала ванной врет", "Весы врут"),
    ("Шкала лежит", "Весы врут"),
    ("Шкала лжет", "Весы врут"),
    ("Весы весов не говорят правду", "Весы врут"),
    ("слизистой мембраны", "слизистой оболочки"),
    ("слизистую мембрану", "слизистую оболочку"),
)

KEEP_CAPS = {"СИБР", "СПКЯ", "ГЭРБ", "ЖКТ", "ТТГ", "СРК", "ДГЭА", "АЛТ", "АСТ"}


def cyr_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for ch in letters if ord(ch) > 127) / len(letters)


def strip_decor(text: str) -> str:
    kept = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("S") or cat.startswith("C"):
            continue
        kept.append(ch)
    cleaned = "".join(kept)
    cleaned = cleaned.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", cleaned).strip(" -–—")


def tidy(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text.strip(" ,;:-")


def _load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def save_cache() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(_CACHE, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


_CACHE = _load_cache()
_TRANSLATOR = None
_TRIED = False


def _translator():
    global _TRANSLATOR, _TRIED
    if _TRIED:
        return _TRANSLATOR
    _TRIED = True
    try:
        import argostranslate.translate
    except ImportError:
        return None
    langs = argostranslate.translate.get_installed_languages()
    source = next((lang for lang in langs if lang.code == "en"), None)
    target = next((lang for lang in langs if lang.code == "ru"), None)
    if source and target:
        _TRANSLATOR = source.get_translation(target)
    return _TRANSLATOR


def _prepare_en(text: str) -> str:
    for pattern, repl in BEFORE:
        text = pattern.sub(repl, text)
    return text


def _polish_ru(text: str) -> str:
    for src, dst in AFTER:
        text = text.replace(src, dst)
    text = re.sub(
        r":\s+([А-ЯЁ])([а-яё]{2,})",
        lambda match: ": " + match.group(1).lower() + match.group(2),
        text,
    )
    return tidy(text)


def soften_caps(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        word = match.group(0)
        if word in KEEP_CAPS:
            return word
        return word.lower()

    return re.sub(r"\b[А-ЯЁ]{2,}\b", repl, text)


def translate_en(text: str) -> str:
    exact = EXACT.get(text)
    if exact:
        return exact
    prepared = _prepare_en(text)
    cached = _CACHE.get(prepared)
    if cached:
        return _polish_ru(cached)
    if _translator() is None:
        return text
    import argostranslate.translate

    rendered = _polish_ru(argostranslate.translate.translate(prepared, "en", "ru"))
    if rendered:
        _CACHE[prepared] = rendered
    return rendered or text


def to_ru(text: str) -> str:
    cleaned = strip_decor(text)
    if not cleaned:
        return ""
    if cyr_ratio(cleaned) >= 0.35:
        return tidy(cleaned)
    return tidy(translate_en(cleaned)) or cleaned


TITLE_FIXES = (
    ("LIVER DETOX", "Детокс печени"),
    ("anti-age", "антивозрастное"),
    ("Apple Cider Vinegar 2 Weeks Later", "яблочный уксус через 2 недели"),
)


def title_ru(text: str) -> str:
    translated = soften_caps(to_ru(text))
    for src, dst in TITLE_FIXES:
        translated = translated.replace(src, dst)
    if not translated:
        return strip_decor(text)
    return translated[:1].upper() + translated[1:]


def title_en(text: str) -> str:
    cleaned = strip_decor(text)
    if cyr_ratio(cleaned) < 0.35:
        return cleaned
    return ""
