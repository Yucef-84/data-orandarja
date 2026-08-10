"""Build the source-only MADOran enrichment scaffold.

This module reads only the canonical sentence layer. It deliberately does not
import or read any morphology representation. Linguistic fields stay empty
until a later, provenance-tracked enrichment run.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_OUT = ROOT / "data" / "master" / "source" / "madoran_sentences.tsv"
SOURCE_QA = ROOT / "data" / "master" / "qa" / "madoran_master_qa.json"
PROVENANCE = ROOT / "data" / "master" / "provenance_manifest.json"
UPSTREAM_SENTENCES = (
    ROOT
    / "sources"
    / "madoran_v2"
    / "Morphologically Annotated Orani-Arbaic Dialect Dat"
    / "Raw Data - Sentences"
    / "MADOran_Sentences.tsv"
)
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
UPSTREAM_SOURCE_FIELDS = ["Sentno", "Sentence", "WordCount"]
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
PROVENANCE_REQUIRED_FIELDS = (
    "source_uid",
    "field",
    "value_hash",
    "method",
    "model",
    "prompt_version",
    "schema_version",
    "generated_at",
    "review_state",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def project_source_rows(upstream_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Build the expected source projection from sentences only."""

    if not upstream_rows or list(upstream_rows[0]) != UPSTREAM_SOURCE_FIELDS:
        raise ValueError("upstream sentence header mismatch")
    expected_sentnos = [str(index) for index in range(1, 1357)]
    if [row.get("Sentno", "") for row in upstream_rows] != expected_sentnos:
        raise ValueError("upstream source Sentno coverage is not exactly 1..1356")
    return [
        {
            "source_uid": f"madoran-s6-sentno-{int(row['Sentno']):04d}",
            "source_id": "S6",
            "source_locator": f"MADOran_Sentences.tsv#Sentno={int(row['Sentno'])}",
            "sentno": row["Sentno"],
            "arabic_original": row["Sentence"],
            "word_count": row["WordCount"],
            "source_file": "MADOran_Sentences.tsv",
            "license_id": "CC-BY-NC-3.0-MADORAN",
            "source_status": "canonical",
            "darija_provenance": "source_exact",
            "enrichment_state": "not_started",
        }
        for row in upstream_rows
    ]


def check_source_projection(
    upstream_rows: list[dict[str, str]], actual_rows: list[dict[str, str]]
) -> dict[str, object]:
    """Compare the tracked canonical source with the live upstream sentences."""

    failures: list[str] = []
    try:
        expected_rows = project_source_rows(upstream_rows)
    except (KeyError, ValueError) as exc:
        expected_rows = []
        failures.append(f"upstream_source_invalid:{exc}")
    if actual_rows != expected_rows:
        failures.append("source_projection_mismatch")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "upstream_rows": len(upstream_rows),
        "actual_rows": len(actual_rows),
    }


def relative_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_pinned_source_snapshot(snapshot: dict[str, object]) -> dict[str, object]:
    """Check the live sentence source against its immutable pinned identity."""

    failures: list[str] = []
    if not snapshot:
        return {
            "result": "FAIL",
            "failures": ["pinned_sentence_snapshot_missing"],
        }
    if not UPSTREAM_SENTENCES.exists():
        return {
            "result": "FAIL",
            "failures": ["pinned_sentence_source_missing"],
        }
    payload = UPSTREAM_SENTENCES.read_bytes().replace(b"\r\n", b"\n")
    if len(payload) != snapshot.get("size_bytes"):
        failures.append("pinned_sentence_size_mismatch")
    if hashlib.sha256(payload).hexdigest() != snapshot.get("sha256"):
        failures.append("pinned_sentence_sha256_mismatch")
    try:
        actual_blob = subprocess.run(
            ["git", "rev-parse", f"HEAD:{relative_posix(UPSTREAM_SENTENCES)}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        actual_blob = ""
        failures.append(f"pinned_sentence_git_blob_unreadable:{exc}")
    if actual_blob != snapshot.get("git_blob_sha1"):
        failures.append("pinned_sentence_git_blob_mismatch")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "git_blob_sha1": actual_blob,
    }


def check_provenance_events(
    event_text: str, source_uids: set[str]
) -> dict[str, object]:
    """Validate append-only provenance events and their required fields."""

    _, failures, event_count = parse_provenance_events(event_text, source_uids)
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "events": event_count,
    }


