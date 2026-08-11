import json
import subprocess
import sys
import unittest

from scripts.apply_madoran_enrichment_batch04 import (
    BATCH_FIELDS,
    BATCH_ID,
    BATCH_OUT,
    BATCH_QA_OUT,
    MANIFEST_OUT,
    validate_batch_rows,
)
from scripts.build_madoran_enrichment_batch04 import BASE_COMMIT, TARGET_END, TARGET_START
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


GENERATION_QA_OUT = (
    ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch04_generation_qa.json"
)


class MadoranEnrichmentBatch04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch04_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch04_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 62)

    def test_batch04_state_distribution_and_ascii(self):
        target = [
            row
            for row in self.enrichment_rows
            if TARGET_START <= int(row["sentno"]) <= TARGET_END
        ]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 43)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 21)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 62)
        self.assertEqual(
            sum(bool(row[field]) for row in target for field in EMPTY_FIELDS),
            64 * len(EMPTY_FIELDS),
        )

    def test_batch04_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["fields"], [*EMPTY_FIELDS, "processing_flags", "enrichment_state"])
        self.assertEqual(manifest["prompt_version"], "madoran-source-enrichment-v4")
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch04_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 3802)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 2970)

    def test_batch04_generation_qa_passes(self):
        qa = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["target_rows"], 64)
        self.assertEqual(qa["draft_rows"], 43)
        self.assertEqual(qa["flagged_rows"], 21)
        self.assertEqual(qa["processing_flags_populated_rows"], 62)
        self.assertEqual(qa["arabic_modified"], 0)
        self.assertEqual(qa["morphology_reads"], 0)

    def test_batch04_application_qa_passes(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["provenance_events_before"], 3036)
        self.assertEqual(qa["new_provenance_events"], 704 + 62)
        self.assertEqual(qa["total_provenance_events"], 3802)
        self.assertEqual(qa["expected_total_provenance_events"], 3802)
        self.assertEqual(qa["outside_target_mutations"], 0)
        self.assertEqual(qa["morphology_gate"], "BLOCKED_UPSTREAM_DEFECT")
        self.assertEqual(qa["learning_unit_rows_created"], 0)
        self.assertEqual(qa["latest_event_hash_gate"], "PASS")
        self.assertEqual(qa["content_review_status"], "pending_headgpt")

    def test_ambiguity_and_corruption_are_visible(self):
        rows = {int(row["sentno"]): row for row in self.enrichment_rows}
        for sentno in (194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 205, 206, 207, 208, 209, 210, 211, 212, 213, 215, 236):
            self.assertEqual(rows[sentno]["enrichment_state"], "flagged")
            self.assertTrue(
                "source_ambiguity" in rows[sentno]["processing_flags"]
                or "source_corruption" in rows[sentno]["processing_flags"]
            )
        self.assertIn("corrupted", rows[206]["english"])
        self.assertIn("손상", rows[236]["korean"])

    def test_batch04_does_not_create_morphology_or_learning_units(self):
        qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["morphology_reads"], 0)
        self.assertEqual(qa["learning_unit_rows_created"], 0)
        self.assertEqual(qa["arabic_modified"], 0)

    def test_full_validator_passes_after_batch04(self):
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
