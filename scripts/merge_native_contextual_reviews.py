"""Merge two independent native-review files into the official manifest.

The command accepts reviewer-facing templates with extra context columns or
compact seven-column manifests. It writes the official manifest only after
both files are complete and exactly cover the packet.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
OUTPUT = ROOT / "reviews" / "native_contextual_reviews.tsv"
REVIEW_FIELDS = [
    "sample_id", "reviewer_id", "oran_native_confirmed", "rating",
    "suggested_arabic", "comment", "reviewed_at",
]
RATINGS = {"natural", "understandable_but_unusual", "not_oran", "wrong"}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def _packet_ids(packet_path: Path) -> set[str]:
    fields, rows = read_tsv(packet_path)
    if fields != [
        "sample_id", "cefr", "domain", "topic", "arabic", "latin", "ko", "en",
        "source_locator", "gpt_review_status",
    ]:
        raise ValueError("native review packet header does not match the packet schema")
    ids = [row.get("sample_id", "") for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("native review packet must contain unique sample IDs")
    return set(ids)


def _load_reviewer_file(path: Path, expected_ids: set[str]) -> tuple[str, list[dict[str, str]]]:
    fields, rows = read_tsv(path)
    missing_fields = [field for field in REVIEW_FIELDS if field not in fields]
    if missing_fields:
        raise ValueError(f"{path.name}: missing review fields {missing_fields}")
    if len(rows) != len(expected_ids):
        raise ValueError(f"{path.name}: expected {len(expected_ids)} rows, got {len(rows)}")
    ids = [row.get("sample_id", "") for row in rows]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError(f"{path.name}: sample IDs do not exactly match the review packet")
    reviewer_ids = {row.get("reviewer_id", "").strip() for row in rows}
    if len(reviewer_ids) != 1 or "" in reviewer_ids:
        raise ValueError(f"{path.name}: every row must have one non-empty reviewer_id")
    reviewer_id = next(iter(reviewer_ids))
    for row in rows:
        sid = row["sample_id"]
        if row.get("oran_native_confirmed") != "true":
            raise ValueError(f"{path.name}:{sid}: oran_native_confirmed must be true")
        if row.get("rating") not in RATINGS:
            raise ValueError(f"{path.name}:{sid}: invalid rating {row.get('rating', '')}")
        if not row.get("reviewed_at", "").strip():
            raise ValueError(f"{path.name}:{sid}: reviewed_at is required")
    return reviewer_id, rows


def merge_reviews(
    reviewer_paths: tuple[Path, Path],
    packet_path: Path = PACKET,
    output_path: Path = OUTPUT,
) -> dict[str, object]:
    expected_ids = _packet_ids(packet_path)
    reviewer_data = [_load_reviewer_file(path, expected_ids) for path in reviewer_paths]
    reviewer_ids = [item[0] for item in reviewer_data]
    if len(set(reviewer_ids)) != 2:
        raise ValueError("the two reviewer files must contain distinct reviewer_id values")
    rows = [row for _, file_rows in reviewer_data for row in file_rows]
    rows.sort(key=lambda row: (row["sample_id"], row["reviewer_id"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in REVIEW_FIELDS} for row in rows)
    return {"reviewers": sorted(reviewer_ids), "samples": len(expected_ids), "review_rows": len(rows), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reviewer_one", type=Path)
    parser.add_argument("reviewer_two", type=Path)
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        print(merge_reviews((args.reviewer_one, args.reviewer_two), args.packet, args.output))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
