import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch11 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_generation_qa.json"
CORRECTION01_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_correction02_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_review.json"


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end


class MadoranEnrichmentBatch11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch11_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch11_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 61)

    def test_batch11_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 3)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 61)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 61)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch11_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v11")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch11_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 12216)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 10567)

    def test_batch11_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 3)
        self.assertEqual(generation["flagged_rows"], 61)
        self.assertEqual(generation["processing_flags_populated_rows"], 61)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 8655)
        self.assertEqual(application["new_provenance_events"], 824)
        self.assertEqual(application["total_provenance_events"], 9479)
        self.assertEqual(application["expected_total_provenance_events"], 9479)
        self.assertEqual(application["processing_flags_populated_rows"], 526)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 61)
        self.assertEqual(application["content_review_status"], "headgpt_passed")

    def test_batch11_correction01_qa_pass(self):
        correction = json.loads(CORRECTION01_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-011-CORRECTION-01")
        self.assertEqual(correction["corrected_rows"], ["641", "644", "648", "652", "653", "654", "655", "658", "665", "671", "674", "675", "677", "679", "680", "682", "683", "685", "687", "688", "689", "691", "692", "694", "699", "701"])
        self.assertEqual(correction["changed_fields"], 52)
        self.assertEqual(correction["provenance_events_before"], 9420)
        self.assertEqual(correction["provenance_events_after"], 9472)
        self.assertEqual(correction["validator"], "PASS")
        self.assertEqual(correction["batch_artifact_sync"], "PASS")

    def test_batch11_correction02_qa_pass(self):
        correction = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-011-CORRECTION-02")
        self.assertEqual(correction["corrected_rows"], ["648", "665", "692", "694"])
        self.assertEqual(correction["changed_fields"], 7)
        self.assertEqual(correction["provenance_events_before"], 9472)
        self.assertEqual(correction["provenance_events_after"], 9479)
        self.assertEqual(correction["validator"], "PASS")
        self.assertEqual(correction["batch_artifact_sync"], "PASS")

    def test_batch11_headgpt_review_is_frozen(self):
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["reviewed_commit"], "208787d7982cfe08e1cc0204fc91ad0dd93c632d")
        self.assertEqual(review["reviewed_batch_rows"], 64)
        self.assertEqual(review["next_batch"]["batch_id"], "MADORAN-ENRICH-012")
        self.assertEqual(review["next_batch"]["sentno_start"], 705)
        self.assertEqual(review["next_batch"]["sentno_end"], 768)

    def test_full_validator_passes_after_batch11(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
