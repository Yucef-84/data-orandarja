import json
import subprocess
import sys
import unittest

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch21 import (
    BATCH_ID, BATCH_OUT, BASE_COMMIT, MANIFEST_OUT, PROMPT_VERSION, TARGET_END, TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import EMPTY_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT, check_provenance_events, read_tsv
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BATCH_FIELDS = engine.BATCH_FIELDS
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
GENERATION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_generation_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction01_qa.json"
CORRECTION02_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction02_qa.json"
CORRECTION03_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction03_qa.json"
CORRECTION04_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction04_qa.json"
CORRECTION05_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction05_qa.json"
CORRECTION06_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction06_qa.json"
CORRECTION07_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction07_qa.json"


def validate_batch_rows(source_rows, batch_rows):
    old_start, old_end = engine.TARGET_START, engine.TARGET_END
    engine.TARGET_START, engine.TARGET_END = TARGET_START, TARGET_END
    try:
        return engine.validate_batch_rows(source_rows, batch_rows)
    finally:
        engine.TARGET_START, engine.TARGET_END = old_start, old_end


class MadoranEnrichmentBatch21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_rows = read_tsv(SOURCE_OUT)
        cls.batch_rows = read_tsv(BATCH_OUT)
        cls.enrichment_rows = read_tsv(ENRICHMENT_OUT)
        cls.event_text = EVENTS_OUT.read_text(encoding="utf-8")

    def test_batch21_header_and_range(self):
        self.assertEqual(list(self.batch_rows[0]), BATCH_FIELDS)
        self.assertEqual([row["sentno"] for row in self.batch_rows], [str(i) for i in range(TARGET_START, TARGET_END + 1)])

    def test_batch21_source_only_validation_passes(self):
        report = validate_batch_rows(self.source_rows, self.batch_rows)
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["target_rows"], 64)
        self.assertEqual(report["required_linguistic_fields"], 64 * len(EMPTY_FIELDS))
        self.assertEqual(report["processing_flags_populated_rows"], 63)

    def test_batch21_state_distribution_and_ascii(self):
        target = [row for row in self.enrichment_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
        self.assertEqual(len(target), 64)
        self.assertEqual(sum(row["enrichment_state"] == "draft" for row in target), 5)
        self.assertEqual(sum(row["enrichment_state"] == "flagged" for row in target), 59)
        self.assertTrue(all(row["latin"].isascii() for row in target))
        self.assertEqual(sum(bool(row["processing_flags"]) for row in target), 63)
        self.assertEqual(sum(bool(row[field]) for row in target for field in EMPTY_FIELDS), 64 * len(EMPTY_FIELDS))

    def test_batch21_manifest_contract(self):
        manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        self.assertEqual(manifest["batch_id"], BATCH_ID)
        self.assertEqual(manifest["base_commit"], BASE_COMMIT)
        self.assertEqual(manifest["sentno_start"], TARGET_START)
        self.assertEqual(manifest["sentno_end"], TARGET_END)
        self.assertEqual(manifest["row_count"], 64)
        self.assertEqual(manifest["prompt_version"], PROMPT_VERSION)
        self.assertFalse(manifest["morphology_dependency"])
        self.assertFalse(manifest["darija_modified"])

    def test_batch21_provenance_and_latest_hash_gate_pass(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        event_check = check_provenance_events(self.event_text, source_uids)
        self.assertEqual(event_check["result"], "PASS", event_check)
        self.assertEqual(event_check["events"], 19182)
        trace = check_enrichment_provenance(self.enrichment_rows, self.event_text)
        self.assertEqual(trace["result"], "PASS", trace)
        self.assertEqual(trace["populated_fields"], 16050)

    def test_batch21_generation_and_application_qa_pass(self):
        generation = json.loads(GENERATION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(generation["result"], "PASS")
        self.assertEqual(generation["target_rows"], 64)
        self.assertEqual(generation["draft_rows"], 0)
        self.assertEqual(generation["flagged_rows"], 64)
        self.assertEqual(generation["processing_flags_populated_rows"], 64)
        self.assertEqual(generation["arabic_modified"], 0)
        application = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(application["result"], "PASS")
        self.assertEqual(application["provenance_events_before"], 17812)
        self.assertEqual(application["new_provenance_events"], 1226)
        self.assertEqual(application["total_provenance_events"], 19038)
        self.assertEqual(application["expected_total_provenance_events"], 19038)
        self.assertEqual(application["processing_flags_populated_rows"], 1122)
        self.assertEqual(application["batch_processing_flags_populated_rows"], 63)
        self.assertEqual(application["correction_state_updates"], 0)
        self.assertEqual(application["content_review_status"], "pending_headgpt_correction_review")

    def test_batch21_correction_qa_and_source_close_fields(self):
        correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-01")
        self.assertEqual(correction["provenance_events_after"], 18699)
        self.assertEqual(correction["state_updates"], 2)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn(by_sentno[1281]["latin"], by_sentno[1281]["english"])
        self.assertIn(by_sentno[1291]["latin"], by_sentno[1291]["korean"])
        self.assertEqual(by_sentno[1312]["register"], "offensive")
        self.assertEqual(by_sentno[1283]["enrichment_state"], "draft")
        self.assertEqual(by_sentno[1283]["processing_flags"], "")
        self.assertEqual(by_sentno[1327]["enrichment_state"], "draft")
        self.assertIn("cefr_boundary", by_sentno[1344]["processing_flags"].split("|"))

    def test_batch21_correction02_qa_and_directional_repairs(self):
        correction = json.loads(CORRECTION02_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-02")
        self.assertEqual(correction["provenance_events_after"], 18776)
        self.assertEqual(correction["state_updates"], 5)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("3nd jij", by_sentno[1292]["english"])
        self.assertIn("shhada", by_sentno[1325]["english"])

    def test_batch21_correction05_qa_and_direct_translation_repair(self):
        correction = json.loads(CORRECTION05_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-05")
        self.assertEqual(correction["provenance_events_after"], 18926)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("I cannot hear your voices", by_sentno[1291]["english"])
        self.assertIn("at least", by_sentno[1293]["english"])
        self.assertIn("the worms", by_sentno[1321]["english"])
        self.assertIn("the bathroom/toilet", by_sentno[1341]["english"])
        self.assertIn("tb3h", by_sentno[1330]["english"])
        self.assertEqual(by_sentno[1307]["enrichment_state"], "draft")
        self.assertEqual(by_sentno[1318]["enrichment_state"], "draft")

    def test_batch21_correction03_canonical_flag_order(self):
        correction = json.loads(CORRECTION03_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["provenance_events_after"], 18777)
        row = next(row for row in self.batch_rows if row["sentno"] == "1293")
        flags = row["processing_flags"].split("|")
        self.assertEqual(flags, sorted(flags))

    def test_batch21_correction04_qa_and_state_repair(self):
        correction = json.loads(CORRECTION04_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-04")
        self.assertEqual(correction["provenance_events_after"], 18852)
        self.assertEqual(correction["state_updates"], 1)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertEqual(by_sentno[1330]["enrichment_state"], "flagged")
        self.assertIn("hwdwli barswl", by_sentno[1281]["english"])
        self.assertIn("shhada", by_sentno[1325]["english"])

    def test_batch21_correction06_qa_and_direct_repairs(self):
        correction = json.loads(CORRECTION06_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-06")
        self.assertEqual(correction["changed_fields"], 78)
        self.assertEqual(correction["state_updates"], 1)
        self.assertEqual(correction["provenance_events_before"], 18926)
        self.assertEqual(correction["provenance_events_after"], 19004)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("you are holding me back", by_sentno[1282]["english"])
        self.assertIn("the heat is killing me", by_sentno[1282]["english"])
        self.assertIn("the worms", by_sentno[1321]["english"])
        self.assertIn("the bathroom/toilet", by_sentno[1341]["english"])
        self.assertEqual(by_sentno[1326]["enrichment_state"], "flagged")
        self.assertIn("context_heavy", by_sentno[1326]["processing_flags"])

    def test_batch21_correction07_qa_and_remaining_direct_repairs(self):
        correction = json.loads(CORRECTION07_QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(correction["result"], "PASS")
        self.assertEqual(correction["correction_id"], "MADORAN-ENRICH-021-CORRECTION-07")
        self.assertEqual(correction["changed_fields"], 34)
        self.assertEqual(correction["state_updates"], 0)
        self.assertEqual(correction["provenance_events_before"], 19004)
        self.assertEqual(correction["provenance_events_after"], 19038)
        by_sentno = {int(row["sentno"]): row for row in self.enrichment_rows}
        self.assertIn("worn out/exhausted because of you", by_sentno[1291]["english"])
        self.assertIn("Harki/traitor", by_sentno[1292]["english"])
        self.assertIn("divorced like them", by_sentno[1293]["english"])
        self.assertIn("what I wanted to tell you", by_sentno[1306]["english"])
        self.assertIn("I said I will not work", by_sentno[1313]["english"])
        self.assertIn("this is your mother", by_sentno[1316]["english"])
        self.assertIn("who do you think you are, turtle", by_sentno[1317]["english"])
        self.assertIn("3nddha", by_sentno[1318]["english"])
        self.assertIn("pay me by the square metre", by_sentno[1320]["english"])
        self.assertIn("involved/getting into it with him", by_sentno[1321]["english"])
        self.assertIn("gold-adorned", by_sentno[1324]["english"])
        self.assertIn("made them anxious/obsessed", by_sentno[1325]["english"])
        self.assertIn("a whole year to come out", by_sentno[1333]["english"])
        self.assertIn("fainted or passed out", by_sentno[1336]["english"])
        self.assertIn("darna fi al3rdat", by_sentno[1339]["english"])
        self.assertIn("perform istinja", by_sentno[1341]["english"])
        self.assertIn("get to the stadium", by_sentno[1344]["english"])

    def test_full_validator_passes_after_batch21_application(self):
        result = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
