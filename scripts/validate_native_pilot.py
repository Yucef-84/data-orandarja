"""Validate the independent Oran-native pilot gate.

The gate is intentionally blocked until two independent reviewers provide a
complete manifest and the summary records a resolved final status for every
active GPT-reviewed row.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXTUAL = ROOT / "data" / "contextual"
REVIEWS = ROOT / "reviews" / "native_contextual_reviews.tsv"
SUMMARY = ROOT / "reviews" / "native_contextual_review_summary.tsv"
ACTIVE = {"gpt_reviewed", "native1_reviewed", "native2_approved"}
RATINGS = {"natural", "understandable_but_unusual", "not_oran", "wrong"}
ACCEPTABLE = {"natural", "understandable_but_unusual"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate(
    review_path: Path = REVIEWS,
    summary_path: Path = SUMMARY,
    batch_paths: list[Path] | None = None,
) -> dict[str, object]:
    errors: list[str] = []
    target: dict[str, dict[str, str]] = {}
    paths = batch_paths if batch_paths is not None else sorted(CONTEXTUAL.glob("oran_darija_contextual_batch*.tsv"))
    for path in sorted(paths):
        for row in read_tsv(path):
            if row["review_status"] in ACTIVE:
                target[row["sample_id"]] = row

    reviews = read_tsv(review_path) if review_path.exists() else []
    summary = read_tsv(summary_path) if summary_path.exists() else []
    by_sample: dict[str, list[dict[str, str]]] = {}
    for row in reviews:
        sid = row.get("sample_id", "")
        if sid not in target:
            errors.append(f"review row references non-active sample {sid}")
        by_sample.setdefault(sid, []).append(row)
        if not row.get("reviewer_id", "").strip():
            errors.append(f"{sid}: reviewer_id is required")
        if row.get("oran_native_confirmed") != "true":
            errors.append(f"{sid}: reviewer {row.get('reviewer_id', '')} is not confirmed Oran-native")
        if row.get("rating") not in RATINGS:
            errors.append(f"{sid}: invalid rating {row.get('rating', '')}")

    complete_samples = 0
    for sid in sorted(target):
        sample_reviews = by_sample.get(sid, [])
        reviewer_ids = [row.get("reviewer_id", "") for row in sample_reviews]
        if len(sample_reviews) != 2 or len(set(reviewer_ids)) != 2:
            errors.append(f"{sid}: requires exactly two independent reviewer rows")
        elif all(row.get("rating") in RATINGS for row in sample_reviews):
            complete_samples += 1

    summary_by_sample: dict[str, dict[str, str]] = {}
    for row in summary:
        sid = row.get("sample_id", "")
        if sid in summary_by_sample:
            errors.append(f"{sid}: duplicate native summary sample_id")
        summary_by_sample[sid] = row
    for sid in sorted(set(summary_by_sample) - set(target)):
        errors.append(f"summary row references non-active sample {sid}")
    for sid in sorted(target):
        row = summary_by_sample.get(sid)
        if row is None:
            errors.append(f"{sid}: missing native summary")
            continue
        if row.get("final_native_status") not in {"native2_approved", "disputed", "rejected"}:
            errors.append(f"{sid}: unresolved final_native_status")
        if row.get("agreement") not in {"true", "false"}:
            errors.append(f"{sid}: agreement must be true/false")
        sample_reviews = by_sample.get(sid, [])
        reviewer_ids = {review.get("reviewer_id", "") for review in sample_reviews}
        if len(sample_reviews) == 2 and len(reviewer_ids) == 2:
            ratings = sorted(review.get("rating", "") for review in sample_reviews)
            summary_ratings = sorted(
                [row.get("reviewer1_rating", ""), row.get("reviewer2_rating", "")]
            )
            if summary_ratings != ratings:
                errors.append(f"{sid}: summary ratings do not match reviewer manifest")
            expected_agreement = ratings[0] == ratings[1]
            actual_agreement = row.get("agreement") == "true"
            if actual_agreement != expected_agreement:
                errors.append(f"{sid}: summary agreement does not match reviewer ratings")
            if not expected_agreement and not row.get("resolution_note", "").strip():
                errors.append(f"{sid}: disagreement requires a non-empty resolution_note")
            if row.get("final_native_status") == "native2_approved" and not all(
                rating in ACCEPTABLE for rating in ratings
            ):
                errors.append(f"{sid}: native2_approved requires two acceptable ratings")

    rating_counts = Counter(row.get("rating", "") for row in reviews)
    acceptable_count = sum(count for rating, count in rating_counts.items() if rating in ACCEPTABLE)
    review_total = len(reviews)
    wrong_not_oran = rating_counts["wrong"] + rating_counts["not_oran"]
    agreement_count = sum(
        1
        for sid in target
        if len(by_sample.get(sid, [])) == 2
        and by_sample[sid][0].get("rating") == by_sample[sid][1].get("rating")
    )
    agreement_denominator = sum(len(by_sample.get(sid, [])) == 2 for sid in target)
    metrics = {
        "target_active": len(target),
        "review_rows": review_total,
        "complete_samples": complete_samples,
        "summary_rows": len(summary),
        "acceptable_rate": acceptable_count / review_total if review_total else 0.0,
        "wrong_plus_not_oran_rate": wrong_not_oran / review_total if review_total else 0.0,
        "reviewer_agreement_rate": agreement_count / agreement_denominator if agreement_denominator else 0.0,
    }
    summary_complete = len(summary) == len(target) and set(summary_by_sample) == set(target)
    all_final_approved = summary_complete and all(
        row.get("final_native_status") == "native2_approved" for row in summary
    )
    gate_pass = (
        not errors
        and metrics["target_active"] > 0
        and metrics["acceptable_rate"] >= 0.95
        and metrics["wrong_plus_not_oran_rate"] <= 0.02
        and metrics["reviewer_agreement_rate"] >= 0.90
        and all_final_approved
    )
    return {
        "p0_errors": errors,
        "gate_status": "PASS" if gate_pass else "BLOCKED",
        "metrics": metrics,
        "learner_ready_eligible": sum(
            row.get("final_native_status") == "native2_approved" for row in summary
        ) if gate_pass else 0,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["gate_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
