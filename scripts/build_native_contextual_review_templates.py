"""Build two independent, reviewer-facing native review templates.

The templates carry the read-only context from the packet plus the seven
official review-manifest fields. They are intentionally separate so reviewer
one cannot see reviewer two's ratings or comments.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
OUTPUT_DIR = ROOT / "reviews" / "native_contextual_templates"
PACKET_FIELDS = [
    "sample_id", "cefr", "domain", "topic", "arabic", "latin", "ko", "en",
    "source_locator", "gpt_review_status",
]
REVIEW_FIELDS = [
    "reviewer_id", "oran_native_confirmed", "rating", "suggested_arabic",
    "comment", "reviewed_at",
]
TEMPLATE_FIELDS = ["sample_id", *PACKET_FIELDS[1:-1], *REVIEW_FIELDS]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_templates(
    packet_path: Path = PACKET,
    output_dir: Path = OUTPUT_DIR,
    reviewer_ids: tuple[str, str] = ("ORAN_R1", "ORAN_R2"),
) -> list[Path]:
    if len(reviewer_ids) != 2 or reviewer_ids[0] == reviewer_ids[1]:
        raise ValueError("reviewer_ids must contain two distinct IDs")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", reviewer_id) for reviewer_id in reviewer_ids):
        raise ValueError("reviewer IDs may contain only ASCII letters, digits, underscore, and hyphen")

    packet_rows = read_tsv(packet_path)
    packet_fields = list(packet_rows[0]) if packet_rows else []
    if packet_fields != PACKET_FIELDS:
        raise ValueError("native review packet header does not match the packet schema")
    sample_ids = [row["sample_id"] for row in packet_rows]
    if not sample_ids or len(sample_ids) != len(set(sample_ids)):
        raise ValueError("native review packet must contain unique sample IDs")

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for reviewer_id in reviewer_ids:
        rows = []
        for packet_row in packet_rows:
            row = {field: packet_row[field] for field in PACKET_FIELDS[:-1]}
            row.update(
                {
                    "reviewer_id": reviewer_id,
                    "oran_native_confirmed": "",
                    "rating": "",
                    "suggested_arabic": "",
                    "comment": "",
                    "reviewed_at": "",
                }
            )
            rows.append(row)
        path = output_dir / f"native_contextual_review_{reviewer_id}.tsv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=TEMPLATE_FIELDS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--reviewer-one", default="ORAN_R1")
    parser.add_argument("--reviewer-two", default="ORAN_R2")
    args = parser.parse_args()
    for path in build_templates(args.packet, args.output_dir, (args.reviewer_one, args.reviewer_two)):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
