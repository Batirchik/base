#!/usr/bin/env python3
"""Build Ukrainian cards from raw public descriptions. Resumable upstream of this step."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract
from translate import cyr_ratio, title_uk, to_en_title, to_uk

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "videos.jsonl"
CARDS = ROOT / "src" / "data" / "cards.json"
CONDITIONS = ROOT / "src" / "data" / "conditions.json"
PROOF = ROOT / "data" / "sample" / "filter-proof.json"
REPORT = ROOT / "data" / "filter-report.json"

RU_ONLY = re.compile(r"[ыэъёЫЭЪЁ]")
TOKEN = re.compile(r"[А-Яа-яЁё]{3,}")


def richness(row: dict) -> int:
    score = len(row["steps"]) * 3 + len(row["foods"]) * 2 + len(row["supplements"]) * 2
    if row.get("publishedAt"):
        score += 1
    if "русская озвучка" in row["title"].lower():
        score -= 4
    return score


def retell_list(items: list[str], limit: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = to_uk(item)
        text = text.strip(" -–—•")
        if len(text) < 2:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= limit:
            break
    return out


def summary(kind: str, title: str, foods: list[str], supplements: list[str]) -> str:
    lead = {
        "recipe": "Рецепт із кількостями і коротким способом приготування.",
        "protocol": "Режим із дозами або розкладом.",
        "recommendation": "Конкретні орієнтири щодо їжі, добавок або режиму.",
    }[kind]
    bits = foods[:5] or supplements[:4]
    if bits:
        label = "Склад" if kind == "recipe" else "У фокусі"
        return f"{title}. {lead} {label}: {', '.join(bits)}."
    return f"{title}. {lead}"


def load_rows() -> list[dict]:
    rows = []
    for line in RAW.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> None:
    rows = load_rows()
    decisions = [extract.analyze(row) for row in rows]
    kept = [row for row in decisions if row["keep"]]
    dropped = [row for row in decisions if not row["keep"]]

    best: dict[str, dict] = {}
    for row in kept:
        key = extract.norm_title(row["title"])
        prev = best.get(key)
        if prev is None or richness(row) > richness(prev):
            best[key] = row

    cards = []
    for row in best.values():
        foods = retell_list(row["foods"], 16)
        supplements = retell_list(row["supplements"], 8)
        steps = retell_list(row["steps"], 12)
        uk_title = title_uk(row["title"])
        card = {
            "id": row["id"],
            "titleUk": uk_title,
            "summaryUk": summary(row["kind"], uk_title, foods, supplements),
            "kind": row["kind"],
            "foods": foods,
            "supplements": supplements,
            "steps": steps,
            "conditions": row["conditions"],
            "bodyParts": row["bodyParts"],
            "titleEn": to_en_title(row["title"]),
            "publishedAt": row.get("publishedAt") or "",
            "url": row["url"],
        }
        cards.append(card)

    cards.sort(key=lambda card: (card["publishedAt"], card["titleUk"]), reverse=True)
    used = {cid for card in cards for cid in card["conditions"]}
    conditions = [
        {"id": cid, "nameUk": extract.CONDITION_NAME[cid]}
        for cid in extract.CONDITION_NAME
        if cid in used
    ]
    conditions.sort(key=lambda item: item["nameUk"])

    CARDS.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CONDITIONS.write_text(
        json.dumps(conditions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    def proof_item(row: dict) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "keep": row["keep"],
            "reason": row["reason"],
            "kind": row.get("kind"),
            "excerpt": (row.get("cleaned") or "")[:420],
        }

    keeps_by_kind = {}
    for row in best.values():
        keeps_by_kind.setdefault(row["kind"], row)
    drops_by_reason = {}
    for row in dropped:
        drops_by_reason.setdefault(row["reason"], row)
    proof = {
        "channel": "https://www.youtube.com/@DrEricBerg",
        "note": "Short excerpts of public descriptions used to check the filter. Not published as pages.",
        "kept": [proof_item(keeps_by_kind[k]) for k in ("recipe", "protocol", "recommendation") if k in keeps_by_kind],
        "dropped": [proof_item(row) for row in list(drops_by_reason.values())[:4]],
    }
    PROOF.parent.mkdir(parents=True, exist_ok=True)
    PROOF.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reasons = Counter(row["reason"] for row in dropped)
    kinds = Counter(card["kind"] for card in cards)
    bad = []
    unknown: Counter[str] = Counter()
    for card in cards:
        blob = " ".join(
            [card["titleUk"], card["summaryUk"], *card["foods"], *card["supplements"], *card["steps"]]
        )
        if RU_ONLY.search(blob):
            bad.append(card["id"])
        if cyr_ratio(card["titleEn"]) > 0.4:
            for token in TOKEN.findall(card["titleEn"].lower()):
                unknown[token] += 1
        for token in TOKEN.findall(blob.lower()):
            if token in {"вітамін", "магній"}:
                continue
            if RU_ONLY.search(token):
                unknown[token] += 1
    report = {
        "channel": "https://www.youtube.com/@DrEricBerg",
        "indexed": len(rows),
        "kept": len(cards),
        "byKind": dict(kinds),
        "dropped": dict(reasons),
        "conditions": len(conditions),
        "cardsWithRussianLetters": len(bad),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("bad letter cards", bad[:12])
    print("unknown sample", unknown.most_common(40))


if __name__ == "__main__":
    main()
