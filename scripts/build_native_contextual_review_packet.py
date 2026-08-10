"""Build the read-only packet for the two independent native reviewers."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXTUAL = ROOT / "data" / "contextual"
OUTPUT = ROOT / "reviews" / "native_contextual_review_packet.tsv"
ACTIVE = {"gpt_reviewed", "native1_reviewed", "native2_approved"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows: list[dict[str, str]] = []
    for path in sorted(CONTEXTUAL.glob("oran_darija_contextual_batch*.tsv")):
        for row in read_tsv(path):
            if row["review_status"] in ACTIVE:
                rows.append(
                    {
                        "sample_id": row["sample_id"],
                        "cefr": row["cefr"],
                        "domain": row["domain"],
                        "topic": row["topic"],
                        "arabic": row["arabic"],
                        "latin": row["latin"],
                        "ko": row["ko"],
                        "en": row["en"],
                        "source_locator": row["source_locator"],
                        "gpt_review_status": row["review_status"],
                    }
                )
    rows.sort(key=lambda row: row["sample_id"])
    fields = list(rows[0]) if rows else [
        "sample_id", "cefr", "domain", "topic", "arabic", "latin", "ko", "en",
        "source_locator", "gpt_review_status",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} native-review packet rows to {OUTPUT}")


if __name__ == "__main__":
    main()
