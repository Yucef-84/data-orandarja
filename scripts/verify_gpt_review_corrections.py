"""Verify the GPT-review migration without rewriting the dataset.

The corrections are committed directly in the TSV.  Keeping this as a verifier
instead of a replayable mutator prevents an old correction map from silently
overwriting later human or native-speaker edits.
"""

from __future__ import annotations

import csv
from pathlib import Path


DATASET = Path(__file__).parents[1] / "data" / "oran_darija_verified.tsv"
LEARNER_READY = DATASET.with_name("oran_darija_learner_ready.tsv")
BUILD_SCRIPT = DATASET.parents[1] / "scripts" / "build_balanced_dataset.ps1"
SPECIAL = {"disputed", "metalinguistic_only", "fragment_only", "construction_specific", "native_review_required"}
ALLOWED_STATUS = {"attested", "lemma_from_attested", "metalinguistic_only", "fragment_only", "construction_specific", "study_backed", "native_review_required", "disputed"}
ALLOWED_MARKER = {"none", "loanword", "phonology", "grammar", "lexicon", "discourse", "metalinguistic", "fragment", "construction", "uncertain"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    with DATASET.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    require(len(rows) == 888, f"expected 888 rows, found {len(rows)}")
    require(len({row["id"] for row in rows}) == 888, "duplicate IDs")
    by_id = {row["id"]: row for row in rows}
    require(by_id["OD-0339"]["en"] == "your father", "OD-0339 translation drifted")
    expected = {
        "OD-0645": ("MADORAN_LEMMA_FROM_ATTESTED", "lemma_from_attested"),
        "OD-0702": ("MADORAN_CONSTRUCTION_SPECIFIC", "construction_specific"),
        "OD-0729": ("MADORAN_FRAGMENT_ONLY", "fragment_only"),
        "OD-0812": ("MADORAN_CONSTRUCTION_SPECIFIC", "construction_specific"),
    }
    for item_id, (evidence, status) in expected.items():
        require(by_id[item_id]["evidence"] == evidence, f"{item_id} evidence drifted")
        require(by_id[item_id]["status"] == status, f"{item_id} status drifted")
    require(all(row["status"] in ALLOWED_STATUS for row in rows), "unknown status enum")
    require(all(row["marker_type"] in ALLOWED_MARKER for row in rows), "unknown marker_type enum")
    require(by_id["OD-0702"]["source_form"] == "شا دخلني فناس", "OD-0702 exact source form drifted")
    require(by_id["OD-0812"]["topic"] == "verbs", "OD-0812 topic drifted")

    raw = LEARNER_READY.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "learner-ready TSV has a UTF-8 BOM")
    with LEARNER_READY.open(encoding="utf-8", newline="") as handle:
        learner_rows = list(csv.DictReader(handle, delimiter="\t"))
    require(len(learner_rows) == 883, f"expected 883 learner-ready rows, found {len(learner_rows)}")
    require(not any(row["status"] in SPECIAL for row in learner_rows), "special status leaked into learner-ready export")
    expected_ids = {row["id"] for row in rows if row["status"] not in SPECIAL}
    require({row["id"] for row in learner_rows} == expected_ids, "learner-ready IDs differ from canonical filter")

    build_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    require("Legacy 500-row inputs are not a reproducible release source" in build_text, "legacy rebuild guard missing")
    require("Write-Utf8NoBomCsv" in build_text, "UTF-8 no-BOM writer missing")
    print(f"OK: 888 canonical rows, {len(learner_rows)} learner-ready rows, {sum(row['status'] in SPECIAL for row in rows)} special-status rows")


if __name__ == "__main__":
    main()
