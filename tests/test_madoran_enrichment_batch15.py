import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch15 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, PROMPT_VERSION, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch15_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch15_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch15_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch15_correction02_qa.json"


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end


class MadoranEnrichmentBatch15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch15_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch15_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 61)

    def test_batch15_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 3)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 61)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 61)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch15_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], PROMPT_VERSION)
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch15_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 13046)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 11332)

    def test_batch15_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 3)
        self.assertEqual(generation["flagged_rows"], 61)
        self.assertEqual(generation["processing_flags_populated_rows"], 61)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 12216)
        self.assertEqual(application["new_provenance_events"], 830)
        self.assertEqual(application["total_provenance_events"], 13046)
        self.assertEqual(application["expected_total_provenance_events"], 13046)
        self.assertEqual(application["processing_flags_populated_rows"], 772)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 61)
        self.assertEqual(application["content_review_status"], "pending_headgpt_correction_review")
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["changed_fields"], 55)
        self.assertEqual(correction["provenance_events_after"], 13036)
        correction02 = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction02["result"], "PASS")
        self.assertEqual(correction02["changed_fields"], 10)
        self.assertEqual(correction02["provenance_events_after"], 13046)

    def test_full_validator_passes_after_batch15_application(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
