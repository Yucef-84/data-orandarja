"""Build a human-completion summary skeleton from the merged review manifest.

This tool computes only the two ratings and exact-string agreement. It leaves
final_native_status and resolution_note blank so it cannot auto-approve a
disagreement or promote a learner row.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
REVIEWS = ROOT / "reviews" / "native_contextual_reviews.tsv"
OUTPUT = ROOT / "reviews" / "native_contextual_review_summary_skeleton.tsv"
SUMMARY_FIELDS = [
    "sample_id", "reviewer1_rating", "reviewer2_rating", "agreement",
    "final_native_status", "resolution_note",
]
REVIEW_FIELDS = {
    "sample_id", "reviewer_id", "oran_native_confirmed", "rating",
    "suggested_arabic", "comment", "reviewed_at",
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def build_summary_skeleton(
    review_path: Path = REVIEWS,
    packet_path: Path = PACKET,
    output_path: Path = OUTPUT,
) -> dict[str, object]:
    packet_fields, packet_rows = read_tsv(packet_path)
    if not packet_rows or packet_fields[:1] != ["sample_id"]:
        raise ValueError("native review packet is empty or malformed")
    packet_ids = {row["sample_id"] for row in packet_rows}
    fields, review_rows = read_tsv(review_path)
    if not REVIEW_FIELDS.issubset(fields):
        raise ValueError("merged review manifest is missing official review fields")
    if len(review_rows) != len(packet_ids) * 2:
        raise ValueError("merged review manifest must contain exactly two rows per packet sample")
    by_sample: dict[str, list[dict[str, str]]] = {}
    for row in review_rows:
        by_sample.setdefault(row.get("sample_id", ""), []).append(row)
    if set(by_sample) != packet_ids or any(len(rows) != 2 for rows in by_sample.values()):
        raise ValueError("merged review manifest does not exactly cover two reviews per packet sample")
    reviewer_ids = {row.get("reviewer_id", "") for row in review_rows}
    if len(reviewer_ids) != 2 or "" in reviewer_ids:
        raise ValueError("merged review manifest must contain exactly two reviewer IDs")

    summary_rows = []
    for sample_id in sorted(packet_ids):
        sample_reviews = sorted(by_sample[sample_id], key=lambda row: row["reviewer_id"])
        rating_one = sample_reviews[0]["rating"]
        rating_two = sample_reviews[1]["rating"]
        summary_rows.append(
            {
                "sample_id": sample_id,
                "reviewer1_rating": rating_one,
                "reviewer2_rating": rating_two,
                "agreement": str(rating_one == rating_two).lower(),
                "final_native_status": "",
                "resolution_note": "",
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)
    return {"samples": len(summary_rows), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", type=Path, default=REVIEWS)
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        print(build_summary_skeleton(args.reviews, args.packet, args.output))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
