import json
import subprocess
import sys
import unittest

from scripts.apply_madoran_enrichment_batch06 import BATCH_OUT, BATCH_FIELDS, validate_batch_rows
from scripts.build_madoran_enrichment_batch06 import BASE_COMMIT, BATCH_ID, MANIFEST_OUT, TARGET_END, TARGET_START
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


BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_generation_qa.json"
CORRECTION01_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_correction02_qa.json"
CORRECTION03_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_correction03_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_review.json"


class MadoranEnrichmentBatch06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch06_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch06_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 44)

    def test_batch06_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 24)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 40)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 44)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch06_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v6")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch06_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 11250)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 9800)

    def test_batch06_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 24)
        self.assertEqual(generation["flagged_rows"], 40)
        self.assertEqual(generation["processing_flags_populated_rows"], 44)
        self.assertEqual(generation["arabic_modified"], 0)
        self.assertEqual(generation["morphology_reads"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 4596)
        self.assertEqual(application["new_provenance_events"], 817)
        self.assertEqual(application["total_provenance_events"], 5413)
        self.assertEqual(application["expected_total_provenance_events"], 5413)
        self.assertEqual(application["draft_rows"], 24)
        self.assertEqual(application["flagged_rows"], 40)
        self.assertEqual(application["processing_flags_populated_rows"], 249)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 44)
        self.assertEqual(application["content_review_status"], "headgpt_passed")

    def test_batch06_correction_evidence_passes(self):
        expected = [
            (CORRECTION01_QA_OUT, "MADORAN-ENRICH-006-CORRECTION-01", ["323", "324", "325", "326", "328", "329", "330", "331", "333", "341", "342", "343", "347", "348", "349", "355", "358", "360", "362", "367", "368", "380", "381"], 52, 5344, 5396),
            (CORRECTION02_QA_OUT, "MADORAN-ENRICH-006-CORRECTION-02", ["322", "328", "332", "346", "360", "381"], 11, 5396, 5407),
            (CORRECTION03_QA_OUT, "MADORAN-ENRICH-006-CORRECTION-03", ["337", "383"], 6, 5407, 5413),
        ]
        for path, correction_id, rows, fields, before, after in expected:
            correction = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(correction["result"], "PASS")
            self.assertEqual(correction["correction_id"], correction_id)
            self.assertEqual(correction["corrected_rows"], rows)
            self.assertEqual(correction["changed_fields"], fields)
            self.assertEqual(correction["new_provenance_events"], fields)
            self.assertEqual(correction["provenance_events_before"], before)
            self.assertEqual(correction["provenance_events_after"], after)
            self.assertEqual(correction["validator"], "PASS")
            self.assertEqual(correction["batch_artifact_sync"], "PASS")

    def test_batch06_corrected_values_are_present(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("unclear colloquial expression", rows[322]["english"])
        self.assertIn("400 meters", rows[328]["english"])
        self.assertIn("popular or widespread", rows[332]["english"])
        self.assertIn("Amina was given or written instead of Amira", rows[346]["english"])
        self.assertIn("Did I tell you to go out?", rows[360]["english"])
        self.assertEqual(rows[381]["context_dependency"], "medium")
        self.assertNotIn("fast-food", rows[337]["english"])
        self.assertIn("chicken stock cube", rows[383]["english"])
        self.assertEqual(rows[383]["topic"], "harira_lamb_and_chicken_stock_cube")
        self.assertEqual(rows[383]["context_dependency"], "high")

    def test_batch06_review_evidence_passes(self):
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["structure"], "PASS")
        self.assertEqual(review["provenance"], "PASS")
        self.assertEqual(review["isolation"], "PASS")
        self.assertTrue(review["next_batch_allowed"])
        self.assertEqual(review["reviewed_batch_rows"], 64)
        self.assertEqual(review["qa_passed_rows"], 24)
        self.assertEqual(len(review["flagged_rows"]), 40)
        self.assertEqual(review["provenance_events_before"], 5413)
        self.assertEqual(review["provenance_events_after"], 5413)
        self.assertEqual(review["batch_artifact_sync"], "PASS")

    def test_full_validator_passes_after_batch06(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_madoran_enrichment.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
