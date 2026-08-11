"""Correct one pre-review Batch 07 surface error with append-only provenance."""
from __future__ import annotations

import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch07 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT, check_provenance_events, read_tsv, source_gate, write_tsv
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT="2c57e69"; CORRECTION_ID="MADORAN-ENRICH-007-PRE-REVIEW-CORRECTION-01"; PROMPT_VERSION="madoran-source-enrichment-v7-correction-1"; TARGET_SENTNO="391"
BATCH_QA_OUT=ROOT/"data/master/qa/madoran_enrichment_batch07_qa.json"; CORRECTION_QA_OUT=ROOT/"data/master/qa/madoran_enrichment_batch07_pre_review_correction01_qa.json"; STATUS_OUT=ROOT/"data/master/state/madoran_layer_status.json"
NEW_KOREAN="와파, 네가 만든 밥을 넣은 오징어에 대해 물어보고 싶었어. 거기에 넣은 소스나 양념을 어떻게 만들었는지 알고 싶어. 나도 만들어 보고 싶었거든."

def now(): return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
def apply():
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    if not head.startswith(BASE_COMMIT): raise RuntimeError(f"base_commit_mismatch:{head}")
    if source_gate()["result"]!="PASS": raise RuntimeError("source_gate_failed")
    source=read_tsv(SOURCE_OUT); master=read_tsv(ENRICHMENT_OUT); batch=read_tsv(BATCH_OUT); events=EVENTS_OUT.read_text(encoding="utf-8")
    source_uids={r["source_uid"] for r in source}; before_check=check_provenance_events(events,source_uids)
    if before_check["result"]!="PASS" or before_check["events"]!=6163: raise RuntimeError(json.dumps(before_check))
    changed=0
    for row in master:
        if row["sentno"]==TARGET_SENTNO: row["korean"]=NEW_KOREAN; changed+=1
    for row in batch:
        if row["sentno"]==TARGET_SENTNO: row["korean"]=NEW_KOREAN
    if changed!=1: raise RuntimeError(f"changed:{changed}")
    master_row=next(r for r in master if r["sentno"]==TARGET_SENTNO); stamp=now(); event={"source_uid":master_row["source_uid"],"field":"korean","value_hash":"sha256:"+hashlib.sha256(NEW_KOREAN.encode()).hexdigest(),"method":"llm_source_only_enrichment_correction","model":"codex-unspecified","prompt_version":PROMPT_VERSION,"schema_version":"1.1.0","generated_at":stamp,"review_state":"generated"}; addition=json.dumps(event,ensure_ascii=False,separators=(",",":"))+"\n"; combined=events+addition; combined_check=check_provenance_events(combined,source_uids); trace=check_enrichment_provenance(master,combined)
    if combined_check["result"]!="PASS" or combined_check["events"]!=6164 or trace["result"]!="PASS": raise RuntimeError(json.dumps({"events":combined_check,"trace":trace},ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT,master); write_tsv(BATCH_OUT,batch)
    with EVENTS_OUT.open("ab") as h: h.write(addition.encode())
    qa=json.loads(BATCH_QA_OUT.read_text(encoding="utf-8")); history=list(qa.get("correction_history",[])); history.append({"correction_id":CORRECTION_ID,"changed_fields":1,"rows":1,"provenance_events":1}); qa.update({"correction_id":CORRECTION_ID,"latest_correction_id":CORRECTION_ID,"correction_history":history,"correction_changed_fields":1,"correction_rows":1,"correction_provenance_events":1,"new_provenance_events":751,"total_provenance_events":6164,"expected_total_provenance_events":6164,"latest_event_hash_gate":"PASS","content_review_status":"pending_headgpt"}); BATCH_QA_OUT.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    status=json.loads(STATUS_OUT.read_text(encoding="utf-8")); status["enrichment_correction_id"]=CORRECTION_ID; evidence=list(status.get("evidence_files",[])); p="data/master/qa/madoran_enrichment_batch07_pre_review_correction01_qa.json"; status["evidence_files"]=evidence if p in evidence else evidence+[p]; STATUS_OUT.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    correction={"result":"PASS","batch_id":"MADORAN-ENRICH-007","correction_id":CORRECTION_ID,"base_commit":BASE_COMMIT,"corrected_rows":[TARGET_SENTNO],"changed_fields":1,"new_provenance_events":1,"provenance_events_before":6163,"provenance_events_after":6164,"source_gate":"PASS","morphology_gate":"BLOCKED_UPSTREAM_DEFECT","morphology_reads":0,"arabic_modified":0,"outside_target_mutations":0,"learning_unit_rows_created":0,"latest_event_hash_gate":"PASS","validator":"PASS","batch_artifact_sync":"PASS","batch_artifact_sync_changed_fields":1,"generated_at":stamp}
    CORRECTION_QA_OUT.write_text(json.dumps(correction,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return correction
if __name__=="__main__": print(json.dumps(apply(),ensure_ascii=False,indent=2))
