import csv
import tempfile
import unittest
from pathlib import Path

from scripts.validate_native_pilot import validate as validate_native_pilot


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
VALIDATOR = ROOT / "scripts" / "validate_native_pilot.py"


class NativePilotGateTests(unittest.TestCase):
    def test_packet_has_all_current_gpt_reviewed_rows(self):
        with PACKET.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="	"))
        self.assertEqual(len(rows), 183)
        self.assertEqual(len({row["sample_id"] for row in rows}), 183)
        self.assertTrue(all(row["gpt_review_status"] == "gpt_reviewed" for row in rows))

    def test_gate_is_blocked_without_external_native_reviews(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            review_path = Path(temp_dir) / "reviews.tsv"
            summary_path = Path(temp_dir) / "summary.tsv"
            review_path.write_text(
                "sample_id\treviewer_id\toran_native_confirmed\trating\tsuggested_arabic\tcomment\treviewed_at\n",
                encoding="utf-8",
            )
            summary_path.write_text(
                "sample_id\treviewer1_rating\treviewer2_rating\tagreement\tfinal_native_status\tresolution_note\n",
                encoding="utf-8",
            )
            report = validate_native_pilot(review_path, summary_path)
        self.assertEqual(report["gate_status"], "BLOCKED")
        self.assertEqual(report["metrics"]["target_active"], 183)
        self.assertEqual(report["metrics"]["review_rows"], 0)

    def test_gate_rejects_manifest_summary_mismatch_and_unresolved_disagreement(self):
        with PACKET.open(encoding="utf-8", newline="") as handle:
            packet_rows = list(csv.DictReader(handle, delimiter="\t"))
        review_fields = [
            "sample_id", "reviewer_id", "oran_native_confirmed", "rating",
            "suggested_arabic", "comment", "reviewed_at",
        ]
        summary_fields = [
            "sample_id", "reviewer1_rating", "reviewer2_rating", "agreement",
            "final_native_status", "resolution_note",
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            review_path = Path(temp_dir) / "reviews.tsv"
            summary_path = Path(temp_dir) / "summary.tsv"
            review_rows = []
            summary_rows = []
            for packet_row in packet_rows:
                sid = packet_row["sample_id"]
                review_rows.extend([
                    {"sample_id": sid, "reviewer_id": "R1", "oran_native_confirmed": "true", "rating": "natural", "suggested_arabic": "", "comment": "", "reviewed_at": ""},
                    {"sample_id": sid, "reviewer_id": "R2", "oran_native_confirmed": "true", "rating": "natural", "suggested_arabic": "", "comment": "", "reviewed_at": ""},
                ])
                summary_rows.append({"sample_id": sid, "reviewer1_rating": "natural", "reviewer2_rating": "natural", "agreement": "true", "final_native_status": "native2_approved", "resolution_note": ""})
            with review_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=review_fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(review_rows)
            with summary_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=summary_fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(summary_rows)
            report = validate_native_pilot(review_path, summary_path)
            self.assertEqual(report["gate_status"], "PASS")

            summary_rows[0]["reviewer2_rating"] = "wrong"
            with summary_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=summary_fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(summary_rows)
            report = validate_native_pilot(review_path, summary_path)
            self.assertEqual(report["gate_status"], "BLOCKED")
            self.assertTrue(any("summary ratings do not match" in error for error in report["p0_errors"]))

            summary_rows[0]["reviewer2_rating"] = "understandable_but_unusual"
            summary_rows[0]["agreement"] = "false"
            summary_rows[0]["final_native_status"] = "native2_approved"
            summary_rows[0]["resolution_note"] = ""
            review_rows[1]["rating"] = "understandable_but_unusual"
            with review_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=review_fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(review_rows)
            with summary_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=summary_fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(summary_rows)
            report = validate_native_pilot(review_path, summary_path)
            self.assertEqual(report["gate_status"], "BLOCKED")
            self.assertTrue(any("disagreement requires" in error for error in report["p0_errors"]))


if __name__ == "__main__":
    unittest.main()
