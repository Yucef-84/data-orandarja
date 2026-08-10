"""Validate the source-only MADOran enrichment scaffold."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.build_madoran_enrichment_scaffold import (
        EMPTY_FIELDS,
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        QA_OUT,
        ROOT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
    )
except ModuleNotFoundError:
    from build_madoran_enrichment_scaffold import (  # type: ignore
        EMPTY_FIELDS,
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        QA_OUT,
        ROOT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
    )


STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
ISSUE_OUT = ROOT / "data" / "master" / "issues" / "madoran_morphology_upstream_defect.json"
MORPHOLOGY_DEPENDENT_FIELDS = frozenset(
    {
        "lemma_features",
        "root_features",
        "pattern_features",
        "morphology_vocabulary",
        "morphology_learning_units",
    }
)
ENRICHMENT_STATES = frozenset(
    {"not_started", "draft", "qa_passed", "reviewed", "flagged"}
)


def check_enrichment_rows(
    source_rows: list[dict[str, str]], enrichment_rows: list[dict[str, str]]
) -> dict[str, object]:
    """Check the source-keyed scaffold without reading morphology data."""

    failures: list[str] = []
    expected_sentnos = [str(index) for index in range(1, 1357)]
    source_uids = [row.get("source_uid", "") for row in source_rows]
    enrichment_uids = [row.get("source_uid", "") for row in enrichment_rows]
    enrichment_sentnos = [row.get("sentno", "") for row in enrichment_rows]

    if len(enrichment_rows) != 1356:
        failures.append("row_count")
    if len(set(enrichment_uids)) != len(enrichment_uids):
        failures.append("duplicate_source_uid")
    if set(enrichment_uids) - set(source_uids):
        failures.append("unknown_source_uid")
    if set(source_uids) - set(enrichment_uids):
        failures.append("missing_source_uid")
    if enrichment_uids != source_uids:
        failures.append("source_uid_linkage")
    if enrichment_sentnos != expected_sentnos:
        failures.append("sentno_coverage")
    for row in enrichment_rows:
        state = row.get("enrichment_state", "")
        if state not in ENRICHMENT_STATES:
            failures.append("invalid_enrichment_state")
            break
        if state == "not_started" and any(
            row.get(field, "") != "" for field in EMPTY_FIELDS
        ):
            failures.append("non_empty_initial_linguistic_field")
            break
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_rows": len(source_rows),
        "enrichment_rows": len(enrichment_rows),
    }


def check_morphology_dependency(
    layer_status: dict[str, object], populated_fields: list[str]
) -> dict[str, object]:
    """Reject morphology-dependent fields unless the morphology gate passes."""

    violations = sorted(
        set(populated_fields).intersection(MORPHOLOGY_DEPENDENT_FIELDS)
    )
    blocked = layer_status.get("morphology") != "PASS"
    failures = ["morphology_dependent_fields_while_blocked"] if blocked and violations else []
    return {
        "result": "PASS" if not failures else "FAIL",
        "morphology_gate": layer_status.get("morphology"),
        "populated_fields": sorted(set(populated_fields)),
        "violations": violations,
        "failures": failures,
    }


def validate() -> dict[str, object]:
    failures: list[str] = []
    gate = source_gate()
    if gate["result"] != "PASS":
        failures.append("source_gate")
    source_rows = read_tsv(SOURCE_OUT)
    enrichment_rows = read_tsv(ENRICHMENT_OUT) if ENRICHMENT_OUT.exists() else []
    if enrichment_rows and list(enrichment_rows[0]) != ENRICHMENT_FIELDS:
        failures.append("header")
    row_check = check_enrichment_rows(source_rows, enrichment_rows)
    failures.extend(row_check["failures"])
    if not EVENTS_OUT.exists():
        event_check = {
            "result": "FAIL",
            "failures": ["provenance_event_log_missing"],
            "events": 0,
        }
    else:
        event_check = check_provenance_events(
            EVENTS_OUT.read_text(encoding="utf-8"),
            {row.get("source_uid", "") for row in source_rows},
        )
    failures.extend(event_check["failures"])
    status: dict[str, object] = {}
    if not STATUS_OUT.exists():
        failures.append("layer_status_missing")
    else:
        status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
        expected_status = {
            "source": "PASS",
            "source_provenance": "PASS",
            "morphology": "BLOCKED_UPSTREAM_DEFECT",
            "format_reconciliation": "UPSTREAM_DEFECT_CONFIRMED",
            "source_only_enrichment": "READY",
            "morphology_dependent_enrichment": "BLOCKED",
            "learning_units": "NOT_STARTED",
            "exports": "NOT_STARTED",
        }
        for key, expected in expected_status.items():
            if status.get(key) != expected:
                failures.append(f"layer_status:{key}")
    dependency_check = check_morphology_dependency(status, [])
    if dependency_check["result"] != "PASS":
        failures.extend(dependency_check["failures"])
    if not ISSUE_OUT.exists():
        failures.append("morphology_issue_missing")
    else:
        issue = json.loads(ISSUE_OUT.read_text(encoding="utf-8"))
        if issue.get("status") != "BLOCKED_UPSTREAM_DEFECT":
            failures.append("morphology_issue_status")
        if issue.get("repaired") is not False:
            failures.append("morphology_issue_repaired")
        if issue.get("synthetic_rows_added") != 0:
            failures.append("synthetic_rows_added")
    report = {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_gate": gate,
        "source_rows": len(source_rows),
        "enrichment_rows": len(enrichment_rows),
        "completed_rows": sum(
            1 for row in enrichment_rows if row.get("enrichment_state") != "not_started"
        ),
        "morphology_dependency": dependency_check,
        "provenance_events": event_check,
        "outputs": {
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "status": STATUS_OUT.relative_to(ROOT).as_posix(),
            "issue": ISSUE_OUT.relative_to(ROOT).as_posix(),
        },
    }
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["result"] == "PASS" else 1)
