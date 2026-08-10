import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_contextual_expansion import validate as validate_expansion


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
        self.assertEqual(
            report["learner_ready"],
            report["review_status"].get("native2_approved", 0),
        )

    def test_native_review_manifest_has_official_schema(self):
        with NATIVE_REVIEWS.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            header = next(reader)
            rows = list(reader)
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
        self.assertIn(len(rows), {0, 366})

    def test_validator_rejects_prohibited_derivation_and_spoofed_source(self):
        source = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / source.name
            rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline=""), delimiter="\t"))
            fieldnames = list(rows[0])

            rows[0]["derivation_type"] = "ai_composed"
            with temp_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(rows)
            report = validate_expansion([temp_path])
            self.assertTrue(any("derivation_type" in error for error in report["p0_errors"]))

            rows[0]["derivation_type"] = "source_direct"
            rows[0]["source_id"] = "S1"
            with temp_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(rows)
            report = validate_expansion([temp_path])
            self.assertTrue(any("replay adapter" in error for error in report["p0_errors"]))

    def test_validator_rejects_canonical_arabic_overlap(self):
        source = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
        canonical = ROOT / "data" / "oran_darija_verified.tsv"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / source.name
            with source.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            with canonical.open(encoding="utf-8-sig", newline="") as handle:
                canonical_arabic = next(csv.DictReader(handle, delimiter="\t"))["arabic"]
            rows[0]["arabic"] = canonical_arabic
            with temp_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(rows)
            report = validate_expansion([temp_path])
            self.assertTrue(any("canonical lexical core" in error for error in report["p0_errors"]))

    def test_validator_rejects_fixed_value_and_learner_ready_enum_bypass(self):
        source = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / source.name
            with source.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            rows[0]["language"] = "en"
            rows[0]["variety"] = "ar-DZ"
            rows[0]["learner_ready"] = "TRUE"
            with temp_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(rows)
            report = validate_expansion([temp_path])
            self.assertTrue(any("language must be ar" in error for error in report["p0_errors"]))
            self.assertTrue(any("variety must be ar-DZ-oran" in error for error in report["p0_errors"]))
            self.assertTrue(any("learner_ready must be true or false" in error for error in report["p0_errors"]))


if __name__ == "__main__":
    unittest.main()
