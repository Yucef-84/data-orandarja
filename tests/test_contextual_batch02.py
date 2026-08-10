import csv
import hashlib
import io
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH01 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
BATCH02 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch02.tsv"
EXPECTED_BATCH01_IMMUTABLE_SHA256 = "4e4c706a8a9dcd6aa5dbf2fe6ebf0f28db2808bb995ea7581f5e76e1e7934907"
EXPECTED_BATCH02_IMMUTABLE_SHA256 = "ec1d117db46c104dc901017082bb6155ba84a0d29977911ce3b3507f024456a6"
IMMUTABLE_FIELDS = [
    "sample_id", "language", "variety", "cefr", "domain", "topic", "sample_type",
    "arabic", "source_form", "latin", "ko", "en", "lexical_refs", "source_id",
    "source_locator", "evidence", "derivation_type", "license_id", "group_id", "family_id", "note",
]
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

    def test_batch02_state_policy(self):
        current = rows(BATCH02)
        allowed = {"source_verified", "gpt_reviewed", "native1_reviewed", "native2_approved", "hold"}
        self.assertTrue(all(row["review_status"] in allowed for row in current))
        self.assertTrue(all(
            row["learner_ready"] == ("true" if row["review_status"] == "native2_approved" else "false")
            for row in current
        ))

    def test_batch02_hold_policy(self):
        current = rows(BATCH02)
        hold = {row["sample_id"] for row in current if row["review_status"] == "hold"}
        self.assertEqual(hold, EXPECTED_HOLD_IDS)
        self.assertEqual(sum(row["review_status"] == "hold" for row in current), 17)
        self.assertEqual(sum(row["review_status"] != "hold" for row in current), 87)
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

    def test_immutable_content_projection_is_frozen(self):
        def digest(path):
            current = rows(path)
            output = io.StringIO(newline="")
            writer = csv.DictWriter(
                output,
                fieldnames=IMMUTABLE_FIELDS,
                delimiter="\t",
                lineterminator="\n",
                quoting=csv.QUOTE_ALL,
            )
            writer.writeheader()
            writer.writerows({field: row.get(field, "") for field in IMMUTABLE_FIELDS} for row in current)
            return hashlib.sha256(output.getvalue().encode("utf-8")).hexdigest()

        self.assertEqual(digest(BATCH01), EXPECTED_BATCH01_IMMUTABLE_SHA256)
        self.assertEqual(digest(BATCH02), EXPECTED_BATCH02_IMMUTABLE_SHA256)


if __name__ == "__main__":
    unittest.main()
