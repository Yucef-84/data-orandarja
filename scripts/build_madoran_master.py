"""Build the immutable MADOran master source and morphology projections."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = ROOT / "sources" / "madoran_v2" / "Morphologically Annotated Orani-Arbaic Dialect Dat"
SENTENCES = UPSTREAM_ROOT / "Raw Data - Sentences" / "MADOran_Sentences.tsv"
MORPHOLOGY = UPSTREAM_ROOT / "MADOran Morphologically Annotated Dataset" / "MADOran.tsv"
SOURCE_OUT = ROOT / "data" / "master" / "source" / "madoran_sentences.tsv"
MORPHOLOGY_OUT = ROOT / "data" / "master" / "morphology" / "madoran_tokens.tsv"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_master_qa.json"
PROVENANCE_OUT = ROOT / "data" / "master" / "provenance_manifest.json"

SOURCE_FIELDS = ["Sentno", "Sentence", "WordCount"]
MORPHOLOGY_FIELDS = [
    "ID", "Sentno", "Wordno", "Word", "diac", "msa", "Proclitic",
    "Stem", "Enclitic", "Root", "Pattern", "num", "gen", "Sentiment",
    "en_gloss", "fr_gloss",
]
MASTER_SOURCE_FIELDS = [
    "source_uid", "source_id", "source_locator", "sentno", "arabic_original",
    "word_count", "source_file", "license_id", "source_status",
    "darija_provenance", "enrichment_state",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_strict_rows(path: Path) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    rows: list[dict[str, str]] = []
    malformed: list[dict[str, object]] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        if header != MORPHOLOGY_FIELDS:
            raise ValueError(f"morphology header mismatch: {header}")
        for line_number, values in enumerate(reader, 2):
            if len(values) != len(MORPHOLOGY_FIELDS):
                malformed.append(
                    {
                        "line": line_number,
                        "field_count": len(values),
                        "id": values[0] if values else "",
                        "prefix": values[:5],
                    }
                )
                continue
            rows.append(dict(zip(MORPHOLOGY_FIELDS, values)))
    return rows, malformed


def build_source(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if list(rows[0]) != SOURCE_FIELDS:
        raise ValueError("source header mismatch")
    expected = list(range(1, 1357))
    sentnos = [int(row["Sentno"]) for row in rows]
    if sentnos != expected:
        raise ValueError("source Sentno must be exactly 1..1356")
    output: list[dict[str, str]] = []
    for row in rows:
        sentno = int(row["Sentno"])
        output.append(
            {
                "source_uid": f"madoran-s6-sentno-{sentno:04d}",
                "source_id": "S6",
                "source_locator": f"MADOran_Sentences.tsv#Sentno={sentno}",
                "sentno": str(sentno),
                "arabic_original": row["Sentence"],
                "word_count": row["WordCount"],
                "source_file": "MADOran_Sentences.tsv",
                "license_id": "CC-BY-NC-3.0-MADORAN",
                "source_status": "canonical",
                "darija_provenance": "source_exact",
                "enrichment_state": "not_started",
            }
        )
    return output


def source_positions(source_rows: list[dict[str, str]]) -> set[tuple[int, int]]:
    return {
        (int(row["Sentno"]), wordno)
        for row in source_rows
        for wordno in range(1, int(row["WordCount"]) + 1)
    }


def morphology_qa(
    source_rows: list[dict[str, str]],
    morphology_rows: list[dict[str, str]],
    malformed_rows: list[dict[str, object]],
) -> dict[str, object]:
    source_sentnos = {int(row["Sentno"]) for row in source_rows}
    source_positions_set = source_positions(source_rows)
    valid_rows = [
        row for row in morphology_rows
        if row["Sentno"].strip().isdigit()
        and int(row["Sentno"]) > 0
        and row["Wordno"].strip().isdigit()
    ]
    actual_positions = {(int(row["Sentno"]), int(row["Wordno"])) for row in valid_rows}
    orphan_rows = [
        row for row in morphology_rows
        if not row["Sentno"].strip().isdigit() or int(row["Sentno"] or 0) not in source_sentnos
    ]
    missing_positions = sorted(source_positions_set - actual_positions)
    extra_positions = sorted(actual_positions - source_positions_set)
    wordcount_mismatches = []
    wordno_errors = []
    rows_by_sentno: dict[int, list[dict[str, str]]] = {}
    for row in valid_rows:
        rows_by_sentno.setdefault(int(row["Sentno"]), []).append(row)
    for source in source_rows:
        sentno = int(source["Sentno"])
        expected_wordnos = list(range(1, int(source["WordCount"]) + 1))
        observed = [int(row["Wordno"]) for row in rows_by_sentno.get(sentno, [])]
        if len(observed) != int(source["WordCount"]):
            wordcount_mismatches.append(
                {"sentno": sentno, "expected": int(source["WordCount"]), "actual": len(observed)}
            )
        if observed != expected_wordnos:
            wordno_errors.append({"sentno": sentno, "expected": expected_wordnos, "actual": observed})

    ids = [row["ID"] for row in morphology_rows if row["ID"].strip()]
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    duplicate_texts = sorted(
        {key for key, count in Counter(row["Sentence"] for row in source_rows).items() if count > 1}
    )
    unlinked_sources = sorted(
        sentno for sentno in source_sentnos if sentno not in rows_by_sentno
    )
    return {
        "raw_rows": len(morphology_rows) + len(malformed_rows),
        "morphology_rows": len(morphology_rows),
        "expected_morphology_rows": sum(int(row["WordCount"]) for row in source_rows),
        "malformed_rows": malformed_rows,
        "orphan_tokens": len(orphan_rows),
        "orphan_token_rows": orphan_rows,
        "unlinked_sources": unlinked_sources,
        "wordcount_mismatches": wordcount_mismatches,
        "wordno_errors": wordno_errors,
        "missing_positions": missing_positions,
        "extra_positions": extra_positions,
        "duplicate_morphology_ids": duplicate_ids,
        "duplicate_texts_reported": duplicate_texts,
        "result": "PASS" if (
            len(morphology_rows) == sum(int(row["WordCount"]) for row in source_rows)
            and not malformed_rows
            and not orphan_rows
            and not unlinked_sources
            and not wordcount_mismatches
            and not wordno_errors
            and not duplicate_ids
        ) else "FAIL",
    }


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerows(rows)


def make_qa(
    upstream_source_rows: list[dict[str, str]],
    expected_source_rows: list[dict[str, str]],
    actual_source_rows: list[dict[str, str]],
    expected_morphology_rows: list[dict[str, str]],
    actual_morphology_rows: list[dict[str, str]],
    malformed_rows: list[dict[str, object]],
) -> dict[str, object]:
    source_mutations = 0 if actual_source_rows == expected_source_rows else 1
    morphology_mutations = 0 if actual_morphology_rows == expected_morphology_rows else 1
    source_sentnos = [row.get("sentno", "") for row in actual_source_rows]
    source_qa = {
        "rows": len(actual_source_rows),
        "expected_rows": 1356,
        "sentno_complete": source_sentnos == [str(i) for i in range(1, 1357)],
        "word_count_sum": sum(int(row["word_count"]) for row in actual_source_rows if row.get("word_count", "").isdigit()),
        "source_file_word_count_sum": sum(int(row["WordCount"]) for row in upstream_source_rows),
        "source_mutations": source_mutations,
        "result": "PASS" if (
            len(actual_source_rows) == 1356
            and source_sentnos == [str(i) for i in range(1, 1357)]
            and source_mutations == 0
        ) else "FAIL",
    }
    morphology = morphology_qa(upstream_source_rows, actual_morphology_rows, malformed_rows)
    morphology["morphology_mutations"] = morphology_mutations
    if morphology_mutations:
        morphology["result"] = "FAIL"
    return {
        "source": source_qa,
        "morphology": morphology,
        "source_rows": len(actual_source_rows),
        "morphology_rows": len(actual_morphology_rows),
        "missing_sentnos": [] if source_qa["sentno_complete"] else source_sentnos,
        "duplicate_sentnos": [
            key for key, count in Counter(source_sentnos).items() if count > 1
        ],
        "duplicate_source_uids": len(
            actual_source_rows
        ) - len({row.get("source_uid", "") for row in actual_source_rows}),
        "duplicate_locators": len(
            actual_source_rows
        ) - len({row.get("source_locator", "") for row in actual_source_rows}),
        "duplicate_texts_reported": morphology["duplicate_texts_reported"],
        "orphan_tokens": morphology["orphan_tokens"],
        "unlinked_sources": morphology["unlinked_sources"],
        "wordcount_mismatches": morphology["wordcount_mismatches"],
        "wordno_errors": morphology["wordno_errors"],
        "source_mutations": source_mutations,
        "morphology_mutations": morphology_mutations,
        "master_source_qa": source_qa["result"],
        "master_morphology_qa": morphology["result"],
        "result": "PASS" if source_qa["result"] == "PASS" and morphology["result"] == "PASS" else "FAIL",
    }


def build() -> dict[str, object]:
    source_rows = read_rows(SENTENCES)
    morphology_rows, malformed_rows = read_strict_rows(MORPHOLOGY)
    master_source = build_source(source_rows)
    write_tsv(SOURCE_OUT, MASTER_SOURCE_FIELDS, master_source)
    write_tsv(MORPHOLOGY_OUT, MORPHOLOGY_FIELDS, morphology_rows)
    actual_source_rows = read_rows(SOURCE_OUT)
    actual_morphology_rows = read_rows(MORPHOLOGY_OUT)
    qa = make_qa(
        source_rows,
        master_source,
        actual_source_rows,
        morphology_rows,
        actual_morphology_rows,
        malformed_rows,
    )
    QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance = {
        "manifest_version": "1.0.0",
        "dataset": "MADOran",
        "doi": "10.17632/pgr766jbhp.2",
        "license_id": "CC-BY-NC-3.0-MADORAN",
        "upstream_snapshot": {
            "sentences": {"path": str(SENTENCES.relative_to(ROOT)), "sha256": sha256(SENTENCES)},
            "morphology": {"path": str(MORPHOLOGY.relative_to(ROOT)), "sha256": sha256(MORPHOLOGY)},
        },
        "outputs": {
            "source": str(SOURCE_OUT.relative_to(ROOT)),
            "morphology": str(MORPHOLOGY_OUT.relative_to(ROOT)),
            "qa": str(QA_OUT.relative_to(ROOT)),
        },
        "builder": "scripts/build_madoran_master.py",
        "qa_result": qa["result"],
    }
    PROVENANCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE_OUT.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = build()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["result"] == "PASS" else 1)
