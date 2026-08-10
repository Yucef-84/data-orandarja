import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.build_native_contextual_review_summary_skeleton import build_summary_skeleton
from scripts.build_native_contextual_review_templates import build_templates
from scripts.merge_native_contextual_reviews import merge_reviews
from scripts.promote_native_contextual_rows import promote_native_rows
from scripts.validate_contextual_expansion import validate as validate_expansion


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reviews" / "native_contextual_review_packet.tsv"
BATCH01 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
BATCH02 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch02.tsv"


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class NativeReviewPlumbingTests(unittest.TestCase):
    def _complete_reviewer_template(self, path):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            rows = list(reader)
            fields = list(reader.fieldnames or [])
        for row in rows:
            row["oran_native_confirmed"] = "true"
            row["rating"] = "natural"
            row["reviewed_at"] = "2026-08-10T20:15:00+09:00"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_templates_merge_and_summary_skeleton_are_complete(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_paths = build_templates(PACKET, root / "templates")
            self.assertEqual([len(read_rows(path)) for path in template_paths], [183, 183])
            self._complete_reviewer_template(template_paths[0])
            self._complete_reviewer_template(template_paths[1])

            merged_path = root / "reviews.tsv"
            result = merge_reviews(tuple(template_paths), PACKET, merged_path)
            self.assertEqual(result["review_rows"], 366)
            self.assertEqual(len(read_rows(merged_path)), 366)

            skeleton_path = root / "summary_skeleton.tsv"
            skeleton_result = build_summary_skeleton(merged_path, PACKET, skeleton_path)
            self.assertEqual(skeleton_result["samples"], 183)
            skeleton_rows = read_rows(skeleton_path)
            self.assertEqual(len(skeleton_rows), 183)
            self.assertTrue(all(row["agreement"] == "true" for row in skeleton_rows))
            self.assertTrue(all(row["final_native_status"] == "" for row in skeleton_rows))

    def test_merge_rejects_incomplete_reviewer_file_without_writing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_paths = build_templates(PACKET, root / "templates")
            self._complete_reviewer_template(template_paths[0])
            self._complete_reviewer_template(template_paths[1])
            rows = read_rows(template_paths[1])[:-1]
            with template_paths[1].open(encoding="utf-8-sig", newline="") as handle:
                fields = list(csv.DictReader(handle, delimiter="\t").fieldnames or [])
            with template_paths[1].open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            output = root / "should_not_exist.tsv"
            with self.assertRaises(ValueError):
                merge_reviews(tuple(template_paths), PACKET, output)
            self.assertFalse(output.exists())

    def test_promotion_is_blocked_until_gate_passes_then_promotes_only_active_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_paths = build_templates(PACKET, root / "templates")
            self._complete_reviewer_template(template_paths[0])
            self._complete_reviewer_template(template_paths[1])
            merged_path = root / "reviews.tsv"
            merge_reviews(tuple(template_paths), PACKET, merged_path)
            skeleton_path = root / "summary_skeleton.tsv"
            build_summary_skeleton(merged_path, PACKET, skeleton_path)

            batch_paths = [root / BATCH01.name, root / BATCH02.name]
            for source, destination in zip((BATCH01, BATCH02), batch_paths):
                shutil.copyfile(source, destination)
            before = [path.read_bytes() for path in batch_paths]

            blocked = promote_native_rows(merged_path, skeleton_path, batch_paths, apply=True)
            self.assertEqual(blocked["gate"]["gate_status"], "BLOCKED")
            self.assertFalse(blocked["applied"])
            self.assertEqual([path.read_bytes() for path in batch_paths], before)

            summary_rows = read_rows(skeleton_path)
            with skeleton_path.open(encoding="utf-8", newline="") as handle:
                fields = list(csv.DictReader(handle, delimiter="\t").fieldnames or [])
            for row in summary_rows:
                row["final_native_status"] = "native2_approved"
            with skeleton_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(summary_rows)

            promoted = promote_native_rows(merged_path, skeleton_path, batch_paths, apply=True)
            self.assertEqual(promoted["gate"]["gate_status"], "PASS")
            self.assertTrue(promoted["applied"])
            self.assertEqual(promoted["promoted"], 183)
            first_rows = read_rows(batch_paths[0])
            second_rows = read_rows(batch_paths[1])
            self.assertTrue(all(row["review_status"] == "native2_approved" and row["learner_ready"] == "true" for row in first_rows))
            self.assertEqual(sum(row["review_status"] == "native2_approved" for row in second_rows), 87)
            self.assertEqual(sum(row["review_status"] == "hold" for row in second_rows), 17)
            promoted_report = validate_expansion(batch_paths)
            self.assertEqual(promoted_report["p0_errors"], [], promoted_report)
            self.assertEqual(promoted_report["learner_ready"], 183)


if __name__ == "__main__":
    unittest.main()
