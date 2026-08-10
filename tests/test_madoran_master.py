import csv
import json
import subprocess
import unittest
from pathlib import Path

from scripts.build_madoran_master import (
    current_upstream_snapshot,
    MORPHOLOGY,
    MASTER_SOURCE_FIELDS,
    MORPHOLOGY_FIELDS,
    MORPHOLOGY_OUT,
    QA_OUT,
    SENTENCES,
    SOURCE_OUT,
    build_source,
    build,
    make_qa,
    read_rows,
    read_strict_rows,
    validate_pinned_provenance,
)
from scripts.reconcile_madoran_formats import reconcile


ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class MadoranMasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build()

    def test_source_has_all_canonical_sentnos(self):
        current = rows(SOURCE_OUT)
        self.assertEqual(len(current), 1356)
        self.assertEqual(list(current[0]), MASTER_SOURCE_FIELDS)
        self.assertEqual([int(row["sentno"]) for row in current], list(range(1, 1357)))
        self.assertTrue(all(row["source_status"] == "canonical" for row in current))
        self.assertTrue(all(row["darija_provenance"] == "source_exact" for row in current))

    def test_provenance_is_pinned_with_posix_paths_and_git_blob_hashes(self):
        report = validate_pinned_provenance()
        self.assertEqual(report["result"], "PASS")
        manifest = json.loads(
            (ROOT / "data" / "master" / "provenance_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["upstream_snapshot"], current_upstream_snapshot())
        self.assertTrue(
            all("git_blob_sha1" in entry for entry in manifest["upstream_snapshot"].values())
        )
        self.assertTrue(
            all("\\" not in entry["path"] for entry in manifest["upstream_snapshot"].values())
        )
        for entry in manifest["upstream_snapshot"].values():
            actual = subprocess.run(
                ["git", "rev-parse", f"HEAD:{entry['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(entry["git_blob_sha1"], actual)

    def test_morphology_preserves_upstream_schema(self):
        current = rows(MORPHOLOGY_OUT)
        self.assertEqual(list(current[0]), MORPHOLOGY_FIELDS)
        self.assertEqual(self.report["morphology_rows"], len(current))

    def test_current_upstream_inconsistency_is_explicit(self):
        qa = json.loads(QA_OUT.read_text(encoding="utf-8"))
        self.assertEqual(qa["source_rows"], 1356)
        self.assertEqual(qa["source"]["word_count_sum"], 30919)
        self.assertEqual(qa["master_morphology_qa"], "FAIL")
        self.assertEqual(qa["morphology"]["morphology_rows"], 30915)
        self.assertTrue(qa["morphology"]["orphan_tokens"])
        self.assertTrue(qa["morphology"]["wordcount_mismatches"])
        self.assertTrue(qa["morphology"]["wordno_errors"])

    def test_validator_detects_source_arabic_mutation(self):
        upstream_source = read_rows(SENTENCES)
        expected_source = build_source(upstream_source)
        expected_morphology, malformed = read_strict_rows(MORPHOLOGY)
        actual_source = read_rows(SOURCE_OUT)
        actual_morphology = read_rows(MORPHOLOGY_OUT)
        actual_source[0]["arabic_original"] += " MUTATED"
        report = make_qa(
            upstream_source,
            expected_source,
            actual_source,
            expected_morphology,
            actual_morphology,
            malformed,
        )
        self.assertEqual(report["source_mutations"], 1)
        self.assertEqual(report["result"], "FAIL")

    def test_validator_detects_morphology_mutation(self):
        upstream_source = read_rows(SENTENCES)
        expected_source = build_source(upstream_source)
        expected_morphology, malformed = read_strict_rows(MORPHOLOGY)
        actual_source = read_rows(SOURCE_OUT)
        actual_morphology = read_rows(MORPHOLOGY_OUT)
        actual_morphology[0]["Word"] += " MUTATED"
        report = make_qa(
            upstream_source,
            expected_source,
            actual_source,
            expected_morphology,
            actual_morphology,
            malformed,
        )
        self.assertEqual(report["morphology_mutations"], 1)
        self.assertEqual(report["result"], "FAIL")

    def test_official_morphology_formats_reconcile_without_repair(self):
        report = reconcile()
        self.assertEqual(report["cross_format_consistency"], "PASS")
        self.assertEqual(report["reconciliation_result"], "UPSTREAM_DEFECT_CONFIRMED")
        self.assertFalse(report["derived_reconciled_layer_created"])
        self.assertEqual(report["master_morphology_gate"], "BLOCKED")
        for comparison in report["comparisons_to_tsv"].values():
            self.assertTrue(comparison["equal"])
        for position_report in report["format_positions"].values():
            self.assertEqual(position_report["rows"], 30915)
            self.assertEqual(position_report["orphan_rows"], 5)
            self.assertEqual(position_report["expected_positions"], 30919)


if __name__ == "__main__":
    unittest.main()