def parse_provenance_events(
    event_text: str, source_uids: set[str]
) -> tuple[list[dict[str, object]], list[str], int]:
    """Parse events and return objects for field-level provenance tracing."""

    failures: list[str] = []
    events: list[dict[str, object]] = []
    event_count = 0
    for line_number, line in enumerate(event_text.splitlines(), 1):
        if not line.strip():
            continue
        event_count += 1
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"invalid_provenance_event:{line_number}")
            continue
        if not isinstance(event, dict):
            failures.append(f"provenance_event_not_object:{line_number}")
            continue
        events.append(event)
        missing = [
            field
            for field in PROVENANCE_REQUIRED_FIELDS
            if not isinstance(event.get(field), str) or not event[field].strip()
        ]
        if missing:
            failures.append(f"provenance_required_fields:{line_number}:{','.join(missing)}")
        if event.get("source_uid") not in source_uids:
            failures.append(f"provenance_unknown_source_uid:{line_number}")
        if event.get("field") not in ENRICHMENT_FIELDS:
            failures.append(f"provenance_unknown_field:{line_number}")
    return events, failures, event_count


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
    if not UPSTREAM_SENTENCES.exists() or not SOURCE_OUT.exists():
        live_source = {
            "result": "FAIL",
            "failures": ["live_source_file_missing"],
            "upstream_rows": 0,
            "actual_rows": 0,
        }
    else:
        try:
            live_source = check_source_projection(
                read_tsv(UPSTREAM_SENTENCES), read_tsv(SOURCE_OUT)
            )
        except (OSError, csv.Error, ValueError) as exc:
            live_source = {
                "result": "FAIL",
                "failures": [f"live_source_unreadable:{exc}"],
                "upstream_rows": 0,
                "actual_rows": 0,
            }
    if live_source["result"] != "PASS":
        failures.append("live_source_integrity")
    pinned_source = check_pinned_source_snapshot(snapshot.get("sentences", {}))
    if pinned_source["result"] != "PASS":
        failures.append("pinned_source_integrity")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_rows": source_report.get("rows", 0),
        "provenance_manifest_version": manifest.get("manifest_version"),
        "live_source": live_source,
        "pinned_source": pinned_source,
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


def scaffold_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "source_uid": row["source_uid"],
            "sentno": row["sentno"],
            **{field: "" for field in EMPTY_FIELDS},
            "enrichment_state": "not_started",
        }
        for row in source_rows
    ]


def load_or_create_enrichment(source_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    """Create the scaffold once; preserve any later enrichment byte-for-byte."""

    if not ENRICHMENT_OUT.exists():
        rows = scaffold_rows(source_rows)
        write_tsv(ENRICHMENT_OUT, rows)
        return rows, False

    rows = read_tsv(ENRICHMENT_OUT)
    if not rows or list(rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("existing enrichment output has an invalid header or no rows")
    if len(rows) != len(source_rows):
        raise RuntimeError(
            f"existing enrichment output row count changed: expected {len(source_rows)}, got {len(rows)}"
        )
    expected_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    actual_keys = [(row.get("source_uid", ""), row.get("sentno", "")) for row in rows]
    if actual_keys != expected_keys:
        raise RuntimeError("existing enrichment output source linkage changed")
    allowed_states = {"not_started", "draft", "qa_passed", "reviewed", "flagged"}
    if any(row.get("enrichment_state") not in allowed_states for row in rows):
        raise RuntimeError("existing enrichment output contains an invalid enrichment_state")
    return rows, True


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
    rows, preserved_existing_enrichment = load_or_create_enrichment(source_rows)
    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_OUT.touch(exist_ok=True)
    report = {
        "result": "PASS",
        "source_gate": gate,
        "rows": len(rows),
        "completed_rows": sum(
            1 for row in rows if row.get("enrichment_state") != "not_started"
        ),
        "enrichment_state": (
            "not_started"
            if all(row.get("enrichment_state") == "not_started" for row in rows)
            else "preserved_existing"
        ),
        "enrichment_output_action": (
            "preserved" if preserved_existing_enrichment else "created"
        ),
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
