import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch08 import (
    BATCH_ID,
    BATCH_OUT,
    BASE_COMMIT,
    MANIFEST_OUT,
    TARGET_END,
    TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    ENRICHMENT_OUT,
    EVENTS_OUT,
    ROOT,
    SOURCE_OUT,
    check_provenance_events,
    read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance


BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_correction02_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_review.json"


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end


class MadoranEnrichmentBatch08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch08_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch08_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 51)

    def test_batch08_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 13)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 51)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 51)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch08_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v8")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch08_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 7818)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 6739)

    def test_batch08_generation_and_correction_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 14)
        self.assertEqual(generation["flagged_rows"], 50)
        self.assertEqual(generation["processing_flags_populated_rows"], 50)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 6228)
        self.assertEqual(application["new_provenance_events"], 775)
        self.assertEqual(application["total_provenance_events"], 7003)
        self.assertEqual(application["draft_rows"], 13)
        self.assertEqual(application["flagged_rows"], 51)
        self.assertEqual(application["processing_flags_populated_rows"], 348)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 51)
        self.assertEqual(application["content_review_status"], "headgpt_passed")
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-008-CORRECTION-01")
        self.assertEqual(len(correction["corrected_rows"]), 8)
        self.assertEqual(correction["changed_fields"], 17)
        self.assertEqual(correction["state_updates"], 1)
        self.assertEqual(correction["provenance_events_before"], 6982)
        self.assertEqual(correction["provenance_events_after"], 6999)
        self.assertEqual(correction["validator"], "PASS")
        correction02 = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction02["result"], "PASS")
        self.assertEqual(correction02["correction_id"], "MADORAN-ENRICH-008-CORRECTION-02")
        self.assertEqual(correction02["corrected_rows"], ["468", "510"])
        self.assertEqual(correction02["changed_fields"], 4)
        self.assertEqual(correction02["provenance_events_before"], 6999)
        self.assertEqual(correction02["provenance_events_after"], 7003)
        self.assertEqual(correction02["validator"], "PASS")

        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["structure"], "PASS")
        self.assertEqual(review["provenance"], "PASS")
        self.assertEqual(review["isolation"], "PASS")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["reviewed_commit"], "bc8428485266d39e5c702dca2bc983595c4eb990")
        self.assertEqual(review["reviewed_batch_rows"], 64)
        self.assertEqual(review["qa_passed_rows"], 13)
        self.assertEqual(len(review["flagged_rows"]), 51)
        self.assertEqual(review["provenance_events_before"], 7003)
        self.assertEqual(review["provenance_events_after"], 7003)
        self.assertEqual(review["next_batch"]["sentno_start"], 513)
        self.assertEqual(review["batch_artifact_sync"], "PASS")

    def test_batch08_corrected_values_are_conservative(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("blurred or weak eyesight", rows[457]["english"])
        self.assertNotIn("blind woman", rows[457]["english"])
        self.assertIn("qarnful", rows[458]["english"])
        self.assertIn("ambiguous", rows[458]["english"])
        self.assertIn("living person's share", rows[462]["english"])
        self.assertIn("grave for him", rows[468]["english"])
        self.assertIn("running away from me with an axe", rows[468]["english"])
        self.assertIn("change your place", rows[469]["english"])
        self.assertIn("source_ambiguity", rows[482]["processing_flags"])
        self.assertEqual(rows[482]["enrichment_state"], "flagged")
        self.assertIn("making a chicken call", rows[494]["english"])
        self.assertIn("left nine behind", rows[510]["english"])
        self.assertIn("making the loss or problem worse", rows[510]["english"])

    def test_full_validator_passes_after_batch08_correction(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_madoran_enrichment.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
