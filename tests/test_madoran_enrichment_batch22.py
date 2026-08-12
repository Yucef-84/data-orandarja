import json
import subprocess
import sys
import unittest

from scripts.build_madoran_enrichment_batch22 import (
    BATCH_ID, BATCH_OUT, MANIFEST_OUT, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_generation_qa.json"
CORRECTION01_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_correction02_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_review.json"


class MadoranEnrichmentBatch22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch22_range_and_source_linkage(self):
        source = {row["sentno"]: row["source_uid"] for row in self.source_rows}
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])
        self.assertTrue(all(row["source_uid"] == source[row["sentno"]] for row in self.batch_rows))
        self.assertEqual(len(self.batch_rows), 12)

    def test_batch22_generation_qa_pass(self):
        qa = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["batch_id"], BATCH_ID)
        self.assertEqual(qa["target_rows"], 12)
        self.assertEqual(qa["flagged_rows"], 12)
        self.assertEqual(qa["processing_flags_populated_rows"], 12)
        self.assertEqual(qa["required_linguistic_fields"], 132)
        self.assertEqual(qa["arabic_modified"], 0)
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["row_count"], 12)
        self.assertEqual(manifest["sentno_start"], 1345)
        self.assertEqual(manifest["sentno_end"], 1356)

    def test_batch22_application_qa_pass(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["provenance_events_before"], 19038)
        self.assertEqual(qa["new_provenance_events"], 152)
        self.assertEqual(qa["total_provenance_events"], 19190)
        self.assertEqual(qa["expected_total_provenance_events"], 19190)
        self.assertEqual(qa["batch_processing_flags_populated_rows"], 12)
        self.assertEqual(qa["outside_target_mutations"], 0)

    def test_batch22_headgpt_review_recorded(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["content_review_status"], "headgpt_passed")
        self.assertEqual(qa["review_id"], "MADORAN-ENRICH-022-REVIEW-01")
        self.assertEqual(review["reviewed_commit"], "92f08a2")
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["p2"], "NONE")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["provenance_summary"]["actual"], 19190)

    def test_batch22_state_and_content_contract(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 12)
        self.assertTrue(all(row["enrichment_state"] == "flagged" for row in target))
        self.assertTrue(all(row["processing_flags"] for row in target))
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 132)

    def test_batch22_provenance_and_validator_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 19190)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 16050)
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_batch22_correction01_qa_and_repairs(self):
        qa = json.loads(CORRECTION01_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-022-CORRECTION-01")
        self.assertEqual(qa["corrected_rows"], ["1350", "1352", "1355"])
        self.assertEqual(qa["changed_fields"], 6)
        self.assertEqual(qa["provenance_events_before"], 19182)
        self.assertEqual(qa["provenance_events_after"], 19188)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("whenever you enter", by_sentno[1350]["english"])
        self.assertIn("only I and a female patient will enter", by_sentno[1352]["english"])
        self.assertIn("wanted to go to my husband", by_sentno[1355]["english"])

    def test_batch22_correction02_qa_and_repairs(self):
        qa = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-022-CORRECTION-02")
        self.assertEqual(qa["corrected_rows"], ["1350"])
        self.assertEqual(qa["changed_fields"], 2)
        self.assertEqual(qa["provenance_events_before"], 19188)
        self.assertEqual(qa["provenance_events_after"], 19190)
        self.assertEqual(qa["draft_rows"], 0)
        self.assertEqual(qa["flagged_rows"], 12)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("you don’t like/love me anymore", by_sentno[1350]["english"])


if __name__ == "__main__":
    unittest.main()
