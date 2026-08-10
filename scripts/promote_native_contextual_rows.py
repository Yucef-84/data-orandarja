"""Promote contextual rows only after the native certification gate passes."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from scripts.validate_native_pilot import SUMMARY, REVIEWS, validate


ROOT = Path(__file__).resolve().parents[1]
CONTEXTUAL = ROOT / "data" / "contextual"
ACTIVE = {"gpt_reviewed", "native1_reviewed", "native2_approved"}
FIELDS = [
    "sample_id", "language", "variety", "cefr", "domain", "topic", "sample_type",
    "arabic", "source_form", "latin", "ko", "en", "lexical_refs", "source_id",
    "source_locator", "evidence", "derivation_type", "license_id", "group_id",
    "family_id", "review_status", "learner_ready", "note",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _write_tsv_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    temporary = path.with_name(path.name + ".native-promotion.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def promote_native_rows(
    review_path: Path = REVIEWS,
    summary_path: Path = SUMMARY,
    batch_paths: list[Path] | None = None,
    apply: bool = False,
) -> dict[str, object]:
    paths = batch_paths if batch_paths is not None else sorted(CONTEXTUAL.glob("oran_darija_contextual_batch*.tsv"))
    report = validate(review_path=review_path, summary_path=summary_path, batch_paths=paths)
    result: dict[str, object] = {"gate": report, "applied": False, "promoted": 0}
    if report["gate_status"] != "PASS":
        return result

    target_ids = {
        row["sample_id"]
        for path in paths
        for row in read_tsv(path)
        if row["review_status"] in ACTIVE
    }
    if not apply:
        result["would_promote"] = len(target_ids)
        return result

    promoted = 0
    for path in paths:
        rows = read_tsv(path)
        for row in rows:
            if row["sample_id"] in target_ids and row["review_status"] in ACTIVE:
                if row["review_status"] != "native2_approved" or row["learner_ready"] != "true":
                    row["review_status"] = "native2_approved"
                    row["learner_ready"] = "true"
                    promoted += 1
        _write_tsv_atomic(path, rows)
    result["applied"] = True
    result["promoted"] = promoted
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", type=Path, default=REVIEWS)
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--batch", type=Path, action="append")
    parser.add_argument("--apply", action="store_true", help="write native2_approved/learner_ready=true only after PASS")
    args = parser.parse_args()
    result = promote_native_rows(args.reviews, args.summary, args.batch, args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"]["gate_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
