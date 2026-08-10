import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.build_madoran_enrichment_scaffold as scaffold
import scripts.validate_madoran_enrichment as enrichment


ROOT = Path(__file__).resolve().parents[1]


class MadoranEnrichmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_report = scaffold.build()
        cls.validation_report = enrichment.validate()
        cls.source_rows = scaffold.read_tsv(scaffold.SOURCE_OUT)
        cls.enrichment_rows = scaffold.read_tsv(scaffold.ENRICHMENT_OUT)

    def test_scaffold_passes_validation(self):
        self.assertEqual(self.build_report["result"], "PASS")
        self.assertEqual(self.validation_report["result"], "PASS")

    def test_scaffold_has_1356_rows_and_exact_header(self):
        self.assertEqual(len(self.enrichment_rows), 1356)
        self.assertEqual(list(self.enrichment_rows[0]), scaffold.ENRICHMENT_FIELDS)

    def test_source_uid_is_unique_and_complete(self):
        source_uids = {row["source_uid"] for row in self.source_rows}
        enrichment_uids = {row["source_uid"] for row in self.enrichment_rows}
        self.assertEqual(len(source_uids), 1356)
        self.assertEqual(enrichment_uids, source_uids)

    def test_sentno_is_exactly_1_through_1356(self):
        self.assertEqual(
            [row["sentno"] for row in self.enrichment_rows],
            [str(number) for number in range(1, 1357)],
        )

    def test_source_link_completeness_is_checked(self):
        mutated = [dict(row) for row in self.enrichment_rows]
        mutated[0]["source_uid"] = "unknown-source-uid"
        report = enrichment.check_enrichment_rows(self.source_rows, mutated)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("unknown_source_uid", report["failures"])

    def test_missing_source_uid_is_rejected(self):
        mutated = [dict(row) for row in self.enrichment_rows[1:]]
        report = enrichment.check_enrichment_rows(self.source_rows, mutated)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("missing_source_uid", report["failures"])

    def test_duplicate_source_uid_is_rejected(self):
        mutated = [dict(row) for row in self.enrichment_rows]
        mutated[1]["source_uid"] = mutated[0]["source_uid"]
        report = enrichment.check_enrichment_rows(self.source_rows, mutated)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("duplicate_source_uid", report["failures"])

    def test_non_empty_initial_field_is_rejected(self):
        mutated = [dict(row) for row in self.enrichment_rows]
        mutated[192]["latin"] = "should not be populated in scaffold"
        report = enrichment.check_enrichment_rows(self.source_rows, mutated)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("non_empty_initial_linguistic_field", report["failures"])

    def test_headgpt_approved_state_is_frozen(self):
        self.assertTrue(
            all(
                row["enrichment_state"] == "qa_passed"
                for row in self.enrichment_rows[:64]
                if row["sentno"] not in {"17", "63"}
            )
        )
        self.assertEqual(self.enrichment_rows[16]["enrichment_state"], "flagged")
        self.assertEqual(self.enrichment_rows[62]["enrichment_state"], "flagged")
        self.assertTrue(
            all(row["enrichment_state"] == "not_started" for row in self.enrichment_rows[192:])
        )

    def test_processing_flags_are_source_metadata_not_workflow_state(self):
        self.assertIn("processing_flags", scaffold.ENRICHMENT_FIELDS)
        self.assertEqual(self.enrichment_rows[16]["processing_flags"], "source_ambiguity")
        self.assertEqual(self.enrichment_rows[62]["processing_flags"], "source_corruption")
        self.assertEqual(sum(bool(row["processing_flags"]) for row in self.enrichment_rows), 92)
        self.assertEqual(self.enrichment_rows[16]["enrichment_state"], "flagged")
        self.assertEqual(self.enrichment_rows[62]["enrichment_state"], "flagged")

    def test_layer_contract_separates_source_sentences_and_learning_units(self):
        contract = json.loads(
            (ROOT / "data" / "master" / "schema" / "madoran_layer_contract.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(enrichment.check_layer_contract()["result"], "PASS")
        self.assertEqual(contract["source_sentence_annotation"]["status"], "ACTIVE")
        self.assertEqual(contract["learning_unit"]["status"], "NOT_STARTED")
        self.assertTrue(contract["learning_unit"]["parent_source_uid_required"])

    def test_source_gate_passes_without_morphology_access(self):
        report = scaffold.source_gate()
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["live_source"]["result"], "PASS")
        self.assertEqual(report["pinned_source"]["result"], "PASS")

    def test_live_source_projection_rejects_arabic_mutation(self):
        upstream_rows = scaffold.read_tsv(scaffold.UPSTREAM_SENTENCES)
        actual_rows = scaffold.read_tsv(scaffold.SOURCE_OUT)
        actual_rows[0]["arabic_original"] += " MUTATED"
        report = scaffold.check_source_projection(upstream_rows, actual_rows)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("source_projection_mismatch", report["failures"])

    def test_source_gate_rejects_mutated_tracked_source(self):
        source_rows = scaffold.read_tsv(scaffold.SOURCE_OUT)
        source_rows[0]["arabic_original"] += " MUTATED"
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            mutated_path = Path(directory) / "madoran_sentences.tsv"
            with mutated_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=scaffold.SOURCE_FIELDS,
                    delimiter="\t",
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerows(source_rows)
            with patch.object(scaffold, "SOURCE_OUT", mutated_path):
                report = scaffold.source_gate()
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("live_source_integrity", report["failures"])

    def test_source_gate_rejects_failed_source_qa(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            source_qa = Path(directory) / "source_qa.json"
            source_qa.write_text(
                json.dumps({"source": {"result": "FAIL"}, "source_mutations": 0}),
                encoding="utf-8",
            )
            with patch.object(scaffold, "SOURCE_QA", source_qa):
                report = scaffold.source_gate()
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("master_source_qa_not_pass", report["failures"])

    def test_source_only_enrichment_is_ready_while_morphology_is_blocked(self):
        status = json.loads(
            (ROOT / "data" / "master" / "state" / "madoran_layer_status.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["source_only_enrichment"], "READY")
        self.assertEqual(status["morphology"], "BLOCKED_UPSTREAM_DEFECT")

    def test_morphology_dependent_field_is_rejected_while_blocked(self):
        report = enrichment.check_morphology_dependency(
            {"morphology": "BLOCKED_UPSTREAM_DEFECT"}, ["root_features"]
        )
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("root_features", report["violations"])

    def test_morphology_dependent_field_is_allowed_only_after_pass(self):
        report = enrichment.check_morphology_dependency(
            {"morphology": "PASS"}, ["root_features"]
        )
        self.assertEqual(report["result"], "PASS")

    def test_morphology_issue_remains_unrepaired(self):
        issue = json.loads(
            (ROOT / "data" / "master" / "issues" / "madoran_morphology_upstream_defect.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(issue["status"], "BLOCKED_UPSTREAM_DEFECT")
        self.assertFalse(issue["repaired"])
        self.assertEqual(issue["synthetic_rows_added"], 0)

    def test_provenance_event_required_fields_are_validated(self):
        source_uid = self.source_rows[0]["source_uid"]
        valid_event = {
            "source_uid": source_uid,
            "field": "latin",
            "value_hash": "sha256:example",
            "method": "test",
            "model": "test-model",
            "prompt_version": "test-v1",
            "schema_version": "1.0.0",
            "generated_at": "2026-08-10T00:00:00Z",
            "review_state": "generated",
        }
        valid = enrichment.check_provenance_events(
            json.dumps(valid_event), {source_uid}
        )
        invalid = enrichment.check_provenance_events("{}", {source_uid})
        self.assertEqual(valid["result"], "PASS")
        self.assertEqual(invalid["result"], "FAIL")
        self.assertTrue(any("provenance_required_fields" in item for item in invalid["failures"]))

    def test_scaffold_rebuild_preserves_existing_provenance_events(self):
        source_uid = self.source_rows[0]["source_uid"]
        event = {
            "source_uid": source_uid,
            "field": "latin",
            "value_hash": "sha256:existing",
            "method": "test",
            "model": "test-model",
            "prompt_version": "test-v1",
            "schema_version": "1.0.0",
            "generated_at": "2026-08-10T00:00:00Z",
            "review_state": "generated",
        }
        event_text = json.dumps(event, ensure_ascii=False) + "\n"
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            directory_path = Path(directory)
            events_path = directory_path / "events.jsonl"
            qa_path = directory_path / "qa.json"
            events_path.write_text(event_text, encoding="utf-8")
            with (
                patch.object(scaffold, "EVENTS_OUT", events_path),
                patch.object(scaffold, "QA_OUT", qa_path),
            ):
                report = scaffold.build()
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(events_path.read_text(encoding="utf-8"), event_text)

    def test_scaffold_rebuild_preserves_existing_enrichment_values(self):
        existing_rows = scaffold.scaffold_rows(self.source_rows)
        existing_rows[0]["latin"] = "existing enrichment"
        existing_rows[0]["enrichment_state"] = "draft"
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            directory_path = Path(directory)
            enrichment_path = directory_path / "enrichment.tsv"
            events_path = directory_path / "events.jsonl"
            qa_path = directory_path / "qa.json"
            scaffold.write_tsv(enrichment_path, existing_rows)
            before_bytes = enrichment_path.read_bytes()
            with (
                patch.object(scaffold, "ENRICHMENT_OUT", enrichment_path),
                patch.object(scaffold, "EVENTS_OUT", events_path),
                patch.object(scaffold, "QA_OUT", qa_path),
            ):
                report = scaffold.build()
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["enrichment_output_action"], "preserved")
            self.assertEqual(report["completed_rows"], 1)
            self.assertEqual(enrichment_path.read_bytes(), before_bytes)

    def test_populated_enrichment_row_is_valid_after_scaffold_phase(self):
        populated = [dict(row) for row in self.enrichment_rows]
        populated[0]["latin"] = "future enrichment"
        populated[0]["enrichment_state"] = "draft"
        report = enrichment.check_enrichment_rows(self.source_rows, populated)
        self.assertEqual(report["result"], "PASS")

    def test_populated_field_requires_matching_provenance_hash(self):
        populated = scaffold.scaffold_rows(self.source_rows)
        populated[0]["latin"] = "future enrichment"
        populated[0]["enrichment_state"] = "draft"
        missing = enrichment.check_enrichment_provenance(populated, "")
        value_hash = "sha256:" + hashlib.sha256(
            populated[0]["latin"].encode("utf-8")
        ).hexdigest()
        event = {
            "source_uid": populated[0]["source_uid"],
            "field": "latin",
            "value_hash": value_hash,
            "method": "test",
            "model": "test-model",
            "prompt_version": "test-v1",
            "schema_version": "1.0.0",
            "generated_at": "2026-08-10T00:00:00Z",
            "review_state": "generated",
        }
        traced = enrichment.check_enrichment_provenance(
            populated, json.dumps(event) + "\n"
        )
        self.assertEqual(missing["result"], "FAIL")
        self.assertIn(
            f"missing_provenance_event:{populated[0]['source_uid']}:latin",
            missing["failures"],
        )
        self.assertEqual(traced["result"], "PASS")

    def test_latest_provenance_event_hash_is_authoritative(self):
        populated = scaffold.scaffold_rows(self.source_rows)
        populated[0]["latin"] = "latest value"
        populated[0]["enrichment_state"] = "draft"
        good_hash = "sha256:" + hashlib.sha256(
            populated[0]["latin"].encode("utf-8")
        ).hexdigest()
        base_event = {
            "source_uid": populated[0]["source_uid"],
            "field": "latin",
            "method": "test",
            "model": "test-model",
            "prompt_version": "test-v1",
            "schema_version": "1.0.0",
            "generated_at": "2026-08-10T13:01:00Z",
            "review_state": "generated",
        }
        old_event = {**base_event, "value_hash": good_hash}
        stale_latest_event = {**base_event, "value_hash": "sha256:" + "0" * 64}
        traced = enrichment.check_enrichment_provenance(
            populated,
            json.dumps(old_event) + "\n" + json.dumps(stale_latest_event) + "\n",
        )
        self.assertEqual(traced["result"], "FAIL")
        self.assertTrue(
            any("provenance_value_hash_mismatch" in item for item in traced["failures"])
        )

    def test_schema_declares_morphology_dependency_gate(self):
        schema = json.loads(
            (ROOT / "data" / "master" / "enrichment" / "enrichment_schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(schema["dependency_policy"]["blocked_when_morphology_gate_not_pass"])
        self.assertIn(
            "root_features", schema["dependency_policy"]["morphology_dependent_fields"]
        )

    def test_source_only_builder_contains_no_morphology_input_path(self):
        builder_text = (
            ROOT / "scripts" / "build_madoran_enrichment_scaffold.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "madoran_tokens.tsv",
            "MADOran.tsv",
            "MADOran.csv",
            "MADOran.json",
            "MADOran.db",
        ):
            self.assertNotIn(forbidden, builder_text)

    def test_provenance_event_log_contains_batch_events(self):
        event_text = scaffold.EVENTS_OUT.read_text(encoding="utf-8")
        report = enrichment.check_provenance_events(
            event_text, {row["source_uid"] for row in self.source_rows}
        )
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["events"], 3029)

    def test_processing_flag_provenance_hashes_are_current(self):
        report = enrichment.check_enrichment_provenance(
            self.enrichment_rows,
            scaffold.EVENTS_OUT.read_text(encoding="utf-8"),
        )
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["populated_fields"], 3 * 64 * len(scaffold.EMPTY_FIELDS) + 92)


if __name__ == "__main__":
    unittest.main()
