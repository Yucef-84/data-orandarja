import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch17 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, PROMPT_VERSION, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction02_qa.json"
CORRECTION03_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction03_qa.json"
CORRECTION04_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction04_qa.json"
CORRECTION05_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction05_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_review.json"


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end


class MadoranEnrichmentBatch17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch17_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch17_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 62)

    def test_batch17_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 7)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 57)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 62)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch17_manifest_contract(self):
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

    def test_batch17_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 14973)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 12863)

    def test_batch17_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 3)
        self.assertEqual(generation["flagged_rows"], 61)
        self.assertEqual(generation["processing_flags_populated_rows"], 64)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 13943)
        self.assertEqual(application["new_provenance_events"], 1030)
        self.assertEqual(application["total_provenance_events"], 14973)
        self.assertEqual(application["expected_total_provenance_events"], 14973)
        self.assertEqual(application["processing_flags_populated_rows"], 895)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 62)
        self.assertEqual(application["content_review_status"], "headgpt_passed")
        self.assertEqual(application["correction_state_updates"], 0)
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["changed_fields"], 210)
        self.assertEqual(correction["provenance_events_before"], 14711)
        self.assertEqual(correction["provenance_events_after"], 14921)
        correction02 = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction02["result"], "PASS")
        self.assertEqual(correction02["changed_fields"], 2)
        self.assertEqual(correction02["state_updates"], 2)
        self.assertEqual(correction02["draft_rows"], 5)
        self.assertEqual(correction02["flagged_rows"], 59)
        self.assertEqual(correction02["provenance_events_before"], 14921)
        self.assertEqual(correction02["provenance_events_after"], 14923)
        correction03 = json.loads(CORRECTION03_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction03["result"], "PASS")
        self.assertEqual(correction03["changed_fields"], 36)
        self.assertEqual(correction03["draft_rows"], 5)
        self.assertEqual(correction03["flagged_rows"], 59)
        self.assertEqual(correction03["provenance_events_before"], 14923)
        self.assertEqual(correction03["provenance_events_after"], 14959)
        correction04 = json.loads(CORRECTION04_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction04["result"], "PASS")
        self.assertEqual(correction04["changed_fields"], 12)
        self.assertEqual(correction04["state_updates"], 2)
        self.assertEqual(correction04["draft_rows"], 7)
        self.assertEqual(correction04["flagged_rows"], 57)
        self.assertEqual(correction04["provenance_events_before"], 14959)
        self.assertEqual(correction04["provenance_events_after"], 14971)
        correction05 = json.loads(CORRECTION05_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction05["result"], "PASS")
        self.assertEqual(correction05["changed_fields"], 2)
        self.assertEqual(correction05["state_updates"], 0)
        self.assertEqual(correction05["draft_rows"], 7)
        self.assertEqual(correction05["flagged_rows"], 57)
        self.assertEqual(correction05["provenance_events_before"], 14971)
        self.assertEqual(correction05["provenance_events_after"], 14973)

    def test_batch17_headgpt_approval_is_frozen(self):
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["review_id"], "MADORAN-ENRICH-017-REVIEW-01")
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["p2"], "NONE")
        self.assertEqual(review["structure"], "PASS")
        self.assertEqual(review["provenance"], "PASS")
        self.assertEqual(review["isolation"], "PASS")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["qa_passed_rows"], 7)
        self.assertEqual(len(review["flagged_rows"]), 57)
        self.assertEqual(review["provenance_events_before"], 13943)
        self.assertEqual(review["provenance_events_after"], 14973)
        self.assertEqual(review["next_batch"]["batch_id"], "MADORAN-ENRICH-018")
        self.assertEqual(review["next_batch"]["sentno_start"], 1089)
        self.assertEqual(review["next_batch"]["sentno_end"], 1152)

    def test_full_validator_passes_after_batch17_application(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
