"""Validate all contextual expansion files and print active-state statistics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXTUAL = ROOT / "data" / "contextual"
CANONICAL = ROOT / "data" / "oran_darija_verified.tsv"
SOURCE = (
    ROOT
    / "sources"
    / "madoran_v2"
    / "Morphologically Annotated Orani-Arbaic Dialect Dat"
    / "Raw Data - Sentences"
    / "MADOran_Sentences.tsv"
)
FIELDS = [
    "sample_id", "language", "variety", "cefr", "domain", "topic", "sample_type",
    "arabic", "source_form", "latin", "ko", "en", "lexical_refs", "source_id",
    "source_locator", "evidence", "derivation_type", "license_id", "group_id",
    "family_id", "review_status", "learner_ready", "note",
]
ACTIVE = {"source_verified", "gpt_reviewed", "native1_reviewed", "native2_approved"}
STATUSES = ACTIVE | {"hold"}
LEVELS = {"A1", "A2", "B1", "B2"}
DOMAINS = {"school_work", "city_transport", "body_health", "food_shopping"}
ALLOWED_SOURCE_IDS = {"S6"}
ALLOWED_EVIDENCE = {"MADORAN_DIRECT"}
ALLOWED_DERIVATIONS = {"source_direct", "source_normalized"}
ALLOWED_LICENSES = {"CC-BY-NC-3.0-MADORAN"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_arabic(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("ـ", "").strip())


def locator_number(value: str) -> int | None:
    match = re.fullmatch(r"MADOran_Sentences\.tsv:Sentno=(\d+)", value.strip())
    return int(match.group(1)) if match else None


def contextual_paths(paths: list[Path] | None = None) -> list[Path]:
    return sorted(paths if paths is not None else CONTEXTUAL.rglob("oran_darija_contextual_*.tsv"))


def validate(paths: list[Path] | None = None) -> dict[str, object]:
    errors: list[str] = []
    source_rows = read_tsv(SOURCE)
    source_by_no = {int(row["Sentno"]): row["Sentence"] for row in source_rows}
    canonical_arabic = {
        normalize_arabic(row.get("arabic", ""))
        for row in read_tsv(CANONICAL)
        if row.get("arabic", "").strip()
    }
    all_rows: list[tuple[Path, dict[str, str]]] = []
    for path in contextual_paths(paths):
        for row in read_tsv(path):
            all_rows.append((path, row))

    ids: set[str] = set()
    arabic_seen: dict[str, str] = {}
    source_seen: dict[int, str] = {}
    replay_failures = 0
    for path, row in all_rows:
        sid = row.get("sample_id", "<missing>")
        if sid in ids:
            errors.append(f"{sid}: duplicate sample_id")
        ids.add(sid)
        if list(row.keys()) != FIELDS:
            errors.append(f"{path.name}: header does not match contextual schema")
            break
        missing = [field for field in FIELDS if not row.get(field, "").strip()]
        if "lexical_refs" in missing:
            missing.remove("lexical_refs")
        if missing:
            errors.append(f"{sid}: missing fields {missing}")
        if row.get("cefr") not in LEVELS or row.get("domain") not in DOMAINS:
            errors.append(f"{sid}: invalid level or domain")
        if row.get("sample_type") != "utterance":
            errors.append(f"{sid}: sample_type must be utterance")
        if row.get("review_status") not in STATUSES:
            errors.append(f"{sid}: invalid review_status")
        if row.get("learner_ready") == "true" and row.get("review_status") != "native2_approved":
            errors.append(f"{sid}: learner_ready requires native2_approved")
        if row.get("review_status") == "hold" and not row.get("note", "").startswith("HOLD:"):
            errors.append(f"{sid}: hold rows require a HOLD note")
        if row.get("source_id") not in ALLOWED_SOURCE_IDS:
            errors.append(f"{sid}: source_id {row.get('source_id', '')} has no implemented replay adapter")
        if row.get("evidence") not in ALLOWED_EVIDENCE:
            errors.append(f"{sid}: invalid evidence {row.get('evidence', '')}")
        if row.get("derivation_type") not in ALLOWED_DERIVATIONS:
            errors.append(f"{sid}: prohibited or unsupported derivation_type {row.get('derivation_type', '')}")
        if row.get("license_id") not in ALLOWED_LICENSES:
            errors.append(f"{sid}: invalid license_id {row.get('license_id', '')}")
        if row.get("derivation_type") == "source_direct" and row.get("arabic") != row.get("source_form"):
            errors.append(f"{sid}: source_direct Arabic/source_form mismatch")
        if row.get("derivation_type") == "source_normalized":
            if row.get("arabic") == row.get("source_form"):
                errors.append(f"{sid}: source_normalized must change the source form")
            if "normal" not in row.get("note", "").lower():
                errors.append(f"{sid}: source_normalized requires a normalization note")
        number = locator_number(row.get("source_locator", ""))
        if number is None or number not in source_by_no:
            errors.append(f"{sid}: source locator does not replay")
            replay_failures += 1
        elif row.get("source_id") == "S6":
            if row.get("source_form") != source_by_no[number]:
                errors.append(f"{sid}: MADOran source replay mismatch")
                replay_failures += 1
            if number in source_seen:
                errors.append(f"{sid}: source locator duplicates {source_seen[number]}")
            source_seen[number] = sid
            if row.get("family_id") != f"MADOran-S6-{number}":
                errors.append(f"{sid}: family_id does not match MADOran S6 locator")
        normalized = normalize_arabic(row.get("arabic", ""))
        if normalized in arabic_seen:
            errors.append(f"{sid}: normalized Arabic duplicates {arabic_seen[normalized]}")
        if normalized in canonical_arabic:
            errors.append(f"{sid}: normalized Arabic overlaps canonical lexical core")
        arabic_seen[normalized] = sid

    cefr_counts = Counter(row["cefr"] for _, row in all_rows)
    domain_counts = Counter(row["domain"] for _, row in all_rows)
    status_counts = Counter(row["review_status"] for _, row in all_rows)
    active_rows = [row for _, row in all_rows if row["review_status"] in ACTIVE]
    return {
        "p0_errors": errors,
        "rows_raw": len(all_rows),
        "active": len(active_rows),
        "hold": status_counts["hold"],
        "learner_ready": sum(row["learner_ready"] == "true" for _, row in all_rows),
        "cefr_active": dict(Counter(row["cefr"] for row in active_rows)),
        "domain_active": dict(Counter(row["domain"] for row in active_rows)),
        "cefr_raw": dict(cefr_counts),
        "domain_raw": dict(domain_counts),
        "review_status": dict(status_counts),
        "source_replay_failures": replay_failures,
        "source_inventory_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    parser.parse_args()
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report["p0_errors"] else 0)


if __name__ == "__main__":
    main()
