import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch18 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, PROMPT_VERSION, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_generation_qa.json"


def validate_batch_rows(source_rows, batch_rows):
    previous_start, previous_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START = previous_start
        engine.TARGET_END = previous_end


class MadoranEnrichmentBatch18Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch18_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual(
            [row["sentno"] for row in self.batch_rows],
            [str(i) for i in range(TARGET_START, TARGET_END + 1)],
        )

    def test_batch18_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 48)

    def test_batch18_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 20)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 44)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 48)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch18_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["prompt_version"], PROMPT_VERSION)
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch18_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 15944)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 13615)

    def test_batch18_headgpt_correction_artifact_and_key_fixes(self):
        rows = {row["sentno"]: row for row in self.enrichment_rows}
        self.assertEqual(rows["1097"]["speech_act"], "wish")
        self.assertEqual(rows["1122"]["topic"], "denial_of_parentage")
        self.assertEqual(rows["1122"]["processing_flags"], "")
        self.assertEqual(rows["1125"]["domain"], "sports")
        self.assertEqual(rows["1125"]["topic"], "football_score_question_and_response")
        self.assertEqual(rows["1140"]["processing_flags"], "code_switching")
        self.assertEqual(rows["1149"]["english"], "Abdelkader says, ‘How are you?’ The row does not add a Hawari recipient.")
        correction01 = json.loads((ROOT / "data/master/qa/madoran_enrichment_batch18_correction01_qa.json").read_text(encoding="utf-8"))
        self.assertEqual(correction01["result"], "PASS")
        self.assertEqual(correction01["changed_fields"], 129)
        self.assertEqual(correction01["state_updates"], 4)
        self.assertEqual(correction01["batch_artifact_sync_state_updates"], 4)
        correction02 = json.loads((ROOT / "data/master/qa/madoran_enrichment_batch18_correction02_qa.json").read_text(encoding="utf-8"))
        self.assertEqual(correction02["result"], "PASS")
        self.assertEqual(correction02["changed_fields"], 76)
        self.assertEqual(correction02["state_updates"], 0)
        self.assertEqual(correction02["batch_artifact_sync_state_updates"], 0)
        correction03 = json.loads((ROOT / "data/master/qa/madoran_enrichment_batch18_correction03_qa.json").read_text(encoding="utf-8"))
        self.assertEqual(correction03["result"], "PASS")
        self.assertEqual(correction03["changed_fields"], 10)
        self.assertEqual(correction03["state_updates"], 0)
        self.assertEqual(correction03["batch_artifact_sync_state_updates"], 0)
        correction04 = json.loads((ROOT / "data/master/qa/madoran_enrichment_batch18_correction04_qa.json").read_text(encoding="utf-8"))
        self.assertEqual(correction04["result"], "PASS")
        self.assertEqual(correction04["changed_fields"], 4)
        self.assertEqual(correction04["state_updates"], 0)
        self.assertEqual(correction04["batch_artifact_sync_state_updates"], 0)
        self.assertEqual(rows["1125"]["speech_act"], "question")
        self.assertEqual(rows["1140"]["processing_flags"], "code_switching")
        self.assertIn("120 doro", rows["1126"]["english"])
        self.assertIn("take him", rows["1143"]["english"])
        self.assertIn("If you remain still", rows["1146"]["english"])
        self.assertIn("Last time", rows["1102"]["english"])
        self.assertIn("Some people took me and tied me", rows["1121"]["english"])

    def test_batch18_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 16)
        self.assertEqual(generation["flagged_rows"], 48)
        self.assertEqual(generation["processing_flags_populated_rows"], 48)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 14973)
        self.assertEqual(application["new_provenance_events"], 971)
        self.assertEqual(application["total_provenance_events"], 15944)
        self.assertEqual(application["expected_total_provenance_events"], 15944)
        self.assertEqual(application["processing_flags_populated_rows"], 943)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 48)
        self.assertEqual(application["content_review_status"], "pending_headgpt_correction_review")

    def test_full_validator_passes_after_batch18_application(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
