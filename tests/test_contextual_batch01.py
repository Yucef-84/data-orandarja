import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_contextual import (  # noqa: E402
    BATCH,
    CANONICAL,
    EXPECTED_CANONICAL_SHA256,
    validate,
)


class ContextualBatch01Tests(unittest.TestCase):
    def test_p0_gates_pass(self):
        report = validate()
        self.assertEqual(report["p0_errors"], [], report)

    def test_batch_shape(self):
        report = validate()
        self.assertEqual(report["rows"], 96)
        self.assertEqual(report["cefr_counts"], {"A1": 48, "A2": 48})
        self.assertEqual(
            report["domain_counts"],
            {
                "school_work": 24,
                "city_transport": 24,
                "body_health": 24,
                "food_shopping": 24,
            },
        )

    def test_canonical_bytes_are_unchanged(self):
        digest = hashlib.sha256(CANONICAL.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_CANONICAL_SHA256)
        self.assertTrue(BATCH.exists())

    def test_batch_is_not_learner_ready_before_review(self):
        report = validate()
        self.assertEqual(report["p1_manual_review_pending"], 96)


if __name__ == "__main__":
    unittest.main()
