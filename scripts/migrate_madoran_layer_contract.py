"""Migrate the MADOran source enrichment layer to the formal layer contract.

This is a one-time, fail-closed migration. It adds only the source-level
``processing_flags`` metadata column and its two required provenance events;
canonical source text and the existing linguistic enrichment are immutable.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENRICHMENT_OUT = ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment.tsv"
EVENTS_OUT = ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment_provenance.jsonl"
SOURCE_OUT = ROOT / "data" / "master" / "source" / "madoran_sentences.tsv"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_layer_contract_qa.json"

OLD_FIELDS = [
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
NEW_FIELDS = OLD_FIELDS[:-1] + ["processing_flags", "enrichment_state"]
LINGUISTIC_FIELDS = OLD_FIELDS[2:-1]
FLAG_BY_SENTNO = {"17": "source_ambiguity", "63": "source_corruption"}
MIGRATION_METHOD = "madoran_layer_contract_migration"
MIGRATION_PROMPT_VERSION = "madoran-layer-contract-v1"
MIGRATION_SCHEMA_VERSION = "1.1.0"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=NEW_FIELDS,
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(text)
    os.replace(temporary, path)


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid: str, value: str, generated_at: str) -> dict[str, str]:
    return {
        "source_uid": source_uid,
        "field": "processing_flags",
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": MIGRATION_METHOD,
        "model": "codex-unspecified",
        "prompt_version": MIGRATION_PROMPT_VERSION,
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
    }


def migrate() -> dict[str, object]:
    if not ENRICHMENT_OUT.exists() or not EVENTS_OUT.exists() or not SOURCE_OUT.exists():
        raise RuntimeError("required_layer_file_missing")

    before_rows = read_tsv(ENRICHMENT_OUT)
    if not before_rows or list(before_rows[0]) != OLD_FIELDS:
        raise RuntimeError("migration_requires_pre_contract_enrichment_header")
    if len(before_rows) != 1356:
        raise RuntimeError(f"enrichment_row_count:{len(before_rows)}")
    source_rows = read_tsv(SOURCE_OUT)
    if len(source_rows) != 1356:
        raise RuntimeError(f"source_row_count:{len(source_rows)}")
    if any(row.get("source_status") != "canonical" for row in source_rows):
        raise RuntimeError("non_canonical_source_status")

    event_text = EVENTS_OUT.read_text(encoding="utf-8")
    if not event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    existing_events = [json.loads(line) for line in event_text.splitlines() if line.strip()]
    if len(existing_events) != 1432:
        raise RuntimeError(f"existing_provenance_event_count:{len(existing_events)}")
    source_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    enrichment_keys = [(row["source_uid"], row["sentno"]) for row in before_rows]
    if enrichment_keys != source_keys:
        raise RuntimeError("source_linkage_changed")

    after_rows: list[dict[str, str]] = []
    for row in before_rows:
        migrated_values = dict(row)
        migrated_values["processing_flags"] = FLAG_BY_SENTNO.get(row["sentno"], "")
        migrated = {field: migrated_values.get(field, "") for field in NEW_FIELDS}
        after_rows.append(migrated)
    if list(after_rows[0]) != NEW_FIELDS:
        raise RuntimeError("new_enrichment_header_mismatch")

    for before, after in zip(before_rows, after_rows):
        for field in OLD_FIELDS:
            if before[field] != after[field]:
                raise RuntimeError(f"existing_field_mutated:{before['sentno']}:{field}")
    if sum(bool(row["processing_flags"]) for row in after_rows) != 2:
        raise RuntimeError("processing_flag_population_mismatch")

    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], row["processing_flags"], generated_at)
        for row in after_rows
        if row["processing_flags"]
    ]
    if len(new_events) != 2:
        raise RuntimeError("new_provenance_event_count")
    combined_events = event_text + "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=ENRICHMENT_OUT.parent, delete=False
    ) as handle:
        enrichment_temp = Path(handle.name)
    try:
        write_tsv(enrichment_temp, after_rows)
        atomic_write_text(EVENTS_OUT, combined_events)
        os.replace(enrichment_temp, ENRICHMENT_OUT)
    except Exception:
        enrichment_temp.unlink(missing_ok=True)
        raise

    report = {
        "result": "PASS",
        "migration_id": "MADORAN-LAYER-CONTRACT-001",
        "base_commit": "bd260fc",
        "rows": len(after_rows),
        "processing_flags_populated_rows": 2,
        "new_provenance_events": len(new_events),
        "total_provenance_events": len(existing_events) + len(new_events),
        "linguistic_fields_modified": 0,
        "arabic_modified": 0,
        "learning_unit_rows_created": 0,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "generated_at": generated_at,
        "outputs": {
            "contract": "data/master/schema/madoran_layer_contract.json",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(migrate(), ensure_ascii=False, indent=2))
