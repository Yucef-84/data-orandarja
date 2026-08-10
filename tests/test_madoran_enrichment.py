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
        mutated[0]["latin"] = "should not be populated in scaffold"
        report = enrichment.check_enrichment_rows(self.source_rows, mutated)
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("non_empty_initial_linguistic_field", report["failures"])

    def test_initial_state_is_not_started(self):
        self.assertTrue(
            all(row["enrichment_state"] == "not_started" for row in self.enrichment_rows)
        )

    def test_source_gate_passes_without_morphology_access(self):
        report = scaffold.source_gate()
        self.assertEqual(report["result"], "PASS")

    def test_source_gate_rejects_failed_source_qa(self):
        with tempfile.TemporaryDirectory() as directory:
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

    def test_provenance_event_log_starts_empty(self):
        self.assertEqual(scaffold.EVENTS_OUT.read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
