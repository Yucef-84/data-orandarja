import csv
import json
import unittest
from pathlib import Path

from scripts.build_madoran_master import (
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
)


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


if __name__ == "__main__":
    unittest.main()
