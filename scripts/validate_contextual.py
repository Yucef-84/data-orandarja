"""Validate the source-backed contextual expansion pilot.

The validator blocks structural/provenance P0 failures. Translation quality
and native acceptability remain human/GPT review gates until the batch is
promoted from source_verified to gpt_reviewed/native_reviewed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "oran_darija_verified.tsv"
BATCH = ROOT / "data" / "contextual" / "oran_darija_contextual_batch01.tsv"
SOURCE = (
    ROOT
    / "sources"
    / "madoran_v2"
    / "Morphologically Annotated Orani-Arbaic Dialect Dat"
    / "Raw Data - Sentences"
    / "MADOran_Sentences.tsv"
)
EXPECTED_CANONICAL_SHA256 = (
    "96cc35a441c91ee70bd1edd70c6c0d48646f7b808b08f140a88b5d98d642eaf6"
)

FIELDS = [
    "sample_id",
    "language",
    "variety",
    "cefr",
    "domain",
    "topic",
    "sample_type",
    "arabic",
    "source_form",
    "latin",
    "ko",
    "en",
    "lexical_refs",
    "source_id",
    "source_locator",
    "evidence",
    "derivation_type",
    "license_id",
    "group_id",
    "family_id",
    "review_status",
    "learner_ready",
    "note",
]
DOMAINS = {"school_work", "city_transport", "body_health", "food_shopping"}
ALLOWED_CEFR = {"A1", "A2"}
ALLOWED_DERIVATIONS = {"source_direct", "source_normalized"}
PROHIBITED_SOURCES = {"ALGERIAN_COMMON", "ALGERIAN_WIDE", "ALGIERS"}
PROHIBITED_DERIVATIONS = {
    "ai_composed",
    "pedagogical_composed",
    "translated_from_msa",
    "synthetic_dialogue",
}


def read_tsv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t", quotechar='"'))


def normalize_arabic(value: str) -> str:
    value = value.replace("\u0640", "")
    return re.sub(r"\s+", " ", value.strip())


def source_sentence_number(locator: str) -> int | None:
    match = re.search(r"Sentno\s*=\s*(\d+)", locator)
    return int(match.group(1)) if match else None


def validate() -> Dict[str, object]:
    p0: List[str] = []
    canonical_sha = hashlib.sha256(CANONICAL.read_bytes()).hexdigest()
    if canonical_sha != EXPECTED_CANONICAL_SHA256:
        p0.append(
            "canonical SHA-256 changed: "
            f"{canonical_sha} != {EXPECTED_CANONICAL_SHA256}"
        )

    canonical_rows = read_tsv(CANONICAL)
    canonical_ids = {row["id"] for row in canonical_rows}
    canonical_arabic = {
        normalize_arabic(row["arabic"]) for row in canonical_rows
    }
    rows = read_tsv(BATCH)
    source_by_number = {
        int(row["Sentno"]): row["Sentence"] for row in read_tsv(SOURCE)
    }

    if (list(rows[0].keys()) if rows else None) != FIELDS:
        p0.append("contextual header does not match schema")
    if len(rows) != 96:
        p0.append(f"row count is {len(rows)}, expected 96")

    ids = [row.get("sample_id", "") for row in rows]
    if len(ids) != len(set(ids)):
        p0.append("duplicate sample_id")
    expected_ids = {f"ODC-{index:06d}" for index in range(1, 97)}
    if set(ids) != expected_ids:
        p0.append("sample_id set is not ODC-000001..ODC-000096")

    arabic_norm = [normalize_arabic(row.get("arabic", "")) for row in rows]
    duplicates = [
        value for value, count in Counter(arabic_norm).items() if value and count > 1
    ]
    if duplicates:
        p0.append(f"duplicate normalized Arabic in batch: {duplicates[:3]}")
    overlap = sorted(set(arabic_norm) & canonical_arabic)
    if overlap:
        p0.append(f"Arabic duplicates canonical core: {overlap[:3]}")

    cefr_counts = Counter(row.get("cefr", "") for row in rows)
    if cefr_counts != Counter({"A1": 48, "A2": 48}):
        p0.append(f"CEFR counts are {dict(cefr_counts)}")
    domain_counts = Counter(row.get("domain", "") for row in rows)
    if domain_counts != Counter({domain: 24 for domain in DOMAINS}):
        p0.append(f"domain counts are {dict(domain_counts)}")

    for row in rows:
        sid = row.get("sample_id", "<missing>")
        missing = [field for field in FIELDS if not row.get(field, "").strip()]
        if "lexical_refs" in missing:
            missing.remove("lexical_refs")
        if missing:
            p0.append(f"{sid}: missing required fields {missing}")
        if row.get("language") != "ar":
            p0.append(f"{sid}: language must be ar")
        if row.get("variety") != "ar-DZ-oran":
            p0.append(f"{sid}: variety must be ar-DZ-oran")
        if row.get("cefr") not in ALLOWED_CEFR:
            p0.append(f"{sid}: invalid CEFR")
        if row.get("domain") not in DOMAINS:
            p0.append(f"{sid}: invalid domain")
        if row.get("sample_type") != "utterance":
            p0.append(f"{sid}: sample_type must be utterance")
        if row.get("source_id") != "S6":
            p0.append(f"{sid}: source_id must be S6 for Batch 01")
        if row.get("evidence") != "MADORAN_DIRECT":
            p0.append(f"{sid}: evidence must be MADORAN_DIRECT")
        if row.get("derivation_type") not in ALLOWED_DERIVATIONS:
            p0.append(f"{sid}: invalid derivation_type")
        if row.get("derivation_type") in PROHIBITED_DERIVATIONS:
            p0.append(f"{sid}: prohibited derivation_type")
        if row.get("license_id") != "CC-BY-NC-3.0-MADORAN":
            p0.append(f"{sid}: missing or invalid license")
        if row.get("review_status") != "source_verified":
            p0.append(f"{sid}: Batch 01 must start source_verified")
        if row.get("learner_ready", "").lower() != "false":
            p0.append(f"{sid}: learner_ready must be false before review")
        refs = [ref for ref in row.get("lexical_refs", "").split("|") if ref]
        unknown_refs = [ref for ref in refs if ref not in canonical_ids]
        if unknown_refs:
            p0.append(f"{sid}: unknown lexical_refs {unknown_refs[:3]}")

        number = source_sentence_number(row.get("source_locator", ""))
        if number is None:
            p0.append(f"{sid}: invalid source_locator")
        else:
            source_form = source_by_number.get(number)
            if source_form is None:
                p0.append(f"{sid}: source sentence {number} not found")
            elif row.get("source_form") != source_form:
                p0.append(f"{sid}: source_form replay mismatch")
            if row.get("derivation_type") == "source_direct" and row.get(
                "arabic"
            ) != row.get("source_form"):
                p0.append(f"{sid}: source_direct Arabic differs from source_form")
            if row.get("derivation_type") == "source_normalized":
                if row.get("arabic") == row.get("source_form"):
                    p0.append(f"{sid}: source_normalized has no source difference")
                if "normal" not in row.get("note", "").lower():
                    p0.append(f"{sid}: normalized source lacks note")

        if any(source in row.get("source_id", "") for source in PROHIBITED_SOURCES):
            p0.append(f"{sid}: prohibited source")
        if any(
            derivation in row.get("derivation_type", "")
            for derivation in PROHIBITED_DERIVATIONS
        ):
            p0.append(f"{sid}: prohibited derivation")
        if not re.search(r"[A-Za-z]", row.get("latin", "")):
            p0.append(f"{sid}: Latin field has no Latin characters")
        if not re.search(r"[\u0600-\u06ff]", row.get("arabic", "")):
            p0.append(f"{sid}: Arabic field has no Arabic characters")

    p1_pending = len(rows) if any(
        row.get("review_status") != "gpt_reviewed" for row in rows
    ) else 0
    return {
        "p0_errors": p0,
        "p1_manual_review_pending": p1_pending,
        "canonical_sha256": canonical_sha,
        "rows": len(rows),
        "cefr_counts": dict(cefr_counts),
        "domain_counts": dict(domain_counts),
        "source_replay_failures": sum(
            1
            for error in p0
            if "source_form replay mismatch" in error
            or "source sentence" in error
        ),
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["p0_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
