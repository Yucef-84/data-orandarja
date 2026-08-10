import csv
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH01 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
BATCH02 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch02.tsv"
EXPECTED_BATCH01_SHA256 = "4268fda4ffaff5e13c0a1a5bc1d948d695288501e3a504d03c3d0060dae15437"
EXPECTED_HOLD_IDS = {
    "ODC-000149", "ODC-000150", "ODC-000153", "ODC-000154", "ODC-000155",
    "ODC-000158", "ODC-000159", "ODC-000160", "ODC-000162", "ODC-000164",
    "ODC-000165", "ODC-000166", "ODC-000167", "ODC-000173", "ODC-000174",
    "ODC-000177", "ODC-000197",
}


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class ContextualBatch02Tests(unittest.TestCase):
    def test_batch02_shape_and_quota(self):
        current = rows(BATCH02)
        self.assertEqual(len(current), 104)
        self.assertEqual({row["sample_id"] for row in current}, {f"ODC-{i:06d}" for i in range(97, 201)})
        self.assertEqual(sum(row["cefr"] == "A1" for row in current), 45)
        self.assertEqual(sum(row["cefr"] == "A2" for row in current), 59)
        for domain in {"school_work", "city_transport", "body_health", "food_shopping"}:
            self.assertEqual(sum(row["domain"] == domain for row in current), 26)

    def test_batch02_is_pre_review_only(self):
        current = rows(BATCH02)
        self.assertTrue(all(row["review_status"] in {"source_verified", "hold"} for row in current))
        self.assertTrue(all(row["learner_ready"] == "false" for row in current))

    def test_batch02_hold_policy(self):
        current = rows(BATCH02)
        hold = {row["sample_id"] for row in current if row["review_status"] == "hold"}
        self.assertEqual(hold, EXPECTED_HOLD_IDS)
        self.assertEqual(sum(row["review_status"] == "hold" for row in current), 17)
        self.assertEqual(sum(row["review_status"] == "source_verified" for row in current), 87)
        self.assertTrue(all(row["learner_ready"] == "false" for row in current if row["review_status"] == "hold"))
        self.assertTrue(all(row["note"].startswith("HOLD:") for row in current if row["review_status"] == "hold"))

    def test_source_ids_and_arabic_are_unique_across_contextual_batches(self):
        first = rows(BATCH01)
        second = rows(BATCH02)
        first_source = {row["source_locator"] for row in first}
        second_source = [row["source_locator"] for row in second]
        self.assertEqual(len(second_source), len(set(second_source)))
        self.assertTrue(first_source.isdisjoint(second_source))
        first_arabic = {" ".join(row["arabic"].split()) for row in first}
        second_arabic = {" ".join(row["arabic"].split()) for row in second}
        self.assertTrue(first_arabic.isdisjoint(second_arabic))

    def test_batch01_is_frozen(self):
        digest = hashlib.sha256(BATCH01.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_BATCH01_SHA256)


if __name__ == "__main__":
    unittest.main()
