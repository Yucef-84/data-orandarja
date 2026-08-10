"""Validate the generated MADOran master source and morphology layers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.build_madoran_master import (
        MORPHOLOGY,
        MORPHOLOGY_OUT,
        SENTENCES,
        SOURCE_OUT,
        build_source,
        make_qa,
        read_rows,
        read_strict_rows,
    )
except ModuleNotFoundError:
    from build_madoran_master import (  # type: ignore
        MORPHOLOGY,
        MORPHOLOGY_OUT,
        SENTENCES,
        SOURCE_OUT,
        build_source,
        make_qa,
        read_rows,
        read_strict_rows,
    )


def validate() -> dict[str, object]:
    upstream_source_rows = read_rows(SENTENCES)
    expected_source_rows = build_source(upstream_source_rows)
    expected_morphology_rows, malformed_rows = read_strict_rows(MORPHOLOGY)
    actual_source_rows = read_rows(SOURCE_OUT) if SOURCE_OUT.exists() else []
    actual_morphology_rows = read_rows(MORPHOLOGY_OUT) if MORPHOLOGY_OUT.exists() else []
    return make_qa(
        upstream_source_rows,
        expected_source_rows,
        actual_source_rows,
        expected_morphology_rows,
        actual_morphology_rows,
        malformed_rows,
    )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["result"] == "PASS" else 1)
