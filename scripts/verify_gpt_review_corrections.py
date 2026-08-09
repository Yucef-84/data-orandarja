"""Verify the GPT-review migration without rewriting the dataset.

The corrections are committed directly in the TSV.  Keeping this as a verifier
instead of a replayable mutator prevents an old correction map from silently
overwriting later human or native-speaker edits.
"""

from __future__ import annotations

import csv
from pathlib import Path


DATASET = Path(__file__).parents[1] / "data" / "oran_darija_verified.tsv"
SPECIAL = {"metalinguistic_only", "fragment_only", "construction_specific"}


def main() -> None:
    with DATASET.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    assert len(rows) == 888, f"expected 888 rows, found {len(rows)}"
    assert len({row["id"] for row in rows}) == 888, "duplicate IDs"
    by_id = {row["id"]: row for row in rows}
    assert by_id["OD-0339"]["en"] == "your father"
    expected = {
        "OD-0645": ("MADORAN_LEMMA_FROM_ATTESTED", "lemma_from_attested"),
        "OD-0702": ("MADORAN_CONSTRUCTION_SPECIFIC", "construction_specific"),
        "OD-0729": ("MADORAN_FRAGMENT_ONLY", "fragment_only"),
        "OD-0812": ("MADORAN_CONSTRUCTION_SPECIFIC", "construction_specific"),
    }
    for item_id, (evidence, status) in expected.items():
        assert by_id[item_id]["evidence"] == evidence, item_id
        assert by_id[item_id]["status"] == status, item_id
    print(f"OK: 888 rows, {sum(row['status'] in SPECIAL for row in rows)} special-status rows")


if __name__ == "__main__":
    main()
