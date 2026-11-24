"""Structured Ukrainian retelling of extracted Russian or English lines."""

from __future__ import annotations

import re
import unicodedata

from lexicon import EN_WORDS, PHRASES, TO_EN, WORDS
from lexicon_extra import EN_EXTRA, EN_PHRASES, RU_EXTRA, TO_EN_EXTRA

WORDS.update(RU_EXTRA)
EN_WORDS.update(EN_EXTRA)
TO_EN.update(TO_EN_EXTRA)
PHRASE_TABLE = sorted(PHRASES + EN_PHRASES, key=lambda pair: len(pair[0]), reverse=True)

TOKEN = re.compile(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9']+(?:-[A-Za-zА-Яа-яЁё0-9]+)?")


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
    cleaned = cleaned.replace("ё", "е").replace("Ё", "Е")
    return re.sub(r"\s+", " ", cleaned).strip(" -–—")


def _sub_phrases(text: str, table: list[tuple[str, str]]) -> str:
    for src, dst in table:
        pattern = re.compile(re.escape(src), re.I)

        def repl(match: re.Match[str], dst: str = dst) -> str:
            found = match.group(0)
            if found[:1].isupper() and dst[:1].isalpha():
                return dst[:1].upper() + dst[1:]
            return dst

        text = pattern.sub(repl, text)
    return text


def _sub_words(text: str, table: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        word = match.group(0)
        key = word.lower().replace("ё", "е")
        if key not in table:
            return word
        dst = table[key]
        if not dst:
            return ""
        if word[:1].isupper() and dst[:1].isalpha():
            return dst[:1].upper() + dst[1:]
        return dst

    return TOKEN.sub(repl, text)


def tidy(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text.strip(" ,;:-")


def to_uk(text: str) -> str:
    cleaned = strip_decor(text)
    if not cleaned:
        return ""
    if cyr_ratio(cleaned) < 0.35:
        phrases = sorted(EN_PHRASES, key=lambda pair: len(pair[0]), reverse=True)
        return tidy(_sub_words(_sub_phrases(cleaned, phrases), EN_WORDS)) or cleaned
    return tidy(_sub_words(_sub_phrases(cleaned, PHRASE_TABLE), WORDS))


def to_en_title(text: str) -> str:
    cleaned = strip_decor(text)
    if cyr_ratio(cleaned) < 0.35:
        return cleaned
    return tidy(_sub_words(cleaned, TO_EN)) or cleaned


def title_uk(text: str) -> str:
    translated = to_uk(text)
    if not translated:
        return strip_decor(text)
    return translated[:1].upper() + translated[1:]
