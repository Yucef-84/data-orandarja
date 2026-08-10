import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "contextual" / "schema_v2.json"
INVENTORY = ROOT / "data" / "contextual" / "madoran_unused_source_inventory.tsv"
VALIDATOR = ROOT / "scripts" / "validate_contextual_expansion.py"
NATIVE_REVIEWS = ROOT / "reviews" / "native_contextual_reviews.tsv"


class ContextualExpansionPolicyTests(unittest.TestCase):
    def test_schema_has_b2_and_native_gate(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["levels"], ["A1", "A2", "B1", "B2"])
        self.assertEqual(schema["target_active_counts"]["total"], 4200)
        self.assertEqual(schema["state_policy"]["learner_ready_requires"], "native2_approved")

    def test_inventory_is_exactly_unused_source_pool(self):
        with INVENTORY.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 1156)
        self.assertTrue(all(row["source_id"] == "S6" for row in rows))
        self.assertTrue(all(row["selection_status"] == "available" for row in rows))
        self.assertTrue(all(not row["candidate_level"] and not row["candidate_domain"] for row in rows))
        self.assertEqual(len({row["source_locator"] for row in rows}), len(rows))

    def test_validator_reports_current_pilot_state(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["p0_errors"], [])
        self.assertEqual(report["rows_raw"], 200)
        self.assertEqual(report["active"], 183)
        self.assertEqual(report["hold"], 17)
        self.assertEqual(report["learner_ready"], 0)

    def test_native_review_manifest_is_separate_and_empty(self):
        with NATIVE_REVIEWS.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            header = next(reader)
            rows = list(reader)
        self.assertEqual(rows, [])
        self.assertEqual(
            header,
            [
                "sample_id",
                "reviewer_id",
                "oran_native_confirmed",
                "rating",
                "suggested_arabic",
                "comment",
                "reviewed_at",
            ],
        )


if __name__ == "__main__":
    unittest.main()
