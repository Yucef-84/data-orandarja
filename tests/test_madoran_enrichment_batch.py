import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.apply_madoran_enrichment_batch import (
    BATCH_FIELDS,
    BATCH_OUT,
    BATCH_QA_OUT,
    CONTROLLED_VALUES,
    EMPTY_FIELDS,
    ENRICHMENT_OUT,
    EVENTS_OUT,
    MANIFEST_OUT,
    ROOT,
    TARGET_END,
    TARGET_START,
    validate_applied_state,
    validate_batch_rows,
)
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS,
    check_provenance_events,
    read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance


class MadoranEnrichmentBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(ROOT / "data" / "master" / "source" / "madoran_sentences.tsv")
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(1, 65)])

    def test_batch_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["populated_fields"], 64 * len(EMPTY_FIELDS))

    def test_batch_values_are_populated_and_controlled(self):
        for row in self.batch_rows:
            for field in EMPTY_FIELDS:
                self.assertTrue(row[field])
            self.assertTrue(row["latin"].isascii())
            self.assertIn(row["cefr_level"], {"A1", "A2", "B1", "B2", "C1", "C2"})
            self.assertIn(row["domain"], CONTROLLED_VALUES["domain"])
            self.assertIn(row["genre"], CONTROLLED_VALUES["genre"])
            self.assertIn(row["speech_act"], CONTROLLED_VALUES["speech_act"])
            self.assertIn(row["register"], CONTROLLED_VALUES["register"])
            self.assertIn(row["context_dependency"], CONTROLLED_VALUES["context_dependency"])
            self.assertGreaterEqual(int(row["difficulty_score"]), 0)
            self.assertLessEqual(int(row["difficulty_score"]), 100)

    def test_manifest_matches_batch_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], "MADORAN-ENRICH-001")
        self.assertEqual(manifest["base_commit"], "c8d85c7")
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], list(EMPTY_FIELDS))
        self.assertEqual(manifest["source_dependency"], "canonical_source_only")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_applied_state_is_exactly_targeted(self):
        target = [row for row in self.enrichment_rows if 1 <= int(row["sentno"]) <= 64]
        batch02 = [row for row in self.enrichment_rows if 65 <= int(row["sentno"]) <= 128]
        batch03 = [row for row in self.enrichment_rows if 129 <= int(row["sentno"]) <= 192]
        batch04 = [row for row in self.enrichment_rows if 193 <= int(row["sentno"]) <= 256]
        outside = [row for row in self.enrichment_rows if int(row["sentno"]) > 320]
        self.assertEqual(len(target), 64)
        self.assertTrue(all(row["enrichment_state"] == "qa_passed" for row in target if row["sentno"] not in {"17", "63"}))
        self.assertEqual(self.enrichment_rows[16]["enrichment_state"], "flagged")
        self.assertEqual(self.enrichment_rows[62]["enrichment_state"], "flagged")
        self.assertTrue(all(row["enrichment_state"] == "not_started" for row in outside))
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))
        self.assertEqual(sum(bool(row[field]) for row in outside for field in EMPTY_FIELDS), 0)
        self.assertEqual(len(batch02), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in batch02), 46)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in batch02), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in batch02), 18)
        self.assertEqual(sum(bool(row["processing_flags"]) for row in batch02), 39)
        self.assertEqual(sum(bool(row[field]) for row in batch02 for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))
        self.assertEqual(len(batch03), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in batch03), 50)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in batch03), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in batch03), 14)
        self.assertEqual(sum(bool(row["processing_flags"]) for row in batch03), 51)
        self.assertEqual(len(batch04), 64)
        self.assertEqual(sum(row["enrichment_state"] == "qa_passed" for row in batch04), 41)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in batch04), 0)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in batch04), 23)
        self.assertEqual(sum(bool(row["processing_flags"]) for row in batch04), 62)

    def test_headgpt_review_evidence_approves_batch01(self):
        review = json.loads(
            (ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["reviewed_commit"], "2031147")
        self.assertEqual(review["qa_passed_rows"], 62)
        self.assertEqual(review["flagged_rows"], ["17", "63"])
        self.assertEqual(review["provenance_events_before"], 1432)
        self.assertEqual(review["provenance_events_after"], 1432)

    def test_headgpt_review_evidence_approves_batch02(self):
        review = json.loads(
            (ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["reviewed_commit"], "1a1a2dd")
        self.assertEqual(review["qa_passed_rows"], 46)
        self.assertEqual(len(review["flagged_rows"]), 18)
        self.assertEqual(review["provenance_events_before"], 2274)
        self.assertEqual(review["provenance_events_after"], 2274)

    def test_headgpt_review_evidence_approves_batch03(self):
        review = json.loads(
            (ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["reviewed_commit"], "984272d")
        self.assertEqual(review["qa_passed_rows"], 50)
        self.assertEqual(len(review["flagged_rows"]), 14)
        self.assertEqual(review["provenance_events_before"], 3036)
        self.assertEqual(review["provenance_events_after"], 3036)

    def test_headgpt_review_evidence_approves_batch04(self):
        review = json.loads(
            (ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch04_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(review["headgpt_result"], "PASS")
        self.assertEqual(review["p0"], "NONE")
        self.assertEqual(review["p1"], "NONE")
        self.assertEqual(review["reviewed_commit"], "0df2021")
        self.assertEqual(review["qa_passed_rows"], 41)
        self.assertEqual(len(review["flagged_rows"]), 23)
        self.assertEqual(review["provenance_events_before"], 3819)
        self.assertEqual(review["provenance_events_after"], 3819)

    def test_provenance_is_field_level_and_hashed(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 4596)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 5 * 64 * len(EMPTY_FIELDS) + 205)

    def test_batch_qa_is_pass(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["new_provenance_events"], 3)
        self.assertEqual(qa["total_provenance_events"], 1432)
        self.assertEqual(qa["outside_target_mutations"], 0)
        self.assertEqual(qa["morphology_gate"], "BLOCKED_UPSTREAM_DEFECT")
        self.assertEqual(qa["validator"], "PASS")

    def test_invalid_batch_value_is_rejected(self):
        invalid = copy.deepcopy(self.batch_rows)
        invalid[0]["cefr_level"] = "C3"
        report = validate_batch_rows(self.source_rows, invalid)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("invalid_cefr:1", report["failures"])

    def test_outside_target_mutation_is_rejected(self):
        before = copy.deepcopy(self.enrichment_rows)
        after = copy.deepcopy(self.enrichment_rows)
        after[-1]["topic"] = "mutated"
        report = validate_applied_state(before, after)
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["outside_target_mutations"], 1)

    def test_full_validator_passes(self):
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
