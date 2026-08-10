"""Validate the source-backed contextual expansion pilot Batch 02."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "oran_darija_verified.tsv"
BATCH01 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
BATCH02 = ROOT / "data" / "contextual" / "oran_darija_contextual_batch02.tsv"
SOURCE = (
    ROOT
    / "sources"
    / "madoran_v2"
    / "Morphologically Annotated Orani-Arbaic Dialect Dat"
    / "Raw Data - Sentences"
    / "MADOran_Sentences.tsv"
)

CANONICAL_SHA256 = "96cc35a441c91ee70bd1edd70c6c0d48646f7b808b08f140a88b5d98d642eaf6"
BATCH01_SHA256 = "4268fda4ffaff5e13c0a1a5bc1d948d695288501e3a504d03c3d0060dae15437"
FIELDS = [
    "sample_id", "language", "variety", "cefr", "domain", "topic",
    "sample_type", "arabic", "source_form", "latin", "ko", "en",
    "lexical_refs", "source_id", "source_locator", "evidence",
    "derivation_type", "license_id", "group_id", "family_id",
    "review_status", "learner_ready", "note",
]
DOMAINS = {"school_work", "city_transport", "body_health", "food_shopping"}
CEFR_QUOTA = {"A1": 45, "A2": 59}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t", quotechar='"'))


def normalize_arabic(value: str) -> str:
    value = value.replace("\u0640", "")
    return re.sub(r"\s+", " ", value.strip())


def locator_number(locator: str) -> int | None:
    match = re.fullmatch(r"MADOran_Sentences\.tsv:Sentno=(\d+)", locator.strip())
    return int(match.group(1)) if match else None


def validate() -> dict[str, object]:
    errors: list[str] = []
    canonical_bytes = CANONICAL.read_bytes()
    batch01_bytes = BATCH01.read_bytes()
    canonical_sha = hashlib.sha256(canonical_bytes).hexdigest()
    batch01_sha = hashlib.sha256(batch01_bytes).hexdigest()
    if canonical_sha != CANONICAL_SHA256:
        errors.append(f"canonical SHA changed: {canonical_sha}")
    if batch01_sha != BATCH01_SHA256:
        errors.append(f"Batch01 SHA changed: {batch01_sha}")

    canonical_rows = read_tsv(CANONICAL)
    batch01_rows = read_tsv(BATCH01)
    rows = read_tsv(BATCH02)
    source_rows = read_tsv(SOURCE)
    source_by_no = {int(row["Sentno"]): row["Sentence"] for row in source_rows}
    canonical_ids = {row["id"] for row in canonical_rows}
    canonical_arabic = {normalize_arabic(row["arabic"]) for row in canonical_rows}
    prior_arabic = {normalize_arabic(row["arabic"]) for row in batch01_rows}
    prior_source_numbers = {
        number for number in (locator_number(row["source_locator"]) for row in batch01_rows)
        if number is not None
    }

    if (list(rows[0].keys()) if rows else None) != FIELDS:
        errors.append("Batch02 header does not match schema")
    if len(rows) != 104:
        errors.append(f"row count is {len(rows)}, expected 104")
    expected_ids = {f"ODC-{index:06d}" for index in range(97, 201)}
    ids = [row.get("sample_id", "") for row in rows]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        errors.append("sample_id set is not unique ODC-000097..ODC-000200")

    normalized = [normalize_arabic(row.get("arabic", "")) for row in rows]
    if any(value and count > 1 for value, count in Counter(normalized).items()):
        errors.append("duplicate normalized Arabic inside Batch02")
    if set(normalized) & prior_arabic:
        errors.append("Arabic overlaps Batch01")
    if set(normalized) & canonical_arabic:
        errors.append("Arabic overlaps canonical core")

    cefr_counts = Counter(row.get("cefr", "") for row in rows)
    domain_counts = Counter(row.get("domain", "") for row in rows)
    if cefr_counts != Counter(CEFR_QUOTA):
        errors.append(f"CEFR counts are {dict(cefr_counts)}")
    if domain_counts != Counter({domain: 26 for domain in DOMAINS}):
        errors.append(f"domain counts are {dict(domain_counts)}")

    source_numbers: list[int] = []
    replay_failures = 0
    for row in rows:
        sid = row.get("sample_id", "<missing>")
        missing = [field for field in FIELDS if not row.get(field, "").strip()]
        if "lexical_refs" in missing:
            missing.remove("lexical_refs")
        if missing:
            errors.append(f"{sid}: missing fields {missing}")
        if row.get("language") != "ar" or row.get("variety") != "ar-DZ-oran":
            errors.append(f"{sid}: invalid language or variety")
        if row.get("cefr") not in {"A1", "A2"} or row.get("domain") not in DOMAINS:
            errors.append(f"{sid}: invalid CEFR or domain")
        if row.get("sample_type") != "utterance":
            errors.append(f"{sid}: sample_type must be utterance")
        if row.get("source_id") != "S6" or row.get("evidence") != "MADORAN_DIRECT":
            errors.append(f"{sid}: invalid provenance source or evidence")
        if row.get("derivation_type") != "source_direct":
            errors.append(f"{sid}: Batch02 must use source_direct")
        if row.get("license_id") != "CC-BY-NC-3.0-MADORAN":
            errors.append(f"{sid}: invalid license")
        if row.get("review_status") not in {"source_verified", "hold"} or row.get("learner_ready") != "false":
            errors.append(f"{sid}: invalid pre-review state")
        if row.get("review_status") == "hold" and not row.get("note", "").startswith("HOLD:"):
            errors.append(f"{sid}: hold rows must carry an explicit HOLD note")
        if row.get("group_id") != f"batch02-{row.get('domain')}":
            errors.append(f"{sid}: group_id does not match domain")
        number = locator_number(row.get("source_locator", ""))
        if number is None or number not in source_by_no:
            errors.append(f"{sid}: invalid or missing source locator")
            replay_failures += 1
            continue
        source_numbers.append(number)
        if number in prior_source_numbers:
            errors.append(f"{sid}: source Sentno={number} already used by Batch01")
        if row.get("source_form") != source_by_no[number] or row.get("arabic") != source_by_no[number]:
            errors.append(f"{sid}: source replay mismatch")
            replay_failures += 1
        if row.get("family_id") != f"MADOran-S6-{number}":
            errors.append(f"{sid}: family_id does not match source")
        unknown_refs = [ref for ref in row.get("lexical_refs", "").split("|") if ref and ref not in canonical_ids]
        if unknown_refs:
            errors.append(f"{sid}: unknown lexical_refs {unknown_refs[:3]}")
        if not re.search(r"[A-Za-z]", row.get("latin", "")):
            errors.append(f"{sid}: Latin field is empty")
        if not re.search(r"[\u0600-\u06ff]", row.get("arabic", "")):
            errors.append(f"{sid}: Arabic field is empty")

    if len(source_numbers) != len(set(source_numbers)):
        errors.append("duplicate MADOran source locator")

    hold_count = sum(row.get("review_status") == "hold" for row in rows)
    active_count = sum(row.get("review_status") == "source_verified" for row in rows)
    return {
        "p0_errors": errors,
        "p1_manual_review_pending": active_count,
        "active": active_count,
        "hold": hold_count,
        "canonical_sha256": canonical_sha,
        "batch01_sha256": batch01_sha,
        "rows": len(rows),
        "cefr_counts": dict(cefr_counts),
        "domain_counts": dict(domain_counts),
        "source_replay_failures": replay_failures,
    }


if __name__ == "__main__":
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report["p0_errors"] else 0)
