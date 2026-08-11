import json
import subprocess
import sys
import unittest

from scripts.apply_madoran_enrichment_batch05 import (
    BATCH_FIELDS,
    BATCH_ID,
    BATCH_OUT,
    BATCH_QA_OUT,
    MANIFEST_OUT,
    validate_batch_rows,
)
from scripts.build_madoran_enrichment_batch05 import BASE_COMMIT, TARGET_END, TARGET_START
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


GENERATION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_correction01_qa.json"


class MadoranEnrichmentBatch05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch05_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch05_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 49)

    def test_batch05_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 34)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 30)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 51)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch05_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v5")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch05_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 4596)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 3725)

    def test_batch05_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 36)
        self.assertEqual(generation["flagged_rows"], 28)
        self.assertEqual(generation["processing_flags_populated_rows"], 49)
        self.assertEqual(generation["arabic_modified"], 0)
        self.assertEqual(generation["morphology_reads"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 3819)
        self.assertEqual(application["new_provenance_events"], 704 + 49 + 24)
        self.assertEqual(application["total_provenance_events"], 4596)
        self.assertEqual(application["expected_total_provenance_events"], 4596)
        self.assertEqual(application["draft_rows"], 34)
        self.assertEqual(application["flagged_rows"], 30)
        self.assertEqual(application["processing_flags_populated_rows"], 205)
        self.assertEqual(application["outside_target_mutations"], 0)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 51)
        self.assertEqual(application["content_review_status"], "pending_headgpt_correction_review")

    def test_batch05_ambiguous_rows_are_explicitly_flagged(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        for sentno in (258, 259, 266, 267, 268, 270, 271, 273, 274, 276, 279, 282, 283, 284, 286, 291, 294, 303, 304, 306, 307, 309, 311, 312, 313, 314, 315, 318, 319):
            self.assertEqual(rows[sentno]["enrichment_state"], "flagged")
            self.assertTrue(
                "source_ambiguity" in rows[sentno]["processing_flags"]
                or "source_corruption" in rows[sentno]["processing_flags"]
            )
        self.assertIn("unclear", rows[273]["english"])
        self.assertIn("source_ambiguity", rows[319]["processing_flags"])

    def test_headgpt_p1_corrections_are_applied(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("Algerians do not know Slim Agha", rows[273]["english"])
        self.assertIn("알제리 사람들은 살림 아가를 모른다", rows[273]["korean"])
        self.assertEqual(rows[294]["enrichment_state"], "flagged")
        self.assertIn("source_ambiguity", rows[294]["processing_flags"])
        self.assertIn("slang", rows[294]["register"])
        self.assertIn("What?", rows[303]["english"])
        self.assertEqual(rows[303]["latin"].split()[0], "choula")
        self.assertIn("does not fawn over women", rows[309]["english"])
        self.assertNotIn("drink milk", rows[309]["english"])
        self.assertIn("please", rows[315]["english"].lower())
        self.assertNotIn("uncle", rows[315]["english"].lower())
        self.assertNotIn("삼촌", rows[315]["korean"])

    def test_batch05_correction_evidence_passes(self):
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-005-CORRECTION-01")
        self.assertEqual(correction["corrected_rows"], ["273", "294", "303", "309", "315"])
        self.assertEqual(correction["changed_fields"], 24)
        self.assertEqual(correction["new_provenance_events"], 24)
        self.assertEqual(correction["provenance_events_before"], 4572)
        self.assertEqual(correction["provenance_events_after"], 4596)
        self.assertEqual(correction["draft_rows"], 34)
        self.assertEqual(correction["flagged_rows"], 30)
        self.assertEqual(correction["processing_flags_populated_rows"], 51)
        self.assertEqual(correction["validator"], "PASS")

    def test_full_validator_passes_after_batch05(self):
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
