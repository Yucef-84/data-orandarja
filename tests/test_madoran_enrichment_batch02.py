import json
import subprocess
import sys
import unittest

from scripts.apply_madoran_enrichment_batch02 import (
    BATCH_FIELDS,
    BATCH_ID,
    BATCH_OUT,
    BATCH_QA_OUT,
    MANIFEST_OUT,
    validate_batch_rows,
)
from scripts.build_madoran_enrichment_batch02 import TARGET_END, TARGET_START
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    ENRICHMENT_OUT,
    EVENTS_OUT,
    ROOT,
    SOURCE_OUT,
    read_tsv,
    check_provenance_events,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance


CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction_qa.json"
CORRECTION02_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction02_qa.json"
CORRECTION03_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction03_qa.json"
CORRECTION04_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction04_qa.json"
REVIEW_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_review.json"


class MadoranEnrichmentBatch02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch02_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch02_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["processing_flags_populated_rows"], 39)

    def test_batch02_states_and_flags_are_separated(self):
        target = [row for row in self.enrichment_rows if 65 <= int(row["sentno"]) <= 128]
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in target), 46)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 18)
        self.assertTrue(
            all(
                row["enrichment_state"] == "flagged"
                for row in target
                if "source_ambiguity" in row["processing_flags"]
                or "source_corruption" in row["processing_flags"]
            )
        )
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 39)
        self.assertEqual(
            sum(bool(row[field]) for row in target for field in EMPTY_FIELDS),
            64 * len(EMPTY_FIELDS),
        )

    def test_batch02_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], "9452f8a")
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags"])
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])
        self.assertEqual(manifest["schema_version"], "1.1.0")

    def test_batch02_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 4572)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 3723)

    def test_batch02_qa_evidence_passes(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["new_provenance_events"], 840)
        self.assertEqual(qa["total_provenance_events"], 2274)
        self.assertEqual(qa["draft_rows"], 46)
        self.assertEqual(qa["flagged_rows"], 18)
        self.assertEqual(qa["processing_flags_populated_rows"], 39)
        self.assertEqual(qa["outside_target_mutations"], 0)
        self.assertEqual(qa["morphology_gate"], "BLOCKED_UPSTREAM_DEFECT")
        self.assertEqual(qa["learning_unit_rows_created"], 0)
        self.assertEqual(qa["validator"], "PASS")
        self.assertEqual(qa["content_review_status"], "headgpt_passed")
        self.assertEqual(qa["review_id"], "MADORAN-ENRICH-002-REVIEW-01")
        self.assertEqual(qa["reviewed_commit"], "1a1a2dd")

    def test_batch02_review_evidence_passes(self):
        review = json.loads(REVIEW_OUT.read_text(encoding="utf-8"))
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["qa_passed_rows"], 46)
        self.assertEqual(len(review["flagged_rows"]), 18)
        self.assertEqual(review["linguistic_fields_modified"], 0)
        self.assertEqual(review["provenance_events_before"], 2274)
        self.assertEqual(review["provenance_events_after"], 2274)

    def test_batch02_correction_qa_evidence_passes(self):
        qa = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-002-CORRECTION-01")
        self.assertEqual(qa["corrected_rows"], ["80", "90", "96", "102", "105"])
        self.assertEqual(qa["changed_fields"], 15)
        self.assertEqual(qa["new_provenance_events"], 15)
        self.assertEqual(qa["provenance_events_before"], 2174)
        self.assertEqual(qa["provenance_events_after"], 2189)
        self.assertEqual(qa["arabic_modified"], 0)
        self.assertEqual(qa["validator"], "PASS")

    def test_batch02_correction02_qa_evidence_passes(self):
        qa = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-002-CORRECTION-02")
        self.assertEqual(len(qa["corrected_rows"]), 30)
        self.assertEqual(qa["changed_fields"], 67)
        self.assertEqual(qa["new_provenance_events"], 67)
        self.assertEqual(qa["provenance_events_before"], 2189)
        self.assertEqual(qa["provenance_events_after"], 2256)
        self.assertEqual(qa["draft_rows"], 46)
        self.assertEqual(qa["flagged_rows"], 18)
        self.assertEqual(qa["processing_flags_populated_rows"], 39)
        self.assertEqual(qa["arabic_modified"], 0)
        self.assertEqual(qa["validator"], "PASS")

    def test_batch02_correction03_qa_evidence_passes(self):
        qa = json.loads(CORRECTION03_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-002-CORRECTION-03")
        self.assertEqual(qa["corrected_rows"], ["85", "97", "99", "100", "117", "121"])
        self.assertEqual(qa["changed_fields"], 15)
        self.assertEqual(qa["new_provenance_events"], 15)
        self.assertEqual(qa["provenance_events_before"], 2256)
        self.assertEqual(qa["provenance_events_after"], 2271)
        self.assertEqual(qa["arabic_modified"], 0)
        self.assertEqual(qa["validator"], "PASS")

    def test_batch02_correction04_qa_evidence_passes(self):
        qa = json.loads(CORRECTION04_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["correction_id"], "MADORAN-ENRICH-002-CORRECTION-04")
        self.assertEqual(qa["corrected_rows"], ["97"])
        self.assertEqual(qa["changed_fields"], 3)
        self.assertEqual(qa["new_provenance_events"], 3)
        self.assertEqual(qa["provenance_events_before"], 2271)
        self.assertEqual(qa["provenance_events_after"], 2274)
        self.assertEqual(qa["arabic_modified"], 0)
        self.assertEqual(qa["validator"], "PASS")

    def test_full_validator_passes_after_batch02(self):
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
