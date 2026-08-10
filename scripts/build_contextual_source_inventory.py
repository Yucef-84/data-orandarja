"""Build a replayable inventory of unused Oran source sentences.

The inventory is intentionally not a learner dataset. It carries exact source
forms and locators so a later semantic, GPT, and native-review workflow can
select rows without silently composing new Darija sentences.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "sources"
    / "madoran_v2"
    / "Morphologically Annotated Orani-Arbaic Dialect Dat"
    / "Raw Data - Sentences"
    / "MADOran_Sentences.tsv"
)
CONTEXTUAL = ROOT / "data" / "contextual"
OUTPUT = CONTEXTUAL / "madoran_unused_source_inventory.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def used_source_numbers() -> set[int]:
    used: set[int] = set()
    for path in CONTEXTUAL.glob("oran_darija_contextual_batch*.tsv"):
        for row in read_tsv(path):
            match = re.fullmatch(r"MADOran_Sentences\.tsv:Sentno=(\d+)", row["source_locator"].strip())
            if match:
                used.add(int(match.group(1)))
    return used


def main() -> None:
    used = used_source_numbers()
    fields = [
        "source_id", "source_locator", "source_form", "word_count", "license_id",
        "selection_status", "candidate_level", "candidate_domain", "note",
    ]
    rows: list[dict[str, str]] = []
    for source in read_tsv(SOURCE):
        sentno = int(source["Sentno"])
        if sentno in used:
            continue
        rows.append(
            {
                "source_id": "S6",
                "source_locator": f"MADOran_Sentences.tsv:Sentno={sentno}",
                "source_form": source["Sentence"],
                "word_count": source["WordCount"],
                "license_id": "CC-BY-NC-3.0-MADORAN",
                "selection_status": "available",
                "candidate_level": "",
                "candidate_domain": "",
                "note": "Exact source inventory only; semantic, translation, GPT, and native review pending.",
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} unused source sentences to {OUTPUT}")


if __name__ == "__main__":
    main()
