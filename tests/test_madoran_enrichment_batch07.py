import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch07 import (
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


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end

BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_generation_qa.json"
CORRECTION01_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_correction02_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_review.json"


class MadoranEnrichmentBatch07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch07_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch07_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 48)

    def test_batch07_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 23)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 41)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 48)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch07_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v7")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch07_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 8655)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 7505)

    def test_batch07_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 23)
        self.assertEqual(generation["flagged_rows"], 41)
        self.assertEqual(generation["processing_flags_populated_rows"], 46)
        self.assertEqual(generation["arabic_modified"], 0)
        self.assertEqual(generation["morphology_reads"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 5413)
        self.assertEqual(application["new_provenance_events"], 815)
        self.assertEqual(application["total_provenance_events"], 6228)
        self.assertEqual(application["expected_total_provenance_events"], 6228)
        self.assertEqual(application["draft_rows"], 23)
        self.assertEqual(application["flagged_rows"], 41)
        self.assertEqual(application["processing_flags_populated_rows"], 297)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 48)
        self.assertEqual(application["content_review_status"], "headgpt_passed")

    def test_batch07_correction_evidence_passes(self):
        expected = [
            (CORRECTION01_QA_OUT, "MADORAN-ENRICH-007-CORRECTION-01", 22, 45, 6164, 6209, 296, 47),
            (CORRECTION02_QA_OUT, "MADORAN-ENRICH-007-CORRECTION-02", 9, 19, 6209, 6228, 297, 48),
        ]
        for path, correction_id, rows, fields, before, after, global_flags, batch_flags in expected:
            correction = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(correction["result"], "PASS")
            self.assertEqual(correction["correction_id"], correction_id)
            self.assertEqual(len(correction["corrected_rows"]), rows)
            self.assertEqual(correction["changed_fields"], fields)
            self.assertEqual(correction["new_provenance_events"], fields)
            self.assertEqual(correction["provenance_events_before"], before)
            self.assertEqual(correction["provenance_events_after"], after)
            self.assertEqual(correction["processing_flags_populated_rows"], global_flags)
            self.assertEqual(correction["batch_processing_flags_populated_rows"], batch_flags)
            self.assertEqual(correction["validator"], "PASS")
            self.assertEqual(correction["batch_artifact_sync"], "PASS")

    def test_batch07_corrected_values_are_present(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("qarfou", rows[390]["english"])
        self.assertNotIn("cinnamon", rows[390]["english"])
        self.assertNotIn("ingredient", rows[391]["english"])
        self.assertIn("three cloves of grated garlic", rows[393]["english"])
        self.assertIn("wanted more", rows[399]["english"])
        self.assertIn("asphalt", rows[404]["english"])
        self.assertIn("Little Kholoud", rows[410]["english"])
        self.assertIn("are served food too", rows[418]["english"])
        self.assertIn("source_ambiguity", rows[418]["processing_flags"])
        self.assertIn("what was wrong", rows[422]["english"])
        self.assertNotIn("Malika", rows[422]["english"])
        self.assertIn("well-built", rows[426]["english"])
        self.assertIn("electricity bill", rows[441]["english"])

    def test_batch07_review_evidence_passes(self):
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["structure"], "PASS")
        self.assertEqual(review["provenance"], "PASS")
        self.assertEqual(review["isolation"], "PASS")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["reviewed_batch_rows"], 64)
        self.assertEqual(review["qa_passed_rows"], 23)
        self.assertEqual(len(review["flagged_rows"]), 41)
        self.assertEqual(review["provenance_events_before"], 6228)
        self.assertEqual(review["provenance_events_after"], 6228)
        self.assertEqual(review["next_batch"]["sentno_start"], 449)
        self.assertEqual(review["batch_artifact_sync"], "PASS")

    def test_full_validator_passes_after_batch07(self):
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
