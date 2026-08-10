# Native pilot workflow

The contextual B2 expansion is currently paused at the native pilot. The
repository contains the 183-row GPT-reviewed packet, but Codex must not invent
ratings or promote rows without two independent Oran-native reviewers.

## 1. Create independent reviewer files

```powershell
python scripts/build_native_contextual_review_templates.py
```

This creates separate files under `reviews/native_contextual_templates/` for
`ORAN_R1` and `ORAN_R2`. Each reviewer completes all 183 rows independently.
The allowed ratings are `natural`, `understandable_but_unusual`, `not_oran`,
and `wrong`; `oran_native_confirmed=true` and `reviewed_at` are required.

## 2. Merge only complete inputs

```powershell
python scripts/merge_native_contextual_reviews.py `
  reviews/native_contextual_templates/native_contextual_review_ORAN_R1.tsv `
  reviews/native_contextual_templates/native_contextual_review_ORAN_R2.tsv
```

The merge refuses partial files, duplicate IDs, mismatched packet IDs,
missing reviewer confirmation, invalid ratings, missing timestamps, or a
reviewer pair other than exactly two distinct IDs.

## 3. Reconcile the summary

```powershell
python scripts/build_native_contextual_review_summary_skeleton.py
```

The skeleton computes exact-string agreement and leaves
`final_native_status` and `resolution_note` blank. A human must resolve every
disagreement and complete `reviews/native_contextual_review_summary.tsv`.
No disagreement is auto-approved.

## 4. Validate and promote only after PASS

```powershell
python scripts/validate_native_pilot.py
python scripts/promote_native_contextual_rows.py --apply
```

The promotion command is a no-op unless the gate passes. On PASS it changes
only the active contextual rows to `review_status=native2_approved` and
`learner_ready=true`; HOLD rows and all language/provenance fields remain
unchanged. It must be committed and revalidated as a separate state
transition.

For production `--apply`, the command uses the official review manifest,
summary, and canonical contextual batch paths; custom `--reviews`, `--summary`,
or `--batch` paths are dry-run/test-only. Direct callers are also blocked unless
the target is the complete canonical 183-sample native packet. The batch
validator pins an immutable content projection that excludes only the two
lifecycle fields (`review_status` and `learner_ready`), so a legitimate native
promotion is allowed while source, language, provenance, and content changes
remain detectable.

Until this workflow receives real reviewer inputs, do not create new A1/A2,
B1, or B2 learner rows. After the pilot, the planned order remains A1/A2 to
1,200 active, then B1 to 1,500, then B2 to 1,500.
