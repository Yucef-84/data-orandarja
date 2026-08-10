"""Reconcile the four official MADOran morphology representations.

This is a read-only comparison. It never repairs, renumbers, or synthesizes
morphology rows. A consistent but incomplete family of files is reported as
an upstream defect so the master morphology gate remains blocked.
"""

from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path

try:
    from scripts.build_madoran_master import (
        MORPHOLOGY,
        MORPHOLOGY_CSV,
        MORPHOLOGY_DB,
        MORPHOLOGY_FIELDS,
        MORPHOLOGY_JSON,
        SENTENCES,
        read_rows,
    )
except ModuleNotFoundError:
    from build_madoran_master import (  # type: ignore
        MORPHOLOGY,
        MORPHOLOGY_CSV,
        MORPHOLOGY_DB,
        MORPHOLOGY_FIELDS,
        MORPHOLOGY_JSON,
        SENTENCES,
        read_rows,
    )


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "master" / "qa" / "madoran_format_reconciliation.json"


def cell(value: object) -> str:
    return "" if value is None else str(value)


def read_delimited(path: Path, delimiter: str) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    rows: list[dict[str, str]] = []
    malformed: list[dict[str, object]] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        header = next(reader)
        if header != MORPHOLOGY_FIELDS:
            raise ValueError(f"{path.name} header mismatch: {header}")
        for line_number, values in enumerate(reader, 2):
            if len(values) != len(MORPHOLOGY_FIELDS):
                malformed.append({"line": line_number, "field_count": len(values)})
                continue
            rows.append(dict(zip(MORPHOLOGY_FIELDS, values)))
    return rows, malformed


def read_json(path: Path) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        raise ValueError("MADOran.json must contain an array")
    rows: list[dict[str, str]] = []
    malformed: list[dict[str, object]] = []
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict) or any(field not in item for field in MORPHOLOGY_FIELDS):
            malformed.append({"row": index, "reason": "missing field or non-object"})
            continue
        rows.append({field: cell(item[field]) for field in MORPHOLOGY_FIELDS})
    return rows, malformed


def read_sqlite(path: Path) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    connection = sqlite3.connect(path)
    try:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(MADOran)")]
        if columns != MORPHOLOGY_FIELDS:
            raise ValueError(f"MADOran.db schema mismatch: {columns}")
        rows = [
            {field: cell(value) for field, value in zip(MORPHOLOGY_FIELDS, values)}
            for values in connection.execute(
                'SELECT "ID", "Sentno", "Wordno", "Word", "diac", "msa", '
                '"Proclitic", "Stem", "Enclitic", "Root", "Pattern", "num", '
                '"gen", "Sentiment", "en_gloss", "fr_gloss" FROM MADOran ORDER BY rowid'
            )
        ]
    finally:
        connection.close()
    return rows, []


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["ID"], row["Sentno"], row["Wordno"]


def index_rows(rows: list[dict[str, str]]) -> tuple[dict[tuple[str, str, str], dict[str, str]], list[tuple[str, str, str]]]:
    indexed: dict[tuple[str, str, str], dict[str, str]] = {}
    duplicates: list[tuple[str, str, str]] = []
    for row in rows:
        row_key = key(row)
        if row_key in indexed:
            duplicates.append(row_key)
        indexed[row_key] = row
    return indexed, sorted(set(duplicates))


def compare_rows(base: list[dict[str, str]], other: list[dict[str, str]]) -> dict[str, object]:
    base_index, base_duplicates = index_rows(base)
    other_index, other_duplicates = index_rows(other)
    missing = sorted(set(base_index) - set(other_index))
    extra = sorted(set(other_index) - set(base_index))
    differences: list[dict[str, object]] = []
    for row_key in sorted(set(base_index) & set(other_index)):
        fields = [
            field
            for field in MORPHOLOGY_FIELDS
            if base_index[row_key][field] != other_index[row_key][field]
        ]
        if fields:
            differences.append({"key": row_key, "fields": fields})
    equal = not missing and not extra and not differences and not base_duplicates and not other_duplicates
    return {
        "equal": equal,
        "base_rows": len(base),
        "other_rows": len(other),
        "missing_keys": missing[:100],
        "extra_keys": extra[:100],
        "field_differences": differences[:100],
        "field_difference_count": len(differences),
        "base_duplicate_keys": base_duplicates[:100],
        "other_duplicate_keys": other_duplicates[:100],
    }


def positions(rows: list[dict[str, str]], source_sentnos: set[int]) -> tuple[set[tuple[int, int]], int]:
    valid: set[tuple[int, int]] = set()
    orphan = 0
    for row in rows:
        if not row["Sentno"].isdigit() or not row["Wordno"].isdigit():
            orphan += 1
            continue
        sentno, wordno = int(row["Sentno"]), int(row["Wordno"])
        if sentno not in source_sentnos or sentno <= 0 or wordno <= 0:
            orphan += 1
            continue
        valid.add((sentno, wordno))
    return valid, orphan


def reconcile() -> dict[str, object]:
    source_rows = read_rows(SENTENCES)
    source_sentnos = {int(row["Sentno"]) for row in source_rows}
    expected_positions = {
        (int(row["Sentno"]), wordno)
        for row in source_rows
        for wordno in range(1, int(row["WordCount"]) + 1)
    }
    loaders = {
        "tsv": lambda: read_delimited(MORPHOLOGY, "\t"),
        "csv": lambda: read_delimited(MORPHOLOGY_CSV, ","),
        "json": lambda: read_json(MORPHOLOGY_JSON),
        "sqlite": lambda: read_sqlite(MORPHOLOGY_DB),
    }
    loaded = {name: loader() for name, loader in loaders.items()}
    rows = {name: value[0] for name, value in loaded.items()}
    malformed = {name: value[1] for name, value in loaded.items()}
    tsv_rows = rows["tsv"]
    comparisons = {
        name: compare_rows(tsv_rows, rows[name])
        for name in ("csv", "json", "sqlite")
    }
    format_positions = {}
    for name, format_rows in rows.items():
        observed, orphan = positions(format_rows, source_sentnos)
        format_positions[name] = {
            "rows": len(format_rows),
            "orphan_rows": orphan,
            "valid_positions": len(observed),
            "missing_positions": sorted(expected_positions - observed)[:100],
            "extra_positions": sorted(observed - expected_positions)[:100],
            "expected_positions": len(expected_positions),
        }
    all_equal = not malformed["tsv"] and all(item["equal"] for item in comparisons.values())
    tsv_observed, _ = positions(tsv_rows, source_sentnos)
    if all_equal and tsv_observed == expected_positions:
        reconciliation_result = "CONSISTENT_COMPLETE"
    elif all_equal:
        reconciliation_result = "UPSTREAM_DEFECT_CONFIRMED"
    else:
        reconciliation_result = "FORMAT_CONFLICT_REQUIRES_REVIEW"
    report = {
        "dataset": "MADOran",
        "comparison_basis": "all 16 morphology fields keyed by (ID, Sentno, Wordno); null and empty cells are equivalent",
        "source_rows": len(source_rows),
        "expected_morphology_positions": len(expected_positions),
        "malformed_rows": malformed,
        "format_positions": format_positions,
        "comparisons_to_tsv": comparisons,
        "cross_format_consistency": "PASS" if all_equal else "FAIL",
        "reconciliation_result": reconciliation_result,
        "derived_reconciled_layer_created": False,
        "master_morphology_gate": "PASS" if reconciliation_result == "CONSISTENT_COMPLETE" else "BLOCKED",
        "result": "PASS" if all_equal else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = reconcile()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["result"] == "PASS" else 1)
