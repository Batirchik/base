#!/usr/bin/env python3
"""Add PDF bookmarks that jump to the same headings as the table of contents."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import Fit

ROOT = Path(__file__).resolve().parents[1]


def _record(found: dict[str, tuple[int, Fit]], page_index: dict[int, int], anchor: str, array) -> None:
    array = array.get_object()
    index = page_index.get(array[0].idnum)
    if index is None:
        return
    left = float(array[2]) if len(array) > 2 else 0
    top = float(array[3]) if len(array) > 3 else 0
    found[anchor.lstrip("/")] = (index, Fit.xyz(left=left, top=top, zoom=0))


def destination_map(reader: PdfReader) -> dict[str, tuple[int, Fit]]:
    """Map HTML anchor ids to a page index and the heading position."""
    root = reader.trailer["/Root"]
    page_index = {
        page.indirect_reference.idnum: i for i, page in enumerate(reader.pages)
    }
    found: dict[str, tuple[int, Fit]] = {}

    def walk(node) -> None:
        node = node.get_object()
        if "/Names" in node:
            pairs = node["/Names"]
            for i in range(0, len(pairs), 2):
                _record(found, page_index, str(pairs[i]), pairs[i + 1])
        elif "/Kids" not in node:
            for key, value in node.items():
                _record(found, page_index, str(key), value)
        for kid in node.get("/Kids", []):
            walk(kid)

    if "/Dests" in root:
        walk(root["/Dests"])
    names = root.get("/Names")
    if names is not None and "/Dests" in names.get_object():
        walk(names.get_object()["/Dests"])
    return found


def main() -> None:
    pdf_path = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public" / "berg-dovidnyk.pdf")
    cards = json.loads((ROOT / "src/data/cards.json").read_text(encoding="utf-8"))
    parts = json.loads((ROOT / "src/data/bodyParts.json").read_text(encoding="utf-8"))
    conditions = json.loads((ROOT / "src/data/conditions.json").read_text(encoding="utf-8"))
    condition_name = {item["id"]: item["nameRu"] for item in conditions}

    reader = PdfReader(str(pdf_path))
    targets = destination_map(reader)
    writer = PdfWriter()
    writer.append(reader)
    added = 0
    missing = []
    for part in parts:
        in_part = [card for card in cards if part["id"] in card["bodyParts"]]
        if not in_part:
            continue
        part_id = f"part-{part['id']}"
        target = targets.get(part_id)
        if target is None:
            missing.append(part_id)
            continue
        parent = writer.add_outline_item(
            title=part["nameRu"], page_number=target[0], fit=target[1]
        )
        added += 1
        groups: dict[str, list] = {}
        loose = False
        for card in in_part:
            if not card["conditions"]:
                loose = True
            for condition_id in card["conditions"]:
                groups.setdefault(condition_id, []).append(card)
        ordered = sorted(groups, key=lambda cid: condition_name.get(cid, cid))
        for condition_id in ordered:
            anchor = f"{part_id}--{condition_id}"
            child = targets.get(anchor)
            if child is None:
                missing.append(anchor)
                continue
            writer.add_outline_item(
                title=condition_name.get(condition_id, condition_id),
                page_number=child[0],
                parent=parent,
                fit=child[1],
            )
            added += 1
        if loose:
            anchor = f"{part_id}--loose"
            child = targets.get(anchor)
            if child is None:
                missing.append(anchor)
            else:
                writer.add_outline_item(
                    title="Без отдельного состояния",
                    page_number=child[0],
                    parent=parent,
                    fit=child[1],
                )
                added += 1

    tmp = pdf_path.with_suffix(".outline.pdf")
    with tmp.open("wb") as handle:
        writer.write(handle)
    tmp.replace(pdf_path)
    print(json.dumps({"bookmarks": added, "missing": missing[:12], "missingCount": len(missing)}))


if __name__ == "__main__":
    main()
