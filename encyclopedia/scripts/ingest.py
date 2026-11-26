#!/usr/bin/env python3
"""Fetch public metadata for @DrEricBerg. No video files.

Resumable: ids already present in data/raw/videos.jsonl are skipped.
Index comes from data/raw/index.tsv (id<TAB>title). Refresh it with
yt-dlp --flat-playlist when the channel gains videos:

  yt-dlp --flat-playlist --print '%(id)s\\t%(title)s' \\
    'https://www.youtube.com/playlist?list=UUNnSNNsd9zCVERp1phyRcaw' \\
    > data/raw/index.tsv
"""

from __future__ import annotations

import argparse
import json
import random
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INDEX = RAW / "index.tsv"
OUT = RAW / "videos.jsonl"
CHANNEL = "https://www.youtube.com/@DrEricBerg"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

RU_MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}
EN_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

write_lock = threading.Lock()


def load_index() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        vid, title = line.split("\t", 1)
        vid = vid.strip()
        if vid:
            rows.append((vid, title.strip()))
    return rows


def load_done() -> set[str]:
    done: set[str] = set()
    if not OUT.exists():
        return done
    for line in OUT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("description"):
            done.add(row["id"])
    return done


def compact() -> None:
    if not OUT.exists():
        return
    best: dict[str, dict] = {}
    for line in OUT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        prev = best.get(row["id"])
        if prev is None or (row.get("description") and not prev.get("description")):
            best[row["id"]] = row
    with OUT.open("w", encoding="utf-8") as fh:
        for row in best.values():
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_date(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text.replace("\u202f", " ").replace("\xa0", " "))
    cleaned = cleaned.replace("Premiered", "").replace("г.", "").strip()
    m = re.search(
        r"(\d{1,2})\s+(янв|фев|мар|апр|ма[йя]|июн|июл|авг|сен|окт|ноя|дек)[а-яё]*\.?\s+(\d{4})",
        cleaned,
        re.I,
    )
    if m:
        month = RU_MONTHS[m.group(2).lower()[:3]]
        return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(1)):02d}"
    m = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),\s+(\d{4})",
        cleaned,
        re.I,
    )
    if m:
        month = EN_MONTHS[m.group(1).lower()[:3]]
        return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(2)):02d}"
    return None


def json_string_at(html: str, marker: str) -> str | None:
    i = html.find(marker)
    if i < 0:
        return None
    start = i + len(marker)
    if start >= len(html) or html[start] != '"':
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(html, start)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, str) else None


def longest_description(html: str) -> str | None:
    marker = '"attributedDescription":{"content":'
    best = ""
    start = 0
    while True:
        i = html.find(marker, start)
        if i < 0:
            break
        value = json_string_at(html, marker if start == 0 and i == html.find(marker) else "")
        # json_string_at searches from the beginning; decode at this offset instead.
        pos = i + len(marker)
        value = None
        if pos < len(html) and html[pos] == '"':
            try:
                value, _ = json.JSONDecoder().raw_decode(html, pos)
            except json.JSONDecodeError:
                value = None
        if isinstance(value, str) and len(value) > len(best):
            best = value
        start = i + len(marker)
    return best or None


def fetch_html(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}&hl=ru&gl=US"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
            "Cookie": "PREF=hl=ru&gl=US",
        },
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_one(video_id: str, title: str) -> dict:
    last_error = "empty"
    for attempt in range(4):
        try:
            html = fetch_html(video_id)
            description = longest_description(html)
            published = parse_date(json_string_at(html, '"publishDate":{"simpleText":'))
            if published is None:
                published = parse_date(json_string_at(html, '"dateText":{"simpleText":'))
            if not description:
                last_error = "no-description"
                time.sleep(0.8 * (attempt + 1) + random.random())
                continue
            return {
                "id": video_id,
                "title": title,
                "publishedAt": published,
                "description": description,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "channel": CHANNEL,
            }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
            time.sleep(1.2 * (attempt + 1) + random.random())
    return {
        "id": video_id,
        "title": title,
        "publishedAt": None,
        "description": "",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "channel": CHANNEL,
        "error": last_error,
    }


def append_row(row: dict) -> None:
    line = json.dumps(row, ensure_ascii=False) + "\n"
    with write_lock:
        with OUT.open("a", encoding="utf-8") as fh:
            fh.write(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Max new videos this run (0 = all)")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--ids", nargs="*", default=[])
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    index = load_index()
    by_id = {vid: title for vid, title in index}
    if args.ids:
        todo = [(vid, by_id.get(vid, "")) for vid in args.ids]
    else:
        done = load_done()
        todo = [(vid, title) for vid, title in index if vid not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"index={len(index)} to_fetch={len(todo)} workers={args.workers}", flush=True)
    if not todo:
        return

    ok = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch_one, vid, title) for vid, title in todo]
        for n, fut in enumerate(as_completed(futures), 1):
            row = fut.result()
            append_row(row)
            if row.get("description"):
                ok += 1
            else:
                failed += 1
            if n % 25 == 0 or n == len(todo):
                print(f"progress {n}/{len(todo)} ok={ok} failed={failed}", flush=True)
    compact()
    print(f"done ok={ok} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
