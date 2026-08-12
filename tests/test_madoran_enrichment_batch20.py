import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch20 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, PROMPT_VERSION, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction02_qa.json"
CORRECTION03_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction03_qa.json"
CORRECTION04_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction04_qa.json"
REVIEW_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_review.json"


def validate_batch_rows(source_rows, batch_rows):
    old_start, old_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START, engine.TARGET_END = TARGET_START, TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START, engine.TARGET_END = old_start, old_end


class MadoranEnrichmentBatch20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch20_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch20_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 61)

    def test_batch20_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 11)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 53)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 61)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch20_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["prompt_version"], PROMPT_VERSION)
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch20_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 18580)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 15907)

    def test_batch20_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 7)
        self.assertEqual(generation["flagged_rows"], 57)
        self.assertEqual(generation["processing_flags_populated_rows"], 63)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 16851)
        self.assertEqual(application["new_provenance_events"], 961)
        self.assertEqual(application["total_provenance_events"], 17812)
        self.assertEqual(application["expected_total_provenance_events"], 17812)
        self.assertEqual(application["processing_flags_populated_rows"], 1059)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 61)
        self.assertEqual(application["content_review_status"], "headgpt_passed")
        self.assertEqual(application["review_id"], "MADORAN-ENRICH-020-REVIEW-01")
        self.assertEqual(application["reviewed_commit"], "7643b95")
        self.assertTrue(application["next_batch_allowed"])
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["changed_fields"], 136)
        self.assertEqual(correction["state_updates"], 9)
        self.assertEqual(correction["provenance_events_after"], 17754)
        self.assertEqual(correction["draft_rows"], 11)
        self.assertEqual(correction["flagged_rows"], 53)
        correction02 = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction02["result"], "PASS")
        self.assertEqual(correction02["changed_fields"], 30)
        self.assertEqual(correction02["provenance_events_after"], 17784)
        self.assertEqual(correction02["draft_rows"], 11)
        self.assertEqual(correction02["flagged_rows"], 53)
        correction03 = json.loads(CORRECTION03_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction03["result"], "PASS")
        self.assertEqual(correction03["changed_fields"], 22)
        self.assertEqual(correction03["provenance_events_after"], 17806)
        self.assertEqual(correction03["draft_rows"], 11)
        self.assertEqual(correction03["flagged_rows"], 53)
        correction04 = json.loads(CORRECTION04_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction04["result"], "PASS")
        self.assertEqual(correction04["changed_fields"], 6)
        self.assertEqual(correction04["provenance_events_after"], 17812)
        self.assertEqual(correction04["draft_rows"], 11)
        self.assertEqual(correction04["flagged_rows"], 53)
        review = json.loads(REVIEW_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["reviewed_commit"], "7643b95")
        self.assertEqual(review["reviewed_batch_rows"], 64)
        self.assertTrue(review["next_batch_allowed"])

    def test_full_validator_passes_after_batch20_application(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
