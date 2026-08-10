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
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
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


def _canonical_target_ids() -> set[str]:
    return {
        row["sample_id"]
        for row in read_tsv(PACKET)
        if row.get("sample_id", "").strip()
    }


def _scope_errors(paths: list[Path]) -> list[str]:
    canonical_ids = _canonical_target_ids()
    active_rows = [
        row
        for path in paths
        for row in read_tsv(path)
        if row.get("review_status") in ACTIVE
    ]
    active_ids = {row.get("sample_id", "") for row in active_rows}
    errors: list[str] = []
    if len(canonical_ids) != 183:
        errors.append(f"canonical native pilot packet must contain 183 samples, found {len(canonical_ids)}")
    if len(active_rows) != len(canonical_ids) or active_ids != canonical_ids:
        missing = sorted(canonical_ids - active_ids)
        extra = sorted(active_ids - canonical_ids)
        errors.append(
            "promotion target must be the complete canonical 183-row pilot scope "
            f"(active_rows={len(active_rows)}, missing={missing[:3]}, extra={extra[:3]})"
        )
    return errors


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
    scope_errors = _scope_errors(paths)
    if scope_errors:
        report["p0_errors"] = [*report.get("p0_errors", []), *scope_errors]
        report["gate_status"] = "BLOCKED"
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
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--batch", type=Path, action="append")
    parser.add_argument("--apply", action="store_true", help="write native2_approved/learner_ready=true only after PASS")
    args = parser.parse_args()
    if args.apply and (args.reviews is not None or args.summary is not None or args.batch):
        parser.error("--apply requires the canonical review, summary, and batch files; custom paths are dry-run only")
    result = promote_native_rows(
        args.reviews or REVIEWS,
        args.summary or SUMMARY,
        args.batch,
        args.apply,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"]["gate_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
