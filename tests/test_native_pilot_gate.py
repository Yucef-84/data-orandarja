import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


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
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["gate_status"], "BLOCKED")
        self.assertEqual(report["metrics"]["target_active"], 183)
        self.assertEqual(report["metrics"]["review_rows"], 0)


if __name__ == "__main__":
    unittest.main()
