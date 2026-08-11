"""Synchronize the reviewed Batch 05 artifact with the corrected master rows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch05 import BATCH_FIELDS, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv, write_tsv


BASE_COMMIT = "704a0b7"
CORRECTION_ID = "MADORAN-ENRICH-005-CORRECTION-01"
TARGET_SENTNOS = {"273", "294", "303", "309", "315"}
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_correction01_qa.json"


def sync() -> dict[str, object]:
    batch_rows = read_tsv(BATCH_OUT)
    master_rows = read_tsv(ENRICHMENT_OUT)
    if list(batch_rows[0]) != BATCH_FIELDS:
        raise RuntimeError("batch_header_mismatch")
    master_by_sentno = {row["sentno"]: row for row in master_rows}
    changed_cells = 0
    for row in batch_rows:
        if row["sentno"] not in TARGET_SENTNOS:
            continue
        master = master_by_sentno[row["sentno"]]
        for field in BATCH_FIELDS:
            if field in {"source_uid", "sentno"}:
                continue
            if row[field] != master[field]:
                row[field] = master[field]
                changed_cells += 1
    if changed_cells != 24:
        raise RuntimeError(f"unexpected_sync_cell_count:{changed_cells}")
    for row in batch_rows:
        if row["sentno"] in TARGET_SENTNOS:
            master = master_by_sentno[row["sentno"]]
            if any(row[field] != master[field] for field in BATCH_FIELDS):
                raise RuntimeError(f"artifact_master_mismatch:{row['sentno']}")
    write_tsv(BATCH_OUT, batch_rows)
    qa = json.loads(QA_OUT.read_text(encoding="utf-8"))
    qa["batch_artifact_sync"] = {
        "result": "PASS",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "rows": sorted(TARGET_SENTNOS, key=int),
        "changed_fields": changed_cells,
    }
    QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction_qa["batch_artifact_sync"] = "PASS"
    correction_qa["batch_artifact_sync_changed_fields"] = changed_cells
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa["batch_artifact_sync"]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(sync(), ensure_ascii=False, indent=2))
