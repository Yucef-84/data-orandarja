"""Build the source-only MADOran enrichment scaffold.

This module reads only the canonical sentence layer. It deliberately does not
import or read any morphology representation. Linguistic fields stay empty
until a later, provenance-tracked enrichment run.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_OUT = ROOT / "data" / "master" / "source" / "madoran_sentences.tsv"
SOURCE_QA = ROOT / "data" / "master" / "qa" / "madoran_master_qa.json"
PROVENANCE = ROOT / "data" / "master" / "provenance_manifest.json"
ENRICHMENT_OUT = ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment.tsv"
EVENTS_OUT = ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment_provenance.jsonl"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_scaffold_qa.json"

SOURCE_FIELDS = [
    "source_uid",
    "source_id",
    "source_locator",
    "sentno",
    "arabic_original",
    "word_count",
    "source_file",
    "license_id",
    "source_status",
    "darija_provenance",
    "enrichment_state",
]
ENRICHMENT_FIELDS = [
    "source_uid",
    "sentno",
    "latin",
    "english",
    "korean",
    "cefr_level",
    "difficulty_score",
    "domain",
    "topic",
    "genre",
    "speech_act",
    "register",
    "context_dependency",
    "enrichment_state",
]
EMPTY_FIELDS = ENRICHMENT_FIELDS[2:-1]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def source_gate() -> dict[str, object]:
    failures: list[str] = []
    if not SOURCE_QA.exists():
        failures.append("source_qa_missing")
        source_qa: dict[str, object] = {}
    else:
        source_qa = json.loads(SOURCE_QA.read_text(encoding="utf-8"))
    source_report = source_qa.get("source", {})
    if source_report.get("result") != "PASS":
        failures.append("master_source_qa_not_pass")
    if source_qa.get("source_mutations") != 0:
        failures.append("source_mutation_detected")
    if not PROVENANCE.exists():
        failures.append("provenance_manifest_missing")
        manifest: dict[str, object] = {}
    else:
        manifest = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != "1.1.0":
        failures.append("provenance_manifest_version")
    snapshot = manifest.get("upstream_snapshot", {})
    if not snapshot:
        failures.append("upstream_snapshot_missing")
    for key, entry in snapshot.items():
        if "\\" in str(entry.get("path", "")):
            failures.append(f"non_posix_provenance_path:{key}")
        for required in ("size_bytes", "sha256", "git_blob_sha1"):
            if not entry.get(required):
                failures.append(f"provenance_field_missing:{key}:{required}")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_rows": source_report.get("rows", 0),
        "provenance_manifest_version": manifest.get("manifest_version"),
    }


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ENRICHMENT_FIELDS,
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)


def build() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    if len(source_rows) != 1356:
        raise ValueError(f"expected 1356 source rows, got {len(source_rows)}")
    expected_sentnos = [str(index) for index in range(1, 1357)]
    if [row.get("sentno", "") for row in source_rows] != expected_sentnos:
        raise ValueError("canonical source Sentno coverage is not exactly 1..1356")
    rows = [
        {
            "source_uid": row["source_uid"],
            "sentno": row["sentno"],
            **{field: "" for field in EMPTY_FIELDS},
            "enrichment_state": "not_started",
        }
        for row in source_rows
    ]
    write_tsv(ENRICHMENT_OUT, rows)
    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_OUT.write_text("", encoding="utf-8")
    report = {
        "result": "PASS",
        "source_gate": gate,
        "rows": len(rows),
        "completed_rows": 0,
        "enrichment_state": "not_started",
        "morphology_dependency": "not_read",
        "output": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
        "provenance_events": EVENTS_OUT.relative_to(ROOT).as_posix(),
    }
    QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2))
